-- ============================================================
-- LOAD DATA INFILE 极速导入 200 万数据
-- 用法：mysql -u root db_sms < test/load_large_data.sql
-- 前提：已运行 python test/generate_large_data.py
-- 预计：30 ~ 60 秒
-- ============================================================

-- ============================================================
-- 第一步：扩展班级基数（学生表依赖 class_id）
-- ============================================================
LOAD DATA LOCAL INFILE 'class_big.csv'
INTO TABLE class
FIELDS TERMINATED BY ',' ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(name, grade, major, status);

SELECT CONCAT('✅ 班级已扩展至 ', (SELECT COUNT(*) FROM class WHERE is_deleted = 0), ' 个');

-- ============================================================
-- 第二步：扩展教师
-- ============================================================
LOAD DATA LOCAL INFILE 'teacher_big.csv'
INTO TABLE teacher
FIELDS TERMINATED BY ',' ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(name, no, title, phone, status);

SELECT CONCAT('✅ 教师已扩展至 ', (SELECT COUNT(*) FROM teacher WHERE is_deleted = 0), ' 人');

-- ============================================================
-- 第三步：扩展学生基数
-- ============================================================
LOAD DATA LOCAL INFILE 'student_big.csv'
INTO TABLE student
FIELDS TERMINATED BY ',' ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(name, no, class_id, status);

SELECT CONCAT('✅ 学生已扩展至 ', (SELECT COUNT(*) FROM student WHERE is_deleted = 0), ' 人');

-- ============================================================
-- 第四步：删触发器（避免 200 万 × 5 次调用）
-- ============================================================
DROP TRIGGER IF EXISTS trg_enrollment_before_insert;
DROP TRIGGER IF EXISTS trg_enrollment_after_insert;
DROP TRIGGER IF EXISTS trg_enrollment_after_insert_score;
DROP TRIGGER IF EXISTS trg_enrollment_after_update;
DROP TRIGGER IF EXISTS trg_enrollment_after_update_score;

SELECT CONCAT('✅ 触发器已删除');

-- ============================================================
-- 第五步：性能调优 + LOAD DATA 极速导入
-- ============================================================
SET unique_checks = 0;
SET FOREIGN_KEY_CHECKS = 0;

LOAD DATA LOCAL INFILE 'enrollment_big.csv'
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
-- 第六步：一次性批量重算 GPA（替代触发器逐行计算）
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
-- 第八步：恢复约束
-- ============================================================
SET UNIQUE_CHECKS = 1;
SET FOREIGN_KEY_CHECKS = 1;

-- 触发器由 Python 脚本自动重建
SELECT CONCAT('✅ 导入完成，触发器由 Python 恢复');
