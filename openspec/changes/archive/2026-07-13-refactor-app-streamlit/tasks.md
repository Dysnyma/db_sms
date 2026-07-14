## Phase 1: 数据库连接池与查询缓存 ✅

### 1.1 连接池化

- [x] 1.1.1 `src/core/config.py`：添加 `get_connection()` 函数，使用 `@st.cache_resource` 装饰
- [x] 1.1.2 `src/app.py` `_make_page`：移除 `conn = connect()` / `conn.close()`，使用 `get_connection()`
- [x] 1.1.3 `src/app.py` `_login_page`：替换 `connect()` / `conn.close()` 为 `get_connection()`
- [ ] 1.1.4 手动验证：页面切换 5 次以上确认连接只创建一次（需人工）

### 1.2 只读查询缓存

- [x] 1.2.1 添加 7 个 `@st.cache_data(ttl=60)` 缓存包装函数
- [x] 1.2.2 在所有 `st.rerun()` 前调用 `_clear_caches()` 刷新缓存
- [x] 1.2.3 `offering_manage_page` 的 `sem_options` / `sem_opts` 改用缓存
- [ ] 1.2.4 手动验证：同一页面反复切换，观察 DB 查询次数减少（需人工）

## Phase 2: UX 与交互优化 ✅

### 2.1 统一操作反馈（6 个管理页面）

- [x] 2.1.1 `class_manage_page`：`st.toast` → `st.success`，移除 msg 模式
- [x] 2.1.2 `course_manage_page`：同上 + `st.warning` → `st.error`
- [x] 2.1.3 `teacher_manage_page`：同上
- [x] 2.1.4 `student_manage_page`：同上
- [x] 2.1.5 `offering_manage_page`：同上
- [x] 2.1.6 `enrollment_manage_page`：同上

### 2.2 减少 `st.rerun()`

- [x] 2.2.1 `class_manage_page`：新增/修改/删除后不 rerun
- [x] 2.2.2 `course_manage_page`：新增（非恢复场景）/修改/删除后不 rerun
- [x] 2.2.3 `teacher_manage_page`：新增/修改/删除后不 rerun
- [x] 2.2.4 `student_manage_page`：新增/修改/删除后不 rerun
- [x] 2.2.5 `offering_manage_page`：新增/修改/删除后不 rerun
- [x] 2.2.6 `enrollment_manage_page`：退选后不 rerun

### 2.3 `st.stop()` 修复

- [x] 2.3.1 `course_manage_page`：`st.stop()` → `return` + `st.error`

### 2.4 侧边栏合并

- [x] 2.4.1 侧边栏已合并为单个 `with st.sidebar:` 块

## 验收

- [ ] 3.1 全功能回归：学生/教师/管理员三个角色核心流程走一遍（需人工）
- [ ] 3.2 性能验证：打开浏览器 DevTools Network 标签，确认 DB 查询次数减少（需人工）
- [ ] 3.3 反馈验证：每个管理页面执行增删改，确认 success/error 消息持久显示（需人工）
- [x] 3.4 `pylint src/app.py --rcfile="" -rn` 通过（9.36/10）
- [x] 3.5 `flake8 src/app.py` 通过
