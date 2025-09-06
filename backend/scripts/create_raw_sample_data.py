#!/usr/bin/env python3
"""Create sample data using raw SQL to avoid model issues."""
import asyncio
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.database import AsyncSessionLocal
from app.services.auth_service import auth_service


async def test_connection():
    """Test database connection."""
    try:
        async with AsyncSessionLocal() as db:
            result = await db.execute(text("SELECT 1 as test"))
            row = result.fetchone()
            print(f"Database connection successful: {row[0]}")
            return True
    except Exception as e:
        print(f"Database connection failed: {str(e)}")
        return False


async def create_tables():
    """Create basic tables."""
    async with AsyncSessionLocal() as db:
        try:
            # Create companies table
            await db.execute(text("""
                CREATE TABLE IF NOT EXISTS companies (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    domain VARCHAR(255) UNIQUE,
                    type ENUM('recruiter', 'employer') NOT NULL,
                    email VARCHAR(255),
                    phone VARCHAR(50),
                    website VARCHAR(255),
                    address TEXT,
                    description TEXT,
                    is_active VARCHAR(1) DEFAULT '1',
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                )
            """))
            
            # Create users table
            await db.execute(text("""
                CREATE TABLE IF NOT EXISTS users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    company_id INT,
                    email VARCHAR(255) NOT NULL UNIQUE,
                    hashed_password VARCHAR(255),
                    first_name VARCHAR(100) NOT NULL,
                    last_name VARCHAR(100) NOT NULL,
                    phone VARCHAR(50),
                    is_active BOOLEAN DEFAULT TRUE,
                    is_admin BOOLEAN DEFAULT FALSE,
                    require_2fa BOOLEAN DEFAULT FALSE,
                    last_login DATETIME,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE
                )
            """))
            
            # Create roles table
            await db.execute(text("""
                CREATE TABLE IF NOT EXISTS roles (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(50) NOT NULL UNIQUE,
                    description TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                )
            """))
            
            # Create user_roles table
            await db.execute(text("""
                CREATE TABLE IF NOT EXISTS user_roles (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT NOT NULL,
                    role_id INT NOT NULL,
                    assigned_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    assigned_by INT,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                    FOREIGN KEY (role_id) REFERENCES roles(id) ON DELETE CASCADE,
                    UNIQUE KEY unique_user_role (user_id, role_id)
                )
            """))
            
            await db.commit()
            print("Tables created successfully")
            
        except Exception as e:
            print(f"Error creating tables: {str(e)}")
            await db.rollback()
            raise


async def insert_sample_data():
    """Insert sample data using raw SQL."""
    async with AsyncSessionLocal() as db:
        try:
            # Insert roles
            roles_data = [
                ('super_admin', 'Super Administrator'),
                ('company_admin', 'Company Administrator'),
                ('recruiter', 'Recruiter'),
                ('employer', 'Employer'),
                ('candidate', 'Job Candidate')
            ]
            
            for name, desc in roles_data:
                await db.execute(text("""
                    INSERT IGNORE INTO roles (name, description) 
                    VALUES (:name, :description)
                """), {"name": name, "description": desc})
            
            print("Roles inserted")
            
            # Insert companies
            companies_data = [
                ('TechCorp Solutions', 'techcorp.com', 'employer', 'hr@techcorp.com', 'Leading technology solutions provider'),
                ('Global Recruiters Inc', 'globalrecruiters.com', 'recruiter', 'info@globalrecruiters.com', 'Premier recruitment agency')
            ]
            
            for name, domain, type_val, email, desc in companies_data:
                await db.execute(text("""
                    INSERT IGNORE INTO companies (name, domain, type, email, description, is_active) 
                    VALUES (:name, :domain, :type, :email, :description, '1')
                """), {"name": name, "domain": domain, "type": type_val, "email": email, "description": desc})
            
            print("Companies inserted")
            
            # Get company IDs
            techcorp_result = await db.execute(text("SELECT id FROM companies WHERE domain = 'techcorp.com'"))
            techcorp_id = techcorp_result.scalar()
            
            recruiter_result = await db.execute(text("SELECT id FROM companies WHERE domain = 'globalrecruiters.com'"))
            recruiter_id = recruiter_result.scalar()
            
            # Get role IDs
            role_results = await db.execute(text("SELECT id, name FROM roles"))
            roles = {row[1]: row[0] for row in role_results.fetchall()}
            
            # Insert users
            users_data = [
                ('admin@techcorp.com', 'admin123!', 'Alice', 'Johnson', techcorp_id, roles['company_admin']),
                ('recruiter@globalrecruiters.com', 'recruiter123!', 'Sarah', 'Wilson', recruiter_id, roles['recruiter']),
                ('jane.developer@email.com', 'candidate123!', 'Jane', 'Developer', None, roles['candidate']),
                ('john.engineer@email.com', 'candidate123!', 'John', 'Engineer', None, roles['candidate'])
            ]
            
            for email, password, first_name, last_name, company_id, role_id in users_data:
                hashed_password = auth_service.get_password_hash(password)
                is_admin = role_id in [roles['super_admin'], roles['company_admin']]
                
                # Insert user
                await db.execute(text("""
                    INSERT IGNORE INTO users (email, hashed_password, first_name, last_name, company_id, is_active, is_admin) 
                    VALUES (:email, :hashed_password, :first_name, :last_name, :company_id, TRUE, :is_admin)
                """), {
                    "email": email, 
                    "hashed_password": hashed_password, 
                    "first_name": first_name, 
                    "last_name": last_name, 
                    "company_id": company_id,
                    "is_admin": is_admin
                })
                
                # Get user ID and assign role
                user_result = await db.execute(text("SELECT id FROM users WHERE email = :email"), {"email": email})
                user_id = user_result.scalar()
                
                if user_id:
                    await db.execute(text("""
                        INSERT IGNORE INTO user_roles (user_id, role_id) 
                        VALUES (:user_id, :role_id)
                    """), {"user_id": user_id, "role_id": role_id})
            
            print("Users and roles inserted")
            
            await db.commit()
            print("Sample data inserted successfully!")
            
        except Exception as e:
            print(f"Error inserting sample data: {str(e)}")
            await db.rollback()
            raise


async def show_sample_data():
    """Display the created sample data."""
    async with AsyncSessionLocal() as db:
        try:
            # Show companies
            print("\n=== COMPANIES ===")
            result = await db.execute(text("SELECT name, type, email FROM companies"))
            for row in result.fetchall():
                print(f"  {row[0]} ({row[1]}) - {row[2]}")
            
            # Show users with roles
            print("\n=== USERS ===")
            result = await db.execute(text("""
                SELECT u.email, u.first_name, u.last_name, r.name as role, c.name as company
                FROM users u
                JOIN user_roles ur ON u.id = ur.user_id
                JOIN roles r ON ur.role_id = r.id
                LEFT JOIN companies c ON u.company_id = c.id
                ORDER BY r.name, u.email
            """))
            
            for row in result.fetchall():
                company = row[4] if row[4] else "No Company"
                print(f"  {row[0]} - {row[1]} {row[2]} ({row[3]}) @ {company}")
            
        except Exception as e:
            print(f"Error showing data: {str(e)}")


async def main():
    """Main function."""
    print("Creating sample data for MiraiWorks using raw SQL...")
    print("Database: mysql://hrms:hrms@localhost:3306/miraiworks")
    
    if not await test_connection():
        print("\nPlease ensure:")
        print("1. MySQL is running: docker ps")
        print("2. Database exists: docker exec hrms_db mysql -u hrms -phrms -e 'SHOW DATABASES;'")
        print("3. Try creating database: docker exec hrms_db mysql -u root -proot_password -e 'CREATE DATABASE miraiworks;'")
        return
    
    try:
        await create_tables()
        await insert_sample_data()
        await show_sample_data()
        
        print("\n" + "="*50)
        print("✅ SAMPLE DATA CREATED SUCCESSFULLY!")
        print("="*50)
        print("\n🔑 LOGIN CREDENTIALS:")
        print("Company Admin: admin@techcorp.com / admin123!")
        print("Recruiter: recruiter@globalrecruiters.com / recruiter123!")
        print("Candidate: jane.developer@email.com / candidate123!")
        print("Candidate: john.engineer@email.com / candidate123!")
        print("\n🚀 Next steps:")
        print("1. Start backend: cd backend && uvicorn app.main:app --reload --port 8001")
        print("2. Start frontend: cd frontend-nextjs && npm run dev")
        print("3. Visit: http://localhost:3000")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())