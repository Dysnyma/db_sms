## Why

代码质量体检报告（Pylint + Flake8）发现 `src/` 下存在 2 处 E0606 运行时错误和 5 处 Flake8 F/E 类逻辑错误。这些错误可能导致程序在某些执行路径下崩溃（变量未定义时使用），或产生无意义的输出（无占位符 f-string），以及造成资源浪费（未使用的导入）。本次修复全部属于零风险的安全改动，不改动业务逻辑。

## What Changes

1. 修复 `src/app.py` E0606：为 `pages` 变量添加兜底赋值，确保所有执行路径均定义该变量
2. 修复 `src/teacher.py` E0606：为 `course_name` 变量添加兜底赋值，确保 `except` 路径有默认值
3. 修复 `src/admin.py` F541（3 处）：将无占位符的 `f'...'` 改为普通 `'...'` 字符串
4. 修复 `src/teacher.py` F541（1 处）：将无占位符的 `f'...'` 改为普通 `'...'` 字符串
5. 修复 `src/teacher.py` F401：删除 `from core.utils import ...` 中的 `input_choice` 和 `pause`
6. 修复 `src/admin.py` E712：将 `if (paged == False)` 改为 `if not paged`

## Capabilities

### New Capabilities

- （无新能力 — 本次为纯缺陷修复）

### Modified Capabilities

- （无规格级别变更 — 修复不改变函数行为或接口）

## Impact

- 修改涉及 4 个文件：`src/app.py`（+3 行兜底赋值）、`src/teacher.py`（+1 行兜底、-2 未使用导入、F541 改普通字符串）、`src/admin.py`（3 处 f→ 普通字符串、1 处布尔比较）
- 无新增依赖，无 API 变更，无数据库变更
- 验收标准：`flake8 src/` 7 条错误全部消失，`pylint src/` 的 E0606 不再出现
