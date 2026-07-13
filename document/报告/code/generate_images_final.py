# -*- coding: utf-8 -*-
"""报告配图 — 300 DPI 高清版"""
import sys,io; sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8')
import matplotlib as mpl; mpl.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
import numpy as np, os

OUT = r'E:\02_Courses\db_lab\document\报告\images'
os.makedirs(OUT, exist_ok=True)

plt.rcParams.update({'font.sans-serif':['Microsoft YaHei','Noto Sans SC','SimHei'],
    'axes.unicode_minus':False,'figure.dpi':300,'savefig.dpi':300})
T,B,S,XS = 20,14,11,9

def save(fig,name):
    fig.savefig(os.path.join(OUT,name),dpi=300,bbox_inches='tight',facecolor='white',edgecolor='none')
    plt.close(fig); print(f'  [OK] {name}')

def add_p(ax,x,y,w,h,**kw):
    """创建 fancy box 并添加到 axes"""
    p = FancyBboxPatch((x,y),w,h,boxstyle='round,pad=0.12',**kw)
    ax.add_patch(p)
    return p

# ============ 图1: 架构图 ============
def arch():
    fig,ax=plt.subplots(figsize=(14,8))
    ax.set_xlim(0,14);ax.set_ylim(0,8.5);ax.axis('off');ax.set_facecolor('#F8F9FA')
    L=[(0.3,6.8,13.4,1.3,'表示层  Presentation Layer','#1565C0',
        'Streamlit Web (st.navigation 多页导航)    |    CLI 命令行界面\n学生端：选课·退选·成绩查询    教师端：成绩录入·批量导入\n教务端：数据概览·CRUD管理·统计报表·备份恢复'),
       (0.3,5.0,13.4,1.3,'业务逻辑层  Business Logic','#2E7D32',
        'app.py  ·  admin.py  ·  student.py  ·  teacher.py\n选课管理 · 退选管理 · 成绩录入 · 统计查询 · 权限控制 · 数据校验'),
       (0.3,3.2,13.4,1.3,'数据访问层  Data Access','#E65100',
        'PyMySQL 数据库驱动 | 存储过程调用 | 游标管理 | 事务控制'),
       (0.3,1.4,13.4,1.3,'数据存储层  Data Storage','#C62828',
        'MySQL 8.0  —  db_sms\n8张表 · 3视图 · 5触发器 · 9存储过程 · 2函数    |    InnoDB · utf8mb4')]
    for x,y,w,h,title,c,desc in L:
        add_p(ax,x,y,w,h,facecolor=c,edgecolor=c,linewidth=0,alpha=0.12)
        add_p(ax,x,y,w,h,facecolor='none',edgecolor=c,linewidth=2)
        ax.text(x+0.3,y+h-0.25,title,fontsize=B,fontweight='bold',color=c,va='top')
        ax.text(x+0.3,y+0.2,desc,fontsize=S,color='#444',va='bottom',linespacing=1.5)
    for i in range(3):
        y1=L[i][1]; y2=L[i+1][1]+L[i+1][3]
        ax.annotate('',xy=(7,y2),xytext=(7,y1),arrowprops=dict(arrowstyle='<->',color='#999',lw=2.5))
    ax.set_title('图1-1  系统四层架构图',fontsize=T,fontweight='bold',pad=18)
    save(fig,'system_architecture.png')

# ============ 图2: DFD ============
def dfd():
    fig,ax=plt.subplots(figsize=(16,9))
    ax.set_xlim(0,16);ax.set_ylim(0,9);ax.axis('off');ax.set_facecolor('#F8F9FA')
    for x,y,lbl,c in [(1.2,7.5,'学生','#1565C0'),(1.2,1.5,'教师','#2E7D32'),(8.5,8.5,'教务管理员','#E65100')]:
        add_p(ax,x-1.2,y-0.45,2.4,0.9,facecolor=c,edgecolor=c,linewidth=0,alpha=0.15)
        add_p(ax,x-1.2,y-0.45,2.4,0.9,facecolor='none',edgecolor=c,linewidth=2)
        ax.text(x,y,lbl,ha='center',va='center',fontsize=B,fontweight='bold',color=c)
    for x,y,lbl in [(5,7.5,'选课管理'),(5,4.5,'成绩管理'),(5,1.5,'信息查询'),(11.5,4.5,'数据维护')]:
        ax.add_patch(plt.Circle((x,y),0.85,facecolor='#FCE4EC',edgecolor='#C62828',linewidth=2))
        ax.text(x,y,lbl,ha='center',va='center',fontsize=B,fontweight='bold',color='#C62828')
    for x,y,lbl in [(12,7.8,'学生/班级/课程表'),(12,1.2,'教师/排课/选课表')]:
        add_p(ax,x-1.4,y-0.55,2.8,1.1,facecolor='#F5F5F5',edgecolor='#666',linewidth=1.5)
        ax.text(x,y,lbl,ha='center',va='center',fontsize=S,color='#444')
    for sx,sy,dx,dy,lbl in [(2.4,7.5,4.15,7.5,'选课请求'),(4.15,7.0,2.4,7.0,'选课结果'),
        (2.4,1.5,4.15,1.5,'录入成绩'),(4.15,1.0,2.4,1.0,'录入结果'),
        (5.85,7.5,10.6,7.8,'读写'),(5.85,1.5,10.6,1.2,'读写'),(5.85,4.5,10.6,4.5,'读写')]:
        ax.annotate('',xy=(dx,dy),xytext=(sx,sy),arrowprops=dict(arrowstyle='->',color='#666',lw=1.8))
        if lbl:
            mx,my=(sx+dx)/2,(sy+dy)/2;ax.text(mx,my+0.15,lbl,fontsize=XS,ha='center',color='#555',bbox=dict(boxstyle='round,pad=0.05',fc='white',alpha=0.85))
    ax.set_title('图2-1  系统数据流图（DFD）',fontsize=T,fontweight='bold',pad=18)
    save(fig,'data_flow_diagram.png')

# ============ 图3: 功能模块 ============
def modules():
    fig,ax=plt.subplots(figsize=(16,8))
    ax.set_xlim(0,16);ax.set_ylim(0,8);ax.axis('off');ax.set_facecolor('#F8F9FA')
    ax.text(8,7.6,'学生成绩管理系统',ha='center',va='center',fontsize=T,fontweight='bold',color='white',
        bbox=dict(boxstyle='round,pad=0.4',facecolor='#1565C0',edgecolor='#0D47A1'))
    for x,y,title,c,items in [(3.2,4.5,'学生端','#1976D2',['浏览可选课程','选课 / 退选','查看我的成绩','查询学期均分']),
        (8,4.5,'教师端','#388E3C',['录入学生成绩','批量 CSV 导入','查看课程学生']),
        (12.8,4.5,'教务端','#F57C00',['数据概览仪表板','班级/课程/教师/学生 CRUD','排课 / 选课管理','成绩统计与报表','数据备份与恢复'])]:
        w,h=3.8,3.8
        add_p(ax,x-w/2,y-h/2,w,h,facecolor=c,edgecolor=c,linewidth=0,alpha=0.88)
        ax.text(x,y+h/2-0.4,title,ha='center',fontsize=B,fontweight='bold',color='white')
        for i,item in enumerate(items): ax.text(x,y+h/2-1.0-i*0.56,f'• {item}',ha='center',fontsize=S,color='white')
        ax.plot([8,x],[7.3,y+h/2],'-',color='#999',lw=1.5)
    ax.set_title('图2-2  系统功能模块图',fontsize=T,fontweight='bold',pad=15)
    save(fig,'function_modules.png')

# ============ 图4: ER图 ============
def er():
    fig,ax=plt.subplots(figsize=(18,12))
    ax.set_xlim(0,18);ax.set_ylim(0,12);ax.axis('off');ax.set_facecolor('#F8F9FA')
    E={'class':(2,8.5,'班级\nclass','#E3F2FD'),'student':(2,4.0,'学生\nstudent','#E8F5E9'),
       'course':(9,8.5,'课程\ncourse','#FFF3E0'),'teacher':(9,4.0,'教师\nteacher','#F3E5F5'),
       'offering':(5.5,6.2,'选课安排\ncourse_offering','#FFEBEE'),'enrollment':(5.5,1.5,'选课\nenrollment','#E0F7FA'),
       'tc':(14,6.2,'讲授\nteacher_course','#F5F5F5'),'gpr':(14,9.5,'绩点对照\ngrade_point_rule','#ECEFF1')}
    P={}
    for nm,(x,y,lb,c) in E.items():
        P[nm]=(x,y); w,h=3.0,2.0
        add_p(ax,x-w/2,y-h/2,w,h,facecolor=c,edgecolor='#333',linewidth=2)
        ax.text(x,y,lb,ha='center',va='center',fontsize=B,fontweight='bold',color='#222')
    for s,d,lb,cs,cd in [('class','student','属于','1','N'),('course','offering','开设','1','N'),
        ('teacher','offering','授课','1','N'),('offering','enrollment','包含','1','N'),
        ('student','enrollment','选修','1','N'),('teacher','tc','拥有','1','N'),('course','tc','被授','1','N')]:
        sx,sy=P[s];dx,dy=P[d];mx,my=(sx+dx)/2,(sy+dy)/2
        ax.annotate('',xy=(dx,dy-0.15),xytext=(sx,sy+0.15),arrowprops=dict(arrowstyle='->',color='#666',lw=2,connectionstyle='arc3,rad=0'))
        ax.text(mx+0.1,my+0.2,lb,fontsize=S,color='#555',ha='center',bbox=dict(boxstyle='round,pad=0.08',fc='white',ec='none',alpha=0.85))
        ax.text(sx+(dx-sx)*0.3,sy+(dy-sy)*0.3-0.3,cs,fontsize=S,color='#C62828',fontweight='bold')
        ax.text(sx+(dx-sx)*0.7,sy+(dy-sy)*0.7+0.1,cd,fontsize=S,color='#C62828',fontweight='bold')
    ax.set_title('图3-1  全局 E-R 图',fontsize=T,fontweight='bold',pad=18)
    save(fig,'er_diagram.png')

# ============ 图5: 表关系 ============
def tables():
    fig,ax=plt.subplots(figsize=(20,12))
    ax.set_xlim(0,20);ax.set_ylim(0,12);ax.axis('off');ax.set_facecolor('#F8F9FA')
    for x,y,lns,c in [
        (0.2,8.0,['class','班级表','PK  id','   name','   grade','   major','   status'],'#BBDEFB'),
        (0.2,3.5,['student','学生表','PK  id','FK  class_id','   no (学号)','   name','   weighted_score','   gpa'],'#C8E6C9'),
        (7,8.0,['course','课程表','PK  id','   name','   credit','   status'],'#FFE0B2'),
        (13.5,8.5,['grade_point_rule','绩点对照表','PK  id','   min_score','   max_score','   point'],'#ECEFF1'),
        (7,3.5,['teacher','教师表','PK  id','   no (工号)','   name','   title','   phone'],'#E1BEE7'),
        (5,0.2,['enrollment','选课表','PK  id','FK  offering_id','FK  student_id','   score (成绩)'],'#B2EBF2'),
        (10.5,0.2,['course_offering','选课安排表','PK  id','FK  course_id','FK  teacher_id','   semester','   max_students','   current_students'],'#FFCDD2'),
        (16.5,3.5,['teacher_course','讲授表','PK  id','FK  teacher_id','FK  course_id'],'#F5F5F5')]:
        w,h=3.6,len(lns)*0.38+0.2
        add_p(ax,x,y-h,w,h,facecolor=c,edgecolor='#333',linewidth=1.5,alpha=0.9)
        for li,ln in enumerate(lns):
            cl='#C62828' if ln.startswith('PK') else ('#2E7D32' if ln.startswith('FK') else '#333')
            fw='bold' if li==0 else 'normal'
            ax.text(x+0.15,y-0.3-li*0.38,ln,fontsize=S-1 if li==0 else XS,color=cl,fontweight=fw,va='top',fontfamily='monospace')
    for sx,sy,dx,dy,lbl in [
        (1.8,7.5,1.8,5.0,'class→student  1:N'),(8.5,7.5,6.5,1.5,'course→offering  1:N'),
        (8.5,4.5,10.5,1.5,'teacher→offering  1:N'),(5.8,1.0,1.8,4.0,'student→enrollment  1:N'),
        (10.8,1.0,6.5,4.0,'offering→enrollment  1:N'),(8.8,4.5,16.5,4.5,'teacher→tc  1:N'),
        (9.0,7.5,16.5,5.0,'course→tc  1:N')]:
        ax.annotate(lbl,xy=(dx,dy),xytext=(sx,sy),arrowprops=dict(arrowstyle='->',color='#777',lw=1.2),
            fontsize=XS-1,color='#555',ha='center',bbox=dict(boxstyle='round,pad=0.05',fc='#FFF9C4',alpha=0.8))
    ax.set_title('图4-1  数据库关系图',fontsize=T,fontweight='bold',pad=18)
    save(fig,'table_relationships.png')

# ============ 图6: EXPLAIN ============
def explain():
    fig,ax=plt.subplots(figsize=(14,4));ax.axis('off')
    cols=['id','select_type','table','type','key','key_len','ref','rows','filtered','Extra']
    data=[['1','SIMPLE','enrollment','ref','idx_enr_student','4','db_sms.e.offering_id','13','100.00','Using where'],
        ['1','SIMPLE','student','eq_ref','PRIMARY','4','db_sms.e.student_id','1','100.00',''],
        ['1','SIMPLE','course_offering','eq_ref','PRIMARY','4','db_sms.e.offering_id','1','100.00','Using where']]
    tbl=ax.table(cellText=data,colLabels=cols,cellLoc='center',loc='center',colWidths=[0.04,0.08,0.09,0.06,0.10,0.06,0.14,0.05,0.06,0.10])
    tbl.auto_set_font_size(False);tbl.set_fontsize(9);tbl.scale(1.15,2.0)
    for i in range(len(cols)):tbl[0,i].set_facecolor('#1565C0');tbl[0,i].set_text_props(color='white',fontweight='bold',fontsize=9)
    ax.set_title('图5-1  EXPLAIN 执行计划分析',fontsize=T,fontweight='bold',pad=18)
    save(fig,'explain_plan.png')

# ============ 图7: UI模拟 ============
def ui_login():
    fig,ax=plt.subplots(figsize=(12,6))
    ax.set_xlim(0,12);ax.set_ylim(0,6);ax.axis('off');ax.set_facecolor('#E8ECF1')
    r=add_p(ax,2,4.3,8,1.0,facecolor='#1565C0',edgecolor='#0D47A1')
    ax.text(6,4.8,'学生成绩管理系统',ha='center',fontsize=20,fontweight='bold',color='white')
    add_p(ax,3.5,2.0,5,2.0,facecolor='white',edgecolor='#CCC',linewidth=1.5)
    ax.text(6,3.7,'请输入学号 / 工号（教务输入 admin）',ha='center',fontsize=10,color='#888')
    add_p(ax,4.2,3.1,3.6,0.45,facecolor='#F0F2F5',edgecolor='#BBB')
    add_p(ax,5,2.2,2,0.5,facecolor='#1565C0',edgecolor='#0D47A1')
    ax.text(6,2.45,'登  录',ha='center',fontsize=13,color='white',fontweight='bold')
    ax.set_title('图7-1  系统登录页面',fontsize=T,fontweight='bold',pad=15)
    save(fig,'ui_login.png')

def ui_admin():
    fig,ax=plt.subplots(figsize=(14,7))
    ax.set_xlim(0,14);ax.set_ylim(0,7);ax.axis('off');ax.set_facecolor('#E8ECF1')
    add_p(ax,0,0,2.5,7,facecolor='#1A237E',edgecolor='none')
    for l,y in [('📊 数据查看',6.3),('  数据概览',5.8),('  班级名单',5.3),('  成绩统计',4.8),('  教师信息',4.3),
        ('🔧 数据管理',3.5),('  班级/课程',3.0),('  教师/学生',2.5),('  排课/选课',2.0),
        ('💾 系统工具',1.2),('  备份/恢复',0.7)]:
        ax.text(0.3,y,l,fontsize=10,fontweight='bold' if not l.startswith('  ') else 'normal',
            color='#E0E0E0' if not l.startswith('  ') else '#90A4AE')
    ax.text(5.5,6.4,'📋 数据概览',fontsize=16,fontweight='bold')
    for i,(l,v) in enumerate([('班级总数','12'),('学生总数','120'),('教师总数','16'),
        ('课程总数','12'),('排课总数','100'),('选课记录','835')]):
        x=3.2+(i%3)*3.5;y=5.0-(i//3)*2.0
        add_p(ax,x,y-0.6,3.0,1.3,facecolor='white',edgecolor='#DDD',linewidth=1)
        ax.text(x+1.5,y+0.3,v,ha='center',fontsize=24,fontweight='bold',color='#1565C0')
        ax.text(x+1.5,y-0.2,l,ha='center',fontsize=10,color='#888')
    ax.set_title('图7-2  教务端数据概览页面',fontsize=T,fontweight='bold',pad=15)
    save(fig,'ui_admin_dashboard.png')

def ui_student():
    fig,ax=plt.subplots(figsize=(14,6))
    ax.set_xlim(0,14);ax.set_ylim(0,6);ax.axis('off');ax.set_facecolor('#E8ECF1')
    ax.text(7,5.5,'📚 可选课程',fontsize=16,fontweight='bold',ha='center')
    h=['排课ID','课程名','学分','教师','学期','剩余名额']
    d=[['12','高等数学','5.0','张教授','2025-2026-1','15/30'],
       ['25','数据结构','4.0','李教授','2025-2026-1',' 8/25'],
       ['38','数据库原理','3.5','王教授','2025-2026-1','20/35']]
    tbl=ax.table(cellText=[h]+d,cellLoc='center',loc='upper center',colWidths=[0.08,0.16,0.06,0.12,0.14,0.10])
    tbl.auto_set_font_size(False);tbl.set_fontsize(10);tbl.scale(1.3,1.8)
    for i in range(len(h)):tbl[0,i].set_facecolor('#1565C0');tbl[0,i].set_text_props(color='white',fontweight='bold',fontsize=10)
    ax.text(7,1.0,'选择要选的排课  [▼  #12 高等数学 - 张教授 (5.0学分)]    [确认选课]',ha='center',fontsize=10,color='#555',
        bbox=dict(boxstyle='round',fc='white',ec='#DDD'))
    ax.set_title('图7-3  学生选课页面',fontsize=T,fontweight='bold',pad=15)
    save(fig,'ui_student_enroll.png')

# ============ 图8: 测试流程 ============
def test_flow():
    fig,ax=plt.subplots(figsize=(14,8))
    ax.set_xlim(0,14);ax.set_ylim(0,8);ax.axis('off');ax.set_facecolor('#F8F9FA')
    for x,y,l,c in [(7,7.3,'测试开始','#1565C0'),(7,6.0,'数据库连接测试','#42A5F5'),
        (3.5,4.5,'学生端测试','#2E7D32'),(10.5,4.5,'教师端测试','#E65100'),
        (1.5,3.0,'选课流程','#C62828'),(5.5,3.0,'退选流程','#C62828'),
        (8.5,3.0,'成绩录入','#C62828'),(12.5,3.0,'批量导入','#C62828'),
        (3.5,1.5,'异常场景\n(满额/重复/超期)','#7B1FA2'),(10.5,1.5,'边界值\n(0分/100分/超限)','#7B1FA2'),
        (7,0.3,'测试通过 ✓','#1565C0')]:
        w=2.4 if '\n' not in l else 2.8;h=0.6 if '\n' not in l else 0.9
        add_p(ax,x-w/2,y-h/2,w,h,facecolor=c,edgecolor='#333',linewidth=1.5)
        ax.text(x,y,l,ha='center',va='center',fontsize=S if '\n' not in l else S-1,fontweight='bold',color='white')
    for sx,sy,dx,dy in [(7,7.0,7,6.3),(7,5.7,3.5,4.8),(7,5.7,10.5,4.8),
        (3.5,4.2,1.5,3.3),(3.5,4.2,5.5,3.3),(10.5,4.2,8.5,3.3),(10.5,4.2,12.5,3.3),
        (1.5,2.7,3.5,2.0),(5.5,2.7,3.5,2.0),(8.5,2.7,10.5,2.0),(12.5,2.7,10.5,2.0),
        (3.5,1.2,7,0.6),(10.5,1.2,7,0.6)]:
        ax.annotate('',xy=(dx,dy),xytext=(sx,sy),arrowprops=dict(arrowstyle='->',color='#888',lw=1.8))
    ax.set_title('图8-1  系统测试流程图',fontsize=T,fontweight='bold',pad=15)
    save(fig,'test_flow.png')

if __name__=='__main__':
    print('生成 300 DPI 高清配图...')
    arch();dfd();modules();er();tables();explain()
    ui_login();ui_admin();ui_student();test_flow()
    print(f'完成！10张图 → {OUT}')
