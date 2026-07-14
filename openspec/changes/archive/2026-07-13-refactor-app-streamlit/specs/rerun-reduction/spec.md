## ADDED Requirements

### Requirement: 减少不必要的 `st.rerun()`

当前管理页面在 CRUD 操作后广泛使用 `st.rerun()`，导致页面闪烁和用户输入丢失。「修改」模式下的 rerun 尤其影响体验 —— 用户刚编辑完一个字段，页面重刷后需要重新选择记录。

#### Scenario: 新增记录后不 rerun
- **WHEN** 用户在管理页面新增一条记录成功
- **THEN** 直接在当前页面流中显示 `st.success()`，不调用 `st.rerun()`
- **AND** 下次用户主动操作（切换模式、切换 tab）时自动刷新列表

#### Scenario: 删除记录后不 rerun
- **WHEN** 用户删除记录成功
- **THEN** 直接显示成功消息，不 rerun
- **AND** 数据列表应在下次用户切换到其他模式再切回来时刷新

#### Scenario: 保留 rerun 的必需场景

以下场景应保留 `st.rerun()`：

1. **登录/登出**（第 932、1009 行）：必须 rerun 以切换导航结构
2. **`grade_input_page` 录完成绩**（第 161 行）：需要 rerun 刷新学生成绩列表
3. **`course_manage_page` 新增**（第 476 行）：涉及「已删除课程恢复」逻辑，需确保最新状态
4. **`batch_grade_page` 已去除 rerun**（已验证可行）

#### Scenario: 消息传递方式调整

去除 `st.rerun()` 后，`st.session_state.msg` 模式不再需要。成功/错误消息直接在同一渲染周期内显示。

- **WHEN** 操作成功
- **THEN** 直接调用 `st.success(...)`，不经过 session_state 中转
- **AND** `st.session_state.pop("msg", None)` 相关的清理代码一并移除

### Requirement: 输入保留策略

去除不必要的 rerun 后，用户在「新增」模式下填写的表单应在操作后保持可见（而非重置为空），方便用户连续录入。

#### Scenario: 连续新增
- **WHEN** 用户新增一条记录成功后
- **THEN** 新增表单应保持展开状态，输入框不清空（当前通过手动 pop session_state 实现清空，应改为显式策略）
- **AND** 用户可再次填写并提交第二条记录

## MODIFIED Requirements

（无。）

## REMOVED Requirements

### Requirement: 管理页面的 st.session_state.msg 模式

**Reason**: 被直接渲染的 `st.success()` / `st.error()` 替代。去掉 rerun 后不再需要 session_state 在重渲染间传递消息。

**Migration**: 移除各管理页面顶部的 `if st.session_state.get("msg"): ..., _ = st.session_state.pop("msg"); st.toast(...)` 代码块。
