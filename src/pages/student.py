"""学生页面（Streamlit）"""

import os
import sys
import pandas as pd
import pymysql
import streamlit as st

# 确保 src/ 在 sys.path 中（student_tui / teacher_tui 模块所在目录）
_src = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _src not in sys.path:
    sys.path.insert(0, _src)

from student_tui import show_courses, my_grades, semester_avg, enrolled_courses
from core.models import SemesterQuery, validate_or_error
from core.grid import st_ag


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
    st_ag(df)


def my_grades_page(conn, sid, sname):
    """显示我的成绩页面"""
    rows, ws, gpa = my_grades(conn, sid, sname, paged=False)
    if not rows:
        st.info("暂无成绩")
        return
    df = pd.DataFrame(rows, columns=["课程", "教师", "学期", "成绩"])
    st_ag(df)
    col1, col2 = st.columns(2)
    col1.metric("学籍分", ws)
    col2.metric("绩点分", gpa)


def semester_avg_page(conn, sno):
    """显示学期均分查询页面"""
    sem = st.text_input(
        "学期",
        placeholder="例如：2024-2025-1",
        help="格式如：2024-2025-1（开始学年-结束学年-学期）",
    )
    if not sem:
        st.info("请输入学期")
        return
    data = validate_or_error(SemesterQuery, semester=sem)
    if data is None:
        return
    rows = semester_avg(conn, sno, sem=data["semester"], paged=False)
    if not rows:
        st.info(f"{sem} 暂无成绩")
        return
    df = pd.DataFrame(rows, columns=["学号", "姓名", "学期", "课程数", "均分"])
    st_ag(df)


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
    st_ag(df)

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
    st_ag(df)

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
