## Context

Streamlit 中两种通知方式：
- `st.toast()`：浮动通知，数秒后自动消失，适合低优先级提醒
- `st.success()`：内联绿色消息框，持续显示直到下次 rerun，适合操作结果反馈

当前代码在 import 类页面使用 `st.toast()` 展示操作结果，对需要查看具体条数的场景不够友好。

## Goals / Non-Goals

**Goals:**
- 批量导入和单条导入的完成提示转为持久显示的 `st.success()`
- 对应错误场景的提示同步转为持久显示的 `st.error()`
- 切换页面后旧提示不再残留

**Non-Goals:**
- 不改动其他管理页面的 `st.toast()` — 其他页面（班级/课程/教师管理等）的 toast 用于快捷操作反馈，自动消失更合适
- 不改动 `teacher.py` 的命令行版本 — 终端用户无此问题

## Decisions

| 决策 | 选择 | 理由 |
|------|------|------|
| 替换页面范围 | `batch_grade_page` + `grade_input_page` | 录入成绩是用户最需要看清结果数字的场景 |
| 替换方式 | `st.toast()` → `st.success()`，`st.error()` | 保持 `_ , m = st.session_state.pop("msg")` 不变，仅改展示函数 |
| 消息残留 | 切换页面后自动清除 | `session_state.pop("msg")` 每次页面加载时消费并移除，不会跨页面残留 |
| 错误提示 | 同步改为 `st.error()` | 导入失败时用户更需要看清报错原因 |

## Risks / Trade-offs

- **[低风险]** 改为 `st.success()` 后，消息会持续到下次 rerun。如果用户重复导入，旧结果会被新结果覆盖，符合预期。
