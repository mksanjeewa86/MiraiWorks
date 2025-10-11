-- Connect admin@miraiworks.com and candidate@example.com
INSERT INTO user_connections (user_id, connected_user_id, is_active, creation_type, created_by, created_at)
SELECT
    u1.id as user_id,
    u2.id as connected_user_id,
    TRUE as is_active,
    'manual' as creation_type,
    u1.id as created_by,
    NOW() as created_at
FROM users u1
CROSS JOIN users u2
WHERE u1.email = 'admin@miraiworks.com'
  AND u2.email = 'candidate@example.com'
  AND NOT EXISTS (
    SELECT 1 FROM user_connections
    WHERE (user_id = u1.id AND connected_user_id = u2.id)
       OR (user_id = u2.id AND connected_user_id = u1.id)
  );

-- Show the connection
SELECT
    u1.email as user1,
    u2.email as user2,
    uc.is_active,
    uc.creation_type
FROM user_connections uc
JOIN users u1 ON uc.user_id = u1.id
JOIN users u2 ON uc.connected_user_id = u2.id
WHERE (u1.email = 'admin@miraiworks.com' AND u2.email = 'candidate@example.com')
   OR (u1.email = 'candidate@example.com' AND u2.email = 'admin@miraiworks.com');
