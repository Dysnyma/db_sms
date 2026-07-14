## Why

Streamlit 最佳实践审查发现 `src/app.py` 存在 12 个规范性问题，主要集中在两方面：**数据库连接与查询效率低下**导致响应随数据量增长而变慢，以及 **UX 交互模式不符合 Streamlit 惯用写法**导致页面闪烁和反馈丢失。这些问题不影响核心功能，但随着系统使用规模扩大，性能瓶颈和体验问题会越来越明显。

## What Changes

### 第一阶段：数据库连接池与查询缓存

| 问题 | 改动 | 预期收益 |
|------|------|----------|
| 1. 每次交互新建连接 | `@st.cache_resource` 缓存连接 | 减少 95%+ 的建连开销 |
| 2. 全量数据每次重查 | `@st.cache_data(ttl=60)` 缓存只读查询 | 翻页/切换时零 DB 查询 |
| 9. 连接管理不一致 | 统一走缓存连接，移除 `_make_page` 中的重复建连 | 代码更简洁 |

### 第二阶段：UX 与交互优化

| 问题 | 改动 | 预期收益 |
|------|------|----------|
| 4. `st.rerun()` 过度使用 | 去掉管理页面中不必要的 rerun | 消除页面闪烁，保留输入 |
| 5. 管理页面 toast 一闪而过 | 统一改为 `st.success()`/`st.error()` | 操作反馈清晰可见 |
| 6. `st.warning` 误用 | 操作拒绝场景改用 `st.error` | 语义更准确 |
| 7. `st.stop()` 中断 | 改为 `return` + 条件渲染 | 页面不会被截断 |

## Capabilities

### New Capabilities

- `db-connection-pool`: 数据库连接池化，通过 `@st.cache_resource` 复用连接
- `query-caching`: 只读查询结果缓存，通过 `@st.cache_data` 减少重复 DB 访问
- `ux-feedback-improvement`: 操作反馈统一为持久显示的 success/error 消息
- `rerun-reduction`: 去除不必要的 `st.rerun()`，改为直接渲染结果

### Modified Capabilities

- （无规格级别变更）

## Impact

- 涉及 1 个文件：`src/app.py`
- 涉及 1 个文件：`src/core/config.py`（连接池改造）
- 无新增外部依赖
- 无数据库结构变更
