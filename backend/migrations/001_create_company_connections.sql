-- Migration: Create company_connections table
-- Date: 2025-10-11
-- Description: New company-based connection system to replace user_connections

-- Create company_connections table
CREATE TABLE IF NOT EXISTS company_connections (
    id INT PRIMARY KEY AUTO_INCREMENT,

    -- Source entity (can be user or company)
    source_type ENUM('user', 'company') NOT NULL COMMENT 'Type of source entity: user or company',
    source_user_id INT NULL COMMENT 'User ID if source is a user',
    source_company_id INT NULL COMMENT 'Company ID if source is a company',

    -- Target entity (always a company for now)
    target_company_id INT NOT NULL COMMENT 'Target company ID',

    -- Connection metadata
    is_active BOOLEAN NOT NULL DEFAULT TRUE COMMENT 'Whether connection is active',
    connection_type VARCHAR(50) NOT NULL DEFAULT 'standard' COMMENT 'Type of connection: standard, partnership, etc',

    -- Permissions (for future expansion)
    can_message BOOLEAN NOT NULL DEFAULT TRUE COMMENT 'Can send messages',
    can_view_profile BOOLEAN NOT NULL DEFAULT TRUE COMMENT 'Can view profiles',
    can_assign_tasks BOOLEAN NOT NULL DEFAULT FALSE COMMENT 'Can assign tasks',

    -- Creation tracking
    creation_type VARCHAR(20) NOT NULL DEFAULT 'manual' COMMENT 'How connection was created: manual, automatic, api',
    created_by INT NULL COMMENT 'User who created this connection',

    -- Timestamps
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'When connection was created',
    updated_at DATETIME NULL ON UPDATE CURRENT_TIMESTAMP COMMENT 'When connection was last updated',

    -- Foreign keys
    CONSTRAINT fk_cc_source_user FOREIGN KEY (source_user_id) REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT fk_cc_source_company FOREIGN KEY (source_company_id) REFERENCES companies(id) ON DELETE CASCADE,
    CONSTRAINT fk_cc_target_company FOREIGN KEY (target_company_id) REFERENCES companies(id) ON DELETE CASCADE,
    CONSTRAINT fk_cc_created_by FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL,

    -- Indexes for performance
    INDEX idx_source_user (source_user_id, is_active),
    INDEX idx_source_company (source_company_id, is_active),
    INDEX idx_target_company (target_company_id, is_active),
    INDEX idx_created_by (created_by),
    INDEX idx_active (is_active),
    INDEX idx_created_at (created_at),

    -- Constraints
    CONSTRAINT chk_source_entity CHECK (
        (source_type = 'user' AND source_user_id IS NOT NULL AND source_company_id IS NULL) OR
        (source_type = 'company' AND source_company_id IS NOT NULL AND source_user_id IS NULL)
    ),

    -- Prevent duplicate user-to-company connections
    CONSTRAINT unique_user_company_connection UNIQUE (source_user_id, target_company_id),

    -- Prevent duplicate company-to-company connections
    CONSTRAINT unique_company_connection UNIQUE (source_company_id, target_company_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Company-based connections for messaging and interactions';

-- Note: user_connections table kept as-is for now (legacy backup)
