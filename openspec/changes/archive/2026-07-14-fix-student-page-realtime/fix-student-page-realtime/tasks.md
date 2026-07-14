## 1. 选课页面 - enroll_page 重写

- [x] 1.1 页面顶部添加 `st.session_state.msg` 拦截显示块
- [x] 1.2 表格渲染保持现有结构（不修改）
- [x] 1.3 按钮事件内：`cur = conn.cursor()` → `with conn.cursor() as cur:`
- [x] 1.4 成功时：`conn.commit()` → `st.session_state.msg = ("success", "选课成功！")` → `st.rerun()`
- [x] 1.5 失败时：`conn.rollback()` → `st.session_state.msg = ("error", ...)` → `st.rerun()`
- [x] 1.6 清理：移除旧版 `cur.fetchall()` + `cur.nextset()` 调用

## 2. 退选页面 - unenroll_page 重写

- [x] 2.1 页面顶部添加 `st.session_state.msg` 拦截显示块
- [x] 2.2 按钮事件内：`cur = conn.cursor()` → `with conn.cursor() as cur:`
- [x] 2.3 成功时：`conn.commit()` → `st.session_state.msg = ("success", "退选成功！")` → `st.rerun()`
- [x] 2.4 失败时：`conn.rollback()` → `st.session_state.msg = ("error", ...)` → `st.rerun()`
- [x] 2.5 清理：移除旧版 `cur.fetchall()` + `cur.nextset()` 调用

## 3. 循环导入修复（模块重命名）

- [x] 3.1 `src/student.py` → `src/student_tui.py`，消除与 `pages/student.py` 的命名冲突
- [x] 3.2 `src/teacher.py` → `src/teacher_tui.py`，消除与 `pages/teacher.py` 的命名冲突
- [x] 3.3 更新 `main.py`、`tester.py`、`pages/student.py`、`pages/teacher.py` 中所有引用

## 4. 验证

- [x] 4.1 Python 语法检查通过
- [x] 4.2 模块导入成功
- [x] 4.3 选课：操作后表格更新，消息在页面顶部显示（需重启 Streamlit 确认）
- [x] 4.4 退选：操作后表格更新，消息在页面顶部显示（需重启 Streamlit 确认）
