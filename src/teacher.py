"""教师功能"""
import csv
import os
from core.utils import cls, pause, hr, input_choice, render_menu, show_table, Paginator


def menu(conn, tid, tname, tno):
    _items = [
        ('录入成绩', lambda c: grade_input(c, tno)),
        ('批量录入 (CSV)', lambda c: batch_grade_input(c, tno)),
        ('查看我的课程学生', lambda c: my_students(c, tid, tname)),
    ]
    while True:
        if render_menu(conn, f'{tname} 老师 [教师]', _items) == 'quit':
            break


def grade_input(conn, tno):
    """两步：先选排课 → 再录成绩，循环直到 Q"""
    cur = conn.cursor()

    # Step 1: 列出该老师的所有排课
    cur.execute("""
        SELECT co.id, c.name, co.semester, co.current_students, co.max_students
        FROM course_offering co
        JOIN course c ON co.course_id = c.id
        WHERE co.teacher_id = fn_get_teacher_id(%s) AND co.is_deleted = 0
        ORDER BY co.semester DESC, c.name
    """, [tno])
    offerings = cur.fetchall()
    if not offerings:
        print('\n  暂无排课记录')
        return

    # 选排课（用分页器）
    o_pager = Paginator(offerings)
    plan_id = None
    while plan_id is None:
        cls()
        show_table(['#', '排课ID', '课程', '学期', '已选/上限'],
                   [[i + 1, r[0], r[1], r[2], f'{r[3]}/{r[4]}']
                    for i, r in enumerate(o_pager.items)])
        print(f'  {o_pager.info}')
        print('  [编号]选排课  [N]下一页  [P]上一页  [Q]返回')
        c = input('  请选择: ').strip().lower()
        if c == 'q':
            return
        elif c == 'n':
            o_pager.next()
        elif c == 'p':
            o_pager.prev()
        else:
            try:
                idx = int(c)
                if 1 <= idx <= len(o_pager.items):
                    r = o_pager.items[idx - 1]
                    plan_id, course_name = r[0], r[1]
            except ValueError:
                pass

    # Step 2: 录成绩循环
    while True:
        cur.execute("""
            SELECT s.no, s.name, e.score
            FROM enrollment e
            JOIN student s ON e.student_id = s.id
            WHERE e.offering_id = %s AND e.is_deleted = 0
            ORDER BY s.no
        """, [plan_id])
        students = cur.fetchall()
        if not students:
            print('\n  该排课暂无学生选课')
            input('\n  按回车...')
            return

        pager = Paginator(students)
        while True:
            cls()
            show_table(['学号', '姓名', '成绩'],
                       [[r[0], r[1], str(r[2]) if r[2] is not None else '未录入']
                        for r in pager.items])
            print(f'  {course_name}  {pager.info}')
            print('  [学号]录入成绩  [N]下一页  [P]上一页  [Q]返回排课列表')
            c = input('  请选择: ').strip().lower()
            if c == 'q':
                return
            elif c == 'n':
                pager.next()
            elif c == 'p':
                pager.prev()
            else:
                stu_no = c
                if not any(s[0] == stu_no for s in students):
                    print(f'\n  ❌ 学号 {stu_no} 不在此排课中')
                    input('\n  按回车...')
                    continue
                score = input(f'  成绩 (0-100, 回车跳过): ').strip()
                if not score:
                    continue
                try:
                    with conn.cursor() as cur2:
                        cur2.callproc('sp_grade_input',
                                      [tno, plan_id, stu_no, float(score)])
                        conn.commit()
                        cur2.fetchall()
                        cur2.nextset()
                    print(f'\n  ✅ 录入成功: {stu_no} → {score}')
                    input('\n  按回车...')
                    # 重新查数据，刷新列表
                    cur.execute("""
                        SELECT s.no, s.name, e.score
                        FROM enrollment e
                        JOIN student s ON e.student_id = s.id
                        WHERE e.offering_id = %s AND e.is_deleted = 0
                        ORDER BY s.no
                    """, [plan_id])
                    students = cur.fetchall()
                    pager = Paginator(students)
                except Exception as e:
                    print(f'\n  ❌ {e}')
                    input('\n  按回车...')


def batch_grade_input(conn, tno, csv_path=None):
    """从 CSV 批量录入成绩，格式：plan_id, student_no, score
    csv_path 参数供 tester 直接传路径，交互模式则提示输入"""
    if csv_path is None:
        csv_path = input('  请输入CSV文件路径: ').strip()
    if not csv_path:
        return
    if not os.path.exists(csv_path):
        print(f'\n  ❌ 文件不存在: {csv_path}')
        return

    ok = fail = 0
    with open(csv_path, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader, 1):
            plan_id = row.get('plan_id', '').strip()
            student_no = row.get('student_no', '').strip()
            score = row.get('score', '').strip()
            if not plan_id or not student_no or not score:
                print(f'  ⚠ 第{i}行 字段不完整，跳过')
                fail += 1
                continue
            try:
                with conn.cursor() as cur:
                    cur.callproc('sp_grade_input',
                                 [tno, int(plan_id), student_no, float(score)])
                    conn.commit()
                    cur.fetchall()
                    cur.nextset()
                print(f'  ✅ 第{i}行 {student_no} → {score}')
                ok += 1
            except Exception as e:
                print(f'  ❌ 第{i}行 {student_no}: {e}')
                fail += 1

    print(f'\n  完成：成功 {ok} 条，失败 {fail} 条')


def my_students(conn, tid, tname):
    cur = conn.cursor()
    cur.execute("""
        SELECT co.id, c.name, co.semester, co.current_students, co.max_students
        FROM course_offering co
        JOIN course c ON co.course_id = c.id
        WHERE co.teacher_id = %s AND co.is_deleted = 0
        ORDER BY co.semester, c.name
    """, [tid])
    offerings = cur.fetchall()
    if not offerings:
        print('\n  暂无排课记录')
        return
    hr()
    print(f'  {tname} 老师的排课')
    hr()
    for i, (oid, cname, sem, cur_s, max_s) in enumerate(offerings):
        print(f'  [{i+1}] ID={oid}  {sem}  {cname}  ({cur_s}/{max_s})')

    oid = input('\n  请输入排课ID查看学生 (0=取消): ').strip()
    if oid == '0' or not oid:
        return
    cur.execute("""
        SELECT s.no, s.name, e.score
        FROM enrollment e
        JOIN student s ON e.student_id = s.id
        WHERE e.offering_id = %s AND e.is_deleted = 0
        ORDER BY s.no
    """, [int(oid)])
    rows = cur.fetchall()
    if not rows:
        print('\n  暂无学生选课')
        return

    pager = Paginator(rows)
    while True:
        cls()
        show_table(['学号', '姓名', '成绩'],
                   [[r[0], r[1], str(r[2]) if r[2] is not None else '未录入']
                    for r in pager.items])
        print(f'  {pager.info}')
        print('  [N]下一页  [P]上一页  [Q]返回')
        c = input('  请选择: ').strip().lower()
        if c == 'q':
            break
        elif c == 'n':
            pager.next()
        elif c == 'p':
            pager.prev()


def teacher_offerings(conn, tno):
    """返回教师的排课列表（供 Streamlit 用）"""
    cur = conn.cursor()
    cur.execute("""
        SELECT co.id, c.name, co.semester, co.current_students, co.max_students
        FROM course_offering co
        JOIN course c ON co.course_id = c.id
        WHERE co.teacher_id = fn_get_teacher_id(%s) AND co.is_deleted = 0
        ORDER BY co.semester DESC, c.name
    """, [tno])
    return cur.fetchall()


def offering_students(conn, plan_id):
    """返回某排课的学生列表（供 Streamlit 用）"""
    cur = conn.cursor()
    cur.execute("""
        SELECT s.no, s.name, e.score
        FROM enrollment e
        JOIN student s ON e.student_id = s.id
        WHERE e.offering_id = %s AND e.is_deleted = 0
        ORDER BY s.no
    """, [plan_id])
    return cur.fetchall()
