"""工具函数"""

import os
import sys
import unicodedata


def _width(s):
    """字符串显示宽度：中文全角算2，英文半角算1"""
    return sum(2 if unicodedata.east_asian_width(c) in "WF" else 1 for c in s)


def _pad(s, w):
    """按显示宽度补空格"""
    return s + " " * (w - _width(s))


def cls():
    """清屏"""
    os.system("cls")
    # 备选：ANSI 强力清屏（Windows Terminal / PowerShell）
    sys.stdout.write("\033[2J\033[H")
    sys.stdout.flush()


def pause():
    """按回车继续 → 清屏"""
    sys.stdout.write("\n  按回车继续...")
    sys.stdout.flush()
    input()
    cls()


def hr():
    print("─" * 60)


def input_choice(prompt):
    sys.stdout.write(prompt)
    sys.stdout.flush()
    try:
        return int(input())
    except ValueError:
        return -1


def render_menu(conn, title, items, cols=2):
    """自动编号 + 分列排版 + 输入分发，返回 'quit' 表示退出"""
    cls()
    hr()
    print(f"  {title}")
    hr()
    for i, (label, _) in enumerate(items):
        print(f"  {i + 1:2}. {_pad(label, 16)}", end="")
        if (i + 1) % cols == 0:
            print()
    if len(items) % cols != 0:
        print()
    print("  0. 退出登录")
    hr()

    c = input_choice("  请选择: ")
    if c <= 0:
        return "quit"
    items[c - 1][1](conn)
    pause()


def confirm(prompt="确认？"):
    """回车/y->True，其他->False"""
    return input(f" {prompt} (Y/n): ").strip().lower() in ("", "y")


class Paginator:
    """分页器：只管切片和翻页，不管显示"""

    def __init__(self, rows, per_page=10):
        self.rows = rows
        self.per_page = per_page
        self.page = 0

    @property
    def items(self):
        start = self.page * self.per_page
        return self.rows[start : start + self.per_page]

    @property
    def total(self):
        return (len(self.rows) + self.per_page - 1) // self.per_page

    @property
    def info(self):
        return f"第 {self.page + 1}/{self.total} 页，共 {len(self.rows)} 条"

    def next(self):
        if self.page < self.total - 1:
            self.page += 1

    def prev(self):
        if self.page > 0:
            self.page -= 1

    def reset(self):
        self.page = 0


def show_table(headers, rows):
    """对齐打印表格，自动算列宽（兼容中文）"""
    if not rows:
        return
    str_rows = [[str(v) if v is not None else "" for v in row] for row in rows]
    widths = [
        max(_width(h), max(_width(r[i]) for r in str_rows))
        for i, h in enumerate(headers)
    ]

    hr()
    print("  " + "  ".join(_pad(h, w) for h, w in zip(headers, widths)))
    hr()
    for row in str_rows:
        print("  " + "  ".join(_pad(v, w) for v, w in zip(row, widths)))
    hr()
