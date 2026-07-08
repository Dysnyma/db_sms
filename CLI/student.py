"""学生功能"""
from core.utils import cls, pause, hr, input_choice


def menu(conn, sid, sname, sno):
    while True:
        cls()
        hr()
        print(f'  {sname} 同学 [学生]')
        hr()
        print('  1. 查询可选课程')
        print('  2. 选课')
        print('  3. 退选')
        print('  4. 查看我的成绩')
        print('  5. 查看学期均分')
        print('  0. 退出登录')
        hr()
        c = input_choice('  请选择: ')
        if c == 0:
            break
        elif c == 1:
            show_courses(conn, sno)
            pause()
        elif c == 2:
            enroll(conn, sno)
            pause()
        elif c == 3:
            unenroll(conn, sno)
            pause()
        elif c == 4:
            my_grades(conn, sid, sname)
            pause()
        elif c == 5:
            semester_avg(conn, sno)
            pause()


def show_courses(conn, sno):
    # with写法可以实现用完自动关掉
    with conn.cursor() as cur:
        cur.callproc('sp_show_courses', [sno])
        rows = cur.fetchall()
        cur.nextset()
    if not rows:
        print('\n  没有可选课程')
        return
    hr()
    print(f'  ID	课程名	学分	教师	名额	截止时间')
    hr()
    for r in rows:
        print(f'  {r[0]}	{r[1]}	{r[2]}	{r[3]}	{r[5]}	{str(r[7])[:16]}')


def enroll(conn, sno):
    show_courses(conn, sno)
    plan_id = input('\n  请输入要选的排课ID (0=取消): ').strip()
    if plan_id == '0' or not plan_id:
        return
    try:
        with conn.cursor() as cur:
            cur.callproc('sp_enroll', [sno, int(plan_id)])
            conn.commit()
            print(f'\n  ✅ {cur.fetchone()[0]}')
    except Exception as e:
        print(f'\n  ❌ {e}')


def unenroll(conn, sno):
    plan_id = input('  请输入要退的排课ID (0=取消): ').strip()
    if plan_id == '0' or not plan_id:
        return
    try:
        with conn.cursor() as cur:
            cur.callproc('sp_unenroll', [sno, int(plan_id)])
            conn.commit()
            print(f'\n  ✅ {cur.fetchone()[0]}')
    except Exception as e:
        print(f'\n  ❌ {e}')


def my_grades(conn, sid, sname):
    cur = conn.cursor()
    cur.execute("""
        SELECT c.name, t.name, co.semester, e.score
        FROM enrollment e
        JOIN course_offering co ON e.offering_id = co.id
        JOIN course c ON co.course_id = c.id
        JOIN teacher t ON co.teacher_id = t.id
        WHERE e.student_id = %s AND e.is_deleted = 0
        ORDER BY co.semester, c.name
    """, [sid])
    rows = cur.fetchall()
    cur.nextset()
    if not rows:
        print('\n  暂无成绩')
        return
    hr()
    print(f'  {sname} 的成绩单')
    hr()
    for cname, tname, sem, score in rows:
        sc = str(score) if score is not None else '未录入'
        print(f'  {sem}	{cname}	{tname}	{sc}')
    cur.execute("SELECT weighted_score, gpa FROM student WHERE id = %s", [sid])
    ws, gpa = cur.fetchone()
    hr()
    print(f'  学籍分: {ws}    绩点分: {gpa}')


def semester_avg(conn, sno):
    sem = input('  请输入学期 (如 2024-2025-1): ').strip()
    if not sem:
        return
    with conn.cursor() as cur:
        cur.callproc('sp_student_semester_avg', [sno, sem])
        rows = cur.fetchall()
        cur.nextset()
    if not rows:
        print(f'\n  {sem} 暂无成绩')
        return
    for r in rows:
        print(f'\n  学期: {r[2]}  课程数: {r[3]}  均分: {r[4]}')
