"""测试员 —— 身份切换 → 调真实菜单，零重复代码"""
from core.utils import cls, show_table
from student import menu as student_menu
from teacher import menu as teacher_menu
from admin import menu as admin_menu


def _pick_student(conn):
    """列出前5个学生，按编号选择，返回 (id, name, no)"""
    cur = conn.cursor()
    cur.execute("""
        SELECT s.id, s.name, s.no, c.name
        FROM student s JOIN class c ON s.class_id = c.id
        WHERE s.is_deleted = 0 ORDER BY s.no
    """)
    rows = cur.fetchall()
    if not rows:
        print('\n  暂无学生')
        return None, None, None
    show_rows = rows[:5]
    show_table(['#', '学号', '姓名', '班级'],
               [[i + 1, r[2], r[1], r[3]] for i, r in enumerate(show_rows)])
    if len(rows) > 5:
        print(f'  ...还有 {len(rows)-5} 人（共 {len(rows)} 人）')
    try:
        n = int(input('  选第几个（0=取消）: '))
        if 1 <= n <= len(show_rows):
            r = rows[n - 1]
            return r[0], r[1], r[2]
    except ValueError:
        pass
    return None, None, None


def _pick_teacher(conn):
    """列出前5个教师，按编号选择，返回 (id, name, no)"""
    cur = conn.cursor()
    cur.execute("""
        SELECT id, name, no, IFNULL(title,'-')
        FROM teacher WHERE is_deleted = 0 ORDER BY no
    """)
    rows = cur.fetchall()
    if not rows:
        print('\n  暂无教师')
        return None, None, None
    show_rows = rows[:5]
    show_table(['#', '工号', '姓名', '职称'],
               [[i + 1, r[2], r[1], r[3]] for i, r in enumerate(show_rows)])
    if len(rows) > 5:
        print(f'  ...还有 {len(rows)-5} 人（共 {len(rows)} 人）')
    try:
        n = int(input('  选第几个（0=取消）: '))
        if 1 <= n <= len(show_rows):
            r = rows[n - 1]
            return r[0], r[1], r[2]
    except ValueError:
        pass
    return None, None, None


def menu(conn, tid, tname, tno):
    while True:
        cls()
        print()
        print('  测试员 — 选择身份进入:')
        print('  S. 切换学生 → 进入学生端')
        print('  T. 切换教师 → 进入教师端')
        print('  A. 进入教务端')
        print('  0. 退出')
        print()
        c = input('  请选择: ').strip().lower()

        if c == '0':
            break
        elif c == 's':
            sid, sname, sno = _pick_student(conn)
            if sid:
                student_menu(conn, sid, sname, sno)
        elif c == 't':
            tid, tname, tno = _pick_teacher(conn)
            if tid:
                teacher_menu(conn, tid, tname, tno)
        elif c == 'a':
            admin_menu(conn)
