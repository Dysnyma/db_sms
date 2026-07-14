## Context

项目当前所有表单输入依靠 Streamlit 原生控件，但 `st.text_input` 只返回字符串，没有任何格式校验。学号、工号、电话、学期等字段直接传入 SQL / 存储过程，错误格式只有在数据库层报错时才能被发现。

已有代码模式：每个页面的 CRUD 表单在 `st.button` 回调中直接拼接 SQL/调用存储过程，验证逻辑散布在业务代码中，没有统一的校验层。

## Goals / Non-Goals

**Goals:**

- 新增 `src/core/models.py`，用 Pydantic 集中定义所有表单输入 model
- 提供统一的 `validate_or_error()` 辅助函数，验证失败自动在 Streamlit 上 toast 错误并中断提交
- 覆盖所有 `st.text_input` 纯文本输入：姓名、学号、工号、电话、学期、年级、专业、课程名、职称
- 改动量控制在 +30 行以内，零重构

**Non-Goals:**

- 不改 `number_input` / `selectbox`（已由控件保证类型安全）
- 不改 CLI TUI 脚本（`student_tui.py` / `teacher_tui.py`，走 `input()`）
- 不改 `import_data.py`（CSV 批量导入自有校验逻辑）
- 不引入前端级联校验（如学号变化后联动查询等）
- 不改数据库层或业务逻辑

## Decisions

### 1. 使用 Pydantic v2 而非自定义校验函数

| 方案 | 对比 |
|------|------|
| Pydantic v2 | 声明式 Field 约束，pattern/ge/le/min_length 开箱即用，错误信息结构化 |
| 手写 if-else | 每个字段要写 if not re.match(...) → 重复代码，维护成本高 |
| marshmallow | 功能类似，但 Pydantic 生态更成熟，与 FastAPI 等工具通用 |

**结论**：Pydantic v2，声明式约束，代价最低。

### 2. validate_or_error() 返回 None 而非抛异常

以 `toast` 方式显示错误，不阻断页面流程（用户可继续修改）。返回 `None` 时调用方 `if data is None: return` 即可。

选择 `st.toast` 而非 `st.error`，因为 toast 短暂出现后消失，不会污染页面状态。

### 3. model 按实体分组，不按页面分组

学生 create/update 共享一个 model（因为字段相同），而不是每页面独立定义。减少重复。

### 4. 可选字段用 `Optional[str] = Field(None)`

教师职称和电话允许为空。Pydantic 默认不将空字符串视为 None，因此需配合 `Optional` + `Field(None)` 处理。

## Risks / Trade-offs

- **[依赖新增]** Pydantic v2 约 2MB，对项目体积影响极小，纯 Python 无原生扩展 → 可接受
- **[双维护点]** `number_input` 的 `min_value` / `max_value` 与 Pydantic 的 `ge`/`le` 存在语义重叠 → 约定以 Pydantic 为唯一真实来源，控件侧设宽松范围
- **[导入耗时]** Pydantic model 首次导入有类创建开销，但对 Streamlit 页面生命周期（秒级）影响可忽略
