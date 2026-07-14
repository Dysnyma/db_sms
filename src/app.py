"""学生成绩管理系统 —— Streamlit 主入口（导航 + 页面路由）"""

import csv
import os
import streamlit as st

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
from core.config import get_connection
from pages.student import (
    show_courses_page,
    my_grades_page,
    semester_avg_page,
    enroll_page,
    unenroll_page,
)
from pages.teacher import grade_input_page, batch_grade_page, my_students_page
from pages.admin_page import (
    summary_page,
    roster_page,
    class_report_page,
    class_grade_roster_page,
    teacher_info_page,
    teacher_list_page,
    class_manage_page,
    course_manage_page,
    teacher_manage_page,
    student_manage_page,
    offering_manage_page,
    enrollment_manage_page,
    major_manage_page,
    backup_page,
    restore_page,
)

st.set_page_config(page_title="学生成绩管理系统", page_icon="🎓", layout="wide")


def _make_page(fn, *args):
    """创建带数据库连接的导航页面包装器（自动归还连接到池）"""

    def wrapper():
        conn = get_connection()
        try:
            fn(conn, *args)
        finally:
            conn.close()

    wrapper.__name__ = fn.__name__
    return wrapper


def _validate_login_input(user_input: str) -> str | None:
    """校验登录输入格式，返回错误信息或 None"""
    import re

    raw = user_input.strip()
    if not raw:
        return "请输入学号/工号"
    if raw == "admin":
        return None
    if raw.startswith("T"):
        # 教师工号
        if not re.match(r"^T\d+$", raw):
            return "工号格式：T 开头 + 数字，如 T20240001"
        if len(raw) > 20:
            return "工号长度不能超过 20 位"
    else:
        # 学生学号
        if not raw.isdigit():
            return "学号只能包含纯数字"
        if len(raw) < 8:
            return "学号不能少于 8 位"
        if len(raw) > 12:
            return "学号不能超过 12 位"
    return None


def _login_page():
    """登录页面：验证学号/工号，识别角色并写入 session_state"""
    st.title("学生成绩管理系统")

    def _on_quick_select():
        st.session_state.login_input = st.session_state.quick_select

    # 从 CSV 读取测试账号
    _test_accounts = [("admin", "admin")]
    with open(os.path.join(_ROOT, "data", "teacher.csv"), encoding="utf-8") as _f:
        for _r in csv.DictReader(_f):
            if _r.get("status", "1") == "1":
                _test_accounts.append((_r["no"], _r["no"]))
                if sum(1 for a in _test_accounts if a[1].startswith("T")) >= 3:
                    break
    with open(os.path.join(_ROOT, "data", "student.csv"), encoding="utf-8") as _f:
        for _r in csv.DictReader(_f):
            if _r.get("status", "1") == "1":
                _test_accounts.append((_r["no"], _r["no"]))
                if sum(1 for a in _test_accounts if a[1].isdigit()) >= 3:
                    break
    _labels, _vals = zip(*_test_accounts)

    user_input = st.text_input("账号", max_chars=20, key="login_input", placeholder="请输入学号/工号")
    st.selectbox("快速选择", _labels, key="quick_select", on_change=_on_quick_select)
    login_clicked = st.button("登录", type="primary", use_container_width=True)
    if login_clicked:
        # 格式校验
        err = _validate_login_input(user_input)
        if err:
            st.error(err)
            return

        conn = get_connection()
        try:
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
                        st.session_state.user = (
                            "student",
                            row[0],
                            row[1],
                            user_input,
                        )
                    else:
                        st.error("用户不存在")
        finally:
            conn.close()
        if st.session_state.user:
            st.rerun()


# 初始化
if "user" not in st.session_state:
    st.session_state.user = None

# 侧边栏 —— 身份信息 & 退出
with st.sidebar:
    if st.session_state.user:
        role, uid, uname, uno = st.session_state.user
        st.write(f"欢迎，{uname}")
        st.caption(f"角色：{role}")
        st.divider()
        if st.button("🚪 退出登录"):
            st.session_state.user = None
            st.rerun()

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
                st.Page(
                    _make_page(class_manage_page),
                    title="班级管理",
                    icon="🏫",
                ),
                st.Page(
                    _make_page(course_manage_page),
                    title="课程管理",
                    icon="📖",
                ),
                st.Page(
                    _make_page(teacher_manage_page),
                    title="教师管理",
                    icon="👨‍🏫",
                ),
                st.Page(
                    _make_page(student_manage_page),
                    title="学生管理",
                    icon="👨‍🎓",
                ),
                st.Page(
                    _make_page(major_manage_page),
                    title="专业管理",
                    icon="📚",
                ),
                st.Page(
                    _make_page(offering_manage_page),
                    title="排课管理",
                    icon="📅",
                ),
                st.Page(
                    _make_page(enrollment_manage_page),
                    title="选课管理",
                    icon="📝",
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
