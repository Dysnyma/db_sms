## Why

`batch_grade_page` 中批量导入完成后，结果提示通过 `st.toast()` + `st.rerun()` 展示。但 `st.toast()` 会在几秒后自动消失，加上页面刷新后用户视线尚未聚焦，提示经常一闪而过，用户来不及看清成功/失败条数。

## What Changes

- 将 `batch_grade_page` 中的 `st.toast(m, icon="✅")` 替换为 `st.success(m)`，使结果提示持续显示在页面上，直到用户下次交互
- 同时在 `grade_input_page` 中做同样替换，保持单条录入和批量录入的体验一致

## Capabilities

### New Capabilities

- （无新能力）

### Modified Capabilities

- （无规格级别变更）

## Impact

- 涉及 1 个文件：`src/app.py` 中 2 处 `st.toast()` → `st.success()`
- 无逻辑变更，仅 UI 展示方式改变
