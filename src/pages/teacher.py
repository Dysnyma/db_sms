"""教师页面（Streamlit）"""

import csv
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

from teacher_tui import teacher_offerings, offering_students
from core.models import GradeRecord, validate_or_error


def grade_input_page(conn, tno):
    """单条录入成绩页面"""
    if st.session_state.get("msg"):
        _, m = st.session_state.pop("msg")
        st.success(m)
    offerings = teacher_offerings(conn, tno)
    if not offerings:
        st.info("暂无排课")
        return
    choices = {f"#{r[0]} {r[1]} ({r[2]}) — {r[3]}/{r[4]}人": r[0] for r in offerings}
    plan_id = choices[st.selectbox("选择排课", list(choices.keys()))]

    students = offering_students(conn, plan_id)
    if not students:
        st.info("暂无学生选课")
        return
    df = pd.DataFrame(students, columns=["学号", "姓名", "成绩"])
    st.dataframe(df, use_container_width=True)

    col1, col2, col3 = st.columns(3)
    sno = col1.text_input(
        "学生学号",
        placeholder="例如：20240001",
        help="学号为 8-12 位纯数字",
        max_chars=12,
    )
    score = col2.text_input(
        "成绩",
        placeholder="例如：88.5",
        help="成绩为 0~100 的数值",
        max_chars=6,
    )
    if col3.button("录入", key="grade_btn"):
        data = validate_or_error(GradeRecord, sno=sno, score=score)
        if data is None:
            return
        try:
            cur = conn.cursor()
            cur.callproc("sp_grade_input", [tno, plan_id, data["sno"], data["score"]])
            conn.commit()
            cur.fetchall()
            cur.nextset()
            st.session_state.msg = ("success", f"{data['sno']} → {data['score']}")
            st.rerun()
        except pymysql.Error as e:
            st.error(str(e))


def batch_grade_page(conn, tno):
    """批量导入 CSV 成绩页面"""
    file = st.file_uploader("上传 CSV（plan_id, student_no, score）", type="csv")
    if not file:
        return

    if st.button("开始导入"):
        content = file.read().decode("utf-8-sig")
        reader = csv.DictReader(content.splitlines())
        ok = fail = 0
        for i, row in enumerate(reader, 1):
            err_msg = None
            try:
                plan_id = int(row["plan_id"])
                student_no = row["student_no"]
                score = float(row["score"])
            except (ValueError, KeyError):
                err_msg = "数据格式错误，请检查 plan_id/student_no/score"
            if err_msg is None:
                try:
                    cur = conn.cursor()
                    cur.callproc("sp_grade_input", [tno, plan_id, student_no, score])
                    conn.commit()
                    cur.fetchall()
                    cur.nextset()
                    ok += 1
                except pymysql.Error as e:
                    err_msg = str(e)
            if err_msg:
                fail += 1
                st.error(f"第{i}行 {row.get('student_no', '?')}: {err_msg}")
        st.success(f"✅ 完成：成功 {ok} 条，失败 {fail} 条")


def my_students_page(conn, tno):
    """查看课程学生页面"""
    offerings = teacher_offerings(conn, tno)
    if not offerings:
        st.info("暂无排课")
        return
    choices = {f"#{r[0]} {r[1]} ({r[2]}) — {r[3]}/{r[4]}人": r[0] for r in offerings}
    plan_id = choices[st.selectbox("选择排课", list(choices.keys()))]

    students = offering_students(conn, plan_id)
    if not students:
        st.info("暂无学生选课")
        return

    graded = [(s[0], s[1], float(s[2])) for s in students if s[2] is not None]
    ungraded = [s for s in students if s[2] is None]

    df = pd.DataFrame(students, columns=["学号", "姓名", "成绩"])
    st.dataframe(df, use_container_width=True)

    if ungraded:
        st.warning(f"⚠️ 还有 **{len(ungraded)}** 名学生未录入成绩")
        with st.expander("查看未录入学生名单"):
            for s in ungraded:
                st.write(f"- {s[1]}（{s[0]}）")

    if graded:
        st.divider()

        buckets = {"优秀 ≥90": 0, "良好 80~89": 0, "中等 70~79": 0, "及格 60~69": 0, "不及格 <60": 0}
        for _, _, sc in graded:
            if sc >= 90:
                buckets["优秀 ≥90"] += 1
            elif sc >= 80:
                buckets["良好 80~89"] += 1
            elif sc >= 70:
                buckets["中等 70~79"] += 1
            elif sc >= 60:
                buckets["及格 60~69"] += 1
            else:
                buckets["不及格 <60"] += 1
        col_l, col_r = st.columns(2)
        with col_l:
            df_pie = pd.DataFrame([(k, v) for k, v in buckets.items() if v > 0], columns=["等级", "人数"])
            fig = px.pie(df_pie, values="人数", names="等级", title="成绩分布",
                         color="等级",
                         color_discrete_map={
                             "优秀 ≥90": "#4CAF50", "良好 80~89": "#8BC34A",
                             "中等 70~79": "#FFC107", "及格 60~69": "#FF9800",
                             "不及格 <60": "#f44336",
                         })
            fig.update_traces(textinfo="label+percent")
            st.plotly_chart(fig, use_container_width=True)
        with col_r:
            df_rank = pd.DataFrame(graded, columns=["学号", "姓名", "成绩"])
            df_rank = df_rank.sort_values("成绩", ascending=False).reset_index(drop=True)
            df_rank["序号"] = range(1, len(df_rank) + 1)
            fig = px.bar(df_rank, x="序号", y="成绩", title="成绩排行",
                         hover_data={"姓名": True, "学号": True, "成绩": ":.1f"},
                         text="成绩", text_auto=".1f",
                         color="成绩", color_continuous_scale=["#f44336", "#FFC107", "#8BC34A", "#4CAF50"],
                         range_color=[0, 100])
            fig.update_traces(textposition="outside")
            fig.update_layout(xaxis_title="名次", showlegend=False)
            st.plotly_chart(fig, use_container_width=True)

        scores_list = [sc for _, _, sc in graded]
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("平均分", f"{sum(scores_list) / len(scores_list):.1f}")
        c2.metric("最高分", f"{max(scores_list):.1f}")
        c3.metric("最低分", f"{min(scores_list):.1f}")
        c4.metric("已录入", f"{len(graded)}/{len(students)}")
