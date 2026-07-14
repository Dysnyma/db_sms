"""管理员页面（Streamlit）"""

import os
import subprocess
from datetime import datetime
import pandas as pd
import pymysql
import streamlit as st
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
from core.config import get_connection


def _sem_options():
    """生成学期选项列表（当前年份前后各 3 年）"""
    this_year = datetime.now().year
    return [
        f"{y}-{y + 1}-{s}" for y in range(this_year - 3, this_year + 2) for s in (1, 2)
    ]


def summary_page(conn):
    """数据概览页面"""
    data = summary(conn, False)
    cols = st.columns(6)
    for i, (label, val) in enumerate(data.items()):
        cols[i % 6].metric(label, val)


def roster_page(conn):
    """班级学生名单页面"""
    classes = class_list(get_connection())
    choices = {f"{r[1]} ({r[2]}级 {r[3]}) — {r[4]}": r[0] for r in classes}
    cid = choices[st.selectbox("选择班级", list(choices.keys()))]

    try:
        rows = roster_data(conn, cid)
    except pymysql.OperationalError as e:
        st.error(f"查询失败（数据库繁忙），请稍后重试：{e}")
        return
    if not rows:
        st.info("该班级暂无学生")
        return
    df = pd.DataFrame(rows, columns=["学号", "姓名", "学籍分", "绩点分"])
    st.dataframe(df, use_container_width=True)


def class_report_page(conn):
    """班级成绩统计页面"""
    col1, col2 = st.columns(2)
    classes = class_list(get_connection())
    courses = course_list(get_connection())
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
    """班级成绩明细页面"""
    classes = class_list(get_connection())
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
    """教师信息查询页面"""
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
    """教师列表页面"""
    rows = teacher_list_data(conn)
    if not rows:
        st.info("暂无教师")
        return
    df = pd.DataFrame(
        rows, columns=["工号", "姓名", "职称", "排课数", "选课学生", "已录入"]
    )
    st.dataframe(df, use_container_width=True)


def backup_page(_conn):
    # 函数开头先消费消息（rerun 后依然能读取并显示）
    if st.session_state.get("conn_reset_msg"):
        st.success(st.session_state.pop("conn_reset_msg"))

    if st.button("备份数据库"):
        os.makedirs("backup", exist_ok=True)
        name = f'backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.sql'
        try:
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
        except FileNotFoundError:
            st.error("未找到 mysqldump 命令，请确保 MySQL 已安装且在 PATH 中")
        except Exception as e:
            st.error(f"备份失败：{e}")

    st.divider()

    if st.button("🔄 重置数据库连接缓存"):
        from core.config import get_engine
        # 关闭当前页面传入的旧连接
        try:
            _conn.close()
        except Exception:
            pass
        # 清空缓存的连接池引擎
        get_engine.clear()
        st.session_state.conn_reset_msg = "连接池引擎缓存已清空，页面将自动重建连接"
        st.rerun()


def _safe_decode_sql(raw: bytes) -> str:
    """多重编码回退：UTF-8 → GBK → 忽略不可解码字节"""
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError:
        pass
    try:
        return raw.decode("gbk")
    except UnicodeDecodeError:
        return raw.decode("utf-8", errors="ignore")


def restore_page(_conn):
    """数据库恢复页面（临时文件 + mysql 命令导入）"""
    import tempfile

    file = st.file_uploader("选择备份文件 (.sql)", type="sql")

    if file is not None:
        st.session_state["_restore_sql_bytes"] = file.getvalue()

    if "_restore_sql_bytes" not in st.session_state:
        st.info("请上传一个 .sql 备份文件")
        return

    if st.button("确认恢复（覆盖当前数据！）", type="primary", key="btn_restore"):
        tmp_path = None
        try:
            # 先提交当前连接未完成的事务，释放表锁，防止 DDL 死锁
            _conn.commit()

            # 1. 安全解码：UTF-8 → GBK → 容错跳过
            sql_content = _safe_decode_sql(st.session_state["_restore_sql_bytes"])
            full_script = (
                "SET FOREIGN_KEY_CHECKS=0;\n"
                + sql_content
                + "\nSET FOREIGN_KEY_CHECKS=1;"
            )

            # 2. 写入临时文件，避免 Windows 管道死锁
            with tempfile.NamedTemporaryFile(
                mode="w",
                suffix=".sql",
                delete=False,
                encoding="utf-8",
            ) as tmp:
                tmp.write(full_script)
                tmp_path = tmp.name

            # 3. 通过文件流 stdin 执行 mysql，指定目标数据库 db_sms
            # 如果 root 有密码，请取消注释下行的 -p：
            #   "-p123456",   ← -p 和密码之间没有空格！
            with open(tmp_path, "r", encoding="utf-8") as f:
                r = subprocess.run(
                    [
                        "mysql",
                        "-u",
                        "root",
                        # "-p123456",
                        "--default-character-set=utf8mb4",
                        "db_sms",
                    ],
                    stdin=f,
                    capture_output=True,
                    text=True,
                    check=False,
                    shell=False,
                )

            if r.returncode == 0:
                st.success("恢复成功！请重启应用")
                del st.session_state["_restore_sql_bytes"]
            else:
                # mysql 可能将错误信息输出到 stdout，两者都检查
                error_msg = r.stderr.strip() or r.stdout.strip()
                st.error(f"恢复失败：{error_msg}")
        except FileNotFoundError:
            st.error(
                "未找到 mysql 命令！请确保 MySQL 的 bin 目录已加入 PATH，"
                "或将下方命令中的 'mysql' 改为绝对路径，例如：\n"
                "r'C:/Program Files/MySQL/MySQL Server 8.0/bin/mysql.exe'"
            )
        except Exception as e:
            st.error(f"恢复过程发生异常：{e}")
        finally:
            # 4. 确保临时文件被清理
            if tmp_path and os.path.exists(tmp_path):
                try:
                    os.unlink(tmp_path)
                except OSError:
                    pass


def class_manage_page(conn):
    """班级管理页面：新增 / 修改 / 删除"""
    # 显示上次操作的消息（跨 st.rerun 存活）
    if st.session_state.get("msg"):
        _, m = st.session_state.pop("msg")
        st.success(m)

    rows = class_list(get_connection())
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
            try:
                with conn.cursor() as cur:
                    cur.execute(
                        "INSERT INTO class (name,grade,major) VALUES (%s,%s,%s)",
                        [name, grade, major],
                    )
                conn.commit()
                st.session_state.msg = ("success", "新增成功")
            except pymysql.Error as e:
                conn.rollback()
                st.error(f"新增失败：{e}")
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
                try:
                    with conn.cursor() as cur:
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
                except pymysql.Error as e:
                    conn.rollback()
                    st.error(f"修改失败：{e}")
                st.rerun()

    elif mode == "删除":
        sel = st.selectbox("选择要删除的班级", labels, key="class_del_sel")
        if sel and st.button("确认删除", type="primary"):
            class_id = label_map[sel]
            try:
                with conn.cursor() as cur:
                    cur.execute("UPDATE class SET is_deleted=1 WHERE id=%s", [class_id])
                conn.commit()
                st.session_state.msg = ("success", "删除成功")
            except pymysql.Error as e:
                conn.rollback()
                st.error(f"删除失败：{e}")
            st.rerun()


def course_manage_page(conn):
    """课程管理页面：新增（含已删除恢复）/ 修改 / 删除"""
    if st.session_state.get("msg"):
        _, m = st.session_state.pop("msg")
        st.success(m)
    rows = course_list(get_connection())
    df = pd.DataFrame(rows, columns=["ID", "课程名", "学分", "状态"])
    st.dataframe(df, use_container_width=True)
    lmap = {f"{r[1]} ({r[2]}学分)": r[0] for r in rows}
    imap = {r[0]: (r[1], r[2]) for r in rows}
    labels = list(lmap.keys())

    mode = st.radio("操作", ["新增", "修改", "删除"], horizontal=True)

    if mode == "新增":
        name = st.text_input("课程名", key="coa_name")
        credit = st.number_input(
            "学分", min_value=0.0, max_value=20.0, value=3.0, step=0.5, key="coa_credit"
        )
        if st.button("新增课程", key="btn_coa"):
            with conn.cursor() as cur:
                # 先检查该课程名是否已存在（含已删除的）
                cur.execute("SELECT id, is_deleted FROM course WHERE name = %s", [name])
                existing = cur.fetchone()
                if existing:
                    if existing[1] == 1:
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
                        st.error("课程名已存在，请使用其他名称")
                else:
                    try:
                        cur.execute(
                            "INSERT INTO course (name,credit) VALUES (%s,%s)",
                            [name, credit],
                        )
                        conn.commit()
                        st.session_state.msg = ("success", "新增成功")
                    except pymysql.Error as e:
                        conn.rollback()
                        st.error(f"新增失败：{e}")
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
            new_credit = st.number_input(
                "学分",
                min_value=0.0,
                max_value=20.0,
                value=float(credit) or 0.0,
                step=0.5,
                key=f"coe_credit_{cid}",
            )
            if st.button("保存修改", key=f"save_course_{cid}"):
                with conn.cursor() as cur:
                    # 如果改了名称，检查新名称是否冲突
                    if new_name != name:
                        cur.execute(
                            "SELECT id, is_deleted FROM course WHERE name = %s AND id != %s",
                            [new_name, cid],
                        )
                        dup = cur.fetchone()
                        if dup:
                            if dup[1] == 1:
                                st.error("该课程名已被删除的课程占用，请先在数据库手动处理")
                            else:
                                st.error("课程名已存在，请使用其他名称")
                            return
                    try:
                        cur.execute(
                            "UPDATE course SET name=%s,credit=%s WHERE id=%s",
                            [new_name, new_credit, cid],
                        )
                        conn.commit()
                        st.session_state.msg = ("success", "修改成功")
                        st.rerun()
                    except pymysql.Error as e:
                        conn.rollback()
                        st.error(f"修改失败：{e}")

    elif mode == "删除":
        sel = st.selectbox("选择要删除的课程", labels, key="course_del_sel")
        if sel and st.button("确认删除", type="primary"):
            cid = lmap[sel]
            try:
                with conn.cursor() as cur:
                    cur.execute("UPDATE course SET is_deleted=1 WHERE id=%s", [cid])
                conn.commit()
                st.session_state.msg = ("success", "删除成功")
            except pymysql.Error as e:
                conn.rollback()
                st.error(f"删除失败：{e}")
            st.rerun()


def enrollment_manage_page(conn):
    """选课管理页面：查看选课记录并支持强制退选"""
    if st.session_state.get("msg"):
        _, m = st.session_state.pop("msg")
        st.success(m)
    rows = enrollment_list(get_connection())
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
        try:
            with conn.cursor() as cur:
                cur.execute("UPDATE enrollment SET is_deleted=1 WHERE id=%s", [emap[sel]])
            conn.commit()
            st.session_state.msg = ("success", "退选成功")
        except pymysql.Error as e:
            conn.rollback()
            st.error(f"退选失败：{e}")
        st.rerun()


def teacher_manage_page(conn):
    """教师管理页面：新增 / 修改 / 删除"""
    if st.session_state.get("msg"):
        _, m = st.session_state.pop("msg")
        st.success(m)
    rows = teacher_full_list(get_connection())
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
            try:
                with conn.cursor() as cur:
                    cur.execute(
                        "INSERT INTO teacher (name,no,title,phone) VALUES (%s,%s,%s,%s)",
                        [name, no, title or None, phone or None],
                    )
                conn.commit()
                st.session_state.msg = ("success", "新增成功")
            except pymysql.Error as e:
                conn.rollback()
                st.error(f"新增失败：{e}")
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
                try:
                    with conn.cursor() as cur:
                        cur.execute(
                            "UPDATE teacher SET name=%s,no=%s,title=%s,phone=%s WHERE id=%s",
                            [new_name, new_no, new_title or None, new_phone or None, tid],
                        )
                    conn.commit()
                    st.session_state.msg = ("success", "修改成功")
                except pymysql.Error as e:
                    conn.rollback()
                    st.error(f"修改失败：{e}")
                st.rerun()

    elif mode == "删除":
        sel = st.selectbox("选择要删除的教师", labels, key="t_del")
        if sel and st.button("确认删除", type="primary"):
            tid = lmap[sel]
            try:
                with conn.cursor() as cur:
                    cur.execute("UPDATE teacher SET is_deleted=1 WHERE id=%s", [tid])
                conn.commit()
                st.session_state.msg = ("success", "删除成功")
            except pymysql.Error as e:
                conn.rollback()
                st.error(f"删除失败：{e}")
            st.rerun()


def student_manage_page(conn):
    """学生管理页面：新增（含已删除恢复）/ 修改 / 删除"""
    if st.session_state.get("msg"):
        _, m = st.session_state.pop("msg")
        st.success(m)
    rows = student_full_list(get_connection())
    df = pd.DataFrame(rows, columns=["ID", "姓名", "学号", "班级ID", "班级", "状态"])
    st.dataframe(df, use_container_width=True)
    classes = class_list(get_connection())
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
            with conn.cursor() as cur:
                # 先检查该学号是否已存在（含已删除的）
                cur.execute("SELECT id, is_deleted FROM student WHERE no = %s", [no])
                existing = cur.fetchone()
                if existing:
                    if existing[1] == 1:
                        # 已逻辑删除 → 恢复
                        cur.execute(
                            "UPDATE student SET is_deleted=0, name=%s, class_id=%s WHERE id=%s",
                            [name, clmap[cid], existing[0]],
                        )
                        conn.commit()
                        st.session_state.msg = (
                            "success",
                            f"学号 {no} 已恢复（之前已删除，现已还原）",
                        )
                        for k in ["sa_name", "sa_no", "sa_class"]:
                            st.session_state.pop(k, None)
                        st.rerun()
                    else:
                        st.error(f"学号 {no} 已存在，请使用其他学号")
                else:
                    try:
                        cur.execute(
                            "INSERT INTO student (name,no,class_id) VALUES (%s,%s,%s)",
                            [name, no, clmap[cid]],
                        )
                        conn.commit()
                        st.session_state.msg = ("success", "新增成功")
                        for k in ["sa_name", "sa_no", "sa_class"]:
                            st.session_state.pop(k, None)
                        st.rerun()
                    except pymysql.Error as e:
                        conn.rollback()
                        st.error(f"新增失败：{e}")

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
                try:
                    with conn.cursor() as cur:
                        cur.execute(
                            "UPDATE student SET name=%s,no=%s,class_id=%s WHERE id=%s",
                            [new_name, new_no, clmap[new_cid], stid],
                        )
                    conn.commit()
                    st.session_state.msg = ("success", "修改成功")
                except pymysql.Error as e:
                    conn.rollback()
                    st.error(f"修改失败：{e}")
                st.rerun()

    elif mode == "删除":
        sel = st.selectbox("选择要删除的学生", slabels, key="s_del")
        if sel and st.button("确认删除", type="primary"):
            stid = slmap[sel]
            try:
                with conn.cursor() as cur:
                    cur.execute("UPDATE student SET is_deleted=1 WHERE id=%s", [stid])
                conn.commit()
                st.session_state.msg = ("success", "删除成功")
            except pymysql.Error as e:
                conn.rollback()
                st.error(f"删除失败：{e}")
            st.rerun()


def offering_manage_page(conn):
    """排课管理页面：新增 / 修改 / 删除"""
    if st.session_state.get("msg"):
        _, m = st.session_state.pop("msg")
        st.success(m)
    rows = offering_full_list(get_connection())
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
    courses = course_list(get_connection())
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
        sem = st.selectbox("学期", _sem_options(), key="oa_sem")
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
                    with conn.cursor() as cur:
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
                    conn.rollback()
                    st.error(f"新增失败：{e}")

    elif mode == "修改":
        sel = st.selectbox("选择要修改的排课", list(olmap.keys()), key="o_edit")
        if sel:
            oid = olmap[sel]
            with conn.cursor() as cur:
                cur.execute(
                    """SELECT semester, max_students, enroll_start_time,
                    enroll_end_time, grade_deadline FROM course_offering WHERE id=%s""",
                    [oid],
                )
                row = cur.fetchone()
                # 学期：当前值不在列表中则追加
                cur_sem = str(row[0])
                sem_opts = list(_sem_options())
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
                        with conn.cursor() as cur:
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
                        conn.rollback()
                        st.error(f"修改失败：{e}")

    elif mode == "删除":
        sel = st.selectbox("选择要删除的排课", list(olmap.keys()), key="o_del")
        if sel and st.button("确认删除", type="primary"):
            oid = olmap[sel]
            try:
                with conn.cursor() as cur:
                    cur.execute(
                        "UPDATE course_offering SET is_deleted=1 WHERE id=%s", [oid]
                    )
                conn.commit()
                st.session_state.msg = ("success", "删除成功")
            except pymysql.Error as e:
                conn.rollback()
                st.error(f"删除失败：{e}")
            st.rerun()
