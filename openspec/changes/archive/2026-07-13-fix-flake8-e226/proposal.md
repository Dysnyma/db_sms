## Why

当前 4 个源文件中存在 7 处 Flake8 E226 告警（算术运算符两侧缺少空格）。虽然不影响代码运行，但不符合 PEP 8 空格规范，也妨碍 `flake8 src/` 全面清零的目标。

## What Changes

- 为 7 处算术运算符补充两侧空格：
  - `src/app.py:718,801` — `*` 运算符
  - `src/core/utils.py:54,93` — `*` 运算符
  - `src/teacher.py:203` — `*` 运算符
  - `src/tester.py:27,55` — `*` 运算符
- 仅补充空格，不修改表达式结构或运算优先级

## Capabilities

### New Capabilities

- （无新能力）

### Modified Capabilities

- （无规格级别变更）

## Impact

- 涉及 4 个文件，全部为纯空格添加
- 算术结果完全不变
