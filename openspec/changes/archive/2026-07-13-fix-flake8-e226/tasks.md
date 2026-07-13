## 1. 修复 E226 空格告警

- [x] 1.1 `src/app.py` 第 718、801 行：补充 `+` 两侧空格
- [x] 1.2 `src/core/utils.py` 第 54、93 行：补充 `+` 两侧空格
- [x] 1.3 `src/teacher.py` 第 203 行：补充 `+` 两侧空格
- [x] 1.4 `src/tester.py` 第 27、55 行：补充 `-` 两侧空格

## 2. 验收

- [x] 2.1 运行 `flake8 src/` 确认全部清零
- [x] 2.2 运行 `black --check src/` 确认格式未被破坏
