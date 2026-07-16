"""生成答辩 PPT——数据库系统课程设计·学生成绩管理系统"""
from pptx import Presentation
from pptx.util import Inches, Pt, Emu, Cm
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
import os

prs = Presentation()
prs.slide_width = Inches(13.33)
prs.slide_height = Inches(7.5)

# ── 色板 ──
C_PRIMARY = RGBColor(0x1A, 0x52, 0x76)   # 深蓝
C_SECONDARY = RGBColor(0x2E, 0x86, 0xC1)  # 中蓝
C_ACCENT = RGBColor(0x4C, 0xAF, 0x50)     # 绿
C_LIGHT = RGBColor(0xEB, 0xF5, 0xFB)      # 浅蓝底
C_WHITE = RGBColor(0xFF, 0xFF, 0xFF)
C_DARK = RGBColor(0x2C, 0x3E, 0x50)
C_GRAY = RGBColor(0x7F, 0x8C, 0x8D)

# ── 辅助函数 ──
def add_bg(slide, color=C_PRIMARY):
    bg = slide.background
    fill = bg.fill
    fill.solid()
    fill.fore_color.rgb = color

def add_shape(slide, left, top, width, height, color=C_PRIMARY):
    shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, left, top, width, height)
    shape.fill.solid()
    shape.fill.fore_color.rgb = color
    shape.line.fill.background()
    return shape

def add_rounded_shape(slide, left, top, width, height, color):
    shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    shape.fill.solid()
    shape.fill.fore_color.rgb = color
    shape.line.fill.background()
    return shape

def _set_font(run, size=14, bold=False, color=C_DARK, font='Microsoft YaHei'):
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.color.rgb = color
    run.font.name = font

def add_text(slide, left, top, width, height, text, size=14, bold=False, color=C_DARK, align=PP_ALIGN.LEFT, font='Microsoft YaHei'):
    txBox = slide.shapes.add_textbox(left, top, width, height)
    tf = txBox.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = text
    p.alignment = align
    _set_font(p.runs[0], size, bold, color, font)
    return txBox

def add_multi_text(slide, left, top, width, height, lines, size=14, color=C_DARK, font='Microsoft YaHei', spacing=Pt(6)):
    txBox = slide.shapes.add_textbox(left, top, width, height)
    tf = txBox.text_frame
    tf.word_wrap = True
    for i, (text, bold, sz, clr) in enumerate(lines):
        if i == 0:
            p = tf.paragraphs[0]
        else:
            p = tf.add_paragraph()
        p.text = text
        p.alignment = PP_ALIGN.LEFT
        p.space_after = spacing
        run = p.runs[0]
        _set_font(run, sz or size, bold, clr or color, font)
    return txBox

def add_accent_bar(slide, left, top, width=Inches(0.06), height=Inches(0.4), color=C_ACCENT):
    return add_shape(slide, left, top, width, height, color)

def add_card(slide, left, top, width, height, title, items, icon=""):
    """添加卡片"""
    card = add_rounded_shape(slide, left, top, width, height, C_WHITE)
    # 标题行
    add_text(slide, left + Inches(0.2), top + Inches(0.1), width - Inches(0.4), Inches(0.4),
             f"{icon} {title}", size=16, bold=True, color=C_PRIMARY)
    # 装饰线
    add_shape(slide, left + Inches(0.2), top + Inches(0.45), Inches(0.6), Inches(0.04), C_SECONDARY)
    # 内容
    add_multi_text(slide, left + Inches(0.2), top + Inches(0.55), width - Inches(0.4), height - Inches(0.65),
                   [(item, False, 13, C_DARK) for item in items], spacing=Pt(4))


# ════════════════════════════════════════════════════════════════
# Slide 1: 封面
# ════════════════════════════════════════════════════════════════
slide = prs.slides.add_slide(prs.slide_layouts[6])  # blank
add_bg(slide, C_PRIMARY)
# 装饰条
add_shape(slide, Inches(0), Inches(0), Inches(13.33), Inches(0.06), C_ACCENT)
add_shape(slide, Inches(0), Inches(7.44), Inches(13.33), Inches(0.06), C_ACCENT)

# 主标题
add_text(slide, Inches(1), Inches(1.8), Inches(11.33), Inches(1.2),
         "数据库系统课程设计", size=44, bold=True, color=C_WHITE, align=PP_ALIGN.CENTER)

# 副标题
add_text(slide, Inches(1), Inches(2.9), Inches(11.33), Inches(0.8),
         "学生成绩管理系统", size=36, bold=False, color=RGBColor(0x85, 0xC1, 0xE9), align=PP_ALIGN.CENTER)

# 分割线
add_shape(slide, Inches(5.5), Inches(3.8), Inches(2.33), Inches(0.04), C_ACCENT)

# 信息
info_lines = [
    ("专    业：计算机科学与技术", 16, C_WHITE),
    ("学    生：蔡坤灿", 16, C_WHITE),
    ("指导教师：", 16, C_WHITE),
    ("日    期：2026年7月", 16, C_WHITE),
]
for i, (txt, sz, clr) in enumerate(info_lines):
    add_text(slide, Inches(4.7), Inches(4.1 + i * 0.5), Inches(4), Inches(0.45),
             txt, size=sz, bold=False, color=clr, align=PP_ALIGN.CENTER)

add_text(slide, Inches(1), Inches(6.5), Inches(11.33), Inches(0.5),
         "AI辅助 | MySQL + Python + Streamlit", size=14, color=RGBColor(0x85, 0xC1, 0xE9), align=PP_ALIGN.CENTER)


# ════════════════════════════════════════════════════════════════
# Slide 2: 目录
# ════════════════════════════════════════════════════════════════
slide = prs.slides.add_slide(prs.slide_layouts[6])
add_shape(slide, Inches(0), Inches(0), Inches(0.4), Inches(7.5), C_PRIMARY)
add_text(slide, Inches(1), Inches(0.3), Inches(4), Inches(0.6),
         "目  录", size=32, bold=True, color=C_PRIMARY)

toc_items = [
    ("01", "项目概述"),
    ("02", "系统架构与技术栈"),
    ("03", "数据库设计"),
    ("04", "功能模块详解"),
    ("05", "AI辅助开发记录"),
    ("06", "总结与演示"),
]
for i, (num, title) in enumerate(toc_items):
    y = Inches(1.3 + i * 0.85)
    add_shape(slide, Inches(1), y, Inches(0.7), Inches(0.6), C_SECONDARY)
    add_text(slide, Inches(1.05), y + Inches(0.08), Inches(0.6), Inches(0.45),
             num, size=18, bold=True, color=C_WHITE, align=PP_ALIGN.CENTER)
    add_text(slide, Inches(2), y + Inches(0.1), Inches(6), Inches(0.45),
             title, size=18, color=C_DARK)


# ════════════════════════════════════════════════════════════════
# Slide 3: 项目概述
# ════════════════════════════════════════════════════════════════
slide = prs.slides.add_slide(prs.slide_layouts[6])
add_accent_bar(slide, Inches(0.4), Inches(0.35))
add_text(slide, Inches(0.6), Inches(0.3), Inches(6), Inches(0.6),
         "01  项目概述", size=28, bold=True, color=C_PRIMARY)

# 卡片布局
add_card(slide, Inches(0.5), Inches(1.2), Inches(3.8), Inches(2.5),
         "选题", [
             "题目二：学生成绩管理系统",
             "覆盖教务、教师、学生三角色",
             "完整数据库设计6阶段流程",
         ], "🎯")

add_card(slide, Inches(4.6), Inches(1.2), Inches(3.8), Inches(2.5),
         "技术路线", [
             "数据库：MySQL 8.0 (InnoDB + utf8mb4)",
             "后端：Python 3.12 + SQLAlchemy 连接池",
             "Web 界面：Streamlit + Plotly 图表",
         ], "⚙️")

add_card(slide, Inches(8.7), Inches(1.2), Inches(4.1), Inches(2.5),
         "双界面交付", [
             "命令行界面 (CLI)：main.py（4角色）",
             "Web 界面：22 个 Streamlit 页面",
             "同一套数据库 + 业务函数",
         ], "🖥️")

# 数据规模卡片
add_card(slide, Inches(0.5), Inches(4.0), Inches(12.3), Inches(3.0),
         "数据规模", [
             "学生 20,000 人 | 教师 300 人 | 班级 329 个 | 课程 18 门",
             "排课 1,004 条 | 选课记录 2,002,688 条 | 专业 160+ 个",
             "覆盖 20 年学期跨度（40 个学期）",
         ], "📊")

add_text(slide, Inches(0.5), Inches(6.8), Inches(12), Inches(0.4),
         "⚠️ 当前截图待补充：请替换为实际系统运行截图", size=11, color=C_GRAY)


# ════════════════════════════════════════════════════════════════
# Slide 4: 系统架构
# ════════════════════════════════════════════════════════════════
slide = prs.slides.add_slide(prs.slide_layouts[6])
add_accent_bar(slide, Inches(0.4), Inches(0.35))
add_text(slide, Inches(0.6), Inches(0.3), Inches(6), Inches(0.6),
         "02  系统架构与技术栈", size=28, bold=True, color=C_PRIMARY)

# 三层架构图
layers = [
    (Inches(0.5), "🎨 表现层", ["Streamlit Web (22 页面)", "CLI 命令行界面"]),
    (Inches(4.8), "🧠 业务逻辑层", ["Pydantic 输入校验", "9 个存储过程", "5 个触发器", "3 个视图"]),
    (Inches(9.1), "🗄️ 数据层", ["MySQL 8.0 / InnoDB", "8 张表 + 连接池", "SQLAlchemy QueuePool"]),
]
for x, title, items in layers:
    box = add_rounded_shape(slide, x, Inches(1.3), Inches(3.8), Inches(2.8), C_LIGHT)
    box.shadow.inherit = False
    add_text(slide, x + Inches(0.2), Inches(1.4), Inches(3.4), Inches(0.5),
             title, size=16, bold=True, color=C_PRIMARY)
    add_shape(slide, x + Inches(0.2), Inches(1.85), Inches(0.5), Inches(0.03), C_SECONDARY)
    add_multi_text(slide, x + Inches(0.2), Inches(2.0), Inches(3.4), Inches(1.8),
                   [(item, False, 13, C_DARK) for item in items], spacing=Pt(5))

# 技术栈详情
techs = [
    ("Python 3.12", "编程语言"),
    ("MySQL 8.0", "数据库"),
    ("Streamlit", "Web 框架"),
    ("PyMySQL + SQLAlchemy", "数据库驱动"),
    ("Plotly", "交互式图表"),
    ("Pydantic", "数据校验"),
]
for i, (name, desc) in enumerate(techs):
    x = Inches(0.5 + i * 2.1)
    y = Inches(4.5)
    t = add_rounded_shape(slide, x, y, Inches(1.9), Inches(1.5), C_WHITE)
    t.shadow.inherit = False
    add_text(slide, x + Inches(0.1), y + Inches(0.2), Inches(1.7), Inches(0.4),
             name, size=14, bold=True, color=C_PRIMARY, align=PP_ALIGN.CENTER)
    add_text(slide, x + Inches(0.1), y + Inches(0.7), Inches(1.7), Inches(0.4),
             desc, size=12, color=C_GRAY, align=PP_ALIGN.CENTER)

add_text(slide, Inches(0.5), Inches(6.8), Inches(12), Inches(0.4),
         "⚠️ 待补充：系统部署架构图截图", size=11, color=C_GRAY)


# ════════════════════════════════════════════════════════════════
# Slide 5: 数据库设计 - 核心表
# ════════════════════════════════════════════════════════════════
slide = prs.slides.add_slide(prs.slide_layouts[6])
add_accent_bar(slide, Inches(0.4), Inches(0.35))
add_text(slide, Inches(0.6), Inches(0.3), Inches(6), Inches(0.6),
         "03  数据库设计 — 核心表", size=28, bold=True, color=C_PRIMARY)

tables = [
    ("class", "班级表", "年级、专业、状态"),
    ("student", "学生表", "学号、班级FK、学籍分、GPA"),
    ("course", "课程表", "课程名、学分"),
    ("teacher", "教师表", "工号、职称、电话"),
    ("course_offering", "排课表", "课程FK+教师FK+学期+时间+容量"),
    ("enrollment", "选课表", "排课FK+学生FK+成绩（触发器维护人数）"),
    ("teacher_course", "讲授关系", "教师FK+课程FK"),
    ("grade_point_rule", "绩点规则", "成绩区间→绩点映射"),
]
for i, (name, cname, desc) in enumerate(tables):
    col = i % 4
    row = i // 4
    x = Inches(0.5 + col * 3.15)
    y = Inches(1.1 + row * 1.9)
    card = add_rounded_shape(slide, x, y, Inches(2.9), Inches(1.7), C_LIGHT if row == 1 else C_WHITE)
    card.shadow.inherit = False
    add_accent_bar(slide, x, y + Inches(0.15), height=Inches(0.35), width=Inches(0.04), color=C_SECONDARY)
    add_text(slide, x + Inches(0.2), y + Inches(0.1), Inches(2.5), Inches(0.35),
             name, size=14, bold=True, color=C_PRIMARY)
    add_text(slide, x + Inches(0.2), y + Inches(0.5), Inches(2.5), Inches(0.3),
             cname, size=12, color=C_SECONDARY)
    add_text(slide, x + Inches(0.2), y + Inches(0.9), Inches(2.5), Inches(0.7),
             desc, size=11, color=C_GRAY)

# 设计原则
add_text(slide, Inches(0.5), Inches(5.3), Inches(12), Inches(0.4),
         "设计原则：全小写+下划线命名 · utf8mb4 · InnoDB · INT自增主键 · 全部逻辑删除(is_deleted) · status与is_deleted职责分离",
         size=12, color=C_GRAY)


# ════════════════════════════════════════════════════════════════
# Slide 6: 数据库对象
# ════════════════════════════════════════════════════════════════
slide = prs.slides.add_slide(prs.slide_layouts[6])
add_accent_bar(slide, Inches(0.4), Inches(0.35))
add_text(slide, Inches(0.6), Inches(0.3), Inches(6), Inches(0.6),
         "03  数据库对象 — 视图 / 触发器 / 存储过程 / 函数", size=28, bold=True, color=C_PRIMARY)

# 卡片
obj_data = [
    ("👁️  视图 (3)", [
        "v_student_message — 学生基本信息",
        "v_course_plan — 选课安排列表（含选课状态）",
        "v_enrollment — 选课详情（学生+课程+教师）",
    ]),
    ("⚡ 触发器 (5)", [
        "trg_before_insert — 选课名额检查",
        "trg_after_insert — 更新选课人数+1",
        "trg_after_update — 退选人数-1",
        "trg_after_insert_score — 带成绩时重算GPA",
        "trg_after_update_score — 成绩变化重算GPA",
    ]),
    ("📦 存储过程 (9)", [
        "sp_enroll / sp_unenroll — 选课/退选",
        "sp_grade_input — 成绩录入（三重身份校验）",
        "sp_student_roster — 班级名单含学籍分/GPA",
        "sp_class_grade_report — 成绩统计",
        "sp_student_semester_avg — 学期均分",
        "sp_teacher_info / sp_teacher_list — 教师统计",
        "sp_show_courses — 可选课程列表",
    ]),
    ("🔧 函数 (2)", [
        "fn_get_student_id — 学号→学生ID",
        "fn_get_teacher_id — 工号→教师ID",
    ]),
]

positions = [
    (Inches(0.5), Inches(1.1), Inches(6.0)),
    (Inches(6.8), Inches(1.1), Inches(6.0)),
    (Inches(0.5), Inches(3.6), Inches(6.0)),
    (Inches(6.8), Inches(3.6), Inches(6.0)),
]
for (title, items), (x, y, w) in zip(obj_data, positions):
    card = add_rounded_shape(slide, x, y, w, Inches(2.2), C_LIGHT)
    card.shadow.inherit = False
    add_text(slide, x + Inches(0.2), y + Inches(0.1), w - Inches(0.4), Inches(0.4),
             title, size=15, bold=True, color=C_PRIMARY)
    add_shape(slide, x + Inches(0.2), y + Inches(0.45), Inches(0.5), Inches(0.03), C_SECONDARY)
    add_multi_text(slide, x + Inches(0.2), y + Inches(0.55), w - Inches(0.4), Inches(1.5),
                   [(item, False, 12, C_DARK) for item in items], spacing=Pt(3))

# GPA 公式
add_text(slide, Inches(0.5), Inches(6.0), Inches(12), Inches(0.6),
         "学籍分公式：weighted_score = Σ(成绩×学分) / Σ(学分)    |    GPA公式：gpa = Σ(学分×绩点) / Σ(学分)",
         size=13, bold=True, color=C_PRIMARY, align=PP_ALIGN.CENTER)


# ════════════════════════════════════════════════════════════════
# Slide 7: 功能模块 — 三角色概览
# ════════════════════════════════════════════════════════════════
slide = prs.slides.add_slide(prs.slide_layouts[6])
add_accent_bar(slide, Inches(0.4), Inches(0.35))
add_text(slide, Inches(0.6), Inches(0.3), Inches(6), Inches(0.6),
         "04  功能模块 — 三角色概览", size=28, bold=True, color=C_PRIMARY)

roles = [
    ("🎓  学  生", C_SECONDARY, [
        "查看可选课程（过滤选课期/满员/同课异师）",
        "选课 / 退选（触发器实时校验）",
        "查看我的成绩（各科柱状图+学籍分/GPA）",
        "学期均分查询（selectbox 下拉）",
    ]),
    ("👨‍🏫  教  师", C_ACCENT, [
        "逐条录入成绩（Pydantic 校验）",
        "CSV 批量导入（按行反馈结果）",
        "查看课程学生（饼图+排行+未录入提醒）",
    ]),
    ("📋  教务管理员", C_PRIMARY, [
        "数据概览（Plotly 交互式图表）",
        "6 大实体 CRUD + 专业管理",
        "排课管理（datetime_input 原生组件）",
        "选课管理（按学号+学期精准查询）",
        "班级成绩统计 / 明细 / 教师排行",
        "备份恢复（mysqldump --routines --triggers）",
    ]),
]
for i, (title, color, items) in enumerate(roles):
    x = Inches(0.5 + i * 4.2)
    card = add_rounded_shape(slide, x, Inches(1.2), Inches(3.9), Inches(4.5), C_LIGHT)
    card.shadow.inherit = False
    add_shape(slide, x, Inches(1.2), Inches(3.9), Inches(0.8), color)
    add_text(slide, x + Inches(0.2), Inches(1.3), Inches(3.5), Inches(0.6),
             title, size=20, bold=True, color=C_WHITE, align=PP_ALIGN.CENTER)
    add_multi_text(slide, x + Inches(0.2), Inches(2.2), Inches(3.5), Inches(3.3),
                   [(f"✓ {item}", False, 12, C_DARK) for item in items], spacing=Pt(6))


# ════════════════════════════════════════════════════════════════
# Slide 8: 特色功能
# ════════════════════════════════════════════════════════════════
slide = prs.slides.add_slide(prs.slide_layouts[6])
add_accent_bar(slide, Inches(0.4), Inches(0.35))
add_text(slide, Inches(0.6), Inches(0.3), Inches(6), Inches(0.6),
         "04  功能亮点", size=28, bold=True, color=C_PRIMARY)

features = [
    ("🎨 交互式图表", "Plotly 饼图/柱状图展示\n成绩分布、教师排行、\n数据概览，悬停显示明细"),
    ("✅ Pydantic 校验", "全表单 Pydantic 模型校验 +\ntext_input max_chars 前端截断，\n中文 toast 错误提示"),
    ("🔑 快速选择登录", "从数据库读取活跃账号，\n下拉自动填充，测试零门槛"),
    ("🏫 班级名自动生成", "年级+专业 selectbox 下拉，\n系统自动查询序号生成班级名\n{年级}{专业}{序号}班"),
    ("📁 专业管理", "专业列表 CSV 存储，支持\n增删操作，班级管理联动\n删除前检查班级引用"),
    ("📊 大数据量支持", "LOAD DATA INFILE 极速导入\n200 万选课 + 自动重算 GPA\n删触发器+批量UPDATE优化"),
]
for i, (title, desc) in enumerate(features):
    col = i % 3
    row = i // 3
    x = Inches(0.5 + col * 4.2)
    y = Inches(1.1 + row * 3.0)
    card = add_rounded_shape(slide, x, y, Inches(3.9), Inches(2.7), C_WHITE)
    card.shadow.inherit = False
    add_shape(slide, x, y, Inches(3.9), Inches(0.6), C_SECONDARY)
    add_text(slide, x + Inches(0.2), y + Inches(0.08), Inches(3.5), Inches(0.45),
             title, size=16, bold=True, color=C_WHITE, align=PP_ALIGN.CENTER)
    add_text(slide, x + Inches(0.2), y + Inches(0.8), Inches(3.5), Inches(1.7),
             desc, size=12, color=C_DARK)


# ════════════════════════════════════════════════════════════════
# Slide 9: 数据规模与性能
# ════════════════════════════════════════════════════════════════
slide = prs.slides.add_slide(prs.slide_layouts[6])
add_accent_bar(slide, Inches(0.4), Inches(0.35))
add_text(slide, Inches(0.6), Inches(0.3), Inches(6), Inches(0.6),
         "04  数据规模与性能优化", size=28, bold=True, color=C_PRIMARY)

# 数据规模表
data_rows = [
    ("班级", "329 个", "24 → 329", "50 专业 × 3 年级 × 2~3 班"),
    ("教师", "300 人", "25 → 300", "新增 275 位仿真教师"),
    ("学生", "20,000 人", "1,000 → 20,000", "每班约 60 人"),
    ("排课", "1,004 条", "54 → 1,004", "覆盖 20 年 40 个学期"),
    ("选课", "2,002,688 条", "2,990 → 200 万", "25% 未录入成绩"),
]

# 表头背景
add_shape(slide, Inches(0.5), Inches(1.1), Inches(7.0), Inches(0.45), C_PRIMARY)

cols_def = [(Inches(0.7), Inches(1.2), "实体"),
            (Inches(2.0), Inches(1.5), "当前规模"),
            (Inches(3.6), Inches(1.7), "扩增倍数"),
            (Inches(5.4), Inches(2.0), "说明")]
for x, w, hdr in cols_def:
    add_text(slide, x, Inches(1.2), w, Inches(0.35), hdr, size=13, bold=True, color=C_WHITE)

for i, (name, count, ratio, note) in enumerate(data_rows):
    y = Inches(1.65 + i * 0.48)
    bg = add_shape(slide, Inches(0.5), y, Inches(7.0), Inches(0.45),
                   C_LIGHT if i % 2 == 0 else C_WHITE)
    add_text(slide, Inches(0.7), y + Inches(0.03), Inches(1.2), Inches(0.35),
             name, size=13, bold=True, color=C_PRIMARY)
    add_text(slide, Inches(2.0), y + Inches(0.03), Inches(1.5), Inches(0.35),
             count, size=13, color=C_DARK)
    add_text(slide, Inches(3.6), y + Inches(0.03), Inches(1.7), Inches(0.35),
             ratio, size=13, color=C_SECONDARY)
    add_text(slide, Inches(5.4), y + Inches(0.03), Inches(2.0), Inches(0.35),
             note, size=11, color=C_GRAY)

# 优化方案
opt_items = [
    ("索引优化", "enrollment 表 (offering_id, student_id, is_deleted)  联合索引减少回表"),
    ("导入优化", "LOAD DATA LOCAL INFILE 20×加速 + 删触发器 + 唯一键检查关闭"),
    ("GPA 重算", "2,002,688 条选课→一次性批量 UPDATE × 20,000 学生，替代逐行触发"),
    ("查询优化", "选课管理改为按学号+学期精准查询，避免 200 万条全量加载"),
]
for i, (title, desc) in enumerate(opt_items):
    x = Inches(0.5) if i < 2 else Inches(0.5)
    y = Inches(4.6 + (i % 2) * 1.1 + (0 if i < 2 else 0))
    # 如果是i>=2，应该是第2行
    if i >= 2:
        y = Inches(4.6 + (i % 2) * 1.1)

# 重新布局
opt_positions = [
    (Inches(0.5), Inches(4.5)),
    (Inches(6.7), Inches(4.5)),
    (Inches(0.5), Inches(5.7)),
    (Inches(6.7), Inches(5.7)),
]
for (title, desc), (x, y) in zip(opt_items, opt_positions):
    card = add_rounded_shape(slide, x, y, Inches(6.0), Inches(1.0), C_WHITE)
    card.shadow.inherit = False
    add_accent_bar(slide, x, y + Inches(0.15), height=Inches(0.7), width=Inches(0.04), color=C_ACCENT)
    add_text(slide, x + Inches(0.2), y + Inches(0.05), Inches(5.5), Inches(0.35),
             title, size=14, bold=True, color=C_PRIMARY)
    add_text(slide, x + Inches(0.2), y + Inches(0.4), Inches(5.5), Inches(0.5),
             desc, size=11, color=C_DARK)


# ════════════════════════════════════════════════════════════════
# Slide 10: AI 辅助开发
# ════════════════════════════════════════════════════════════════
slide = prs.slides.add_slide(prs.slide_layouts[6])
add_accent_bar(slide, Inches(0.4), Inches(0.35))
add_text(slide, Inches(0.6), Inches(0.3), Inches(6), Inches(0.6),
         "05  AI 辅助开发记录", size=28, bold=True, color=C_PRIMARY)

# 双栏布局
left_items = [
    ("✅ AI 有效应用", C_ACCENT, [
        "DDL/SQL 代码生成（快 70%）",
        "CRUD 重复代码（快 80%）",
        "Bug 定位（排序规则冲突等）",
        "代码重构（tester.py 175→83 行）",
        "文档生成（说明书初稿）",
    ]),
    ("⚠️ 人工修正记录", C_PRIMARY, [
        "sp_enroll 未检查同课异师 → 新增第4步校验",
        "1267 collation 冲突 → 统一 utf8mb4_unicode_ci",
        "st.tabs+st.form 组件干扰 → 改为 st.button",
        "备份缺少 routines/triggers → 新增参数",
    ]),
]
for i, (title, clr, items) in enumerate(left_items):
    x = Inches(0.5 + i * 6.3)
    card = add_rounded_shape(slide, x, Inches(1.0), Inches(6.0), Inches(3.0), C_LIGHT)
    card.shadow.inherit = False
    add_shape(slide, x, Inches(1.0), Inches(6.0), Inches(0.55), clr)
    add_text(slide, x + Inches(0.2), Inches(1.05), Inches(5.5), Inches(0.45),
             title, size=16, bold=True, color=C_WHITE, align=PP_ALIGN.CENTER)
    add_multi_text(slide, x + Inches(0.2), Inches(1.7), Inches(5.5), Inches(2.1),
                   [(f"• {item}", False, 12, C_DARK) for item in items], spacing=Pt(5))

# 反思区域
add_text(slide, Inches(0.5), Inches(4.3), Inches(12), Inches(0.4),
         "💡 反思与总结", size=18, bold=True, color=C_PRIMARY)

reflections = [
    ("AI 是强大的辅助工具", "核心设计决策（ER建模、范式、索引）必须由人工主导，AI仅提供建议"),
    ("提示词决定输出质量", "明确指定数据库对象类型（触发器/存储过程/视图）可获得更准确的代码"),
    ("人工审核不可替代", "AI对 Streamlit 组件行为理解不够深入，st.form/st.tabs 方案经历了 3 轮迭代"),
]
for i, (title, desc) in enumerate(reflections):
    y = Inches(4.8 + i * 0.7)
    add_accent_bar(slide, Inches(0.5), y, width=Inches(0.04), height=Inches(0.5), color=C_SECONDARY)
    add_text(slide, Inches(0.7), y, Inches(2.5), Inches(0.4),
             title, size=13, bold=True, color=C_PRIMARY)
    add_text(slide, Inches(3.2), y, Inches(9.5), Inches(0.5),
             desc, size=12, color=C_DARK)


# ════════════════════════════════════════════════════════════════
# Slide 11: 总结
# ════════════════════════════════════════════════════════════════
slide = prs.slides.add_slide(prs.slide_layouts[6])
add_bg(slide, C_PRIMARY)
add_shape(slide, Inches(0), Inches(0), Inches(13.33), Inches(0.06), C_ACCENT)
add_shape(slide, Inches(0), Inches(7.44), Inches(13.33), Inches(0.06), C_ACCENT)

add_text(slide, Inches(1), Inches(0.8), Inches(11.33), Inches(0.8),
         "06  总  结", size=36, bold=True, color=C_WHITE, align=PP_ALIGN.CENTER)
add_shape(slide, Inches(5.5), Inches(1.5), Inches(2.33), Inches(0.04), C_ACCENT)

summary_items = [
    ("📐 数据库设计", "8 表 · 3 视图 · 5 触发器 · 9 存储过程 · 2 函数"),
    ("💻 应用实现", "CLI + Streamlit 双界面，22 个 Web 页面"),
    ("📊 数据规模", "20,000 学生 · 300 教师 · 200 万选课记录"),
    ("🤖 AI 辅助", "Claude Code 全流程辅助，人工审核逐行把关"),
    ("🔧 代码质量", "Pydantic 校验 · Plotly 图表 · 连接池 · 逻辑删除"),
]

for i, (icon_title, desc) in enumerate(summary_items):
    y = Inches(2.0 + i * 0.85)
    add_text(slide, Inches(2), y, Inches(9.33), Inches(0.5),
             icon_title, size=18, bold=True, color=C_WHITE, align=PP_ALIGN.CENTER)
    add_text(slide, Inches(2), y + Inches(0.4), Inches(9.33), Inches(0.4),
             desc, size=14, color=RGBColor(0x85, 0xC1, 0xE9), align=PP_ALIGN.CENTER)

add_text(slide, Inches(1), Inches(6.5), Inches(11.33), Inches(0.5),
         "谢谢老师！请各位老师批评指正 🙏", size=20, bold=True, color=C_WHITE, align=PP_ALIGN.CENTER)


# ════════════════════════════════════════════════════════════════
# Slide 12: 待补充截图清单
# ════════════════════════════════════════════════════════════════
slide = prs.slides.add_slide(prs.slide_layouts[6])
add_accent_bar(slide, Inches(0.4), Inches(0.35))
add_text(slide, Inches(0.6), Inches(0.3), Inches(6), Inches(0.6),
         "📸  请在此处插入系统运行截图", size=28, bold=True, color=C_PRIMARY)

screenshots = [
    "登录页面（快速选择下拉）",
    "数据概览（Plotly 饼图 + 柱状图）",
    "班级管理（年级/专业下拉 + 自动生成班级名）",
    "教师查看课程学生（饼图+排行并排）",
    "学生我的成绩（各科成绩柱状图+及格线）",
    "排课管理（datetime_input 原生组件）",
    "班级成绩统计（分布柱状图）",
    "选课管理（按学号+学期查询）",
    "专业管理页面",
    "生成器运行效果（200 万数据导入）",
]
for i, (ss) in enumerate(screenshots):
    col = i % 2
    row = i // 2
    x = Inches(0.5 + col * 6.3)
    y = Inches(1.1 + row * 0.65)
    add_shape(slide, x, y, Inches(6.0), Inches(0.5), C_LIGHT)
    add_text(slide, x + Inches(0.2), y + Inches(0.07), Inches(5.5), Inches(0.35),
             f"{i+1:02d}. {ss}", size=12, color=C_DARK)


# ── 保存 ──
output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                           "数据库系统课程设计_答辩PPT.pptx")
prs.save(output_path)
print(f"✅ PPT 已保存到: {output_path}")
