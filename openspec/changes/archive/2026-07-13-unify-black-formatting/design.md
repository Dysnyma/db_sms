## Context

当前 11 个 Python 源文件的代码风格与 Black 默认格式不一致，主要差异包括：
- 字符串引号不统一（部分单引号、部分双引号）
- 函数/方法参数换行位置不一致
- 括号内尾随逗号缺失
- 空行数量不规范

## Goals / Non-Goals

**Goals:**
- 所有 11 个项目文件通过 `black --check src/` 检查
- black 格式化后不影响业务逻辑

**Non-Goals:**
- 不自定义 Black 配置（`pyproject.toml` 中不设 `--line-length` 等覆盖项）
- 不修改 VSCode 临时文件 `tempCodeRunnerFile.py`
- 不主动修复 Black 无法覆盖的 Pylint/Flake8 问题

## Decisions

| 决策 | 选择 | 理由 |
|------|------|------|
| **格式化方式** | `black src/` 批量处理 | Black 为确定性格式化工具，多次运行结果一致 |
| **配置** | 纯默认配置 | 与社区标准对齐，避免争议；项目无已有 `pyproject.toml` |
| **排除文件** | `tempCodeRunnerFile.py` | 属于 VSCode 自动生成的临时文件，不应纳入版本管理 |
| **git 处理** | 格式化后提交 | 与之前 E0606/F541/E712 修复一并提交，避免游离改动 |

## Risks / Trade-offs

- **[低风险]** Black 格式化可能改变长字符串的换行位置，但不会改变字符串值本身。→ 在 PR 审查中重点关注 `print()` / `input()` 的参数换行。
- **[低风险]** 大量文件变更会导致 git blame 信息被覆盖。→ 本次与之前的安全修复一并提交，可通过 `.git-blame-ignore-revs` 标记格式化提交。

## Open Questions

- 无。
