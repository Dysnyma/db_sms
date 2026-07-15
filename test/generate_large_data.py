"""
200 万仿真数据生成器
用法：
    pip install faker          # 可选，不装也能用随机中文名
    python test/generate_large_data.py

输出：test/enrollment_big.csv
      test/student_big.csv（扩展学生用）
"""

from core.config import connect as get_connection
import csv
import os
import random
import sys
from datetime import datetime, timedelta

# 添加 src 到路径
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src"))

TEST_DIR = os.path.dirname(os.path.abspath(__file__))

# ── 姓名库 ──
SURNAMES = list("张李王赵陈刘黄周吴郑钱孙朱马胡林郭何高罗梁宋唐许邓冯韩曹曾彭萧蔡潘田董袁于叶蒋余杜苏魏程吕丁沈任姚卢傅钟崔")
GIVEN = list("伟强磊军勇杰涛明超波斌峰辉刚健龙翔鹏博文飞浩亮华刚毅刚杰鑫杰铭洋健文浩宇昊然鸿涛志远泽宇昕宇梓豪俊哲睿")
GIVEN_F = list("芳敏静丽娟燕霞娜莹婷琳颖宁雪萌瑶倩洁蕊瑶婷美玲淑华桂英玉华秀英桂兰秀兰英")


def random_name(used):
    """支持单字名和双字名，约 40 * 100 * 100 = 40 万种组合"""
    while True:
        s = random.choice(SURNAMES)
        pool = GIVEN + GIVEN_F
        # 70% 双字名，30% 单字名
        if random.random() < 0.7:
            g = random.choice(pool) + random.choice(pool)
        else:
            g = random.choice(pool)
        name = s + g
        if name not in used:
            used.add(name)
            return name


def main():
    conn = get_connection()
    cur = conn.cursor()

    print("=" * 50)
    print("  读取现有数据库基础数据...")
    print("=" * 50)

    # ── 读取现有数据 ──
    cur.execute("SELECT MAX(id) FROM student")
    max_stu_id = cur.fetchone()[0] or 0

    cur.execute("SELECT MAX(CAST(no AS UNSIGNED)) FROM student")
    max_stu_no = cur.fetchone()[0] or 20240000

    cur.execute("SELECT COUNT(*) FROM class WHERE is_deleted = 0")
    cls_cnt = cur.fetchone()[0]

    cur.execute("SELECT MAX(id) FROM course_offering")
    max_off_id = cur.fetchone()[0] or 0

    cur.execute("SELECT MAX(id) FROM student")
    total_students = cur.fetchone()[0] or 0

    conn.close()

    print(f"  当前学生 ID 范围: 1 ~ {total_students}")
    print(f"  当前排课 ID 范围: 1 ~ {max_off_id}")
    print(f"  现有班级数: {cls_cnt}")

    # ── 扩排课：先在数据库插入新排课 ──
    print("\n  扩展排课至 1000 条...")
    conn = get_connection()
    cur = conn.cursor()
    from datetime import datetime, timedelta
    semesters = ['2024-2025-1','2024-2025-2','2025-2026-1','2025-2026-2','2026-2027-1','2026-2027-2']
    course_cnt = max_off_id  # 排课跟课程数差不多
    # 查找现有课程和教师 ID
    cur.execute("SELECT id FROM course WHERE is_deleted=0 ORDER BY id")
    course_ids = [r[0] for r in cur.fetchall()]
    cur.execute("SELECT id FROM teacher WHERE is_deleted=0 AND status=1")
    teacher_ids = [r[0] for r in cur.fetchall()]
    for _ in range(950):
        cid = random.choice(course_ids)
        tid = random.choice(teacher_ids)
        sem = random.choice(semesters)
        start = datetime.now() - timedelta(days=random.randint(0, 365))
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
    print(f"  排课后最大 ID: {max_off_id}")

    # ── 生成扩展学生 CSV（19000 人） ──
    print("\n  生成扩展学生数据 19000 人...")
    used = set()
    csv_path = os.path.join(TEST_DIR, "student_big.csv")
    with open(csv_path, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["name", "no", "class_id", "status"])
        for i in range(1, 19001):
            name = random_name(used)
            no = max_stu_no + i
            cid = random.randint(1, cls_cnt)
            status = 0 if random.random() < 0.15 else 1
            w.writerow([name, no, cid, status])

    # ── 生成选课 CSV（流式写入，防唯一键冲突） ──
    max_all_id = total_students + 19000
    max_pairs = max_off_id * max_all_id  # 理论最大不重复组合
    target = min(2_000_000, max_pairs)   # 不超过理论上限
    print(f"  选课目标: {target:,} 条（理论最大 {max_pairs:,}）")
    csv_enr = os.path.join(TEST_DIR, "enrollment_big.csv")
    pct_ungraded = 0.25
    used_pairs = set()
    rows = 0

    with open(csv_enr, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["offering_id", "student_id", "score"])

        while rows < target:
            oid = random.randint(1, max_off_id)
            sid = random.randint(1, max_all_id)
            pair = (oid, sid)
            if pair in used_pairs:
                continue
            used_pairs.add(pair)

            if random.random() < pct_ungraded:
                score = "\\N"  # MySQL NULL 标准写法
            else:
                raw = random.gauss(75, 15)
                raw = max(0.0, min(100.0, raw))  # 截断越界
                score = f"{raw:.1f}"

            w.writerow([oid, sid, score])
            rows += 1
            if rows % 500_000 == 0:
                print(f"   已生成 {rows:,} 行...")

    print(f"\n✅ 文件生成完毕！")
    print(f"   学生: {csv_path}（未含已存在的 {total_students} 人）")
    print(f"   选课: {csv_enr}")
    print(f"\n后续步骤:")
    print(f"   1. mysql -u root db_sms < test/load_large_data.sql")
    print(f"   2. (导入完成后 CSV 自动删除)")


if __name__ == "__main__":
    main()
