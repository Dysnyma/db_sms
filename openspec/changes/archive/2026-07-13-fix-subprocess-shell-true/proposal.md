## Why

代码质量检查发现 `src/` 中存在 4 处 `subprocess.run()` 调用未设置 `shell=False`（或等效的列表传参），存在命令注入安全风险。虽然当前已使用列表参数传递（无需 `shell=True`），但未显式声明 `shell=False`，Pylint W1510 告警说明调用方未对子进程失败做显式处置。本次变更将所有 subprocess 调用的安全模式用显式参数确认，并确保无任何 `shell=True` 残留。

## What Changes

- `src/admin.py` 第 149 行 & 第 172 行：确认列表传参，添加 `check=False`、`shell=False` 显式声明
- `src/app.py` 第 267 行 & 第 294 行：同上
- `src/reset_data.py` 第 27 行：同上
- 无功能行为变更，仅安全加固与静默告警消除

## Capabilities

### New Capabilities

- （无新能力 — 纯安全加固）

### Modified Capabilities

- （无规格级别变更 — 不改变函数行为或接口）

## Impact

- 涉及 3 个文件：`src/admin.py`、`src/app.py`、`src/reset_data.py`
- 无新增依赖，无 API 变更，无数据库变更
- 验收：`pylint src/` W1510 告警归零
