## Context

`src/app.py` 包含三类页面函数，按角色自然划分。当前所有函数共享 `conn` 参数（通过 `_make_page` 注入），拆分后每个模块从 `core.config` 导入 `get_connection()`。

## Goals / Non-Goals

**Goals:**
- 按角色拆分为 3 个独立页面模块
- `app.py` 精简为仅导航 + 辅助函数

**Non-Goals:**
- 不改动业务逻辑
- 不改变 `st.Page()` 调用方式
- 不改变 `_make_page` / `_login_page` 逻辑

## Decisions

| 决策 | 选择 | 理由 |
|------|------|------|
| 模块位置 | `src/pages/` 目录 | 与 `src/core/` 平行，结构清晰 |
| 管理员文件名 | `admin_page.py`（而非 `admin.py`） | 避免与项目根目录的 `admin.py`（CLI 教务模块）命名冲突 |
| 函数签名 | 保留 `conn` 参数不变 | 改动最小，不破坏 `_make_page` 调用 |
| 共用工具 | 留在 `app.py` 中 `_make_page` / `_login_page` | 只有 `app.py` 需要它们 |
| 依赖注入 | 各模块独立导入所需函数 | 从 `core.config` 导入 `get_connection`，`app.py` 的 import 段也会大幅简化 |
| `_sem_options` 辅助函数 | 随调用者移入 `pages/admin_page.py` | 只在 `offering_manage_page` 中使用 |

## Risks / Trade-offs

- **[低风险]** 移动函数到新文件时可能漏掉 import → 验收时跑一遍 3 个角色即可发现
- **[低风险]** 拆分后 app.py 变短，方便后续维护

## Migration Plan

1. 创建 `src/pages/` 目录，**不加 `__init__.py`**
2. 从 `app.py` 剪切学生页面 → `src/pages/student.py`，补全 import
3. 从 `app.py` 剪切教师页面 → `src/pages/teacher.py`，补全 import
4. 从 `app.py` 剪切管理员页面 → `src/pages/admin_page.py`（注意文件名），连带 `_sem_options` 一起迁移，补全 import
5. 更新 `app.py`：删除已迁移的函数和过时的 import，保留导航 + `_make_page` + `_login_page` + 各角色页面模块的导入
6. 验收

## Open Questions

- 无。
