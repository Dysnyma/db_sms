"""重建数据库 + 跑全部 SQL + 导入数据"""

import import_data
import subprocess
import os

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SQL = os.path.join(BASE, "sql")
MYSQL = "mysql"

files = [
    "01_数据库创建.sql",
    "02_基础数据表.sql",
    "03_中间表.sql",
    "04_视图.sql",
    "06_触发器.sql",
    "07_存储过程.sql",
    "08_存储函数.sql",
]

print("=" * 50)
print("  重建数据库...")
print("=" * 50)

for f in files:
    path = os.path.join(SQL, f)
    print(f"  >>> {f}", end=" ", flush=True)
    r = subprocess.run(
        [MYSQL, "-u", "root", "--default-character-set=utf8mb4", "--batch"],
        stdin=open(path, "r", encoding="utf-8"),
        capture_output=True,
        text=True,
        timeout=30,
        encoding="utf-8",
        errors="replace",
        check=False,
        shell=False,
    )
    if r.returncode == 0:
        print("[OK]")
    else:
        print("[FAIL]")
        if r.stderr:
            print(f"    {r.stderr.strip()[:300]}")
        if r.stdout:
            print(f"    stdout: {r.stdout.strip()[:300]}")

print()
print("=" * 50)
print("  导入数据...")
print("=" * 50)

import_data.main()
