-- ============================================================
-- 文件：03_中间表.sql
-- 说明：创建关系表 —— 选课、讲授、绩点对照
-- ============================================================

USE db_sms;

-- ------------------------------------------------------------
-- 3.1 选课表 (enrollment)
-- 学生与选课安排之间的 M:N 关系
-- ------------------------------------------------------------
DROP TABLE IF EXISTS enrollment;
CREATE TABLE enrollment (
    id              INT             NOT NULL AUTO_INCREMENT  COMMENT '选课记录ID',
    offering_id     INT             NOT NULL                 COMMENT '选课安排ID',
    student_id      INT             NOT NULL                 COMMENT '学生ID',
    score           DECIMAL(5,2)    DEFAULT NULL             COMMENT '成绩，NULL=未录入',
    create_time     DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '选课时间',
    update_time     DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    is_deleted      TINYINT(1)      NOT NULL DEFAULT 0       COMMENT '逻辑删除：0=选课中，1=已退选',
    PRIMARY KEY (id),
    UNIQUE INDEX uk_enrollment (offering_id, student_id),
    INDEX idx_enr_offering (offering_id),
    INDEX idx_enr_student (student_id),
    CONSTRAINT fk_enr_offering FOREIGN KEY (offering_id) REFERENCES course_offering(id),
    CONSTRAINT fk_enr_student FOREIGN KEY (student_id) REFERENCES student(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='选课表';


-- ------------------------------------------------------------
-- 3.2 讲授表 (teacher_course)
-- 教师与课程之间的 M:N 关系（教师有资格讲哪些课）
-- ------------------------------------------------------------
DROP TABLE IF EXISTS teacher_course;
CREATE TABLE teacher_course (
    id          INT             NOT NULL AUTO_INCREMENT  COMMENT '关系ID',
    teacher_id  INT             NOT NULL                 COMMENT '教师ID',
    course_id   INT             NOT NULL                 COMMENT '课程ID',
    create_time DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    update_time DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    is_deleted  TINYINT(1)      NOT NULL DEFAULT 0       COMMENT '逻辑删除',
    PRIMARY KEY (id),
    UNIQUE INDEX uk_teacher_course (teacher_id, course_id),
    INDEX idx_tc_teacher (teacher_id),
    INDEX idx_tc_course (course_id),
    CONSTRAINT fk_tc_teacher FOREIGN KEY (teacher_id) REFERENCES teacher(id),
    CONSTRAINT fk_tc_course FOREIGN KEY (course_id) REFERENCES course(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='讲授表';


-- ------------------------------------------------------------
-- 3.3 绩点对照表 (grade_point_rule)
-- 成绩区间 → 绩点转换规则
-- ------------------------------------------------------------
DROP TABLE IF EXISTS grade_point_rule;
CREATE TABLE grade_point_rule (
    id          INT             NOT NULL AUTO_INCREMENT  COMMENT '规则ID',
    min_score   DECIMAL(5,2)    NOT NULL                 COMMENT '成绩下限',
    max_score   DECIMAL(5,2)    NOT NULL                 COMMENT '成绩上限',
    point       DECIMAL(3,1)    NOT NULL                 COMMENT '对应绩点',
    PRIMARY KEY (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='绩点对照表';

-- 插入绩点规则（题目要求）
INSERT INTO grade_point_rule (min_score, max_score, point) VALUES
(0,    59.99, 0),
(60,   69.99, 1),
(70,   79.99, 2),
(80,   89.99, 3),
(90,  100.00, 4);


SELECT '中间表创建完成' AS message;
