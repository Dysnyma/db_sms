-- ============================================================
-- 生成两百万测试数据
-- 用法：在 MySQL 中执行此文件，或复制内容到 MySQL 客户端运行
-- 前提：已通过 reset_data.py 导入基础数据（1000 学生 / 54 排课）
-- 预计执行时间：30 秒 ~ 2 分钟
-- ================================================  =============

-- ============================================================
-- 第一步：扩展学生基数至 20000 人
-- ============================================================
SET @base_id  = (SELECT MAX(id) FROM student);
SET @base_no  = (SELECT CAST(MAX(no) AS UNSIGNED) FROM student);
SET @cls_cnt  = (SELECT COUNT(*) FROM class WHERE is_deleted = 0);

INSERT INTO student (name, no, class_id, status)
SELECT
    CONCAT('用户', @base_id + n),
    @base_no + n,
    CEIL(RAND() * @cls_cnt),
    IF(RAND() < 0.15, 0, 1)
FROM (
    SELECT (@rn := @rn + 1) AS n
    FROM information_schema.COLUMNS a
    CROSS JOIN information_schema.COLUMNS b
    CROSS JOIN (SELECT @rn := 0) r
    LIMIT 19000
) t;

SELECT CONCAT('✅ 学生扩充完成，当前: ', (SELECT COUNT(*) FROM student WHERE is_deleted = 0), ' 人');

-- ============================================================
-- 第二步：扩展排课基数至 1000 条
-- ============================================================
SET @max_offering_id = (SELECT MAX(id) FROM course_offering);
SET @course_count    = (SELECT COUNT(*) FROM course WHERE is_deleted = 0);
SET @teacher_count   = (SELECT COUNT(*) FROM teacher WHERE is_deleted = 0);

INSERT INTO course_offering (course_id, teacher_id, semester, max_students,
                             enroll_start_time, enroll_end_time, grade_deadline)
SELECT
    CEIL(RAND() * @course_count) AS course_id,
    CEIL(RAND() * @teacher_count) AS teacher_id,
    ELT(FLOOR(RAND() * 6) + 1, '2024-2025-1','2024-2025-2','2025-2026-1','2025-2026-2','2026-2027-1','2026-2027-2') AS semester,
    FLOOR(30 + RAND() * 171) AS max_students,  -- 30~200
    DATE_ADD('2024-01-01', INTERVAL FLOOR(RAND() * 1095) DAY) AS enroll_start_time,
    DATE_ADD('2025-06-01', INTERVAL FLOOR(RAND() * 365) DAY) AS enroll_end_time,
    DATE_ADD('2026-01-01', INTERVAL FLOOR(RAND() * 365) DAY) AS grade_deadline
FROM (
    SELECT 1 FROM information_schema.COLUMNS a
    CROSS JOIN information_schema.COLUMNS b
    LIMIT 950
) tmp;

SELECT CONCAT('✅ 排课扩充完成，当前总数: ', (SELECT COUNT(*) FROM course_offering WHERE is_deleted = 0));

-- ============================================================
-- 第三步：生成 200 万选课 + 成绩
-- ============================================================
SET @max_offering_id = (SELECT MAX(id) FROM course_offering);
SET @max_student_id  = (SELECT MAX(id) FROM student);

INSERT IGNORE INTO enrollment (offering_id, student_id, score)
SELECT
    CEIL(RAND() * @max_offering_id) AS offering_id,
    CEIL(RAND() * @max_student_id)  AS student_id,
    -- 正态分布模拟成绩，约 25% 未录入
    IF(RAND() < 0.25, NULL, ROUND(30 + RAND() * 70, 1)) AS score
FROM (
    SELECT 1 FROM information_schema.COLUMNS a
    CROSS JOIN information_schema.COLUMNS b
    CROSS JOIN information_schema.COLUMNS c
    LIMIT 2000000
) tmp;

SELECT CONCAT('✅ 选课生成完成！');
SELECT CONCAT('   学生: ', (SELECT COUNT(*) FROM student WHERE is_deleted = 0));
SELECT CONCAT('   排课: ', (SELECT COUNT(*) FROM course_offering WHERE is_deleted = 0));
SELECT CONCAT('   选课: ', (SELECT COUNT(*) FROM enrollment WHERE is_deleted = 0));

-- 恢复外键检查
SET FOREIGN_KEY_CHECKS = 1;
