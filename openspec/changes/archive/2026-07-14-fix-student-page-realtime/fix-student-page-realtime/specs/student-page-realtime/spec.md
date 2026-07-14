## ADDED Requirements

### Requirement: 选课操作后页面实时更新
系统 SHALL 在学生完成选课操作后，通过 `st.rerun()` 强制刷新页面，使表格立即反映最新数据，并通过 `st.session_state.msg` 显示操作结果消息。

#### Scenario: 正常选课成功
- **WHEN** 学生选择排课后点击"确认选课"按钮，存储过程执行成功且 `conn.commit()` 完成
- **THEN** 调用 `st.rerun()`，页面重新渲染后表格不包含刚选的课程，并在页面顶部显示"选课成功！"

#### Scenario: 选课失败（存储过程异常）
- **WHEN** 存储过程抛出 `pymysql.Error`
- **THEN** 调用 `conn.rollback()` 回滚事务，`st.session_state.msg` 存入错误类型消息，`st.rerun()` 后页面顶部显示错误信息

#### Scenario: 选课后表格数据一致性
- **WHEN** 选课成功且 `st.rerun()` 完成
- **THEN** 表格查询结果与数据库中剩余可选课程完全一致

### Requirement: 退选操作后页面实时更新
系统 SHALL 在学生完成退选操作后，通过 `st.rerun()` 强制刷新页面，使表格立即反映最新数据，并通过 `st.session_state.msg` 显示操作结果消息。

#### Scenario: 正常退选成功
- **WHEN** 学生选择已选排课后点击"确认退选"按钮，存储过程执行成功且 `conn.commit()` 完成
- **THEN** 调用 `st.rerun()`，页面重新渲染后表格不包含已退选的课程，并在页面顶部显示"退选成功！"

#### Scenario: 退选失败（存储过程异常）
- **WHEN** 存储过程抛出 `pymysql.Error`
- **THEN** 调用 `conn.rollback()` 回滚事务，`st.session_state.msg` 存入错误类型消息，`st.rerun()` 后页面顶部显示错误信息

#### Scenario: 连续操作消息更新
- **WHEN** 学生连续进行两次选课/退选操作
- **THEN** 每次操作后 `st.session_state.msg` 被 pop 后重新写入，仅显示最新一次操作的结果消息
