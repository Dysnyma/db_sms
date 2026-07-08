"""学生成绩管理系统 —— 命令行交互界面（三角色）"""
from core.config import connect
from core.utils import cls, pause
from core.auth import login
import student
import teacher
import admin
import tester


def main():
    conn = connect()
    cls()
    print()
    print('╔══════════════════════════════════════╗')
    print('║     学生成绩管理系统 v2.0            ║')
    print('╚══════════════════════════════════════╝')
    print()

    while True:
        user = login(conn)
        if user is None:
            print('\n  ❌ 用户不存在')
            pause()
            continue

        role, uid, uname, uno = user
        if role == 'quit':
            break
        print(f'\n  欢迎，{uname}！')
        pause()

        if role == 'student':
            student.menu(conn, uid, uname, uno)
        elif role == 'teacher':
            teacher.menu(conn, uid, uname, uno)
        elif role == 'tester':
            tester.menu(conn, uid, uname, uno)
        else:
            admin.menu(conn)

        cls()
        print('\n  已退出登录')

    conn.close()
    print('\n  再见！\n')


if __name__ == '__main__':
    main()
