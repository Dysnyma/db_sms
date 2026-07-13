# 学生成绩管理系统 (Student Grade Management System)

数据库系统课程设计 —— 题目二

## 项目简介

基于 **MySQL + Streamlit** 的学生成绩管理系统，支持三种角色登录：

| 角色 | 功能 |
|------|------|
| **管理员** | 数据概览、班级/学生/教师/课程 CRUD、排课管理、数据库备份恢复 |
| **教师** | 录入成绩（单个 / CSV 批量导入）、查看任课班级学生 |
| **学生** | 选课/退课、查看各科成绩、学期均分和绩点 |

## 技术栈

- **语言**：Python 3.12
- **Web 框架**：Streamlit
- **数据库**：MySQL 8.0（InnoDB, utf8mb4）
- **驱动**：PyMySQL
- **数据**：pandas, CSV

## 快速开始

### 1. 环境准备

```bash
pip install streamlit pymysql pandas
```

确保本地 MySQL 服务已启动（默认 127.0.0.1:3306）。

### 2. 初始化数据库

```bash
# 一键建库 + 导入种子数据
python code/reset_data.py
```

或手动按顺序执行 `SQL/` 目录下的 `.sql` 文件：

```
01_数据库创建.sql → 02_基础数据表.sql → 03_中间表.sql → 04_视图.sql → 06_触发器.sql → 07_存储过程.sql → 08_存储函数.sql
```

然后导入 CSV 数据：

```bash
python code/import_data.py
```

### 3. 启动应用

```bash
# Web 界面（推荐）
streamlit run code/app.py

# 命令行界面
python code/main.py
```

### 4. 登录

- **管理员**：在工号/学号输入框输入 `admin`
- **教师**：输入教师工号（如 `T001`）
- **学生**：输入学号（如 `S001`）

## 数据库设计

- **数据库名**：`db_sms`
- **字符集**：`utf8mb4` / `utf8mb4_unicode_ci`
- **存储引擎**：`InnoDB`
- **设计规范**：全表逻辑删除（`is_deleted`），`status` 与 `is_deleted` 职责分离

### 核心表

| 表 | 说明 |
|----|------|
| `class` | 班级 |
| `student` | 学生（N:1 班级） |
| `teacher` | 教师 |
| `course` | 课程 |
| `course_offering` | 排课（关联课程、教师、时间、容量） |
| `enrollment` | 选课（学生 N:M 排课，含成绩） |
| `teacher_course` | 教师可授课程 |
| `grade_point_rule` | 分数→绩点转换规则 |

## 项目结构

```
├── code/               # Python 源码
│   ├── app.py          # Streamlit Web 入口
│   ├── main.py         # CLI 入口
│   ├── reset_data.py   # 一键重建数据库
│   ├── import_data.py  # CSV 数据导入
│   └── core/           # 配置、认证、工具函数
├── SQL/                # 数据库 DDL/DML
├── data/               # 种子 CSV 数据
├── backup/             # 数据库备份
├── document/           # 课程设计文档、报告
├── archive/            # 历史参考文件
└── images/             # 图片资源
```

## 配置

数据库连接在 `code/core/config.py` 中修改：

```python
DB = {
    'host': '127.0.0.1',
    'port': 3306,
    'user': 'root',
    'password': '',
    'database': 'db_sms',
    'charset': 'utf8mb4',
}
```
