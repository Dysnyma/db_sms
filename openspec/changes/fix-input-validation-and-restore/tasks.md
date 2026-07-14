## 1. SQL 恢复反馈修复

- [x] 1.1 `restore_page`：添加 `try/except FileNotFoundError` + `Exception`

## 2. 班级管理异常保护

- [x] 2.1 新增班级：`try/except pymysql.Error`
- [x] 2.2 修改班级：`try/except pymysql.Error`
- [x] 2.3 删除班级：`try/except pymysql.Error`

## 3. 课程管理异常保护

- [x] 3.1 删除课程：`try/except pymysql.Error`

## 4. 教师管理异常保护

- [x] 4.1 新增教师：`try/except pymysql.Error`
- [x] 4.2 修改教师：`try/except pymysql.Error`
- [x] 4.3 删除教师：`try/except pymysql.Error`

## 5. 学生管理异常保护

- [x] 5.1 修改学生：`try/except pymysql.Error`
- [x] 5.2 删除学生：`try/except pymysql.Error`

## 6. 排课管理异常保护

- [x] 6.1 删除排课：`try/except pymysql.Error`

## 7. 选课管理异常保护

- [x] 7.1 强制退选：`try/except pymysql.Error`

## 8. 学分输入保护

- [x] 8.1 新增课程学分：`st.number_input(min=0, max=20)`
- [x] 8.2 修改课程学分：`st.number_input(min=0, max=20)`

## 9. 验收

- [x] 9.1 `flake8 src/pages/admin_page.py` 无告警
- [ ] 9.2 手动验证：上传 .sql 文件 → 点确认 → 看是否有错误提示
- [ ] 9.3 手动验证：学分输入框只能填 0~20
