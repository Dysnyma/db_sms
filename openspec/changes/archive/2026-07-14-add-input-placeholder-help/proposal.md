## Why

当前所有 `st.text_input` 没有 `placeholder` 和 `help` 提示，用户只能靠 label 猜测输入格式，容易填错后被 Pydantic toast 拦截 — 体验不好。加上 inline 提示可以让用户 **在输入前就知道规则**，减少试错。

## What Changes

- 为 `admin_page.py` 中所有 `st.text_input` 添加 `placeholder` 和 `help` 参数
- 为 `student.py` 中的学期输入添加 `placeholder` 和 `help` 参数
- 提示文字与 `core/models.py` 中 Field 的约束（pattern / min_length / max_length）保持一致
- 不改动任何业务逻辑、校验逻辑、控件类型

## Capabilities

### New Capabilities
- `input-placeholder`: 为所有 Streamlit 文本输入框添加 placeholder 和 help 提示，与验证规则对齐

### Modified Capabilities

（无）

## Impact

- **修改文件**: `src/pages/admin_page.py`（约 22 个 `st.text_input` 加参数）、`src/pages/student.py`（1 个加参数）
- **零逻辑变更**：仅 UI 提示层改动，不影响任何功能
