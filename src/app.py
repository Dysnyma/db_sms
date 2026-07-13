import pandas as pd
from datetime import datetime
import subprocess
import os
import csv
import pymysql
from admin import (
    summary,
    class_list,
    roster_data,
    course_list,
    class_report_data,
    grade_roster_data,
    teacher_info_data,
    teacher_list_data,
    enrollment_list,
    teacher_full_list,
    student_full_list,
    offering_full_list,
    teacher_course_teachers,
)
from teacher import teacher_offerings, offering_students
from student import show_courses, my_grades, semester_avg, enrolled_courses
from core.config import connect
import streamlit as st

st.set_page_config(page_title="学生成绩管理系统", page_icon="🎓", layout="wide")


def show_courses_page(conn, sno):
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
    rows, ws, gpa = my_grades(conn, sid, sname, paged=False)
    if not rows:
        st.info("暂无成绩")
        return
    df = pd.DataFrame(rows, columns=["课程", "教师", "学期", "成绩"])
    st.dataframe(df, use_container_width=True)
    col1, col2 = st.columns(2)
    col1.metric("学籍分", ws)
    col2.metric("绩点分", gpa)


def semester_avg_page(conn, sno):
    sem = st.text_input("学期 (如 2024-2025-1)")
    if not sem:
        st.info("请输入学期")
        return
    rows = semester_avg(conn, sno, sem=sem, paged=False)
    if not rows:
        st.info(f"{sem} 暂无成绩")
        return
    df = pd.DataFrame(rows, columns=["学号", "姓名", "学期", "课程数", "均分"])
    st.dataframe(df, use_container_width=True)


def enroll_page(conn, sno):
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
    if st.button("确认选课"):
        cur = conn.cursor()
        try:
            cur.callproc("sp_enroll", [sno, int(plan_id)])
            conn.commit()
            cur.fetchall()
            cur.nextset()
            st.success("选课成功")
        except pymysql.Error as e:
            st.error(str(e))


def unenroll_page(conn, sno):
    rows = enrolled_courses(conn, sno)
    if not rows:
        st.info("没有已选课程")
        return
    df = pd.DataFrame(rows, columns=["排课ID", "课程名", "教师", "学期", "选课截止"])
    st.dataframe(df, use_container_width=True)

    choices = {f"#{r[0]} {r[1]} - {r[2]}": r[0] for r in rows}
    plan_id = choices[st.selectbox("选择要退的排课", list(choices.keys()))]
    if st.button("确认退选"):
        cur = conn.cursor()
        try:
            cur.callproc("sp_unenroll", [sno, int(plan_id)])
            conn.commit()
            cur.fetchall()
            cur.nextset()
            st.success("退选成功")
        except pymysql.Error as e:
            st.error(str(e))


def grade_input_page(conn, tno):
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
    sno = col1.text_input("学生学号")
    score = col2.text_input("成绩 (0-100)")
    if col3.button("录入", key="grade_btn"):
        try:
            cur = conn.cursor()
            cur.callproc("sp_grade_input", [tno, plan_id, sno, float(score)])
            conn.commit()
            cur.fetchall()
            cur.nextset()
            st.session_state.msg = ("success", f"{sno} → {score}")
            st.rerun()
        except pymysql.Error as e:
            st.error(str(e))


def batch_grade_page(conn, tno):
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


def summary_page(conn):
    data = summary(conn, False)
    cols = st.columns(6)
    for i, (label, val) in enumerate(data.items()):
        cols[i % 6].metric(label, val)


def roster_page(conn):
    classes = class_list(conn)
    choices = {f"{r[1]} ({r[2]}级 {r[3]}) — {r[4]}": r[0] for r in classes}
    cid = choices[st.selectbox("选择班级", list(choices.keys()))]

    rows = roster_data(conn, cid)
    if not rows:
        st.info("该班级暂无学生")
        return
    df = pd.DataFrame(rows, columns=["学号", "姓名", "学籍分", "绩点分"])
    st.dataframe(df, use_container_width=True)


def class_report_page(conn):
    col1, col2 = st.columns(2)
    classes = class_list(conn)
    courses = course_list(conn)
    cmap = {f"{r[1]} ({r[2]}级)": r[0] for r in classes}
    gmap = {f"{r[1]} ({r[2]}学分)": r[0] for r in courses}
    cid = col1.selectbox("选择班级", list(cmap.keys()))
    gid = col2.selectbox("选择课程", list(gmap.keys()))
    class_id = cmap[cid]
    course_id = gmap[gid]

    rows = class_report_data(conn, class_id, course_id)
    if not rows or not rows[0][0]:
        st.info("暂无成绩")
        return
    avg_s, max_s, min_s, pass_r, count = rows[0]
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("平均分", avg_s)
    c2.metric("最高分", max_s)
    c3.metric("最低分", min_s)
    c4.metric("及格率", f"{pass_r}%")
    c5.metric("人数", count)


def class_grade_roster_page(conn):
    classes = class_list(conn)
    cmap = {f"{r[1]} ({r[2]}级)": r[0] for r in classes}
    cid = st.selectbox("选择班级", list(cmap.keys()))
    class_id = cmap[cid]
    rows = grade_roster_data(conn, class_id)
    if not rows:
        st.info("该班级暂无成绩")
        return
    df = pd.DataFrame(rows, columns=["姓名", "学号", "课程", "教师", "学期", "成绩"])
    st.dataframe(df, use_container_width=True)


def teacher_info_page(conn):
    tno = st.text_input("输入教师工号")
    if not tno:
        return
    rows = teacher_info_data(conn, tno)
    if not rows:
        st.error("教师不存在")
        return
    r = rows[0]
    c1, c2, c3 = st.columns(3)
    c1.metric("工号", r[0])
    c2.metric("姓名", r[1])
    c3.metric("职称", r[2] or "-")
    c1, c2, c3 = st.columns(3)
    c1.metric("排课数", r[3])
    c2.metric("选课学生", r[4])
    c3.metric("已录入成绩", r[5])


def teacher_list_page(conn):
    rows = teacher_list_data(conn)
    if not rows:
        st.info("暂无教师")
        return
    df = pd.DataFrame(
        rows, columns=["工号", "姓名", "职称", "排课数", "选课学生", "已录入"]
    )
    st.dataframe(df, use_container_width=True)


def backup_page(_conn):
    if st.button("备份数据库"):
        os.makedirs("backup", exist_ok=True)
        name = f'backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.sql'
        r = subprocess.run(
            [
                "mysqldump",
                "-u",
                "root",
                "--databases",
                "db_sms",
                "--routines",
                "--triggers",
                "--add-drop-table",
                "--default-character-set=utf8mb4",
                f"--result-file=backup/{name}",
            ],
            capture_output=True,
            text=True,
            check=False,
            shell=False,
        )
        if r.returncode == 0:
            st.success(f"备份成功: backup/{name}")
        else:
            st.error(r.stderr[:200])


def restore_page(_conn):
    file = st.file_uploader("选择备份文件 (.sql)", type="sql")

    # 上传文件后立即保存到 session_state，防止 button 点击重跑时丢失
    if file is not None:
        st.session_state["_restore_sql_bytes"] = file.getvalue()

    if "_restore_sql_bytes" not in st.session_state:
        st.info("请上传一个 .sql 备份文件")
        return

    if st.button("确认恢复（覆盖当前数据！）", type="primary"):
        content = (
            "SET FOREIGN_KEY_CHECKS=0;\n"
            + st.session_state["_restore_sql_bytes"].decode("utf-8")
            + "\nSET FOREIGN_KEY_CHECKS=1;"
        )
        r = subprocess.run(
            ["mysql", "-u", "root", "--default-character-set=utf8mb4"],
            input=content,
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=False,
            shell=False,
        )
        if r.returncode == 0:
            st.success("恢复成功！请重启应用")
            del st.session_state["_restore_sql_bytes"]
        else:
            st.error(r.stderr.strip() or "恢复失败，请检查备份文件是否完整")


# ---- 管理类页面 ----


def class_manage_page(conn):
    # 显示上次操作的消息（跨 st.rerun 存活）
    if st.session_state.get("msg"):
        _, m = st.session_state.pop("msg")
        st.toast(m, icon="✅")

    rows = class_list(conn)
    df = pd.DataFrame(rows, columns=["ID", "班级名", "年级", "专业", "状态"])
    st.dataframe(df, use_container_width=True)

    label_map = {f"{r[1]} ({r[2]}级 {r[3]})": r[0] for r in rows}
    labels = list(label_map.keys())
    id_map = {r[0]: (r[1], r[2], r[3], r[4]) for r in rows}

    mode = st.radio("操作", ["新增", "修改", "删除"], horizontal=True)

    if mode == "新增":
        name = st.text_input("班级名", key="ca_name")
        grade = st.text_input("年级", key="ca_grade")
        major = st.text_input("专业", key="ca_major")
        if st.button("新增班级", key="btn_ca"):
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO class (name,grade,major) VALUES (%s,%s,%s)",
                [name, grade, major],
            )
            conn.commit()
            st.session_state.msg = ("success", "新增成功")
            for k in ["ca_name", "ca_grade", "ca_major"]:
                st.session_state.pop(k, None)
            st.rerun()

    elif mode == "修改":
        sel = st.selectbox("选择要修改的班级", labels, key="class_edit_sel")
        if sel:
            class_id = label_map[sel]
            name, grade, major, status = id_map[class_id]
            new_name = st.text_input("班级名", value=name, key=f"ce_name_{class_id}")
            new_grade = st.text_input("年级", value=grade, key=f"ce_grade_{class_id}")
            new_major = st.text_input("专业", value=major, key=f"ce_major_{class_id}")
            new_status = st.selectbox(
                "状态",
                ["在读", "毕业"],
                index=0 if status == "在读" else 1,
                key=f"ce_status_{class_id}",
            )
            if st.button("保存修改", key=f"save_class_{class_id}"):
                cur = conn.cursor()
                cur.execute(
                    "UPDATE class SET name=%s,grade=%s,major=%s,status=%s WHERE id=%s",
                    [
                        new_name,
                        new_grade,
                        new_major,
                        1 if new_status == "在读" else 0,
                        class_id,
                    ],
                )
                conn.commit()
                st.session_state.msg = ("success", "修改成功")
                st.rerun()

    elif mode == "删除":
        sel = st.selectbox("选择要删除的班级", labels, key="class_del_sel")
        if sel and st.button("确认删除", type="primary"):
            class_id = label_map[sel]
            cur = conn.cursor()
            cur.execute("UPDATE class SET is_deleted=1 WHERE id=%s", [class_id])
            conn.commit()
            st.session_state.msg = ("success", "删除成功")
            st.rerun()


def course_manage_page(conn):
    if st.session_state.get("msg"):
        _, m = st.session_state.pop("msg")
        st.toast(m, icon="✅")
    rows = course_list(conn)
    df = pd.DataFrame(rows, columns=["ID", "课程名", "学分", "状态"])
    st.dataframe(df, use_container_width=True)
    lmap = {f"{r[1]} ({r[2]}学分)": r[0] for r in rows}
    imap = {r[0]: (r[1], r[2]) for r in rows}
    labels = list(lmap.keys())

    mode = st.radio("操作", ["新增", "修改", "删除"], horizontal=True)

    if mode == "新增":
        name = st.text_input("课程名", key="coa_name")
        credit = st.text_input("学分", key="coa_credit")
        if st.button("新增课程", key="btn_coa"):
            cur = conn.cursor()
            # 先检查该课程名是否已存在（含已删除的）
            cur.execute("SELECT id, is_deleted FROM course WHERE name = %s", [name])
            existing = cur.fetchone()
            if existing:
                if existing[1] == 1:
                    # 已逻辑删除 → 恢复
                    cur.execute(
                        "UPDATE course SET is_deleted=0, credit=%s, status=1 WHERE id=%s",
                        [credit, existing[0]],
                    )
                    conn.commit()
                    st.session_state.msg = (
                        "success",
                        "课程已恢复（之前已删除，现已还原）",
                    )
                else:
                    st.warning("课程名已存在，请使用其他名称")
            else:
                cur.execute(
                    "INSERT INTO course (name,credit) VALUES (%s,%s)", [name, credit]
                )
                conn.commit()
                st.session_state.msg = ("success", "新增成功")
            if st.session_state.get("msg"):
                for k in ["coa_name", "coa_credit"]:
                    st.session_state.pop(k, None)
                st.rerun()

    elif mode == "修改":
        sel = st.selectbox("选择要修改的课程", labels, key="course_edit_sel")
        if sel:
            cid = lmap[sel]
            name, credit = imap[cid]
            new_name = st.text_input("课程名", value=name, key=f"coe_name_{cid}")
            new_credit = st.text_input(
                "学分", value=str(credit), key=f"coe_credit_{cid}"
            )
            if st.button("保存修改", key=f"save_course_{cid}"):
                cur = conn.cursor()
                # 如果改了名称，检查新名称是否冲突
                if new_name != name:
                    cur.execute(
                        "SELECT id, is_deleted FROM course WHERE name = %s AND id != %s",
                        [new_name, cid],
                    )
                    dup = cur.fetchone()
                    if dup:
                        if dup[1] == 1:
                            st.warning(
                                "该课程名已被删除的课程占用，请先在数据库手动处理"
                            )
                        else:
                            st.warning("课程名已存在，请使用其他名称")
                        st.stop()
                cur.execute(
                    "UPDATE course SET name=%s,credit=%s WHERE id=%s",
                    [new_name, new_credit, cid],
                )
                conn.commit()
                st.session_state.msg = ("success", "修改成功")
                st.rerun()

    elif mode == "删除":
        sel = st.selectbox("选择要删除的课程", labels, key="course_del_sel")
        if sel and st.button("确认删除", type="primary"):
            cid = lmap[sel]
            cur = conn.cursor()
            cur.execute("UPDATE course SET is_deleted=1 WHERE id=%s", [cid])
            conn.commit()
            st.session_state.msg = ("success", "删除成功")
            st.rerun()


def enrollment_manage_page(conn):
    if st.session_state.get("msg"):
        _, m = st.session_state.pop("msg")
        st.toast(m, icon="✅")
    rows = enrollment_list(conn)
    if not rows:
        st.info("暂无选课记录")
        return
    df = pd.DataFrame(
        rows, columns=["选课ID", "学生", "学号", "课程", "教师", "学期", "成绩"]
    )
    st.dataframe(df, use_container_width=True)

    emap = {f"#{r[0]} {r[1]} → {r[3]} ({r[5]})": r[0] for r in rows}
    sel = st.selectbox("选择要退选的记录", list(emap.keys()))
    if sel and st.button("强制退选", type="primary"):
        cur = conn.cursor()
        cur.execute("UPDATE enrollment SET is_deleted=1 WHERE id=%s", [emap[sel]])
        conn.commit()
        st.session_state.msg = ("success", "退选成功")
        st.rerun()


def teacher_manage_page(conn):
    if st.session_state.get("msg"):
        _, m = st.session_state.pop("msg")
        st.toast(m, icon="✅")
    rows = teacher_full_list(conn)
    df = pd.DataFrame(rows, columns=["ID", "姓名", "工号", "职称", "电话", "状态"])
    st.dataframe(df, use_container_width=True)

    lmap = {f"{r[1]} ({r[2]})": r[0] for r in rows}
    imap = {r[0]: (r[1], r[2], r[3], r[4]) for r in rows}
    labels = list(lmap.keys())

    mode = st.radio("操作", ["新增", "修改", "删除"], horizontal=True)

    if mode == "新增":
        name = st.text_input("姓名", key="ta_name")
        no = st.text_input("工号", key="ta_no")
        title = st.text_input("职称（可空）", key="ta_title")
        phone = st.text_input("电话（可空）", key="ta_phone")
        if st.button("新增教师", key="btn_ta"):
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO teacher (name,no,title,phone) VALUES (%s,%s,%s,%s)",
                [name, no, title or None, phone or None],
            )
            conn.commit()
            st.session_state.msg = ("success", "新增成功")
            for k in ["ta_name", "ta_no", "ta_title", "ta_phone"]:
                st.session_state.pop(k, None)
            st.rerun()

    elif mode == "修改":
        sel = st.selectbox("选择要修改的教师", labels, key="t_edit")
        if sel:
            tid = lmap[sel]
            name, no, title, phone = imap[tid]
            new_name = st.text_input("姓名", value=name, key=f"te_name_{tid}")
            new_no = st.text_input("工号", value=no, key=f"te_no_{tid}")
            new_title = st.text_input("职称", value=title or "", key=f"te_title_{tid}")
            new_phone = st.text_input("电话", value=phone or "", key=f"te_phone_{tid}")
            if st.button("保存修改", key=f"save_teacher_{tid}"):
                cur = conn.cursor()
                cur.execute(
                    "UPDATE teacher SET name=%s,no=%s,title=%s,phone=%s WHERE id=%s",
                    [new_name, new_no, new_title or None, new_phone or None, tid],
                )
                conn.commit()
                st.session_state.msg = ("success", "修改成功")
                st.rerun()

    elif mode == "删除":
        sel = st.selectbox("选择要删除的教师", labels, key="t_del")
        if sel and st.button("确认删除", type="primary"):
            tid = lmap[sel]
            cur = conn.cursor()
            cur.execute("UPDATE teacher SET is_deleted=1 WHERE id=%s", [tid])
            conn.commit()
            st.session_state.msg = ("success", "删除成功")
            st.rerun()


def student_manage_page(conn):
    if st.session_state.get("msg"):
        _, m = st.session_state.pop("msg")
        st.toast(m, icon="✅")
    rows = student_full_list(conn)
    df = pd.DataFrame(rows, columns=["ID", "姓名", "学号", "班级ID", "班级", "状态"])
    st.dataframe(df, use_container_width=True)
    classes = class_list(conn)
    clmap = {f"{r[1]} ({r[2]}级 {r[3]})": r[0] for r in classes}  # 班级标签→ID
    slmap = {f"{r[1]} ({r[2]})": r[0] for r in rows}  # 学生标签→ID
    simap = {r[0]: (r[1], r[2], r[3]) for r in rows}  # 学生ID→(name,no,class_id)
    slabels = list(slmap.keys())
    clabels = list(clmap.keys())

    mode = st.radio("操作", ["新增", "修改", "删除"], horizontal=True)

    if mode == "新增":
        name = st.text_input("姓名", key="sa_name")
        no = st.text_input("学号", key="sa_no")
        cid = st.selectbox("班级", clabels, key="sa_class")
        if st.button("新增学生", key="btn_sa"):
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO student (name,no,class_id) VALUES (%s,%s,%s)",
                [name, no, clmap[cid]],
            )
            conn.commit()
            st.session_state.msg = ("success", "新增成功")
            for k in ["sa_name", "sa_no", "sa_class"]:
                st.session_state.pop(k, None)
            st.rerun()

    elif mode == "修改":
        sel = st.selectbox("选择要修改的学生", slabels, key="s_edit")
        if sel:
            stid = slmap[sel]
            name, no, cur_cid = simap[stid]
            cur_clabel = [k for k, v in clmap.items() if v == cur_cid][0]
            new_name = st.text_input("姓名", value=name, key=f"se_name_{stid}")
            new_no = st.text_input("学号", value=no, key=f"se_no_{stid}")
            new_cid = st.selectbox(
                "班级", clabels, index=clabels.index(cur_clabel), key=f"se_class_{stid}"
            )
            if st.button("保存修改", key=f"save_student_{stid}"):
                cur = conn.cursor()
                cur.execute(
                    "UPDATE student SET name=%s,no=%s,class_id=%s WHERE id=%s",
                    [new_name, new_no, clmap[new_cid], stid],
                )
                conn.commit()
                st.session_state.msg = ("success", "修改成功")
                st.rerun()

    elif mode == "删除":
        sel = st.selectbox("选择要删除的学生", slabels, key="s_del")
        if sel and st.button("确认删除", type="primary"):
            stid = slmap[sel]
            cur = conn.cursor()
            cur.execute("UPDATE student SET is_deleted=1 WHERE id=%s", [stid])
            conn.commit()
            st.session_state.msg = ("success", "删除成功")
            st.rerun()


def offering_manage_page(conn):
    if st.session_state.get("msg"):
        _, m = st.session_state.pop("msg")
        st.toast(m, icon="✅")
    rows = offering_full_list(conn)
    df = pd.DataFrame(
        rows,
        columns=[
            "ID",
            "课程",
            "教师",
            "学期",
            "已选",
            "上限",
            "状态",
            "course_id",
            "teacher_id",
        ],
    )
    st.dataframe(
        df[["ID", "课程", "教师", "学期", "已选", "上限", "状态"]],
        use_container_width=True,
    )
    courses = course_list(conn)
    clmap = {f"{r[1]} ({r[2]}学分)": r[0] for r in courses}
    olmap = {f"#{r[0]} {r[1]}-{r[2]} ({r[3]})": r[0] for r in rows}

    mode = st.radio("操作", ["新增", "修改", "删除"], horizontal=True)

    if mode == "新增":
        cid = st.selectbox("课程", list(clmap.keys()), key="oa_course")
        course_id = clmap[cid]
        teachers = teacher_course_teachers(conn, course_id)
        if not teachers:
            st.warning("该课程暂无能上的教师")
            tid = st.selectbox(
                "教师", ["（无可用教师）"], disabled=True, key="oa_teacher"
            )
        else:
            tlmap = {f"{r[1]} ({r[2]})": r[0] for r in teachers}
            tid = st.selectbox("教师", list(tlmap.keys()), key="oa_teacher")
        # 学期下拉：当前年份前后各3年
        this_year = datetime.now().year
        sem_options = [
            f"{y}-{y + 1}-{s}"
            for y in range(this_year - 3, this_year + 2)
            for s in (1, 2)
        ]
        sem = st.selectbox("学期", sem_options, key="oa_sem")
        max_s = st.number_input("上限", min_value=1, value=30, key="oa_max")
        st.caption("选课开始")
        c1, c2 = st.columns([3, 1])
        start_date = c1.date_input(
            "日期", key="oa_start_date", label_visibility="collapsed"
        )
        start_time = c2.text_input(
            "时间", value="00:00", key="oa_start_time", label_visibility="collapsed"
        )
        st.caption("选课截止")
        c1, c2 = st.columns([3, 1])
        end_date = c1.date_input(
            "日期", key="oa_end_date", label_visibility="collapsed"
        )
        end_time = c2.text_input(
            "时间", value="23:59", key="oa_end_time", label_visibility="collapsed"
        )
        st.caption("成绩截止")
        c1, c2 = st.columns([3, 1])
        dl_date = c1.date_input(
            "日期", key="oa_deadline_date", label_visibility="collapsed"
        )
        dl_time = c2.text_input(
            "时间", value="23:59", key="oa_deadline_time", label_visibility="collapsed"
        )
        if st.button("新增排课", key="btn_oa"):
            if not teachers:
                st.error("该课程暂无能上的教师，请重新选择课程")
            else:
                try:
                    cur = conn.cursor()
                    cur.execute(
                        """INSERT INTO course_offering
                        (course_id,teacher_id,semester,max_students,
                         enroll_start_time,enroll_end_time,grade_deadline)
                        VALUES (%s,%s,%s,%s,%s,%s,%s)""",
                        [
                            course_id,
                            tlmap[tid],
                            sem,
                            max_s,
                            f"{start_date} {start_time}:00",
                            f"{end_date} {end_time}:00",
                            f"{dl_date} {dl_time}:00",
                        ],
                    )
                    conn.commit()
                    st.session_state.msg = ("success", "新增成功")
                    for k in [
                        "oa_course",
                        "oa_teacher",
                        "oa_sem",
                        "oa_max",
                        "oa_start_date",
                        "oa_start_time",
                        "oa_end_date",
                        "oa_end_time",
                        "oa_deadline_date",
                        "oa_deadline_time",
                    ]:
                        st.session_state.pop(k, None)
                    st.rerun()
                except pymysql.Error as e:
                    st.error(f"新增失败：{e}")

    elif mode == "修改":
        sel = st.selectbox("选择要修改的排课", list(olmap.keys()), key="o_edit")
        if sel:
            oid = olmap[sel]
            cur = conn.cursor()
            cur.execute(
                """SELECT semester, max_students, enroll_start_time,
                enroll_end_time, grade_deadline FROM course_offering WHERE id=%s""",
                [oid],
            )
            row = cur.fetchone()
            # 学期：当前值不在列表中则追加
            sem_opts = [
                f"{y}-{y + 1}-{s}"
                for y in range(datetime.now().year - 3, datetime.now().year + 2)
                for s in (1, 2)
            ]
            cur_sem = str(row[0])
            if cur_sem not in sem_opts:
                sem_opts.insert(0, cur_sem)
            new_sem = st.selectbox(
                "学期", sem_opts, index=sem_opts.index(cur_sem), key=f"oe_sem_{oid}"
            )
            new_max = st.number_input(
                "上限", min_value=1, value=int(row[1]), key=f"oe_max_{oid}"
            )
            # 日期+时间 拆分
            s_d, s_t = str(row[2])[:10], str(row[2])[11:16]
            e_d, e_t = str(row[3])[:10], str(row[3])[11:16]
            d_d, d_t = str(row[4])[:10], str(row[4])[11:16]
            st.caption("选课开始")
            c1, c2 = st.columns([3, 1])
            new_sd = c1.date_input(
                "日期",
                value=datetime.strptime(s_d, "%Y-%m-%d").date(),
                key=f"oe_start_date_{oid}",
                label_visibility="collapsed",
            )
            new_st = c2.text_input(
                "时间",
                value=s_t,
                key=f"oe_start_time_{oid}",
                label_visibility="collapsed",
            )
            st.caption("选课截止")
            c1, c2 = st.columns([3, 1])
            new_ed = c1.date_input(
                "日期",
                value=datetime.strptime(e_d, "%Y-%m-%d").date(),
                key=f"oe_end_date_{oid}",
                label_visibility="collapsed",
            )
            new_et = c2.text_input(
                "时间",
                value=e_t,
                key=f"oe_end_time_{oid}",
                label_visibility="collapsed",
            )
            st.caption("成绩截止")
            c1, c2 = st.columns([3, 1])
            new_dd = c1.date_input(
                "日期",
                value=datetime.strptime(d_d, "%Y-%m-%d").date(),
                key=f"oe_deadline_date_{oid}",
                label_visibility="collapsed",
            )
            new_dt = c2.text_input(
                "时间",
                value=d_t,
                key=f"oe_deadline_time_{oid}",
                label_visibility="collapsed",
            )
            if st.button("保存修改", key=f"save_offering_{oid}"):
                try:
                    cur = conn.cursor()
                    cur.execute(
                        """UPDATE course_offering
                        SET semester=%s,max_students=%s,enroll_start_time=%s,
                        enroll_end_time=%s,grade_deadline=%s WHERE id=%s""",
                        [
                            new_sem,
                            new_max,
                            f"{new_sd} {new_st}:00",
                            f"{new_ed} {new_et}:00",
                            f"{new_dd} {new_dt}:00",
                            oid,
                        ],
                    )
                    conn.commit()
                    st.session_state.msg = ("success", "修改成功")
                    st.rerun()
                except pymysql.Error as e:
                    st.error(f"修改失败：{e}")

    elif mode == "删除":
        sel = st.selectbox("选择要删除的排课", list(olmap.keys()), key="o_del")
        if sel and st.button("确认删除", type="primary"):
            oid = olmap[sel]
            cur = conn.cursor()
            cur.execute("UPDATE course_offering SET is_deleted=1 WHERE id=%s", [oid])
            conn.commit()
            st.session_state.msg = ("success", "删除成功")
            st.rerun()


def _make_page(fn, *args):
    """创建带数据库连接的导航页面包装器"""

    def wrapper():
        conn = connect()
        try:
            fn(conn, *args)
        finally:
            conn.close()

    wrapper.__name__ = fn.__name__
    return wrapper


def _login_page():
    st.title("学生成绩管理系统")
    user_input = st.text_input("请输入学号/工号（教务输入 admin）")
    if st.button("登录"):
        conn = connect()
        cur = conn.cursor()
        if user_input == "admin":
            st.session_state.user = ("admin", 0, "教务管理员", "admin")
        else:
            cur.execute(
                "SELECT id, name FROM teacher WHERE no=%s AND is_deleted=0",
                [user_input],
            )
            row = cur.fetchone()
            if row:
                st.session_state.user = ("teacher", row[0], row[1], user_input)
            else:
                cur.execute(
                    "SELECT id, name FROM student WHERE no=%s AND is_deleted=0",
                    [user_input],
                )
                row = cur.fetchone()
                if row:
                    st.session_state.user = ("student", row[0], row[1], user_input)
                else:
                    st.error("用户不存在")
        conn.close()
        if st.session_state.user:
            st.rerun()


# 初始化
if "user" not in st.session_state:
    st.session_state.user = None

# 侧边栏 —— 身份信息
with st.sidebar:
    if st.session_state.user:
        role, uid, uname, uno = st.session_state.user
        st.write(f"欢迎，{uname}")
        st.caption(f"角色：{role}")

# 构建导航页面（始终调用 st.navigation，避免侧边栏残留）
if not st.session_state.user:
    pages = [st.Page(_login_page, title="登录", icon="🔑")]
else:
    role, uid, uname, uno = st.session_state.user
    if role == "student":
        pages = [
            st.Page(_make_page(show_courses_page, uno), title="可选课程", icon="📚"),
            st.Page(_make_page(enroll_page, uno), title="选课", icon="✏️"),
            st.Page(_make_page(unenroll_page, uno), title="退选", icon="↩️"),
            st.Page(
                _make_page(my_grades_page, uid, uname), title="我的成绩", icon="📊"
            ),
            st.Page(_make_page(semester_avg_page, uno), title="学期均分", icon="📈"),
        ]
    elif role == "teacher":
        pages = [
            st.Page(_make_page(grade_input_page, uno), title="录入成绩", icon="📝"),
            st.Page(_make_page(batch_grade_page, uno), title="批量录入CSV", icon="📂"),
            st.Page(_make_page(my_students_page, uno), title="查看课程学生", icon="👥"),
        ]
    elif role == "admin":
        pages = {
            "📊 数据查看": [
                st.Page(_make_page(summary_page), title="数据概览", icon="📋"),
                st.Page(_make_page(roster_page), title="班级学生名单", icon="📄"),
                st.Page(_make_page(class_report_page), title="班级成绩统计", icon="📈"),
                st.Page(
                    _make_page(class_grade_roster_page), title="班级成绩明细", icon="📑"
                ),
                st.Page(_make_page(teacher_info_page), title="教师信息", icon="👤"),
                st.Page(_make_page(teacher_list_page), title="教师列表", icon="📜"),
            ],
            "🔧 数据管理": [
                st.Page(_make_page(class_manage_page), title="班级管理", icon="🏫"),
                st.Page(_make_page(course_manage_page), title="课程管理", icon="📖"),
                st.Page(
                    _make_page(teacher_manage_page), title="教师管理", icon="👨‍🏫"
                ),
                st.Page(
                    _make_page(student_manage_page), title="学生管理", icon="👨‍🎓"
                ),
                st.Page(_make_page(offering_manage_page), title="排课管理", icon="📅"),
                st.Page(
                    _make_page(enrollment_manage_page), title="选课管理", icon="📝"
                ),
            ],
            "💾 系统工具": [
                st.Page(_make_page(backup_page), title="备份数据", icon="💾"),
                st.Page(_make_page(restore_page), title="恢复数据", icon="🔄"),
            ],
        }
    else:
        pages = []  # 兜底：未知角色

pg = st.navigation(pages)
pg.run()

if st.session_state.user:
    with st.sidebar:
        st.divider()
        if st.button("🚪 退出登录"):
            st.session_state.user = None
            st.rerun()
