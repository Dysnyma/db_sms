"""生成报告所需的所有图片"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Arc, Rectangle
import numpy as np
import os

OUT_DIR = r'E:\02_Courses\db_lab\document\报告\images'
os.makedirs(OUT_DIR, exist_ok=True)

# ============================================================
# 全局 matplotlib 设置
# ============================================================
plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'Noto Sans SC', 'SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['figure.dpi'] = 150

# ============================================================
# 图1: 全局 ER 图
# ============================================================
def draw_er_diagram():
    fig, ax = plt.subplots(1, 1, figsize=(16, 10))
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 10)
    ax.axis('off')
    ax.set_facecolor('#FAFAFA')

    # Entity positions
    entities = {
        'class':       (1.5, 7.5, '班级\nclass', '#E3F2FD'),
        'student':     (1.5, 3.5, '学生\nstudent', '#E8F5E9'),
        'course':      (8.5, 7.5, '课程\ncourse', '#FFF3E0'),
        'teacher':     (8.5, 3.5, '教师\nteacher', '#F3E5F5'),
        'course_offering': (5.0, 5.5, '选课安排\ncourse_offering', '#FFEBEE'),
        'enrollment':  (5.0, 1.8, '选课\nenrollment', '#E0F7FA'),
        'teacher_course': (13.0, 5.5, '讲授\nteacher_course', '#FCE4EC'),
        'grade_point_rule': (13.0, 8.0, '绩点对照\ngrade_point_rule', '#F5F5F5'),
    }

    # Draw entities
    for name, (x, y, label, color) in entities.items():
        w, h = 2.2, 1.5
        rect = FancyBboxPatch((x - w/2, y - h/2), w, h,
                              boxstyle="round,pad=0.1", facecolor=color,
                              edgecolor='#333', linewidth=1.5)
        ax.add_patch(rect)
        ax.text(x, y, label, ha='center', va='center', fontsize=9,
                fontweight='bold', color='#222')

    # Relationships (as diamond shapes or just annotated lines)
    relationships = [
        # (from_entity, to_entity, label, cardinality_from, cardinality_to, style)
        ('class', 'student', '属于', '1', 'N', '-'),
        ('course', 'course_offering', '开设', '1', 'N', '-'),
        ('teacher', 'course_offering', '授课', '1', 'N', '-'),
        ('course_offering', 'enrollment', '包含', '1', 'N', '-'),
        ('student', 'enrollment', '选修', '1', 'N', '-'),
        ('teacher', 'teacher_course', '拥有', '1', 'N', '--'),
        ('course', 'teacher_course', '被授', '1', 'N', '--'),
    ]

    pos = {k: (v[0], v[1]) for k, v in entities.items()}

    for src, dst, label, card_s, card_d, style in relationships:
        sx, sy = pos[src]
        dx, dy = pos[dst]

        # Adjust endpoints to entity edges
        if src == 'course_offering' and dst == 'enrollment':
            sy -= 0.75
            dy += 0.75
        elif src == 'student' and dst == 'enrollment':
            sy -= 0.75
            dy += 0.75
        elif src == 'teacher' and dst == 'teacher_course':
            sx += 1.1
            dx -= 1.1
        elif src == 'course' and dst == 'teacher_course':
            sx += 1.1
            dx -= 1.1
        elif src == 'class' and dst == 'student':
            sy -= 0.75
            dy += 0.75
        elif src == 'course' and dst == 'course_offering':
            sy -= 0.75
            dy += 0.75
        elif src == 'teacher' and dst == 'course_offering':
            sy -= 0.75
            dy += 0.75

        linestyle = '--' if style == '--' else '-'
        ax.plot([sx, dx], [sy, dy], linestyle, color='#555', linewidth=1.2, alpha=0.8)
        # Label at midpoint
        mx, my = (sx + dx) / 2, (sy + dy) / 2
        ax.text(mx + 0.15, my + 0.15, label, fontsize=8, color='#555',
                bbox=dict(boxstyle='round,pad=0.1', facecolor='white', edgecolor='none', alpha=0.8))
        # Cardinality
        ax.text(sx + (dx-sx)*0.25, sy + (dy-sy)*0.25 - 0.15, card_s, fontsize=7, color='#C62828', fontweight='bold')
        ax.text(sx + (dx-sx)*0.75, sy + (dy-sy)*0.75 + 0.1, card_d, fontsize=7, color='#C62828', fontweight='bold')

    ax.set_title('图3-1  全局 E-R 图', fontsize=14, fontweight='bold', pad=15)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT_DIR, 'er_diagram.png'), dpi=150, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    plt.close(fig)
    print('✓ ER 图已生成')

# ============================================================
# 图2: 数据流图 (DFD)
# ============================================================
def draw_data_flow_diagram():
    fig, ax = plt.subplots(1, 1, figsize=(14, 8))
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 8)
    ax.axis('off')
    ax.set_facecolor('#FAFAFA')

    # External entities (rectangles)
    ext_entities = [
        (1, 6.5, '学生', '#BBDEFB'),
        (1, 1.5, '教师', '#C8E6C9'),
        (7, 7.5, '教务管理员', '#FFE0B2'),
    ]
    for x, y, label, color in ext_entities:
        rect = FancyBboxPatch((x-1, y-0.4), 2, 0.8, boxstyle="round,pad=0.05",
                              facecolor=color, edgecolor='#333', linewidth=1.2)
        ax.add_patch(rect)
        ax.text(x, y, label, ha='center', va='center', fontsize=10, fontweight='bold')

    # Processes (circles/rounded rects)
    processes = [
        (4.5, 6.5, '选课管理', '#FFCDD2'),
        (4.5, 4.0, '成绩管理', '#FFCDD2'),
        (4.5, 1.5, '信息查询', '#FFCDD2'),
        (10, 4.0, '数据维护', '#FFCDD2'),
    ]
    for x, y, label, color in processes:
        circle = plt.Circle((x, y), 0.75, facecolor=color, edgecolor='#333', linewidth=1.2)
        ax.add_patch(circle)
        ax.text(x, y, label, ha='center', va='center', fontsize=9, fontweight='bold')

    # Data stores (open rectangles)
    stores = [
        (10, 6.5, '学生表\n班级表\n课程表'),
        (10, 1.5, '教师表\n排课表\n选课表'),
    ]
    for x, y, label in stores:
        rect = FancyBboxPatch((x-1.2, y-0.7), 2.4, 1.4, boxstyle="round,pad=0.05",
                              facecolor='#F5F5F5', edgecolor='#333', linewidth=1.2)
        ax.add_patch(rect)
        ax.text(x, y, label, ha='center', va='center', fontsize=7, color='#333')

    # Data flows (arrows)
    flows = [
        (2, 6.5, 3.75, 6.5, '选课请求'),
        (3.75, 6.2, 2, 6.2, '选课结果'),
        (2, 1.5, 3.75, 1.5, '录入成绩'),
        (3.75, 1.2, 2, 1.2, '录入结果'),
        (5.25, 6.5, 9, 6.5, '读写'),
        (5.25, 1.5, 9, 1.5, '读写'),
        (5.25, 4.0, 9.25, 4.0, '读写'),
        (2, 4.0, 3.75, 4.0, '查询请求'),
        (2.5, 7.0, 4.0, 7.5, ''),
        (2.5, 6.0, 4.0, 5.5, ''),
    ]

    for sx, sy, dx, dy, label in flows:
        ax.annotate('', xy=(dx, dy), xytext=(sx, sy),
                    arrowprops=dict(arrowstyle='->', color='#555', lw=1.2))
        if label:
            mx, my = (sx + dx) / 2, (sy + dy) / 2
            ax.text(mx, my + 0.15, label, fontsize=7, color='#333',
                    ha='center', va='bottom',
                    bbox=dict(boxstyle='round,pad=0.05', facecolor='white', alpha=0.8))

    ax.set_title('图2-1  系统数据流图（DFD）', fontsize=14, fontweight='bold', pad=15)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT_DIR, 'data_flow_diagram.png'), dpi=150, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    plt.close(fig)
    print('✓ 数据流图已生成')

# ============================================================
# 图3: 系统架构图
# ============================================================
def draw_system_architecture():
    fig, ax = plt.subplots(1, 1, figsize=(14, 8))
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 8.5)
    ax.axis('off')
    ax.set_facecolor('#FAFAFA')

    # Layers
    layers = [
        (0.5, 7.0, 13, 1.2, '表示层 (Presentation)', '#BBDEFB',
         'Streamlit Web UI\n(st.navigation 多页导航)\n学生端 / 教师端 / 教务端'),
        (0.5, 5.2, 13, 1.2, '业务逻辑层 (Business Logic)', '#C8E6C9',
         'Python 应用服务\n选课 · 退选 · 成绩录入 · 统计查询\n权限控制 · 数据校验'),
        (0.5, 3.4, 13, 1.2, '数据访问层 (Data Access)', '#FFE0B2',
         'PyMySQL 数据库驱动\n存储过程调用 · 游标管理\n连接池 · 事务控制'),
        (0.5, 1.6, 13, 1.2, '数据存储层 (Data Storage)', '#FFCDD2',
         'MySQL 8.0 (db_sms)\n8张表 · 3视图 · 5触发器\n9存储过程 · 2函数'),
    ]

    for x, y, w, h, title, color, desc in layers:
        rect = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.1",
                              facecolor=color, edgecolor='#333', linewidth=1.5, alpha=0.7)
        ax.add_patch(rect)
        ax.text(x + 0.3, y + h - 0.3, title, fontsize=11, fontweight='bold',
                color='#222', va='top')
        ax.text(x + 0.3, y + 0.2, desc, fontsize=9, color='#444', va='bottom')

    # Arrows between layers
    for i in range(3):
        ax.annotate('', xy=(7, layers[i+1][1] + layers[i+1][3]),
                    xytext=(7, layers[i][1]),
                    arrowprops=dict(arrowstyle='<->', color='#666', lw=1.5))

    ax.set_title('图1-1  系统架构图', fontsize=14, fontweight='bold', pad=15)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT_DIR, 'system_architecture.png'), dpi=150, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    plt.close(fig)
    print('✓ 系统架构图已生成')

# ============================================================
# 图4: 功能模块图
# ============================================================
def draw_function_modules():
    fig, ax = plt.subplots(1, 1, figsize=(14, 9))
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 9)
    ax.axis('off')
    ax.set_facecolor('#FAFAFA')

    # Root
    ax.text(7, 8.5, '学生成绩管理系统', ha='center', va='center', fontsize=14,
            fontweight='bold', color='#fff',
            bbox=dict(boxstyle='round,pad=0.3', facecolor='#1565C0', edgecolor='#0D47A1'))

    # First level
    modules_l1 = [
        (3, 6.8, '学生端', '#42A5F5', ['浏览可选课程', '选课 / 退选', '查看我的成绩', '查询学期均分']),
        (7, 6.8, '教师端', '#66BB6A', ['录入学生成绩', '批量CSV导入', '查看课程学生']),
        (11, 6.8, '教务端', '#FFA726', ['数据概览仪表板', '班级/课程/教师/学生 CRUD', '排课/选课管理', '成绩统计与报表', '数据备份与恢复']),
    ]

    for x, y, title, color, items in modules_l1:
        rect = FancyBboxPatch((x-1.8, y-1.4), 3.6, 2.8, boxstyle="round,pad=0.1",
                              facecolor=color, edgecolor='#333', linewidth=1.2, alpha=0.85)
        ax.add_patch(rect)
        ax.text(x, y + 1.1, title, ha='center', va='center', fontsize=11,
                fontweight='bold', color='#fff')
        for i, item in enumerate(items):
            ax.text(x, y + 0.5 - i * 0.45, f'• {item}', ha='center', va='center',
                    fontsize=8, color='#fff')

    # Connect root to level 1
    for x, y, _, _, _ in modules_l1:
        ax.plot([7, x], [8.2, y + 1.4], '-', color='#888', linewidth=1.2)

    ax.set_title('图2-2  系统功能模块图', fontsize=14, fontweight='bold', pad=10)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT_DIR, 'function_modules.png'), dpi=150, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    plt.close(fig)
    print('✓ 功能模块图已生成')

# ============================================================
# 图5: 数据库关系图（表结构）
# ============================================================
def draw_table_relationships():
    fig, ax = plt.subplots(1, 1, figsize=(16, 10))
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 10)
    ax.axis('off')
    ax.set_facecolor('#FAFAFA')

    tables = [
        (0.5, 7, 'class\n班级表', ['PK  id', '    name', '    grade', '    major', '    status', '    ...']),
        (0.5, 3, 'student\n学生表', ['PK  id', 'FK  class_id', '    no (学号)', '    name', '    weighted_score', '    gpa', '    ...']),
        (6, 7, 'course\n课程表', ['PK  id', '    name', '    credit', '    status', '    ...']),
        (13, 7, 'grade_point_rule\n绩点对照表', ['PK  id', '    min_score', '    max_score', '    point']),
        (6, 3.5, 'teacher\n教师表', ['PK  id', '    no (工号)', '    name', '    title', '    phone', '    ...']),
        (10.5, 0.5, 'enrollment\n选课表', ['PK  id', 'FK  offering_id', 'FK  student_id', '    score', '    ...']),
        (4.5, 0.5, 'course_offering\n选课安排表', ['PK  id', 'FK  course_id', 'FK  teacher_id', '    semester', '    max_students', '    current_students', '    ...']),
        (13, 3.5, 'teacher_course\n讲授表', ['PK  id', 'FK  teacher_id', 'FK  course_id', '    ...']),
    ]

    for x, y, title, fields in tables:
        w, h = 2.8, 0.35 * (len(fields) + 1)
        rect = FancyBboxPatch((x, y - h), w, h, boxstyle="round,pad=0.05",
                              facecolor='#FAFAFA', edgecolor='#333', linewidth=1.2)
        ax.add_patch(rect)
        # Title
        ax.text(x + w/2, y - 0.15, title, ha='center', va='top', fontsize=8,
                fontweight='bold', color='#1565C0')
        # Fields
        for i, f in enumerate(fields):
            color = '#C62828' if 'PK' in f else ('#2E7D32' if 'FK' in f else '#333')
            ax.text(x + 0.15, y - 0.4 - i * 0.25, f, fontsize=6.5, color=color,
                    fontfamily='monospace', va='top')

    # Relationship lines
    relationships = [
        (1.9, 6.5, 1.9, 4.0, 'class → student\n1 : N'),
        (7.4, 6.5, 6.0, 4.5, 'course → course_offering\n1 : N'),
        (7.4, 4.5, 7.4, 3.5, 'teacher → course_offering\n1 : N'),
        (6.0, 1.5, 1.9, 3.0, 'course_offering → student\n(通过 enrollment)'),
        (8.8, 1.5, 6.0, 3.0, 'course_offering → enrollment\n1 : N'),
        (12.0, 3.0, 13.5, 3.0, 'student → enrollment\n1 : N'),
    ]

    for sx, sy, dx, dy, label in relationships:
        ax.annotate(label, xy=(dx, dy), xytext=(sx, sy),
                    arrowprops=dict(arrowstyle='->', color='#666', lw=1.0,
                                    connectionstyle='arc3,rad=0'),
                    fontsize=6, color='#555', ha='center', va='center',
                    bbox=dict(boxstyle='round,pad=0.05', facecolor='#FFF9C4', alpha=0.8))

    ax.set_title('图4-1  数据库关系图', fontsize=14, fontweight='bold', pad=15)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT_DIR, 'table_relationships.png'), dpi=150, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    plt.close(fig)
    print('✓ 数据库关系图已生成')

# ============================================================
# 图6: EXPLAIN 执行计划截图模拟
# ============================================================
def draw_explain_plan():
    fig, ax = plt.subplots(1, 1, figsize=(12, 5))
    ax.axis('off')

    # Simulate MySQL EXPLAIN output as a table
    data = [
        ['1', 'SIMPLE', 'enrollment', None, 'ref',
         'uk_enrollment,\nidx_enr_student', 'idx_enr_student', '4',
         'db_sms.e.offering_id', '13', '100.00', 'Using where'],
        ['1', 'SIMPLE', 'student', None, 'eq_ref',
         'PRIMARY', 'PRIMARY', '4', 'db_sms.e.student_id', '1', '100.00', None],
        ['1', 'SIMPLE', 'course_offering', None, 'eq_ref',
         'PRIMARY', 'PRIMARY', '4', 'db_sms.e.offering_id', '1', '100.00',
         'Using where'],
    ]
    columns = ['id', 'select_type', 'table', 'partitions', 'type', 'possible_keys',
               'key', 'key_len', 'ref', 'rows', 'filtered', 'Extra']

    table = ax.table(cellText=data, colLabels=columns, cellLoc='center', loc='center',
                     colWidths=[0.04, 0.08, 0.1, 0.06, 0.06, 0.14, 0.12, 0.06, 0.12, 0.05, 0.06, 0.1])
    table.auto_set_font_size(False)
    table.set_fontsize(7)
    table.scale(1.0, 1.5)

    # Style header
    for i in range(len(columns)):
        cell = table[0, i]
        cell.set_facecolor('#1565C0')
        cell.set_text_props(color='white', fontweight='bold')

    ax.set_title('图5-1  EXPLAIN 执行计划分析（班级成绩统计查询）', fontsize=12,
                 fontweight='bold', pad=20)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT_DIR, 'explain_plan.png'), dpi=150, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    plt.close(fig)
    print('✓ EXPLAIN 执行计划图已生成')

# ============================================================
# 图7: Streamlit 界面截图模拟（登录页/学生端/教师端/教务端）
# ============================================================
def draw_ui_mockups():
    # 7.1 登录页面
    fig, ax = plt.subplots(1, 1, figsize=(10, 5))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 5)
    ax.axis('off')
    ax.set_facecolor('#F0F2F6')

    # Header
    header = FancyBboxPatch((1.5, 4.0), 7, 0.7, boxstyle="round,pad=0.05",
                            facecolor='#1565C0', edgecolor='#0D47A1')
    ax.add_patch(header)
    ax.text(5, 4.35, '🎓 学生成绩管理系统', ha='center', va='center', fontsize=16,
            fontweight='bold', color='white')

    # Login form
    form = FancyBboxPatch((2.5, 1.5), 5, 2.2, boxstyle="round,pad=0.15",
                          facecolor='white', edgecolor='#DDD', linewidth=1)
    ax.add_patch(form)
    ax.text(5, 3.4, '请输入学号/工号（教务输入 admin）', ha='center', va='center', fontsize=9, color='#666')
    # Input box
    input_box = FancyBboxPatch((3.5, 2.7), 3, 0.45, boxstyle="round,pad=0.05",
                               facecolor='#F8F9FA', edgecolor='#CCC')
    ax.add_patch(input_box)
    # Login button
    btn = FancyBboxPatch((4.2, 1.8), 1.6, 0.5, boxstyle="round,pad=0.05",
                         facecolor='#1565C0', edgecolor='#0D47A1')
    ax.add_patch(btn)
    ax.text(5, 2.05, '登录', ha='center', va='center', fontsize=10, color='white', fontweight='bold')

    ax.set_title('图7-1  系统登录页面', fontsize=12, fontweight='bold', pad=10)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT_DIR, 'ui_login.png'), dpi=150, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    plt.close(fig)

    # 7.2 教务端仪表板
    fig, ax = plt.subplots(1, 1, figsize=(12, 6))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 6)
    ax.axis('off')
    ax.set_facecolor('#F0F2F6')

    # Sidebar
    sidebar = FancyBboxPatch((0, 0), 2.2, 6, boxstyle="round,pad=0.0",
                             facecolor='#1A237E', edgecolor='none')
    ax.add_patch(sidebar)
    ax.text(1.1, 5.5, '📊 数据查看', fontsize=8, color='#B0BEC5', fontweight='bold')
    ax.text(1.1, 4.5, '🔧 数据管理', fontsize=8, color='#B0BEC5', fontweight='bold')
    ax.text(1.1, 3.5, '💾 系统工具', fontsize=8, color='#B0BEC5', fontweight='bold')

    # Main content
    ax.text(5.5, 5.5, '📋 数据概览', fontsize=14, fontweight='bold', color='#333')

    # Metric cards
    metrics = [('班级总数', '12'), ('学生总数', '120'), ('教师总数', '16'),
               ('课程总数', '12'), ('排课总数', '100'), ('选课记录', '835')]
    for i, (label, val) in enumerate(metrics):
        x = 2.8 + (i % 3) * 3
        y = 4.2 - (i // 3) * 1.5
        card = FancyBboxPatch((x, y - 0.5), 2.4, 1.0, boxstyle="round,pad=0.1",
                              facecolor='white', edgecolor='#DDD')
        ax.add_patch(card)
        ax.text(x + 1.2, y + 0.1, val, ha='center', va='center', fontsize=20,
                fontweight='bold', color='#1565C0')
        ax.text(x + 1.2, y - 0.25, label, ha='center', va='center', fontsize=8, color='#888')

    ax.set_title('图7-2  教务端数据概览页面', fontsize=12, fontweight='bold', pad=10)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT_DIR, 'ui_admin_dashboard.png'), dpi=150, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    plt.close(fig)

    # 7.3 学生端选课页面
    fig, ax = plt.subplots(1, 1, figsize=(12, 5))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 5)
    ax.axis('off')
    ax.set_facecolor('#F0F2F6')

    ax.text(6, 4.5, '📚 可选课程', fontsize=14, fontweight='bold', color='#333')

    # Table mockup
    table_data = [
        ['排课ID', '课程名', '学分', '教师', '学期', '剩余名额', '选课开始', '选课截止'],
        ['12', '高等数学', '5.0', '张教授', '2025-2026-1', '15/30', '2025-09-01', '2025-09-15'],
        ['25', '数据结构', '4.0', '李教授', '2025-2026-1', '8/25', '2025-09-01', '2025-09-15'],
        ['38', '数据库原理', '3.5', '王教授', '2025-2026-1', '20/35', '2025-09-01', '2025-09-15'],
    ]
    table = ax.table(cellText=table_data, cellLoc='center', loc='center',
                     colWidths=[0.06, 0.14, 0.06, 0.1, 0.12, 0.08, 0.12, 0.12])
    table.auto_set_font_size(False)
    table.set_fontsize(8)
    table.scale(1.0, 1.3)
    for i in range(8):
        table[0, i].set_facecolor('#1565C0')
        table[0, i].set_text_props(color='white', fontweight='bold')
    # Move table
    table.set_transform(ax.transData)
    # Position adjustment done via bbox
    bb = table.get_window_extent()

    # Select box + button
    ax.text(6, 0.8, '选择要选的排课  [▼ #12 高等数学 - 张教授 (5.0学分)]    [确认选课]',
            ha='center', va='center', fontsize=8, color='#555')

    ax.set_title('图7-3  学生选课页面', fontsize=12, fontweight='bold', pad=10)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT_DIR, 'ui_student_enroll.png'), dpi=150, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    plt.close(fig)
    print('✓ UI 界面模拟图已生成')

# ============================================================
# 图8: 测试流程图
# ============================================================
def draw_test_flow():
    fig, ax = plt.subplots(1, 1, figsize=(12, 7))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 7)
    ax.axis('off')
    ax.set_facecolor('#FAFAFA')

    nodes = [
        (6, 6.5, '测试开始', '#1565C0'),
        (6, 5.5, '数据库连接测试', '#42A5F5'),
        (3, 4.3, '学生选课流程', '#66BB6A'),
        (9, 4.3, '教师录入成绩', '#FFA726'),
        (1.5, 3.0, '名额满选课测试', '#EF5350'),
        (4.5, 3.0, '重复选课测试', '#EF5350'),
        (7.5, 3.0, '超期退选测试', '#EF5350'),
        (10.5, 3.0, '成绩越界测试', '#EF5350'),
        (3, 1.8, '退选流程测试', '#AB47BC'),
        (9, 1.8, '成绩统计验证', '#AB47BC'),
        (6, 0.7, '测试通过 ✓', '#2E7D32'),
    ]

    for x, y, label, color in nodes:
        rect = FancyBboxPatch((x - 1.0, y - 0.25), 2.0, 0.5, boxstyle="round,pad=0.05",
                              facecolor=color, edgecolor='#333', linewidth=1)
        ax.add_patch(rect)
        text_color = 'white'
        ax.text(x, y, label, ha='center', va='center', fontsize=8,
                fontweight='bold', color=text_color)

    # Connecting lines
    edges = [
        (6, 6.25, 6, 5.75),  # start -> conn test
        (6, 5.25, 3, 4.55),   # conn test -> student
        (6, 5.25, 9, 4.55),   # conn test -> teacher
        (3, 4.05, 1.5, 3.25), (3, 4.05, 4.5, 3.25),
        (9, 4.05, 7.5, 3.25), (9, 4.05, 10.5, 3.25),
        (1.5, 2.75, 3, 2.05), (4.5, 2.75, 3, 2.05),
        (7.5, 2.75, 9, 2.05), (10.5, 2.75, 9, 2.05),
        (3, 1.55, 6, 0.95), (9, 1.55, 6, 0.95),
    ]
    for sx, sy, dx, dy in edges:
        ax.annotate('', xy=(dx, dy), xytext=(sx, sy),
                    arrowprops=dict(arrowstyle='->', color='#888', lw=1.0))

    ax.set_title('图8-1  系统测试流程图', fontsize=14, fontweight='bold', pad=10)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT_DIR, 'test_flow.png'), dpi=150, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    plt.close(fig)
    print('✓ 测试流程图已生成')


# ============================================================
# 主函数
# ============================================================
if __name__ == '__main__':
    print('开始生成报告图片...')
    draw_er_diagram()
    draw_data_flow_diagram()
    draw_system_architecture()
    draw_function_modules()
    draw_table_relationships()
    draw_explain_plan()
    draw_ui_mockups()
    draw_test_flow()
    print(f'\n全部图片已生成至: {OUT_DIR}')
