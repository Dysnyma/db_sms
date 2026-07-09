import streamlit as st
from CLI.core.config import connect
from CLI.student import show_courses, my_grades, semester_avg, enrolled_courses
from CLI.teacher import teacher_offerings, offering_students
import csv
import pandas as pd
st.title('学生成绩管理系统')


def show_courses_page(conn, sno):
    rows = show_courses(conn, sno, False)
    if not rows:
        st.info('没有可选课程')
        return
    df = pd.DataFrame(rows, columns=[
        '排课ID', '课程名', '学分', '教师', '学期', '剩余名额', '选课开始', '选课截止'
    ])
    st.dataframe(df, use_container_width=True)


def my_grades_page(conn, sid, sname):
    rows, ws, gpa = my_grades(conn, sid, sname, paged=False)
    if not rows:
        st.info('暂无成绩')
        return
    df = pd.DataFrame(rows, columns=['课程', '教师', '学期', '成绩'])
    st.dataframe(df, use_container_width=True)
    col1, col2 = st.columns(2)
    col1.metric('学籍分', ws)
    col2.metric('绩点分', gpa)


def semester_avg_page(conn, sno):
    sem = st.text_input('学期 (如 2024-2025-1)')
    if not sem:
        st.info('请输入学期')
        return
    rows = semester_avg(conn, sno, sem=sem, paged=False)
    if not rows:
        st.info(f'{sem} 暂无成绩')
        return
    df = pd.DataFrame(rows, columns=['学号', '姓名', '学期', '课程数', '均分'])
    st.dataframe(df, use_container_width=True)


def enroll_page(conn, sno):
    rows = show_courses(conn, sno, paged=False)
    if not rows:
        st.info('没有可选课程')
        return
    df = pd.DataFrame(rows, columns=[
        '排课ID', '课程名', '学分', '教师', '学期', '剩余名额', '选课开始', '选课截止'])
    st.dataframe(df, use_container_width=True)

    choices = {f'#{r[0]} {r[1]} - {r[3]} ({r[2]}学分)': r[0] for r in rows}
    plan_id = choices[st.selectbox('选择要选的排课', list(choices.keys()))]
    if st.button('确认选课'):
        cur = conn.cursor()
        try:
            cur.callproc('sp_enroll', [sno, int(plan_id)])
            conn.commit()
            cur.fetchall()
            cur.nextset()
            st.success('选课成功')
        except Exception as e:
            st.error(str(e))


def unenroll_page(conn, sno):
    rows = enrolled_courses(conn, sno)
    if not rows:
        st.info('没有已选课程')
        return
    df = pd.DataFrame(rows, columns=['排课ID', '课程名', '教师', '学期', '选课截止'])
    st.dataframe(df, use_container_width=True)

    choices = {f'#{r[0]} {r[1]} - {r[2]}': r[0] for r in rows}
    plan_id = choices[st.selectbox('选择要退的排课', list(choices.keys()))]
    if st.button('确认退选'):
        cur = conn.cursor()
        try:
            cur.callproc('sp_unenroll', [sno, int(plan_id)])
            conn.commit()
            cur.fetchall()
            cur.nextset()
            st.success('退选成功')
        except Exception as e:
            st.error(str(e))


def grade_input_page(conn, tno):
    offerings = teacher_offerings(conn, tno)
    if not offerings:
        st.info('暂无排课')
        return
    choices = {f'#{r[0]} {r[1]} ({r[2]}) — {r[3]}/{r[4]}人': r[0]
               for r in offerings}
    plan_id = choices[st.selectbox('选择排课', list(choices.keys()))]

    students = offering_students(conn, plan_id)
    if not students:
        st.info('暂无学生选课')
        return
    df = pd.DataFrame(students, columns=['学号', '姓名', '成绩'])
    st.dataframe(df, use_container_width=True)

    col1, col2, col3 = st.columns(3)
    sno = col1.text_input('学生学号')
    score = col2.text_input('成绩 (0-100)')
    if col3.button('录入', key='grade_btn'):
        try:
            cur = conn.cursor()
            cur.callproc('sp_grade_input', [tno, plan_id, sno, float(score)])
            conn.commit()
            cur.fetchall()
            cur.nextset()
            st.success(f'{sno} → {score}')
            st.rerun()
        except Exception as e:
            st.error(str(e))


def batch_grade_page(conn, tno):
    file = st.file_uploader('上传 CSV（plan_id, student_no, score）', type='csv')
    if not file:
        return

    if st.button('开始导入'):
        content = file.read().decode('utf-8-sig')
        reader = csv.DictReader(content.splitlines())
        ok = fail = 0
        for row in reader:
            try:
                cur = conn.cursor()
                cur.callproc('sp_grade_input',
                             [tno, int(row['plan_id']), row['student_no'], float(row['score'])])
                conn.commit()
                cur.fetchall()
                cur.nextset()
                ok += 1
            except Exception as e:
                fail += 1
                st.warning(f"{row.get('student_no', '?')}: {e}")
        st.success(f'完成：成功 {ok} 条，失败 {fail} 条')
        st.rerun()


def my_students_page(conn, tno):
    offerings = teacher_offerings(conn, tno)
    if not offerings:
        st.info('暂无排课')
        return
    choices = {f'#{r[0]} {r[1]} ({r[2]}) — {r[3]}/{r[4]}人': r[0]
               for r in offerings}
    plan_id = choices[st.selectbox('选择排课', list(choices.keys()))]

    students = offering_students(conn, plan_id)
    if not students:
        st.info('暂无学生选课')
        return
    df = pd.DataFrame(students, columns=['学号', '姓名', '成绩'])
    st.dataframe(df, use_container_width=True)


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
            page = st.radio('菜单', ['录入成绩', '批量录入CSV', '查看课程学生'])
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
    elif role == 'student' and page == '选课':
        enroll_page(conn, uno)
    elif role == 'student' and page == '退选':
        unenroll_page(conn, uno)
    elif role == 'student' and page == '学期均分':
        semester_avg_page(conn, uno)
    elif role == 'teacher' and page == '录入成绩':
        grade_input_page(conn, uno)
    elif role == 'teacher' and page == '批量录入CSV':
        batch_grade_page(conn, uno)
    elif role == 'teacher' and page == '查看课程学生':
        my_students_page(conn, uno)
    conn.close()
