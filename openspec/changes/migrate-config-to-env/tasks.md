## 1. 依赖安装

- [ ] 1.1 安装 python-dotenv：`pip install python-dotenv`

## 2. 创建配置文件

- [ ] 2.1 创建 `.env.example` 模板文件（提交到 git）
- [ ] 2.2 创建 `.env` 本地配置文件（不提交）
- [ ] 2.3 将 `.env` 加入 `.gitignore`

## 3. 修改代码

- [ ] 3.1 修改 `core/config.py`：导入 `load_dotenv` + `os.getenv` 替换硬编码
- [ ] 3.2 修改 `import_data.py`：删除 `DB_CONFIG`，改从 `core.config` 导入 `DB`
