## Context

34 条 Warning 分布：

| 代码 | 数量 | 含义 | 修复策略 |
|------|------|------|----------|
| W0718 | 21 | `except Exception` 过于宽泛 | 改为捕获具体异常，多个异常用元组 |
| W0612 | 8 | 定义了未使用的变量 | 删除或改为 `_` |
| W0613 | 5 | 函数参数未使用 | 加 `_` 前缀或删除 |

## Goals / Non-Goals

**Goals:**
- 34 条 Warning 全部清除（保留 2 处合理的顶层兜底，加注释说明）
- Pylint 评分预计 ≥9.4

**Non-Goals:**
- 不改动 Convention / Refactor 类问题
- 不引入新功能

## Decisions

| 决策 | 选择 | 理由 |
|------|------|------|
| W0718 修复策略 | 按场景选择具体异常 | 数据库操作→`pymysql.Error`；文件操作→`FileNotFoundError`/`PermissionError`/`OSError`；类型转换→`ValueError`/`TypeError`；CSV→添加 `csv.Error`。不用 `Exception` 一刀切 |
| W0718 顶层兜底 | 保留 2 处并加注释 | Streamlit 页面最外层的异常捕获保留 `except Exception`，标注 `# 顶层兜底：防止页面白屏` |
| W0612 未用变量 | 删除或 `_` | 若变量仅在赋值中使用 → 删除；若用于占位 → `_` |
| W0613 未用参数 | 加 `_` 前缀 | 回调函数签名保持接口兼容，不删除；Streamlit 事件回调尤其注意 |

## Risks / Trade-offs

- **[中风险]** W0718 误换：如果不区分场景全换成 `pymysql.Error`，文件操作/CSV 导入/类型转换场景的异常会漏接，程序直接崩溃。→ **已解决**：按数据库、文件、CSV、类型转换四类场景分别选择配套的异常类型。
- **[低风险]** 静态检查通过但异常捕获失效：`except ValueError` 无法捕获 `pymysql.Error`，反之亦然。→ **已解决**：验收增加功能边界测试（格式错误的 CSV 导入 + 断数据库连接），人工验证异常提示是否正常。
- **[低风险]** Streamlit 页面白屏：删除所有 `except Exception` 后某些未预料异常会导致无兜底。→ **已解决**：保留 2 处顶层 `except Exception`，加注释说明身份。

## 验收补充

静态检查之外，增加 2 项功能验证：
1. 手动导入格式错误的 CSV，观察错误提示是否正常弹出
2. 断开数据库连接后操作，观察是否能报错而非白屏崩溃

## Open Questions

- 无。
