"""
生成仿真数据并写入 data/*.csv
运行方式：python data/generate_data.py
覆盖现有的 CSV 文件，然后可用 reset_data.py 导入数据库

所有数据关系一致：
  teacher_course → course 存在, teacher 存在
  course_offering → course 存在, teacher 存在
  student → class 存在
  enrollment → course_offering 存在, student 存在，且不重复
"""

import csv
import os
import random
from collections import defaultdict

random.seed(42)

DATA_DIR = os.path.dirname(os.path.abspath(__file__))

# ── 配置 ──
TARGET_STUDENTS = 1000
GRADES = ["2022", "2023", "2024"]
TEACHER_COUNT = 25

# ── 姓名库 ──
SURNAMES = list("张李王赵陈刘黄周吴郑钱孙朱马胡林郭何高罗梁宋唐许邓冯韩曹曾彭萧蔡潘田董袁于叶蒋余杜苏魏")
GIVEN_M = ["伟", "强", "磊", "军", "勇", "杰", "涛", "明", "超", "波",
           "斌", "峰", "辉", "刚", "健", "龙", "翔", "鹏", "博", "文",
           "飞", "浩", "亮", "建华", "志强", "国栋"]
GIVEN_F = ["芳", "敏", "静", "丽", "娟", "燕", "霞", "娜", "莹", "婷",
           "琳", "颖", "宁", "雪", "萌", "瑶", "倩", "洁", "蕊",
           "秀英", "玉兰", "晓红", "雪梅"]


def random_name(used):
    while True:
        s = random.choice(SURNAMES)
        g = random.choice(GIVEN_M + GIVEN_F)
        name = s + g
        if name not in used:
            used.add(name)
            return name


def main():
    # ── 读取专业列表 ──
    with open(os.path.join(DATA_DIR, "majors.csv"), encoding="utf-8") as f:
        majors = [r["name"] for r in csv.DictReader(f)]
    # 取前 6 个，避免班级太分散
    majors = majors[:6]
    print(f"专业: {len(majors)} 个")

    # ═══════════════════════════════════════════
    # 1. 班级
    # ═══════════════════════════════════════════
    class_list = []  # (name, grade, major)

    def make_class(grade, major):
        seq = 1
        for n, g, m in class_list:
            if g == grade and m == major:
                seq += 1
        name = f"{grade}{major}{seq}班"
        class_list.append((name, grade, major))

    for g in GRADES:
        for m in majors:
            make_class(g, m)
            # 计算机、软件工程各开 2 个班
            if m in ("计算机科学与技术", "软件工程"):
                make_class(g, m)

    with open(os.path.join(DATA_DIR, "class.csv"), "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["name", "grade", "major"])
        w.writerows(class_list)
    print(f"班级: {len(class_list)} 个")

    # ═══════════════════════════════════════════
    # 2. 教师
    # ═══════════════════════════════════════════
    titles_pool = ["教授", "教授", "副教授", "副教授", "副教授", "副教授",
                   "讲师", "讲师", "讲师", "讲师", "讲师", "讲师",
                   "助教", "助教", "高级工程师", "工程师"]
    teacher_list = []  # (name, no, title, phone)
    used_name = set()
    for i in range(TEACHER_COUNT):
        name = random_name(used_name)
        no = f"T{20240000 + i + 1}"
        title = random.choice(titles_pool)
        phone = f"138{random.randint(10000000, 99999999)}"
        teacher_list.append((name, no, title, phone))

    with open(os.path.join(DATA_DIR, "teacher.csv"), "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["name", "no", "title", "phone"])
        w.writerows(teacher_list)
    print(f"教师: {len(teacher_list)} 人")

    # ═══════════════════════════════════════════
    # 3. 课程
    # ═══════════════════════════════════════════
    course_list = [
        ("数据库系统", 3.0), ("操作系统", 4.0), ("数据结构", 4.0),
        ("计算机网络", 3.0), ("软件工程", 2.0), ("人工智能", 3.0),
        ("编译原理", 3.0), ("离散数学", 3.0), ("高等数学", 5.0),
        ("线性代数", 3.0), ("大学英语", 4.0), ("算法设计", 3.0),
        ("Python程序设计", 2.5), ("Web开发技术", 2.5),
        ("机器学习", 3.0), ("计算机组成原理", 3.5),
        ("概率论与数理统计", 3.0), ("数字逻辑", 2.5),
    ]

    with open(os.path.join(DATA_DIR, "course.csv"), "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["name", "credit"])
        w.writerows(course_list)
    print(f"课程: {len(course_list)} 门")

    # ═══════════════════════════════════════════
    # 4. 讲授关系  teacher_no + course_name
    # ═══════════════════════════════════════════
    tc_list = []  # (teacher_no, course_name)
    for _, tno, *_ in teacher_list:
        for cname, *_ in random.sample(course_list, random.randint(1, 4)):
            tc_list.append((tno, cname))

    with open(os.path.join(DATA_DIR, "teacher_course.csv"), "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["teacher_no", "course_name"])
        w.writerows(tc_list)
    print(f"讲授关系: {len(tc_list)} 条")

    # ═══════════════════════════════════════════
    # 5. 学生
    # ═══════════════════════════════════════════
    student_list = []  # (name, no, class_name)
    used_name = set()
    per_class = TARGET_STUDENTS // len(class_list)
    remainder = TARGET_STUDENTS % len(class_list)

    for ci, (cname, cgrade, _) in enumerate(class_list):
        n = per_class + (1 if ci < remainder else 0)
        base = int(cgrade) * 10000 + (ci + 1) * 100
        for si in range(1, n + 1):
            name = random_name(used_name)
            sno = str(base + si)
            student_list.append((name, sno, cname))

    with open(os.path.join(DATA_DIR, "student.csv"), "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["name", "no", "class_name"])
        w.writerows(student_list)
    print(f"学生: {len(student_list)} 人")

    # ═══════════════════════════════════════════
    # 6. 排课  course_name + teacher_no + semester + ...
    # ═══════════════════════════════════════════
    # 限定在合理的学期范围内（与学生入学时间匹配）
    semesters = ["2024-2025-1", "2024-2025-2", "2025-2026-1", "2025-2026-2",
                 "2026-2027-1", "2026-2027-2"]
    sem_times = {
        "2024-2025-1": ("2024-07-01", "2024-09-15", "2025-01-31"),
        "2024-2025-2": ("2025-02-01", "2025-03-01", "2025-07-15"),
        "2025-2026-1": ("2025-07-01", "2025-09-15", "2026-01-31"),
        "2025-2026-2": ("2026-02-01", "2026-03-01", "2026-07-15"),
        "2026-2027-1": ("2026-07-01", "2026-09-15", "2027-01-31"),
        "2026-2027-2": ("2027-02-01", "2027-03-01", "2027-07-15"),
    }

    offering_list = []  # (course_name, teacher_no, semester, max_students, enroll_start, enroll_end, grade_deadline)
    # 构建 teacher_no → set(course_name)
    tc_map = defaultdict(set)
    for tno, cname in tc_list:
        tc_map[tno].add(cname)

    for cname, *_ in course_list:
        # 找到所有能教该课的教师
        qualified = [tno for tno, cs in tc_map.items() if cname in cs]
        if not qualified:
            continue
        for sem in random.sample(semesters, random.randint(2, 4)):
            tno = random.choice(qualified)
            max_s = random.randint(60, 120)
            start_d, enroll_end, deadline_d = sem_times[sem]
            offering_list.append((
                cname, tno, sem, max_s,
                f"{start_d} 08:00:00",
                f"{enroll_end} 23:59:59",
                f"{deadline_d} 23:59:59",
            ))

    with open(os.path.join(DATA_DIR, "course_offering.csv"), "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["course_name", "teacher_no", "semester", "max_students",
                     "enroll_start", "enroll_end", "grade_deadline"])
        w.writerows(offering_list)
    print(f"排课: {len(offering_list)} 条")

    # ═══════════════════════════════════════════
    # 7. 选课 + 成绩
    # ═══════════════════════════════════════════
    # 构建 (course_name, teacher_no, semester) → offering_index 的索引
    offering_idx = {}
    for i, o in enumerate(offering_list):
        offering_idx[(o[0], o[1], o[2])] = i

    # 构建每个学期有哪些排课
    sem_offerings = defaultdict(list)
    for i, o in enumerate(offering_list):
        sem_offerings[o[2]].append(i)

    enrollment_list = []  # (student_no, course_name, teacher_no, semester, score)
    used_enrollment = set()
    offering_used = [0] * len(offering_list)  # 已选人数跟踪

    for sname, sno, cname in student_list:
        sgrade = int(cname[:4])
        taken = 0
        target = random.randint(2, 4)
        # 按时间顺序遍历学期
        for sem in semesters:
            if taken >= target:
                break
            sem_start_year = int(sem[:4])
            # 学生在该学期是否在校：入学年份 ≤ 学期开始年份 < 入学年份+4
            if not (sgrade <= sem_start_year < sgrade + 4):
                continue
            available = sem_offerings.get(sem, [])
            if not available:
                continue
            # 每学期选 1-2 门
            for oi in random.sample(available, min(random.randint(1, 2), len(available))):
                if taken >= target:
                    break
                key = (sno, oi)
                if key in used_enrollment:
                    continue
                # 检查选课容量
                if offering_used[oi] >= offering_list[oi][3]:
                    continue
                used_enrollment.add(key)
                offering_used[oi] += 1
                cn, tn, sem_s, *_ = offering_list[oi]
                score = round(random.gauss(75, 15), 1)
                score = max(0, min(100, score))
                enrollment_list.append((sno, cn, tn, sem_s, score))
                taken += 1

    with open(os.path.join(DATA_DIR, "enrollment.csv"), "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["student_no", "course_name", "teacher_no", "semester", "score"])
        w.writerows(enrollment_list)
    print(f"选课+成绩: {len(enrollment_list)} 条")

    # ── 汇总 ──
    print(f"\n{'='*40}")
    print(f"  班级: {len(class_list)}")
    print(f"  教师: {len(teacher_list)}")
    print(f"  课程: {len(course_list)}")
    print(f"  讲授关系: {len(tc_list)}")
    print(f"  学生: {len(student_list)}")
    print(f"  排课: {len(offering_list)}")
    print(f"  选课+成绩: {len(enrollment_list)}")
    print(f"{'='*40}")
    print("运行 python reset_data.py 导入数据库")


if __name__ == "__main__":
    main()
