"""
一站式生成 20000 学生、300 教师、1000 排课、200 万选课的仿真数据
自动导入数据库并清洁 CSV，无需手动操作。
用法：python test/generate_large_data.py
前提：先运行 python src/reset_data.py 初始化基础数据
"""

import csv
import os
import random
import subprocess
import sys
from datetime import datetime, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src"))
from core.majors import all_majors
from core.config import connect as get_connection

TEST_DIR = os.path.dirname(os.path.abspath(__file__))

# ── 姓名库 ──
SURNAMES = list("张李王赵陈刘黄周吴郑钱孙朱马胡林郭何高罗梁宋唐许邓冯韩曹曾彭萧蔡潘田董袁于叶蒋余杜苏魏程吕丁沈任姚卢傅钟崔")
GIVEN = list("伟强磊军勇杰涛明超波斌峰辉刚健龙翔鹏博文飞浩亮华毅鑫铭洋宇然鸿远泽昕梓豪俊哲睿")
GIVEN_F = list("芳敏静丽娟燕霞娜莹婷琳颖宁雪萌瑶倩洁蕊美玲淑桂玉华秀兰英")

# ── 配置 ──
TARGET_STUDENTS = 20000
TARGET_ENROLLMENTS = 2_000_000
SEMESTER_YEARS = 20  # 20 年
USED_MAJORS = 50     # 取前 50 个专业用于建班


def random_name(used):
    while True:
        s = random.choice(SURNAMES)
        pool = GIVEN + GIVEN_F
        name = s + (random.choice(pool) + random.choice(pool) if random.random() < 0.7 else random.choice(pool))
        if name not in used:
            used.add(name)
            return name


def main():
    conn = get_connection()
    cur = conn.cursor()

    print("=" * 50)
    print("  读取基础数据...")
    print("=" * 50)

    cur.execute("SELECT MAX(id) FROM student")
    max_stu_id = cur.fetchone()[0] or 0
    cur.execute("SELECT MAX(CAST(no AS UNSIGNED)) FROM student")
    max_stu_no = cur.fetchone()[0] or 20240000
    cur.execute("SELECT COUNT(*) FROM class WHERE is_deleted = 0")
    cls_cnt = cur.fetchone()[0]
    cur.execute("SELECT MAX(id) FROM course_offering")
    max_off_id = cur.fetchone()[0] or 0
    cur.execute("SELECT id FROM course WHERE is_deleted=0 ORDER BY id")
    course_ids = [r[0] for r in cur.fetchall()]
    conn.close()

    # ── 1. 生成班级 CSV ──
    print("\n📌 第一步：生成班级数据...")
    majors = all_majors()[:USED_MAJORS]
    grades = ["2022", "2023", "2024"]
    class_data = []
    seen_names = set()
    for g in grades:
        for m in majors:
            for seq in range(1, random.randint(2, 4)):
                name = f"{g}{m}{seq}班"
                if name not in seen_names:
                    seen_names.add(name)
                    class_data.append((name, g, m, 1))
    cls_path = os.path.join(TEST_DIR, "class_big.csv")
    with open(cls_path, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["name", "grade", "major", "status"])
        w.writerows(class_data)
    total_classes = cls_cnt + len(class_data)
    print(f"  新增 {len(class_data)} 个班，共 {total_classes} 个")

    # ── 2. 生成教师 CSV ──
    print("📌 第二步：生成教师数据...")
    used_names = set()
    titles_pool = ["教授", "教授", "副教授", "副教授", "副教授", "讲师", "讲师", "讲师", "讲师", "助教", "高级工程师", "工程师"]
    teacher_data = []
    for i in range(1, 276):
        name = random_name(used_names)
        no = f"T{20240000 + 25 + i}"
        title = random.choice(titles_pool)
        phone = f"138{random.randint(10000000, 99999999)}"
        teacher_data.append((name, no, title, phone, 1))
    tch_path = os.path.join(TEST_DIR, "teacher_big.csv")
    with open(tch_path, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["name", "no", "title", "phone", "status"])
        w.writerows(teacher_data)
    print(f"  新增 {len(teacher_data)} 位教师，共 {25 + len(teacher_data)} 人")

    # ── 3. 生成学生 CSV ──
    print("📌 第三步：生成学生数据...")
    used_names = set()
    stu_path = os.path.join(TEST_DIR, "student_big.csv")
    with open(stu_path, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["name", "no", "class_id", "status"])
        for i in range(1, TARGET_STUDENTS - max_stu_id + 1):
            name = random_name(used_names)
            no = max_stu_no + i
            cid = random.randint(1, total_classes)
            status = 0 if random.random() < 0.15 else 1
            w.writerow([name, no, cid, status])
    print(f"  共 {TARGET_STUDENTS} 名学生")

    # ── 4. 扩排课（直接入库）──
    print("📌 第四步：扩排课至 1000+ 条...")
    conn = get_connection()
    cur = conn.cursor()
    semesters = [f"{y}-{y + 1}-{s}" for y in range(2024, 2024 + SEMESTER_YEARS) for s in (1, 2)]
    cur.execute("SELECT id FROM teacher WHERE is_deleted=0 AND status=1")
    teacher_ids = [r[0] for r in cur.fetchall()]
    for _ in range(950):
        cid = random.choice(course_ids)
        tid = random.choice(teacher_ids)
        sem = random.choice(semesters)
        start = datetime.now() - timedelta(days=random.randint(0, 365 * SEMESTER_YEARS))
        end = start + timedelta(days=90)
        deadline = end + timedelta(days=180)
        cur.execute(
            "INSERT INTO course_offering (course_id, teacher_id, semester, max_students, "
            "enroll_start_time, enroll_end_time, grade_deadline) VALUES (%s,%s,%s,99999,%s,%s,%s)",
            [cid, tid, sem, start, end, deadline]
        )
    conn.commit()
    cur.execute("SELECT MAX(id) FROM course_offering")
    max_off_id = cur.fetchone()[0] or 0
    conn.close()
    print(f"  排课共 {max_off_id} 条")

    # ── 5. 生成选课 CSV ──
    print("📌 第五步：生成选课数据...")
    max_pairs = max_off_id * TARGET_STUDENTS
    target = min(TARGET_ENROLLMENTS, max_pairs)
    enr_path = os.path.join(TEST_DIR, "enrollment_big.csv")
    used_pairs = set()
    rows_count = 0
    with open(enr_path, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["offering_id", "student_id", "score"])
        while rows_count < target:
            oid = random.randint(1, max_off_id)
            sid = random.randint(1, TARGET_STUDENTS)
            pair = (oid, sid)
            if pair not in used_pairs:
                used_pairs.add(pair)
                score = "\\N" if random.random() < 0.25 else f"{max(0, min(100, random.gauss(75, 15))):.1f}"
                w.writerow([oid, sid, score])
                rows_count += 1
                if rows_count % 500_000 == 0:
                    print(f"   已生成 {rows_count:,} / {target:,}")
    print(f"  选课共 {rows_count} 条")

    # ── 6. 导入数据库 ──
    print("\n📌 第六步：导入数据库...")
    sql_path = os.path.join(TEST_DIR, "load_large_data.sql")
    trigger_path = os.path.join(os.path.dirname(TEST_DIR), "sql", "06_触发器.sql")

    # 确保 local_infile 开启
    subprocess.run(["mysql", "-u", "root", "-e", "SET GLOBAL local_infile = 1;"],
                   capture_output=True)

    # 主数据导入
    r = subprocess.run(
        f"mysql -u root --local-infile=1 db_sms < \"{sql_path}\"",
        shell=True, capture_output=True, text=True, encoding="utf-8", errors="replace"
    )
    for line in r.stdout.split("\n"):
        if line.strip():
            print(f"  {line.strip()}")

    # 单独恢复触发器（DELIMITER 不支持批量模式，用 Python 直连重建）
    print("  重建 5 个触发器中...")
    conn_t = get_connection()
    cur_t = conn_t.cursor()
    cur_t.execute("DROP TRIGGER IF EXISTS trg_enrollment_before_insert")
    cur_t.execute("DROP TRIGGER IF EXISTS trg_enrollment_after_insert")
    cur_t.execute("DROP TRIGGER IF EXISTS trg_enrollment_after_insert_score")
    cur_t.execute("DROP TRIGGER IF EXISTS trg_enrollment_after_update")
    cur_t.execute("DROP TRIGGER IF EXISTS trg_enrollment_after_update_score")
    conn_t.commit()

    triggers = [
        ("""CREATE TRIGGER trg_enrollment_before_insert
BEFORE INSERT ON enrollment FOR EACH ROW
BEGIN
    DECLARE v_current INT; DECLARE v_max INT;
    SELECT current_students, max_students INTO v_current, v_max
    FROM course_offering WHERE id = NEW.offering_id FOR UPDATE;
    IF v_current >= v_max THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = CONCAT('选课已满！当前 ', v_current, '/', v_max);
    END IF;
END"""),
        ("""CREATE TRIGGER trg_enrollment_after_insert
AFTER INSERT ON enrollment FOR EACH ROW
BEGIN
    UPDATE course_offering SET current_students = current_students + 1
    WHERE id = NEW.offering_id;
END"""),
        ("""CREATE TRIGGER trg_enrollment_after_insert_score
AFTER INSERT ON enrollment FOR EACH ROW
BEGIN
    IF NEW.score IS NOT NULL THEN
        UPDATE student s SET weighted_score = (
            SELECT ROUND(SUM(e.score * c.credit) / SUM(c.credit), 2)
            FROM enrollment e JOIN course_offering co ON e.offering_id = co.id
            JOIN course c ON co.course_id = c.id
            WHERE e.student_id = NEW.student_id AND e.score IS NOT NULL AND e.is_deleted = 0
        ), gpa = (
            SELECT ROUND(SUM(c.credit * r.point) / SUM(c.credit), 2)
            FROM enrollment e JOIN course_offering co ON e.offering_id = co.id
            JOIN course c ON co.course_id = c.id
            JOIN grade_point_rule r ON e.score BETWEEN r.min_score AND r.max_score
            WHERE e.student_id = NEW.student_id AND e.score IS NOT NULL AND e.is_deleted = 0
        ) WHERE s.id = NEW.student_id;
    END IF;
END"""),
        ("""CREATE TRIGGER trg_enrollment_after_update
AFTER UPDATE ON enrollment FOR EACH ROW
BEGIN
    IF OLD.is_deleted = 0 AND NEW.is_deleted = 1 THEN
        UPDATE course_offering SET current_students = current_students - 1
        WHERE id = NEW.offering_id;
    END IF;
END"""),
        ("""CREATE TRIGGER trg_enrollment_after_update_score
AFTER UPDATE ON enrollment FOR EACH ROW
BEGIN
    IF NOT (OLD.score <=> NEW.score) THEN
        UPDATE student s SET weighted_score = (
            SELECT ROUND(SUM(e.score * c.credit) / SUM(c.credit), 2)
            FROM enrollment e JOIN course_offering co ON e.offering_id = co.id
            JOIN course c ON co.course_id = c.id
            WHERE e.student_id = NEW.student_id AND e.score IS NOT NULL AND e.is_deleted = 0
        ), gpa = (
            SELECT ROUND(SUM(c.credit * r.point) / SUM(c.credit), 2)
            FROM enrollment e JOIN course_offering co ON e.offering_id = co.id
            JOIN course c ON co.course_id = c.id
            JOIN grade_point_rule r ON e.score BETWEEN r.min_score AND r.max_score
            WHERE e.student_id = NEW.student_id AND e.score IS NOT NULL AND e.is_deleted = 0
        ) WHERE s.id = NEW.student_id;
    END IF;
END"""),
    ]
    for t in triggers:
        cur_t.execute(t)
    conn_t.commit()
    conn_t.close()
    print(f"  5 个触发器已恢复 ✅")

    # ── 7. 清理 CSV ──
    print("\n📌 第七步：清理临时 CSV 文件...")
    for f in ["class_big.csv", "teacher_big.csv", "student_big.csv", "enrollment_big.csv"]:
        p = os.path.join(TEST_DIR, f)
        if os.path.exists(p):
            os.remove(p)
            print(f"  ✅ 已删除 {f}")

    print("\n" + "=" * 50)
    print("  🎉 全部完成！")
    print("=" * 50)


if __name__ == "__main__":
    main()
