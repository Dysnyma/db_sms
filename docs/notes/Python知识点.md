# Python 知识点总结（学生成绩管理系统实战）

## 1. pymysql 数据库操作

```python
import pymysql

# 连接
conn = pymysql.connect(host='127.0.0.1', port=3306, user='root',
                        password='', database='db_sms', charset='utf8mb4')

# 游标
cur = conn.cursor()

# 执行 SQL
cur.execute("SELECT id, name FROM student WHERE no = %s", [stu_no])

# 调用存储过程
cur.callproc('sp_enroll', [sno, plan_id])
conn.commit()

# 取结果
row = cur.fetchone()         # 一行 → (val1, val2, ...)
rows = cur.fetchall()        # 全部 → [(...), (...)]
cur.nextset()                # 跳过存储过程的多余结果集

# 事务
conn.commit()     # 提交
conn.rollback()   # 回滚

# 关闭
cur.close()
conn.close()
```

## 2. 模块拆分与导入

```
scripts/
├── main.py           ← 入口， import core.config, student, ...
├── core/
│   ├── __init__.py   ← 空文件，标识这是一个包
│   ├── config.py     ← 数据库配置
│   ├── utils.py      ← 工具函数
│   └── auth.py       ← 登录逻辑
├── student.py        ← 学生功能
├── teacher.py        ← 教师功能
└── admin.py          ← 教务功能
```

### 导入方式

```python
# 从子包导入
from core.config import connect
from core.utils import cls, pause, hr

# 导入同级模块
import student
import teacher

# 然后调用
student.menu(conn, uid, uname, uno)
```

### `__init__.py` 是干什么的

一个空文件，告诉 Python "这个文件夹是一个包"。没有它，`from core.xxx import ...` 会报错。

## 3. def 函数定义

```python
# 基本
def add(a, b):
    return a + b

# 多参数 + 默认值
def menu(conn, sid, sname, sno):
    ...

# 函数内部调用函数
def main():
    conn = connect()   # 先连库
    login(conn)         # 再登录
    student_menu(conn)  # 进入菜单
```

## 4. f-string 格式化

```python
name = "张三"
score = 85.5

# f 前缀，变量直接写进花括号
print(f'{name} 同学，你的成绩是 {score}')

# 对齐：<左对齐，数字是宽度
print(f'  {name:<10} {score:<8}')
# 输出:   张三        85.5

# 截断
print(f'{str(end)[:16]}')    # 只取前16个字符
```

## 5. try/except 异常处理

```python
try:
    cur.callproc('sp_enroll', [sno, plan_id])
    conn.commit()
    print('选课成功')
except Exception as e:
    conn.rollback()
    print(f'选课失败: {e}')
```

## 6. while 循环 + 菜单

```python
while True:
    print('1. 功能A')
    print('0. 退出')
    c = input('请选择: ')
    if c == '0':
        break          # 跳出循环
    elif c == '1':
        do_something()
    elif c == '':
        continue        # 空输入，重来
```

## 7. 清屏（跨平台）

```python
import os
import sys

def cls():
    os.system('cls')                    # Windows CMD
    sys.stdout.write('\033[2J\033[H')   # ANSI 强力清屏
    sys.stdout.flush()                  # 立即刷新
```

## 8. input 与 flush

```python
# 问题：print 没加 end 参数时自动换行，没问题
# 但 prompt 不带换行时，要 flush 才能立即显示
sys.stdout.write('请输入: ')
sys.stdout.flush()
result = input()
```

## 9. CSV 读写

```python
import csv

# 读
with open('data.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)           # 第一行是列名
    for row in reader:
        print(row['name'], row['no'])

# 写
with open('data.csv', 'w', newline='', encoding='utf-8') as f:
    w = csv.writer(f)
    w.writerow(['name', 'no'])           # 写表头
    w.writerow(['张三', '2024001'])       # 写数据
```

## 10. set 去重

```python
pairs = set()
pairs.add(('T001', '数据库'))
pairs.add(('T001', '数据库'))   # 重复，自动忽略
# 最终 pairs 里不重复
```

## 11. random 随机数

```python
import random
random.seed(42)                    # 固定种子，每次生成一样
random.randint(1000, 9999)         # 随机整数
random.choice(['教授', '讲师'])     # 随机选一个
```

## 12. 列表推导式

```python
# 传统写法
result = []
for x in range(10):
    result.append(x * 2)

# 推导式
result = [x * 2 for x in range(10)]
```

## 13. 全局变量 nonlocal

```python
def outer():
    count = 0
    def inner():
        nonlocal count    # 声明用的是外层的 count
        count += 1
    inner()
    print(count)          # 1
```

## 14. 元组、列表、字典对比

| 类型 | 符号 | 是否可改 | 取值方式 | 示例 |
|------|------|----------|----------|------|
| 元组 tuple | `( )` | ❌ 不可改 | 下标 `r[0]` | `(1, '张老师')` |
| 列表 list | `[ ]` | ✅ 可改 | 下标 `names[0]` | `['张三', '李四']` |
| 字典 dict | `{ }` | ✅ 可改 | 键 `d['name']` | `{'name': '张三', 'age': 20}` |

`fetchone()` 返回的是**元组**——因为查询字段顺序固定，用下标取就行。

## 15. if 变量直接判断（truthiness）

Python 中任何值都可以放在 `if` 后面：

| 值 | 判断结果 |
|----|---------|
| `None`, `0`, `0.0`, `''`（空字符串）, `[]`（空列表）, `()`（空元组） | ❌ False |
| 其他一切（非零数、非空字符串/列表/元组/字典） | ✅ True |

```python
row = cur.fetchone()    # (1, '张三') 或 None
if row:                 # 等价于 if row is not None:
    print('查到了')
else:
    print('没查到')
```

## 16. fetchone / fetchall / fetchmany 详解

```python
cur.execute("SELECT id, name FROM student")

# fetchone —— 取一行，返回元组；取完光标移到下一行；没得取时返回 None
row = cur.fetchone()      # (1, '张三')

# fetchall —— 取剩下全部，返回列表套元组
rows = cur.fetchall()     # [(1, '张三'), (2, '李四'), (3, '王五')]

# fetchmany(n) —— 取 n 行
rows = cur.fetchmany(5)   # 取 5 行
```

## 17. 同一游标重复 execute 会覆盖结果集

```python
cur.execute("SELECT ... FROM teacher ...")   # 第 1 个结果集
cur.execute("SELECT ... FROM student ...")   # 第 1 个结果集被覆盖！
```

**安全的做法：每次 execute 后立刻 fetch 到变量里。**

```python
cur.execute("SELECT ... FROM teacher ...")
row = cur.fetchone()    # ← 结果已存到 row 变量
if row:
    return ...

cur.execute("SELECT ... FROM student ...")  # ← 覆盖也没关系，上面已取走
```

## 18. with conn.cursor() 自动关闭游标

```python
# 传统写法（需要手动关闭）
cur = conn.cursor()
cur.execute("SELECT ...")
cur.close()              # ← 容易忘

# with 写法（自动关闭）
with conn.cursor() as cur:
    cur.execute("SELECT ...")
# ← 离开缩进块时自动 cur.close()，不管是否报错
```

## 19. nextset() —— 存储过程专用

存储过程可能产生**多个结果集**，`fetchall()` 只取第一个，剩下的残留会阻塞后续操作。

```python
cur.callproc('sp_show_courses', [sno])
rows = cur.fetchall()      # 取第一个结果集
cur.nextset()               # 跳到（并清理）下一个结果集
```

如果不写 `nextset()`，下次执行 SQL 会报错 `Commands out of sync`。

普通 `SELECT` 不需要 `nextset()`，只有 `callproc` 才需要。

## 20. `**` 字典解包

```python
DB = {'host': '127.0.0.1', 'port': 3306, 'user': 'root'}

pymysql.connect(**DB)
# 等价于：
pymysql.connect(host='127.0.0.1', port=3306, user='root')
```

- `*` → 拆列表/元组，变位置参数
- `**` → 拆字典，变关键字参数（必须字典，列表/元组不行）

## 21. 字符串切片 `[:]`

```python
s = "2025-07-08 18:00:00"
s[:16]    → "2025-07-08 18:00"   # 从开头取到第 16 个字符（不含）
s[5:]     → "07-08 18:00:00"     # 从第 5 个取到末尾
s[2:7]    → "25-07"              # 从第 2 个取到第 7 个
```

## 22. 链式调用

确定有结果时，可以省略中间变量：

```python
# 分两步
row = cur.fetchone()
msg = row[0]

# 合一步（链式调用）
msg = cur.fetchone()[0]
```

注意：如果 `fetchone()` 返回 `None`，`None[0]` 会报错，所以只在确定有结果时用。

## 23. 压缩 if-else（不推荐）

```python
# 压缩写法（不推荐，可读性差）
if r: a, b = r[0], r[1]; print(f'hi {a}')
else: print('no')

# 正常写法（推荐）
if r:
    a, b = r[0], r[1]
    print(f'hi {a}')
else:
    print('no')
```

分号 `;` 相当于换行，但影响可读性，不推荐使用。
