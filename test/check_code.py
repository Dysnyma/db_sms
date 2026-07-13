"""
┌──────────────────────────────────────────────┐
│  学生成绩管理系统 · 代码质量体检工具           │
│  整合 Pylint + Flake8 + Black 三大工具         │
│  生成 Markdown 详细报告                        │
└──────────────────────────────────────────────┘

用法：
    python test/check_code.py                     # 检查 src/ 目录
    python test/check_code.py --target <路径>      # 检查指定路径
    python test/check_code.py --no-report         # 仅终端输出，不生成文件

输出：
    test/code_quality_report_<时间戳>.md          # 详细报告
"""

import os
import re
import sys
import json
import glob
import datetime
import subprocess
import argparse
from pathlib import Path


# ── 常量 ──────────────────────────────────────────────────────────
REPORT_DIR = Path(__file__).parent.absolute()
DEFAULT_TARGET = str(Path(__file__).parent.parent / "src")
PYTHON_EXT = ".py"
SEPARATOR = "-" * 60

# Flake8 错误码 → 中文描述（常见部分）
FLAKE8_CODE_DESC = {
    # PyFlakes (F)
    "F401": "模块/名称已导入但未使用",
    "F402": "同一行导入的模块与循环中的变量名冲突",
    "F403": "from X import * —— 不符合星号导入规范",
    "F404": "from __future__ 导入不在文件最顶部",
    "F405": "from X import * 后变量名可能未被定义",
    "F406": "from X import * 只能在模块顶层使用",
    "F407": "__future__ 特性名称未知",
    "F601": "字典中有重复的键",
    "F602": "字典推导式中有重复的键",
    "F621": "赋值表达式中存在语法歧义",
    "F622": "赋值表达式的目标无效",
    "F631": "assert 语句后永远为 True，可能是元组",
    "F632": "使用 is / is not 比较字面量（应与 == 区分）",
    "F701": "break 在循环之外",
    "F702": "continue 在循环之外",
    "F703": "continue 在 finally 块中",
    "F704": "yield 或 yield from 在函数之外",
    "F705": "return 在生成器之外",
    "F706": "return 在 finally 块中",
    "F707": "except 块缺少异常名（Python 2 语法）",
    "F811": "名称被重复定义",
    "F821": "使用了未定义的变量",
    "F822": "__all__ 中定义的名称在模块中不存在",
    "F823": "在函数作用域内引用了未赋值的局部变量",
    "F831": "参数列表中出现了重复的参数名",
    "F841": "局部变量被赋值但从未使用",
    "F842": "局部变量被注解但从未使用",
    "F901": "存在无法到达的代码",
    # pycodestyle (E / W)
    "E101": "缩进包含混合的空格和制表符",
    "E111": "缩进使用了 4 个空格以外的数量",
    "E112": "期望缩进的块",
    "E113": "意外的缩进",
    "E114": "注释使用了 4 个空格以外的缩进",
    "E115": "注释缩进的块期望缩进",
    "E116": "意外的注释缩进",
    "E117": "缩进过多",
    "E121": "续行缩进未使用区分/悬挂式缩进",
    "E122": "续行缩进过多或不足",
    "E123": "括号结束符位置不正确",
    "E124": "括号结束符缩进不匹配开头",
    "E125": "续行缩进与下一行的缩进相同",
    "E126": "续行缩进过多（>4 空格）",
    "E127": "续行缩进过多（垂直对齐）",
    "E128": "续行缩进不足",
    "E129": "视觉缩进的行与下一行相同",
    "E131": "续行缩进不一致",
    "E133": "括号结束符缩进错误",
    "E201": "左括号前有多余空格",
    "E202": "右括号后有多余空格",
    "E203": "冒号前有多余空格",
    "E211": "左括号前有多余空格",
    "E221": "运算符前有多余空格",
    "E222": "运算符后有多余空格",
    "E223": "分号前有多余空格",
    "E224": "分号后有多余空格",
    "E225": "运算符两侧缺少空格",
    "E226": "算术运算符两侧缺少空格",
    "E227": "位运算符两侧缺少空格",
    "E228": "模运算符两侧缺少空格",
    "E231": "逗号/分号/冒号后缺少空格",
    "E241": "逗号/分号后有多余空格",
    "E242": "制表符在逗号后",
    "E251": "等号参数前后有多余空格",
    "E252": "等号参数前后缺少空格",
    "E261": "注释前至少需两个空格",
    "E262": "注释中 # 后应有一个空格",
    "E265": "块注释 # 后应有一个空格",
    "E266": "块注释使用了三个 # 以上",
    "E271": "关键字后有多余空格",
    "E272": "关键字前有多余空格",
    "E273": "关键字后缺少空格",
    "E274": "关键字前缺少空格",
    "E275": "关键字后缺少空格",
    "E301": "需要 1 个空行（类方法间）",
    "E302": "需要 2 个空行（函数/类间）",
    "E303": "空行过多",
    "E304": "装饰器后需要空行",
    "E305": "函数/类后需要 2 个空行",
    "E306": "方法间需要 1 个空行",
    "E401": "多个导入写在同一行",
    "E402": "模块导入不在文件顶部",
    "E501": "行过长（> 最大长度）",
    "E502": "反斜杠续行冗余",
    "E701": "多条语句写在同一行（冒号分隔）",
    "E702": "多条语句写在同一行（分号分隔）",
    "E703": "行尾多余的分号",
    "E704": "单行函数定义",
    "E711": "与 None 比较应使用 is / is not",
    "E712": "布尔值比较应使用 is / is not",
    "E713": "not in 应使用成员测试",
    "E714": "is not 应使用身份测试",
    "E721": "不应直接使用 type() 比较类型",
    "E722": "不要使用裸 except",
    "E731": "不要使用赋值语句定义 lambda，改用 def",
    "E741": "不要使用单字母变量名 l / O / I",
    "E742": "不要将 l / O / I 作为函数名",
    "E743": "不要将 l / O / I 作为类名",
    "E901": "语法错误或 TokenError",
    "E902": "IO 错误",
    "W291": "行尾有多余空格",
    "W292": "文件末尾缺少换行",
    "W293": "空行有多余空格",
    "W391": "文件末尾有多余空行",
    "W503": "换行后二元运算符应放在行首",
    "W504": "换行后二元运算符应放在行尾",
    "W505": "文档字符串过长（> 最大长度）",
    "W601": "使用 has_key() 已被弃用",
    "W602": "使用 raise Exception, message 已被弃用",
    "W603": "使用 <> 而非 !=",
    "W604": "使用 backtick 而非 repr()",
    "W605": "字符串中存在无效的转义序列",
    "W606": "async 或 await 在 Python 3.5 之前",
}

# Pylint 消息类别 → 中文标签与严重程度
PYLINT_CATEGORIES = {
    "C": ("约定", "Convention", "🟢"),
    "W": ("警告", "Warning", "🟡"),
    "E": ("错误", "Error", "🔴"),
    "F": ("致命", "Fatal", "💀"),
    "R": ("重构", "Refactor", "🔵"),
}

# Pylint 消息码 → 中文描述（常见部分）
PYLINT_CODE_DESC = {
    "C0103": "名称不符合命名规范",
    "C0114": "缺少模块文档字符串",
    "C0115": "缺少类文档字符串",
    "C0116": "缺少函数文档字符串",
    "C0121": "单例比较应使用 is",
    "C0209": "格式化字符串应使用 f-string",
    "C0301": "行过长（> 最大行长度）",
    "C0302": "文件行数过多",
    "C0303": "行尾有多余空格",
    "C0304": "文件末尾缺少换行",
    "C0305": "文件末尾存在多余空行",
    "C0411": "导入顺序不规范",
    "C0412": "分组导入不规范",
    "C0413": "import 不在文件顶部",
    "C0415": "import 在函数/方法内部",
    "E0001": "语法错误",
    "E0011": "配置编译错误",
    "E0100": "__init__ 中调用了 super() 但未返回",
    "E0101": "函数中 return 返回了不一致的值",
    "E0102": "函数/方法被重复定义",
    "E0103": "类未被使用",
    "E0104": "函数中 return 和 yield 混用",
    "E0105": "类属性名错误",
    "E0106": "参数默认值为可变对象",
    "E0107": "字典推导式中存在星号",
    "E0108": "字典字面量中存在重复键",
    "E0110": "抽象类被实例化",
    "E0202": "类属性隐藏了继承的类方法",
    "E0203": "私有方法被外部访问",
    "E0211": "方法缺少 self 参数",
    "E0213": "方法参数顺序错误",
    "E0401": "无法导入模块",
    "E0402": "__init__ 外的相对导入",
    "E0601": "变量可能未定义",
    "E0602": "使用了未定义的变量",
    "E0603": "未定义的 __all__ 名",
    "E0604": "__all__ 中的值类型错误",
    "E0611": "模块中无此名称",
    "E0633": "未知的命名空间名称",
    "E0701": "raise 语句不是异常类",
    "E0702": "raise 语句中的异常类无效",
    "E0703": "except 的值不是异常类或基类",
    "E0704": "裸 raise 不在 except 块中",
    "E0710": "自定义异常不继承 BaseException",
    "E0711": "抛出的是 NotImplemented 而非 NotImplementedError",
    "E0712": "捕获的异常是 Exception 的子类",
    "E1003": "super() 的参数错误",
    "E1120": "函数调用缺少必选参数",
    "E1121": "函数调用参数过多",
    "E1123": "函数调用了意外的关键字参数",
    "E1124": "函数调用了重复的关键字参数",
    "E1125": "函数调用缺少必须的关键字参数",
    "E1126": "序列下标类型不正确",
    "E1127": "切片索引类型不正确",
    "E1128": "赋值的目标不是可写的",
    "E1129": "不支持的上下文管理器",
    "E1130": "isinstance / issubclass 参数不是类",
    "E1131": "不支持的操作数类型",
    "E1132": "不支持的格式字符",
    "E1133": "非可迭代对象用于迭代",
    "E1134": "不支持的成员测试操作",
    "E1135": "不支持 'not in' 操作",
    "E1136": "下标取值不支持",
    "E1137": "不支持通过下标赋值",
    "E1138": "不支持 del 操作",
    "E1140": "不支持键值解包",
    "E1141": "不支持解包操作",
    "E1205": "logging 格式字符串参数不足",
    "E1206": "logging 格式字符串参数过多",
    "F0010": "模块已损坏或语法错误",
    "F5400": "内置异常",
    "R0901": "类继承层次过深（> 7 层）",
    "R0902": "类的属性过多（> 20 个）",
    "R0903": "类中的公有方法过少（< 2 个）",
    "R0904": "类的公有方法过多（> 20 个）",
    "R0911": "函数中的 return 语句过多（> 6 个）",
    "R0912": "函数中的分支过多（> 12 个）",
    "R0913": "函数参数过多（> 5 个）",
    "R0914": "函数中的局部变量过多（> 15 个）",
    "R0915": "函数语句过多（> 50 条）",
    "R0916": "函数的布尔表达式过多（> 6 个）",
    "R1701": "存在重复代码块",
    "R1702": "嵌套过深（> 5 层）",
    "R1703": "if 分支中仅有 return，应简化",
    "R1704": "重新定义了外层名称",
    "R1705": "不必要的 else / elif 跟在 return 后",
    "R1706": "条件表达式可简化",
    "R1707": "逗号在元组中的位置错误",
    "R1708": "不必要的断言",
    "R1709": "不必要的 pass 语句",
    "R1710": "函数缺少 return 语句",
    "R1711": "函数返回值不一致",
    "R1712": "使用元组交换变量",
    "R1713": "使用 join 而非 + 拼接字符串",
    "R1714": "条件判断可简化为 in",
    "R1715": "使用 while 代替 for 循环",
    "R1716": "链式比较可简化",
    "R1720": "try 中没有 raise 语句",
    "R1721": "不必要的 enumerate 调用",
    "R1722": "使用 sys.exit 而非 exit",
    "R1723": "在 try 中如果所有分支都 return，不用 finally",
    "R1724": "在 if 中如果所有分支都 return，不用 else",
    "R1725": "使用 super() 无参数形式",
    "W0101": "存在无法到达的代码",
    "W0102": "参数默认值为可变对象（如 [] 或 {}）",
    "W0104": "语句似乎没有效果",
    "W0105": "字符串被用作注释（多余字符串）",
    "W0106": "列表推导式中的表达式没有效果",
    "W0107": "不必要的 pass 语句",
    "W0108": "不必要的 lambda 表达式",
    "W0109": "字典推导式中存在重复键",
    "W0111": "return 的类型不一致",
    "W0120": "循环体中没有 break 语句",
    "W0122": "使用了 exec 语句",
    "W0123": "使用了 eval 语句",
    "W0124": "未绑定的方法被调用",
    "W0125": "变量在条件表达式中被重复赋值",
    "W0141": "使用了 filter 等内置函数",
    "W0143": "使用了 map 等内置函数",
    "W0199": "assert 语句后跟元组（永远为真）",
    "W0201": "类属性在 __init__ 外定义",
    "W0212": "访问了 protected 成员",
    "W0221": "子类方法参数数量不匹配",
    "W0222": "子类方法参数签名不同",
    "W0223": "子类未实现抽象方法",
    "W0231": "__init__ 未调用父类 __init__",
    "W0233": "__init__ 未调用 super().__init__",
    "W0235": "super().__init__ 在类中无参数",
    "W0236": "类方法被覆写为实例方法",
    "W0237": "子类方法参数名不匹配",
    "W0238": "子类方法参数默认值不一致",
    "W0301": "不必要的分号",
    "W0401": "通配符导入（from X import *）",
    "W0404": "重新导入已有模块",
    "W0406": "模块导入自身",
    "W0407": "混用了 __import__",
    "W0410": "__future__ 导入不在最顶部",
    "W0511": "TODO / FIXME / XXX 标记未处理",
    "W0601": "使用了全局变量",
    "W0602": "全局变量在函数内部被赋值",
    "W0603": "在子例程中使用 global 语句",
    "W0604": "在 except 块中创建全局变量",
    "W0611": "导入但未使用的模块",
    "W0612": "定义了但未使用的变量",
    "W0613": "未使用的函数参数",
    "W0614": "通配符导入中未使用的名称",
    "W0621": "变量在外层作用域已定义",
    "W0622": "变量名与 Python 内置函数重名",
    "W0623": "重定义了循环变量",
    "W0631": "循环变量可能未定义",
    "W0632": "序列解包的变量数与序列长度不匹配",
    "W0702": "裸 except 语句",
    "W0703": "捕获了过于宽泛的 Exception",
    "W0706": "except 块中的异常链",
    "W0715": "except 块中 raise 的参数不正确",
    "W0716": "在 except 块中错误地使用了 raise",
    "W0717": "未使用的 try/except 块",
    "W0718": "捕获了 Exception 的子类",
    "W0719": "抛出的不是 Exception 的子类",
    "W1201": "logging 使用了 % 格式化",
    "W1202": "logging 使用了 format 字符串",
    "W1203": "logging 使用了 f-string",
    "W1300": "logging 格式字符串参数不匹配",
    "W1301": "logging 格式字符串引用不存在的位置",
    "W1401": "字符串中存在反斜杠转义",
    "W1402": "字符串中存在无效的转义序列",
    "W1403": "正则表达式字符串缺少 r 前缀",
    "W1404": "字符串中使用了隐式字符串拼接",
    "W1501": "使用了坏的文件模式",
    "W1502": "使用了不安全的 eval 或 exec",
    "W1503": "字典的 get() 方法被误用",
    "W1505": "使用了已弃用的模块或方法",
    "W1506": "使用了 subprocess 调用的 Popen",
    "W1507": "使用了 os.system 或 os.popen",
    "W1508": "使用了默认的 hash 方法",
    "W1509": "使用了 subprocess 的 shell=True",
    "W1510": "使用了 subprocess 的 shell=True",
}


def color(text, code):
    """终端颜色包装。"""
    return f"\033[{code}m{text}\033[0m"


def green(text):
    return color(text, "32")


def yellow(text):
    return color(text, "33")


def red(text):
    return color(text, "31")


def blue(text):
    return color(text, "34")


def bold(text):
    return color(text, "1")


# ── GBK/终端兼容输出 ─────────────────────────────────────────
# Windows 终端（cmd/PowerShell）默认 GBK，不支持 emoji
_CONSOLE_ENCODING = sys.stdout.encoding or "utf-8"
_IS_GBK = _CONSOLE_ENCODING.lower() in ("gbk", "gb2312", "gb18030")


def safe_emoji(emoji_char: str, fallback: str = "") -> str:
    """在 GBK 终端中替换 emoji 为安全字符。"""
    if _IS_GBK:
        return fallback
    return emoji_char


# 预定义的终端安全符号
E_STAR = safe_emoji("⭐", "*")
E_CHECK = safe_emoji("✅", "[OK]")
E_CROSS = safe_emoji("✗", "[X]")
E_WARN = safe_emoji("⚠️", "[!]")
E_FOLDER = safe_emoji("📁", "[DIR]")
E_CLOCK = safe_emoji("⏳", "[.]")
E_FIRE = safe_emoji("🔥", "!!")
E_CHART = safe_emoji("📊", "[#]")

# GBK 安全版 emoji 映射表，供 Markdown 报告使用（报告是 UTF-8 无此限制）
# 这里只处理终端输出部分


# ── 文件发现 ──────────────────────────────────────────────────────


def find_py_files(target: str) -> list[str]:
    """
    智能发现 .py 文件：
    - 目录 → 递归搜索
    - glob 模式 → 展开
    - 单个文件 → 直接返回
    """
    target = target.strip().strip("'\"")
    files = []

    if os.path.isfile(target) and target.endswith(PYTHON_EXT):
        return [os.path.normpath(target)]

    if os.path.isdir(target):
        for root, _, filenames in os.walk(target):
            for fn in filenames:
                if fn.endswith(PYTHON_EXT) and fn != "tempCodeRunnerFile.py":
                    files.append(os.path.normpath(os.path.join(root, fn)))
        return sorted(files)

    # glob 模式（如 ../*.py）
    matches = glob.glob(target)
    for m in matches:
        if m.endswith(PYTHON_EXT):
            files.append(os.path.normpath(m))
    return sorted(files)


# ── 命令执行 ──────────────────────────────────────────────────────


def run_tool(
    cmd_parts: list[str], title: str, timeout: int = 120
) -> dict:
    """
    安全执行外部命令，返回结构化的结果。

    Returns
        {"ok": bool, "stdout": str, "stderr": str, "combined": str, "tool_missing": bool}
    """
    sys.stdout.write(f"  {E_CLOCK} {title} ... ")
    sys.stdout.flush()
    try:
        result = subprocess.run(
            cmd_parts,
            shell=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
        )
        combined = (result.stdout or "") + (result.stderr or "")
        sys.stdout.write(green("OK\n"))
        sys.stdout.flush()
        return {
            "ok": result.returncode == 0,
            "stdout": result.stdout or "",
            "stderr": result.stderr or "",
            "combined": combined,
            "tool_missing": "not found" in combined.lower()
            or "no module named" in combined.lower(),
        }
    except FileNotFoundError:
        sys.stdout.write(red(f"{E_CROSS} (工具未安装)\n"))
        sys.stdout.flush()
        return {
            "ok": False,
            "stdout": "",
            "stderr": f"工具 '{cmd_parts[0]}' 未安装。请运行: pip install {cmd_parts[0]}",
            "combined": f"工具 '{cmd_parts[0]}' 未安装",
            "tool_missing": True,
        }
    except subprocess.TimeoutExpired:
        sys.stdout.write(red(f"{E_CROSS} (超时 {timeout}s)\n"))
        sys.stdout.flush()
        return {
            "ok": False,
            "stdout": "",
            "stderr": f"执行超时（{timeout} 秒）",
            "combined": f"执行超时（{timeout} 秒）",
            "tool_missing": False,
        }
    except Exception as e:
        sys.stdout.write(red(f"{E_CROSS}\n"))
        sys.stdout.flush()
        return {
            "ok": False,
            "stdout": "",
            "stderr": str(e),
            "combined": str(e),
            "tool_missing": False,
        }


# ── Pylint 解析 ───────────────────────────────────────────────────


def parse_pylint(text: str) -> dict:
    """
    解析 Pylint 输出：
    - 评分
    - 消息列表（文件、行、类别、消息码、描述）
    - 按类别计数的统计
    """
    result = {
        "score": None,
        "messages": [],
        "counts": {"C": 0, "W": 0, "E": 0, "F": 0, "R": 0},
        "by_file": {},
    }

    # 提取评分：Your code has been rated at X.XX/10
    score_match = re.search(
        r"Your code has been rated at\s+([\d\.\-]+)/10", text
    )
    if score_match:
        result["score"] = float(score_match.group(1))

    # 解析每一条消息
    # 格式：file:line:col: category: message-code: message
    # 跳过：************* Module xxx 等非消息行
    pattern = re.compile(
        r"^([^:]+):(\d+):(\d+):\s*([CWEFR]\d+):\s*(.+)$", re.MULTILINE
    )
    for m in pattern.finditer(text):
        raw_file = m.group(1).strip()
        # 跳过模块头伪文件（如 "************* Module admin"）
        if raw_file.startswith("***"):
            continue
        if raw_file in ("", " "):
            continue
        # 跳过评分统计行
        if raw_file.startswith("Your code") or raw_file.startswith("Report"):
            continue

        filepath = os.path.normpath(raw_file)
        line = int(m.group(2))
        col = int(m.group(3))
        code = m.group(4).strip()
        msg = m.group(5).strip()
        cat = code[0]

        entry = {
            "file": filepath,
            "line": line,
            "col": col,
            "code": code,
            "category": cat,
            "description": PYLINT_CODE_DESC.get(code, msg),
            "raw": f"{code}: {msg}",
        }
        result["messages"].append(entry)

        if cat in result["counts"]:
            result["counts"][cat] += 1

        # 按文件分组
        if filepath not in result["by_file"]:
            result["by_file"][filepath] = {
                "total": 0, "C": 0, "W": 0, "E": 0, "F": 0, "R": 0}
        result["by_file"][filepath]["total"] += 1
        result["by_file"][filepath][cat] += 1

    return result


# ── Flake8 解析 ───────────────────────────────────────────────────


def parse_flake8(text: str) -> dict:
    """
    解析 Flake8 输出：
    - 消息列表（文件、行、列、错误码、描述）
    - 按文件统计
    - 按类型统计（F/E/W）

    Flake8 输出格式:
        path/file.py:line:col: CODE description
    注意 Windows 路径含盘符（E:），不能用简单 split(":") 处理。
    """
    result = {
        "total": 0,
        "messages": [],
        "by_file": {},
        "by_code": {},
    }

    if not text.strip():
        return result

    # 格式: 盘符可选 + 路径 + :行号 + :列号 + : + 错误码 + 描述
    # 用 regex 正确识别 Windows/Unix 路径
    # 组: 1=完整路径, 2=行号, 3=列号, 4=错误码, 5=描述
    pattern = re.compile(
        r"^([A-Za-z]:)?([^:]+?):(\d+):(\d+):\s+([A-Z]\d{3})\s+(.+?)$"
    )
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        m = pattern.match(line)
        if not m:
            continue

        drive = m.group(1) or ""
        path_part = m.group(2)
        filepath = os.path.normpath(drive + path_part)
        lineno = int(m.group(3))
        colno = int(m.group(4))
        code = m.group(5)
        desc_raw = m.group(6).strip()

        description = FLAKE8_CODE_DESC.get(code, desc_raw)
        cat = code[0] if code else "?"

        entry = {
            "file": filepath,
            "line": lineno,
            "col": colno,
            "code": code,
            "category": cat,
            "description": description,
            "raw": line,
        }
        result["messages"].append(entry)
        result["total"] += 1

        if filepath not in result["by_file"]:
            result["by_file"][filepath] = 0
        result["by_file"][filepath] += 1

        if code not in result["by_code"]:
            result["by_code"][code] = {
                "count": 0, "description": description, "category": cat}
        result["by_code"][code]["count"] += 1

    return result


# ── Black 解析 ────────────────────────────────────────────────────


def parse_black(text: str) -> dict:
    """
    解析 Black --check --diff 输出：
    - 会改写的文件列表
    - 每个文件的 diff hunk 数
    - 总体判断（通过/未通过）

    Black diff 格式:
        --- src\file.py\t2026-07-09 10:19:53...
        +++ src\file.py\t2026-07-13 05:43:05...
        @@ ... @@
    """
    result = {
        "would_reformat": [],
        "already_formatted": [],
        "total_files_changed": 0,
        "by_file": {},
    }

    if not text.strip():
        result["status"] = "all_good"
        return result

    # Black 输出的 diff 格式：
    # --- src/file.py\t2026-07-09 10:19:53...
    # +++ src/file.py\t2026-07-13 05:43:05...
    # @@ ... @@
    current_file = None
    for line in text.splitlines():
        line_stripped = line.strip()
        if line_stripped.startswith("--- "):
            # 提取路径: "--- src\file.py\t2026..." → "src\file.py"
            rest = line_stripped[4:]  # 去掉 "--- "
            # 去掉时间戳（tab 后的内容）
            if "\t" in rest:
                rest = rest.split("\t")[0]
            current_file = rest.strip()
        elif line_stripped.startswith("@@") and current_file:
            if current_file not in result["by_file"]:
                result["by_file"][current_file] = 0
                result["would_reformat"].append(current_file)
            if "@@" in line_stripped:
                result["by_file"][current_file] += 1

    # 如果输出中有 "would reformat" 统计行
    would_match = re.search(
        r"(\d+)\s+file[s]?\s+(?:would\s+)?be\s+reformatted", text)
    if would_match:
        result["total_files_changed"] = int(would_match.group(1))

    # 检测状态
    if result["would_reformat"]:
        result["status"] = "changes_needed"
    elif "All done" in text or "already formatted" in text:
        result["status"] = "all_good"
    else:
        result["status"] = "all_good" if result["total_files_changed"] == 0 else "changes_needed"

    return result


# ── 报告生成 ──────────────────────────────────────────────────────


def fmt_score(score: float | None) -> str:
    """Pylint 评分转带颜色/表情的字符串。"""
    if score is None:
        return "N/A"
    if score >= 9.0:
        return f"🟢 {score:.2f}/10 (优秀)"
    elif score >= 7.0:
        return f"🟡 {score:.2f}/10 (一般)"
    elif score >= 5.0:
        return f"🟠 {score:.2f}/10 (待改进)"
    else:
        return f"🔴 {score:.2f}/10 (急需改进)"


def generate_report(
    target: str,
    files_found: list[str],
    pylint_result: dict,
    pylint_parsed: dict,
    flake8_result: dict,
    flake8_parsed: dict,
    black_result: dict,
    black_parsed: dict,
) -> str:
    """生成完整的 Markdown 报告。"""
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    basename = os.path.basename(target) if os.path.isdir(target) else target

    # ── 统计汇总 ──
    pylint_issues = sum(pylint_parsed["counts"].values())
    flake8_issues = flake8_parsed["total"]
    black_changed = black_parsed["total_files_changed"]
    total_issues = pylint_issues + flake8_issues

    # 严重问题（Pylint E/F + Flake8 F 类）
    severe = (
        pylint_parsed["counts"]["E"]
        + pylint_parsed["counts"]["F"]
        + sum(
            1 for m in flake8_parsed["messages"] if m.get("code", "").startswith("F")
        )
    )

    # 评分
    score_str = fmt_score(pylint_parsed["score"])
    score_simple = f"{pylint_parsed['score']:.2f}" if pylint_parsed["score"] is not None else "N/A"

    # ── 严重程度评估 ──
    if severe > 0:
        severity_emoji = "🔴"
        severity_label = "存在严重问题，建议优先修复"
    elif pylint_parsed["score"] is not None and pylint_parsed["score"] < 7:
        severity_emoji = "🟠"
        severity_label = "代码质量一般，建议有计划地改进"
    elif pylint_parsed["score"] is not None and pylint_parsed["score"] < 9:
        severity_emoji = "🟡"
        severity_label = "代码质量尚可，仍有一些改进空间"
    else:
        severity_emoji = "🟢"
        severity_label = "代码质量良好，继续保持"

    # ── 构建报告 ──
    lines = []
    _w = lines.append  # shorthand

    _w(f"# 🔍 代码质量体检报告")
    _w("")
    _w(f"> **学生成绩管理系统** · 综合代码质量分析")
    _w("")
    _w("| 项目 | 值 |")
    _w("|------|-----|")
    _w(f"| **生成时间** | {now} |")
    _w(f"| **检查目标** | `{target}` |")
    _w(f"| **Python 文件数** | {len(files_found)} |")
    _w(f"| **代码总行数** | {_count_lines(files_found)} |")
    _w(f"| **检查工具** | Pylint + Flake8 + Black |")
    _w("")
    _w("---")
    _w("")

    # ════════════════════════════════════════════════════════════
    #  1. 执行摘要
    # ════════════════════════════════════════════════════════════
    _w("## 📊 执行摘要")
    _w("")
    _w("| 维度 | 结果 |")
    _w("|------|------|")
    _w(f"| **Pylint 评分** | {score_str} |")
    _w(f"| **Pylint 问题总数** | {pylint_issues} 条 |")
    _w(f"| **Flake8 问题总数** | {flake8_issues} 条 |")
    _w(f"| **Black 格式检查** | {'✅ 全部通过' if black_parsed.get('status') == 'all_good' else f'⚠️ {black_changed} 个文件需格式化'} |")
    _w(f"| **严重问题数** | {severe} |")
    _w(f"| **总体评估** | {severity_emoji} {severity_label} |")
    _w("")

    if pylint_issues + flake8_issues == 0:
        _w("> 🎉 **恭喜！未发现任何代码问题，代码质量非常优秀！**")
        _w("")

    # ════════════════════════════════════════════════════════════
    #  2. 各类问题统计
    # ════════════════════════════════════════════════════════════
    _w("## 📈 问题分类统计")
    _w("")

    # 2a. Pylint 类别分布
    cats = pylint_parsed["counts"]
    pylint_cat_total = sum(cats.values())
    if pylint_cat_total > 0:
        _w("### 2.1 Pylint 问题类别分布")
        _w("")
        _w("| 类别 | 数量 | 占比 | 说明 |")
        _w("|------|------|------|------|")
        for cat_code in ["C", "W", "E", "F", "R"]:
            label, _, emoji = PYLINT_CATEGORIES[cat_code]
            count = cats.get(cat_code, 0)
            if count > 0:
                pct = count / pylint_cat_total * 100
                _w(
                    f"| {emoji} **{label}** ({cat_code}) | {count} | {pct:.1f}% | "
                    f"{_pylint_cat_explain(cat_code)} |"
                )
        _w("")

    # 2b. Flake8 类别分布
    if flake8_issues > 0:
        _w("### 2.2 Flake8 问题类别分布")
        _w("")
        f8_cats = {}
        for m in flake8_parsed["messages"]:
            c = m.get("category", "?")
            f8_cats[c] = f8_cats.get(c, 0) + 1
        _w("| 类别 | 数量 | 说明 |")
        _w("|------|------|------|")
        f8_cat_names = {"E": "pycodestyle 格式",
                        "W": "pycodestyle 警告", "F": "PyFlakes 逻辑"}
        for code in ["F", "E", "W"]:
            if code in f8_cats:
                _w(f"| **{f8_cat_names.get(code, code)}** ({code}) | {f8_cats[code]} | "
                   f"{'🔴 可能为逻辑错误' if code == 'F' else '🟡 格式规范'} |")
        _w("")

    # 2c. Top 问题类型
    if flake8_parsed["by_code"]:
        _w("### 2.3 Flake8 最高频问题 TOP 10")
        _w("")
        sorted_codes = sorted(
            flake8_parsed["by_code"].items(), key=lambda x: -x[1]["count"]
        )[:10]
        _w("| 错误码 | 出现次数 | 描述 |")
        _w("|--------|----------|------|")
        for code, info in sorted_codes:
            _w(f"| {code} | {info['count']} | {info['description']} |")
        _w("")

    # ════════════════════════════════════════════════════════════
    #  3. Pylint 详情
    # ════════════════════════════════════════════════════════════
    _w("---")
    _w("")
    _w("## 1. Pylint — 代码规范检查")
    _w("")
    _w(f"**评分**: {score_str}")
    _w("")

    if pylint_result.get("tool_missing"):
        _w(f"> ⚠️ Pylint 未安装，跳过分析。运行 `pip install pylint` 后重试。")
        _w("")
    elif pylint_result.get("ok") and not pylint_parsed["messages"]:
        _w("> ✅ **完美！Pylint 未发现任何代码规范问题。**")
        _w("")
    else:
        # 文件级别概览
        if pylint_parsed["by_file"]:
            _w("### 文件问题分布")
            _w("")
            _w("| 文件 | 总计 | C(约定) | W(警告) | E(错误) | R(重构) |")
            _w("|------|------|---------|---------|---------|---------|")
            sorted_files = sorted(
                pylint_parsed["by_file"].items(), key=lambda x: -x[1]["total"]
            )
            for fpath, counts in sorted_files:
                rel = _rel_path(fpath)
                _w(f"| `{rel}` | {counts['total']} | {counts['C']} | {counts['W']} | "
                   f"{counts['E']} | {counts['R']} |")
            _w("")

        _w("### 详细问题列表")
        _w("")
        _w("| 文件 | 行 | 消息码 | 类别 | 描述 |")
        _w("|------|-----|--------|------|------|")
        for msg in pylint_parsed["messages"]:
            _, _, emoji = PYLINT_CATEGORIES.get(msg["category"], ("", "", "❓"))
            rel = _rel_path(msg["file"])
            _w(f"| `{rel}` | {msg['line']} | `{msg['code']}` | {emoji} | {msg['description']} |")
        _w("")

    # ════════════════════════════════════════════════════════════
    #  4. Flake8 详情
    # ════════════════════════════════════════════════════════════
    _w("---")
    _w("")
    _w("## 2. Flake8 — 语法与风格检查")
    _w("")
    _w(f"**发现问题**: {flake8_issues} 条")
    _w("")

    if flake8_result.get("tool_missing"):
        _w(f"> ⚠️ Flake8 未安装，跳过分析。运行 `pip install flake8` 后重试。")
        _w("")
    elif flake8_issues == 0:
        _w("> ✅ **完美！Flake8 未发现任何语法或风格问题。**")
        _w("")
    else:
        # 文件级别概览
        if flake8_parsed["by_file"]:
            _w("### 文件问题分布")
            _w("")
            _w("| 文件 | 问题数 |")
            _w("|------|--------|")
            sorted_files = sorted(
                flake8_parsed["by_file"].items(), key=lambda x: -x[1]
            )
            for fpath, cnt in sorted_files:
                _w(f"| `{_rel_path(fpath)}` | {cnt} |")
            _w("")

        _w("### 详细问题列表")
        _w("")
        _w("| 文件 | 行 | 列 | 错误码 | 类别 | 描述 |")
        _w("|------|-----|-----|--------|------|------|")
        for msg in flake8_parsed["messages"]:
            cat_label = {"F": "🔴 PyFlakes", "E": "🟡 格式", "W": "🔵 警告"}.get(
                msg.get("category", ""), "❓"
            )
            rel = _rel_path(msg["file"])
            _w(f"| `{rel}` | {msg['line']} | {msg['col']} | `{msg['code']}` | {cat_label} | {msg['description']} |")
        _w("")

    # ════════════════════════════════════════════════════════════
    #  5. Black 详情
    # ════════════════════════════════════════════════════════════
    _w("---")
    _w("")
    _w("## 3. Black — 代码格式一致性检查")
    _w("")

    if black_result.get("tool_missing"):
        _w(f"> ⚠️ Black 未安装，跳过分析。运行 `pip install black` 后重试。")
        _w("")
    elif black_parsed.get("status") == "all_good":
        _w("> ✅ **格式完美！所有文件均符合 Black 格式标准。**")
        _w("")
    elif black_parsed["would_reformat"] or black_parsed["total_files_changed"] > 0:
        change_count = max(
            black_parsed["total_files_changed"],
            len(black_parsed["would_reformat"])
        )
        _w(f"> ⚠️ **发现 {change_count} 个文件** 不符合 Black 格式标准。")
        _w("")
        _w("### 需要格式化的文件")
        _w("")
        _w("| 文件 | 需要修改的块数 |")
        _w("|------|----------------|")
        for fpath, hunks in black_parsed["by_file"].items():
            _w(f"| `{_rel_path(fpath)}` | {hunks} 处 |")
        _w("")
        _w("> 💡 **自动修复**: 运行 `black .` 即可自动格式化所有文件。")
        _w("")
    else:
        _w("> ℹ️ 格式检查完成，无异常。")
        _w("")

    # ════════════════════════════════════════════════════════════
    #  6. 改进建议
    # ════════════════════════════════════════════════════════════
    if total_issues > 0:
        _w("---")
        _w("")
        _w("## 💡 改进建议")
        _w("")

        recommendations = []

        # 根据问题类型给出针对性建议
        if pylint_parsed["counts"]["C"] > 10:
            recommendations.append(
                "🔵 **命名与文档规范**：大量 Convention 类问题，建议统一添加模块/函数/类文档字符串，"
                "并检查命名是否符合 PEP 8 规范。"
            )
        if pylint_parsed["counts"]["R"] > 5:
            recommendations.append(
                "🔵 **代码重构**：存在较多 Refactor 建议，可考虑简化复杂函数、减少嵌套、"
                "消除重复代码。"
            )
        if pylint_parsed["counts"]["W"] > 5:
            recommendations.append(
                "🟡 **潜在问题修复**：Warning 类问题应优先处理，特别是未使用的导入、"
                "未使用的变量、以及重定义名称等。"
            )
        if pylint_parsed["counts"]["E"] > 0 or pylint_parsed["counts"]["F"] > 0:
            recommendations.append(
                "🔴 **严重错误修复**：Error 和 Fatal 类问题必须立即修复，可能影响程序运行。"
            )
        if any(m.get("code", "").startswith("F") for m in flake8_parsed["messages"]):
            recommendations.append(
                "🔴 **Flake8 逻辑错误**：PyFlakes 检测到的问题可能为实际代码错误，"
                "请逐一排查。"
            )
        if black_parsed["would_reformat"]:
            recommendations.append(
                "⚫ **格式统一**：运行 `black .` 自动格式化所有文件，统一代码风格。"
            )
        if total_issues > 50:
            recommendations.append(
                "📋 **逐步改进**：问题较多时，建议先修复严重问题（E/F 类），"
                "再处理警告和重构建议。"
            )

        # 软件工程建议
        if len(files_found) > 0:
            recommendations.append(
                "🧪 **添加类型注解**：考虑在函数签名中添加类型注解（type hints），"
                "配合 mypy 进一步提升代码健壮性。"
            )

        for rec in recommendations:
            _w(f"- {rec}")
            _w("")

    # ════════════════════════════════════════════════════════════
    #  7. 脚注
    # ════════════════════════════════════════════════════════════
    _w("---")
    _w("")
    _w("## ℹ️ 关于本报告")
    _w("")
    _w("| 工具 | 版本 | 用途 |")
    _w("|------|------|------|")
    _w(f"| **Pylint** | {_get_tool_version('pylint')} | 代码规范、命名、复杂度检查 |")
    _w(f"| **Flake8** | {_get_tool_version('flake8')} | PEP 8 风格 + PyFlakes 逻辑检查 |")
    _w(f"| **Black** | {_get_tool_version('black')} | 代码格式自动格式化规范 |")
    _w("")
    _w(f"*报告由 `check_code.py` 自动生成 · {now}*")
    _w("")

    return "\n".join(lines)


def _pylint_cat_explain(cat: str) -> str:
    """Pylint 类别的简短说明。"""
    explanations = {
        "C": "命名规范、文档字符串等约定性问题",
        "W": "潜在 bug 和不良实践",
        "E": "代码错误或导入失败",
        "F": "阻止程序继续分析的致命错误",
        "R": "代码可读性、可维护性重构建议",
    }
    return explanations.get(cat, "")


def _rel_path(path: str) -> str:
    """将绝对路径转为相对路径（相对于项目根或简洁显示）。"""
    # 尝试转为相对于脚本所在目录
    try:
        rel = os.path.relpath(path, str(REPORT_DIR))
        if not rel.startswith(".."):
            return rel
    except ValueError:
        pass
    # 尝试转为相对于项目根
    project_root = REPORT_DIR.parent
    try:
        rel = os.path.relpath(path, str(project_root))
        return rel
    except ValueError:
        pass
    return path


def _count_lines(files: list[str]) -> int:
    """统计文件总行数。"""
    total = 0
    for f in files:
        try:
            with open(f, "r", encoding="utf-8", errors="ignore") as fh:
                total += sum(1 for _ in fh)
        except Exception:
            pass
    return total


def _get_tool_version(name: str) -> str:
    """获取工具版本号。"""
    try:
        result = subprocess.run(
            [name, "--version"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        out = (result.stdout or result.stderr or "").strip()
        # 提取版本号（第一个数字）
        v_match = re.search(r"(\d+\.\d+\.\w+)", out)
        if v_match:
            return v_match.group(1)
        return out.split(",")[0] if out else "?"
    except Exception:
        return "?"


# ── 主流程 ──────────────────────────────────────────────────────


def main():
    parser = argparse.ArgumentParser(
        description="学生成绩管理系统 · 代码质量体检工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "示例:\n"
            f"  python test/check_code.py                     # 默认检查 {DEFAULT_TARGET}\n"
            "  python test/check_code.py --target src/app.py  # 检查单个文件\n"
            "  python test/check_code.py --no-report          # 仅终端输出\n"
        ),
    )
    parser.add_argument(
        "--target",
        default=DEFAULT_TARGET,
        help=f"检查目标文件/目录（默认: {DEFAULT_TARGET}）",
    )
    parser.add_argument(
        "--no-report",
        action="store_true",
        help="不生成 Markdown 报告文件，仅终端输出",
    )
    args = parser.parse_args()

    target = os.path.abspath(args.target)
    no_report = args.no_report

    print()
    print(bold("+----------------------------------------------+"))
    print(bold("|   学生成绩管理系统 - 代码质量体检工具         |"))
    print(bold("+----------------------------------------------+"))
    print(f"  目标目录: {target}")
    print()

    # ── 发现文件 ──
    files = find_py_files(target)
    if not files:
        print(red(f"  {E_CROSS} 未找到 .py 文件: {target}"))
        sys.exit(1)

    total_lines = _count_lines(files)
    print(f"  {E_FOLDER} 发现 {len(files)} 个 Python 文件（共 {total_lines} 行）")
    for f in files:
        rel = _rel_path(f)
        print(f"     - {rel}")
    print()
    print(SEPARATOR)
    print()

    # ── 执行三工具 ──
    # 构建排除 tempCodeRunnerFile.py 的参数
    black_targets = [f for f in files if "tempCodeRunnerFile" not in f]

    pylint_result = run_tool(
        ["pylint"] + files + ["--rcfile=", "-rn"],
        "Pylint  代码规范检查",
    )
    flake8_result = run_tool(
        ["flake8"] + files + ["--max-line-length=120"],
        "Flake8  语法与风格检查",
    )
    black_result = run_tool(
        ["black", "--check", "--diff"] + black_targets,
        "Black   格式一致性检查",
    )

    print()
    print(SEPARATOR)
    print()

    # ── 解析输出 ──
    pylint_parsed = parse_pylint(pylint_result["combined"])
    flake8_parsed = parse_flake8(flake8_result["combined"])
    black_parsed = parse_black(black_result["combined"])

    # ── 终端摘要 ──
    _print_terminal_summary(pylint_parsed, flake8_parsed, black_parsed)

    # ── 生成报告 ──
    if not no_report:
        report = generate_report(
            target=target,
            files_found=files,
            pylint_result=pylint_result,
            pylint_parsed=pylint_parsed,
            flake8_result=flake8_result,
            flake8_parsed=flake8_parsed,
            black_result=black_result,
            black_parsed=black_parsed,
        )

        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = REPORT_DIR / f"code_quality_report_{timestamp}.md"
        with open(report_file, "w", encoding="utf-8") as f:
            f.write(report)

        print(green(f"  {E_CHECK} 详细报告已生成: {report_file}"))
        print()

        # 尝试打开报告（仅在 Windows 上）
        try:
            os.startfile(str(report_file))
        except Exception:
            pass
    else:
        print("  （已跳过报告文件生成）")


def _print_terminal_summary(
    pylint_parsed: dict,
    flake8_parsed: dict,
    black_parsed: dict,
):
    """在终端输出简洁的检查摘要。"""
    pylint_issues = sum(pylint_parsed["counts"].values())
    flake8_issues = flake8_parsed["total"]
    black_changed = len(black_parsed.get("would_reformat", []))

    print(bold(f"  {E_CHART} 检查结果摘要"))
    print(f"  {'─' * 50}")

    # Pylint
    score = pylint_parsed["score"]
    if score is not None:
        score_color = green if score >= 9 else (yellow if score >= 7 else red)
        print(
            f"  Pylint  评分: {score_color(f'{score:.2f}/10')}    问题数: {pylint_issues}")
    else:
        print(f"  Pylint  评分: N/A    问题数: {pylint_issues}")
    cats = pylint_parsed["counts"]
    parts = []
    for c in ["F", "E", "W", "C", "R"]:
        if cats.get(c, 0) > 0:
            label, _, _ = PYLINT_CATEGORIES.get(c, ("?", "?", "?"))
            parts.append(f"{label}={cats[c]}")
    if parts:
        print(f"          ({', '.join(parts)})")

    # Flake8
    flake_color = green if flake8_issues == 0 else yellow
    print(f"  Flake8  问题数: {flake_color(str(flake8_issues))}")
    f8_cats_display = {}
    for m in flake8_parsed.get("messages", []):
        c = m.get("category", "?")
        f8_cats_display[c] = f8_cats_display.get(c, 0) + 1
    if f8_cats_display:
        f8_parts = [f"{k}={v}" for k, v in sorted(f8_cats_display.items())]
        print(f"          ({', '.join(f8_parts)})")

    # Black
    if black_parsed.get("status") == "all_good":
        print(f"  Black   格式: {E_CHECK} 全部通过")
    elif black_changed > 0:
        print(f"  Black   格式: {E_WARN} {black_changed} 个文件需格式化")
    else:
        print(f"  Black   格式: {E_CHECK} 通过")

    print(f"  {'─' * 50}")
    print()


if __name__ == "__main__":
    main()
