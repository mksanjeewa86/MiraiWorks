-- Initialize database with proper charset and collation
CREATE DATABASE IF NOT EXISTS hrms CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE hrms;

-- Create user if it doesn't exist
CREATE USER IF NOT EXISTS 'hrms'@'%' IDENTIFIED BY 'hrms123';
GRANT ALL PRIVILEGES ON hrms.* TO 'hrms'@'%';
FLUSH PRIVILEGES;