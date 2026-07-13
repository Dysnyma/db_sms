## Context

项目使用 `subprocess.run()` 在 3 个文件中调用外部命令（`mysqldump`、`mysql`），涉及数据库备份与恢复操作。当前实际代码已使用列表参数传递（`['mysqldump', '-u', 'root', ...]`），避免 `shell=True` 带来的命令注入风险，但未显式声明 `shell=False` 和 `check=False`，导致 Pylint W1510 告警。

## Goals / Non-Goals

**Goals:**
- 所有 `subprocess.run()` 调用添加 `shell=False` 显式声明
- 所有 `subprocess.run()` 调用添加 `check=False` 显式声明
- Pylint W1510 告警归零

**Non-Goals:**
- 不改变命令调用参数或执行逻辑
- 不改动返回值处理方式
- 不引入 `check=True`（当前代码自行检查 `returncode`，不需要抛出异常）

## Decisions

| 决策 | 选择 | 理由 |
|------|------|------|
| `shell=False` | 添加显式声明 | 当前隐式行为即为 `False`，显式声明消除静默依赖，且满足安全检查 |
| `check=False` | 添加显式声明 | 当前代码已自行检查 `r.returncode`，不需要 subprocess 替它抛异常；显式声明消除 Pylint W1510 告警 |
| 参数顺序 | `shell=False` 放在最后，`check=False` 紧随其后 | 与 subprocess 文档推荐的参数顺序一致 |

## Risks / Trade-offs

- **无风险**：两项参数均保持当前默认行为不变，仅将隐式默认值改为显式声明。

## Open Questions

- 无。
