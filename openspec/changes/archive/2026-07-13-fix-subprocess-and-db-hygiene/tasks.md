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
