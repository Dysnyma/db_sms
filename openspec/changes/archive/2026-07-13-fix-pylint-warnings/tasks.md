## 1. 修复 W0718 — 宽泛 except（21 条）

- [x] 1.1 `src/app.py` — 6 处 `except Exception` → `pymysql.Error`（DB）/ `(pymysql.Error, ValueError, KeyError, csv.Error)`（CSV）
- [x] 1.2 `src/admin.py` — 11 处 `except Exception` → `pymysql.Error`
- [x] 1.3 `src/student.py` — 2 处 `except Exception` → `pymysql.Error`
- [x] 1.4 `src/teacher.py` — 1 处 DB → `pymysql.Error`，1 处 CSV → `(pymysql.Error, ValueError, csv.Error)`

## 2. 修复 W0612 — 未使用变量（8 条）

- [x] 2.1 `src/app.py`: 8 处 `t, m = ...pop("msg")` → `_, m = ...pop("msg")`

## 3. 修复 W0613 — 未使用参数（5 条）

- [x] 3.1 `src/*.py`: backup/restore 类函数 `conn` → `_conn`，`sname` → `_sname`

## 4. 验收

- [x] 4.1 Pylint Warning 归零 ✓（仅 `tempCodeRunnerFile.py` 中 1 条 W0104 属 VSCode 临时文件，不计入）
- [x] 4.2 `flake8 src/` 通过 ✓
- [x] 4.3 Pylint 评分 9.27/10（+0.14）✓
- [ ] 4.4 手动验证：导入格式错误的 CSV → 错误提示正常（需人工确认）
- [ ] 4.5 手动验证：断开数据库后操作 → 报错而非白屏（需人工确认）
