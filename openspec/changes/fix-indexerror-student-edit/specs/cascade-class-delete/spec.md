## ADDED Requirements

### Requirement: 班级级联删除学生

当班级被逻辑删除时，系统必须自动级联逻辑删除该班级下所有在读学生。

#### Scenario: 删除班级后学生被级联删除

- **WHEN** 将 `class` 表中某条记录的 `is_deleted` 更新为 `1`
- **AND** `OLD.is_deleted` 为 `0`（或 `NULL`）
- **THEN** 系统必须自动将该班级下所有 `is_deleted = 0` 的学生记录更新为 `is_deleted = 1`

#### Scenario: 非删除更新不触发级联

- **WHEN** 更新 `class` 表中某条记录的 `is_deleted` 之外的字段（如 `name`、`grade`、`major`、`status`）
- **THEN** 不得触发学生级联删除

#### Scenario: 重复删除不重复影响

- **WHEN** 将 `class` 表中某条记录的 `is_deleted` 再次更新为 `1`（已是删除状态）
- **THEN** 即使重新触发，已删除的学生不应受到额外影响（幂等性）

#### Scenario: 级联删除不影响其他班级

- **WHEN** 删除某个班级
- **THEN** 只影响该班级下的学生
- **THEN** 其他班级的学生不受影响
