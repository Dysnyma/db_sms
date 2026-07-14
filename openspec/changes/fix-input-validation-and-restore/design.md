## Context

当前 `admin_page.py` 中的 CRUD 操作存在两种模式：

**有 try/except 保护的**（已修复）：
- 课程新增/修改 ✅
- 学生新增 ✅
- 排课新增/修改 ✅

**无 try/except 保护的**（需修复）：
- 班级新增/修改/删除
- 课程删除
- 教师新增/修改/删除
- 学生修改/删除
- 排课删除
- 选课退选

这些操作如果遇到数据库错误（外键约束、字段溢出等），会直接崩溃或静默失败。

## Goals / Non-Goals

**Goals:**
- SQL 恢复操作的完整反馈链
- 所有 CRUD 操作有 try/except 保护
- 操作失败时显示具体错误原因

**Non-Goals:**
- 不改动业务逻辑
- 不使用 `st.number_input` 替换所有 `text_input`（只改最重要的）

## Decisions

| 决策 | 选择 | 理由 |
|------|------|------|
| 异常类型 | `pymysql.Error` | 数据库操作的主要异常类型，覆盖 INSERT/UPDATE/DELETE 错误 |
| 恢复操作异常 | `FileNotFoundError` + `Exception` | mysql 命令不存在 + 其他未预见的错误 |
| 错误展示 | `st.error()` | 持久显示，用户看清再操作 |

## Risks / Trade-offs

- **[低风险]** 加了 try/except 后，原本应该崩溃的错误会被捕获并显示为 `st.error()`。这是改进，不是风险。

## Migration Plan

1. 修复 `restore_page`：添加 try/except（已完成）
2. 为班级管理三个操作加 try/except
3. 为课程删除加 try/except
4. 为教师管理三个操作加 try/except
5. 为学生管理修改/删除加 try/except
6. 为排课管理删除加 try/except
7. 为选课退选加 try/except
8. 验收
