# fix-subprocess-and-db-hygiene

> 合并自 `proposal.md` · `design.md` · `tasks.md`

---

# 📋 proposal.md

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

---

# 🏗️ design.md

## Context

当前系统通过 Streamlit 页面提供数据库备份（mysqldump）和恢复（mysql）功能，所有 CRUD 操作通过 pymysql 直连 MySQL。现有实现存在三类缺陷：

1. **子进程调用不可靠**：`restore_page` 用 `input=content` 向 mysql 传 SQL，Windows 管道缓冲区易死锁；备份/恢复命令未显式指定数据库名
2. **事务管理缺失**：所有 `except pymysql.Error` 分支无 `conn.rollback()`，失败后事务残留
3. **游标泄漏**：`cur = conn.cursor()` 未配对 `cur.close()`，长期运行会耗尽 MySQL 连接句柄

## Goals / Non-Goals

**Goals:**
- 恢复功能 100% 可靠：点击按钮后正常执行并返回结果
- 备份/恢复命令显式指定目标数据库 `db_sms`
- 所有 CRUD 异常分支执行 `conn.rollback()`
- 所有 CRUD 游标使用 `with conn.cursor() as cur:` 上下文管理器
- 编码容错：解码备份文件时 `errors="ignore"` 避免 `UnicodeDecodeError`

**Non-Goals:**
- 不添加 MySQL 密码管理机制（当前环境 root 无密码，密码问题由 `core/config.py` 统一管理）
- 不修改 TUI 终端版本（`admin.py` 中的 `restore`/`backup` 函数）—— 仅修复 Streamlit 端
- 不改变现有 CRUD 业务逻辑

## Decisions

### 1. 恢复：临时文件 + 文件流 stdin（替代 `input=` 管道）

**选择**：SQL 内容写入临时文件 → `open(path, "r")` 作为 `stdin` → `subprocess.run` 执行 → 清理临时文件

**替代方案**：
- `input=content`（当前做法）：Windows 管道缓冲区 ~64KB，129KB+ 的 SQL 会导致子进程写 stdout/stderr 填满缓冲区 → 死锁。**放弃**。
- `shell=True` 重定向：`mysql < file.sql` 简洁，但引入 shell 注入风险。**放弃**。
- `subprocess.Popen` + `communicate()`：理论上能处理 I/O 并发，但实测在 Windows 上仍有概率阻塞。**放弃**。

**理由**：文件流方式避免了 Python 进程内同时持有完整 SQL 字符串，`stdin` 由操作系统按块读取，无缓冲区死锁风险。

### 2. 命令补全目标数据库名 `db_sms`

**选择**：`mysql ... db_sms`（数据库名作为 mysql CLI 最后一个位置参数）

**理由**：mysqldump 备份使用 `--databases db_sms`，SQL 文件中包含 `CREATE DATABASE` 但不一定包含 `USE db_sms`。显式指定目标数据库确保导入不会因 `No database selected` 失败。

### 3. 编码容错：`errors="ignore"`

**选择**：`.decode("utf-8", errors="ignore")` 而非严格 decode

**理由**：Windows 环境下 mysqldump 输出可能混入 GBK/CP936 字符。`errors="ignore"` 跳过无法解码的字节，比直接崩溃更合理。丢失的字节通常是注释中的中文字符，不影响 SQL 执行。

### 4. 事务回滚：`conn.rollback()` 在 `except pymysql.Error` 中

**选择**：每个 `except pymysql.Error` 分支首行添加 `conn.rollback()`

**理由**：pymysql `autocommit=False` 时（默认），失败的 DML 会在连接上残留未提交事务，后续操作可能看到脏数据或遭遇锁等待。`rollback()` 确保干净状态。

### 5. 游标管理：统一 `with conn.cursor() as cur:`

**选择**：所有手动 `cur = conn.cursor()` 改为 `with conn.cursor() as cur:` 上下文管理器

**理由**：`with` 块退出时自动调用 `cur.close()`，无泄漏。对 `SELECT` 无副作用；对 `INSERT`/`UPDATE`/`DELETE`，`commit()` 仍在 `with` 块外调用（游标关闭不影响已提交事务）。当前 Streamlit 端 `admin_page.py` 中约 12 处需修改。

## Risks / Trade-offs

- [临时文件残留] → `finally` 块 `os.unlink()` 确保清理；进程崩溃时残留于系统 TEMP 目录，重启后自动回收
- [`errors="ignore"` 可能丢失数据] → 仅跳过多字节序列中无法解码的孤立字节，不影响 ASCII SQL 关键字；风险极低
- [`conn.rollback()` 在游标已关闭时] → 不影响，`rollback()` 是连接级别操作，与游标生命周期无关

---

# ✅ tasks.md

## 1. 恢复功能修复 (Streamlit)

- [x] 1.1 重写 `restore_page`：改用临时文件 + `stdin` 文件流替代 `input=content` 管道
- [x] 1.2 mysql 命令末尾添加目标数据库名 `db_sms`
- [x] 1.3 SQL 解码使用多重回退策略（UTF-8 → GBK → errors="ignore"）
- [x] 1.4 finally 块中 `os.unlink()` 确保临时文件清理
- [x] 1.5 预留 `-p` 密码参数注释位置
- [x] 1.6 执行前 `_conn.commit()` 释放事务锁，防止 DDL 死锁
- [x] 1.7 合并 stdout/stderr 错误信息，防止错误被静默吞掉

## 2. 备份功能加固 (Streamlit)

- [x] 2.1 `backup_page` 确认 `--databases db_sms` 已显式指定
- [x] 2.2 补充 `FileNotFoundError` 和通用 `Exception` 异常处理
- [x] 2.3 预留 `-p` 密码参数注释位置

## 3. 事务回滚 (TUI + Streamlit)

- [x] 3.1 `src/admin.py` 所有 `except pymysql.Error` 分支（11 处）添加 `conn.rollback()`
- [x] 3.2 `src/pages/admin_page.py` 所有 `except pymysql.Error` 分支（16 处）添加 `conn.rollback()`

## 4. 游标管理 (Streamlit)

- [x] 4.1 `src/pages/admin_page.py` 中 17 处 `cur = conn.cursor()` 全部改为 `with conn.cursor() as cur:` 上下文管理器

## 5. 验证

- [x] 5.1 Python 语法检查通过
- [x] 5.2 模块导入成功
- [x] 5.3 零残留 `cur = conn.cursor()`
- [x] 5.4 恢复功能实测：上传备份文件 → 点击恢复 → 显示"恢复成功"
