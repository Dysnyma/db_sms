## Why

当前 `src/` 目录下 12 个 Python 文件（含 1 个 VSCode 临时文件）不符合 Black 默认格式标准。尽管 Pylint 评分为 9.10/10，但格式不统一（单引号/双引号混用、缩进风格不一致、括号换行不统一）降低了代码可读性与团队协作体验。本次变更一次性格式化所有项目源文件，零语义改动。

## What Changes

- 对 `src/` 下 11 个项目 Python 文件执行 `black src/` 标准化格式化：
  `admin.py`, `app.py`, `student.py`, `teacher.py`, `utils.py`, `config.py`, `auth.py`, `main.py`, `reset_data.py`, `import_data.py`, `tester.py`
- 排除 VSCode 临时文件 `tempCodeRunnerFile.py`
- 仅涉及：引号统一（单引号→双引号）、尾随逗号、括号换行、空行规范等纯格式调整

## Capabilities

### New Capabilities

- （无新能力 — 纯代码风格统一）

### Modified Capabilities

- （无规格级别变更 — 不改变函数行为或接口）

## Impact

- 涉及 11 个文件，全部为纯格式改动
- 无新增依赖，无 API 变更，无数据库变更
- 验收：`black --check src/` 无告警，`pylint + flake8` 问题数不反弹
