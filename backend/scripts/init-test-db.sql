-- Test database initialization
-- This file is executed when the MySQL test container starts

-- Create test database (redundant but ensures it exists)
CREATE DATABASE IF NOT EXISTS miraiworks_test;

-- Grant permissions to test user
GRANT ALL PRIVILEGES ON miraiworks_test.* TO 'changeme'@'%';
FLUSH PRIVILEGES;

-- Set default character set
ALTER DATABASE miraiworks_test CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;