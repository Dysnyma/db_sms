## 1. 执行 Black 格式化

- [x] 1.1 运行 `black src/` 格式化所有源文件

## 2. 验收

- [x] 2.1 运行 `black --check src/` 确认全部通过
- [x] 2.2 运行 `flake8 src/` 确认无新问题（E226 为预先存在）
- [x] 2.3 运行 `pylint src/ --rcfile="" -rn` 确认格式化后仍通过（9.10/10）
