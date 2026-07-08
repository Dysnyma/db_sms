# Python 代码说明文档

## 目录结构

```
scripts/
├── main.py            # 程序入口
├── import_data.py     # 批量导入 CSV 数据
├── reset_data.py      # 一键重建数据库+导入
├── student.py         # 学生角色
├── teacher.py         # 教师角色
├── admin.py           # 教务角色（含备份恢复）
├── tester.py          # 测试员角色（全功能）
└── core/
    ├── __init__.py     # 包标识
    ├── config.py       # 数据库连接配置
    ├── utils.py        # 工具函数
    └── auth.py         # 登录认证
```

---

## 一、入口文件

### `main.py` —— 程序入口

- `main()`：连接数据库 → 显示标题 → 循环登录
- 根据角色分发到 student / teacher / admin / tester 的 `menu()`

**调用链：**
```
main() → auth.login() → 判断角色 → xxx.menu()
```

---

## 二、核心模块 `core/`

### `config.py` —— 数据库连接

```python
DB = { host, port, user, password, database, charset }
connect() → 返回 pymysql 连接对象
```

### `utils.py` —— 工具函数

| 函数 | 功能 |
|------|------|
| `cls()` | 清屏（os.system + ANSI 双保险） |
| `pause()` | 显示"按回车继续"→ 等待 → 清屏 |
| `hr()` | 打印分隔线 `━━━` |
| `input_choice(prompt)` | 读取数字输入，失败返回 -1 |

### `auth.py` —— 登录认证

```python
login(conn) → (role, id, name, no)
```

| 输入 | 角色 |
|------|------|
| `admin` | 教务 |
| `test` | 测试员 |
| 教师工号（如 T20240001） | 教师 |
| 学生学号（如 202210101） | 学生 |
| `q` / `exit` / `quit` | 退出程序 |
| 空 | 重试 |

---

## 三、角色模块

### `student.py` —— 学生功能

| 函数 | 功能 | 调用的存储过程 |
|------|------|---------------|
| `menu(conn, sid, sname, sno)` | 学生菜单循环 | — |
| `show_courses(conn, sno)` | 查询可选课程 | `sp_show_courses` |
| `enroll(conn, sno)` | 选课 | `sp_enroll` |
| `unenroll(conn, sno)` | 退选 | `sp_unenroll` |
| `my_grades(conn, sid, sname)` | 查看我的成绩单 | 直接 SQL |
| `semester_avg(conn, sno)` | 学期均分 | `sp_student_semester_avg` |

### `teacher.py` —— 教师功能

| 函数 | 功能 | 调用的存储过程 |
|------|------|---------------|
| `menu(conn, tid, tname, tno)` | 教师菜单循环 | — |
| `grade_input(conn, tno)` | 录成绩（先展示学生名单） | `sp_grade_input` |
| `my_students(conn, tid, tname)` | 查看排课+学生名单 | 直接 SQL |

### `admin.py` —— 教务功能

| 函数 | 功能 | 调用的存储过程 |
|------|------|---------------|
| `menu(conn)` | 教务菜单循环 | — |
| `summary(conn)` | 数据概览（6 张表计数） | 直接 SQL |
| `roster(conn)` | 班级学生名单 | `sp_student_roster` |
| `class_report(conn)` | 班级+课程成绩统计 | `sp_class_grade_report` |
| `teacher_info(conn)` | 单个教师信息 | `sp_teacher_info` |
| `teacher_list(conn)` | 全部教师列表 | `sp_teacher_list` |
| `backup(conn)` | 备份数据库到 SQL 文件 | `mysqldump` |
| `restore(conn)` | 从 SQL 文件恢复数据库 | `mysql` |

**备份恢复原理：**
```python
# 备份：调用 mysqldump
mysqldump -u root --databases db_sms > backup/backup_20260708_120000.sql

# 恢复：调用 mysql 执行 SQL 文件
mysql -u root db_sms < backup/backup_20260708_120000.sql
```

### `tester.py` —— 测试员功能

- 登录输入 `test`
- 整合全部角色功能（通过 import 引用，不重复代码）
- 提供 S/T 键切换学生/教师身份

| import 来源 | 导入的函数 |
|------------|-----------|
| `student.py` | `show_courses, enroll, unenroll, my_grades, semester_avg` |
| `teacher.py` | `grade_input, my_students` |
| `admin.py` | `summary, roster, class_report, teacher_info, teacher_list, backup, restore` |

---

## 四、数据脚本

### `import_data.py` —— 批量导入

从 `data/` 目录读取 CSV 文件，按依赖顺序导入：

```
class → teacher → course → teacher_course → student → course_offering → enrollment
```

导入选课时逐条处理（先查 ID 再 INSERT），避免触发器与外层 SQL 冲突。

### `reset_data.py` —— 一键重建

1. 依次执行 7 个 SQL 文件（通过 `mysql` 命令行）
2. 调用 `import_data.main()` 导入数据

---

## 五、函数调用关系图

```
main.py
  └─ auth.login()
  └─ student.menu(conn, sid, sname, sno)
  │     ├─ show_courses()     → sp_show_courses
  │     ├─ enroll()           → sp_enroll
  │     ├─ unenroll()         → sp_unenroll
  │     ├─ my_grades()        → SQL
  │     └─ semester_avg()     → sp_student_semester_avg
  │
  └─ teacher.menu(conn, tid, tname, tno)
  │     ├─ grade_input()      → sp_grade_input
  │     └─ my_students()      → SQL
  │
  └─ admin.menu(conn)
  │     ├─ summary()          → SQL
  │     ├─ roster()           → sp_student_roster
  │     ├─ class_report()     → sp_class_grade_report
  │     ├─ teacher_info()     → sp_teacher_info
  │     ├─ teacher_list()     → sp_teacher_list
  │     ├─ backup()           → mysqldump
  │     └─ restore()          → mysql
  │
  └─ tester.menu(conn, ...)
        └─ 引用上述全部函数
```

---

## 六、关键技术点

| 技术 | 应用场景 |
|------|---------|
| `pymysql` | 数据库连接、存储过程调用 |
| `subprocess` | 备份恢复（mysqldump/mysql） |
| `csv.DictReader` | 读取 CSV 测试数据 |
| `os.system` + ANSI | 清屏 |
| `sys.stdout.flush` | 确保提示立即显示 |
| `try/except` | 存储过程错误捕获 |
| `cur.nextset()` | 排空存储过程多余结果集 |
| `f-string` | 格式化输出 |
| 制表符 `\t` | 中英文混排对齐 |
