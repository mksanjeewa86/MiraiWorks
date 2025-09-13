UPDATE users SET hashed_password = '$2b$12$vXKKsA.zSmpBdvshxYEePeKSJ0FKAwBJ29GcNs9ecm38ZpUoBjpGu' WHERE email = 'admin@example.com';
UPDATE users SET hashed_password = '$2b$12$de.VzsEL/pASkY0yuYTLo.53fC9bADX3jRm/LTLvTU7amBIaJrIuK' WHERE email = 'admin@ccc.com';
SELECT email, LEFT(hashed_password, 20) as hash_preview FROM users WHERE email IN ('admin@example.com', 'admin@ccc.com');