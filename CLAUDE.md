# CLAUDE.md

## 项目概况

- **课程**：数据库系统课程设计
- **选题**：题目二 —— 学生成绩管理系统
- **数据库名**：`db_sms`（Student Management System）
- **当前阶段**：逻辑结构设计（建表分析中）
- **分析文档**：`docs/notes/建表分析.md`
- **优化建议**：`docs/notes/建表分析优化建议.md`

## 设计规范

- 表名：全小写 + 下划线，如 `student_course`
- 字符集：`utf8mb4`，排序规则：`utf8mb4_unicode_ci`
- 存储引擎：`InnoDB`
- 全部采用逻辑删除（`is_deleted` 字段）
- `status` 管业务状态，`is_deleted` 管数据状态，两者分开

## 关键决策

- 学生与班级：1:N，学生表加 `class_id` 外键，不建中间表
- 学生与课程：M:N，通过选课中间表实现
- VS Code SQL 文件不自动格式化（`.vscode/settings.json` 已配置）

## 版本管理

- 旧版本文件存入 `archive/` 文件夹
- 开发日志：`docs/开发日志.md`
- 问答日志：`docs/日志.md`
- AI 修正日志：`docs/AI修正日志.md`

## 历史参考

- 题目一（进销存）的完整设计，已放弃但保留作为学习参考
