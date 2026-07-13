"""登录认证"""

from core.utils import hr


def login(conn):
    """返回 (角色, id, name, no)  角色: 'admin' | 'teacher' | 'student'"""
    hr()
    user_no = input(
        "  请输入工号/学号 (教务输入 admin, 退出输入 q): "
    ).strip()  # 清理空格
    hr()

    if not user_no:
        return None
    if user_no.lower() in ("exit", "quit", "q"):
        return ("quit", 0, "", "")

    if user_no == "admin":
        return ("admin", 0, "教务管理员", "admin")
    if user_no == "test":
        return ("tester", 0, "测试员", "test")
    cur = conn.cursor()

    cur.execute(
        "SELECT id, name FROM teacher WHERE no = %s AND is_deleted = 0", [user_no]
    )
    row = cur.fetchone()  # 取一行（fetch：取），返回一个元组
    if row:
        return ("teacher", row[0], row[1], user_no)

    cur.execute(
        "SELECT id, name FROM student WHERE no = %s AND is_deleted = 0", [user_no]
    )
    row = cur.fetchone()
    if row:
        return ("student", row[0], row[1], user_no)

    return None
