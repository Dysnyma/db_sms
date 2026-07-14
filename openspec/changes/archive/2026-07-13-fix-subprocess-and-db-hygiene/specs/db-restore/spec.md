## ADDED Requirements

### Requirement: 可靠的数据库恢复
系统 SHALL 通过临时文件 + mysql CLI 方式执行数据库恢复，避免管道死锁，并明确指定目标数据库。

#### Scenario: 上传 SQL 备份文件并成功恢复
- **WHEN** 管理员上传有效的 `db_sms` SQL 备份文件且点击"确认恢复"按钮
- **THEN** 系统将 SQL 内容写入临时文件，通过文件流 stdin 执行 `mysql -u root --default-character-set=utf8mb4 db_sms`，完成后显示"恢复成功"并清理临时文件

#### Scenario: 备份文件包含非 UTF-8 字节
- **WHEN** SQL 备份文件包含 GBK/CP936 编码字节
- **THEN** 系统以 `errors="ignore"` 解码，跳过无法解析的字节，继续执行恢复而不崩溃

#### Scenario: mysql 命令不在 PATH 中
- **WHEN** 系统无法找到 mysql 可执行文件
- **THEN** 显示明确错误信息，提示用户检查 MySQL 安装和 PATH 配置

#### Scenario: mysql 执行报错
- **WHEN** mysql 命令返回非零退出码
- **THEN** 显示 mysql 的 stderr 输出作为错误信息

#### Scenario: 恢复过程中发生异常
- **WHEN** 临时文件写入失败或其他非预期异常发生
- **THEN** 显示异常信息，且临时文件（如已创建）在 finally 块中被删除
