## ADDED Requirements

### Requirement: 可靠的数据库备份
系统 SHALL 通过 mysqldump CLI 执行数据库备份，显式指定数据库名 `db_sms`，输出到 `backup/` 目录。

#### Scenario: 成功备份
- **WHEN** 管理员点击"备份数据库"按钮
- **THEN** 系统执行 `mysqldump -u root --databases db_sms --routines --triggers --add-drop-table --default-character-set=utf8mb4`，生成时间戳命名的 SQL 文件，显示"备份成功"及文件名

#### Scenario: mysqldump 命令不在 PATH 中
- **WHEN** 系统无法找到 mysqldump 可执行文件
- **THEN** 显示明确错误信息，提示用户检查 MySQL 安装和 PATH 配置

#### Scenario: mysqldump 执行失败
- **WHEN** mysqldump 返回非零退出码
- **THEN** 将 stderr 前 200 字符作为错误信息显示
