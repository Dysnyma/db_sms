# 人工修正 AI 日志

> 记录 AI 给出错误/多余建议，以及人工纠正的过程

| 时间 | AI 错误 | 人工修正 |
|------|---------|----------|
| 2026-07-07 08:45:00 | `course_offering` 多加了一个 `effective_time` 字段，与 `enroll_start_time` 重复 | 删掉，两者是同一个概念 |
| 2026-07-07 08:52:00 | `enrollment` 表同时有 `enroll_time` 和 `create_time`，两者重复 | 删掉 `enroll_time`，`create_time` 就是选课时间 |
| 2026-07-07 09:57:28 | 01_数据库创建.sql 写错了数据库全称 `db_purchase_sales_inventory` | 改为 `db_student_management_system` |
| 2026-07-07 10:21:33 | 说 `IN` 关键字必须写 | 用户指出 MySQL 可省略 IN，我认错 |
| 2026-07-07 15:10:12 | 多次忘记更新日志 | 用户提醒后补全 |
| 2026-07-07 15:10:12 | sed 替换 `_show_courses` 时把存储过程名 `sp_show_courses` 也改成了 `spshow_courses` | 手动逐条修复所有存储过程名称 |
| 2026-07-07 15:10:12 | tester.py 把 student/teacher/admin 的函数重新定义了一遍，代码大量重复 | 公开原函数，tester 用 import 引用 |
| 2026-07-08 | `sp_enroll` 未检查「同一门课不能选两个老师」，学生可以对同一课程选不同老师的班 | 新增第 4 步校验：JOIN `course_offering` 查 `course_id`，已选过同课程任意排课则拒绝 |
