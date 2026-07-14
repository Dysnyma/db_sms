## ADDED Requirements

### Requirement: SQL 恢复操作必须有明确反馈

用户点击"确认恢复"后，无论成功或失败，页面必须显示对应的提示消息。

#### Scenario: 恢复成功
- **WHEN** mysql 命令执行成功且返回码为 0
- **THEN** 页面显示绿色 `st.success("恢复成功！请重启应用")`
- **AND** `_restore_sql_bytes` 从 session_state 中清除

#### Scenario: mysql 命令未找到
- **WHEN** mysql 可执行文件不在 PATH 中
- **THEN** 页面显示 `st.error("未找到 mysql 命令")`

#### Scenario: 恢复失败
- **WHEN** mysql 命令返回非零退出码
- **THEN** 页面显示 `st.error()` 包含 MySQL 的错误输出

## MODIFIED Requirements

（无。）

## REMOVED Requirements

（无。）
