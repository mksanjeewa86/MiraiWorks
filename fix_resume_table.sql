-- Fix resumes table to add missing columns
USE miraiworks;

-- Add missing enum values first
ALTER TABLE resumes MODIFY COLUMN status ENUM('draft', 'published', 'archived') DEFAULT 'draft';
ALTER TABLE resumes MODIFY COLUMN visibility ENUM('private', 'public', 'unlisted') DEFAULT 'private';

-- Add the missing columns
ALTER TABLE resumes
ADD COLUMN resume_format ENUM('RIREKISHO', 'SHOKUMU_KEIREKISHO', 'INTERNATIONAL', 'MODERN', 'CREATIVE') DEFAULT 'INTERNATIONAL' AFTER template_id,
ADD COLUMN resume_language ENUM('JAPANESE', 'ENGLISH', 'BILINGUAL') DEFAULT 'ENGLISH' AFTER resume_format,
ADD COLUMN furigana_name VARCHAR(100) NULL AFTER custom_css,
ADD COLUMN birth_date DATETIME NULL AFTER furigana_name,
ADD COLUMN gender VARCHAR(10) NULL AFTER birth_date,
ADD COLUMN nationality VARCHAR(50) NULL AFTER gender,
ADD COLUMN marital_status VARCHAR(20) NULL AFTER nationality,
ADD COLUMN emergency_contact JSON NULL AFTER marital_status,
ADD COLUMN photo_path VARCHAR(500) NULL AFTER emergency_contact,
ADD COLUMN is_public BOOLEAN DEFAULT FALSE AFTER original_file_path,
ADD COLUMN public_url_slug VARCHAR(100) NULL AFTER is_public,
ADD COLUMN can_download_pdf BOOLEAN DEFAULT TRUE AFTER share_token,
ADD COLUMN can_edit BOOLEAN DEFAULT TRUE AFTER can_download_pdf,
ADD COLUMN can_delete BOOLEAN DEFAULT TRUE AFTER can_edit;

-- Create index for public_url_slug
CREATE UNIQUE INDEX ix_resumes_public_url_slug ON resumes(public_url_slug);

-- Create resume_message_attachments table if it doesn't exist
CREATE TABLE IF NOT EXISTS resume_message_attachments (
    id INT PRIMARY KEY AUTO_INCREMENT,
    resume_id INT NOT NULL,
    message_id INT NOT NULL,
    auto_attached BOOLEAN DEFAULT FALSE,
    attachment_format VARCHAR(20) DEFAULT 'pdf',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (resume_id) REFERENCES resumes(id) ON DELETE CASCADE,
    FOREIGN KEY (message_id) REFERENCES messages(id) ON DELETE CASCADE
);

-- Update all existing resumes to have default values
UPDATE resumes SET
    resume_format = 'INTERNATIONAL',
    resume_language = 'ENGLISH',
    is_public = FALSE,
    can_download_pdf = TRUE,
    can_edit = TRUE,
    can_delete = TRUE
WHERE resume_format IS NULL OR resume_language IS NULL OR is_public IS NULL;

-- Fix the slug column to be public_url_slug (if they're different)
UPDATE resumes SET public_url_slug = slug WHERE public_url_slug IS NULL AND slug IS NOT NULL;

-- Set default status and visibility for existing records
UPDATE resumes SET status = 'draft' WHERE status IS NULL;
UPDATE resumes SET visibility = 'private' WHERE visibility IS NULL;

COMMIT;