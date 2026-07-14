## Context

`student_manage_page` 的「修改」模式中，通过 `[k for k, v in clmap.items() if v == cur_cid][0]` 将学生记录的 `class_id` 逆向映射回班级标签。当该班级已被逻辑删除时，`clmap`（仅包含 `is_deleted=0` 的班级）中查不到 `cur_cid`，列表为空，`[0]` 抛出 `IndexError`。

当前相关数据流：

```
class_list(conn)       → classes       → clmap = {label: id}     只含 is_deleted=0
student_full_list(conn) → rows          → simap = {id: (name,no,class_id)}
                                          slmap = {label: id}
```

`clmap` 的值类型取决于 PyMySQL 游标返回的 `r[0]`（class.id），`simap` 中 `r[3]`（student.class_id）同理。两者在默认游标下均为 `int`，但如果游标类型不同或不一致，可能存在隐式类型不匹配风险。

## Goals / Non-Goals

**Goals:**
- 彻底消除 `admin_page.py:622` 处的 `IndexError`
- 当学生所属班级不在 `clmap` 中时，编辑表单不会崩溃，而是默认选中第一个可用班级
- 统一标签查找模式，使类似问题不再出现在其他页面

**Non-Goals:**
- 不修改数据库 schema 或查询逻辑（`class_list` 仍只返回 `is_deleted=0` 的班级）
- 不重构整个学生管理页面

## Decisions

1. **[防御层] 触发器方案：`AFTER UPDATE` 检测 `is_deleted` 变化**
   - 在 `class` 表上创建 `AFTER UPDATE` 触发器
   - 仅在 `NEW.is_deleted = 1 AND (OLD.is_deleted = 0 OR OLD.is_deleted IS NULL)` 时触发
   - 执行 `UPDATE student SET is_deleted = 1 WHERE class_id = NEW.id AND is_deleted = 0`
   - **为什么不用 `BEFORE`**：`BEFORE` 在修改生效前执行，不适合跨表级联操作；`AFTER` 保证当前行的修改已提交
   - **为什么不走应用层**：触发器确保不论通过哪种方式删除班级（管理页面、手动 SQL、未来新界面），级联删除都自动生效

2. **[兜底层] UI 安全查找**
   - 用反向字典 `cid_to_label` + `.get()` 替代列表推导式
   - 当 `cur_cid` 不在 `clmap` 中时，fallback 到 `clabels[0]` + 显示提示
   - 即使触发器失效或存在历史脏数据，UI 也不会崩溃

3. **提取为可复用工具函数（低优先级，可选）**
   - 考虑到类似模式在其他管理页面也可能出现，可将 `clmap` + 反向查找封装为通用 `LabelMap` 辅助类
   - 本次修复暂不引入，保持最小改动原则

## Risks / Trade-offs

- **[体验] 学生班级被删除后编辑时默认选中第一个班级** → 用户需手动重新选择正确班级。页面顶部有提示文字说明原因
- **[一致性问题] 若同页面多处使用相同查找模式** → 本次仅修复 `student_manage_page`，其他页面如有类似问题需单独处理
- **[游标类型] 不同数据库游标可能导致 int/str 不匹配** → 使用 `int()` 或 `str()` 显式转换比对值，消除隐式类型问题
