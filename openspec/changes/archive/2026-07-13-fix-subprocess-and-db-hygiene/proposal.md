## Why

恢复功能完全不可用（点击按钮无反应），备份功能存在隐性鉴权失败风险，所有 CRUD 操作缺少事务回滚和游标关闭 —— 这三个问题叠加会导致数据操作不可靠、连接泄漏、以及子进程死锁。需要系统性修复，确保生产可用。

## What Changes

- **恢复功能重写**：改用临时文件 + `stdin` 文件流替代 `input=content` 管道传参，消除 Windows 管道死锁；补全目标数据库名 `db_sms`；解码失败时使用 `errors="ignore"` 容错
- **备份功能加固**：`mysqldump` 命令补全数据库名（已有 `--databases db_sms`），确保与恢复对称
- **事务安全**：所有 `except pymysql.Error` 分支添加 `conn.rollback()`，防止事务残留和锁未释放
- **游标管理**：所有 CRUD 函数中 `cur = conn.cursor()` 改为 `with conn.cursor() as cur:` 上下文管理器，杜绝游标泄漏

## Capabilities

### New Capabilities

- `db-restore`: 可靠的数据库恢复 —— 临时文件 + mysql CLI，管道不死锁，编码容错，明确指定目标数据库
- `db-backup`: 可靠的数据库备份 —— mysqldump CLI 显式指定数据库名，输出到 backup/ 目录
- `db-transaction-safety`: 事务安全与游标管理 —— 异常时回滚事务，游标通过 `with` 自动关闭

### Modified Capabilities

<!-- No existing specs to modify -->

## Impact

- `src/pages/admin_page.py` — `restore_page` 函数重写，`backup_page` 加固
- `src/admin.py` — 所有 `except pymysql.Error` 添加 `conn.rollback()`（TUI 端 CRUD）
- `src/pages/admin_page.py` — 所有 Streamlit 端 CRUD 添加 `conn.rollback()` 且游标改为 `with` 写法
