## ADDED Requirements

### Requirement: 所有 CRUD 操作必须有异常保护

每个涉及数据库写入的操作（INSERT/UPDATE/DELETE）必须包裹在 try/except 中，失败时显示具体错误信息。

#### Scenario: 操作成功
- **WHEN** 数据库操作成功
- **THEN** 页面按现有逻辑显示成功消息

#### Scenario: 操作失败
- **WHEN** 数据库操作抛出 `pymysql.Error`
- **THEN** 页面显示 `st.error()` 包含错误详情
- **AND** 页面不崩溃、不白屏

### Requirement: 受影响的管理操作

以下操作必须添加 try/except `pymysql.Error`：

| 页面 | 操作 | 当前状态 |
|------|------|----------|
| 班级管理 | 新增/修改/删除 | ❌ 无保护 |
| 课程管理 | 删除 | ❌ 无保护 |
| 教师管理 | 新增/修改/删除 | ❌ 无保护 |
| 学生管理 | 修改/删除 | ❌ 无保护 |
| 排课管理 | 删除 | ❌ 无保护 |
| 选课管理 | 退选 | ❌ 无保护 |

## MODIFIED Requirements

（无。）

## REMOVED Requirements

（无。）
