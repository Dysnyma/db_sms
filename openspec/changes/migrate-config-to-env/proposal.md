## Why

当前 MySQL 数据库配置（host、user、password、database）硬编码在 `core/config.py` 和 `import_data.py` 两个文件中。如果有人想用不同的数据库地址、用户名或密码，必须直接修改代码。更严重的是，如果将来设了密码，会被 git 记录并传到 GitHub，造成安全隐患。

## What Changes

- 在项目根目录创建 `.env` 文件，存放所有数据库配置
- 创建 `.env.example` 作为模板（提交到 git，供其他人参考）
- 修改 `core/config.py`，改用 `os.getenv` 读取配置，保留默认值
- 修改 `import_data.py`，统一引用 `core.config.DB`，消除重复配置
- 将 `.env` 加入 `.gitignore`，防止敏感信息被提交

## Capabilities

### New Capabilities
- `env-config`: 基于 `.env` + `os.getenv` 的数据库配置管理

### Modified Capabilities

（无）

## Impact

- **修改文件**: `core/config.py`、`import_data.py`、`.gitignore`
- **新增文件**: `.env`（本地，不提交）、`.env.example`（模板，提交）
- **零功能变化**：只改变配置的读取方式，不改变任何运行逻辑
