-- ============================================================
-- LOAD DATA INFILE 极速导入 200 万数据
-- 用法：mysql -u root db_sms < test/load_large_data.sql
-- 前提：已运行 python test/generate_large_data.py
-- 预计：30 ~ 60 秒
-- ============================================================

-- ============================================================
-- 第一步：扩展学生基数
-- ============================================================
LOAD DATA LOCAL INFILE 'test/student_big.csv'
INTO TABLE student
FIELDS TERMINATED BY ',' ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(name, no, class_id, status);

SELECT CONCAT('✅ 学生已扩展至 ', (SELECT COUNT(*) FROM student WHERE is_deleted = 0), ' 人');

-- ============================================================
-- 第二步：删触发器（避免 200 万 × 5 次调用）
-- ============================================================
DROP TRIGGER IF EXISTS trg_enrollment_before_insert;
DROP TRIGGER IF EXISTS trg_enrollment_after_insert;
DROP TRIGGER IF EXISTS trg_enrollment_after_insert_score;
DROP TRIGGER IF EXISTS trg_enrollment_after_update;
DROP TRIGGER IF EXISTS trg_enrollment_after_update_score;

SELECT CONCAT('✅ 触发器已删除');

-- ============================================================
-- 第三步：性能调优 + LOAD DATA 极速导入
-- ============================================================
SET unique_checks = 0;
SET FOREIGN_KEY_CHECKS = 0;

LOAD DATA LOCAL INFILE 'test/enrollment_big.csv'
INTO TABLE enrollment
FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(offering_id, student_id, score);

SELECT CONCAT('✅ 选课导入完成，共 ', (SELECT COUNT(*) FROM enrollment), ' 条');

-- 更新排课人数
UPDATE course_offering co
SET co.current_students = (
    SELECT COUNT(*) FROM enrollment e
    WHERE e.offering_id = co.id AND e.is_deleted = 0
);

SELECT CONCAT('✅ 排课人数已同步');

-- ============================================================
-- 第四步：一次性批量重算 GPA（替代触发器逐行计算）
-- ============================================================
UPDATE student s
SET weighted_score = (
    SELECT ROUND(SUM(e.score * c.credit) / SUM(c.credit), 2)
    FROM enrollment e
    JOIN course_offering co ON e.offering_id = co.id
    JOIN course c ON co.course_id = c.id
    WHERE e.student_id = s.id AND e.score IS NOT NULL AND e.is_deleted = 0
),
gpa = (
    SELECT ROUND(SUM(c.credit * r.point) / SUM(c.credit), 2)
    FROM enrollment e
    JOIN course_offering co ON e.offering_id = co.id
    JOIN course c ON co.course_id = c.id
    JOIN grade_point_rule r ON e.score BETWEEN r.min_score AND r.max_score
    WHERE e.student_id = s.id AND e.score IS NOT NULL AND e.is_deleted = 0
)
WHERE s.is_deleted = 0;

SELECT CONCAT('✅ GPA 批量重算完成');

-- ============================================================
-- 第五步：恢复约束
-- ============================================================
SET UNIQUE_CHECKS = 1;
SET FOREIGN_KEY_CHECKS = 1;

-- ============================================================
-- 第六步：恢复触发器（从 sql/06_触发器.sql 复制）
-- ============================================================
DELIMITER $$
-- trg_enrollment_before_insert：选课前检查名额
CREATE TRIGGER trg_enrollment_before_insert
BEFORE INSERT ON enrollment FOR EACH ROW
BEGIN
    DECLARE v_current INT; DECLARE v_max INT;
    SELECT current_students, max_students INTO v_current, v_max
    FROM course_offering WHERE id = NEW.offering_id FOR UPDATE;
    IF v_current >= v_max THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = CONCAT('选课已满！当前 ', v_current, '/', v_max);
    END IF;
END$$

-- trg_enrollment_after_insert：选课后更新人数
CREATE TRIGGER trg_enrollment_after_insert
AFTER INSERT ON enrollment FOR EACH ROW
BEGIN
    UPDATE course_offering SET current_students = current_students + 1
    WHERE id = NEW.offering_id;
END$$

-- trg_enrollment_after_insert_score：选课带成绩时重算 GPA
CREATE TRIGGER trg_enrollment_after_insert_score
AFTER INSERT ON enrollment FOR EACH ROW
BEGIN
    IF NEW.score IS NOT NULL THEN
        UPDATE student s SET weighted_score = (
            SELECT ROUND(SUM(e.score * c.credit) / SUM(c.credit), 2)
            FROM enrollment e JOIN course_offering co ON e.offering_id = co.id
            JOIN course c ON co.course_id = c.id
            WHERE e.student_id = NEW.student_id AND e.score IS NOT NULL AND e.is_deleted = 0
        ), gpa = (
            SELECT ROUND(SUM(c.credit * r.point) / SUM(c.credit), 2)
            FROM enrollment e JOIN course_offering co ON e.offering_id = co.id
            JOIN course c ON co.course_id = c.id
            JOIN grade_point_rule r ON e.score BETWEEN r.min_score AND r.max_score
            WHERE e.student_id = NEW.student_id AND e.score IS NOT NULL AND e.is_deleted = 0
        ) WHERE s.id = NEW.student_id;
    END IF;
END$$

-- trg_enrollment_after_update：退选后更新人数
CREATE TRIGGER trg_enrollment_after_update
AFTER UPDATE ON enrollment FOR EACH ROW
BEGIN
    IF OLD.is_deleted = 0 AND NEW.is_deleted = 1 THEN
        UPDATE course_offering SET current_students = current_students - 1
        WHERE id = NEW.offering_id;
    END IF;
END;

-- trg_enrollment_after_update_score：成绩变化时重算 GPA
CREATE TRIGGER trg_enrollment_after_update_score
AFTER UPDATE ON enrollment FOR EACH ROW
BEGIN
    IF NOT (OLD.score <=> NEW.score) THEN
        UPDATE student s SET weighted_score = (
            SELECT ROUND(SUM(e.score * c.credit) / SUM(c.credit), 2)
            FROM enrollment e JOIN course_offering co ON e.offering_id = co.id
            JOIN course c ON co.course_id = c.id
            WHERE e.student_id = NEW.student_id AND e.score IS NOT NULL AND e.is_deleted = 0
        ), gpa = (
            SELECT ROUND(SUM(c.credit * r.point) / SUM(c.credit), 2)
            FROM enrollment e JOIN course_offering co ON e.offering_id = co.id
            JOIN course c ON co.course_id = c.id
            JOIN grade_point_rule r ON e.score BETWEEN r.min_score AND r.max_score
            WHERE e.student_id = NEW.student_id AND e.score IS NOT NULL AND e.is_deleted = 0
        ) WHERE s.id = NEW.student_id;
    END IF;
END$$

DELIMITER ;

SELECT CONCAT('✅ 触发器已恢复');

-- ============================================================
-- 第七步：清理 CSV
-- ============================================================
SELECT CONCAT('📊 最终统计:');
SELECT CONCAT('   学生: ', COUNT(*)) FROM student WHERE is_deleted = 0;
SELECT CONCAT('   排课: ', COUNT(*)) FROM course_offering WHERE is_deleted = 0;
SELECT CONCAT('   选课: ', COUNT(*)) FROM enrollment WHERE is_deleted = 0;

-- CSV 文件清理（手动执行或在 Python 中执行）
-- 建议：python -c "import os; os.remove('test/enrollment_big.csv'); os.remove('test/student_big.csv')"
