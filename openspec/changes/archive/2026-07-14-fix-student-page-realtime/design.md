## Context

学生选课页面 (`enroll_page`) 和退选页面 (`unenroll_page`) 在 `src/pages/student.py` 中实现。现有流程是：

1. 页面加载时调用 `show_courses()` / `enrolled_courses()` 查询数据
2. Streamlit 渲染表格
3. 用户选择排课并点击按钮
4. 调用存储过程执行选课/退选，`conn.commit()`，打印成功消息

问题在于 Streamlit 每次用户交互都会**从头重新执行脚本**。步骤 4 的数据库更新发生在页面渲染之后 —— 因此用户看到的表格永远是旧数据。即使用了 `st.rerun()`，如果成功消息不跨渲染持久化，也会被刷掉。

## Goals / Non-Goals

**Goals:**
- 选课/退选操作后表格立即反映最新数据库状态
- 操作成功/失败的消息在 `st.rerun()` 后仍然可见
- 异常时正确回滚事务
- 游标使用 `with` 上下文管理器自动管理

**Non-Goals:**
- 不修改 `show_courses`、`enrolled_courses` 等查询函数（它们只负责查询，逻辑正确）
- 不修改 Streamlit 页面导航或架构
- 不覆盖已完成的 `conn.rollback()` / 游标管理改动

## Decisions

### 1. `st.session_state.msg` 跨渲染消息传递

**选择**：使用 `st.session_state.msg = (type, text)` 存储操作结果，在页面顶部拦截并显示。

**替代方案**：
- `st.success()` 直接打印 → `st.rerun()` 会清空。**放弃**。
- `st.toast()` → Streamlit 中不可靠，用户可能看不到。**放弃**。
- `st.cache` → 设计用于计算结果缓存，不适合消息传递。**放弃**。

**理由**：`st.session_state` 是 Streamlit 官方推荐的跨渲染状态持久化方式，`pop()` 读取后自动清除，不会堆积。

### 2. `conn.commit()` 后立即 `st.rerun()`

**选择**：事务提交成功后调用 `st.rerun()`。

**理由**：`st.rerun()` 强制 Streamlit 从顶部重新执行页面，此时数据库已包含最新数据，渲染出的表格自然是最新的。失败时也调用 `st.rerun()` 并在 `session_state` 中携带错误消息以保证一致的 UX。

### 3. 消息显示在查询渲染之前

**选择**：在页面函数顶部、查询语句之前读取并显示 `session_state.msg`。

**理由**：如果消息显示在表格后面，用户需要滚动才能看到。放在顶部符合 F 形阅读模式，用户操作后第一眼就能看到结果。

## Risks / Trade-offs

- [`st.rerun()` 循环风险] → 只在按钮事件中调用，按钮事件不会自动再次触发（Streamlit 保证按钮点击状态不会跨 rerun 传递），无无限循环可能
- [消息覆盖] → 如果用户快速连续操作两次，后一次的消息会覆盖前一次。`pop()` 确保每次只显示最新一条，是可接受的行为
- [`session_state.msg` 未初始化] → 首次访问时 `get("msg")` 返回 None，跳过消息显示块，安全
