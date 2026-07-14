## ADDED Requirements

### Requirement: 事务异常回滚
系统 SHALL 在捕获 `pymysql.Error` 时调用 `conn.rollback()`，确保失败的事务不残留于数据库连接。

#### Scenario: INSERT 操作失败后回滚
- **WHEN** `cur.execute("INSERT INTO ...")` 抛出 `pymysql.Error`
- **THEN** 系统调用 `conn.rollback()` 撤销未完成的事务，然后显示错误信息

#### Scenario: UPDATE 操作失败后回滚
- **WHEN** `cur.execute("UPDATE ... SET ...")` 抛出 `pymysql.Error`
- **THEN** 系统调用 `conn.rollback()` 撤销未完成的事务，然后显示错误信息

#### Scenario: DELETE 操作失败后回滚
- **WHEN** `cur.execute("UPDATE ... SET is_deleted=1 ...")` 抛出 `pymysql.Error`
- **THEN** 系统调用 `conn.rollback()` 撤销未完成的事务，然后显示错误信息

### Requirement: 游标生命周期管理
系统 SHALL 使用 `with conn.cursor() as cur:` 上下文管理器管理所有数据库游标，确保游标在退出作用域时自动关闭。

#### Scenario: SELECT 游标自动关闭
- **WHEN** `with conn.cursor() as cur:` 代码块执行完毕（包括正常返回和异常退出）
- **THEN** 游标的 `close()` 方法被自动调用，释放 MySQL 游标资源

#### Scenario: INSERT/UPDATE/DELETE 游标自动关闭
- **WHEN** `with conn.cursor() as cur:` 代码块内执行 DML 语句后 `conn.commit()` 在块外调用
- **THEN** 游标在 `with` 块退出时关闭，已提交的事务不受影响
