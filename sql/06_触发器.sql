-- ============================================================
-- 文件：06_触发器.sql
-- 说明：选课相关触发器 —— 名额检查 + 人数实时更新
-- 清单：
--   1. trg_enrollment_before_insert       —— 选课前检查名额是否已满
--   2. trg_enrollment_after_insert        —— 选课后 current_students +1
--   3. trg_enrollment_after_update        —— 退选后 current_students -1
--   4. trg_enrollment_after_insert_score —— 选课时有成绩则自动重算学籍分+绩点分
--   5. trg_enrollment_after_update_score  —— 成绩变化后自动重算学籍分+绩点分
-- ============================================================

USE db_sms;

-- ------------------------------------------------------------
-- 6.1 选课前：检查名额
-- ------------------------------------------------------------
DROP TRIGGER IF EXISTS trg_enrollment_before_insert;
DELIMITER ;;

CREATE TRIGGER trg_enrollment_before_insert
BEFORE INSERT ON enrollment
FOR EACH ROW
BEGIN
    DECLARE v_current INT;
    DECLARE v_max INT;
    DECLARE v_msg    VARCHAR(100);

    SELECT current_students, max_students
    INTO v_current, v_max
    FROM course_offering
    WHERE id = NEW.offering_id;

    IF v_current >= v_max THEN
        SET v_msg = CONCAT('选课已满！当前 ', v_current, '/', v_max);
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = v_msg;
    END IF;
END;;

DELIMITER ;


-- ------------------------------------------------------------
-- 6.2 选课后：人数 +1
-- ------------------------------------------------------------
DROP TRIGGER IF EXISTS trg_enrollment_after_insert;
DELIMITER ;;

CREATE TRIGGER trg_enrollment_after_insert
AFTER INSERT ON enrollment
FOR EACH ROW
BEGIN
    UPDATE course_offering
    SET current_students = current_students + 1
    WHERE id = NEW.offering_id;
END;;

DELIMITER ;


-- ------------------------------------------------------------
-- 6.3 退选后：人数 -1
-- ------------------------------------------------------------
DROP TRIGGER IF EXISTS trg_enrollment_after_update;
DELIMITER ;;

CREATE TRIGGER trg_enrollment_after_update
AFTER UPDATE ON enrollment
FOR EACH ROW
BEGIN
    -- 逻辑删除从 0 → 1 时，人数减一
    IF OLD.is_deleted = 0 AND NEW.is_deleted = 1 THEN
        UPDATE course_offering
        SET current_students = current_students - 1
        WHERE id = NEW.offering_id;
    END IF;
END;;

DELIMITER ;


-- ------------------------------------------------------------
-- 6.4 选课时：有成绩则自动重算学籍分 + 绩点分
-- ------------------------------------------------------------
DROP TRIGGER IF EXISTS trg_enrollment_after_insert_score;
DELIMITER ;;

CREATE TRIGGER trg_enrollment_after_insert_score
AFTER INSERT ON enrollment
FOR EACH ROW
BEGIN
    IF NEW.score IS NOT NULL THEN
        UPDATE student s
        SET weighted_score = (
            SELECT ROUND(SUM(e.score * c.credit) / SUM(c.credit), 2)
            FROM enrollment e
            JOIN course_offering co ON e.offering_id = co.id
            JOIN course c ON co.course_id = c.id
            WHERE e.student_id = NEW.student_id
              AND e.score IS NOT NULL
              AND e.is_deleted = 0
        ), gpa = (
            SELECT ROUND(SUM(c.credit * r.point) / SUM(c.credit), 2)
            FROM enrollment e
            JOIN course_offering co ON e.offering_id = co.id
            JOIN course c ON co.course_id = c.id
            JOIN grade_point_rule r ON e.score BETWEEN r.min_score AND r.max_score
            WHERE e.student_id = NEW.student_id
              AND e.score IS NOT NULL
              AND e.is_deleted = 0
        )
        WHERE s.id = NEW.student_id;
    END IF;
END;;

DELIMITER ;


-- ------------------------------------------------------------
-- 6.5 成绩变化后：自动重算学籍分 + 绩点分
-- ------------------------------------------------------------
DROP TRIGGER IF EXISTS trg_enrollment_after_update_score;
DELIMITER ;;

CREATE TRIGGER trg_enrollment_after_update_score
AFTER UPDATE ON enrollment
FOR EACH ROW
BEGIN
    -- 只在成绩实际变化时重算
    IF NOT (OLD.score <=> NEW.score) THEN

        -- 更新学籍分 = SUM(成绩×学分) / SUM(学分)
        UPDATE student s
        SET weighted_score = (
            SELECT ROUND(SUM(e.score * c.credit) / SUM(c.credit), 2)
            FROM enrollment e
            JOIN course_offering co ON e.offering_id = co.id
            JOIN course c ON co.course_id = c.id
            WHERE e.student_id = NEW.student_id
              AND e.score IS NOT NULL
              AND e.is_deleted = 0
        )
        WHERE s.id = NEW.student_id;

        -- 更新绩点分 = SUM(学分×绩点) / SUM(学分)
        UPDATE student s
        SET gpa = (
            SELECT ROUND(SUM(c.credit * r.point) / SUM(c.credit), 2)
            FROM enrollment e
            JOIN course_offering co ON e.offering_id = co.id
            JOIN course c ON co.course_id = c.id
            JOIN grade_point_rule r ON e.score BETWEEN r.min_score AND r.max_score
            WHERE e.student_id = NEW.student_id
              AND e.score IS NOT NULL
              AND e.is_deleted = 0
        )
        WHERE s.id = NEW.student_id;

    END IF;
END;;

DELIMITER ;


SELECT '触发器创建完成' AS message;
