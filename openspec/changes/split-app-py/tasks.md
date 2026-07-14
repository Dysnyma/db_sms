## 1. 准备工作

- [x] 1.1 创建 `src/pages/` 目录（**不加 `__init__.py`**）

## 2. 拆分学生页面

- [x] 2.1 创建 `src/pages/student.py`（108 行）：`show_courses_page`、`my_grades_page`、`semester_avg_page`、`enroll_page`、`unenroll_page`

## 3. 拆分教师页面

- [x] 3.1 创建 `src/pages/teacher.py`（83 行）：`grade_input_page`、`batch_grade_page`、`my_students_page`

## 4. 拆分管理员页面

- [x] 4.1 创建 `src/pages/admin_page.py`（725 行，含 `_sem_options`）：全部 14 个管理员页面

## 5. 精简 app.py

- [x] 5.1 更新 `app.py`（1039→162 行）：只保留 `_make_page`、`_login_page`、导航配置

## 6. 验收

- [x] 6.1 `flake8 src/app.py src/pages/` 通过
- [x] 6.2 `pylint src/app.py --rcfile="" -rn` 通过
- [ ] 6.3 手动验证：运行 `streamlit run src/app.py` 走一遍三个角色核心流程
