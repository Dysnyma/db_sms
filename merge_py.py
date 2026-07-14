#!/usr/bin/env python3
"""将 src/ 下所有 .py 文件合并为一个 txt 文件（排除虚拟环境和临时文件）。"""

import os

SRC_DIR = "src"
OUTPUT_FILE = "all_py_files_merged.txt"
EXCLUDE = {"tempCodeRunnerFile.py"}


def main():
    py_files = []
    for root, dirs, files in os.walk(SRC_DIR):
        for f in files:
            if f.endswith(".py") and f not in EXCLUDE:
                py_files.append(os.path.join(root, f))

    py_files.sort()

    with open(OUTPUT_FILE, "w", encoding="utf-8") as out:
        for path in py_files:
            out.write("\n")
            out.write("=" * 40 + "\n")
            out.write(f"FILE: {path}\n")
            out.write("=" * 40 + "\n")
            out.write("\n")
            with open(path, "r", encoding="utf-8") as fh:
                out.write(fh.read())
            out.write("\n")

    print(f"✅ 合并完成！共 {len(py_files)} 个文件 -> {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
