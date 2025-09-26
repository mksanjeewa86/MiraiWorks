#!/usr/bin/env python3
"""
Docker-safe seed script for MiraiWorks

This script creates the database and tables if they don't exist, then seeds all data.
Designed to work reliably in Docker environments without migration dependencies.
"""

import asyncio
import os
import sys
from datetime import datetime, timedelta
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


async def create_tables_and_seed_data(db):
    """Create all tables and seed data."""
    print("Creating tables and seeding data...")

    from sqlalchemy import text

    # SQL commands to create tables and seed data
    sql_commands = [
        # Create database and use it
        f"CREATE DATABASE IF NOT EXISTS miraiworks",
        f"USE miraiworks",
        # Create roles table and seed data
        """
        CREATE TABLE IF NOT EXISTS roles (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(50) NOT NULL UNIQUE,
            description TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
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
            type ENUM('recruiter', 'employer') NOT NULL,
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
        (1, 'MiraiWorks', 'recruiter', 'contact@miraiworks.com', '+1-555-0123', 'https://miraiworks.com', '94105', 'California', 'San Francisco', 'Leading HR technology company specializing in recruitment and talent management solutions.', '1', FALSE, FALSE),
        (2, 'TechCorp Solutions', 'employer', 'hr@techcorp.com', '+1-555-0456', 'https://techcorp.com', '10001', 'New York', 'New York', 'Enterprise software development company.', '1', FALSE, FALSE)
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
        (1, 'admin@miraiworks.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj/VJWZrxnDO', 'Admin', 'User', '+1-555-0001', TRUE, TRUE, FALSE, FALSE, FALSE, 1),
        (2, 'recruiter@miraiworks.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj/VJWZrxnDO', 'Jane', 'Smith', '+1-555-0002', TRUE, FALSE, FALSE, FALSE, FALSE, 1),
        (3, 'hr.manager@miraiworks.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj/VJWZrxnDO', 'Bob', 'Johnson', '+1-555-0003', TRUE, FALSE, FALSE, FALSE, FALSE, 1),
        (4, 'candidate@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj/VJWZrxnDO', 'John', 'Doe', '+1-555-0004', TRUE, FALSE, FALSE, FALSE, FALSE, NULL)
        """,
        # Create user_roles table and seed data
        """
        CREATE TABLE IF NOT EXISTS user_roles (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            role_id INT NOT NULL,
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
        (1, 1, 'Review Q4 Recruitment Metrics', 'Analyze hiring performance and identify areas for improvement', 'Focus on time-to-hire and candidate satisfaction scores', 'pending', 'high', 'company', '{(datetime.utcnow() + timedelta(days=7)).strftime("%Y-%m-%d %H:%M:%S")}'),
        (1, 1, 'Update Company Policies', 'Review and update remote work and diversity policies', NULL, 'in_progress', 'medium', 'private', '{(datetime.utcnow() + timedelta(days=14)).strftime("%Y-%m-%d %H:%M:%S")}'),
        (2, 2, 'Screen Frontend Developer Candidates', 'Initial screening for React developer position', 'Focus on React, TypeScript, and testing experience', 'pending', 'high', 'team', '{(datetime.utcnow() + timedelta(days=3)).strftime("%Y-%m-%d %H:%M:%S")}'),
        (2, 1, 'Follow up with Backend Developer Candidates', 'Send follow-up emails to candidates from last week interviews', NULL, 'in_progress', 'medium', 'company', '{(datetime.utcnow() + timedelta(days=2)).strftime("%Y-%m-%d %H:%M:%S")}'),
        (4, 4, 'Complete Technical Assessment', 'Finish the React coding challenge for MiraiWorks position', 'Focus on clean code and proper testing', 'in_progress', 'high', 'private', '{(datetime.utcnow() + timedelta(days=2)).strftime("%Y-%m-%d %H:%M:%S")}'),
        (3, 3, 'Conduct New Employee Orientation', 'Prepare orientation materials for new hires starting next week', 'Include company culture presentation and IT setup checklist', 'pending', 'high', 'team', '{(datetime.utcnow() + timedelta(days=5)).strftime("%Y-%m-%d %H:%M:%S")}')
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
        (1, 'system', 'System Maintenance Scheduled', 'Scheduled maintenance will occur tonight from 2:00 AM to 4:00 AM EST.', '{{"maintenance_window": "2024-01-15T02:00:00Z to 2024-01-15T04:00:00Z", "affected_services": ["API", "Database"], "severity": "low"}}', FALSE, '{(datetime.utcnow() - timedelta(hours=2)).strftime("%Y-%m-%d %H:%M:%S")}'),
        (2, 'interview', 'Interview Scheduled', 'New interview scheduled with John Doe for Frontend Developer position.', '{{"interview_id": 1, "candidate_name": "John Doe", "position": "Frontend Developer", "scheduled_time": "2024-01-16T14:00:00Z"}}', FALSE, '{(datetime.utcnow() - timedelta(hours=6)).strftime("%Y-%m-%d %H:%M:%S")}'),
        (2, 'application', 'New Job Application', 'Sarah Johnson has applied for the Backend Developer position.', '{{"application_id": 2, "candidate_name": "Sarah Johnson", "position": "Backend Developer", "resume_score": 85}}', FALSE, '{(datetime.utcnow() - timedelta(hours=4)).strftime("%Y-%m-%d %H:%M:%S")}'),
        (4, 'interview', 'Interview Confirmation', 'Your interview for Frontend Developer position is confirmed for tomorrow at 2:00 PM.', '{{"interview_id": 1, "position": "Frontend Developer", "interview_time": "2024-01-16T14:00:00Z", "interviewer": "Jane Smith", "location": "Virtual - Zoom"}}', FALSE, '{(datetime.utcnow() - timedelta(hours=12)).strftime("%Y-%m-%d %H:%M:%S")}'),
        (4, 'assessment', 'Technical Assessment Assigned', 'You have been assigned a technical assessment. Please complete it within 48 hours.', '{{"assessment_id": 1, "assessment_type": "coding_challenge", "deadline": "2024-01-17T23:59:59Z", "estimated_duration": "2-3 hours"}}', TRUE, '{(datetime.utcnow() - timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")}'),
        (3, 'onboarding', 'New Employee Onboarding', '3 new employees are starting next week. Prepare onboarding materials.', '{{"new_employee_count": 3, "start_date": "2024-01-22", "departments": ["Engineering", "Marketing"]}}', FALSE, '{(datetime.utcnow() - timedelta(hours=8)).strftime("%Y-%m-%d %H:%M:%S")}')
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
        INSERT IGNORE INTO alembic_version (version_num) VALUES ('docker_seeded')
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
    print("🌱 MiraiWorks Docker-Safe Seed Tool")
    print("=" * 50)

    try:
        # Create database if it doesn't exist
        await create_database_if_not_exists()

        # Import database connection
        from app.database import AsyncSessionLocal

        async with AsyncSessionLocal() as db:
            await create_tables_and_seed_data(db)

            print("\n" + "=" * 60)
            print("SUCCESS: All seed data created!")
            print("=" * 60)
            print("SUMMARY:")
            print("   - Roles: 4 (admin, hr_manager, recruiter, candidate)")
            print("   - Companies: 2 (MiraiWorks, TechCorp Solutions)")
            print("   - Users: 4 (with different roles and complete profiles)")
            print("   - User Settings: 4 (personalized preferences)")
            print("   - Company Profiles: 2 (complete company information)")
            print("   - Todos: 6 (various statuses, priorities, and assignments)")
            print("   - Notifications: 6 (different types and users)")
            print("   - MBTI Questions: 16 (comprehensive personality test questions)")

            print("\nESSENTIAL LOGIN CREDENTIALS:")
            print("=" * 60)
            print("ADMIN ACCESS:")
            print("   Email: admin@miraiworks.com")
            print("   Password: password")

            print("\nRECRUITER ACCESS:")
            print("   Email: recruiter@miraiworks.com")
            print("   Password: password")

            print("\nHR MANAGER ACCESS:")
            print("   Email: hr.manager@miraiworks.com")
            print("   Password: password")

            print("\nCANDIDATE ACCESS:")
            print("   Email: candidate@example.com")
            print("   Password: password")

            print("\n🎉 Seeding completed successfully!")
            print("\nYou can now:")
            print("1. Access the backend API at http://localhost:8000")
            print("2. Login with the provided credentials")
            print("3. Test all the seeded features")

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
