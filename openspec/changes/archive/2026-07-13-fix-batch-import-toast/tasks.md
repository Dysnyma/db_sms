## 1. 修改提示展示方式

- [x] 1.1 `batch_grade_page`：去掉 `st.session_state.msg` + `st.rerun()`，直接 `st.success()` 在页面底部
- [x] 1.2 `grade_input_page`：`st.toast(m, icon="✅")` → `st.success(m)`
- [x] 1.3 `batch_grade_page`：行错误 `st.warning()` → `st.error()` + 添加行号
- [x] 1.4 `teacher.py` CLI 版：结果后加 `input("\n  按回车继续...")` 暂停

## 2. 验收

- [ ] 2.1 运行 `streamlit run src/app.py` 导入 CSV，确认结果在页面**底部**持久显示
- [ ] 2.2 导入格式错误的 CSV，确认行错误以红色 `st.error()` 逐行显示
- [ ] 2.3 CLI 版 `python src/tester.py` 批量导入，确认按回车才返回菜单
