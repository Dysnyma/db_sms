## ADDED Requirements

### Requirement: 按角色拆分页面模块

页面函数应按角色分组到独立的 Python 模块中，每个模块对应一个角色。

#### Scenario: 学生页面可独立导入
- **WHEN** `from pages.student import show_courses_page, enroll_page, unenroll_page, my_grades_page, semester_avg_page`
- **THEN** 所有导入成功，无循环依赖

#### Scenario: 教师页面可独立导入
- **WHEN** `from pages.teacher import grade_input_page, batch_grade_page, my_students_page`
- **THEN** 所有导入成功

#### Scenario: 管理员页面可独立导入
- **WHEN** `from pages.admin import summary_page, roster_page, class_report_page, class_manage_page, course_manage_page, teacher_manage_page, student_manage_page, offering_manage_page, enrollment_manage_page`（及其他管理页面）
- **THEN** 所有导入成功

### Requirement: 模块维护独立的 import 声明

每个页面模块应包含自身所需的 import，不依赖 `app.py` 的全局导入。

#### Scenario: 模块自包含
- **WHEN** 检查 `pages/student.py` 的 import 段
- **THEN** 应包含 `pandas`、`pymysql`、`streamlit`、`get_connection` 等该模块页面所需的全部导入

## MODIFIED Requirements

（无。）

## REMOVED Requirements

（无。）
