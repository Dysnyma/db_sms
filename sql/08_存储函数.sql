-- ============================================================
-- 文件：08_存储函数.sql
-- 说明：辅助查询函数，供存储过程调用
-- 清单：
--   1. fn_get_student_id —— 学号 → 学生ID
--   2. fn_get_teacher_id —— 工号 → 教师ID
-- ============================================================

USE db_sms;

-- ------------------------------------------------------------
-- 8.1 学号 → 学生ID
-- ------------------------------------------------------------
DROP FUNCTION IF EXISTS fn_get_student_id;
DELIMITER ;;

CREATE FUNCTION fn_get_student_id(
    p_student_no VARCHAR(20)
) RETURNS INT
READS SQL DATA
DETERMINISTIC
BEGIN
    DECLARE v_id INT;
    SELECT id INTO v_id
    FROM student
    WHERE no = p_student_no AND is_deleted = 0;
    RETURN v_id;
END;;

DELIMITER ;


-- ------------------------------------------------------------
-- 8.2 工号 → 教师ID
-- ------------------------------------------------------------
DROP FUNCTION IF EXISTS fn_get_teacher_id;
DELIMITER ;;

CREATE FUNCTION fn_get_teacher_id(
    p_teacher_no VARCHAR(20)
) RETURNS INT
READS SQL DATA
DETERMINISTIC
BEGIN
    DECLARE v_id INT;
    SELECT id INTO v_id
    FROM teacher
    WHERE no = p_teacher_no AND is_deleted = 0;
    RETURN v_id;
END;;

DELIMITER ;


SELECT '函数创建完成' AS message;
