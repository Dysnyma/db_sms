## 1. 依赖安装

- [x] 1.1 安装 pydantic：`pip install pydantic`

## 2. 核心 Model 定义

- [x] 2.1 新建 `src/core/models.py`，定义 `StudentCreate` / `StudentUpdate` model（name min_length=1, max_length=50；no pattern=r"^\d{8,12}$"；class_id: int）
- [x] 2.2 定义 `TeacherCreate` / `TeacherUpdate` model（name；no pattern=r"^\d{5,20}$"；title Optional；phone Optional + pattern=r"^\d{7,15}$"）
- [x] 2.3 定义 `ClassCreate` / `ClassUpdate` model（name；grade pattern=r"^\d{4}$"；major）
- [x] 2.4 定义 `CourseCreate` / `CourseUpdate` model（name；credit: float + ge=0.5 + le=30.0）
- [x] 2.5 定义 `SemesterQuery` model（semester pattern=r"^\d{4}-\d{4}-\d+$"）
- [x] 2.6 实现 `validate_or_error(model_cls, **data)` 辅助函数：捕获 ValidationError，用 st.toast 显示错误，返回 dict 或 None

## 3. 集成到 admin_page.py

- [x] 3.1 在新增/修改教师处插入 TeacherCreate / TeacherUpdate 验证
- [x] 3.2 在新增/修改学生处插入 StudentCreate / StudentUpdate 验证
- [x] 3.3 在新增/修改班级处插入 ClassCreate / ClassUpdate 验证
- [x] 3.4 在新增/修改课程处插入 CourseCreate / CourseUpdate 验证

## 4. 集成到 student.py

- [x] 4.1 在学期查询处插入 SemesterQuery 验证
