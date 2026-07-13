"""
批量导入数据到 db_sms
用法：python 数据/import_data.py
前提：已执行 sql/01~03 建库建表
"""
import csv
import os
import pymysql
from datetime import datetime

# ---- 配置 ----
DB_CONFIG = {
    'host': '127.0.0.1',
    'port': 3306,
    'user': 'root',
    'password': '',
    'database': 'db_sms',
    'charset': 'utf8mb4',
}

DATA_DIR = os.path.join(os.path.dirname(
    os.path.abspath(__file__)), '..', 'data')


def connect():
    return pymysql.connect(**DB_CONFIG)


def log(msg):
    print(f'  [{datetime.now().strftime("%H:%M:%S")}] {msg}')


def import_csv(cursor, filepath, sql, *col_keys):
    """从 CSV 读取指定列，批量执行 INSERT"""
    rows = []
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append([row[k] for k in col_keys])
    if rows:
        cursor.executemany(sql, rows)
    return len(rows)


def main():
    conn = connect()
    cursor = conn.cursor()
    start = datetime.now()
    print(f'开始导入数据 → db_sms [{start.strftime("%Y-%m-%d %H:%M:%S")}]')
    print()

    try:
        # ---- 1. 班级 ----
        n = import_csv(cursor, f'{DATA_DIR}/class.csv',
                       'INSERT INTO class (name, grade, major) VALUES (%s, %s, %s)',
                       'name', 'grade', 'major')
        log(f'班级：{n} 条')

        # ---- 2. 教师 ----
        n = import_csv(cursor, f'{DATA_DIR}/teacher.csv',
                       'INSERT INTO teacher (name, no, title, phone) VALUES (%s, %s, %s, %s)',
                       'name', 'no', 'title', 'phone')
        log(f'教师：{n} 条')

        # ---- 3. 课程 ----
        n = import_csv(cursor, f'{DATA_DIR}/course.csv',
                       'INSERT INTO course (name, credit) VALUES (%s, %s)',
                       'name', 'credit')
        log(f'课程：{n} 条')

        # ---- 4. 讲授关系（依赖教师+课程） ----
        n = import_csv(cursor, f'{DATA_DIR}/teacher_course.csv',
                       '''INSERT INTO teacher_course (teacher_id, course_id)
               SELECT t.id, c.id FROM teacher t, course c
               WHERE t.no = %s AND c.name = %s
                 AND NOT EXISTS (
                   SELECT 1 FROM teacher_course tc
                   WHERE tc.teacher_id = t.id AND tc.course_id = c.id
                 )''',
                       'teacher_no', 'course_name')
        log(f'讲授关系：{n} 条')

        # ---- 5. 学生（依赖班级） ----
        n = import_csv(cursor, f'{DATA_DIR}/student.csv',
                       '''INSERT INTO student (name, no, class_id)
               SELECT %s, %s, c.id FROM class c
               WHERE c.name = %s''',
                       'name', 'no', 'class_name')
        log(f'学生：{n} 条')

        # ---- 6. 选课安排（依赖课程+教师） ----
        n = import_csv(cursor, f'{DATA_DIR}/course_offering.csv',
                       '''INSERT INTO course_offering (course_id, teacher_id, semester,
                       max_students, enroll_start_time, enroll_end_time, grade_deadline)
               SELECT c.id, t.id, %s, %s, %s, %s, %s
               FROM course c, teacher t
               WHERE c.name = %s AND t.no = %s''',
                       'semester', 'max_students', 'enroll_start', 'enroll_end', 'grade_deadline',
                       'course_name', 'teacher_no')
        log(f'选课安排：{n} 条')

        # ---- 7. 选课 + 成绩（逐条导入，避免触发器冲突） ----
        n = 0
        with open(f'{DATA_DIR}/enrollment.csv', 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                score_val = row['score'].strip(
                ) if row['score'].strip() else None
                # 先查排课ID和学生ID
                cursor.execute('''
                    SELECT co.id, s.id FROM course_offering co
                    JOIN course c ON co.course_id = c.id
                    JOIN teacher t ON co.teacher_id = t.id
                    JOIN student s ON s.no = %s
                    WHERE c.name = %s AND t.no = %s AND co.semester = %s
                ''', [row['student_no'], row['course_name'],
                      row['teacher_no'], row['semester']])
                r = cursor.fetchone()
                if not r:
                    continue
                oid, sid = r
                # 检查重复
                cursor.execute(
                    'SELECT 1 FROM enrollment WHERE offering_id=%s AND student_id=%s', [oid, sid])
                if cursor.fetchone():
                    continue
                # 单独 INSERT（不 JOIN course_offering，触发器可以安全更新它）
                if score_val is not None:
                    cursor.execute('INSERT INTO enrollment (offering_id, student_id, score) VALUES (%s, %s, %s)',
                                   [oid, sid, float(score_val)])
                else:
                    cursor.execute('INSERT INTO enrollment (offering_id, student_id) VALUES (%s, %s)',
                                   [oid, sid])
                n += 1
        log(f'选课 + 成绩：{n} 条')

        conn.commit()
        print()
        log('全部导入成功！')

    except Exception as e:
        conn.rollback()
        print(f'\n  导入失败: {e}')
        raise
    finally:
        cursor.close()
        conn.close()
        elapsed = (datetime.now() - start).total_seconds()
        print(f'  耗时: {elapsed:.1f} 秒')


if __name__ == '__main__':
    main()
