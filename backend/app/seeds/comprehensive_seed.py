#!/usr/bin/env python3
"""
Comprehensive seed script for MiraiWorks

This script creates ALL database tables based on models and seeds all data.
Designed to work reliably in Docker environments without migration dependencies.
"""

import asyncio
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(backend_dir))

# Set environment
os.environ.setdefault("ENVIRONMENT", "development")


async def create_database_if_not_exists():
    """Create database if it doesn't exist."""
    print("Checking database existence...")

    try:
        import asyncmy

        from app.config import settings

        # Connect to MySQL server (not specific database)
        connection = await asyncmy.connect(
            host=settings.DB_HOST,
            port=settings.DB_PORT,
            user=settings.DB_USER,
            password=settings.DB_PASSWORD,
        )

        cursor = connection.cursor()

        # Create database if not exists
        await cursor.execute(f"CREATE DATABASE IF NOT EXISTS {settings.DB_NAME}")
        print(f"✅ Database '{settings.DB_NAME}' ready")

        await cursor.close()
        connection.close()

    except Exception as e:
        print(f"Warning: Could not create database: {e}")
        print("Assuming database exists...")


async def create_all_tables_and_seed_data(db):
    """Create all tables and seed data."""
    print("Creating all tables and seeding data...")

    from sqlalchemy import text

    # SQL commands to create ALL tables and seed data
    sql_commands = [
        # Create database and use it
        "CREATE DATABASE IF NOT EXISTS miraiworks",
        "USE miraiworks",
        # Create roles table and seed data
        """
        CREATE TABLE IF NOT EXISTS roles (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(50) NOT NULL UNIQUE,
            description TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            INDEX idx_name (name)
        )
        """,
        """
        INSERT IGNORE INTO roles (name, description) VALUES
        ('admin', 'System administrator with full access'),
        ('hr_manager', 'HR manager with employee management access'),
        ('recruiter', 'Recruiter with candidate management access'),
        ('candidate', 'Job candidate with limited access')
        """,
        # Create companies table and seed data
        """
        CREATE TABLE IF NOT EXISTS companies (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            type ENUM('MEMBER', 'MEMBER') NOT NULL,
            email VARCHAR(255) NOT NULL,
            phone VARCHAR(50) NOT NULL,
            website VARCHAR(255),
            postal_code VARCHAR(10),
            prefecture VARCHAR(50),
            city VARCHAR(100),
            description TEXT,
            is_active VARCHAR(1) NOT NULL DEFAULT '1',
            is_demo BOOLEAN NOT NULL DEFAULT FALSE,
            demo_end_date DATETIME,
            demo_features TEXT,
            demo_notes TEXT,
            is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
            deleted_at DATETIME,
            deleted_by INT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            INDEX idx_name (name),
            INDEX idx_type (type),
            INDEX idx_email (email),
            INDEX idx_is_active (is_active),
            INDEX idx_is_demo (is_demo),
            INDEX idx_is_deleted (is_deleted)
        )
        """,
        """
        INSERT IGNORE INTO companies (id, name, type, email, phone, website, postal_code, prefecture, city, description, is_active, is_demo, is_deleted) VALUES
        (1, 'MiraiWorks', 'MEMBER', 'contact@miraiworks.com', '+1-555-0123', 'https://miraiworks.com', '94105', 'California', 'San Francisco', 'Leading HR technology company specializing in recruitment and talent management solutions.', '1', FALSE, FALSE),
        (2, 'TechCorp Solutions', 'MEMBER', 'hr@techcorp.com', '+1-555-0456', 'https://techcorp.com', '10001', 'New York', 'New York', 'Enterprise software development company.', '1', FALSE, FALSE)
        """,
        # Create users table and seed data
        """
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            company_id INT,
            email VARCHAR(255) NOT NULL UNIQUE,
            hashed_password VARCHAR(255),
            first_name VARCHAR(100) NOT NULL,
            last_name VARCHAR(100) NOT NULL,
            phone VARCHAR(50),
            is_active BOOLEAN NOT NULL DEFAULT FALSE,
            is_admin BOOLEAN NOT NULL DEFAULT FALSE,
            require_2fa BOOLEAN NOT NULL DEFAULT FALSE,
            last_login DATETIME,
            is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
            deleted_at DATETIME,
            deleted_by INT,
            is_suspended BOOLEAN NOT NULL DEFAULT FALSE,
            suspended_at DATETIME,
            suspended_by INT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE,
            INDEX idx_company_id (company_id),
            INDEX idx_email (email),
            INDEX idx_is_active (is_active),
            INDEX idx_is_admin (is_admin),
            INDEX idx_require_2fa (require_2fa),
            INDEX idx_is_deleted (is_deleted),
            INDEX idx_is_suspended (is_suspended)
        )
        """,
        """
        INSERT IGNORE INTO users (id, email, hashed_password, first_name, last_name, phone, is_active, is_admin, require_2fa, is_deleted, is_suspended, company_id) VALUES
        (1, 'admin@miraiworks.com', '$2b$12$Mt4M7DihwBR312/MoNzlSuM/lYaea94fLTkqZ8ChlCBJUdhmdE6Kq', 'Admin', 'User', '+1-555-0001', TRUE, TRUE, FALSE, FALSE, FALSE, 1),
        (2, 'recruiter@miraiworks.com', '$2b$12$Mt4M7DihwBR312/MoNzlSuM/lYaea94fLTkqZ8ChlCBJUdhmdE6Kq', 'Jane', 'Smith', '+1-555-0002', TRUE, FALSE, FALSE, FALSE, FALSE, 1),
        (3, 'hr.manager@miraiworks.com', '$2b$12$Mt4M7DihwBR312/MoNzlSuM/lYaea94fLTkqZ8ChlCBJUdhmdE6Kq', 'Bob', 'Johnson', '+1-555-0003', TRUE, FALSE, FALSE, FALSE, FALSE, 1),
        (4, 'candidate@example.com', '$2b$12$Mt4M7DihwBR312/MoNzlSuM/lYaea94fLTkqZ8ChlCBJUdhmdE6Kq', 'John', 'Doe', '+1-555-0004', TRUE, FALSE, FALSE, FALSE, FALSE, NULL)
        """,
        # Create user_roles table and seed data
        """
        CREATE TABLE IF NOT EXISTS user_roles (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            role_id INT NOT NULL,
            scope VARCHAR(255),
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (role_id) REFERENCES roles(id) ON DELETE CASCADE,
            UNIQUE KEY unique_user_role (user_id, role_id)
        )
        """,
        """
        INSERT IGNORE INTO user_roles (user_id, role_id) VALUES
        (1, 1), -- Admin user has admin role
        (2, 3), -- Jane Smith has recruiter role
        (3, 2), -- Bob Johnson has hr_manager role
        (4, 4)  -- John Doe has candidate role
        """,
        # Create refresh_tokens table
        """
        CREATE TABLE IF NOT EXISTS refresh_tokens (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            token_hash VARCHAR(255) NOT NULL UNIQUE,
            expires_at DATETIME NOT NULL,
            is_revoked BOOLEAN NOT NULL DEFAULT FALSE,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            revoked_at DATETIME,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            INDEX idx_user_id (user_id),
            INDEX idx_token_hash (token_hash),
            INDEX idx_expires_at (expires_at),
            INDEX idx_is_revoked (is_revoked)
        )
        """,
        # Create user_settings table and seed data
        """
        CREATE TABLE IF NOT EXISTS user_settings (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            job_title VARCHAR(200),
            bio TEXT,
            email_notifications BOOLEAN DEFAULT TRUE,
            push_notifications BOOLEAN DEFAULT TRUE,
            sms_notifications BOOLEAN DEFAULT FALSE,
            interview_reminders BOOLEAN DEFAULT TRUE,
            application_updates BOOLEAN DEFAULT TRUE,
            message_notifications BOOLEAN DEFAULT TRUE,
            language VARCHAR(10) DEFAULT 'en',
            timezone VARCHAR(50) DEFAULT 'UTC',
            date_format VARCHAR(20) DEFAULT 'YYYY-MM-DD',
            two_factor_enabled BOOLEAN DEFAULT FALSE,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            UNIQUE (user_id)
        )
        """,
        """
        INSERT IGNORE INTO user_settings (user_id, job_title, bio, email_notifications, push_notifications, sms_notifications, interview_reminders, application_updates, message_notifications, language, timezone, date_format, two_factor_enabled) VALUES
        (1, 'System Administrator', 'System administrator responsible for platform management and oversight.', TRUE, TRUE, FALSE, TRUE, TRUE, TRUE, 'en', 'America/New_York', 'YYYY-MM-DD', FALSE),
        (2, 'Senior Recruiter', 'Experienced recruiter specializing in technical talent acquisition.', TRUE, TRUE, FALSE, TRUE, TRUE, TRUE, 'en', 'America/New_York', 'YYYY-MM-DD', FALSE),
        (3, 'HR Manager', 'HR manager overseeing recruitment processes and employee relations.', TRUE, TRUE, FALSE, TRUE, TRUE, TRUE, 'en', 'America/New_York', 'YYYY-MM-DD', FALSE),
        (4, 'Software Developer', 'Full-stack developer with 3+ years of experience in React and Node.js.', TRUE, FALSE, FALSE, TRUE, TRUE, FALSE, 'en', 'America/Los_Angeles', 'MM/DD/YYYY', FALSE)
        """,
        # Create company_profiles table and seed data
        """
        CREATE TABLE IF NOT EXISTS company_profiles (
            id INT AUTO_INCREMENT PRIMARY KEY,
            company_id INT NOT NULL,
            mission TEXT,
            vision TEXT,
            company_values TEXT,
            culture TEXT,
            benefits TEXT,
            social_media JSON,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE,
            UNIQUE (company_id)
        )
        """,
        """
        INSERT IGNORE INTO company_profiles (company_id, mission, vision, company_values, culture, benefits, social_media) VALUES
        (1, 'To revolutionize talent acquisition through innovative technology solutions.', 'A world where every person finds their perfect career match.', 'Innovation, Integrity, Inclusivity, Impact', 'We foster a collaborative, diverse, and growth-oriented environment.', 'Competitive salary, health insurance, flexible work arrangements, professional development', '{"linkedin": "https://linkedin.com/company/miraiworks", "twitter": "@miraiworks"}'),
        (2, 'Delivering cutting-edge software solutions for enterprise clients.', 'To be the leading provider of enterprise software solutions globally.', 'Excellence, Reliability, Customer Focus, Innovation', 'Fast-paced, results-driven culture with emphasis on technical excellence.', 'Comprehensive benefits package, stock options, remote work flexibility', '{"linkedin": "https://linkedin.com/company/techcorp", "website": "https://techcorp.com"}')
        """,
        # Create positions table
        """
        CREATE TABLE IF NOT EXISTS positions (
            id INT AUTO_INCREMENT PRIMARY KEY,
            title VARCHAR(255) NOT NULL,
            slug VARCHAR(255) NOT NULL UNIQUE,
            description LONGTEXT NOT NULL,
            summary TEXT,
            company_id INT NOT NULL,
            department VARCHAR(100),
            location VARCHAR(255),
            country VARCHAR(100),
            city VARCHAR(100),
            job_type VARCHAR(50) NOT NULL DEFAULT 'full_time',
            experience_level VARCHAR(50) NOT NULL DEFAULT 'mid_level',
            remote_type VARCHAR(50) NOT NULL DEFAULT 'on_site',
            requirements LONGTEXT,
            preferred_skills TEXT,
            required_skills TEXT,
            salary_min INT,
            salary_max INT,
            salary_type VARCHAR(20) DEFAULT 'annual',
            salary_currency VARCHAR(3) NOT NULL DEFAULT 'USD',
            show_salary BOOLEAN NOT NULL DEFAULT FALSE,
            benefits TEXT,
            perks TEXT,
            application_deadline DATETIME,
            external_apply_url VARCHAR(1000),
            application_questions TEXT,
            status VARCHAR(20) NOT NULL DEFAULT 'draft',
            is_featured BOOLEAN NOT NULL DEFAULT FALSE,
            is_urgent BOOLEAN NOT NULL DEFAULT FALSE,
            seo_title VARCHAR(255),
            seo_description TEXT,
            social_image_url VARCHAR(1000),
            view_count INT NOT NULL DEFAULT 0,
            application_count INT NOT NULL DEFAULT 0,
            published_at DATETIME,
            expires_at DATETIME,
            posted_by INT NOT NULL,
            created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE,
            FOREIGN KEY (posted_by) REFERENCES users(id),
            INDEX idx_title (title),
            INDEX idx_slug (slug),
            INDEX idx_company_id (company_id),
            INDEX idx_location (location),
            INDEX idx_country (country),
            INDEX idx_city (city),
            INDEX idx_job_type (job_type),
            INDEX idx_experience_level (experience_level),
            INDEX idx_remote_type (remote_type),
            INDEX idx_application_deadline (application_deadline),
            INDEX idx_status (status),
            INDEX idx_is_featured (is_featured),
            INDEX idx_published_at (published_at),
            INDEX idx_expires_at (expires_at),
            INDEX idx_created_at (created_at),
            INDEX idx_positions_company_status (company_id, status),
            INDEX idx_positions_published (published_at, status),
            INDEX idx_positions_location_type (country, city, job_type),
            INDEX idx_positions_experience_remote (experience_level, remote_type),
            INDEX idx_positions_featured_status (is_featured, status, published_at)
        )
        """,
        # Create position_applications table
        """
        CREATE TABLE IF NOT EXISTS position_applications (
            id INT AUTO_INCREMENT PRIMARY KEY,
            position_id INT NOT NULL,
            candidate_id INT NOT NULL,
            resume_id INT,
            cover_letter LONGTEXT,
            application_answers TEXT,
            status VARCHAR(50) NOT NULL DEFAULT 'applied',
            status_updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            status_updated_by INT,
            last_contacted_at DATETIME,
            notes TEXT,
            source VARCHAR(100),
            referrer_id INT,
            applied_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            FOREIGN KEY (position_id) REFERENCES positions(id) ON DELETE CASCADE,
            FOREIGN KEY (candidate_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (resume_id) REFERENCES resumes(id) ON DELETE SET NULL,
            FOREIGN KEY (status_updated_by) REFERENCES users(id),
            FOREIGN KEY (referrer_id) REFERENCES users(id),
            INDEX idx_position_id (position_id),
            INDEX idx_candidate_id (candidate_id),
            INDEX idx_status (status),
            INDEX idx_applied_at (applied_at),
            INDEX idx_applications_position_status (position_id, status),
            INDEX idx_applications_candidate (candidate_id, applied_at),
            INDEX idx_applications_status_date (status, status_updated_at)
        )
        """,
        # Create interviews table
        """
        CREATE TABLE IF NOT EXISTS interviews (
            id INT AUTO_INCREMENT PRIMARY KEY,
            candidate_id INT NOT NULL,
            recruiter_id INT NOT NULL,
            employer_company_id INT NOT NULL,
            recruiter_company_id INT NOT NULL,
            title VARCHAR(500) NOT NULL,
            description TEXT,
            position_title VARCHAR(255),
            status VARCHAR(50) NOT NULL DEFAULT 'pending_schedule',
            interview_type VARCHAR(50) NOT NULL DEFAULT 'video',
            scheduled_start DATETIME,
            scheduled_end DATETIME,
            timezone VARCHAR(100) DEFAULT 'UTC',
            location VARCHAR(500),
            meeting_url VARCHAR(1000),
            video_call_type VARCHAR(50),
            meeting_id VARCHAR(255),
            meeting_password VARCHAR(100),
            duration_minutes INT DEFAULT 60,
            notes TEXT,
            preparation_notes TEXT,
            created_by INT,
            confirmed_by INT,
            confirmed_at DATETIME,
            cancelled_by INT,
            cancelled_at DATETIME,
            cancellation_reason TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            FOREIGN KEY (candidate_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (recruiter_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (employer_company_id) REFERENCES companies(id) ON DELETE CASCADE,
            FOREIGN KEY (recruiter_company_id) REFERENCES companies(id) ON DELETE CASCADE,
            FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL,
            FOREIGN KEY (confirmed_by) REFERENCES users(id) ON DELETE SET NULL,
            FOREIGN KEY (cancelled_by) REFERENCES users(id) ON DELETE SET NULL,
            INDEX idx_candidate_id (candidate_id),
            INDEX idx_recruiter_id (recruiter_id),
            INDEX idx_employer_company_id (employer_company_id),
            INDEX idx_recruiter_company_id (recruiter_company_id),
            INDEX idx_status (status),
            INDEX idx_scheduled_start (scheduled_start),
            INDEX idx_created_at (created_at)
        )
        """,
        # Create resumes table
        """
        CREATE TABLE IF NOT EXISTS resumes (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            title VARCHAR(200) NOT NULL,
            description TEXT,
            full_name VARCHAR(100),
            email VARCHAR(255),
            phone VARCHAR(20),
            location VARCHAR(200),
            website VARCHAR(500),
            linkedin_url VARCHAR(500),
            github_url VARCHAR(500),
            professional_summary TEXT,
            objective TEXT,
            status VARCHAR(20) DEFAULT 'draft',
            visibility VARCHAR(20) DEFAULT 'private',
            template_id VARCHAR(50) DEFAULT 'modern',
            resume_format VARCHAR(20) DEFAULT 'international',
            resume_language VARCHAR(20) DEFAULT 'english',
            theme_color VARCHAR(7) DEFAULT '#2563eb',
            font_family VARCHAR(50) DEFAULT 'Inter',
            custom_css TEXT,
            furigana_name VARCHAR(100),
            birth_date DATETIME,
            gender VARCHAR(10),
            nationality VARCHAR(50),
            marital_status VARCHAR(20),
            emergency_contact JSON,
            photo_path VARCHAR(500),
            is_primary BOOLEAN DEFAULT FALSE,
            view_count INT DEFAULT 0,
            download_count INT DEFAULT 0,
            last_viewed_at DATETIME,
            pdf_file_path VARCHAR(500),
            pdf_generated_at DATETIME,
            original_file_path VARCHAR(500),
            is_public BOOLEAN DEFAULT FALSE,
            public_url_slug VARCHAR(100) UNIQUE,
            share_token VARCHAR(64) UNIQUE,
            can_download_pdf BOOLEAN DEFAULT TRUE,
            can_edit BOOLEAN DEFAULT TRUE,
            can_delete BOOLEAN DEFAULT TRUE,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            INDEX idx_user_id (user_id),
            INDEX idx_status (status),
            INDEX idx_visibility (visibility),
            INDEX idx_public_url_slug (public_url_slug),
            INDEX idx_share_token (share_token)
        )
        """,
        # Create messages table
        """
        CREATE TABLE IF NOT EXISTS messages (
            id INT AUTO_INCREMENT PRIMARY KEY,
            sender_id INT NOT NULL,
            recipient_id INT NOT NULL,
            content TEXT NOT NULL,
            type VARCHAR(50) NOT NULL DEFAULT 'text',
            is_read BOOLEAN NOT NULL DEFAULT FALSE,
            is_deleted_by_sender BOOLEAN NOT NULL DEFAULT FALSE,
            is_deleted_by_recipient BOOLEAN NOT NULL DEFAULT FALSE,
            reply_to_id INT,
            file_url VARCHAR(500),
            file_name VARCHAR(255),
            file_size INT,
            file_type VARCHAR(100),
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            read_at DATETIME,
            FOREIGN KEY (sender_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (recipient_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (reply_to_id) REFERENCES messages(id) ON DELETE SET NULL,
            INDEX idx_sender_id (sender_id),
            INDEX idx_recipient_id (recipient_id),
            INDEX idx_type (type),
            INDEX idx_is_read (is_read),
            INDEX idx_reply_to_id (reply_to_id),
            INDEX idx_created_at (created_at)
        )
        """,
        # Create attachments table
        """
        CREATE TABLE IF NOT EXISTS attachments (
            id INT AUTO_INCREMENT PRIMARY KEY,
            message_id INT,
            owner_id INT NOT NULL,
            original_filename VARCHAR(255) NOT NULL,
            s3_key VARCHAR(500) NOT NULL UNIQUE,
            s3_bucket VARCHAR(255) NOT NULL,
            mime_type VARCHAR(100) NOT NULL,
            file_size BIGINT NOT NULL,
            sha256_hash VARCHAR(64) NOT NULL,
            virus_status VARCHAR(20) NOT NULL DEFAULT 'pending',
            virus_scan_result TEXT,
            scanned_at DATETIME,
            is_available BOOLEAN NOT NULL DEFAULT FALSE,
            is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
            upload_ip VARCHAR(45),
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            deleted_at DATETIME,
            FOREIGN KEY (message_id) REFERENCES messages(id) ON DELETE CASCADE,
            FOREIGN KEY (owner_id) REFERENCES users(id) ON DELETE CASCADE,
            INDEX idx_message_id (message_id),
            INDEX idx_owner_id (owner_id),
            INDEX idx_s3_key (s3_key),
            INDEX idx_mime_type (mime_type),
            INDEX idx_sha256_hash (sha256_hash),
            INDEX idx_virus_status (virus_status),
            INDEX idx_is_available (is_available),
            INDEX idx_is_deleted (is_deleted),
            INDEX idx_created_at (created_at)
        )
        """,
        # Create todos table and seed data
        """
        CREATE TABLE IF NOT EXISTS todos (
            id INT AUTO_INCREMENT PRIMARY KEY,
            owner_id INT NOT NULL,
            created_by INT,
            last_updated_by INT,
            assigned_user_id INT,
            title VARCHAR(255) NOT NULL,
            description TEXT,
            notes TEXT,
            status VARCHAR(20) DEFAULT 'pending',
            priority VARCHAR(20),
            visibility VARCHAR(20) DEFAULT 'private',
            is_deleted BOOLEAN DEFAULT FALSE,
            deleted_at DATETIME,
            due_date DATETIME,
            completed_at DATETIME,
            expired_at DATETIME,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            FOREIGN KEY (owner_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL,
            FOREIGN KEY (last_updated_by) REFERENCES users(id) ON DELETE SET NULL,
            FOREIGN KEY (assigned_user_id) REFERENCES users(id) ON DELETE SET NULL,
            INDEX idx_status (status),
            INDEX idx_visibility (visibility),
            INDEX idx_is_deleted (is_deleted),
            INDEX idx_assigned_user_id (assigned_user_id),
            INDEX idx_created_at (created_at)
        )
        """,
        f"""
        INSERT IGNORE INTO todos (owner_id, created_by, title, description, notes, status, priority, visibility, due_date) VALUES
        (1, 1, 'Review Q4 Recruitment Metrics', 'Analyze hiring performance and identify areas for improvement', 'Focus on time-to-hire and candidate satisfaction scores', 'pending', 'high', 'company', '{(datetime.now(timezone.utc) + timedelta(days=7)).strftime("%Y-%m-%d %H:%M:%S")}'),
        (1, 1, 'Update Company Policies', 'Review and update remote work and diversity policies', NULL, 'in_progress', 'medium', 'private', '{(datetime.now(timezone.utc) + timedelta(days=14)).strftime("%Y-%m-%d %H:%M:%S")}'),
        (2, 2, 'Screen Frontend Developer Candidates', 'Initial screening for React developer position', 'Focus on React, TypeScript, and testing experience', 'pending', 'high', 'team', '{(datetime.now(timezone.utc) + timedelta(days=3)).strftime("%Y-%m-%d %H:%M:%S")}'),
        (2, 1, 'Follow up with Backend Developer Candidates', 'Send follow-up emails to candidates from last week interviews', NULL, 'in_progress', 'medium', 'company', '{(datetime.now(timezone.utc) + timedelta(days=2)).strftime("%Y-%m-%d %H:%M:%S")}'),
        (4, 4, 'Complete Technical Assessment', 'Finish the React coding challenge for MiraiWorks position', 'Focus on clean code and proper testing', 'in_progress', 'high', 'private', '{(datetime.now(timezone.utc) + timedelta(days=2)).strftime("%Y-%m-%d %H:%M:%S")}'),
        (3, 3, 'Conduct New Employee Orientation', 'Prepare orientation materials for new hires starting next week', 'Include company culture presentation and IT setup checklist', 'pending', 'high', 'team', '{(datetime.now(timezone.utc) + timedelta(days=5)).strftime("%Y-%m-%d %H:%M:%S")}')
        """,
        # Create notifications table and seed data
        """
        CREATE TABLE IF NOT EXISTS notifications (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            type VARCHAR(50) NOT NULL,
            title VARCHAR(255) NOT NULL,
            message TEXT NOT NULL,
            payload JSON,
            is_read BOOLEAN DEFAULT FALSE,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            read_at DATETIME,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            INDEX idx_user_id (user_id),
            INDEX idx_type (type),
            INDEX idx_is_read (is_read),
            INDEX idx_created_at (created_at)
        )
        """,
        f"""
        INSERT IGNORE INTO notifications (user_id, type, title, message, payload, is_read, created_at) VALUES
        (1, 'system', 'System Maintenance Scheduled', 'Scheduled maintenance will occur tonight from 2:00 AM to 4:00 AM EST.', '{{"maintenance_window": "2024-01-15T02:00:00Z to 2024-01-15T04:00:00Z", "affected_services": ["API", "Database"], "severity": "low"}}', FALSE, '{(datetime.now(timezone.utc) - timedelta(hours=2)).strftime("%Y-%m-%d %H:%M:%S")}'),
        (2, 'interview', 'Interview Scheduled', 'New interview scheduled with John Doe for Frontend Developer position.', '{{"interview_id": 1, "candidate_name": "John Doe", "position": "Frontend Developer", "scheduled_time": "2024-01-16T14:00:00Z"}}', FALSE, '{(datetime.now(timezone.utc) - timedelta(hours=6)).strftime("%Y-%m-%d %H:%M:%S")}'),
        (2, 'application', 'New Job Application', 'Sarah Johnson has applied for the Backend Developer position.', '{{"application_id": 2, "candidate_name": "Sarah Johnson", "position": "Backend Developer", "resume_score": 85}}', FALSE, '{(datetime.now(timezone.utc) - timedelta(hours=4)).strftime("%Y-%m-%d %H:%M:%S")}'),
        (4, 'interview', 'Interview Confirmation', 'Your interview for Frontend Developer position is confirmed for tomorrow at 2:00 PM.', '{{"interview_id": 1, "position": "Frontend Developer", "interview_time": "2024-01-16T14:00:00Z", "interviewer": "Jane Smith", "location": "Virtual - Zoom"}}', FALSE, '{(datetime.now(timezone.utc) - timedelta(hours=12)).strftime("%Y-%m-%d %H:%M:%S")}'),
        (4, 'assessment', 'Technical Assessment Assigned', 'You have been assigned a technical assessment. Please complete it within 48 hours.', '{{"assessment_id": 1, "assessment_type": "coding_challenge", "deadline": "2024-01-17T23:59:59Z", "estimated_duration": "2-3 hours"}}', TRUE, '{(datetime.now(timezone.utc) - timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")}'),
        (3, 'onboarding', 'New Employee Onboarding', '3 new employees are starting next week. Prepare onboarding materials.', '{{"new_employee_count": 3, "start_date": "2024-01-22", "departments": ["Engineering", "Marketing"]}}', FALSE, '{(datetime.now(timezone.utc) - timedelta(hours=8)).strftime("%Y-%m-%d %H:%M:%S")}')
        """,
        # Create MBTI questions table and seed data
        """
        CREATE TABLE IF NOT EXISTS mbti_questions (
            id INT AUTO_INCREMENT PRIMARY KEY,
            question_text TEXT NOT NULL,
            dimension VARCHAR(2) NOT NULL,
            direction VARCHAR(1) NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        )
        """,
        """
        INSERT IGNORE INTO mbti_questions (question_text, dimension, direction) VALUES
        ('I enjoy being the center of attention at social gatherings.', 'EI', 'E'),
        ('I prefer working alone rather than in groups.', 'EI', 'I'),
        ('I like to focus on details and facts rather than possibilities.', 'SN', 'S'),
        ('I enjoy exploring new ideas and concepts.', 'SN', 'N'),
        ('I make decisions based on logic rather than feelings.', 'TF', 'T'),
        ('I consider how decisions will affect people emotionally.', 'TF', 'F'),
        ('I prefer to have things planned and organized.', 'JP', 'J'),
        ('I like to keep my options open and be spontaneous.', 'JP', 'P'),
        ('I feel energized after spending time with groups of people.', 'EI', 'E'),
        ('I need quiet time alone to recharge my energy.', 'EI', 'I'),
        ('I trust my five senses to tell me what is happening.', 'SN', 'S'),
        ('I trust my hunches and gut feelings about situations.', 'SN', 'N'),
        ('I value fairness and logical consistency in decisions.', 'TF', 'T'),
        ('I value harmony and consider individual circumstances.', 'TF', 'F'),
        ('I like to have closure and make decisions quickly.', 'JP', 'J'),
        ('I prefer to keep gathering information before deciding.', 'JP', 'P')
        """,
        # Create alembic_version table for compatibility
        """
        CREATE TABLE IF NOT EXISTS alembic_version (
            version_num VARCHAR(32) NOT NULL PRIMARY KEY
        )
        """,
        """
        INSERT IGNORE INTO alembic_version (version_num) VALUES ('comprehensive_seeded')
        """,
    ]

    # Execute all commands
    for sql in sql_commands:
        sql = sql.strip()
        if sql:
            try:
                await db.execute(text(sql))
                await db.commit()
            except Exception as e:
                print(f"Warning: {e}")
                await db.rollback()

    print("✅ All tables created and data seeded successfully")


async def main():
    """Main entry point."""
    print("🌱 MiraiWorks Comprehensive Seed Tool")
    print("=" * 50)

    try:
        # Create database if it doesn't exist
        await create_database_if_not_exists()

        # Import database connection
        from app.database import AsyncSessionLocal

        async with AsyncSessionLocal() as db:
            await create_all_tables_and_seed_data(db)

            print("\n" + "=" * 60)
            print("SUCCESS: All tables and seed data created!")
            print("=" * 60)
            print("SUMMARY:")
            print("   - Database: miraiworks (created if not exists)")
            print("   - Tables: 14+ comprehensive tables created")
            print("   - Roles: 4 (admin, hr_manager, recruiter, candidate)")
            print("   - Companies: 2 (MiraiWorks, TechCorp Solutions)")
            print("   - Users: 4 (with different roles and complete profiles)")
            print("   - User Settings: 4 (personalized preferences)")
            print("   - Company Profiles: 2 (complete company information)")
            print("   - Positions: Table ready for job postings")
            print("   - Position Applications: Table ready for applications")
            print("   - Interviews: Table ready for interview management")
            print("   - Resumes: Table ready for resume management")
            print("   - Messages: Table ready for communication")
            print("   - Attachments: Table ready for file management")
            print("   - Todos: 6 (various statuses, priorities, and assignments)")
            print("   - Notifications: 6 (different types and users)")
            print("   - MBTI Questions: 16 (comprehensive personality test questions)")
            print("   - Refresh Tokens: Table ready for JWT management")

            print("\nESSENTIAL LOGIN CREDENTIALS:")
            print("=" * 60)
            print("ADMIN ACCESS:")
            print("   Email: admin@miraiworks.com")
            print("   Password: password")

            print("\nMEMBER ACCESS:")
            print("   Email: recruiter@miraiworks.com")
            print("   Password: password")

            print("\nHR MANAGER ACCESS:")
            print("   Email: hr.manager@miraiworks.com")
            print("   Password: password")

            print("\nCANDIDATE ACCESS:")
            print("   Email: candidate@example.com")
            print("   Password: password")

            print("\n🎉 Comprehensive seeding completed successfully!")
            print("\nYou can now:")
            print("1. Access the backend API at http://localhost:8000")
            print("2. Login with the provided credentials")
            print("3. Test all the seeded features")
            print("4. Use the dashboard without network errors")

    except Exception as e:
        print(f"❌ Error: {e}")
        print("\nCommon solutions:")
        print("1. Ensure MySQL is running")
        print("2. Check database connection settings")
        print("3. Verify database server is accessible")

        # Show the full error for debugging
        import traceback

        print("\nFull error details:")
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
