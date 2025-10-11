-- Rollback: Drop company_connections table
-- Date: 2025-10-11
-- Description: Rollback company_connections table creation

-- Drop the new table
DROP TABLE IF EXISTS company_connections;

-- Remove legacy marker from user_connections
ALTER TABLE user_connections
DROP COLUMN IF EXISTS is_legacy;

-- Remove index if it exists
ALTER TABLE user_connections
DROP INDEX IF EXISTS idx_is_legacy;
