## Why

学生管理页面的「修改」模式中，当某个学生所属的班级已被逻辑删除时，`clmap`（来自 `class_list`，仅查询 `is_deleted=0`）中不再包含该班级 ID，导致列表推导式 `[k for k, v in clmap.items() if v == cur_cid][0]` 得到空列表，抛出 `IndexError: list index out of range`，页面崩溃。

## What Changes

- **[防御层]** 创建数据库触发器，班级逻辑删除时自动级联逻辑删除该班级所有学生（`trg_class_soft_delete_students`）
- **[兜底层]** 修复 `admin_page.py:622` 处 `cur_clabel` 的查找逻辑，当学生所属班级不在 `clmap` 中时提供安全回退（默认选中第一个可用班级）
- 避免页面因空列表 `[0]` 下标越界而崩溃

## Capabilities

### New Capabilities
- `robust-label-lookup`: 提供安全的标签→ID 双向查找工具，保证任意不匹配场景（班级被删除、类型不一致等）不会引发下标越界
- `cascade-class-delete`: 班级逻辑删除时自动级联逻辑删除该班级所有学生（数据库触发器）

### Modified Capabilities

<!-- 无 spec 级别行为变更——这是一个纯实现层面的 bug 修复 -->

## Impact

- `src/pages/admin_page.py`：修改 `student_manage_page` 函数中的标签查找逻辑
- `sql/06_触发器.sql`：新增触发器 `trg_class_soft_delete_students`
- 无新依赖引入
