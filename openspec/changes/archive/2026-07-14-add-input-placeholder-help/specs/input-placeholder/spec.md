## ADDED Requirements

### Requirement: Text input has placeholder and help text

Every `st.text_input` on the admin and student pages SHALL display a `placeholder` (example value) and `help` (format rule) consistent with the Pydantic validation constraints.

#### Scenario: Student number input
- **WHEN** admin sees the "学号" text input
- **THEN** it SHALL show placeholder="20240001" and help="学号为 8-12 位纯数字，不可包含字母或符号"

#### Scenario: Teacher number input
- **WHEN** admin sees the "工号" text input
- **THEN** it SHALL show placeholder="10001" and help="工号为 5-20 位数字"

#### Scenario: Teacher phone input
- **WHEN** admin sees the "电话" text input
- **THEN** it SHALL show placeholder="13800138000" and help="电话为 7-15 位纯数字"

#### Scenario: Class grade input
- **WHEN** admin sees the "年级" text input
- **THEN** it SHALL show placeholder="2024" and help="年级为 4 位年份"

#### Scenario: Semester query input
- **WHEN** student sees the "学期" text input
- **THEN** it SHALL show placeholder="2024-2025-1" and help="格式如：2024-2025-1（开始学年-结束学年-学期）"

#### Scenario: Name input (student/teacher/class)
- **WHEN** admin sees any "姓名"/"班级名"/"课程名"/"专业" text input
- **THEN** it SHALL show placeholder with an example and help for max length
