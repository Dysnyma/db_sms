## Why

当前 `src/` 存在 34 条 Pylint Warning 类告警，涉及 4 个文件。虽然不影响运行，但掩盖了真正的潜在 bug，且不利于代码健壮性维护。

## What Changes

修复全部 34 条 Warning，分为三类：

1. **W0718（21 条）** — `except Exception` 改为捕获具体异常类型（`pymysql.Error`、`ValueError`、`FileNotFoundError` 等）
2. **W0612（8 条）** — 删除未使用的局部变量，或将 `_` 用作忽略标记
3. **W0613（5 条）** — 删除未使用的函数参数，或加 `_` 前缀标记为有意忽略

不改动任何业务逻辑。

## Capabilities

### New Capabilities

- （无新能力）

### Modified Capabilities

- （无规格级别变更）

## Impact

- 涉及 4 个文件：`src/app.py`（16 条）、`src/admin.py`（13 条）、`src/student.py`（3 条）、`src/teacher.py`（2 条）
- 验收：Pylint Warning 归零，评分提升
