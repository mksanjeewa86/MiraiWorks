-- Fix password hashes in MiraiWorks database
-- Update all users to have proper bcrypt hash for password 'password'

USE miraiworks;

-- First, fix the specific user that had the corrupted hash
UPDATE users 
SET hashed_password = '$2b$12$rUXVC0fajXLO/NcnE6CMz.Xll0kasunGiCoaQ7PHkr9vEdUlwE9BS',
    updated_at = NOW()
WHERE email = 'jane.candidate@email.com';

-- Update all other users with the correct bcrypt hash for 'password'
-- Hash: $2b$12$rUXVC0fajXLO/NcnE6CMz.Xll0kasunGiCoaQ7PHkr9vEdUlwE9BS
UPDATE users 
SET hashed_password = '$2b$12$rUXVC0fajXLO/NcnE6CMz.Xll0kasunGiCoaQ7PHkr9vEdUlwE9BS',
    updated_at = NOW()
WHERE hashed_password IS NOT NULL AND hashed_password != '$2b$12$rUXVC0fajXLO/NcnE6CMz.Xll0kasunGiCoaQ7PHkr9vEdUlwE9BS';

-- Verify the update
SELECT email, LEFT(hashed_password, 30) as hash_prefix, 'password' as password_hint
FROM users 
WHERE hashed_password IS NOT NULL
ORDER BY email;

SELECT 'Password hashes fixed successfully!' as status;