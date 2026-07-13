"""教务功能"""

import os
import subprocess
from datetime import datetime
import pymysql
from core.utils import hr, render_menu, show_table, cls, confirm, Paginator


def menu(conn):
    _items = [
        ("数据概览", summary),
        ("班级学生名单", roster),
        ("班级成绩统计", class_report),
        ("班级成绩明细", class_grade_roster),
        ("教师信息", teacher_info),
        ("教师列表", teacher_list),
        ("备份数据", backup),
        ("恢复数据", restore),
        ("班级管理", class_menu),
        ("课程管理", course_menu),
        ("教师管理", teacher_menu),
        ("学生管理", student_menu),
        ("排课管理", offering_menu),
        ("选课管理", enrollment_menu),
    ]
    while True:
        if render_menu(conn, "教务管理员 [教务]", _items, 2) == "quit":
            break


def summary(conn, paged=True):
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
    if not paged:
        return {
            "班级": c1,
            "学生": c2,
            "课程": c3,
            "教师": c4,
            "排课": c5,
            "选课记录": c6,
        }
    hr()
    print(f"  班级: {c1}    学生: {c2}    课程: {c3}    教师: {c4}")
    print(f"  排课: {c5}    选课记录: {c6}")
    hr()


def roster(conn):
    cid = input("  请输入班级ID: ").strip()
    if not cid:
        return
    with conn.cursor() as cur:
        cur.callproc("sp_student_roster", [int(cid)])
        rows = cur.fetchall()
        cur.nextset()
    if not rows:
        print("\n  该班级没有学生")
        return

    pager = Paginator(rows)
    while True:
        cls()
        show_table(["学号", "姓名", "学籍分", "绩点分"], pager.items)
        print(f"  {pager.info}")
        print("  [N]下一页  [P]上一页  [Q]返回")
        c = input("  请选择: ").strip().lower()
        if c == "q":
            break
        elif c == "n":
            pager.next()
        elif c == "p":
            pager.prev()


def class_report(conn):
    cid = input("  请输入班级ID: ").strip()
    gid = input("  请输入课程ID: ").strip()
    if not cid or not gid:
        return
    with conn.cursor() as cur:
        cur.callproc("sp_class_grade_report", [int(cid), int(gid)])
        rows = cur.fetchall()
        cur.nextset()
    if not rows or not rows[0][0]:
        print("\n  暂无成绩")
        return
    avg_s, max_s, min_s, pass_r, count = rows[0]
    hr()
    print(f"  平均分: {avg_s}    最高分: {max_s}    最低分: {min_s}")
    print(f"  及格率: {pass_r}%    人数: {count}")
    hr()


def teacher_list(conn):
    with conn.cursor() as cur:
        cur.callproc("sp_teacher_list")
        rows = cur.fetchall()
        cur.nextset()
    if not rows:
        print("\n  暂无教师")
        return

    pager = Paginator(rows)
    while True:
        cls()
        show_table(
            ["工号", "姓名", "职称", "排课", "学生", "已录"],
            [[r[0], r[1], r[2] or "-", r[3], r[4], r[5]] for r in pager.items],
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


def teacher_info(conn):
    tno = input("  请输入教师工号: ").strip()
    if not tno:
        return
    with conn.cursor() as cur:
        cur.callproc("sp_teacher_info", [tno])
        rows = cur.fetchall()
        cur.nextset()
    if not rows:
        print("\n  教师不存在")
        return
    r = rows[0]
    hr()
    print(f"  工号: {r[0]}    姓名: {r[1]}    职称: {r[2]}")
    print(f"  排课数: {r[3]}    选课学生: {r[4]}    已录入: {r[5]}")
    hr()


def backup(_conn):
    folder = input("  备份到哪个文件夹 (默认 backup/): ").strip()
    if not folder:
        folder = "backup"
    # 确保文件夹存在
    os.makedirs(folder, exist_ok=True)
    filename = f'backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.sql'
    path = os.path.join(folder, filename)
    r = subprocess.run(
        [
            "mysqldump",
            "-u",
            "root",
            "--databases",
            "db_sms",
            "--routines",
            "--triggers",
            "--add-drop-table",
            "--default-character-set=utf8mb4",
            "--result-file=" + path,
        ],
        capture_output=True,
        text=True,
        check=False,
        shell=False,
    )
    if r.returncode == 0:
        print(f"\n  ✅ 备份成功: {path}")
    else:
        print(f"\n  ❌ 备份失败: {r.stderr.strip()[:200]}")


def restore(_conn):
    path = input("  SQL 文件路径: ").strip()
    if not path or not os.path.exists(path):
        print(f"\n  ❌ 文件不存在: {path}")
        return
    confirm_result = input("  确认恢复？这将覆盖当前数据！(y/N): ").strip().lower()
    if confirm_result != "y":
        print("  已取消")
        return
    with open(path, "r", encoding="utf-8") as f:
        content = (
            "SET FOREIGN_KEY_CHECKS=0;\n" + f.read() + "\nSET FOREIGN_KEY_CHECKS=1;"
        )
    r = subprocess.run(
        ["mysql", "-u", "root", "--default-character-set=utf8mb4"],
        input=content,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
        shell=False,
    )
    if r.returncode == 0:
        print("\n  ✅ 恢复成功！请重启程序")
    else:
        print(f"\n  ❌ 恢复失败: {r.stderr.strip()[:200]}")


def class_menu(conn):
    pager = None
    while True:
        cls()
        cur = conn.cursor()
        cur.execute("""
            SELECT id,name,grade,major,
                CASE status WHEN 1 THEN '在读' ELSE '毕业' END
            FROM class
            WHERE is_deleted = 0
            ORDER BY id
        """)
        rows = cur.fetchall()
        if not pager:
            pager = Paginator(rows)
        else:
            pager.rows = rows

        show_table(["班级ID", "班级名", "年级", "专业", "状态"], pager.items)
        print(f"  {pager.info}")
        print("  [A]新增  [E]修改  [D]删除  [N]下一页  [P]上一页  [Q]返回")
        c = input("  请选择: ").strip().lower()
        if c == "q":
            break
        elif c == "n":
            pager.next()
        elif c == "p":
            pager.prev()
        elif c == "a":
            class_add(conn)
            pager.reset()
        elif c == "e":
            class_edit(conn)
        elif c == "d":
            class_delete(conn)


def class_add(conn):
    cls()
    print(" —— 新增班级 ——\n")
    name = input(" 班级名：").strip()
    if not name:
        return

    grade = input(" 年级（如2024）：").strip()
    if not grade:
        return

    major = input(" 专业：").strip()
    if not major:
        return

    try:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO class (name, grade, major) VALUES (%s, %s, %s)",
                [name, grade, major],
            )
            conn.commit()
        print(f"\n  ✅ 新增成功: {name}")
    except pymysql.Error as e:
        print(f"\n  ❌ 新增失败: {e}")
    cls()


def class_edit(conn):
    cid = input("  要修改的班级ID: ").strip()
    if not cid:
        return
    cid = int(cid)

    cur = conn.cursor()
    cur.execute(
        "SELECT name, grade, major, status FROM class WHERE id = %s AND is_deleted = 0",
        [cid],
    )
    row = cur.fetchone()
    if not row:
        print("  班级不存在")
        return

    # 逐字段询问，回车保留原值
    changes = {}
    for label, col, old in [
        ("班级名", "name", row[0]),
        ("年级", "grade", row[1]),
        ("专业", "major", row[2]),
    ]:
        val = input(f"  {label} [{old}]: ").strip()
        if val and val != str(old):
            changes[col] = val

    s = input(f"  状态 [1=在读 0=毕业，当前:{row[3]}]: ").strip()
    if s in ("0", "1") and int(s) != row[3]:
        changes["status"] = int(s)

    if not changes:
        print("  没有改动")
        return

    print("\n  将修改:")
    for k, v in changes.items():
        print(f"    {k} → {v}")
    if not confirm():
        return

    set_clause = ", ".join(f"{k}=%s" for k in changes)
    cur.execute(
        f"UPDATE class SET {set_clause} WHERE id = %s", list(changes.values()) + [cid]
    )
    conn.commit()
    print("  ✅ 已修改")


def class_delete(conn):
    cid = input("  要删除的班级ID: ").strip()
    if not cid:
        return
    cid = int(cid)

    cur = conn.cursor()
    cur.execute("SELECT name FROM class WHERE id = %s AND is_deleted = 0", [cid])
    row = cur.fetchone()
    if not row:
        print("  班级不存在")
        return

    if confirm(f"确认删除「{row[0]}」？"):
        try:
            with conn.cursor() as cur:
                cur.execute("UPDATE class SET is_deleted = 1 WHERE id = %s", [cid])
                conn.commit()
            print(f"\n  ✅ 已删除: {row[0]}")
        except pymysql.Error as e:
            print(f"\n  ❌ 删除失败: {e}")


def course_menu(conn):
    pager = None
    while True:
        cls()
        cur = conn.cursor()
        cur.execute("""
            SELECT id,name,credit,
                CASE status WHEN 1 THEN '开课' ELSE '停开' END
            FROM course
            WHERE is_deleted = 0
            ORDER BY id
        """)
        rows = cur.fetchall()
        if not pager:
            pager = Paginator(rows)
        else:
            pager.rows = rows

        show_table(["课程ID", "课程名", "学分", "状态"], pager.items)
        print(f"  {pager.info}")
        print("  [A]新增  [E]修改  [D]删除  [N]下一页  [P]上一页  [Q]返回")
        c = input("  请选择: ").strip().lower()
        if c == "q":
            break
        elif c == "n":
            pager.next()
        elif c == "p":
            pager.prev()
        elif c == "a":
            course_add(conn)
            pager.reset()
        elif c == "e":
            course_edit(conn)
        elif c == "d":
            course_delete(conn)


def course_add(conn):
    cls()
    print(" —— 新增课程 ——\n")
    name = input(" 课程名：").strip()
    if not name:
        return

    credit = input(" 学分（如3.0）：").strip()
    if not credit:
        return

    try:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO course (name, credit) VALUES (%s, %s)", [name, credit]
            )
            conn.commit()
        print(f"\n  ✅ 新增成功: {name}")
    except pymysql.Error as e:
        print(f"\n  ❌ 新增失败: {e}")
    cls()
    return


def course_edit(conn):
    cid = input("  要修改的课程ID: ").strip()
    if not cid:
        return
    cid = int(cid)

    cur = conn.cursor()
    cur.execute(
        "SELECT name, credit, status FROM course WHERE id = %s AND is_deleted = 0",
        [cid],
    )
    row = cur.fetchone()
    if not row:
        print("  课程不存在")
        return

    changes = {}
    for label, col, old in [
        ("课程名", "name", row[0]),
        ("学分", "credit", row[1]),
    ]:
        val = input(f"  {label} [{old}]: ").strip()
        if val and val != str(old):
            changes[col] = val

    s = input(f"  状态 [1=开课 0=停开，当前:{row[2]}]: ").strip()
    if s in ("0", "1") and int(s) != row[2]:
        changes["status"] = int(s)

    if not changes:
        print("  没有改动")
        return

    print("\n  将修改:")
    for k, v in changes.items():
        print(f"    {k} → {v}")
    if not confirm():
        return

    set_clause = ", ".join(f"{k}=%s" for k in changes)
    cur.execute(
        f"UPDATE course SET {set_clause} WHERE id = %s", list(changes.values()) + [cid]
    )
    conn.commit()
    print("  ✅ 已修改")


def course_delete(conn):
    cid = input("  要删除的课程ID: ").strip()
    if not cid:
        return
    cid = int(cid)

    cur = conn.cursor()
    cur.execute("SELECT name FROM course WHERE id = %s AND is_deleted = 0", [cid])
    row = cur.fetchone()
    if not row:
        print("  课程不存在")
        return

    if confirm(f"确认删除「{row[0]}」？"):
        try:
            with conn.cursor() as cur:
                cur.execute("UPDATE course SET is_deleted = 1 WHERE id = %s", [cid])
                conn.commit()
            print(f"\n  ✅ 已删除: {row[0]}")
        except pymysql.Error as e:
            print(f"\n  ❌ 删除失败: {e}")
    return


# ============================================================
#  教师管理
# ============================================================


def teacher_menu(conn):
    pager = None
    while True:
        cls()
        cur = conn.cursor()
        cur.execute("""
            SELECT id, name, no, IFNULL(title, '-'), IFNULL(phone, '-'),
                   CASE status WHEN 1 THEN '在职' ELSE '离职' END
            FROM teacher
            WHERE is_deleted = 0
            ORDER BY no
        """)
        rows = cur.fetchall()
        if not pager:
            pager = Paginator(rows)
        else:
            pager.rows = rows

        show_table(["教师ID", "姓名", "工号", "职称", "电话", "状态"], pager.items)
        print(f"  {pager.info}")
        print("  [A]新增  [E]修改  [D]删除  [N]下一页  [P]上一页  [Q]返回")
        c = input("  请选择: ").strip().lower()
        if c == "q":
            break
        elif c == "n":
            pager.next()
        elif c == "p":
            pager.prev()
        elif c == "a":
            teacher_add(conn)
            pager.reset()
        elif c == "e":
            teacher_edit(conn)
        elif c == "d":
            teacher_delete(conn)


def teacher_add(conn):
    cls()
    print(" —— 新增教师 ——\n")
    name = input(" 姓名：").strip()
    if not name:
        return
    no = input(" 工号：").strip()
    if not no:
        return
    title = input(" 职称（回车跳过）：").strip() or None
    phone = input(" 电话（回车跳过）：").strip() or None

    try:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO teacher (name, no, title, phone) VALUES (%s, %s, %s, %s)",
                [name, no, title, phone],
            )
            conn.commit()
        print(f"\n  ✅ 新增成功: {name}")
    except pymysql.Error as e:
        print(f"\n  ❌ 新增失败: {e}")


def teacher_edit(conn):
    cid = input("  要修改的教师ID: ").strip()
    if not cid:
        return
    cid = int(cid)

    cur = conn.cursor()
    cur.execute(
        "SELECT name, no, title, phone, status FROM teacher WHERE id = %s AND is_deleted = 0",
        [cid],
    )
    row = cur.fetchone()
    if not row:
        print("  教师不存在")
        return

    changes = {}
    for label, col, old in [
        ("姓名", "name", row[0]),
        ("工号", "no", row[1]),
        ("职称", "title", row[2] or ""),
        ("电话", "phone", row[3] or ""),
    ]:
        val = input(f"  {label} [{old}]: ").strip()
        if val and val != str(old):
            changes[col] = val

    s = input(f"  状态 [1=在职 0=离职，当前:{row[4]}]: ").strip()
    if s in ("0", "1") and int(s) != row[4]:
        changes["status"] = int(s)

    if not changes:
        print("  没有改动")
        return

    print("\n  将修改:")
    for k, v in changes.items():
        print(f"    {k} → {v}")
    if not confirm():
        return

    set_clause = ", ".join(f"{k}=%s" for k in changes)
    cur.execute(
        f"UPDATE teacher SET {set_clause} WHERE id = %s", list(changes.values()) + [cid]
    )
    conn.commit()
    print("  ✅ 已修改")


def teacher_delete(conn):
    cid = input("  要删除的教师ID: ").strip()
    if not cid:
        return
    cid = int(cid)

    cur = conn.cursor()
    cur.execute("SELECT name FROM teacher WHERE id = %s AND is_deleted = 0", [cid])
    row = cur.fetchone()
    if not row:
        print("  教师不存在")
        return

    if confirm(f"确认删除「{row[0]}」？"):
        try:
            with conn.cursor() as cur:
                cur.execute("UPDATE teacher SET is_deleted = 1 WHERE id = %s", [cid])
                conn.commit()
            print(f"\n  ✅ 已删除: {row[0]}")
        except pymysql.Error as e:
            print(f"\n  ❌ 删除失败: {e}")


# ============================================================
#  学生管理
# ============================================================


def student_menu(conn):
    pager = None
    while True:
        cls()
        cur = conn.cursor()
        cur.execute("""
            SELECT s.id, s.name, s.no, c.name,
                   CASE s.status WHEN 1 THEN '在读' ELSE '离校' END
            FROM student s
            JOIN class c ON s.class_id = c.id
            WHERE s.is_deleted = 0
            ORDER BY s.no
        """)
        rows = cur.fetchall()
        if not pager:
            pager = Paginator(rows)
        else:
            pager.rows = rows

        show_table(["学生ID", "姓名", "学号", "班级", "状态"], pager.items)
        print(f"  {pager.info}")
        print("  [A]新增  [E]修改  [D]删除  [N]下一页  [P]上一页  [Q]返回")
        c = input("  请选择: ").strip().lower()
        if c == "q":
            break
        elif c == "n":
            pager.next()
        elif c == "p":
            pager.prev()
        elif c == "a":
            student_add(conn)
            pager.reset()
        elif c == "e":
            student_edit(conn)
        elif c == "d":
            student_delete(conn)


def student_add(conn):
    cls()
    print(" —— 新增学生 ——\n")
    no = input(" 学号：").strip()
    if not no:
        return
    name = input(" 姓名：").strip()
    if not name:
        return

    cur = conn.cursor()
    cur.execute("SELECT id, name FROM class WHERE is_deleted = 0 ORDER BY id")
    classes = cur.fetchall()
    show_table(["班级ID", "班级名"], classes)
    cid = input(" 班级ID：").strip()
    if not cid:
        return

    try:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO student (no, name, class_id) VALUES (%s, %s, %s)",
                [no, name, int(cid)],
            )
            conn.commit()
        print(f"\n  ✅ 新增成功: {name}")
    except pymysql.Error as e:
        print(f"\n  ❌ 新增失败: {e}")


def student_edit(conn):
    cid = input("  要修改的学生ID: ").strip()
    if not cid:
        return
    cid = int(cid)

    cur = conn.cursor()
    cur.execute(
        "SELECT name, no, class_id, status FROM student WHERE id = %s AND is_deleted = 0",
        [cid],
    )
    row = cur.fetchone()
    if not row:
        print("  学生不存在")
        return

    changes = {}
    for label, col, old in [
        ("姓名", "name", row[0]),
        ("学号", "no", row[1]),
    ]:
        val = input(f"  {label} [{old}]: ").strip()
        if val and val != str(old):
            changes[col] = val

    cur.execute("SELECT id, name FROM class WHERE is_deleted = 0 ORDER BY id")
    classes = cur.fetchall()
    show_table(["班级ID", "班级名"], classes)
    val = input(f"  班级ID [当前:{row[2]}]: ").strip()
    if val and int(val) != row[2]:
        changes["class_id"] = int(val)

    s = input(f"  状态 [1=在读 0=离校，当前:{row[3]}]: ").strip()
    if s in ("0", "1") and int(s) != row[3]:
        changes["status"] = int(s)

    if not changes:
        print("  没有改动")
        return

    print("\n  将修改:")
    for k, v in changes.items():
        print(f"    {k} → {v}")
    if not confirm():
        return

    set_clause = ", ".join(f"{k}=%s" for k in changes)
    cur.execute(
        f"UPDATE student SET {set_clause} WHERE id = %s", list(changes.values()) + [cid]
    )
    conn.commit()
    print("  ✅ 已修改")


def student_delete(conn):
    cid = input("  要删除的学生ID: ").strip()
    if not cid:
        return
    cid = int(cid)

    cur = conn.cursor()
    cur.execute("SELECT name, no FROM student WHERE id = %s AND is_deleted = 0", [cid])
    row = cur.fetchone()
    if not row:
        print("  学生不存在")
        return

    if confirm(f"确认删除「{row[0]}({row[1]})」？"):
        try:
            with conn.cursor() as cur:
                cur.execute("UPDATE student SET is_deleted = 1 WHERE id = %s", [cid])
                conn.commit()
            print(f"\n  ✅ 已删除: {row[0]}")
        except pymysql.Error as e:
            print(f"\n  ❌ 删除失败: {e}")


# ============================================================
#  排课管理
# ============================================================


def offering_menu(conn):
    pager = None
    while True:
        cls()
        cur = conn.cursor()
        cur.execute("""
            SELECT co.id, c.name, t.name, co.semester,
                   co.current_students, co.max_students,
                   CASE co.status WHEN 1 THEN '有效' ELSE '取消' END
            FROM course_offering co
            JOIN course c ON co.course_id = c.id
            JOIN teacher t ON co.teacher_id = t.id
            WHERE co.is_deleted = 0
            ORDER BY co.semester DESC, c.name
        """)
        rows = cur.fetchall()
        if not pager:
            pager = Paginator(rows)
        else:
            pager.rows = rows

        show_table(
            ["排课ID", "课程", "教师", "学期", "已选", "上限", "状态"], pager.items
        )
        print(f"  {pager.info}")
        print("  [A]新增  [E]修改  [D]删除  [N]下一页  [P]上一页  [Q]返回")
        c = input("  请选择: ").strip().lower()
        if c == "q":
            break
        elif c == "n":
            pager.next()
        elif c == "p":
            pager.prev()
        elif c == "a":
            offering_add(conn)
            pager.reset()
        elif c == "e":
            offering_edit(conn)
        elif c == "d":
            offering_delete(conn)


def offering_add(conn):
    cls()
    print(" —— 新增排课 ——\n")
    cur = conn.cursor()

    # 选课程
    cur.execute("SELECT id, name FROM course WHERE is_deleted = 0 ORDER BY id")
    courses = cur.fetchall()
    show_table(["课程ID", "课程名"], courses)
    cid = input(" 课程ID：").strip()
    if not cid:
        return

    # 列出该课程有资格的教师
    cur.execute(
        """
        SELECT t.id, t.name, IFNULL(t.title,'-')
        FROM teacher t
        JOIN teacher_course tc ON t.id = tc.teacher_id
        WHERE tc.course_id = %s AND t.is_deleted = 0
    """,
        [int(cid)],
    )
    teachers = cur.fetchall()
    if not teachers:
        print("  该课程没有教师能上！请先在管理中设置讲授关系")
        return
    show_table(["教师ID", "姓名", "职称"], teachers)
    tid = input(" 教师ID：").strip()
    if not tid:
        return

    sem = input(" 学期（如 2024-2025-1）：").strip()
    if not sem:
        return
    max_s = input(" 选课上限：").strip()
    if not max_s:
        return
    start = input(" 选课开始时间（YYYY-MM-DD HH:MM:SS）：").strip()
    if not start:
        return
    end = input(" 选课截止时间（YYYY-MM-DD HH:MM:SS）：").strip()
    if not end:
        return
    deadline = input(" 成绩录入截止时间（YYYY-MM-DD HH:MM:SS）：").strip()
    if not deadline:
        return

    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO course_offering
                  (course_id, teacher_id, semester, max_students,
                   enroll_start_time, enroll_end_time, grade_deadline)
                VALUES (%s,%s,%s,%s,%s,%s,%s)
            """,
                [int(cid), int(tid), sem, int(max_s), start, end, deadline],
            )
            conn.commit()
        print("\n  ✅ 新增成功")
    except pymysql.Error as e:
        print(f"\n  ❌ 新增失败: {e}")


def offering_edit(conn):
    cid = input("  要修改的排课ID: ").strip()
    if not cid:
        return
    cid = int(cid)

    cur = conn.cursor()
    cur.execute(
        """
        SELECT semester, max_students,
               enroll_start_time, enroll_end_time, grade_deadline,
               status
        FROM course_offering
        WHERE id = %s AND is_deleted = 0
    """,
        [cid],
    )
    row = cur.fetchone()
    if not row:
        print("  排课不存在")
        return

    changes = {}
    for label, col, old in [
        ("学期", "semester", str(row[0])),
        ("选课上限", "max_students", row[1]),
        ("选课开始时间", "enroll_start_time", str(row[2])),
        ("选课截止时间", "enroll_end_time", str(row[3])),
        ("成绩录入截止时间", "grade_deadline", str(row[4])),
    ]:
        val = input(f"  {label} [{old}]: ").strip()
        if val and val != str(old):
            changes[col] = val

    s = input(f"  状态 [1=有效 0=取消，当前:{row[5]}]: ").strip()
    if s in ("0", "1") and int(s) != row[5]:
        changes["status"] = int(s)

    if not changes:
        print("  没有改动")
        return

    print("\n  将修改:")
    for k, v in changes.items():
        print(f"    {k} → {v}")
    if not confirm():
        return

    set_clause = ", ".join(f"{k}=%s" for k in changes)
    cur.execute(
        f"UPDATE course_offering SET {set_clause} WHERE id = %s",
        list(changes.values()) + [cid],
    )
    conn.commit()
    print("  ✅ 已修改")


def offering_delete(conn):
    cid = input("  要删除的排课ID: ").strip()
    if not cid:
        return
    cid = int(cid)

    cur = conn.cursor()
    cur.execute(
        """
        SELECT c.name, t.name, co.semester
        FROM course_offering co
        JOIN course c ON co.course_id = c.id
        JOIN teacher t ON co.teacher_id = t.id
        WHERE co.id = %s AND co.is_deleted = 0
    """,
        [cid],
    )
    row = cur.fetchone()
    if not row:
        print("  排课不存在")
        return

    if confirm(f"确认删除「{row[0]} - {row[1]} ({row[2]})」？"):
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "UPDATE course_offering SET is_deleted = 1 WHERE id = %s", [cid]
                )
                conn.commit()
            print("\n  ✅ 已删除")
        except pymysql.Error as e:
            print(f"\n  ❌ 删除失败: {e}")


# ============================================================
#  选课管理
# ============================================================


def enrollment_menu(conn):
    pager = None
    while True:
        cls()
        cur = conn.cursor()
        cur.execute("""
            SELECT e.id, s.name, s.no, c.name, t.name, co.semester,
                   IFNULL(e.score, '未录入'), c.name AS class_name
            FROM enrollment e
            JOIN student s ON e.student_id = s.id
            JOIN class cl ON s.class_id = cl.id
            JOIN course_offering co ON e.offering_id = co.id
            JOIN course c ON co.course_id = c.id
            JOIN teacher t ON co.teacher_id = t.id
            WHERE e.is_deleted = 0
            ORDER BY co.semester DESC, s.no
        """)
        rows = cur.fetchall()
        if not pager:
            pager = Paginator(rows)
        else:
            pager.rows = rows

        show_table(
            ["选课ID", "学生", "学号", "课程", "教师", "学期", "成绩"], pager.items
        )
        print(f"  {pager.info}")
        print("  [D]强制退选  [Q]返回")
        c = input("  请选择: ").strip().lower()
        if c == "q":
            break
        elif c == "n":
            pager.next()
        elif c == "p":
            pager.prev()
        elif c == "d":
            enrollment_delete(conn)
            pager.reset()


def enrollment_delete(conn):
    eid = input("  要退选的选课ID: ").strip()
    if not eid:
        return

    cur = conn.cursor()
    cur.execute(
        """
        SELECT s.name, c.name, t.name
        FROM enrollment e
        JOIN student s ON e.student_id = s.id
        JOIN course_offering co ON e.offering_id = co.id
        JOIN course c ON co.course_id = c.id
        JOIN teacher t ON co.teacher_id = t.id
        WHERE e.id = %s AND e.is_deleted = 0
    """,
        [int(eid)],
    )
    row = cur.fetchone()
    if not row:
        print("  选课记录不存在")
        return

    if confirm(f"强制退选「{row[0]} → {row[1]} ({row[2]})」？"):
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "UPDATE enrollment SET is_deleted = 1 WHERE id = %s", [int(eid)]
                )
                conn.commit()
            print(f"\n  ✅ 已退选: {row[0]}")
        except pymysql.Error as e:
            print(f"\n  ❌ 操作失败: {e}")


# ============================================================
#  按班级查成绩登记册
# ============================================================


def class_grade_roster(conn):
    """按班级查看每个学生的各科成绩明细"""
    cid = input("  请输入班级ID: ").strip()
    if not cid:
        return

    cur = conn.cursor()
    cur.execute(
        """
        SELECT s.name, s.no, c.name AS course, t.name AS teacher,
               co.semester, IFNULL(e.score, '未录入')
        FROM enrollment e
        JOIN student s ON e.student_id = s.id
        JOIN course_offering co ON e.offering_id = co.id
        JOIN course c ON co.course_id = c.id
        JOIN teacher t ON co.teacher_id = t.id
        WHERE s.class_id = %s AND e.is_deleted = 0
        ORDER BY s.no, co.semester, c.name
    """,
        [int(cid)],
    )
    rows = cur.fetchall()
    if not rows:
        print("\n  该班级暂无成绩")
        return

    pager = Paginator(rows)
    while True:
        cls()
        show_table(["姓名", "学号", "课程", "教师", "学期", "成绩"], pager.items)
        print(f"  {pager.info}")
        print("  [N]下一页  [P]上一页  [Q]返回")
        c = input("  请选择: ").strip().lower()
        if c == "q":
            break
        elif c == "n":
            pager.next()
        elif c == "p":
            pager.prev()


# ============================================================
#  Streamlit 辅助函数
# ============================================================


def class_list(conn):
    """返回全部班级列表"""
    cur = conn.cursor()
    cur.execute("""
        SELECT id, name, grade, major,
               CASE status WHEN 1 THEN '在读' ELSE '毕业' END
        FROM class WHERE is_deleted = 0 ORDER BY id
    """)
    return cur.fetchall()


def roster_data(conn, class_id):
    """返回某班级的学生名单"""
    cur = conn.cursor()
    cur.callproc("sp_student_roster", [class_id])
    rows = cur.fetchall()
    cur.nextset()
    return rows


def course_list(conn):
    """返回全部课程列表"""
    cur = conn.cursor()
    cur.execute("""
        SELECT id, name, credit,
               CASE status WHEN 1 THEN '开课' ELSE '停开' END
        FROM course WHERE is_deleted = 0 ORDER BY id
    """)
    return cur.fetchall()


def class_report_data(conn, class_id, course_id):
    """返回某班级某课程的成绩统计"""
    cur = conn.cursor()
    cur.callproc("sp_class_grade_report", [class_id, course_id])
    rows = cur.fetchall()
    cur.nextset()
    return rows


def grade_roster_data(conn, class_id):
    """返回某班级每人每课的成绩明细"""
    cur = conn.cursor()
    cur.execute(
        """
        SELECT s.name, s.no, c.name, t.name, co.semester,
               IFNULL(e.score, '未录入')
        FROM enrollment e
        JOIN student s ON e.student_id = s.id
        JOIN course_offering co ON e.offering_id = co.id
        JOIN course c ON co.course_id = c.id
        JOIN teacher t ON co.teacher_id = t.id
        WHERE s.class_id = %s AND e.is_deleted = 0
        ORDER BY s.no, co.semester, c.name
    """,
        [class_id],
    )
    return cur.fetchall()


def teacher_info_data(conn, tno):
    """返回单个教师信息及授课统计"""
    cur = conn.cursor()
    cur.callproc("sp_teacher_info", [tno])
    rows = cur.fetchall()
    cur.nextset()
    return rows


def teacher_list_data(conn):
    """返回全部教师列表及授课统计"""
    cur = conn.cursor()
    cur.callproc("sp_teacher_list")
    rows = cur.fetchall()
    cur.nextset()
    return rows


def teacher_full_list(conn):
    """返回全部教师（id, name, no, title, phone, status）"""
    cur = conn.cursor()
    cur.execute("""
        SELECT id, name, no, IFNULL(title,''), IFNULL(phone,''),
               CASE status WHEN 1 THEN '在职' ELSE '离职' END
        FROM teacher WHERE is_deleted = 0 ORDER BY no
    """)
    return cur.fetchall()


def student_full_list(conn):
    """返回全部学生（id, name, no, class_id, status + class名）"""
    cur = conn.cursor()
    cur.execute("""
        SELECT s.id, s.name, s.no, s.class_id, c.name,
               CASE s.status WHEN 1 THEN '在读' ELSE '离校' END
        FROM student s JOIN class c ON s.class_id = c.id
        WHERE s.is_deleted = 0 ORDER BY s.no
    """)
    return cur.fetchall()


def offering_full_list(conn):
    """返回全部排课（id, course, teacher, semester, cur/max, status）"""
    cur = conn.cursor()
    cur.execute("""
        SELECT co.id, c.name, t.name, co.semester,
               co.current_students, co.max_students,
               CASE co.status WHEN 1 THEN '有效' ELSE '取消' END,
               co.course_id, co.teacher_id
        FROM course_offering co
        JOIN course c ON co.course_id = c.id
        JOIN teacher t ON co.teacher_id = t.id
        WHERE co.is_deleted = 0
        ORDER BY co.semester DESC, c.name
    """)
    return cur.fetchall()


def teacher_course_teachers(conn, course_id):
    """返回能教某课程的教师列表"""
    cur = conn.cursor()
    cur.execute(
        """
        SELECT t.id, t.name, IFNULL(t.title,'')
        FROM teacher t
        JOIN teacher_course tc ON t.id = tc.teacher_id
        WHERE tc.course_id = %s AND t.is_deleted = 0
    """,
        [course_id],
    )
    return cur.fetchall()


def enrollment_list(conn):
    """返回全部选课记录"""
    cur = conn.cursor()
    cur.execute("""
        SELECT e.id, s.name, s.no, c.name, t.name, co.semester,
               IFNULL(e.score, '未录入')
        FROM enrollment e
        JOIN student s ON e.student_id = s.id
        JOIN course_offering co ON e.offering_id = co.id
        JOIN course c ON co.course_id = c.id
        JOIN teacher t ON co.teacher_id = t.id
        WHERE e.is_deleted = 0
        ORDER BY co.semester DESC, s.no
    """)
    return cur.fetchall()
