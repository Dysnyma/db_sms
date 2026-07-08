-- ============================================================
-- 文件：01_数据库创建.sql
-- 说明：创建学生成绩管理系统数据库
-- 数据库：db_student_management_system (db_sms)
-- 字符集：utf8mb4
-- 排序规则：utf8mb4_unicode_ci
-- ============================================================

-- 创建数据库
DROP DATABASE IF EXISTS db_sms;
CREATE DATABASE db_sms
    DEFAULT CHARACTER SET utf8mb4
    DEFAULT COLLATE utf8mb4_unicode_ci;

USE db_sms;
