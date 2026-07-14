## Context

上一轮已通过 `core/models.py` 添加了 Pydantic 输入校验，用户输入错误后会通过 `st.toast` 收到错误提示。但 toast 在输入之后才出现，用户更希望在输入前就知道规则。

## Goals / Non-Goals

**Goals:**
- 为所有 `st.text_input` 添加 `placeholder`（示例值）和 `help`（格式说明）
- 提示文字与 `core/models.py` 中 Field 的约束完全一致
- 不改任何业务逻辑

**Non-Goals:**
- 不改 `st.selectbox` / `st.number_input`（已有控件级提示）
- 不改 CLI 脚本
- 不更改校验逻辑

## Decisions

### 1. placeholder 放示例值，help 放规则说明

- `placeholder`：具体示例值，如 "20240001"
- `help`：规则一句话，如 "学号为 8-12 位纯数字，不可包含字母或符号"

### 2. 规则文本直接从 models.py 字段约束翻译

| 字段 | pattern / 约束 | placeholder | help |
|------|---------------|-------------|------|
| StudentCreate.no | `^\d{8,12}$` | "20240001" | 学号为 8-12 位纯数字 |
| TeacherCreate.no | `^\d{5,20}$` | "10001" | 工号为 5-20 位数字 |
| TeacherCreate.phone | `^\d{7,15}$` | "13800138000" | 电话为 7-15 位纯数字 |
| ClassCreate.grade | `^\d{4}$` | "2024" | 年级为 4 位年份 |
| SemesterQuery.semester | `^\d{4}-\d{4}-\d+$` | "2024-2025-1" | 格式如：2024-2025-1 |

## Risks / Trade-offs

- **[同步风险]** 如果日后修改 models.py 字段约束，忘记同步更新这里的提示文字 → 无自动化检查，靠 code review 保证
