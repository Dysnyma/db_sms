"""教务功能"""
import os
import subprocess
from datetime import datetime
from core.utils import hr, render_menu


def menu(conn):
    _items = [
        ('数据概览',     summary),
        ('班级学生名单', roster),
        ('班级成绩统计', class_report),
        ('教师信息',     teacher_info),
        ('教师列表',     teacher_list),
        ('备份数据',     backup),
        ('恢复数据',     restore),
    ]
    while True:
        if render_menu(conn, '教务管理员 [教务]', _items, 2) == 'quit':
            break


def summary(conn):
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM class WHERE is_deleted = 0")
    c1 = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM student WHERE is_deleted = 0")
    c2 = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM course WHERE is_deleted = 0")
    c3 = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM teacher WHERE is_deleted = 0")
    c4 = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM course_offering WHERE is_deleted = 0")
    c5 = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM enrollment WHERE is_deleted = 0")
    c6 = cur.fetchone()[0]
    hr()
    print(f'  班级: {c1}    学生: {c2}    课程: {c3}    教师: {c4}')
    print(f'  排课: {c5}    选课记录: {c6}')
    hr()


def roster(conn):
    cid = input('  请输入班级ID: ').strip()
    if not cid:
        return
    with conn.cursor() as cur:
        cur.callproc('sp_student_roster', [int(cid)])
        rows = cur.fetchall()
        cur.nextset()
    if not rows:
        print('\n  该班级没有学生')
        return
    hr()
    print(f'  学号\t姓名\t学籍分\t绩点分')
    hr()
    for no, name, ws, gpa in rows:
        print(f'  {no}\t{name}\t{str(ws)}\t{str(gpa)}')


def class_report(conn):
    cid = input('  请输入班级ID: ').strip()
    gid = input('  请输入课程ID: ').strip()
    if not cid or not gid:
        return
    with conn.cursor() as cur:
        cur.callproc('sp_class_grade_report', [int(cid), int(gid)])
        rows = cur.fetchall()
        cur.nextset()
    if not rows or not rows[0][0]:
        print('\n  暂无成绩')
        return
    avg_s, max_s, min_s, pass_r, count = rows[0]
    hr()
    print(f'  平均分: {avg_s}    最高分: {max_s}    最低分: {min_s}')
    print(f'  及格率: {pass_r}%    人数: {count}')
    hr()


def teacher_list(conn):
    with conn.cursor() as cur:
        cur.callproc('sp_teacher_list')
        rows = cur.fetchall()
        cur.nextset()
    if not rows:
        print('\n  暂无教师')
        return
    hr()
    print(f'  工号\t姓名\t职称\t排课\t学生\t已录')
    hr()
    for r in rows:
        print(f'  {r[0]}\t{r[1]}\t{r[2] or "-"}\t{r[3]}\t{r[4]}\t{r[5]}')


def teacher_info(conn):
    tno = input('  请输入教师工号: ').strip()
    if not tno:
        return
    with conn.cursor() as cur:
        cur.callproc('sp_teacher_info', [tno])
        rows = cur.fetchall()
        cur.nextset()
    if not rows:
        print('\n  教师不存在')
        return
    r = rows[0]
    hr()
    print(f'  工号: {r[0]}    姓名: {r[1]}    职称: {r[2]}')
    print(f'  排课数: {r[3]}    选课学生: {r[4]}    已录入: {r[5]}')
    hr()


def backup(conn):
    folder = input('  备份到哪个文件夹 (默认 backup/): ').strip()
    if not folder:
        folder = 'backup'
    # 确保文件夹存在
    os.makedirs(folder, exist_ok=True)
    filename = f'backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.sql'
    path = os.path.join(folder, filename)
    r = subprocess.run(
        ['mysqldump', '-u', 'root', '--databases', 'db_sms',
         '--default-character-set=utf8mb4', '--result-file=' + path],
        capture_output=True, text=True
    )
    if r.returncode == 0:
        print(f'\n  ✅ 备份成功: {path}')
    else:
        print(f'\n  ❌ 备份失败: {r.stderr.strip()[:200]}')


def restore(conn):
    path = input('  SQL 文件路径: ').strip()
    if not path or not os.path.exists(path):
        print(f'\n  ❌ 文件不存在: {path}')
        return
    confirm = input(f'  确认恢复？这将覆盖当前数据！(y/N): ').strip().lower()
    if confirm != 'y':
        print('  已取消')
        return
    r = subprocess.run(
        ['mysql', '-u', 'root', '--default-character-set=utf8mb4'],
        stdin=open(path, 'r', encoding='utf-8'),
        capture_output=True, text=True
    )
    if r.returncode == 0:
        print(f'\n  ✅ 恢复成功！请重启程序')
    else:
        print(f'\n  ❌ 恢复失败: {r.stderr.strip()[:200]}')
