## Why

学生选课/退选页面提交操作后，表格数据未能实时反映最新状态 —— 旧的选课记录仍在列表中，新选的课程没有出现。原因是 Streamlit 自上而下的执行顺序：数据查询在按钮事件处理之前完成，导致 UI 永远比数据库"慢半拍"。需要修复以确保用户操作后立即看到最新数据。

## What Changes

- **enroll_page 重写**：操作成功后调用 `st.rerun()` 强制重新渲染，通过 `st.session_state.msg` 跨渲染传递消息
- **unenroll_page 重写**：同上，操作成功后调用 `st.rerun()` + `st.session_state.msg`
- **事务安全**：所有 `except pymysql.Error` 分支添加 `conn.rollback()`（选课/退选）
- **游标管理**：使用 `with conn.cursor() as cur:` 上下文管理代替手动 `cur = conn.cursor()`

## Capabilities

### New Capabilities

- `student-page-realtime`: 学生选课/退选页面实时更新 —— 操作后 `st.rerun()` 强制刷新，`st.session_state.msg` 跨渲染持久化提示消息

### Modified Capabilities

<!-- No existing specs to modify -->

## Impact

- `src/pages/student.py` — `enroll_page` 和 `unenroll_page` 重写，引入 `st.session_state.msg` + `st.rerun()` 模式；所有 CRUD 添加 `conn.rollback()` 和 `with conn.cursor() as cur:`
