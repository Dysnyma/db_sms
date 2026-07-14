## Why

当前项目所有表单输入（姓名、学号、工号、电话、学期等）直接经 `st.text_input` 进入 SQL 或存储过程，没有任何格式校验。格式错误（如学号含字母、学期格式不对、电话长度不对）只有落到数据库层才会被发现，甚至静默写入脏数据。引入 Pydantic 可以低成本约束所有纯文本输入，提前在 UI 层拦截错误。

## What Changes

- 新增文件 `src/core/models.py`，用 Pydantic 定义所有表单输入 model
- 新增统一验证辅助函数 `validate_or_error()`，自动在 Streamlit 上 toast 错误消息
- 在 `pages/admin_page.py` 的各个 CRUD 表单 `st.button` 入口处插入验证
- 在 `pages/student.py` 的学期查询入口处插入验证
- 安装 `pydantic` 依赖

不改动：
- `number_input` / `selectbox`（已由 Streamlit 保证类型安全）
- CLI 脚本（`student_tui.py` / `teacher_tui.py`，走 `input()`）
- `import_data.py`（CSV 导入）
- 数据库层、认证层、工具函数

## Capabilities

### New Capabilities
- `input-validation`: 基于 Pydantic 的 Streamlit 表单输入校验，覆盖 admin 页面的学生/教师/班级/课程 CRUD 及学生页面的学期查询

### Modified Capabilities

（无）

## Impact

- **新依赖**: `pydantic`
- **新增文件**: `src/core/models.py`（~70 行 model 定义 + 辅助函数）
- **修改文件**:
  - `src/pages/admin_page.py`（约 +20 行，import + 每个 button 入口加验证）
  - `src/pages/student.py`（约 +3 行，学期查询加验证）
- **零重构**：不改现有业务逻辑，验证只增加一层前置守卫
