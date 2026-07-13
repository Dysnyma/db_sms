## 1. 准备工作

- [x] 1.1 `.gitignore` 添加 `venv/`
- [x] 1.2 确认 `code/reset_data.py` 中 SQL 路径已是 `sql/`（小写），无需修改

## 2. 目录重命名

- [x] 2.1 `git mv SQL/ sql/`（Git 中已是小写，跳过）
- [x] 2.2 `git mv code/ src/`
- [x] 2.3 `document/上交/` → `document/submission/`（已在 .gitignore 中，跳过）
- [x] 2.4 `document/报告/` → `document/report/`
- [x] 2.5 `document/报告/版本/` → `document/report/versions/`
- [x] 2.6 `document/开发记录/` → `document/dev-log/`
- [x] 2.7 消除 `document/notes/notes/` 冗余嵌套（内容上提到 `document/notes/`）
- [x] 2.8 `git mv images/ document/images/`（根 images 归入文档）

## 3. 更新路径引用

- [x] 3.1 更新 `code/import_data.py` 注释中的 `SQL/` → `sql/`
- [x] 3.2 更新 `README.md` 中所有 `SQL/`、`code/` 引用
- [x] 3.3 更新 `document/report/code/` 下报告生成脚本中的路径引用
- [x] 3.4 更新 `document/dev-log/开发日志.md` 中的路径引用
- [x] 3.5 更新 `document/report/versions/` 中说明书 md 的路径引用

## 4. 更新文档

- [x] 4.1 更新 `CLAUDE.md` 中的目录说明
- [x] 4.2 更新 `README.md` 中的项目结构图

## 5. 验证与提交

- [x] 5.1 确认 `src/reset_data.py` 仍可正常运行
- [x] 5.2 `git status` 确认所有重命名被追踪
- [x] 5.3 提交并推送
