-- Reset all user passwords to 'password' in MiraiWorks database
-- The password hash is generated using bcrypt for 'password'

USE miraiworks;

-- Create companies if they don't exist
INSERT IGNORE INTO companies (name, domain, type, email, description, is_active, created_at, updated_at) VALUES
('TechCorp Solutions', 'techcorp.com', 'employer', 'hr@techcorp.com', 'Leading technology solutions provider', '1', NOW(), NOW()),
('Global Recruiters Inc', 'globalrecruiters.com', 'recruiter', 'info@globalrecruiters.com', 'Premier recruitment agency', '1', NOW(), NOW());

-- Get company IDs
SET @techcorp_id = (SELECT id FROM companies WHERE name = 'TechCorp Solutions' LIMIT 1);
SET @recruiters_id = (SELECT id FROM companies WHERE name = 'Global Recruiters Inc' LIMIT 1);

-- Create roles if they don't exist
INSERT IGNORE INTO roles (name, display_name, description, created_at, updated_at) VALUES
('super_admin', 'Super Administrator', 'Full system access', NOW(), NOW()),
('company_admin', 'Company Administrator', 'Company management access', NOW(), NOW()),
('recruiter', 'Recruiter', 'Recruitment access', NOW(), NOW()),
('candidate', 'Candidate', 'Job seeker access', NOW(), NOW());

-- Create or update users with password = 'password'
-- Password hash for 'password' using bcrypt: $2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewlBPtdCiGkOzVlW
INSERT INTO users (email, hashed_password, first_name, last_name, company_id, is_admin, is_active, created_at, updated_at) VALUES
('admin@techcorp.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewlBPtdCiGkOzVlW', 'Alice', 'Johnson', @techcorp_id, 1, 1, NOW(), NOW()),
('recruiter@globalrecruiters.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewlBPtdCiGkOzVlW', 'Sarah', 'Wilson', @recruiters_id, 0, 1, NOW(), NOW()),
('jane.candidate@email.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewlBPtdCiGkOzVlW', 'Jane', 'Developer', NULL, 0, 1, NOW(), NOW()),
('john.candidate@email.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewlBPtdCiGkOzVlW', 'John', 'Engineer', NULL, 0, 1, NOW(), NOW()),
('admin@miraiworks.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewlBPtdCiGkOzVlW', 'Super', 'Admin', NULL, 1, 1, NOW(), NOW())
ON DUPLICATE KEY UPDATE 
    hashed_password = VALUES(hashed_password),
    first_name = VALUES(first_name),
    last_name = VALUES(last_name),
    company_id = VALUES(company_id),
    is_admin = VALUES(is_admin),
    is_active = VALUES(is_active),
    updated_at = NOW();

-- Assign roles to users
INSERT IGNORE INTO user_roles (user_id, role_id, created_at)
SELECT u.id, r.id, NOW()
FROM users u
CROSS JOIN roles r
WHERE 
    (u.email = 'admin@miraiworks.com' AND r.name = 'super_admin') OR
    (u.email = 'admin@techcorp.com' AND r.name = 'company_admin') OR
    (u.email = 'recruiter@globalrecruiters.com' AND r.name = 'recruiter') OR
    (u.email = 'jane.candidate@email.com' AND r.name = 'candidate') OR
    (u.email = 'john.candidate@email.com' AND r.name = 'candidate');

-- Show created users
SELECT 
    u.id,
    u.email,
    u.first_name,
    u.last_name,
    c.name as company,
    CASE u.is_admin WHEN 1 THEN 'Yes' ELSE 'No' END as is_admin,
    'password' as password_hint
FROM users u
LEFT JOIN companies c ON u.company_id = c.id
ORDER BY u.email;

SELECT 'All users now have password: password' as message;