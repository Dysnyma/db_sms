## Why

项目目录结构存在中英混用、命名风格不一致（大小写混用、单复数混用）、嵌套冗余等问题，影响代码可维护性和项目专业度。需要在当前阶段统一规范，避免后续累积更多混乱。

## What Changes

- **BREAKING**: `SQL/` → `sql/`（全小写，与其他目录统一）
- **BREAKING**: `code/` → `src/`（业界通用命名）
- **BREAKING**: `document/` 目录重构：
  - `document/上交/` → `document/submission/`
  - `document/报告/` → `document/report/`
  - `document/开发记录/` → 内容合并到 `document/` 根下
  - `document/notes/notes/` → `document/notes/`（消除冗余嵌套）
- `images/` → 移入 `document/images/`（该目录仅含报告用图片）
- `.gitignore` 补充 `venv/`
- `CLAUDE.md` 中的路径引用同步更新

## Capabilities

### New Capabilities

- `project-directory-conventions`: 定义统一的目录命名规范（全小写 + 下划线/连字符），作为后续开发的结构约定

### Modified Capabilities

<!-- 无现有 spec 需要修改 -->

## Impact

- 所有 `code/` 和 `SQL/` 下的 import / 路径引用需同步更新
- `CLAUDE.md` 中的目录说明需更新
- `README.md` 中的项目结构说明需更新
- `code/core/config.py` 中如有路径引用需更新
- `code/reset_data.py` 中 SQL 目录路径需更新
- Streamlit 入口 `code/app.py`（将成为 `src/app.py`）无需内部改动
