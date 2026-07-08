"""学生功能"""
from core.utils import cls, pause, hr, input_choice, render_menu


def menu(conn, sid, sname, sno):
    # lambda c: xxx(c, sno) 的意思是：
    # "包装一个只收 c(onn) 的函数，内部调用 xxx(c, sno)"
    # 这样 render_menu 统一传 func(conn) 时，sno 已经被填好了
    _items = [
        ('查询可选课程', lambda c: show_courses(c, sno)),
        ('选课',         lambda c: enroll(c, sno)),
        ('退选',         lambda c: unenroll(c, sno)),
        ('查看我的成绩', lambda c: my_grades(c, sid, sname)),
        ('查看学期均分', lambda c: semester_avg(c, sno)),
    ]
    while True:
        if render_menu(conn, f'{sname} 同学 [学生]', _items) == 'quit':
            break


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
