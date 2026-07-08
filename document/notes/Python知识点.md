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
