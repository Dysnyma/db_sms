"""3.5 工作日志 —— 结构化版本，每条记录独立成段"""
import os
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "3.5工作日志.docx")
doc = Document()

style = doc.styles['Normal']
style.font.name = '宋体'; style.font.size = Pt(11)
style.element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')
style.paragraph_format.line_spacing = 1.35

for sec in doc.sections:
    sec.top_margin = Cm(2.0); sec.bottom_margin = Cm(1.5)
    sec.left_margin = Cm(2.5); sec.right_margin = Cm(2.5)

def sf(run, name):
    rPr = run._element.get_or_add_rPr()
    rf = rPr.find(qn('w:rFonts'))
    if rf is None: rf = OxmlElement('w:rFonts'); rPr.append(rf)
    rf.set(qn('w:eastAsia'), name)

def H(text, level=1):
    h = doc.add_heading(text, level=level)
    for r in h.runs:
        r.font.name = '黑体'; sf(r, '黑体')
        if level == 1: r.font.size = Pt(16); r.font.color.rgb = RGBColor(0x1A, 0x52, 0x76)
        elif level == 2: r.font.size = Pt(13); r.font.color.rgb = RGBColor(0x2E, 0x86, 0xC1)

def tag(text):
    p = doc.add_paragraph()
    run = p.add_run(f'  {text}  ')
    run.font.size = Pt(9); run.bold = True; run.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
    sf(run, '微软雅黑')
    shading = OxmlElement('w:shd')
    shading.set(qn('w:fill'), '2E86C1'); shading.set(qn('w:val'), 'clear')
    p._element.get_or_add_pPr().append(shading)
    p.paragraph_format.space_before = Pt(4); p.paragraph_format.space_after = Pt(2)

def P(text, sz=10.5):
    p = doc.add_paragraph()
    p.paragraph_format.line_spacing = 1.35
    p.paragraph_format.first_line_indent = Cm(0.74)
    run = p.add_run(text); run.font.size = Pt(sz); sf(run, '宋体')
    return p

# ══ 封面 ══
for _ in range(5): doc.add_paragraph()
p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = p.add_run('数据库系统课程设计\n工作日志'); r.font.size = Pt(26); r.bold = True
r.font.color.rgb = RGBColor(0x1A, 0x52, 0x76); sf(r, '黑体')
doc.add_paragraph()
p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = p.add_run('学生姓名：蔡坤灿    专业：计算机科学与技术')
r.font.size = Pt(14); sf(r, '宋体')
for _ in range(6): doc.add_paragraph()
p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = p.add_run('2026年7月'); r.font.size = Pt(14); sf(r, '宋体')
doc.add_page_break()

# ════════════════════════════════════════
# 7月6日
# ════════════════════════════════════════
H('第七日：7月6日 — 选题切换与项目初始化', level=1)

tag('1.1 确定选题方向')
P('本课程设计最初选定题目一"进销存管理系统"，并完成了 17 张表、8 个视图、7 个触发器、15 个存储过程的完整数据库设计，累积 SQL 代码量约 800 行。完成全部建表 DDL 和初始数据脚本后，经综合评估决定切换至题目二"学生成绩管理系统"。原进销存代码完整保留至 archive/ 目录作为学习参考，新数据库命名为 db_sms（Student Management System）。')

tag('1.2 搭建日志与记忆体系')
P('建立三线并行的日志体系：开发日志（记录实际操作时间线和产出物）、问答日志（记录与 AI 交互的问题与回答）、AI 修正日志（记录 AI 错误输出与人工修正过程）。创建 CLAUDE.md 项目说明文件与 Memory 记忆系统，记录项目概况、设计规范、关键决策，确保 AI 在跨会话对话中保持上下文一致。')

tag('1.3 配置开发环境')
P('配置 VS Code 开发环境：关闭 SQL 文件保存时的自动格式化功能，避免 DDL 脚本被误格式化。确定项目编码规范：全小写+下划线表名、utf8mb4 字符集、utf8mb4_unicode_ci 排序规则、InnoDB 存储引擎、INT 自增主键、全部表采用逻辑删除（is_deleted 字段）。')

doc.add_page_break()

# ════════════════════════════════════════
# 7月7日
# ════════════════════════════════════════
H('第一天：7月7日 — 数据库设计与 CLI 应用骨架搭建', level=1)

tag('2.1 概念结构设计')
P('完成实体关系模型的核心决策。学生与班级之间采用 1:N 关系，在 student 表加 class_id 外键，不建中间表。学生与课程之间为 M:N 关系，通过 enrollment 中间表实现，该中间表同时承担成绩存储功能。课程与教师之间为 M:N 关系，采用 teacher_course（讲授资格）和 course_offering（实际排课）两层设计，实现逻辑分离。')

tag('2.2 建表 DDL 设计')
P('完成 8 张表的 DDL 设计。class（班级）含 name/grade/major 字段。student（学生）含 name/no（学号，唯一索引）/class_id（外键）/weighted_score（学籍分）/gpa（绩点分）字段。course（课程）含 name/credit。teacher（教师）含 name/no（工号）/title（职称，可空）/phone（电话，可空）。course_offering（排课）含 course_id+teacher_id+semester+max_students+三个时间窗口。enrollment（选课）含 offering_id+student_id（联合唯一索引）/score（可空）。teacher_course（讲授关系）含 teacher_id+course_id（联合唯一索引）。grade_point_rule（绩点规则）含 min_score/max_score/point。')

tag('2.3 视图开发')
P('完成 3 个视图的开发。v_student_message 封装学生与班级基本信息联查，不暴露学籍分/GPA。v_course_plan 作为学生选课视图，输出课程名、教师名、剩余名额和选课状态（未开始/选课中/已截止/已结束），是选课功能的核心数据源。v_enrollment 封装选课详情的五表联查（选课+学生+排课+课程+教师）。')

tag('2.4 存储函数开发')
P('将存储过程中重复出现的"学号→学生 ID"和"工号→教师 ID"转换逻辑抽取为两个公共函数：fn_get_student_id 和 fn_get_teacher_id。采用 COLLATE utf8mb4_unicode_ci 确保字符串比较兼容排序规则。函数被 sp_enroll、sp_unenroll、sp_grade_input、teacher_tui 等多个模块复用。')

tag('2.5 选课与退选存储过程开发')
P('sp_enroll 实现选课事务。包含 4 步校验：①fn_get_student_id 校验学生存在性；②检查排课在有效期（NOW BETWEEN enroll_start AND enroll_end）；③检查未重复选同一排课；④检查未选同一课程的不同教师（JOIN course_offering 查 course_id）。满足条件后 INSERT enrollment，触发器自动完成名额检查和人数更新。sp_unenroll 逻辑类似，校验后将 enrollment.is_deleted 更新为 1，触发器自动减人数。')

tag('2.6 成绩录入存储过程开发')
P('sp_grade_input 实现成绩录入。包含三重身份校验：①通过 fn_get_teacher_id 校验教师工号存在性；②校验该教师是该排课的授课教师（WHERE co.teacher_id = 教师ID AND co.id = plan_id）；③校验成绩录入截止时间（NOW <= co.grade_deadline）。校验通过后 UPDATE enrollment SET score，触发器自动重算学籍分和 GPA。')

tag('2.7 统计报表存储过程开发')
P('完成 5 个统计报表 SP。sp_student_roster 按班级输出学生学籍分和 GPA。sp_class_grade_report 统计某班某课程的平均分、最高分、最低分、及格率。sp_student_semester_avg 按学期聚合某学生的课程数和平均分。sp_teacher_info 查询单个教师的排课数、选课学生数和已录入成绩数。sp_teacher_list 列出全部教师的授课统计并按排课数降序排列。')

tag('2.8 触发器开发')
P('完成 5 个触发器的开发。trg_enrollment_before_insert 在 INSERT 前检查名额，使用 FOR UPDATE 行级锁防止并发超卖。trg_enrollment_after_insert 在 INSERT 后更新排课人数+1。trg_enrollment_after_update 检测逻辑删除（is_deleted: 0→1）时更新人数-1。trg_enrollment_after_insert_score 和 trg_enrollment_after_update_score 在成绩变化时自动重算学籍分（加权平均）和 GPA（学分绩点加权平均）。')

tag('2.9 排序规则冲突修复')
P('MySQL 8.0 默认排序规则为 utf8mb4_0900_ai_ci，与数据库的 utf8mb4_unicode_ci 不兼容，存储过程执行时报错 1267。修复方案：在 pymysql 连接参数中指定 collation=utf8mb4_unicode_ci，并在所有存储过程和函数的字符串比较字段后显式加 COLLATE utf8mb4_unicode_ci 子句。')

tag('2.10 Python CLI 骨架搭建')
P('创建完整的命令行交互系统。main.py 作为统一入口。auth.py 处理登录认证，支持 admin、教师工号、学生学号三种身份识别。utils.py 封装 render_menu（数据驱动菜单）、show_table（中英文自动对齐）、Paginator（分页器）、confirm（确认）、cls（清屏）、pause（暂停）等基础设施。角色模块按 student_tui（学生功能）、teacher_tui（教师功能）、admin（教务功能）分类管理。tester.py 作为测试员跳板，可切换任意角色身份。')

tag('2.11 AI 辅助开发与修正记录')
P('AI 生成了 DDL 和存储过程的框架代码，但经人工审核发现多处问题：course_offering 的 effective_time 字段与 enroll_start_time 语义重复（已删除）；enrollment 同时存在 enroll_time 和 create_time（已删除重复字段）；sp_enroll 未能检查同一课程不同教师的排课问题（已新增第 4 步校验）；sp_show_courses 同样存在该问题（已新增 course_id NOT IN 子查询）；tester.py 自建子菜单与角色代码大量重复（已精简为 83 行跳板）。')

doc.add_page_break()

# ════════════════════════════════════════
# 7月8日
# ════════════════════════════════════════
H('第二天：7月8日 — CLI 功能完整实现与 Streamlit 起步', level=1)

tag('3.1 六大实体 CRUD 开发')
P('完成班级、课程、教师、学生、排课、选课六大实体的增删改查功能。新增时校验必填字段和外键约束。修改采用逐字段交互模式，每字段显示当前值，回车保留原值。删除采用逻辑删除（SET is_deleted=1）。教师管理的职称和电话设计为可空字段。学生新增时列出可选班级列表。排课新增时自动筛选有资格的教师。')

tag('3.2 分页器组件推广')
P('将 Paginator 分页器组件推广至十余处列表展示场景：5 个管理菜单、班级学生名单、教师列表、我的成绩、可选课程列表、成绩录入排课选择、课程学生列表等。每页固定显示 10 条记录，支持上一页/下一页翻页。')

tag('3.3 教师成绩录入流程优化')
P('教师成绩录入改为两步分页模式：第一步使用分页器展示该教师的全部排课，显示每门课的已选人数和上限；第二步进入循环录入界面，输入学号后自动校验是否在选课名单中，录入完成后自动刷新成绩列表。支持 CSV 文件批量导入，逐行调用 sp_grade_input 并反馈处理结果。')

tag('3.4 Streamlit 双界面起步')
P('开始构建 Streamlit Web 界面。app.py 采用 session_state 管理用户登录状态，st.navigation 实现多页导航。完成学生端 5 个页面（可选课程、选课、退选、我的成绩、学期均分）和教师端 3 个页面（录入成绩、批量 CSV 上传、查看课程学生）。')

tag('3.5 代码质量优化')
P('tester.py 从 175 行自建子菜单精简为 83 行跳板，直接调用真实 menu 函数消除重复代码。为 my_grades 和 semester_avg 函数增加 paged 参数，支持 CLI 和 Streamlit 双模式调用。重构 import 路径，解决 core/ 模块在双界面下的导入兼容性问题。')

doc.add_page_break()

# ════════════════════════════════════════
# 7月9日
# ════════════════════════════════════════
H('第三天：7月9日 — Streamlit 教务端页面开发与架构迭代', level=1)

tag('4.1 教务端 14 页面开发')
P('完成教务端全部 Streamlit 页面。查询统计类 6 个（数据概览、班级学生名单、班级成绩统计、班级成绩明细、教师信息、教师列表）。数据管理类 6 个（班级管理、课程管理、教师管理、学生管理、排课管理、选课管理）。系统工具类 2 个（备份、恢复）。各页面复用 CLI 阶段开发的查询函数和存储过程。')

tag('4.2 管理页面组件架构三次重构')
P('管理页面的组件架构经历了三次重大迭代。第一次使用 st.tabs 按新增/修改/删除分 tab，发现 Streamlit 同时渲染全部 tab 导致组件互相干扰（如一个 tab 中的 selectbox 值影响其他 tab），改用 st.radio 单模式渲染。第二次使用 st.form + st.form_submit_button 包裹表单，发现动态 widget key 下预填值不更新、保存按钮无效，全部改为 st.button + 动态 key + session_state 消息传递。第三次发现操作成功后消息被 st.rerun 清掉，改用 st.toast 弹窗通知。')

tag('4.3 备份恢复功能加固')
P('备份命令补全 --routines（存储过程）、--triggers（触发器）、--add-drop-table（恢复前先 DROP）。恢复功能弃用 DROP DATABASE 方式，改用 SET FOREIGN_KEY_CHECKS=0 包裹 SQL 文件，避免外键约束中断恢复。增加 Windows tempfile 临时文件处理，解决管道死锁。')

tag('4.4 连接池配置')
P('引入 SQLAlchemy QueuePool 管理数据库连接。配置 pool_size=5（常驻连接数）、max_overflow=10（峰值连接数）、pool_pre_ping=True（取连接前自动检测）、pool_recycle=3600（1 小时回收）。_make_page 包装器使用 try/except/finally 模式，异常时先 rollback 再归还连接，防止未决事务污染连接池。')

doc.add_page_break()

# ════════════════════════════════════════
# 7月13日
# ════════════════════════════════════════
H('第四天：7月13日 — 代码质量修复与规范化', level=1)

tag('5.1 目录结构规范')
P('对项目目录进行规范化整理。SQL/ → sql/，document/上交/ → document/submission/。清理过时的日志副本。添加 README.md 项目说明文件。')

tag('5.2 代码质量清零')
P('修复 Pylint 全部警告（未使用的 import、不规范变量命名、过长函数等）。统一算术运算符空格规范。统一代码格式。更新 requirements.txt，补充遗漏的 python-dotenv、sqlalchemy、pydantic 依赖。')

tag('5.3 数据库配置迁移')
P('数据库连接配置从硬编码迁移至 .env 文件管理，支持环境变量覆盖默认值。')

doc.add_page_break()

# ════════════════════════════════════════
# 7月14日
# ════════════════════════════════════════
H('第五天：7月14日 — 交互式图表与功能增强', level=1)

tag('6.1 Pydantic 输入校验系统')
P('引入 Pydantic 模型进行全表单校验。创建 StudentCreate、TeacherCreate、ClassCreate、CourseCreate、GradeRecord 等校验模型，通过 validate_or_error 统一调用。学号校验 8-12 位纯数字，工号校验 T+数字格式。校验失败通过 st.toast 显示中文错误。全部 text_input 配置 max_chars 与后端对齐。')

tag('6.2 Plotly 交互式图表')
P('引入 Plotly Express，在 7 个页面增加交互式图表。数据概览：3 饼图+2 柱状图。班级学生名单：学籍分/GPA 分布饼图。班级成绩统计：成绩分布柱状图。教师课程学生：成绩饼图+排行柱状图（并排）。我的成绩：各科柱状图+60 分及格线。教师列表：排课数和选课数排行。')

tag('6.3 专业管理模块')
P('专业列表以 CSV 文件存储。前端提供增删操作，删除时检查班级引用。初始 26 个专业，后扩展至 160+ 覆盖工学、理学、医学、文学、法学、经济学、管理学各学科门类。班级管理联动专业下拉选择。')

tag('6.4 班级管理升级')
P('年级和专业改为 selectbox 下拉选择。系统自动查询该年级+专业已有班级序号，自动生成班级名（{年级}{专业}{序号}班）。修改模式中班级信息只读显示。删除时检查是否有在读学生。')

tag('6.5 排课管理优化')
P('排课上限改用 text_input + max_chars=5，解决 JS 数字精度问题。时间选择从 date_input+两个 selectbox 升级为 st.datetime_input，砍掉 108 行冗余代码。')

doc.add_page_break()

# ════════════════════════════════════════
# 7月15日
# ════════════════════════════════════════
H('第六天：7月15日 — 大规模数据支持', level=1)

tag('7.1 200 万数据生成器')
P('创建 test/generate_large_data.py 一站式生成器。从基础数据（1000 学生/25 教师/54 排课）扩增至 20,000 学生、300 教师、329 班级、1,004 排课、2,002,688 条选课。采用导入前删触发器 + LOAD DATA INFILE + 导入后批量重算 GPA 策略，整体约 30 秒。')

tag('7.2 LOAD DATA INFILE 导入优化')
P('采用 LOAD DATA LOCAL INFILE 替代逐条 INSERT，速度提升约 20 倍。关键策略：导入前 Python 删除 5 个触发器，导入后 UPDATE 批量重算全部 GPA。CSV 中空成绩用 \\N（MySQL NULL 标准写法）。排课容量设为 99999 防止触发器拦截。')

tag('7.3 性能优化')
P('选课管理改为按学期+学号查询，避免 200 万条全量加载。退选改为输入选课 ID。生成器修复：姓名库扩展至 40 万组合、used_pairs 去重、高斯分布截断、CROSS JOIN 从 3 次减为 2 次。')

tag('7.4 防御性修复')
P('班级删除检查学生数。student_full_list 过滤已删班级。teacher_course_teachers 过滤离职教师。grade_roster_data 返回原生 NULL。饼图过滤 0% 扇区。')

doc.add_page_break()

# ════════════════════════════════════════
# 7月16日
# ════════════════════════════════════════
H('第七天：7月16日 — 文档收尾与答辩准备', level=1)

tag('8.1 答辩 PPT 制作')
P('使用 python-pptx 制作 11 页答辩 PPT。深蓝主题配色、卡片式布局。含项目概述、系统架构、数据库设计、功能模块、特色功能、数据规模、AI 辅助、总结等完整章节。')

tag('8.2 课程设计说明书重构')
P('使用 python-docx 重构说明书，更新全部数据规模和新增功能描述。提供说明书修改清单和精准文本替换脚本。')

tag('8.3 代码附录生成')
P('整理全部 23 个源代码文件为代码附录.docx，等宽字体加灰色底纹排版。')

tag('8.4 每日工作总结')
P('编写本工作日志，按天组织全部开发过程的完整记录。')

tag('8.5 源码打包')
P('使用 zipfile 打包源码为 4.2 MB 压缩包，57 个文件，排除非源码目录。')

# ══ 保存 ══
doc.save(OUT)
sz = os.path.getsize(OUT) // 1024
print(f'OK: {sz} KB -> {OUT}')
