"""工具函数"""
import os
import sys


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
