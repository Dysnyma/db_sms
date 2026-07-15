-- ============================================================
-- 生成两百万测试数据（性能优化版）
-- 用法：python src/reset_data.py → 然后运行此文件
-- 预计：30 秒 ~ 1 分钟
-- 策略：临时删除触发器 → 批量插入 → 末尾一次性批量重算 GPA
-- ============================================================

-- ============================================================
-- 第一步：扩展学生基数至 20000
-- ============================================================
SET @base_id = (SELECT MAX(id) FROM student);
SET @base_no = (SELECT CAST(MAX(no) AS UNSIGNED) FROM student);
SET @cls_cnt = (SELECT COUNT(*) FROM class WHERE is_deleted = 0);

INSERT INTO student (name, no, class_id, status)
SELECT CONCAT('用户', @base_id + n), @base_no + n,
       CEIL(RAND() * @cls_cnt), IF(RAND() < 0.15, 0, 1)
FROM (SELECT @rn := @rn + 1 AS n FROM information_schema.COLUMNS a
      CROSS JOIN information_schema.COLUMNS b
      CROSS JOIN (SELECT @rn := 0) r LIMIT 19000) t;

SELECT CONCAT('✅ 学生 20000 人');

-- ============================================================
-- 第二步：扩展排课至 1000 条
-- ============================================================
SET @course_cnt  = (SELECT COUNT(*) FROM course WHERE is_deleted = 0);
SET @teacher_cnt = (SELECT COUNT(*) FROM teacher WHERE is_deleted = 0);

INSERT INTO course_offering (course_id, teacher_id, semester, max_students,
                             enroll_start_time, enroll_end_time, grade_deadline)
SELECT CEIL(RAND() * @course_cnt), CEIL(RAND() * @teacher_cnt),
       ELT(FLOOR(RAND() * 6) + 1, '2024-2025-1','2024-2025-2','2025-2026-1',
           '2025-2026-2','2026-2027-1','2026-2027-2'),
       99999,
       DATE_ADD('2024-01-01', INTERVAL FLOOR(RAND() * 1095) DAY),
       DATE_ADD('2025-06-01', INTERVAL FLOOR(RAND() * 365) DAY),
       DATE_ADD('2026-01-01', INTERVAL FLOOR(RAND() * 365) DAY)
FROM (SELECT 1 FROM information_schema.COLUMNS a
      CROSS JOIN information_schema.COLUMNS b LIMIT 950) t;

SET @max_o = (SELECT MAX(id) FROM course_offering);
SET @max_s = (SELECT MAX(id) FROM student);
SELECT CONCAT('✅ 排课 ', @max_o, ' 条');

-- ============================================================
-- 第三步：性能优化设置 + 批量插入 200 万选课
-- ============================================================
-- 核心优化：删除触发器，避免 2M × 5 次触发器调用
DROP TRIGGER IF EXISTS trg_enrollment_before_insert;
DROP TRIGGER IF EXISTS trg_enrollment_after_insert;
DROP TRIGGER IF EXISTS trg_enrollment_after_insert_score;
DROP TRIGGER IF EXISTS trg_enrollment_after_update;
DROP TRIGGER IF EXISTS trg_enrollment_after_update_score;

-- 会话级优化（innodb_flush 和 sync_binlog 是全局变量，临时调低）
SET unique_checks = 0;
SET FOREIGN_KEY_CHECKS = 0;

INSERT IGNORE INTO enrollment (offering_id, student_id, score)
SELECT CEIL(RAND() * @max_o), CEIL(RAND() * @max_s),
       IF(RAND() < 0.25, NULL, ROUND(30 + RAND() * 70, 1))
FROM information_schema.COLUMNS a
CROSS JOIN information_schema.COLUMNS b
LIMIT 2000000;

SELECT CONCAT('✅ 选课 ', (SELECT COUNT(*) FROM enrollment), ' 条');

-- ============================================================
-- 第四步：一次性批量重算所有学生的学籍分和 GPA
-- ============================================================
-- 学籍分 = Σ(成绩 × 学分) / Σ(学分)
-- GPA    = Σ(学分 × 绩点) / Σ(学分)
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
-- 第五步：恢复触发器和约束
-- ============================================================
-- 从 sql/06_触发器.sql 复制而来
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
END;

-- trg_enrollment_after_insert：选课后更新人数
CREATE TRIGGER trg_enrollment_after_insert
AFTER INSERT ON enrollment FOR EACH ROW
BEGIN
    UPDATE course_offering SET current_students = current_students + 1
    WHERE id = NEW.offering_id;
END;

-- trg_enrollment_after_insert_score：选课带成绩时重算 GPA（INSERT 触发）
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
END;

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
END;

SET UNIQUE_CHECKS = 1;
SET FOREIGN_KEY_CHECKS = 1;

SELECT CONCAT('✅ 触发器已恢复');
SELECT CONCAT('📊 最终数据: 学生 ', (SELECT COUNT(*) FROM student WHERE is_deleted = 0),
              ', 排课 ', (SELECT COUNT(*) FROM course_offering WHERE is_deleted = 0),
              ', 选课 ', (SELECT COUNT(*) FROM enrollment WHERE is_deleted = 0));
