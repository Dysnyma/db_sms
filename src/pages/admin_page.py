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
from core.models import (
    ClassCreate,
    CourseCreate,
    CourseUpdate,
    TeacherCreate,
    TeacherUpdate,
    StudentCreate,
    StudentUpdate,
    TeacherQuery,
    validate_or_error,
)
from core.majors import all_majors, add_major, delete_major


def _sem_options():
    """生成学期选项列表（当前年份前后各 3 年）"""
    this_year = datetime.now().year
    return [
        f"{y}-{y + 1}-{s}" for y in range(this_year - 3, this_year + 2) for s in (1, 2)
    ]


def _check_times(start_date, start_hour, start_min,
                 end_date, end_hour, end_min,
                 deadline_date, deadline_hour, deadline_min):
    """校验时间顺序：开始 ≤ 截止 ≤ 成绩截止"""
    try:
        start_dt = datetime.strptime(
            f"{start_date} {start_hour:02d}:{start_min:02d}:00", "%Y-%m-%d %H:%M:%S")
        end_dt = datetime.strptime(
            f"{end_date} {end_hour:02d}:{end_min:02d}:00", "%Y-%m-%d %H:%M:%S")
        deadline_dt = datetime.strptime(
            f"{deadline_date} {deadline_hour:02d}:{deadline_min:02d}:00", "%Y-%m-%d %H:%M:%S")
    except ValueError:
        st.error("日期或时间无效")
        return False
    if not (start_dt <= end_dt):
        st.error("选课开始时间必须 ≤ 选课截止时间")
        return False
    if not (end_dt <= deadline_dt):
        st.error("选课截止时间必须 ≤ 成绩截止时间")
        return False
    return True


def summary_page(conn):
    """数据概览页面"""
    data = summary(conn, False)
    cols = st.columns(6)
    for i, (label, val) in enumerate(data.items()):
        cols[i % 6].metric(label, val)


def roster_page(conn):
    """班级学生名单页面"""
    classes = class_list(conn)
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
    """班级成绩明细页面"""
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
    """教师信息查询页面"""
    tno = st.text_input(
        "教师工号",
        placeholder="例如：T20240001",
        help="工号格式：T 开头 + 数字，如 T20240001",
        max_chars=20,
    )
    if not tno:
        return
    data = validate_or_error(TeacherQuery, no=tno)
    if data is None:
        return
    rows = teacher_info_data(conn, data["no"])

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

    rows = class_list(conn)
    df = pd.DataFrame(rows, columns=["ID", "班级名", "年级", "专业", "状态"])
    st.dataframe(df, use_container_width=True)

    label_map = {f"{r[1]} ({r[2]}级 {r[3]})": r[0] for r in rows}
    labels = list(label_map.keys())
    id_map = {r[0]: (r[1], r[2], r[3], r[4]) for r in rows}

    mode = st.radio("操作", ["新增", "修改", "删除"], horizontal=True)

    if mode == "新增":
        this_year = datetime.now().year
        grade_opts = [str(y) for y in range(this_year - 5, this_year + 5)]
        grade = st.selectbox("年级", grade_opts, index=5, key="ca_grade")
        majors = all_majors()
        major = st.selectbox("专业", majors, key="ca_major")

        # 自动生成班级名预览
        generated_name = None
        if grade and major:
            import re
            cur = conn.cursor()
            cur.execute(
                "SELECT name FROM class WHERE grade=%s AND major=%s AND is_deleted=0",
                [grade, major],
            )
            seq = 0
            for (name,) in cur.fetchall():
                m = re.search(r"(\d+)班$", name)
                if m:
                    n = int(m.group(1))
                    if n > seq:
                        seq = n
            generated_name = f"{grade}{major}{seq + 1}班"
            st.info(f"📌 将新增：**{generated_name}**")

        if st.button("新增班级", key="btn_ca"):
            if not generated_name:
                return
            data = validate_or_error(ClassCreate, name=generated_name, grade=grade, major=major)
            if data is None:
                return
            try:
                with conn.cursor() as cur:
                    cur.execute(
                        "INSERT INTO class (name,grade,major) VALUES (%s,%s,%s)",
                        [data["name"], data["grade"], data["major"]],
                    )
                conn.commit()
                st.session_state.msg = ("success", "新增成功")
            except pymysql.Error as e:
                conn.rollback()
                st.error(f"新增失败：{e}")
            for k in ["ca_grade", "ca_major"]:
                st.session_state.pop(k, None)
            st.rerun()

    elif mode == "修改":
        sel = st.selectbox("选择要修改的班级", labels, key="class_edit_sel")
        if sel:
            class_id = label_map[sel]
            name, grade, major, status = id_map[class_id]
            st.text(f"📌 班级名：{name}")
            st.text(f"📌 年级：{grade}级")
            st.text(f"📌 专业：{major}")
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
                            "UPDATE class SET status=%s WHERE id=%s",
                            [1 if new_status == "在读" else 0, class_id],
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
    rows = course_list(conn)
    df = pd.DataFrame(rows, columns=["ID", "课程名", "学分", "状态"])
    st.dataframe(df, use_container_width=True)
    lmap = {f"{r[1]} ({r[2]}学分)": r[0] for r in rows}
    imap = {r[0]: (r[1], r[2]) for r in rows}
    labels = list(lmap.keys())

    mode = st.radio("操作", ["新增", "修改", "删除"], horizontal=True)

    if mode == "新增":
        name = st.text_input(
            "课程名",
            placeholder="例如：数据库原理",
            help="课程名长度为 1-100 个字符",
            max_chars=100,
            key="coa_name",
        )
        credit = st.text_input(
            "学分", value="3.0", key="coa_credit", max_chars=4,
            help="学分范围为 0.5~30.0，步长 0.5",
        )
        if st.button("新增课程", key="btn_coa"):
            data = validate_or_error(CourseCreate, name=name, credit=credit)
            if data is None:
                return
            with conn.cursor() as cur:
                # 先检查该课程名是否已存在（含已删除的）
                cur.execute("SELECT id, is_deleted FROM course WHERE name = %s", [data["name"]])
                existing = cur.fetchone()
                if existing:
                    if existing[1] == 1:
                        cur.execute(
                            "UPDATE course SET is_deleted=0, credit=%s, status=1 WHERE id=%s",
                            [data["credit"], existing[0]],
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
                            [data["name"], data["credit"]],
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
            new_name = st.text_input(
                "课程名", value=name,
                placeholder="例如：数据库原理",
                help="课程名长度为 1-100 个字符",
                max_chars=100,
                key=f"coe_name_{cid}",
            )
            new_credit = st.text_input(
                "学分", value=f"{float(credit):.1f}" if credit else "3.0",
                key=f"coe_credit_{cid}", max_chars=4,
                help="学分范围为 0.5~30.0，步长 0.5",
            )
            if st.button("保存修改", key=f"save_course_{cid}"):
                data = validate_or_error(CourseUpdate, name=new_name, credit=new_credit)
                if data is None:
                    return
                with conn.cursor() as cur:
                    # 如果改了名称，检查新名称是否冲突
                    if data["name"] != name:
                        cur.execute(
                            "SELECT id, is_deleted FROM course WHERE name = %s AND id != %s",
                            [data["name"], cid],
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
                            [data["name"], data["credit"], cid],
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
    rows = teacher_full_list(conn)
    df = pd.DataFrame(rows, columns=["ID", "姓名", "工号", "职称", "电话", "状态"])
    st.dataframe(df, use_container_width=True)

    lmap = {f"{r[1]} ({r[2]})": r[0] for r in rows}
    imap = {r[0]: (r[1], r[2], r[3], r[4]) for r in rows}
    labels = list(lmap.keys())

    mode = st.radio("操作", ["新增", "修改", "删除"], horizontal=True)

    if mode == "新增":
        name = st.text_input(
            "姓名",
            placeholder="例如：张三",
            help="姓名长度为 1-50 个字符",
            max_chars=50,
            key="ta_name",
        )
        no = st.text_input(
            "工号",
            placeholder="例如：T20240001",
            help="工号格式：T 开头 + 数字，如 T20240001",
            max_chars=20,
            key="ta_no",
        )
        _title_opts = ["", "教授", "副教授", "讲师", "助教", "高级工程师", "工程师", "实验师", "研究员", "副研究员"]
        title = st.selectbox("职称", _title_opts, index=0, key="ta_title", format_func=lambda x: "（空）" if x == "" else x)
        phone = st.text_input(
            "电话（可空）",
            placeholder="例如：13800138000",
            help="电话为 7-15 位纯数字",
            max_chars=15,
            key="ta_phone",
        )
        if st.button("新增教师", key="btn_ta"):
            data = validate_or_error(TeacherCreate, name=name, no=no, title=title, phone=phone)
            if data is None:
                return
            try:
                with conn.cursor() as cur:
                    cur.execute(
                        "INSERT INTO teacher (name,no,title,phone) VALUES (%s,%s,%s,%s)",
                        [data["name"], data["no"], data.get("title"), data.get("phone")],
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
            new_name = st.text_input(
                "姓名", value=name,
                placeholder="例如：张三",
                help="姓名长度为 1-50 个字符",
                max_chars=50,
                key=f"te_name_{tid}",
            )
            new_no = st.text_input(
                "工号", value=no,
                placeholder="例如：T20240001",
                help="工号格式：T 开头 + 数字，如 T20240001",
                max_chars=20,
                key=f"te_no_{tid}",
            )
            _title_opts = ["", "教授", "副教授", "讲师", "助教", "高级工程师", "工程师", "实验师", "研究员", "副研究员"]
            _title_fmt = lambda x: "（空）" if x == "" else x
            default_idx = _title_opts.index(title) if title in _title_opts else 0
            new_title = st.selectbox("职称", _title_opts, index=default_idx, key=f"te_title_{tid}", format_func=_title_fmt)
            new_phone = st.text_input(
                "电话", value=phone or "",
                placeholder="例如：13800138000",
                help="电话为 7-15 位纯数字",
                max_chars=15,
                key=f"te_phone_{tid}",
            )
            if st.button("保存修改", key=f"save_teacher_{tid}"):
                data = validate_or_error(TeacherUpdate, name=new_name, no=new_no, title=new_title, phone=new_phone)
                if data is None:
                    return
                try:
                    with conn.cursor() as cur:
                        cur.execute(
                            "UPDATE teacher SET name=%s,no=%s,title=%s,phone=%s WHERE id=%s",
                            [data["name"], data["no"], data.get("title"), data.get("phone"), tid],
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
        name = st.text_input(
            "姓名",
            placeholder="例如：张三",
            help="姓名长度为 1-50 个字符",
            max_chars=50,
            key="sa_name",
        )
        no = st.text_input(
            "学号", key="sa_no", placeholder="例如：20240001",
            help="学号为 8-12 位纯数字，不可包含字母或符号",
            max_chars=12,
        )
        cid = st.selectbox("班级", clabels, key="sa_class")
        if st.button("新增学生", key="btn_sa"):
            data = validate_or_error(StudentCreate, name=name, no=no, class_id=clmap[cid])
            if data is None:
                return
            with conn.cursor() as cur:
                # 先检查该学号是否已存在（含已删除的）
                cur.execute("SELECT id, is_deleted FROM student WHERE no = %s", [data["no"]])
                existing = cur.fetchone()
                if existing:
                    if existing[1] == 1:
                        # 已逻辑删除 → 恢复
                        cur.execute(
                            "UPDATE student SET is_deleted=0, name=%s, class_id=%s WHERE id=%s",
                            [data["name"], data["class_id"], existing[0]],
                        )
                        conn.commit()
                        st.session_state.msg = (
                            "success",
                            f"学号 {data['no']} 已恢复（之前已删除，现已还原）",
                        )
                        for k in ["sa_name", "sa_no", "sa_class"]:
                            st.session_state.pop(k, None)
                        st.rerun()
                    else:
                        st.error(f"学号 {data['no']} 已存在，请使用其他学号")
                else:
                    try:
                        cur.execute(
                            "INSERT INTO student (name,no,class_id) VALUES (%s,%s,%s)",
                            [data["name"], data["no"], data["class_id"]],
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
            new_name = st.text_input(
                "姓名", value=name,
                placeholder="例如：张三",
                help="姓名长度为 1-50 个字符",
                max_chars=50,
                key=f"se_name_{stid}",
            )
            new_no = st.text_input(
                "学号", value=no,
                placeholder="例如：20240001",
                help="学号为 8-12 位纯数字，不可包含字母或符号",
                max_chars=12,
                key=f"se_no_{stid}",
            )
            new_cid = st.selectbox(
                "班级", clabels, index=clabels.index(cur_clabel), key=f"se_class_{stid}"
            )
            if st.button("保存修改", key=f"save_student_{stid}"):
                data = validate_or_error(StudentUpdate, name=new_name, no=new_no, class_id=clmap[new_cid])
                if data is None:
                    return
                try:
                    with conn.cursor() as cur:
                        cur.execute(
                            "UPDATE student SET name=%s,no=%s,class_id=%s WHERE id=%s",
                            [data["name"], data["no"], data["class_id"], stid],
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
        sem = st.selectbox("学期", _sem_options(), key="oa_sem")
        max_s = st.text_input("上限", value="30", key="oa_max", max_chars=5, placeholder="上限 1~99999", help="选课人数上限，1~99999")
        st.caption("选课开始")
        c1, c2, c3 = st.columns([3, 1, 1])
        start_date = c1.date_input(
            "日期", key="oa_start_date", label_visibility="collapsed"
        )
        start_hour = c2.selectbox(
            "时", options=range(24), index=0,
            key="oa_start_hour", label_visibility="collapsed",
        )
        start_min = c3.selectbox(
            "分", options=range(60), index=0,
            key="oa_start_min", label_visibility="collapsed",
        )
        st.caption("选课截止")
        c1, c2, c3 = st.columns([3, 1, 1])
        end_date = c1.date_input(
            "日期", key="oa_end_date", label_visibility="collapsed"
        )
        end_hour = c2.selectbox(
            "时", options=range(24), index=23,
            key="oa_end_hour", label_visibility="collapsed",
        )
        end_min = c3.selectbox(
            "分", options=range(60), index=59,
            key="oa_end_min", label_visibility="collapsed",
        )
        st.caption("成绩截止")
        c1, c2, c3 = st.columns([3, 1, 1])
        dl_date = c1.date_input(
            "日期", key="oa_deadline_date", label_visibility="collapsed"
        )
        dl_hour = c2.selectbox(
            "时", options=range(24), index=23,
            key="oa_dl_hour", label_visibility="collapsed",
        )
        dl_min = c3.selectbox(
            "分", options=range(60), index=59,
            key="oa_dl_min", label_visibility="collapsed",
        )
        if st.button("新增排课", key="btn_oa"):
            if not teachers:
                st.error("该课程暂无能上的教师，请重新选择课程")
            else:
                try:
                    max_s_val = int(max_s)
                except (ValueError, TypeError):
                    st.error("选课上限必须为整数")
                    return
                if max_s_val > 99999:
                    st.error("选课上限不能超过 99999")
                elif not _check_times(
                    start_date, start_hour, start_min,
                    end_date, end_hour, end_min,
                    dl_date, dl_hour, dl_min,
                ):
                    pass
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
                                    max_s_val,
                                    f"{start_date} {start_hour:02d}:{start_min:02d}:00",
                                    f"{end_date} {end_hour:02d}:{end_min:02d}:00",
                                    f"{dl_date} {dl_hour:02d}:{dl_min:02d}:00",
                                ],
                            )
                        conn.commit()
                        st.session_state.msg = ("success", "新增成功")
                        for k in [
                            "oa_course", "oa_teacher", "oa_sem", "oa_max",
                            "oa_start_date", "oa_start_hour", "oa_start_min",
                            "oa_end_date", "oa_end_hour", "oa_end_min",
                            "oa_deadline_date", "oa_dl_hour", "oa_dl_min",
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
            # 显示当前课程和教师（只读）
            for r in rows:
                if r[0] == oid:
                    st.info(f"📌 课程：{r[1]}　教师：{r[2]}　（如需更改请删除后重建）")
                    break
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
                new_max = st.text_input("上限", value=str(row[1]), key=f"oe_max_{oid}", max_chars=5, placeholder="上限 1~99999", help="选课人数上限，1~99999")
                # 日期+时间 拆分
                s_d, s_t = str(row[2])[:10], str(row[2])[11:16]
                e_d, e_t = str(row[3])[:10], str(row[3])[11:16]
                d_d, d_t = str(row[4])[:10], str(row[4])[11:16]
                s_h, s_m = s_t.split(":")
                e_h, e_m = e_t.split(":")
                d_h, d_m = d_t.split(":")
                st.caption("选课开始")
                c1, c2, c3 = st.columns([3, 1, 1])
                new_sd = c1.date_input(
                    "日期",
                    value=datetime.strptime(s_d, "%Y-%m-%d").date(),
                    key=f"oe_start_date_{oid}",
                    label_visibility="collapsed",
                )
                new_sh = c2.selectbox(
                    "时", options=range(24), index=int(s_h),
                    key=f"oe_start_hour_{oid}", label_visibility="collapsed",
                )
                new_sm = c3.selectbox(
                    "分", options=range(60), index=int(s_m),
                    key=f"oe_start_min_{oid}", label_visibility="collapsed",
                )
                st.caption("选课截止")
                c1, c2, c3 = st.columns([3, 1, 1])
                new_ed = c1.date_input(
                    "日期",
                    value=datetime.strptime(e_d, "%Y-%m-%d").date(),
                    key=f"oe_end_date_{oid}",
                    label_visibility="collapsed",
                )
                new_eh = c2.selectbox(
                    "时", options=range(24), index=int(e_h),
                    key=f"oe_end_hour_{oid}", label_visibility="collapsed",
                )
                new_em = c3.selectbox(
                    "分", options=range(60), index=int(e_m),
                    key=f"oe_end_min_{oid}", label_visibility="collapsed",
                )
                st.caption("成绩截止")
                c1, c2, c3 = st.columns([3, 1, 1])
                new_dd = c1.date_input(
                    "日期",
                    value=datetime.strptime(d_d, "%Y-%m-%d").date(),
                    key=f"oe_deadline_date_{oid}",
                    label_visibility="collapsed",
                )
                new_dh = c2.selectbox(
                    "时", options=range(24), index=int(d_h),
                    key=f"oe_dl_hour_{oid}", label_visibility="collapsed",
                )
                new_dm = c3.selectbox(
                    "分", options=range(60), index=int(d_m),
                    key=f"oe_dl_min_{oid}", label_visibility="collapsed",
                )
                if st.button("保存修改", key=f"save_offering_{oid}"):
                    try:
                        new_max_val = int(new_max)
                    except (ValueError, TypeError):
                        st.error("选课上限必须为整数")
                        return
                    if new_max_val > 99999:
                        st.error("选课上限不能超过 99999")
                    elif _check_times(
                        new_sd, new_sh, new_sm,
                        new_ed, new_eh, new_em,
                        new_dd, new_dh, new_dm,
                    ):
                        try:
                            with conn.cursor() as cur:
                                cur.execute(
                                    """UPDATE course_offering
                                    SET semester=%s,max_students=%s,enroll_start_time=%s,
                                    enroll_end_time=%s,grade_deadline=%s WHERE id=%s""",
                                    [
                                        new_sem,
                                        new_max_val,
                                        f"{new_sd} {new_sh:02d}:{new_sm:02d}:00",
                                        f"{new_ed} {new_eh:02d}:{new_em:02d}:00",
                                        f"{new_dd} {new_dh:02d}:{new_dm:02d}:00",
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


def major_manage_page(_conn):
    """专业管理页面：查看 / 新增 / 删除"""
    if st.session_state.get("msg"):
        _, m = st.session_state.pop("msg")
        st.success(m)

    majors = all_majors()
    df = pd.DataFrame(majors, columns=["专业名称"])
    st.dataframe(df, use_container_width=True)

    col1, col2 = st.columns([3, 1])
    new_name = col1.text_input(
        "新增专业",
        placeholder="例如：物联网工程",
        help="专业名 1-50 个字符，不能包含逗号且不能重复",
        max_chars=50,
        key="ma_new",
    )
    if col2.button("添加", key="btn_ma"):
        err = add_major(new_name)
        if err:
            st.error(err)
        else:
            st.session_state.msg = ("success", f"专业「{new_name}」已添加")
            st.session_state.pop("ma_new", None)
            st.rerun()

    st.divider()
    if majors:
        del_sel = st.selectbox("选择要删除的专业", majors, key="ma_del")
        if st.button("删除专业", type="primary"):
            cur = _conn.cursor()
            cur.execute(
                "SELECT COUNT(*) FROM class WHERE major = %s AND is_deleted = 0",
                [del_sel],
            )
            count = cur.fetchone()[0]
            if count > 0:
                st.error(f"还有 {count} 个班级属于「{del_sel}」，请先处理这些班级")
            else:
                err = delete_major(del_sel)
                if err:
                    st.error(err)
                else:
                    st.session_state.msg = ("success", f"专业「{del_sel}」已删除")
                    st.rerun()
