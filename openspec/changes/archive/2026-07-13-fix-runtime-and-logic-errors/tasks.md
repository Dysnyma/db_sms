## 1. 修复 E0606 运行时错误

- [x] 1.1 `src/app.py` — 为 `pages` 变量添加兜底空字典赋值，确保所有执行路径均有定义
- [x] 1.2 `src/teacher.py` — 在函数开头为 `course_name` 添加兜底空字符串赋值（`course_name = ""`）

## 2. 修复 Flake8 F541 无占位符 f-string

- [x] 2.1 `src/admin.py` — 修复第 166 行：`f'  确认恢复？这将覆盖当前数据！(y/N): '` → 去掉 `f` 前缀
- [x] 2.2 `src/admin.py` — 修复第 177 行：`f'\n  ✅ 恢复成功！请重启程序'` → 去掉 `f` 前缀
- [x] 2.3 `src/admin.py` — 修复第 910 行：`f'\n  ✅ 已删除'` → 去掉 `f` 前缀
- [x] 2.4 `src/teacher.py` — 修复第 97 行：无占位符 f-string → 去掉 `f` 前缀

## 3. 修复 Flake8 F401 未使用导入

- [x] 3.1 `src/teacher.py` — 从 `from core.utils import ...` 中删除 `input_choice` 和 `pause`

## 4. 修复 Flake8 E712 布尔值比较

- [x] 4.1 `src/admin.py` — 第 44 行：`if (paged == False):` → `if not paged:`

## 5. 验收

- [x] 5.1 运行 `flake8 src/ --max-line-length=120` 确认 7 条问题全部消失
- [x] 5.2 运行 `python test/check_code.py` 确认 Pylint 的 E0606 不再出现
