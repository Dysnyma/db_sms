import streamlit as st
from CLI.core.config import connect
from CLI.student import show_courses
import pandas as pd
st.title('学生成绩管理系统')


def show_courses_page(conn, sno):
    rows = show_courses(conn, sno, False)
    if not rows:
        st.info('没有可选课程')
        return
    df = pd.DataFrame(rows, columns=[
        '排课ID', '课程名', '学分', '教师', '剩余名额', '选课开始', '选课截止'
    ])
    st._dialog_decorator(df, use_container_width=True)


def my_grades_page(conn, uid, uname):
    return


# 初始化
if 'user' not in st.session_state:
    st.session_state.user = None

# 已登录 → 显示内容
if st.session_state.user:
    role, uid, uname, uno = st.session_state.user
    st.success(f'欢迎，{uname} [{role}]')
    if st.button('退出登录'):
        st.session_state.user = None
        st.rerun()

# 未登录 → 显示登录表单
else:
    user_input = st.text_input('请输入学号/工号 (教务输入 admin)')
    if st.button('登录'):
        conn = connect()
        cur = conn.cursor()
        # 复刻 auth.py 的登录逻辑
        if user_input == 'admin':
            st.session_state.user = ('admin', 0, '教务管理员', 'admin')
        else:
            cur.execute(
                "SELECT id, name FROM teacher WHERE no=%s AND is_deleted=0", [user_input])
            row = cur.fetchone()
            if row:
                st.session_state.user = (
                    'teacher', row[0], row[1], user_input)
            else:
                cur.execute(
                    "SELECT id, name FROM student WHERE no=%s AND is_deleted=0", [user_input])
                row = cur.fetchone()
                if row:
                    st.session_state.user = (
                        'student', row[0], row[1], user_input)
                else:
                    st.error('用户不存在')
        conn.close()
        if st.session_state.user:
            st.rerun()

if st.session_state.user:
    role, uid, uname, uno = st.session_state.user

    # 侧边栏 —— 菜单 + 身份
    with st.sidebar:
        st.write(f'欢迎，{uname}')
        st.caption(f'角色：{role}')

        if role == 'student':
            page = st.radio('菜单', ['可选课程', '选课', '退选', '我的成绩', '学期均分'])
        elif role == 'teacher':
            page = st.radio('菜单', ['录入成绩', '查看课程学生'])
        elif role == 'admin':
            page = st.radio('菜单', ['数据概览', '班级管理', '课程管理', '教师管理',
                                   '学生管理', '排课管理', '选课管理', '备份恢复'])

        if st.button('退出登录'):
            st.session_state.user = None
            st.rerun()

    # 主区域 —— 根据菜单显示对应内容
    conn = connect()
    if role == 'student' and page == '可选课程':
        show_courses_page(conn, uno)
    elif role == 'student' and page == '我的成绩':
        my_grades_page(conn, uid, uname)
    conn.close()
