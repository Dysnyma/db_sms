"""教师功能"""
import csv
import os
from core.utils import cls, pause, hr, input_choice, render_menu


def menu(conn, tid, tname, tno):
    _items = [
        ('录入成绩',           lambda c: grade_input(c, tno)),
        ('批量录入 (CSV)',     lambda c: batch_grade_input(c, tno)),
        ('查看我的课程学生',   lambda c: my_students(c, tid, tname)),
    ]
    while True:
        if render_menu(conn, f'{tname} 老师 [教师]', _items) == 'quit':
            break


def grade_input(conn, tno):
    plan_id = input('  排课ID: ').strip()
    if not plan_id:
        return
    cur = conn.cursor()
    # 检查该老师有没有这个排课
    cur.execute("""
          SELECT 1
          FROM course_offering
          WHERE id = %s AND teacher_id = fn_get_teacher_id(%s)
      """, [int(plan_id), tno])

    if not cur.fetchone():
        print('\n  您并没有这个排课')
        return

    # 展示这个排课的学生名单
    cur.execute("""
        SELECT s.no, s.name, e.score
        FROM enrollment e
        JOIN student s ON e.student_id = s.id
        WHERE e.offering_id = %s AND e.is_deleted = 0
        ORDER BY s.no
    """, [int(plan_id)])
    rows = cur.fetchall()
    if not rows:
        print('\n  该排课暂无学生选课')
        return
    hr()
    print(f'  排课ID={plan_id} 的学生名单')
    hr()
    for no, name, score in rows:
        sc = f'{score}分' if score is not None else '未录入'
        print(f'  {no}\t{name}\t{sc}')
    hr()

    stu_no = input('  学生学号: ').strip()
    score = input('  成绩 (0-100, 回车跳过): ').strip()
    if not stu_no:
        return
    if not score:
        print('  已跳过')
        return
    try:
        with conn.cursor() as cur:
            cur.callproc('sp_grade_input', [
                         tno, int(plan_id), stu_no, float(score)])
            conn.commit()
            print(f'\n  ✅ {cur.fetchone()[0]}')
    except Exception as e:
        print(f'\n  ❌ {e}')


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
    cur.nextset()
    if not rows:
        print('\n  暂无学生选课')
        return
    hr()
    print(f'  学号	姓名	成绩')
    hr()
    for sno, name, score in rows:
        sc = str(score) if score is not None else '未录入'
        print(f'  {sno}	{name}	{sc}')
