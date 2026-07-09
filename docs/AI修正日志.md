# AI 修正日志

| 时间 | AI 错误 | 人工修正 |
|------|---------|----------|
| 2026-07-07 08:45:00 | course_offering 多加了 effective_time 字段，与 enroll_start_time 重复 | 删掉 |
| 2026-07-07 08:52:00 | enrollment 表同时有 enroll_time 和 create_time | 删掉 enroll_time |
| 2026-07-07 09:57:28 | 01_数据库创建.sql 错写为 db_purchase_sales_inventory | 改为 db_student_management_system |
| 2026-07-07 10:21:33 | 说 IN 关键字必须写 | 用户指出 MySQL 可省略 |
| 2026-07-07 10:21:33 | sed 替换时损坏存储过程名 | 手动逐条修复 |
| 2026-07-07 15:10:12 | tester.py 重复定义函数 | 改为 import 引用 |
| 2026-07-07 15:10:12 | 多次忘记更新日志 | 用户提醒后补全 |
| 2026-07-08 00:03:30 | sed 把 admin.py 覆盖为 teacher.py 内容 | 重新写入完整 admin.py |
| 2026-07-08 00:03:30 | subprocess.run 卡死 | 加 --batch + timeout |
| 2026-07-08 00:03:30 | import os 放在函数内部致 restore 报错 | 移到文件顶部 |
| 2026-07-09 | 教师管理新增后清除 ca_name 等班级 key（复制粘贴） | 改为 ta_name/ta_no/ta_title/ta_phone |
| 2026-07-09 | 学生管理新增后清除 coa_name 等课程 key（复制粘贴） | 改为 sa_name/sa_no/sa_class |
| 2026-07-09 | 排课管理删除末尾双重 st.rerun() | 删除多余的死代码 |
| 2026-07-09 | grade_input / batch_grade / enrollment 用 st.success+rerun 导致消息丢失 | 统一改为 session_state.msg 模式 |
| 2026-07-09 | enrollment_manage 字典构建两次 | 提取为 emap 变量 |
| 2026-07-09 | 排课管理新增用 selectbox 下拉 + number_input 带初始值，风格突兀 | 改为纯 text_input，校验移入按钮逻辑 |
| 2026-07-09 | teacher_course_teachers 导入未使用 | 移除 |
| 2026-07-09 | class_report/grade_roster 字典构建两次 + format_func 冗余 + 函数内 import | 字典去重/去冗余/import 移顶 |
| 2026-07-09 | teacher_info_page 6个 metric 挤 4 列，c1/c2 覆盖导致工号+姓名丢失 | 改为两行 3 列 |
