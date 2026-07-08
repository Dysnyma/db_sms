-- ============================================================
-- 文件：02_基础数据表.sql
-- 说明：创建基础实体表 —— 学生、班级、课程、教师、选课安排
-- 设计原则：
--   1. 全部逻辑删除 (is_deleted)
--   2. status 管业务状态，is_deleted 管数据状态
--   3. 表名全小写 + 下划线
--   4. 字符集 utf8mb4，排序规则 utf8mb4_unicode_ci
-- ============================================================

USE db_sms;

-- ------------------------------------------------------------
-- 2.1 班级表 (class)
-- ------------------------------------------------------------
DROP TABLE IF EXISTS class;
CREATE TABLE class (
    id          INT             NOT NULL AUTO_INCREMENT  COMMENT '班级ID',
    name        VARCHAR(50)     NOT NULL                 COMMENT '班级名',
    grade       VARCHAR(10)     NOT NULL                 COMMENT '年级',
    major       VARCHAR(100)    NOT NULL                 COMMENT '专业',
    status      TINYINT(1)      NOT NULL DEFAULT 1       COMMENT '状态：1=在读，0=毕业',
    create_time DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    update_time DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    is_deleted  TINYINT(1)      NOT NULL DEFAULT 0       COMMENT '逻辑删除',
    PRIMARY KEY (id),
    INDEX idx_class_name (name),
    INDEX idx_class_grade (grade),
    INDEX idx_class_major (major)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='班级表';


-- ------------------------------------------------------------
-- 2.2 学生表 (student)
-- ------------------------------------------------------------
DROP TABLE IF EXISTS student;
CREATE TABLE student (
    id              INT             NOT NULL AUTO_INCREMENT  COMMENT '学生ID',
    name            VARCHAR(50)     NOT NULL                 COMMENT '姓名',
    no              VARCHAR(20)     NOT NULL                 COMMENT '学号',
    class_id        INT             NOT NULL                 COMMENT '班级ID',
    weighted_score  DECIMAL(5,2)    NOT NULL DEFAULT 0.00    COMMENT '学籍分',
    gpa             DECIMAL(5,2)    NOT NULL DEFAULT 0.00    COMMENT '绩点分',
    status          TINYINT(1)      NOT NULL DEFAULT 1       COMMENT '状态：1=在读，0=离校',
    create_time     DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    update_time     DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    is_deleted      TINYINT(1)      NOT NULL DEFAULT 0       COMMENT '逻辑删除',
    PRIMARY KEY (id),
    UNIQUE INDEX uk_student_no (no),
    INDEX idx_student_name (name),
    INDEX idx_student_class (class_id),
    CONSTRAINT fk_student_class FOREIGN KEY (class_id) REFERENCES class(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='学生表';


-- ------------------------------------------------------------
-- 2.3 课程表 (course)
-- ------------------------------------------------------------
DROP TABLE IF EXISTS course;
CREATE TABLE course (
    id          INT             NOT NULL AUTO_INCREMENT  COMMENT '课程ID',
    name        VARCHAR(100)    NOT NULL                 COMMENT '课程名',
    credit      DECIMAL(3,1)    NOT NULL                 COMMENT '学分',
    status      TINYINT(1)      NOT NULL DEFAULT 1       COMMENT '状态：1=开课，0=停开',
    create_time DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    update_time DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    is_deleted  TINYINT(1)      NOT NULL DEFAULT 0       COMMENT '逻辑删除',
    PRIMARY KEY (id),
    UNIQUE INDEX uk_course_name (name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='课程表';


-- ------------------------------------------------------------
-- 2.4 教师表 (teacher)
-- ------------------------------------------------------------
DROP TABLE IF EXISTS teacher;
CREATE TABLE teacher (
    id          INT             NOT NULL AUTO_INCREMENT  COMMENT '教师ID',
    name        VARCHAR(50)     NOT NULL                 COMMENT '姓名',
    no          VARCHAR(20)     NOT NULL                 COMMENT '工号',
    title       VARCHAR(50)     DEFAULT NULL             COMMENT '职称',
    phone       VARCHAR(20)     DEFAULT NULL             COMMENT '联系电话',
    status      TINYINT(1)      NOT NULL DEFAULT 1       COMMENT '状态：1=在职，0=离职',
    create_time DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    update_time DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    is_deleted  TINYINT(1)      NOT NULL DEFAULT 0       COMMENT '逻辑删除',
    PRIMARY KEY (id),
    UNIQUE INDEX uk_teacher_no (no),
    INDEX idx_teacher_name (name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='教师表';


-- ------------------------------------------------------------
-- 2.5 选课安排表 (course_offering)
-- 每次排课产生一条记录，指定哪门课由哪个老师讲、多少人能选
-- ------------------------------------------------------------
DROP TABLE IF EXISTS course_offering;
CREATE TABLE course_offering (
    id                  INT             NOT NULL AUTO_INCREMENT  COMMENT '排课ID',
    course_id           INT             NOT NULL                 COMMENT '课程ID',
    teacher_id          INT             NOT NULL                 COMMENT '授课教师ID',
    semester            VARCHAR(20)     NOT NULL                 COMMENT '学期',
    max_students        INT             NOT NULL                 COMMENT '最高选课人数',
    current_students    INT             NOT NULL DEFAULT 0       COMMENT '当前选课人数（触发器维护）',
    enroll_start_time   DATETIME        NOT NULL                 COMMENT '选课开始时间',
    enroll_end_time     DATETIME        NOT NULL                 COMMENT '选课截止时间',
    grade_deadline      DATETIME        NOT NULL                 COMMENT '成绩录入截止时间',
    status              TINYINT(1)      NOT NULL DEFAULT 1       COMMENT '状态：1=有效，0=取消',
    create_time         DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    update_time         DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    is_deleted          TINYINT(1)      NOT NULL DEFAULT 0       COMMENT '逻辑删除',
    PRIMARY KEY (id),
    INDEX idx_co_course (course_id),
    INDEX idx_co_teacher (teacher_id),
    INDEX idx_co_semester (semester),
    INDEX idx_co_enroll_time (enroll_start_time, enroll_end_time),
    CONSTRAINT fk_co_course FOREIGN KEY (course_id) REFERENCES course(id),
    CONSTRAINT fk_co_teacher FOREIGN KEY (teacher_id) REFERENCES teacher(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='选课安排表';


SELECT '基础数据表创建完成' AS message;
