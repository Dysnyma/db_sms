## Context

当前数据库配置在两个地方硬编码：
- `core/config.py`：DB 字典（host/user/password/database），供 `connect()` 和 `get_connection()` 使用
- `import_data.py`：自己又写了一份几乎相同的 `DB_CONFIG` 字典

两份配置要同步修改，容易漏。且硬编码不利于安全（密码可能随着 git 提交暴露）。

## Goals / Non-Goals

**Goals:**
- 使用 `os.getenv` 从环境变量读取配置，`.env` 文件作为开发环境的载体
- `import_data.py` 改为引用 `core.config.DB`，消除重复
- 零功能变化，不改任何业务逻辑

**Non-Goals:**
- 不改 Streamlit 页面代码
- 不改数据库结构或查询逻辑

## Decisions

### 1. 使用 python-dotenv 而非 os.environ 手动解析

`python-dotenv` 是最流行的 `.env` 加载库，用 `load_dotenv()` 一行代码把 `.env` 内容注入 `os.environ`。

| 方案 | 对比 |
|------|------|
| `python-dotenv` | 一行引入，自动加载 `.env`，社区标准 |
| 手动 `open/read/split` | 要处理注释、引号、空格等边界情况，重复造轮子 |

### 2. 保留默认值

`os.getenv("DB_HOST", "127.0.0.1")` 的第二个参数是默认值。即使 `.env` 文件不存在，项目也能用默认配置直接运行，降低上手成本。

### 3. import_data.py 统一引用 core.config.DB

原来 `import_data.py` 自己定义了 `DB_CONFIG` 字典，和 `config.py` 的 `DB` 内容重复。改为 `from core.config import DB`，消除两份配置维护问题。

### 4. .env.example 提交到 git，.env 不提交

- `.env.example`：模板文件，提交到 git，别人 clone 后复制为 `.env` 即可使用
- `.env`：实际配置，加入 `.gitignore`，不上传 GitHub

## Risks / Trade-offs

- **[运行时依赖]** 新增 `python-dotenv` 一个包，极小且纯 Python，无风险
- **[配置不存在的风险]** 如果 `.env` 文件缺失，所有值都用默认值，仍然能连接本机 MySQL → 可接受
