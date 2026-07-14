## Why

使用中发现两个影响体验的稳定问题：

1. **SQL 恢复无反馈**：点击"确认恢复"按钮后页面没有任何反应——不报错、不成功、不提示，用户不知道发生了什么。
2. **输入校验缺失**：学分等数字字段可以输入非法值（如 1000），显示"修改成功"但没有真正写入数据库，用户被虚假的成功提示误导。

## What Changes

### 问题 1：SQL 恢复无反馈

- 为 `restore_page` 的 `subprocess.run` 添加 try/except 保护
- `mysql` 命令找不到时提示"请确保 MySQL 已安装"
- 成功时明确显示绿色成功消息并清除 session_state
- 失败时显示红色错误消息（MySQL 具体报错）

### 问题 2：统一输入校验

| 字段 | 当前 | 改为 |
|------|------|------|
| 学分（新增+修改） | ✅ 已修（number_input 0~20） | 确认无误 |
| 成绩录入 | ✅ 已修（float 转换保护） | 确认无误 |
| 班级管理新增/修改/删除 | `text_input` + 无 try | 加 try/except，操作失败给反馈 |
| 教师管理新增/修改/删除 | `text_input` + 无 try | 加 try/except，操作失败给反馈 |
| 学生管理修改/删除 | 部分有 try | 补齐缺失的 try/except |
| 排课管理删除 | 无 try | 加 try/except |
| 选课管理退选 | 无 try | 加 try/except |

## Capabilities

### New Capabilities

- `input-validation`: 全页面输入校验和操作反馈统一化
- `restore-feedback`: SQL 恢复操作的完整错误/成功反馈

### Modified Capabilities

- （无）

## Impact

- 涉及 1 个文件：`src/pages/admin_page.py`
- 全是 try/except 包装，不改业务逻辑
