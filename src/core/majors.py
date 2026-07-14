"""专业列表管理（CSV 存储）"""

import csv
import os

_CSV_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "data",
    "majors.csv",
)


def all_majors() -> list[str]:
    """返回全部专业名称列表"""
    if not os.path.exists(_CSV_PATH):
        os.makedirs(os.path.dirname(_CSV_PATH), exist_ok=True)
        with open(_CSV_PATH, "w", encoding="utf-8-sig", newline="") as f:
            csv.writer(f).writerow(["name"])
        return []
    majors = []
    with open(_CSV_PATH, "r", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            majors.append(row["name"].strip())
    return majors


def add_major(name: str) -> str | None:
    """新增专业，重复或格式错误时返回错误信息"""
    name = name.strip()
    if not name:
        return "专业名不能为空"
    if "," in name or "，" in name:
        return "专业名不能包含逗号"
    if len(name) > 50:
        return "专业名不能超过 50 个字符"
    if name in all_majors():
        return f"专业「{name}」已存在"
    with open(_CSV_PATH, "a", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([name])
    return None


def delete_major(name: str) -> str | None:
    """删除专业，返回错误信息"""
    majors = all_majors()
    if name not in majors:
        return f"专业「{name}」不存在"
    majors.remove(name)
    with open(_CSV_PATH, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["name"])
        for m in majors:
            writer.writerow([m])
    return None
