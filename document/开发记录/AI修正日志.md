# 人工修正 AI 日志

> 记录 AI 给出错误/多余建议，以及人工纠正的过程

| 时间                | AI 错误                                                                                  | 人工修正                                                                                   |
| ------------------- | ---------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------ |
| 2026-07-07 08:45:00 | `course_offering` 多加了一个 `effective_time` 字段，与 `enroll_start_time` 重复          | 删掉，两者是同一个概念                                                                     |
| 2026-07-07 08:52:00 | `enrollment` 表同时有 `enroll_time` 和 `create_time`，两者重复                           | 删掉 `enroll_time`，`create_time` 就是选课时间                                             |
| 2026-07-07 09:57:28 | 01_数据库创建.sql 写错了数据库全称 `db_purchase_sales_inventory`                         | 改为 `db_student_management_system`                                                        |
| 2026-07-07 10:21:33 | 说 `IN` 关键字必须写                                                                     | 用户指出 MySQL 可省略 IN，我认错                                                           |
| 2026-07-07 15:10:12 | 多次忘记更新日志                                                                         | 用户提醒后补全                                                                             |
| 2026-07-07 15:10:12 | sed 替换 `_show_courses` 时把存储过程名 `sp_show_courses` 也改成了 `spshow_courses`      | 手动逐条修复所有存储过程名称                                                               |
| 2026-07-07 15:10:12 | tester.py 把 student/teacher/admin 的函数重新定义了一遍，代码大量重复                    | 公开原函数，tester 用 import 引用                                                          |
| 2026-07-08          | `sp_enroll` 未检查「同一门课不能选两个老师」，学生可以对同一课程选不同老师的班           | 新增第 4 步校验：JOIN `course_offering` 查 `course_id`，已选过同课程任意排课则拒绝         |
| 2026-07-08          | `sp_show_courses` 同上，查可选课时仍会显示已选同课的其他教师                             | 新增 `course_id NOT IN` 子查询，排除已选过的课程 ID                                        |
| 2026-07-08          | MySQL 8.0 连接默认 `utf8mb4_0900_ai_ci` 与数据库 `utf8mb4_unicode_ci` 冲突，报 1267 错误 | pymysql 连接加 `collation: 'utf8mb4_unicode_ci'`，fn 和 SP 的字符串比较加 `COLLATE` 双保险 |
| 2026-07-08          | tester.py 自建子菜单和 lambda 包装，代码 175 行且与 student/teacher/admin 重复           | 精简为 83 行跳板：S 换学生→调 student.menu，T 换教师→调 teacher.menu，A→调 admin.menu      |
| 2026-07-08          | `class_edit` 被 `class_delete` 覆盖丢失                                                  | 重新写回，顺便补上 `course_edit`                                                           |
| 2026-07-08          | `class_add` SQL 用 f-string 拼接，无引号会报错 + 注入风险                                | 改用 `%s` 占位符传参                                                                       |
| 2026-07-08          | 各 menu 数据太多一次全显示                                                               | 封装 Paginator 类，5 个管理菜单 + roster/teacher_list/my_grades/show_courses 全用分页      |
| 2026-07-08          | 教师录成绩要盲打排课 ID                                                                  | 改为两步分页：先选排课（带已选/上限）→ 循环录成绩，录完自动刷新列表                        |
| 2026-07-08          | ORDER BY course_name 不够                                                                | 改 `ORDER BY course_id, teacher_name`，同一门课排在一起                                    |
| 2026-07-08          | import 路径 `from core.` 在 streamlit 下找不到模块                                       | 全部改为 `from CLI.core.` 绝对路径                                                             |
| 2026-07-09 | 批量替换误伤 | 替换 `CLI.` → 空时同步改掉了日志中的 `CLI.` | 手动恢复日志中 3 处被误替换的 CL条目 |
| 2026-07-09 | `st.tabs` 渲染全部 tab 导致管理页面组件互相干扰 | 改用 `st.radio`，每次只渲染当前模式 |
| 2026-07-09 | `st.rerun()` 后 `st.success` 消息消失 | 改用 `st.toast` 弹窗，表单提交补回 `st.rerun()` |
| 2026-07-09 | 恢复用 `DROP DATABASE` 失败后数据库残废 | 改用 `SET FOREIGN_KEY_CHECKS=0` 包裹 SQL，不删库 |
| 2026-07-09 | 备份缺存储过程和触发器 | 加 `--routines --triggers --add-drop-table` |
| 2026-07-09 | `@st.cache_resource` 缓存连接超时报 `InterfaceError` | 回退，不缓存数据库连接 |
| 2026-07-08          | selectbox 用 lambda + next 遍历，代码又绕又慢                                            | 改用字典 `{label: id}` 映射，一行搞定                                                      |
| 2026-07-08          | my_grades/semester_avg 没有返回数据模式                                                  | 加 `paged` 参数，`paged=False` 返回原始数据供 Streamlit 用                                 |
