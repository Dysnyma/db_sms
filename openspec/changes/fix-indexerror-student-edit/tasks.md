## 1. 数据库触发器——级联删除学生

- [x] 1.1 在 `sql/06_触发器.sql` 末尾追加触发器 `trg_class_soft_delete_students`

## 2. UI 安全查找——反向字典 + fallback

- [x] 2.1 在 `clmap` 构建完成后，新建 `cid_to_label` 反向字典：`{v: k for k, v in clmap.items()}`
- [x] 2.2 替换 `admin_page.py:622` 的列表推导式为 `cid_to_label.get(cur_cid)`，当找不到时返回 `None`
- [x] 2.3 在编辑表单中处理 `cur_clabel is None` 的情况：`new_cid` 默认选 `clabels[0]`，并在 selectbox 上方用 `st.info()` 显示"原班级已删除，请重新选择"提示
- [x] 2.4 确保 selectbox 的 `index` 参数在 `cur_clabel is None` 时使用 `index=0`，而不是 `clabels.index(None)` 抛异常

## 3. 验证

- [ ] 3.1 手动测试：在数据库管理工具或通过应用删除一个班级，确认该班级所有学生被自动逻辑删除
- [ ] 3.2 手动测试：新增一个学生→软删除其班级→进入学生管理页的修改模式→选中该学生→确认页面不崩溃，下拉框默认选中第一个班级且显示提示
- [ ] 3.3 手动测试：正常班级的学生编辑功能不受影响（回归测试）
- [ ] 3.4 手动测试：新增学生功能不受影响（回归测试）
