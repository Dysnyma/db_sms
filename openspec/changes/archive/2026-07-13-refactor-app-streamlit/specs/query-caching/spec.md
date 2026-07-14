## ADDED Requirements

### Requirement: 只读查询结果缓存

对于不随用户操作实时变化的基础数据查询（如班级列表、课程列表、教师列表），应使用 `@st.cache_data` 缓存结果，避免每次页面渲染都重复查询数据库。

#### Scenario: 班级列表缓存
- **WHEN** `class_manage_page`、`roster_page`、`student_manage_page` 等页面多次调用 `class_list(conn)`
- **THEN** 在 TTL 有效期内，后续调用应返回缓存结果，不执行 SQL

#### Scenario: 课程列表缓存
- **WHEN** `offering_manage_page` 加载课程下拉列表
- **THEN** 使用 `@st.cache_data(ttl=60)` 缓存课程列表，60 秒内不重复查询

#### Scenario: 缓存失效
- **WHEN** 用户执行增/删/改操作后
- **THEN** `st.cache_data.clear()` 应被调用以刷新相关缓存

#### Scenario: 参数化缓存
- **WHEN** 查询函数接收不同参数（如不同 `class_id`）
- **THEN** 缓存应区分参数值，不同参数对应不同缓存条目

### Requirement: 缓存 TTL 策略

| 数据类型 | TTL | 理由 |
|----------|-----|------|
| 班级列表 | 60s | 不频繁变更，可容忍短暂延迟 |
| 课程列表 | 60s | 同上 |
| 教师列表 | 60s | 同上 |
| 排课列表 | 30s | 相对变化较多 |
| 学生列表 | 30s | 班级管理可能新增学生 |

## MODIFIED Requirements

（无。）

## REMOVED Requirements

（无。）
