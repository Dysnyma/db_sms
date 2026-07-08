"""测试员 —— 可操作所有功能"""
import sys
from core.utils import cls, pause, hr
from student import show_courses, enroll, unenroll, my_grades, semester_avg
from teacher import grade_input, batch_grade_input, my_students
from admin import summary, roster, class_report, teacher_info, teacher_list, backup, restore


def menu(conn, tid, tname, tno):
    stu_no = ''
    stu_id = 0
    stu_name = ''
    tch_no = ''
    tch_id = 0
    tch_name = ''

    while True:
        cls()
        hr()
        print(f'  {tname} [测试员]')
        if stu_no:
            print(f'  学生: {stu_name}({stu_no})')
        if tch_no:
            print(f'  教师: {tch_name}({tch_no})')
        hr()
        print('  S.切换学生   T.切换教师')
        print('  【学生】1.查课程  2.选课  3.退选  4.成绩  5.学期均分')
        print('  【教师】6.录成绩  7.批量录(CSV)  8.看课程学生')
        print('  【教务】9.概览  10.班级名单  11.成绩统计  12.教师信息  13.教师列表  14.备份  15.恢复')
        print('  0.退出')
        hr()

        raw = input('  请选择: ').strip().lower()

        if raw == '0':
            break

        elif raw == 's':
            no = input('  输入学生学号: ').strip()
            if no:
                cur = conn.cursor()
                cur.execute(
                    "SELECT id,name FROM student WHERE no=%s AND is_deleted=0", [no])
                r = cur.fetchone()
                if r:
                    stu_no, stu_id, stu_name = no, r[0], r[1]
                    print(f'\n  ✅ 已切换为 {stu_name}')
                else:
                    print(f'\n  ❌ 学号不存在')
        elif raw == 't':
            no = input('  输入教师工号: ').strip()
            if no:
                cur = conn.cursor()
                cur.execute(
                    "SELECT id,name FROM teacher WHERE no=%s AND is_deleted=0", [no])
                r = cur.fetchone()
                if r:
                    tch_no, tch_id, tch_name = no, r[0], r[1]
                    print(f'\n  ✅ 已切换为 {tch_name}')
                else:
                    print(f'\n  ❌ 工号不存在')

        elif raw == '1':
            if stu_no:
                show_courses(conn, stu_no)
            else:
                print('\n  请先按 S 选择学生')
        elif raw == '2':
            if stu_no:
                enroll(conn, stu_no)
            else:
                print('\n  请先按 S 选择学生')
        elif raw == '3':
            if stu_no:
                unenroll(conn, stu_no)
            else:
                print('\n  请先按 S 选择学生')
        elif raw == '4':
            if stu_id:
                my_grades(conn, stu_id, stu_name)
            else:
                print('\n  请先按 S 选择学生')
        elif raw == '5':
            if stu_no:
                semester_avg(conn, stu_no)
            else:
                print('\n  请先按 S 选择学生')
        elif raw == '6':
            if tch_no:
                grade_input(conn, tch_no)
            else:
                print('\n  请先按 T 选择教师')
        elif raw == '7':
            if tch_no:
                batch_grade_input(conn, tch_no)
            else:
                print('\n  请先按 T 选择教师')
        elif raw == '8':
            if tch_no:
                my_students(conn, tch_id, tch_name)
            else:
                print('\n  请先按 T 选择教师')
        elif raw == '9':
            summary(conn)
        elif raw == '10':
            roster(conn)
        elif raw == '11':
            class_report(conn)
        elif raw == '12':
            teacher_info(conn)
        elif raw == '13':
            teacher_list(conn)
        elif raw == '14':
            backup(conn)
        elif raw == '15':
            restore(conn)
        else:
            continue

        if raw in ('s', 't'):
            sys.stdout.write('\n  按回车...')
            sys.stdout.flush()
            input()
            cls()
        elif raw in ('0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15'):
            pause()
