## 1. 加固 admin.py subprocess 调用

- [x] 1.1 `src/admin.py` 第 149 行：`subprocess.run([...])` → 添加 `check=False, shell=False` 参数
- [x] 1.2 `src/admin.py` 第 172 行：`subprocess.run([...], input=...)` → 添加 `check=False, shell=False` 参数

## 2. 加固 app.py subprocess 调用

- [x] 2.1 `src/app.py` 第 267 行：`subprocess.run([...])` → 添加 `check=False, shell=False` 参数
- [x] 2.2 `src/app.py` 第 294 行：`subprocess.run([...], input=...)` → 添加 `check=False, shell=False` 参数

## 3. 加固 reset_data.py subprocess 调用

- [x] 3.1 `src/reset_data.py` 第 27 行：`subprocess.run([...], stdin=...)` → 添加 `check=False, shell=False` 参数

## 4. 验收

- [x] 4.1 运行 `pylint src/ --rcfile="" -rn` 确认 W1510 告警归零
- [x] 4.2 运行 `python -m bandit -r src/` 确认无 B602 高危告警
