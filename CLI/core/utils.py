"""工具函数"""
import os
import sys
import unicodedata


def _width(s):
    """字符串显示宽度：中文全角算2，英文半角算1"""
    return sum(2 if unicodedata.east_asian_width(c) in 'WF' else 1 for c in s)


def _pad(s, w):
    """按显示宽度补空格"""
    return s + ' ' * (w - _width(s))


def cls():
    """清屏"""
    os.system('cls')
    # 备选：ANSI 强力清屏（Windows Terminal / PowerShell）
    sys.stdout.write('\033[2J\033[H')
    sys.stdout.flush()


def pause():
    """按回车继续 → 清屏"""
    sys.stdout.write('\n  按回车继续...')
    sys.stdout.flush()
    input()
    cls()


def hr():
    print('─' * 60)


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
    print(f'  {title}')
    hr()
    for i, (label, _) in enumerate(items):
        print(f'  {i+1:2}. {_pad(label, 16)}', end='')
        if (i + 1) % cols == 0:
            print()
    if len(items) % cols != 0:
        print()
    print('  0. 退出登录')
    hr()

    c = input_choice('  请选择: ')
    if c <= 0:
        return 'quit'
    items[c-1][1](conn)
    pause()
