# 学生成绩管理系统 (Student Grade Management System)

数据库系统课程设计 —— 题目二

## 项目简介

基于 **MySQL + Streamlit** 的学生成绩管理系统，支持三种角色登录，提供 Web 和 CLI 双界面。

| 角色 | 功能 |
|------|------|
| **教务管理员** | 数据概览（含 Plotly 交互图表）、班级/学生/教师/课程/专业 CRUD、排课管理、选课管理、数据库备份恢复 |
| **教师** | 录入成绩（单个 / CSV 批量导入）、查看课程学生（含成绩分布饼图、排行柱状图） |
| **学生** | 选课/退选、查看各科成绩（含成绩柱状图）、学期均分、学籍分/绩点分 |

## 技术栈

- **语言**：Python 3.12
- **Web 框架**：Streamlit
- **数据库**：MySQL 8.0（InnoDB, utf8mb4）
- **驱动**：PyMySQL + SQLAlchemy（连接池）
- **图表**：Plotly Express
- **数据校验**：Pydantic
- **数据**：pandas, CSV

## 快速开始

### 1. 环境准备

```bash
pip install streamlit pymysql pandas plotly pydantic sqlalchemy python-dotenv
```

确保本地 MySQL 服务已启动（默认 127.0.0.1:3306，无密码 root）。

### 2. 初始化数据库

```bash
# 一键建库 + 导入 1000 学生仿真数据
python src/reset_data.py
```

或手动按顺序执行 `sql/` 目录下的 `.sql` 文件：

```
01_数据库创建.sql → 02_基础数据表.sql → 03_中间表.sql → 04_视图.sql → 06_触发器.sql → 07_存储过程.sql → 08_存储函数.sql
```

然后导入 CSV 数据：

```bash
python src/import_data.py
```

### 3. 启动应用

```bash
# Web 界面（推荐）
streamlit run src/app.py

# 命令行界面
python src/main.py
```

### 4. 登录

登录页提供 **快速选择** 下拉框，可直接选择测试账号（从 CSV 实时读取）：

- **管理员**：`admin`
- **教师**：如 `T20240001`（下拉选择）
- **学生**：如 `20220101`（下拉选择）

或手动输入工号/学号登录。

### 5. 重新生成数据（可选）

```bash
python data/generate_data.py   # 生成新数据
python src/reset_data.py       # 重建数据库并导入
```

## 数据库设计

- **数据库名**：`db_sms`
- **字符集**：`utf8mb4` / `utf8mb4_unicode_ci`
- **存储引擎**：`InnoDB`
- **设计规范**：全表逻辑删除（`is_deleted`），`status` 与 `is_deleted` 职责分离

### 核心表

| 表 | 说明 |
|----|------|
| `class` | 班级（含年级、专业、状态） |
| `student` | 学生（N:1 班级，含学籍分/绩点分，触发器维护） |
| `teacher` | 教师（含工号、职称、电话、状态） |
| `course` | 课程（含学分） |
| `course_offering` | 排课（关联课程/教师/学期/时间/容量，含触发器维护人数） |
| `enrollment` | 选课（学生 N:M 排课，含成绩，触发器自动计算 GPA） |
| `teacher_course` | 教师可授课程（讲授资格） |
| `grade_point_rule` | 分数→绩点转换规则 |

### 数据库对象

| 类型 | 数量 | 说明 |
|------|------|------|
| 视图 | 3 | v_student_message, v_course_plan, v_enrollment |
| 触发器 | 5 | 选课名额检查、人数维护、成绩变化自动计算 |
| 存储过程 | 9 | 选课、退选、成绩录入、各类统计报表 |
| 存储函数 | 2 | 学号→ID, 工号→ID |

## 项目结构

```
├── src/                    # Python 源码
│   ├── app.py              # Streamlit Web 入口（22 个页面）
│   ├── main.py             # CLI 入口
│   ├── admin.py            # 教务功能（CRUD + 统计查询）
│   ├── student_tui.py      # 学生功能（CLI）
│   ├── teacher_tui.py      # 教师功能（CLI）
│   ├── tester.py           # 测试员跳板
│   ├── import_data.py      # CSV 数据导入
│   ├── reset_data.py       # 一键重建数据库
│   ├── pages/              # Streamlit 页面模块
│   │   ├── admin_page.py   # 教务 14 页面（含 Plotly 图表）
│   │   ├── student.py      # 学生 5 页面
│   │   └── teacher.py      # 教师 3 页面
│   └── core/
│       ├── config.py       # 数据库连接池（SQLAlchemy QueuePool）
│       ├── auth.py         # 登录认证
│       ├── models.py       # Pydantic 输入校验模型
│       ├── majors.py       # 专业列表管理
│       └── utils.py        # 工具函数
├── sql/                    # 数据库 DDL/DML（7 个文件）
├── data/                   # CSV 数据
│   ├── generate_data.py    # 仿真数据生成器
│   ├── majors.csv          # 专业列表（26 个专业）
│   └── *.csv               # 8 张表的初始化数据
├── backup/                 # 数据库备份（mysqldump）
├── document/               # 课程设计文档、报告
├── images/                 # ER 图等图片
└── archive/                # 历史参考文件
```

## 特色功能

| 功能 | 说明 |
|------|------|
| 🎨 **交互式图表** | 数据概览、成绩分布、教师排行等使用 Plotly 图表 |
| 📊 **学籍分/绩点分布** | 饼图展示优秀/良好/中等/及格/不及格占比 |
| 📈 **成绩排行** | 柱状图展示学生排名，颜色渐变直观反映水平 |
| ✅ **输入校验** | Pydantic 模型统一校验 + `max_chars` 前端截断 |
| 🔑 **快速选择登录** | 下拉选择测试账号，自动填充 |
| 📋 **CSV 批量录入** | 教师可上传 CSV 批量导入成绩 |
| 🏫 **专业管理** | 专业列表 CSV 存储，支持增删，班级管理联动 |
| 🔄 **触发器自动计算** | 成绩变化后自动重算学籍分/GPA |
| 📁 **数据生成器** | `generate_data.py` 一键生成 1000 学生仿真数据 |

## 测试数据规模

| 实体 | 数量 |
|------|------|
| 班级 | 24 |
| 学生 | 1000 |
| 课程 | 18 |
| 教师 | 25 |
| 排课 | 约 54 |
| 选课记录 | 约 3000（~25% 未录入成绩） |

## 配置

### 数据库配置

数据库连接支持 `.env` 文件配置（复制 `.env.example` 修改）：

```env
DB_HOST=127.0.0.1
DB_PORT=3306
DB_USER=root
DB_PASSWORD=
DB_NAME=db_sms
```

或在 `src/core/config.py` 中直接修改默认值。
