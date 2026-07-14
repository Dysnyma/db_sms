## ADDED Requirements

### Requirement: 数据库连接池化

Streamlit 应用每次页面渲染和交互回调都应复用数据库连接，而非新建。

#### Scenario: 页面间共享连接
- **WHEN** 用户在多个管理页面之间切换
- **THEN** 所有页面应复用同一个数据库连接实例

#### Scenario: 操作后页面重渲染
- **WHEN** 用户执行增删改操作后页面 rerun
- **THEN** rerun 后的页面应复用已建立的连接，不新建

### Requirement: `@st.cache_resource` 封装

连接池应通过 Streamlit 的 `@st.cache_resource` 装饰器实现，该装饰器专为管理全局资源（数据库连接、HTTP 客户端等）设计。

#### Scenario: 连接函数签名
- **WHEN** 模块导入或首次渲染时调用连接函数
- **THEN** 返回的连接对象应被 `@st.cache_resource` 缓存，后续调用返回同一实例

#### Scenario: 连接异常处理
- **WHEN** 数据库服务器断开导致连接失效
- **THEN** 下一次页面渲染应自动重建连接，不抛出未捕获异常

### Requirement: 移除 `_make_page` 重复建连

当前 `_make_page` 包装器在每个页面函数调用时独立建连和关连。改为统一使用池化连接后，应移除包装器中的建连逻辑。

#### Scenario: 页面函数不再建连
- **WHEN** 页面函数（如 `class_manage_page`）被调用
- **THEN** 函数应通过 `get_connection()` 获取池化连接，而非 `_make_page` 传入

## MODIFIED Requirements

（无。）

## REMOVED Requirements

### Requirement: `_make_page` 的独立连接管理

**Reason**: 被 `@st.cache_resource` 池化连接替代，不再需要每个页面独立建连。

**Migration**: 将 `_make_page` 中的 `connect()` / `conn.close()` 逻辑移除，改为 `get_connection()` 调用池化连接。
