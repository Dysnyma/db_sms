## Context

当前 `src/app.py` 共 1010 行，12 个页面函数，全部采用 `_make_page` 包装器模式管理数据库连接。审查发现的 12 个问题分布在两层：**基础设施层**（连接管理、查询效率）和 **表现层**（交互反馈、渲染稳定性）。分两阶段重构，互不依赖，可独立执行和验证。

## Goals / Non-Goals

**Goals:**
- Phase 1：连接池化 + 查询缓存，减少 90%+ 的冗余 DB 交互
- Phase 2：统一操作反馈为持久消息、去除不必要的 `st.rerun()`、修复 `st.stop()` 截断

**Non-Goals:**
- 不改动业务逻辑或数据库结构
- 不引入新的第三方库
- 不重构 `src/admin.py`、`src/teacher.py` 等调用方（连接池对它们透明）

## Phase 1: 数据库连接池与查询缓存

### 连接池化方案

在 `src/core/config.py` 中添加：

```python
import streamlit as st
import pymysql
from .config import DB

@st.cache_resource
def get_connection():
    """应用级共享数据库连接（Streamlit 自动管理生命周期）"""
    return pymysql.connect(**DB)
```

**改动影响**：
- `_make_page` 包装器：不再创建和关闭连接，页面函数通过 `get_connection()` 获取
- 各页面函数签名：去掉 `conn` 参数，内部调用 `get_connection()`
- `_login_page`：改用 `get_connection()` 统一连接入口

### 查询缓存方案

对 `core/config.py` 中或页面内的只读查询函数添加 `@st.cache_data(ttl=60)`：

```python
@st.cache_data(ttl=60)
def get_class_list():
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute("SELECT id, name, grade, major, status FROM class WHERE is_deleted=0")
        return cur.fetchall()
```

**缓存失效策略**：在 CRUD 操作后调用 `st.cache_data.clear()` 清除所有缓存，确保列表刷新。

### 移除重复连接

- `_make_page` 包装器中的 `conn = connect()` / `conn.close()` 移除
- `_login_page` 中的 `conn = connect()` / `conn.close()` 替换为 `get_connection()`

## Phase 2: UX 与交互优化

### 统一操作反馈

所有管理页面当前使用的 msg + toast 模式：
```python
# 当前（6 处，以 class_manage_page 为例）
if st.session_state.get("msg"):
    _, m = st.session_state.pop("msg")
    st.toast(m, icon="✅")

# 改为：直接在操作成功后渲染
st.success("新增成功")
```

**涉及页面**：`class_manage_page`、`course_manage_page`、`teacher_manage_page`、`student_manage_page`、`offering_manage_page`、`enrollment_manage_page`

### 减少 `st.rerun()`

针对每个管理页面的增/删/改操作逐一评估：

| 页面              | 操作           | 当前  | 改为                               | 理由                         |
| ----------------- | -------------- | ----- | ---------------------------------- | ---------------------------- |
| class_manage      | 新增/修改/删除 | rerun | 不 rerun                           | 数据不常变，下次操作自动刷新 |
| course_manage     | 新增/修改/删除 | rerun | 不 rerun（新增涉及恢复逻辑时保留） | 同上                         |
| teacher_manage    | 新增/修改/删除 | rerun | 不 rerun                           | 同上                         |
| student_manage    | 新增/修改/删除 | rerun | 不 rerun                           | 同上                         |
| offering_manage   | 新增/修改/删除 | rerun | 不 rerun                           | 同上                         |
| enrollment_manage | 退选           | rerun | 不 rerun                           | 同上                         |

### `st.stop()` 修复

`course_manage_page` 修改模式下：
```python
# 当前
if dup:
    st.warning("课程名已存在...")
    st.stop()  # 页面被截断

# 改为
if dup:
    st.error("课程名已存在...")
    return  # 仅退出当前 mode 分支，页面保持完整
```

### 侧边栏合并

将两处分离的 `with st.sidebar:` 合并为同一代码块，提升可维护性。

## Decisions

| 决策           | 选择                      | 理由                                                            |
| -------------- | ------------------------- | --------------------------------------------------------------- |
| 连接池作用域   | `@st.cache_resource` 单例 | Streamlit 官方推荐模式，自动管理生命周期                        |
| 缓存粒度       | 函数级 `@st.cache_data`   | 针对高频只读查询，TTL 60s 平衡新鲜度和性能                      |
| rerun 保留场景 | 登录/登出/成绩录入        | 需要切换导航结构和刷新数据列表，无法避免                        |
| 执行顺序       | Phase 1 → Phase 2 串行    | Phase 1 的连接改造会改变函数签名，先做完 Phase 1 再改 UX 更干净 |

## Risks / Trade-offs

- **[中风险]** Phase 1 改造 `_make_page` 后，所有页面函数的签名变化（去掉 `conn` 参数）。如果某个页面在 `_make_page` 之外被调用（如 tester），可能破坏调用链。→ **缓解**：`_make_page` 改为注入 `get_connection()`，页面函数内部获取连接，外部调用不变。
- **[低风险]** `@st.cache_data` 默认基于参数哈希。如果查询参数是可变类型（如 list/dict），可能无法正确缓存。→ **缓解**：确保参数为简单类型（int/str/tuple）。
- **[低风险]** 去除 rerun 后，数据列表不会自动刷新。用户可能看到旧数据。→ **缓解**：保留「切换 tab 时刷新」的能力，通过 `st.session_state` 标记脏数据。
- **[低风险]** `course_manage_page` 的「已删除课程恢复」逻辑（第 454-465 行）有复杂的状态分支，去掉 rerun 可能影响状态流转。→ **缓解**：此场景保留 rerun，单独评估。

## Open Questions

- 无。
