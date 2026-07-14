"""教师页面（Streamlit）"""

import csv
import os
import sys
import pandas as pd
import pymysql
import streamlit as st

# 确保 src/ 在 sys.path 中（student_tui / teacher_tui 模块所在目录）
_src = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _src not in sys.path:
    sys.path.insert(0, _src)

from teacher_tui import teacher_offerings, offering_students
from core.grid import st_ag


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
    st_ag(df)

    col1, col2, col3 = st.columns(3)
    sno = col1.text_input("学生学号")
    score = col2.text_input("成绩 (0-100)")
    if col3.button("录入", key="grade_btn"):
        try:
            score_val = float(score)
        except ValueError:
            st.error("成绩必须是数字")
            st.stop()
        try:
            cur = conn.cursor()
            cur.callproc("sp_grade_input", [tno, plan_id, sno, score_val])
            conn.commit()
            cur.fetchall()
            cur.nextset()
            st.session_state.msg = ("success", f"{sno} → {score}")
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
        for row in reader:
            try:
                cur = conn.cursor()
                cur.callproc(
                    "sp_grade_input",
                    [tno, int(row["plan_id"]), row["student_no"], float(row["score"])],
                )
                conn.commit()
                cur.fetchall()
                cur.nextset()
                ok += 1
            except (pymysql.Error, ValueError, KeyError, csv.Error) as e:
                fail += 1
                st.error(f"第{ok + fail + 1}行 {row.get('student_no', '?')}: {e}")
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
    df = pd.DataFrame(students, columns=["学号", "姓名", "成绩"])
    st_ag(df)
