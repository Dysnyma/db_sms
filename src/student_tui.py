"""学生功能"""

import pymysql
from core.utils import cls, render_menu, show_table, Paginator


def menu(conn, sid, sname, sno):
    """显示功能菜单并循环等待用户选择"""
    # lambda c: xxx(c, sno) 的意思是：
    # "包装一个只收 c(onn) 的函数，内部调用 xxx(c, sno)"
    # 这样 render_menu 统一传 func(conn) 时，sno 已经被填好了
    _items = [
        ("查询可选课程", lambda c: show_courses(c, sno)),
        ("选课", lambda c: enroll(c, sno)),
        ("退选", lambda c: unenroll(c, sno)),
        ("查看我的成绩", lambda c: my_grades(c, sid, sname)),
        ("查看学期均分", lambda c: semester_avg(c, sno)),
    ]
    while True:
        if render_menu(conn, f"{sname} 同学 [学生]", _items) == "quit":
            break


def show_courses(conn, sno, paged=True):
    """查询当前学生的可选课程列表"""
    with conn.cursor() as cur:
        cur.callproc("sp_show_courses", [sno])
        rows = cur.fetchall()
        cur.nextset()
    if not rows:
        print("\n  没有可选课程")
        return []

    if not paged:
        return rows

    pager = Paginator(rows)
    while True:
        cls()
        show_table(
            ["排课ID", "课程名", "学分", "教师", "名额", "截止时间"],
            [[r[0], r[1], r[2], r[3], r[5], str(r[7])[:16]] for r in pager.items],
        )
        print(f"  {pager.info}")
        print("  [N]下一页  [P]上一页  [Q]返回")
        c = input("  请选择: ").strip().lower()
        if c == "q":
            break
        elif c == "n":
            pager.next()
        elif c == "p":
            pager.prev()


def enroll(conn, sno):
    """学生选课"""
    rows = show_courses(conn, sno, paged=False)
    if not rows:
        return
    plan_id = input("\n  请输入要选的排课ID (0=取消): ").strip()
    if plan_id == "0" or not plan_id:
        return
    try:
        with conn.cursor() as cur:
            cur.callproc("sp_enroll", [sno, int(plan_id)])
            conn.commit()
            print(f"\n  ✅ {cur.fetchone()[0]}")
    except pymysql.Error as e:
        print(f"\n  ❌ {e}")


def unenroll(conn, sno):
    """学生退选"""
    plan_id = input("  请输入要退的排课ID (0=取消): ").strip()
    if plan_id == "0" or not plan_id:
        return
    try:
        with conn.cursor() as cur:
            cur.callproc("sp_unenroll", [sno, int(plan_id)])
            conn.commit()
            print(f"\n  ✅ {cur.fetchone()[0]}")
    except pymysql.Error as e:
        print(f"\n  ❌ {e}")


def my_grades(conn, sid, _sname, paged=True):
    """查询当前学生的成绩列表及学籍分、绩点分"""
    cur = conn.cursor()
    cur.execute(
        """
        SELECT c.name, t.name, co.semester, e.score
        FROM enrollment e
        JOIN course_offering co ON e.offering_id = co.id
        JOIN course c ON co.course_id = c.id
        JOIN teacher t ON co.teacher_id = t.id
        WHERE e.student_id = %s AND e.is_deleted = 0
        ORDER BY co.semester, c.name
    """,
        [sid],
    )
    rows = cur.fetchall()
    cur.execute("SELECT weighted_score, gpa FROM student WHERE id = %s", [sid])
    ws, gpa = cur.fetchone()

    if not paged:
        return rows, ws, gpa

    if not rows:
        print("\n  暂无成绩")
        return

    pager = Paginator(rows)
    while True:
        cls()
        show_table(
            ["课程", "教师", "学期", "成绩"],
            [
                [r[0], r[1], r[2], str(r[3]) if r[3] is not None else "未录入"]
                for r in pager.items
            ],
        )
        print(f"  学籍分: {ws}    绩点分: {gpa}")
        print(f"  {pager.info}")
        print("  [N]下一页  [P]上一页  [Q]返回")
        c = input("  请选择: ").strip().lower()
        if c == "q":
            break
        elif c == "n":
            pager.next()
        elif c == "p":
            pager.prev()


def semester_avg(conn, sno, sem=None, paged=True):
    """查询当前学期平均分"""
    if sem is None:
        sem = input("  请输入学期 (如 2024-2025-1): ").strip()
    if not sem:
        return None
    with conn.cursor() as cur:
        cur.callproc("sp_student_semester_avg", [sno, sem])
        rows = cur.fetchall()
        cur.nextset()
    if not paged:
        return rows
    if not rows:
        print(f"\n  {sem} 暂无成绩")
        return
    for r in rows:
        print(f"\n  学期: {r[2]}  课程数: {r[3]}  均分: {r[4]}")


def enrolled_courses(conn, sno):
    """返回学生已选课程（供 Streamlit 用）"""
    cur = conn.cursor()
    cur.execute(
        """
        SELECT co.id, c.name, t.name, co.semester, co.enroll_end_time
        FROM enrollment e
        JOIN course_offering co ON e.offering_id = co.id
        JOIN course c ON co.course_id = c.id
        JOIN teacher t ON co.teacher_id = t.id
        WHERE e.student_id = fn_get_student_id(%s)
          AND e.is_deleted = 0
        ORDER BY co.semester, c.name
    """,
        [sno],
    )
    return cur.fetchall()
