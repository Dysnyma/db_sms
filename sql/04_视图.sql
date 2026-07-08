-- ============================================================
-- 文件：04_视图.sql
-- 说明：创建业务视图，封装复杂查询，实现外模式
-- 视图清单：
--   1. v_student_message —— 学生基本信息（隐藏学籍分/绩点分）
--   2. v_course_plan     —— 选课安排列表（含课程名+教师名）
--   3. v_enrollment      —— 选课详情（含学生+课程+教师+成绩）
-- 设计原则：
--   1. 视图过滤 is_deleted = 0，应用层无需重复过滤
--   2. 视图封装多表 JOIN，简化应用层查询
-- ============================================================

USE db_sms;

-- ------------------------------------------------------------
-- 4.1 学生基本信息视图 (v_student_message)
-- 说明：向学生和教务提供基本信息，不暴露学籍分/绩点分
-- ------------------------------------------------------------
DROP VIEW IF EXISTS v_student_message;
CREATE VIEW v_student_message AS
SELECT
    s.id                AS student_id,
    s.name              AS student_name,
    s.no                AS student_no,
    s.class_id,
    c.name              AS class_name,
    c.grade,
    c.major,
    s.status
FROM student s
INNER JOIN class c ON s.class_id = c.id
WHERE s.is_deleted = 0;


-- ------------------------------------------------------------
-- 4.2 选课安排列表视图 (v_course_plan)
-- 说明：学生选课时看到的排课列表，直接输出课程名+教师名+选课状态
-- ------------------------------------------------------------
DROP VIEW IF EXISTS v_course_plan;
CREATE VIEW v_course_plan AS
SELECT

    co.id                       AS plan_id,
    co.course_id,
    c.name                      AS course_name,
    c.credit,
    co.teacher_id,
    t.name                      AS teacher_name,
    co.semester,
    co.max_students,
    co.current_students,
    co.max_students - co.current_students AS remaining_seats,
    co.enroll_start_time,
    co.enroll_end_time,
    co.grade_deadline,
    CASE
        WHEN NOW() < co.enroll_start_time THEN '未开始'
        WHEN NOW() BETWEEN co.enroll_start_time AND co.enroll_end_time THEN '选课中'
        WHEN NOW() > co.grade_deadline THEN '已结束'
        ELSE '已截止'
    END                         AS enroll_status,
    co.status
FROM course_offering co
INNER JOIN course c  ON co.course_id = c.id
INNER JOIN teacher t ON co.teacher_id = t.id
WHERE co.is_deleted = 0;


-- ------------------------------------------------------------
-- 4.3 选课详情视图 (v_enrollment)
-- 说明：学生名+课程名+教师名+成绩，四表联查封装为单视图
-- ------------------------------------------------------------
DROP VIEW IF EXISTS v_enrollment;
CREATE VIEW v_enrollment AS
SELECT
    e.id                        AS enroll_id,
    e.offering_id,
    e.student_id,
    s.name                      AS student_name,
    s.no                        AS student_no,
    c.id                        AS course_id,
    c.name                      AS course_name,
    c.credit,
    t.id                        AS teacher_id,
    t.name                      AS teacher_name,
    co.semester,
    e.score,
    e.create_time               AS enroll_time
FROM enrollment e
INNER JOIN student s          ON e.student_id  = s.id
INNER JOIN course_offering co ON e.offering_id = co.id
INNER JOIN course c           ON co.course_id  = c.id
INNER JOIN teacher t          ON co.teacher_id = t.id
WHERE e.is_deleted = 0;


SELECT '视图创建完成' AS message;
