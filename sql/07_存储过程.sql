-- ============================================================
-- 文件：07_存储过程.sql
-- 说明：核心业务存储过程
-- 清单：
--   1. sp_show_courses —— 查询可选课程
--   2. sp_enroll       —— 选课
--   3. sp_unenroll     —— 退选
--   4. sp_grade_input   —— 录入成绩
--   5. sp_student_roster       —— 按班级输出学生名单（含学籍分）
--   6. sp_class_grade_report    —— 按班级+课程统计成绩
--   7. sp_student_semester_avg  —— 某学生某学期平均成绩
--   8. sp_teacher_info           —— 单个教师信息及授课统计
--   9. sp_teacher_list           —— 全部教师列表及授课统计
-- ============================================================

USE db_sms;

-- ------------------------------------------------------------
-- 7.1 查询可选课程
-- 说明：学生输入学号，返回正在选课中、有名额、自己没选过的课程
-- ------------------------------------------------------------
DROP PROCEDURE IF EXISTS sp_show_courses;
DELIMITER ;;

CREATE PROCEDURE sp_show_courses(
    p_student_no VARCHAR(20)
)
BEGIN
    SELECT
        plan_id,
        course_name,
        credit,
        teacher_name,
        semester,
        remaining_seats,
        enroll_start_time,
        enroll_end_time
    FROM v_course_plan
    WHERE enroll_status = '选课中'
      AND remaining_seats > 0
      AND plan_id NOT IN (
          SELECT offering_id FROM enrollment
          WHERE student_id = fn_get_student_id(p_student_no)
            AND is_deleted = 0
      )
    ORDER BY course_name, teacher_name;
END;;

DELIMITER ;


-- ------------------------------------------------------------
-- 7.2 选课
-- 说明：学生输入学号和排课ID，校验通过后插入选课记录
-- ------------------------------------------------------------
DROP PROCEDURE IF EXISTS sp_enroll;
DELIMITER ;;

CREATE PROCEDURE sp_enroll(
    p_student_no VARCHAR(20),
    p_plan_id    INT
)
BEGIN
    DECLARE v_student_id INT;
    DECLARE v_msg VARCHAR(200);

    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        RESIGNAL;
    END;

    START TRANSACTION;

    -- 1. 根据学号找学生ID
    SET v_student_id = fn_get_student_id(p_student_no);

    IF v_student_id IS NULL THEN
        SET v_msg = CONCAT('学生 ', p_student_no, ' 不存在');
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = v_msg;
    END IF;

    -- 2. 检查排课是否存在且在选课期内
    IF NOT EXISTS (
        SELECT 1 FROM course_offering
        WHERE id = p_plan_id
          AND is_deleted = 0
          AND NOW() BETWEEN enroll_start_time AND enroll_end_time
    ) THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = '该课程不在选课期内或不存在';
    END IF;

    -- 3. 检查是否已选过同一排课
    IF EXISTS (
        SELECT 1 FROM enrollment
        WHERE offering_id = p_plan_id
          AND student_id = v_student_id
          AND is_deleted = 0
    ) THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = '你已经选过这门课了';
    END IF;

    -- 4. 检查是否已选过同一门课的其他老师（同一课程不能选两个老师）
    IF EXISTS (
        SELECT 1 FROM enrollment e
        JOIN course_offering co ON e.offering_id = co.id
        WHERE e.student_id = v_student_id
          AND e.is_deleted = 0
          AND co.course_id = (SELECT course_id FROM course_offering WHERE id = p_plan_id)
    ) THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = '你已选过该课程的其他教师，不能重复选同一门课';
    END IF;

    -- 5. 选课（触发器自动检查名额 + 更新人数）
    INSERT INTO enrollment (offering_id, student_id)
    VALUES (p_plan_id, v_student_id);

    COMMIT;
    SELECT '选课成功' AS message;
END;;

DELIMITER ;


-- ------------------------------------------------------------
-- 7.3 退选
-- 说明：选课到期前可退选，逻辑删除选课记录，触发器自动更新人数
-- ------------------------------------------------------------
DROP PROCEDURE IF EXISTS sp_unenroll;
DELIMITER ;;

CREATE PROCEDURE sp_unenroll(
    p_student_no VARCHAR(20),
    p_plan_id    INT
)
BEGIN
    DECLARE v_student_id INT;
    DECLARE v_msg VARCHAR(200);

    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        RESIGNAL;
    END;

    START TRANSACTION;

    -- 1. 根据学号找学生ID
    SET v_student_id = fn_get_student_id(p_student_no);

    IF v_student_id IS NULL THEN
        SET v_msg = CONCAT('学生 ', p_student_no, ' 不存在');
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = v_msg;
    END IF;

    -- 2. 检查是否已选课（存在且未退选）
    IF NOT EXISTS (
        SELECT 1 FROM enrollment
        WHERE offering_id = p_plan_id
          AND student_id = v_student_id
          AND is_deleted = 0
    ) THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = '你未选这门课，无法退选';
    END IF;

    -- 3. 检查是否还在退选期内（选课截止前才能退）
    IF NOT EXISTS (
        SELECT 1 FROM course_offering co
        JOIN enrollment e ON co.id = e.offering_id
        WHERE e.offering_id = p_plan_id
          AND e.student_id = v_student_id
          AND NOW() <= co.enroll_end_time
    ) THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = '已过退选截止时间，无法退选';
    END IF;

    -- 4. 逻辑删除（触发器检测到 0→1，自动 current_students -1）
    UPDATE enrollment
    SET is_deleted = 1
    WHERE offering_id = p_plan_id
      AND student_id = v_student_id
      AND is_deleted = 0;

    COMMIT;
    SELECT '退选成功' AS message;
END;;

DELIMITER ;


-- ------------------------------------------------------------
-- 7.4 录入成绩
-- 说明：教师输入工号、排课ID、学生学号、成绩，校验后更新成绩
-- ------------------------------------------------------------
DROP PROCEDURE IF EXISTS sp_grade_input;
DELIMITER ;;

CREATE PROCEDURE sp_grade_input(
    p_teacher_no VARCHAR(20)
    ,p_plan_id INT
    ,p_student_no VARCHAR(20)
    ,p_score DECIMAL(5,2)
)
BEGIN   
    DECLARE v_msg VARCHAR(200);
    DECLARE v_teacher_id INT;
    DECLARE v_student_id INT;


    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        RESIGNAL;
    END;

    START TRANSACTION;

    -- 1. 获取老师工号对应的ID
    SET v_teacher_id = fn_get_teacher_id(p_teacher_no);
    IF v_teacher_id IS NULL THEN
        SET v_msg = CONCAT('不存在工号为 ', p_teacher_no, ' 的老师');
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = v_msg;
    END IF;

    -- 2. 检查老师是否有教这门课（并且还没过成绩录入截止时间）
    IF NOT EXISTS (
        SELECT 1 FROM course_offering
        WHERE id = p_plan_id
          AND teacher_id = v_teacher_id
          AND is_deleted = 0
          AND NOW() <= grade_deadline
    ) THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = '这不是你的课或已过成绩录入截止时间';
    END IF;

    -- 3. 检查学生是否存在并且确实选了这门课
    SET v_student_id = fn_get_student_id(p_student_no);
    IF v_student_id IS NULL THEN
        SET v_msg = CONCAT('学生 ', p_student_no, ' 不存在');
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = v_msg;
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM enrollment
        WHERE offering_id = p_plan_id
          AND student_id = v_student_id
          AND is_deleted = 0
    ) THEN
        SET v_msg = CONCAT('学号为 ', p_student_no, ' 的学生未选这门课');
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = v_msg;
    END IF;

    -- 4. 检查成绩范围并录入
    IF p_score NOT BETWEEN 0 AND 100 THEN
        SET v_msg = CONCAT('成绩 ', p_score, ' 不在 0~100 之间');
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = v_msg;
    END IF;

    UPDATE enrollment
    SET score = p_score
    WHERE offering_id = p_plan_id
      AND student_id = v_student_id;

    COMMIT;
    SELECT '成绩录入成功' AS message;
END;;

DELIMITER ;


-- ------------------------------------------------------------
-- 7.5 按班级输出学生名单（含学籍分）
-- 说明：教务输入班级ID，输出学号、姓名、学籍分、绩点分
-- ------------------------------------------------------------
DROP PROCEDURE IF EXISTS sp_student_roster;
DELIMITER ;;

CREATE PROCEDURE sp_student_roster(
    p_class_id INT
)
BEGIN
    SELECT
        no              AS student_no,
        name            AS student_name,
        weighted_score,
        gpa
    FROM student
    WHERE class_id = p_class_id
      AND is_deleted = 0
    ORDER BY no;
END;;

DELIMITER ;


-- ------------------------------------------------------------
-- 7.6 按班级+课程统计成绩
-- 说明：传入班级ID和课程ID，输出平均/最高/最低/及格率
-- ------------------------------------------------------------
DROP PROCEDURE IF EXISTS sp_class_grade_report;
DELIMITER ;;

CREATE PROCEDURE sp_class_grade_report(
    p_class_id  INT,
    p_course_id INT
)
BEGIN
    SELECT
        AVG(e.score)                        AS avg_score,
        MAX(e.score)                        AS max_score,
        MIN(e.score)                        AS min_score,
        ROUND(
            SUM(CASE WHEN e.score >= 60 THEN 1 ELSE 0 END) / COUNT(*) * 100,
            2
        )                                   AS pass_rate,
        COUNT(*)                            AS student_count
    FROM enrollment e
    JOIN student s         ON e.student_id  = s.id
    JOIN course_offering co ON e.offering_id = co.id
    WHERE s.class_id   = p_class_id
      AND co.course_id = p_course_id
      AND e.score IS NOT NULL
      AND e.is_deleted = 0
      AND s.is_deleted = 0;
END;;

DELIMITER ;


-- ------------------------------------------------------------
-- 7.7 某学生某学期平均成绩
-- 说明：传入学号和学期，返回该学期所有课程平均分
-- ------------------------------------------------------------
DROP PROCEDURE IF EXISTS sp_student_semester_avg;
DELIMITER ;;

CREATE PROCEDURE sp_student_semester_avg(
    p_student_no VARCHAR(20),
    p_semester   VARCHAR(20)
)
BEGIN
    SELECT
        s.no                                AS student_no,
        s.name                              AS student_name,
        co.semester,
        COUNT(*)                            AS course_count,
        ROUND(AVG(e.score), 2)              AS avg_score
    FROM enrollment e
    JOIN student s          ON e.student_id  = s.id
    JOIN course_offering co ON e.offering_id = co.id
    WHERE s.no          = p_student_no
      AND co.semester   = p_semester
      AND e.score       IS NOT NULL
      AND e.is_deleted  = 0
    GROUP BY s.no, s.name, co.semester;
END;;

DELIMITER ;


-- ------------------------------------------------------------
-- 7.8 教师信息及授课统计
-- 说明：传教师工号，返回基本信息 + 授课统计
-- ------------------------------------------------------------
DROP PROCEDURE IF EXISTS sp_teacher_info;
DELIMITER ;;

CREATE PROCEDURE sp_teacher_info(
    p_teacher_no VARCHAR(20)
)
BEGIN
    SELECT
        t.no                                        AS teacher_no,
        t.name                                      AS teacher_name,
        t.title                                     AS title,
        COUNT(DISTINCT co.id)                       AS offering_count,
        COUNT(DISTINCT e.id)                        AS student_count,
        COUNT(DISTINCT CASE WHEN e.score IS NOT NULL THEN e.id END) AS graded_count
    FROM teacher t
    LEFT JOIN course_offering co ON t.id = co.teacher_id AND co.is_deleted = 0
    LEFT JOIN enrollment e ON co.id = e.offering_id AND e.is_deleted = 0
    WHERE t.no = p_teacher_no AND t.is_deleted = 0
    GROUP BY t.no, t.name, t.title;
END;;

DELIMITER ;


-- ------------------------------------------------------------
-- 7.9 全部教师列表及授课统计
-- 说明：返回所有在职教师的基本信息及授课汇总
-- ------------------------------------------------------------
DROP PROCEDURE IF EXISTS sp_teacher_list;
DELIMITER ;;

CREATE PROCEDURE sp_teacher_list()
BEGIN
    SELECT
        t.no                                        AS teacher_no,
        t.name                                      AS teacher_name,
        t.title                                     AS title,
        COUNT(DISTINCT co.id)                       AS offering_count,
        COUNT(DISTINCT e.id)                        AS student_count,
        COUNT(DISTINCT CASE WHEN e.score IS NOT NULL THEN e.id END) AS graded_count
    FROM teacher t
    LEFT JOIN course_offering co ON t.id = co.teacher_id AND co.is_deleted = 0
    LEFT JOIN enrollment e ON co.id = e.offering_id AND e.is_deleted = 0
    WHERE t.is_deleted = 0
    GROUP BY t.no, t.name, t.title
    ORDER BY offering_count DESC, t.no;
END;;

DELIMITER ;


SELECT '存储过程创建完成' AS message;
