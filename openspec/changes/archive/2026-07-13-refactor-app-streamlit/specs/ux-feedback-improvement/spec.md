## ADDED Requirements

### Requirement: 操作反馈持久化

所有 CRUD 页面的操作结果反馈应使用持久显示的 `st.success()` / `st.error()`，而非自动消失的 `st.toast()`。

#### Scenario: 新增操作反馈
- **WHEN** 用户新增班级/课程/教师/学生/排课成功
- **THEN** 页面应显示绿色 `st.success("新增成功")`，该消息持续到用户下次操作，而非一闪而过

#### Scenario: 修改操作反馈
- **WHEN** 用户修改记录成功
- **THEN** 页面应显示持久化的成功消息

#### Scenario: 删除操作反馈
- **WHEN** 用户执行删除成功
- **THEN** 页面应显示持久化的成功消息

#### Scenario: 错误操作反馈
- **WHEN** 操作因数据库异常或业务规则拒绝而失败
- **THEN** 页面应显示红色 `st.error()`，包含具体错误描述

### Requirement: `st.warning` 语义纠正

当前 `course_manage_page` 在课程名冲突时使用 `st.warning`。操作被拒绝的场景应使用 `st.error`。

#### Scenario: 课程名冲突
- **WHEN** 用户新增课程时输入已存在的课程名
- **THEN** 页面应显示 `st.error("课程名已存在")`，表示操作被拒绝

### Requirement: 消除 `st.stop()` 页面截断

当前 `course_manage_page` 的修改模式下使用 `st.stop()` 终止脚本执行，导致页面内容被截断。改为条件渲染 + `return`。

#### Scenario: 课程名冲突（修改模式）
- **WHEN** 用户修改课程名时新名称与已有课程冲突
- **THEN** 页面应显示错误消息，同时下方的保存按钮应保持可见或禁用，页面不应被截断

## MODIFIED Requirements

（无。）

## REMOVED Requirements

（无。）
