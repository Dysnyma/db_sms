"""Pydantic 模型：表单输入校验"""

from typing import Optional
from pydantic import BaseModel, Field, field_validator, ValidationError
import streamlit as st

# (model名, 字段名) → 中文标签（不同 model 同名字段可区分）
_FIELD_LABELS = {
    ("StudentCreate", "name"): "姓名",
    ("StudentCreate", "no"): "学号",
    ("StudentCreate", "class_id"): "班级",
    ("TeacherCreate", "name"): "姓名",
    ("TeacherCreate", "no"): "工号",
    ("TeacherCreate", "title"): "职称",
    ("TeacherCreate", "phone"): "电话",
    ("ClassCreate", "name"): "班级名",
    ("ClassCreate", "grade"): "年级",
    ("ClassCreate", "major"): "专业",
    ("CourseCreate", "name"): "课程名",
    ("CourseCreate", "credit"): "学分",
    ("SemesterQuery", "semester"): "学期",
    ("TeacherQuery", "no"): "教师工号",
    ("GradeRecord", "sno"): "学生学号",
    ("GradeRecord", "score"): "成绩",
}

# Pydantic 错误类型 → 中文模板
_ERROR_TRANSLATIONS = {
    "string_too_short": "最少 {min_length} 个字符",
    "string_too_long": "最多 {max_length} 个字符",
    "greater_than_equal": "不能小于 {ge}",
    "less_than_equal": "不能大于 {le}",
    "missing": "此项不能为空",
    "int_parsing": "必须为整数",
    "float_parsing": "必须为数字",
}


# ── 学生 ──

class StudentCreate(BaseModel):
    """新增/修改学生"""
    name: str = Field(..., min_length=1, max_length=50)
    no: str = Field(..., title="学号")
    class_id: int

    @field_validator("no")
    @classmethod
    def check_no(cls, v: str) -> str:
        v = v.strip()
        if not v.isdigit():
            raise ValueError("只能包含数字，不能有字母或符号")
        if len(v) < 8:
            raise ValueError("长度不能少于 8 位")
        if len(v) > 12:
            raise ValueError("长度不能超过 12 位")
        return v


StudentUpdate = StudentCreate


# ── 教师 ──

class TeacherCreate(BaseModel):
    """新增/修改教师"""
    name: str = Field(..., min_length=1, max_length=50)
    no: str = Field(..., title="工号")
    title: Optional[str] = Field(None, max_length=20)
    phone: Optional[str] = Field(None, title="电话")

    @field_validator("no")
    @classmethod
    def check_no(cls, v: str) -> str:
        v = v.strip()
        if not v.isdigit():
            raise ValueError("只能包含数字，不能有字母或符号")
        if len(v) < 5:
            raise ValueError("长度不能少于 5 位")
        if len(v) > 20:
            raise ValueError("长度不能超过 20 位")
        return v

    @field_validator("phone")
    @classmethod
    def check_phone(cls, v: Optional[str]) -> Optional[str]:
        if not v:
            return v
        v = v.strip()
        if not v.isdigit():
            raise ValueError("电话只能包含数字，不能有字母或符号")
        if len(v) < 7:
            raise ValueError("长度不能少于 7 位")
        if len(v) > 15:
            raise ValueError("长度不能超过 15 位")
        return v


TeacherUpdate = TeacherCreate


# ── 班级 ──

class ClassCreate(BaseModel):
    """新增/修改班级"""
    name: str = Field(..., min_length=1, max_length=50)
    grade: str = Field(..., title="年级")
    major: str = Field(..., min_length=1, max_length=100)

    @field_validator("grade")
    @classmethod
    def check_grade(cls, v: str) -> str:
        v = v.strip()
        if not v.isdigit():
            raise ValueError("年级只能包含数字，不能有字母或符号")
        if len(v) != 4:
            raise ValueError("必须为 4 位年份，如 2024")
        return v


ClassUpdate = ClassCreate


# ── 课程 ──

class CourseCreate(BaseModel):
    """新增/修改课程"""
    name: str = Field(..., min_length=1, max_length=100)
    credit: float = Field(..., ge=0.5, le=30.0)


CourseUpdate = CourseCreate


# ── 查询 ──

class SemesterQuery(BaseModel):
    """学期查询"""
    semester: str = Field(..., title="学期")

    @field_validator("semester")
    @classmethod
    def check_semester(cls, v: str) -> str:
        import re
        v = v.strip()
        if not re.match(r"^\d{4}-\d{4}-\d+$", v):
            raise ValueError("格式不正确，示例：2024-2025-1")
        return v


# ── 查询（教师）──

class TeacherQuery(BaseModel):
    """教师工号查询"""
    no: str = Field(..., title="教师工号")

    @field_validator("no")
    @classmethod
    def check_no(cls, v: str) -> str:
        v = v.strip()
        if not v.isdigit():
            raise ValueError("只能包含数字，不能有字母或符号")
        if len(v) < 5:
            raise ValueError("长度不能少于 5 位")
        if len(v) > 20:
            raise ValueError("长度不能超过 20 位")
        return v


# ── 成绩录入 ──

class GradeRecord(BaseModel):
    """成绩录入"""
    sno: str = Field(..., title="学生学号")
    score: float = Field(..., ge=0, le=100)

    @field_validator("sno")
    @classmethod
    def check_sno(cls, v: str) -> str:
        v = v.strip()
        if not v.isdigit():
            raise ValueError("只能包含数字，不能有字母或符号")
        if len(v) < 8:
            raise ValueError("长度不能少于 8 位")
        if len(v) > 12:
            raise ValueError("长度不能超过 12 位")
        return v


# ── 辅助函数 ──

def validate_or_error(model_cls, **data):
    """
    验证输入，失败时 st.toast 显示所有错误。
    返回 model_dump() 的 dict，验证失败返回 None。
    """
    try:
        return model_cls(**data).model_dump()
    except ValidationError as e:
        model_name = model_cls.__name__
        for err in e.errors():
            field = err["loc"][0]
            # 中文标签（不同 model 同名字段可区分）
            label = _FIELD_LABELS.get((model_name, field), field)
            # 中文翻译
            err_type = err["type"]
            template = _ERROR_TRANSLATIONS.get(err_type)
            if template:
                # field_validator 的 ctx 里带有自定义 error 上下文
                ctx = err.get("ctx") or {}
                msg = template.format(**ctx)
            else:
                # field_validator 抛的 ValueError，去掉 "Value error, " 前缀
                msg = err["msg"].removeprefix("Value error, ")
            st.toast(f"❌ {label}：{msg}")
        return None
