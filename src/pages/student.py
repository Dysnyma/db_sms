"""学生页面（Streamlit）"""

import os
import sys
import pandas as pd
import plotly.express as px
import pymysql
import streamlit as st

# 确保 src/ 在 sys.path 中（student_tui / teacher_tui 模块所在目录）
_src = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _src not in sys.path:
    sys.path.insert(0, _src)

from student_tui import show_courses, my_grades, semester_avg, enrolled_courses
from core.models import SemesterQuery, validate_or_error


def show_courses_page(conn, sno):
    """显示可选课程列表页面"""
    rows = show_courses(conn, sno, False)
    if not rows:
        st.info("没有可选课程")
        return
    df = pd.DataFrame(
        rows,
        columns=[
            "排课ID",
            "课程名",
            "学分",
            "教师",
            "学期",
            "剩余名额",
            "选课开始",
            "选课截止",
        ],
    )
    st.dataframe(df, use_container_width=True)


def my_grades_page(conn, sid, sname):
    """显示我的成绩页面"""
    rows, ws, gpa = my_grades(conn, sid, sname, paged=False)
    if not rows:
        st.info("暂无成绩")
        return
    df = pd.DataFrame(rows, columns=["课程", "教师", "学期", "成绩"])
    st.dataframe(df, use_container_width=True)
    col1, col2 = st.columns(2)
    col1.metric("学籍分", ws)
    col2.metric("绩点分", gpa)

    # 各科成绩柱状图
    st.divider()
    df_chart = df.dropna(subset=["成绩"]).copy()
    if not df_chart.empty:
        df_chart["颜色"] = df_chart["成绩"].apply(
            lambda x: "优秀" if x >= 90 else "良好" if x >= 80 else "中等" if x >= 70 else "及格" if x >= 60 else "不及格"
        )
        fig = px.bar(df_chart, x="课程", y="成绩", title="各科成绩一览",
                     text_auto=".1f", hover_data={"学期": True, "教师": True},
                     color="颜色",
                     color_discrete_map={
                         "优秀": "#4CAF50", "良好": "#8BC34A",
                         "中等": "#FFC707", "及格": "#FF9800", "不及格": "#f44336",
                     })
        fig.add_hline(y=60, line_dash="dash", line_color="red", annotation_text="及格线")
        fig.update_traces(textposition="outside")
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)


def semester_avg_page(conn, sno):
    """显示学期均分查询页面"""
    # 查询该学生有数据的学期
    cur = conn.cursor()
    cur.execute(
        """SELECT DISTINCT co.semester FROM enrollment e
        JOIN course_offering co ON e.offering_id = co.id
        JOIN student s ON e.student_id = s.id
        WHERE s.no = %s AND e.is_deleted = 0
        ORDER BY co.semester""",
        [sno],
    )
    semester_opts = [r[0] for r in cur.fetchall()]
    if not semester_opts:
        st.info("暂无成绩数据")
        return

    sem = st.selectbox("学期", semester_opts)
    rows = semester_avg(conn, sno, sem=sem, paged=False)
    if not rows:
        st.info(f"{sem} 暂无成绩")
        return
    df = pd.DataFrame(rows, columns=["学号", "姓名", "学期", "课程数", "均分"])
    st.dataframe(df, use_container_width=True)


def enroll_page(conn, sno):
    """选课操作页面"""
    # 拦截并显示上一次操作的消息（跨 st.rerun 存活）
    if st.session_state.get("msg"):
        msg_type, msg_text = st.session_state.pop("msg")
        if msg_type == "success":
            st.success(msg_text)
        else:
            st.error(msg_text)

    rows = show_courses(conn, sno, paged=False)
    if not rows:
        st.info("没有可选课程")
        return
    df = pd.DataFrame(
        rows,
        columns=[
            "排课ID",
            "课程名",
            "学分",
            "教师",
            "学期",
            "剩余名额",
            "选课开始",
            "选课截止",
        ],
    )
    st.dataframe(df, use_container_width=True)

    choices = {f"#{r[0]} {r[1]} - {r[3]} ({r[2]}学分)": r[0] for r in rows}
    plan_id = choices[st.selectbox("选择要选的排课", list(choices.keys()))]
    if st.button("确认选课", type="primary"):
        try:
            with conn.cursor() as cur:
                cur.callproc("sp_enroll", [sno, int(plan_id)])
            conn.commit()
            st.session_state.msg = ("success", "选课成功！")
            st.rerun()
        except pymysql.Error as e:
            conn.rollback()
            st.session_state.msg = ("error", f"选课失败：{e}")
            st.rerun()


def unenroll_page(conn, sno):
    """退选操作页面"""
    # 拦截并显示上一次操作的消息（跨 st.rerun 存活）
    if st.session_state.get("msg"):
        msg_type, msg_text = st.session_state.pop("msg")
        if msg_type == "success":
            st.success(msg_text)
        else:
            st.error(msg_text)

    rows = enrolled_courses(conn, sno)
    if not rows:
        st.info("没有已选课程")
        return
    df = pd.DataFrame(rows, columns=["排课ID", "课程名", "教师", "学期", "选课截止"])
    st.dataframe(df, use_container_width=True)

    choices = {f"#{r[0]} {r[1]} - {r[2]}": r[0] for r in rows}
    plan_id = choices[st.selectbox("选择要退的排课", list(choices.keys()))]
    if st.button("确认退选", type="primary"):
        try:
            with conn.cursor() as cur:
                cur.callproc("sp_unenroll", [sno, int(plan_id)])
            conn.commit()
            st.session_state.msg = ("success", "退选成功！")
            st.rerun()
        except pymysql.Error as e:
            conn.rollback()
            st.session_state.msg = ("error", f"退选失败：{e}")
            st.rerun()
