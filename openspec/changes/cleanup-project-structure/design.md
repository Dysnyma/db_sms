## Context

当前项目处于课程设计中期，目录结构是自然增长的，缺乏统一规范。现在重构成本较低（文件数量可控），是清理的最佳时机。

### 当前结构 vs 目标结构

```
当前                              目标
├── SQL/           (大写)   →    ├── sql/            (全小写)
├── code/          (非标)   →    ├── src/             (业界通用)
│   ├── app.py                 │   ├── app.py
│   ├── main.py                │   ├── main.py
│   ├── import_data.py         │   ├── import_data.py
│   ├── reset_data.py          │   ├── reset_data.py
│   ├── admin.py               │   ├── admin.py
│   ├── student.py             │   ├── student.py
│   ├── teacher.py             │   ├── teacher.py
│   ├── tester.py              │   ├── tester.py
│   └── core/                  │   └── core/
├── images/          →         ├── document/images/   (归入文档)
├── document/                  ├── document/
│   ├── 上交/           →      │   ├── submission/
│   ├── 报告/           →      │   ├── report/
│   │   ├── code/              │   │   ├── code/
│   │   ├── images/            │   │   ├── images/
│   │   └── 版本/       →      │   │   └── versions/
│   ├── 开发记录/        →      │   ├── dev-log/     (或合并)
│   ├── notes/                 │   ├── notes/
│   │   └── notes/     →      │   │   └── (内容上提)
│   └── references/            │   └── references/
├── archive/                   ├── archive/
├── backup/                    ├── backup/
├── data/                      ├── data/
├── test/                      ├── test/
└── images/ (根)               └── (移除)
```

## Goals / Non-Goals

**Goals:**
- 所有目录名统一全小写，单词间用连字符或下划线
- 消除中英文混用，中文目录名改为英文
- 消除冗余嵌套
- 更新所有受影响的路径引用

**Non-Goals:**
- 不重构 Python 代码内部逻辑
- 不修改数据库结构或 SQL 内容
- 不改变 `.gitignore` 之外的配置文件
- 不移动 `archive/`、`backup/`、`data/` 的内容

## Decisions

### D1: `code/` → `src/`

- **选择**：`src/` 而非 `app/`、`source/`、保持 `code/`
- **理由**：`src/` 是 Python/通用项目最普遍的源码目录命名，IDE 和工具链默认识别度高

### D2: 中文目录 → 英文

- **选择**：
  - `上交/` → `submission/`
  - `报告/` → `report/`
  - `版本/` → `versions/`
  - `开发记录/` → `dev-log/`
- **理由**：英文命名避免编码问题，GitHub 上更专业，跨平台无乱码风险

### D3: `document/notes/notes/` 冗余消除

- **选择**：将 `document/notes/notes/` 内容上提到 `document/notes/`
- **理由**：双层嵌套无意义，可能是手动整理时的误操作

### D4: `images/` 归入 `document/`

- **选择**：`images/` → `document/images/`
- **理由**：该目录仅含一个 ER 图 SVG，属于文档资源，归入 document 统一管理。报告相关的 images 已在 `document/report/images/` 中

### D5: 迁移方式

- **选择**：使用 `git mv` 进行所有重命名
- **理由**：Git 自动追踪重命名历史，无需手动 `git add` + `git rm`

## Risks / Trade-offs

- **[风险] 路径引用遗漏** → 用 `rg` 全局搜索 `code/`、`SQL/`、`images/` 等旧路径，确保全部更新
- **[风险] 中文路径名 git mv 失败** → Windows 下 Git Bash 对中文路径支持良好，但需注意引号转义
- **[风险] Python import 路径** → `code/` 下的模块间 import 使用的是相对/绝对 import 而非路径字符串，重命名目录不影响 import
- **[风险] `code/reset_data.py` 中硬编码 SQL 路径** → 这是唯一需要修改的 Python 文件
