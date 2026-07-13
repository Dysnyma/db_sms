# -*- coding: utf-8 -*-
"""重新生成报告图片 —— 大字版，清晰可读"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch
import numpy as np, os

OUT_DIR = r'E:\02_Courses\db_lab\document\报告\images'
os.makedirs(OUT_DIR, exist_ok=True)

plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'Noto Sans SC', 'SimHei']
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['figure.dpi'] = 200  # 高清

FONT_TITLE = 16
FONT_BODY = 12
FONT_SMALL = 10

# ============================================================
# 图1: 全局 ER 图（精简版，大字）
# ============================================================
def draw_er():
    fig, ax = plt.subplots(figsize=(18, 12))
    ax.set_xlim(0, 18); ax.set_ylim(0, 12)
    ax.axis('off'); ax.set_facecolor('#FAFAFA')

    ents = {
        'class':      (2, 9, '班级\nclass', '#BBDEFB'),
        'student':    (2, 5, '学生\nstudent', '#C8E6C9'),
        'course':     (9, 9, '课程\ncourse', '#FFE0B2'),
        'teacher':    (9, 5, '教师\nteacher', '#E1BEE7'),
        'offering':   (5.5, 7, '选课安排\ncourse_offering', '#FFCDD2'),
        'enrollment': (5.5, 2.5, '选课\nenrollment', '#B2EBF2'),
        'tc':         (14, 7, '讲授\nteacher_course', '#F0F0F0'),
        'gpr':        (14, 10, '绩点对照\ngrade_point_rule', '#F5F5F5'),
    }
    pos = {}
    for name, (x, y, label, color) in ents.items():
        pos[name] = (x, y)
        w, h = 2.8, 1.8
        rect = FancyBboxPatch((x-w/2, y-h/2), w, h, boxstyle="round,pad=0.15",
                              facecolor=color, edgecolor='#333', linewidth=2)
        ax.add_patch(rect)
        ax.text(x, y, label, ha='center', va='center', fontsize=FONT_BODY,
                fontweight='bold', color='#222')

    rels = [
        ('class', 'student', '属于', '1', 'N'),
        ('course', 'offering', '开设', '1', 'N'),
        ('teacher', 'offering', '授课', '1', 'N'),
        ('offering', 'enrollment', '包含', '1', 'N'),
        ('student', 'enrollment', '选修', '1', 'N'),
        ('teacher', 'tc', '拥有', '1', 'N'),
        ('course', 'tc', '被授', '1', 'N'),
    ]

    for src, dst, label, card_s, card_d in rels:
        sx, sy = pos[src]; dx, dy = pos[dst]
        # 缩短连线，不穿入实体框
        margin = 0.9
        vx, vy = dx - sx, dy - sy
        dist = np.sqrt(vx**2 + vy**2)
        if dist > 0:
            ux, uy = vx/dist, vy/dist
            sx2, sy2 = sx + ux*margin, sy + uy*margin
            dx2, dy2 = dx - ux*margin, dy - uy*margin
        else:
            sx2, sy2, dx2, dy2 = sx, sy, dx, dy

        ax.annotate('', xy=(dx2, dy2), xytext=(sx2, sy2),
                    arrowprops=dict(arrowstyle='->', color='#555', lw=2))
        mx, my = (sx+dx)/2, (sy+dy)/2
        ax.text(mx+0.1, my+0.2, label, fontsize=FONT_SMALL, color='#555',
                bbox=dict(boxstyle='round,pad=0.1', fc='white', ec='none', alpha=0.85))
        ax.text(sx2-0.15, sy2-0.3, card_s, fontsize=FONT_SMALL, color='#C62828', fontweight='bold')
        ax.text(dx2+0.05, dy2-0.3, card_d, fontsize=FONT_SMALL, color='#C62828', fontweight='bold')

    ax.set_title('图3-1  全局 E-R 图', fontsize=FONT_TITLE, fontweight='bold', pad=20)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT_DIR, 'er_diagram.png'), dpi=200, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    print('[OK] ER图')

# ============================================================
# 图2: 数据流图
# ============================================================
def draw_dfd():
    fig, ax = plt.subplots(figsize=(18, 10))
    ax.set_xlim(0, 18); ax.set_ylim(0, 10)
    ax.axis('off'); ax.set_facecolor('#FAFAFA')

    # 外部实体
    externals = [(1.5, 8, '学生', '#BBDEFB'), (1.5, 2, '教师', '#C8E6C9'), (9, 9.2, '教务管理员', '#FFE0B2')]
    for x, y, label, color in externals:
        rect = FancyBboxPatch((x-1.3, y-0.5), 2.6, 1.0, boxstyle="round,pad=0.1",
                              facecolor=color, edgecolor='#333', linewidth=2)
        ax.add_patch(rect)
        ax.text(x, y, label, ha='center', va='center', fontsize=FONT_BODY, fontweight='bold')

    # 处理过程（圆形）
    procs = [(5.5, 8, '选课管理'), (5.5, 5, '成绩管理'), (5.5, 2, '信息查询'), (11.5, 5, '数据维护')]
    for x, y, label in procs:
        c = plt.Circle((x, y), 1.0, facecolor='#FFCDD2', edgecolor='#333', linewidth=2)
        ax.add_patch(c)
        ax.text(x, y, label, ha='center', va='center', fontsize=FONT_BODY, fontweight='bold')

    # 数据存储
    stores = [(12, 8.5, '学生/班级/课程表'), (12, 1.5, '教师/排课/选课表')]
    for x, y, label in stores:
        rect = FancyBboxPatch((x-1.5, y-0.6), 3.0, 1.2, boxstyle="round,pad=0.1",
                              facecolor='#F5F5F5', edgecolor='#333', linewidth=2)
        ax.add_patch(rect)
        ax.text(x, y, label, ha='center', va='center', fontsize=FONT_SMALL)

    # 箭头
    arrows = [
        (2.8,8,4.5,8,'选课请求'), (4.5,7.5,2.8,7.5,'选课结果'),
        (2.8,2,4.5,2,'录入成绩'), (4.5,1.5,2.8,1.5,'录入结果'),
        (6.5,8,10.5,8.5,'读写'), (6.5,2,10.5,1.5,'读写'),
        (6.5,5,10.5,5,'读写'),
    ]
    for sx, sy, dx, dy, label in arrows:
        ax.annotate('', xy=(dx, dy), xytext=(sx, sy),
                    arrowprops=dict(arrowstyle='->', color='#555', lw=2))
        if label:
            mx, my = (sx+dx)/2, (sy+dy)/2
            ax.text(mx, my+0.2, label, fontsize=FONT_SMALL, ha='center',
                    bbox=dict(boxstyle='round', fc='white', alpha=0.8))

    ax.set_title('图2-1  系统数据流图（DFD）', fontsize=FONT_TITLE, fontweight='bold', pad=20)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT_DIR, 'data_flow_diagram.png'), dpi=200, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    print('[OK] DFD')

# ============================================================
# 图3: 系统架构图
# ============================================================
def draw_arch():
    fig, ax = plt.subplots(figsize=(16, 9))
    ax.set_xlim(0, 16); ax.set_ylim(0, 9)
    ax.axis('off'); ax.set_facecolor('#FAFAFA')

    layers = [
        (0.5, 7.0, 15, 1.4, '表示层 (Presentation Layer)', '#BBDEFB',
         'Streamlit Web UI（st.navigation 多页导航）  |  CLI 命令行界面\n'
         '学生端：选课/退选/成绩查询      教师端：成绩录入/批量导入\n'
         '教务端：数据概览/CRUD管理/统计报表/备份恢复'),
        (0.5, 5.1, 15, 1.4, '业务逻辑层 (Business Logic Layer)', '#C8E6C9',
         'Python 应用服务（app.py / admin.py / student.py / teacher.py）\n'
         '选课管理 · 退选管理 · 成绩录入 · 统计查询 · 权限控制 · 数据校验'),
        (0.5, 3.2, 15, 1.4, '数据访问层 (Data Access Layer)', '#FFE0B2',
         'PyMySQL 数据库驱动  |  存储过程调用  |  游标管理  |  事务控制'),
        (0.5, 1.3, 15, 1.4, '数据存储层 (Data Storage Layer)', '#FFCDD2',
         'MySQL 8.0 — db_sms 数据库\n'
         '8张表 · 3视图 · 5触发器 · 9存储过程 · 2函数  |  InnoDB · utf8mb4'),
    ]
    for x, y, w, h, title, color, desc in layers:
        rect = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.15",
                              facecolor=color, edgecolor='#333', linewidth=2, alpha=0.75)
        ax.add_patch(rect)
        ax.text(x+0.3, y+h-0.3, title, fontsize=FONT_BODY, fontweight='bold', va='top')
        ax.text(x+0.3, y+0.15, desc, fontsize=FONT_SMALL, color='#333', va='bottom', linespacing=1.4)

    for i in range(3):
        y1 = layers[i][1]
        y2 = layers[i+1][1] + layers[i+1][3]
        ax.annotate('', xy=(8, y2), xytext=(8, y1),
                    arrowprops=dict(arrowstyle='<->', color='#555', lw=2))

    ax.set_title('图1-1  系统四层架构图', fontsize=FONT_TITLE, fontweight='bold', pad=20)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT_DIR, 'system_architecture.png'), dpi=200, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    print('[OK] 架构图')

# ============================================================
# 图4: 功能模块图
# ============================================================
def draw_modules():
    fig, ax = plt.subplots(figsize=(18, 9))
    ax.set_xlim(0, 18); ax.set_ylim(0, 9)
    ax.axis('off'); ax.set_facecolor('#FAFAFA')

    ax.text(9, 8.5, '学生成绩管理系统', ha='center', va='center', fontsize=FONT_TITLE,
            fontweight='bold', color='#fff',
            bbox=dict(boxstyle='round,pad=0.4', facecolor='#1565C0', edgecolor='#0D47A1'))

    mods = [
        (3.5, 5.5, '学生端', '#42A5F5', ['浏览可选课程', '选课 / 退选', '查看我的成绩', '查询学期均分']),
        (9, 5.5, '教师端', '#66BB6A', ['录入学生成绩', '批量 CSV 导入', '查看课程学生']),
        (14.5, 5.5, '教务端', '#FFA726', ['数据概览仪表板', '班级/课程/教师/学生 CRUD', '排课/选课管理', '成绩统计与报表', '数据备份与恢复']),
    ]
    for x, y, title, color, items in mods:
        w, h = 4.2, 3.8
        rect = FancyBboxPatch((x-w/2, y-h/2), w, h, boxstyle="round,pad=0.15",
                              facecolor=color, edgecolor='#333', linewidth=2, alpha=0.88)
        ax.add_patch(rect)
        ax.text(x, y+h/2-0.4, title, ha='center', va='center', fontsize=FONT_BODY, fontweight='bold', color='#fff')
        for i, item in enumerate(items):
            ax.text(x, y+h/2-1.0 - i*0.6, f'• {item}', ha='center', va='center', fontsize=FONT_SMALL+1, color='#fff')
        ax.plot([9, x], [8.2, y+h/2], '-', color='#999', lw=1.5)

    ax.set_title('图2-2  系统功能模块图', fontsize=FONT_TITLE, fontweight='bold', pad=15)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT_DIR, 'function_modules.png'), dpi=200, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    print('[OK] 功能模块图')

# ============================================================
# 图5: 数据库关系图（表结构概览）
# ============================================================
def draw_tables():
    fig, ax = plt.subplots(figsize=(20, 12))
    ax.set_xlim(0, 20); ax.set_ylim(0, 12)
    ax.axis('off'); ax.set_facecolor('#FAFAFA')

    tables = [
        (0.3, 8.2, 'class 班级表\nPK id\n  name\n  grade\n  major\n  status', '#BBDEFB'),
        (0.3, 3.8, 'student 学生表\nPK id\nFK class_id\n  no(学号)\n  name\n  weighted_score\n  gpa', '#C8E6C9'),
        (7, 8.2, 'course 课程表\nPK id\n  name\n  credit\n  status', '#FFE0B2'),
        (13.5, 8.2, 'grade_point_rule\n绩点对照表\nPK id\n  min_score\n  max_score\n  point', '#F5F5F5'),
        (7, 3.8, 'teacher 教师表\nPK id\n  no(工号)\n  name\n  title\n  phone', '#E1BEE7'),
        (5.5, 0.3, 'enrollment 选课表\nPK id\nFK offering_id\nFK student_id\n  score(成绩)', '#B2EBF2'),
        (11, 0.3, 'course_offering\n选课安排表\nPK id\nFK course_id\nFK teacher_id\n  semester\n  max_students\n  current_students', '#FFCDD2'),
        (16, 3.8, 'teacher_course\n讲授表\nPK id\nFK teacher_id\nFK course_id', '#F0F0F0'),
    ]

    for x, y, label, color in tables:
        lines = label.split('\n')
        w, h = 3.5, 0.4 * len(lines) + 0.3
        rect = FancyBboxPatch((x, y-h), w, h, boxstyle="round,pad=0.08",
                              facecolor=color, edgecolor='#333', linewidth=1.5, alpha=0.85)
        ax.add_patch(rect)
        for li, line in enumerate(lines):
            c = '#C62828' if line.startswith('PK') else ('#2E7D32' if line.startswith('FK') else '#222')
            fs = FONT_SMALL if li == 0 else FONT_SMALL-1
            fw = 'bold' if li == 0 else 'normal'
            ax.text(x+0.2, y-0.25-li*0.35, line, fontsize=fs, color=c, fontweight=fw, va='top', fontfamily='monospace')

    # 关系线
    ax.annotate('class→student\n1:N', xy=(1.8, 5.2), xytext=(1.8, 8.0),
                arrowprops=dict(arrowstyle='->', color='#666', lw=1.5), fontsize=8, ha='center',
                bbox=dict(boxstyle='round', fc='#FFF9C4', alpha=0.9))
    ax.annotate('course→offering\n1:N', xy=(7.5, 2.0), xytext=(8.5, 8.0),
                arrowprops=dict(arrowstyle='->', color='#666', lw=1.5), fontsize=8, ha='center',
                bbox=dict(boxstyle='round', fc='#FFF9C4', alpha=0.9))
    ax.annotate('teacher→offering\n1:N', xy=(10.5, 2.0), xytext=(8.5, 4.5),
                arrowprops=dict(arrowstyle='->', color='#666', lw=1.5), fontsize=8, ha='center',
                bbox=dict(boxstyle='round', fc='#FFF9C4', alpha=0.9))
    ax.annotate('offering→\nenrollment\n1:N', xy=(7.0, 1.5), xytext=(11.5, 1.5),
                arrowprops=dict(arrowstyle='->', color='#666', lw=1.5), fontsize=8, ha='center',
                bbox=dict(boxstyle='round', fc='#FFF9C4', alpha=0.9))
    ax.annotate('student→\nenrollment\n1:N', xy=(5.5, 1.5), xytext=(2.0, 3.5),
                arrowprops=dict(arrowstyle='->', color='#666', lw=1.5), fontsize=8, ha='center',
                bbox=dict(boxstyle='round', fc='#FFF9C4', alpha=0.9))
    ax.annotate('teacher→tc\n1:N', xy=(17.5, 4.5), xytext=(8.5, 4.5),
                arrowprops=dict(arrowstyle='->', color='#999', lw=1.5, ls='--'), fontsize=8, ha='center')
    ax.annotate('course→tc\n1:N', xy=(17.5, 5.0), xytext=(8.5, 8.0),
                arrowprops=dict(arrowstyle='->', color='#999', lw=1.5, ls='--'), fontsize=8, ha='center')

    ax.set_title('图4-1  数据库关系图', fontsize=FONT_TITLE, fontweight='bold', pad=20)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT_DIR, 'table_relationships.png'), dpi=200, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    print('[OK] 表关系图')

# ============================================================
# 图6: EXPLAIN 执行计划
# ============================================================
def draw_explain():
    fig, ax = plt.subplots(figsize=(16, 5))
    ax.axis('off')
    cols = ['id', 'select_type', 'table', 'type', 'key', 'key_len', 'ref', 'rows', 'filtered', 'Extra']
    data = [
        ['1', 'SIMPLE', 'enrollment', 'ref', 'idx_enr_student', '4', 'db_sms.e.offering_id', '13', '100.00', 'Using where'],
        ['1', 'SIMPLE', 'student', 'eq_ref', 'PRIMARY', '4', 'db_sms.e.student_id', '1', '100.00', ''],
        ['1', 'SIMPLE', 'course_offering', 'eq_ref', 'PRIMARY', '4', 'db_sms.e.offering_id', '1', '100.00', 'Using where'],
    ]
    table = ax.table(cellText=data, colLabels=cols, cellLoc='center', loc='center',
                     colWidths=[0.04, 0.08, 0.09, 0.06, 0.10, 0.06, 0.14, 0.05, 0.06, 0.10])
    table.auto_set_font_size(False)
    table.set_fontsize(9)
    table.scale(1.1, 1.8)
    for i in range(len(cols)):
        table[0, i].set_facecolor('#1565C0')
        table[0, i].set_text_props(color='white', fontweight='bold', fontsize=9)
    ax.set_title('图5-1  EXPLAIN 执行计划分析', fontsize=FONT_TITLE, fontweight='bold', pad=20)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT_DIR, 'explain_plan.png'), dpi=200, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    print('[OK] EXPLAIN图')

# ============================================================
# 图7: UI 模拟截图
# ============================================================
def draw_ui():
    # 登录页
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.set_xlim(0, 12); ax.set_ylim(0, 6)
    ax.axis('off'); ax.set_facecolor('#E8ECF1')

    header = FancyBboxPatch((2, 4.5), 8, 0.9, boxstyle="round,pad=0.1",
                            facecolor='#1565C0', edgecolor='#0D47A1')
    ax.add_patch(header)
    ax.text(6, 4.95, '学生成绩管理系统', ha='center', va='center', fontsize=18, fontweight='bold', color='white')
    form = FancyBboxPatch((3.5, 2.0), 5, 2.2, boxstyle="round,pad=0.2", facecolor='white', edgecolor='#CCC', linewidth=1.5)
    ax.add_patch(form)
    ax.text(6, 3.8, '请输入学号 / 工号（教务输入 admin）', ha='center', fontsize=10, color='#888')
    input_box = FancyBboxPatch((4.2, 3.1), 3.6, 0.5, boxstyle="round,pad=0.05", facecolor='#F0F2F5', edgecolor='#BBB')
    ax.add_patch(input_box)
    btn = FancyBboxPatch((5, 2.2), 2, 0.55, boxstyle="round,pad=0.05", facecolor='#1565C0', edgecolor='#0D47A1')
    ax.add_patch(btn)
    ax.text(6, 2.48, '登  录', ha='center', fontsize=12, color='white', fontweight='bold')
    ax.set_title('图7-1  系统登录页面', fontsize=FONT_TITLE, fontweight='bold', pad=15)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT_DIR, 'ui_login.png'), dpi=200, bbox_inches='tight', facecolor='white')
    plt.close(fig)

    # 教务仪表板
    fig, ax = plt.subplots(figsize=(14, 7))
    ax.set_xlim(0, 14); ax.set_ylim(0, 7)
    ax.axis('off'); ax.set_facecolor('#E8ECF1')

    sidebar = FancyBboxPatch((0, 0), 2.5, 7, boxstyle="round,pad=0.0", facecolor='#1A237E', edgecolor='none')
    ax.add_patch(sidebar)
    for i, (label, y) in enumerate([('📊 数据查看', 6.2), ('  - 数据概览', 5.6), ('  - 班级名单', 5.1),
                                     ('  - 成绩统计', 4.6), ('  - 教师信息', 4.1),
                                     ('🔧 数据管理', 3.2), ('  - 班级管理', 2.7), ('  - 课程管理', 2.2),
                                     ('  - 教师管理', 1.7), ('  - 学生管理', 1.2),
                                     ('💾 系统工具', 0.4)]):
        fs = 9 if label.startswith('  ') else 9
        fw = 'bold' if not label.startswith('  ') else 'normal'
        ax.text(0.3, y, label, fontsize=fs, color='#B0BEC5' if label.startswith('  ') else '#E0E0E0', fontweight=fw)

    ax.text(5.5, 6.4, '📋 数据概览', fontsize=14, fontweight='bold')
    metrics = [('班级总数', '12'), ('学生总数', '120'), ('教师总数', '16'),
               ('课程总数', '12'), ('排课总数', '100'), ('选课记录', '835')]
    for i, (label, val) in enumerate(metrics):
        x = 3.2 + (i%3)*3.5; y = 5.0 - (i//3)*2.0
        card = FancyBboxPatch((x, y-0.6), 3.0, 1.3, boxstyle="round,pad=0.1", facecolor='white', edgecolor='#DDD')
        ax.add_patch(card)
        ax.text(x+1.5, y+0.3, val, ha='center', fontsize=22, fontweight='bold', color='#1565C0')
        ax.text(x+1.5, y-0.2, label, ha='center', fontsize=10, color='#888')

    ax.set_title('图7-2  教务端数据概览页面', fontsize=FONT_TITLE, fontweight='bold', pad=15)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT_DIR, 'ui_admin_dashboard.png'), dpi=200, bbox_inches='tight', facecolor='white')
    plt.close(fig)

    # 学生选课页
    fig, ax = plt.subplots(figsize=(14, 6))
    ax.set_xlim(0, 14); ax.set_ylim(0, 6)
    ax.axis('off'); ax.set_facecolor('#E8ECF1')
    ax.text(7, 5.5, '📚 可选课程', fontsize=14, fontweight='bold', ha='center')
    hdr = ['排课ID', '课程名', '学分', '教师', '学期', '剩余名额']
    rows_data = [['12', '高等数学', '5.0', '张教授', '2025-2026-1', '15/30'],
                 ['25', '数据结构', '4.0', '李教授', '2025-2026-1', '8/25'],
                 ['38', '数据库原理', '3.5', '王教授', '2025-2026-1', '20/35']]
    all_data = [hdr] + rows_data
    table = ax.table(cellText=all_data, cellLoc='center', loc='upper center',
                     colWidths=[0.08, 0.16, 0.06, 0.12, 0.14, 0.10])
    table.auto_set_font_size(False)
    table.set_fontsize(9)
    table.scale(1.2, 1.6)
    for i in range(len(hdr)):
        table[0, i].set_facecolor('#1565C0')
        table[0, i].set_text_props(color='white', fontweight='bold')
    # 底部控件模拟
    ax.text(7, 1.0, '选择要选的排课  [▼ #12 高等数学 - 张教授 (5.0学分)]    [确认选课]',
            ha='center', fontsize=10, color='#555',
            bbox=dict(boxstyle='round', fc='white', ec='#DDD'))
    ax.set_title('图7-3  学生选课页面', fontsize=FONT_TITLE, fontweight='bold', pad=15)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT_DIR, 'ui_student_enroll.png'), dpi=200, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    print('[OK] UI截图')

# ============================================================
# 图8: 测试流程图
# ============================================================
def draw_test():
    fig, ax = plt.subplots(figsize=(14, 8))
    ax.set_xlim(0, 14); ax.set_ylim(0, 8)
    ax.axis('off'); ax.set_facecolor('#FAFAFA')

    nodes = [
        (7, 7.3, '测试开始', '#1565C0'),
        (7, 6.0, '数据库连接测试', '#42A5F5'),
        (3.5, 4.5, '学生端测试', '#66BB6A'),
        (10.5, 4.5, '教师端测试', '#FFA726'),
        (1.5, 3.0, '选课流程', '#EF5350'),
        (5.5, 3.0, '退选流程', '#EF5350'),
        (8.5, 3.0, '成绩录入', '#EF5350'),
        (12.5, 3.0, '批量导入', '#EF5350'),
        (3.5, 1.5, '异常场景\n（满额/重复/超期）', '#AB47BC'),
        (10.5, 1.5, '边界值\n（0分/100分/超限）', '#AB47BC'),
        (7, 0.3, '测试通过', '#2E7D32'),
    ]
    for x, y, label, color in nodes:
        w = 2.2 if '\n' not in label else 2.6
        h = 0.55 if '\n' not in label else 0.75
        rect = FancyBboxPatch((x-w/2, y-h/2), w, h, boxstyle="round,pad=0.08",
                              facecolor=color, edgecolor='#333', linewidth=1.5)
        ax.add_patch(rect)
        ax.text(x, y, label, ha='center', va='center', fontsize=FONT_SMALL, fontweight='bold', color='white')

    edges = [
        (7,7.0,7,6.3), (7,5.7,3.5,4.8), (7,5.7,10.5,4.8),
        (3.5,4.2,1.5,3.3), (3.5,4.2,5.5,3.3),
        (10.5,4.2,8.5,3.3), (10.5,4.2,12.5,3.3),
        (1.5,2.7,3.5,2.0), (5.5,2.7,3.5,2.0),
        (8.5,2.7,10.5,2.0), (12.5,2.7,10.5,2.0),
        (3.5,1.2,7,0.6), (10.5,1.2,7,0.6),
    ]
    for sx, sy, dx, dy in edges:
        ax.annotate('', xy=(dx, dy), xytext=(sx, sy),
                    arrowprops=dict(arrowstyle='->', color='#777', lw=1.5))

    ax.set_title('图8-1  系统测试流程图', fontsize=FONT_TITLE, fontweight='bold', pad=15)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT_DIR, 'test_flow.png'), dpi=200, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    print('[OK] 测试流程图')

if __name__ == '__main__':
    print('生成高清大图...')
    draw_er()
    draw_dfd()
    draw_arch()
    draw_modules()
    draw_tables()
    draw_explain()
    draw_ui()
    draw_test()
    print(f'完成！图片目录: {OUT_DIR}')
