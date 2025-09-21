"""
Default seed data for MiraiWorks database initialization.

This file contains:
- 1 super admin user
- 5 company users (1 for super admin's company, 4 for other companies)
- 6 companies (1 for super admin, 5 others)
- User settings for all users
- Company profiles for all companies
- User roles and roles for all users
- 7 direct messages between users for testing messaging functionality
- 3 interviews with different statuses and scheduling details

HOW TO RUN:
    1. Navigate to the backend directory:
       cd backend

    2. Run the script:
       PYTHONPATH=. python app/seed_data.py

    3. Alternative method:
       python -m app.seed_data

REQUIREMENTS:
    - Database must exist and be accessible
    - Database tables must be created (run: alembic upgrade head)
    - Environment variables must be set (.env file)

WARNING: This script will DELETE all existing seed data and create fresh data!
         It completely refreshes the database with clean seed data every time.
         All passwords are set to: "password"
"""

import asyncio
import os
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession

# Set environment to avoid conflicts
os.environ.setdefault("ENVIRONMENT", "development")

# Import through FastAPI app to ensure proper model loading
from app.main import app
from app.database import AsyncSessionLocal
from app.models import User, Company, Role, UserRole, UserSettings, CompanyProfile
from app.models.message import Message
from app.models.interview import Interview
from app.services.auth_service import auth_service
from app.utils.constants import CompanyType, MessageType, InterviewStatus


async def create_seed_data():
    """Create all seed data fresh (removes existing seed data first)."""
    print("Starting FRESH seed data creation...")
    print("=" * 60)
    print("WARNING: This will DELETE all existing seed data and create new data!")
    print("=" * 60)

    async with AsyncSessionLocal() as db:
        try:
            from sqlalchemy import select, delete

            # Clear existing seed data in correct order (reverse of creation)
            print("\nClearing existing seed data...")

            # Clear messages
            await db.execute(delete(Message))
            print("   - Cleared messages")

            # Clear interviews
            await db.execute(delete(Interview))
            print("   - Cleared interviews")

            # Clear company profiles
            await db.execute(delete(CompanyProfile))
            print("   - Cleared company profiles")

            # Clear user settings
            await db.execute(delete(UserSettings))
            print("   - Cleared user settings")

            # Clear user roles
            await db.execute(delete(UserRole))
            print("   - Cleared user roles")

            # Clear users
            await db.execute(delete(User))
            print("   - Cleared users")

            # Clear companies
            await db.execute(delete(Company))
            print("   - Cleared companies")

            # Clear roles
            await db.execute(delete(Role))
            print("   - Cleared roles")

            await db.commit()
            print("   > All existing seed data cleared!")

            # Create roles first
            print("\nCreating fresh roles...")
            roles_data = [
                {"name": "super_admin", "description": "Super administrator with full system access"},
                {"name": "company_admin", "description": "Company administrator with full company access"},
                {"name": "recruiter", "description": "Recruiter with candidate and position management access"},
                {"name": "employer", "description": "Employer with position management access"},
                {"name": "candidate", "description": "Candidate with profile and application access"},
            ]

            roles = {}
            for role_data in roles_data:
                role = Role(**role_data)
                db.add(role)
                await db.flush()
                roles[role_data["name"]] = role
                print(f"   - Created role '{role_data['name']}'")

            await db.commit()

            # Create companies
            print("\nCreating companies...")
            companies_data = [
                {
                    "name": "MiraiWorks System",
                    "type": CompanyType.EMPLOYER,
                    "email": "admin@miraiworks.com",
                    "phone": "+1-555-0100",
                    "website": "https://miraiworks.com",
                    "postal_code": "10001",
                    "prefecture": "NY",
                    "city": "New York",
                    "description": "MiraiWorks platform system company",
                    "is_active": "1",
                },
                {
                    "name": "TechCorp Solutions",
                    "type": CompanyType.EMPLOYER,
                    "email": "hr@techcorp.com",
                    "phone": "+1-555-0101",
                    "website": "https://techcorp.com",
                    "postal_code": "94105",
                    "prefecture": "CA",
                    "city": "San Francisco",
                    "description": "Leading technology solutions provider",
                    "is_active": "1",
                },
                {
                    "name": "InnovateLab Inc",
                    "type": CompanyType.RECRUITER,
                    "email": "contact@innovatelab.com",
                    "phone": "+1-555-0102",
                    "website": "https://innovatelab.com",
                    "postal_code": "02101",
                    "prefecture": "MA",
                    "city": "Boston",
                    "description": "Innovation-focused recruitment agency",
                    "is_active": "1",
                },
                {
                    "name": "DataDriven Analytics",
                    "type": CompanyType.EMPLOYER,
                    "email": "jobs@datadriven.com",
                    "phone": "+1-555-0103",
                    "website": "https://datadriven.com",
                    "postal_code": "98101",
                    "prefecture": "WA",
                    "city": "Seattle",
                    "description": "Data analytics and business intelligence company",
                    "is_active": "1",
                },
                {
                    "name": "CloudScale Systems",
                    "type": CompanyType.EMPLOYER,
                    "email": "careers@cloudscale.com",
                    "phone": "+1-555-0104",
                    "website": "https://cloudscale.com",
                    "postal_code": "78701",
                    "prefecture": "TX",
                    "city": "Austin",
                    "description": "Cloud infrastructure and scaling solutions",
                    "is_active": "1",
                },
                {
                    "name": "NextGen Recruiting",
                    "type": CompanyType.RECRUITER,
                    "email": "info@nextgenrecruiting.com",
                    "phone": "+1-555-0105",
                    "website": "https://nextgenrecruiting.com",
                    "postal_code": "60601",
                    "prefecture": "IL",
                    "city": "Chicago",
                    "description": "Next generation recruitment services",
                    "is_active": "1",
                },
            ]

            companies = []
            for company_data in companies_data:
                company = Company(**company_data)
                db.add(company)
                await db.flush()
                companies.append(company)
                print(f"   - Created company '{company_data['name']}'")

            await db.commit()

            # Create users
            print("\nCreating users...")
            users_data = [
                {
                    "company_id": companies[0].id,  # MiraiWorks System
                    "email": "superadmin@miraiworks.com",
                    "hashed_password": auth_service.get_password_hash("password"),
                    "first_name": "Super",
                    "last_name": "Administrator",
                    "phone": "+1-555-0200",
                    "is_active": True,
                    "is_admin": True,
                    "role": "super_admin",
                },
                {
                    "company_id": companies[1].id,  # TechCorp Solutions
                    "email": "admin@techcorp.com",
                    "hashed_password": auth_service.get_password_hash("password"),
                    "first_name": "John",
                    "last_name": "Smith",
                    "phone": "+1-555-0201",
                    "is_active": True,
                    "is_admin": False,
                    "role": "company_admin",
                },
                {
                    "company_id": companies[2].id,  # InnovateLab Inc
                    "email": "recruiter@innovatelab.com",
                    "hashed_password": auth_service.get_password_hash("password"),
                    "first_name": "Sarah",
                    "last_name": "Johnson",
                    "phone": "+1-555-0202",
                    "is_active": True,
                    "is_admin": False,
                    "role": "recruiter",
                },
                {
                    "company_id": companies[3].id,  # DataDriven Analytics
                    "email": "hr@datadriven.com",
                    "hashed_password": auth_service.get_password_hash("password"),
                    "first_name": "Michael",
                    "last_name": "Chen",
                    "phone": "+1-555-0203",
                    "is_active": True,
                    "is_admin": False,
                    "role": "employer",
                },
                {
                    "company_id": companies[4].id,  # CloudScale Systems
                    "email": "manager@cloudscale.com",
                    "hashed_password": auth_service.get_password_hash("password"),
                    "first_name": "Emily",
                    "last_name": "Davis",
                    "phone": "+1-555-0204",
                    "is_active": True,
                    "is_admin": False,
                    "role": "company_admin",
                },
                {
                    "company_id": companies[5].id,  # NextGen Recruiting
                    "email": "lead@nextgenrecruiting.com",
                    "hashed_password": auth_service.get_password_hash("password"),
                    "first_name": "David",
                    "last_name": "Wilson",
                    "phone": "+1-555-0205",
                    "is_active": True,
                    "is_admin": False,
                    "role": "recruiter",
                },
            ]

            users = []
            for user_data in users_data:
                user_role = user_data.pop("role")
                user = User(**user_data)
                db.add(user)
                await db.flush()
                users.append((user, user_role))
                print(f"   - Created user '{user_data['email']}'")

            await db.commit()

            # Create user roles
            for user, role_name in users:
                user_role = UserRole(
                    user_id=user.id,
                    role_id=roles[role_name].id,
                    scope=f"company_{user.company_id}" if role_name != "super_admin" else "global"
                )
                db.add(user_role)

            # Create user settings for all users
            user_settings_data = [
                {
                    "job_title": "System Administrator",
                    "bio": "Super administrator managing the MiraiWorks platform",
                    "language": "en",
                    "timezone": "America/New_York",
                },
                {
                    "job_title": "HR Director",
                    "bio": "Leading talent acquisition and human resources at TechCorp",
                    "language": "en",
                    "timezone": "America/Los_Angeles",
                },
                {
                    "job_title": "Senior Recruiter",
                    "bio": "Specialized in tech recruitment and talent sourcing",
                    "language": "en",
                    "timezone": "America/New_York",
                },
                {
                    "job_title": "Talent Acquisition Manager",
                    "bio": "Data-driven approach to finding the best talent",
                    "language": "en",
                    "timezone": "America/Los_Angeles",
                },
                {
                    "job_title": "People Operations Manager",
                    "bio": "Building great teams for cloud-scale solutions",
                    "language": "en",
                    "timezone": "America/Chicago",
                },
                {
                    "job_title": "Lead Recruitment Consultant",
                    "bio": "Next-generation recruitment strategies and solutions",
                    "language": "en",
                    "timezone": "America/Chicago",
                },
            ]

            for i, (user, _) in enumerate(users):
                settings_data = user_settings_data[i].copy()
                settings_data["user_id"] = user.id
                settings = UserSettings(**settings_data)
                db.add(settings)

            # Create company profiles for all companies
            company_profiles_data = [
                {
                    "tagline": "Powering the future of recruitment",
                    "mission": "To revolutionize how companies and candidates connect through innovative technology",
                    "values": '["Innovation", "Transparency", "Excellence", "Collaboration"]',
                    "culture": "A dynamic, technology-driven environment focused on continuous improvement and user satisfaction",
                    "employee_count": "11-50",
                    "headquarters": "New York, NY",
                    "founded_year": 2024,
                    "benefits_summary": "Comprehensive health benefits, flexible working, professional development",
                    "perks_highlights": '["Remote work options", "Professional development budget", "Health & wellness programs"]',
                },
                {
                    "tagline": "Technology solutions that matter",
                    "mission": "Delivering cutting-edge technology solutions that drive business success",
                    "values": '["Innovation", "Quality", "Customer Success", "Integrity"]',
                    "culture": "Fast-paced, innovative environment where creativity and technical excellence thrive",
                    "employee_count": "201-500",
                    "headquarters": "San Francisco, CA",
                    "founded_year": 2018,
                    "benefits_summary": "Full health coverage, equity participation, unlimited PTO",
                    "perks_highlights": '["Stock options", "Unlimited vacation", "Top-tier equipment", "Learning stipend"]',
                },
                {
                    "tagline": "Innovation meets talent",
                    "mission": "Connecting innovative companies with exceptional talent through strategic recruitment",
                    "values": '["Excellence", "Partnership", "Innovation", "Trust"]',
                    "culture": "Collaborative and results-driven, focused on building lasting partnerships",
                    "employee_count": "51-100",
                    "headquarters": "Boston, MA",
                    "founded_year": 2020,
                    "benefits_summary": "Competitive compensation, health benefits, flexible schedules",
                    "perks_highlights": '["Flexible hours", "Professional networking", "Performance bonuses"]',
                },
                {
                    "tagline": "Data-driven decisions, human-centered results",
                    "mission": "Transforming data into actionable insights for business growth",
                    "values": '["Data Integrity", "Innovation", "Collaboration", "Impact"]',
                    "culture": "Analytical and collaborative environment where data meets creativity",
                    "employee_count": "101-200",
                    "headquarters": "Seattle, WA",
                    "founded_year": 2019,
                    "benefits_summary": "Comprehensive benefits, professional development, work-life balance",
                    "perks_highlights": '["Data science training", "Conference attendance", "Wellness programs"]',
                },
                {
                    "tagline": "Scaling possibilities in the cloud",
                    "mission": "Empowering businesses to scale seamlessly with cloud infrastructure solutions",
                    "values": '["Scalability", "Reliability", "Innovation", "Excellence"]',
                    "culture": "High-performance culture focused on reliability and continuous improvement",
                    "employee_count": "51-100",
                    "headquarters": "Austin, TX",
                    "founded_year": 2021,
                    "benefits_summary": "Full benefits package, equity options, professional growth",
                    "perks_highlights": '["Cloud certifications", "Tech conferences", "Team building events"]',
                },
                {
                    "tagline": "The future of recruitment is here",
                    "mission": "Revolutionizing recruitment through technology and personalized service",
                    "values": '["Innovation", "Personalization", "Results", "Partnership"]',
                    "culture": "Forward-thinking and client-focused, embracing new technologies and methodologies",
                    "employee_count": "11-50",
                    "headquarters": "Chicago, IL",
                    "founded_year": 2022,
                    "benefits_summary": "Competitive package, professional development, flexible work",
                    "perks_highlights": '["Remote flexibility", "Industry training", "Performance incentives"]',
                },
            ]

            for i, company in enumerate(companies):
                profile_data = company_profiles_data[i].copy()
                profile_data["company_id"] = company.id
                profile_data["last_updated_by"] = users[0][0].id if i == 0 else users[min(i, len(users)-1)][0].id
                profile = CompanyProfile(**profile_data)
                db.add(profile)

            # Create direct messages between users
            print("\nCreating direct messages...")
            messages_data = [
                # TechCorp and InnovateLab recruitment discussion
                {
                    "sender_id": users[1][0].id,  # admin@techcorp.com
                    "recipient_id": users[2][0].id,  # recruiter@innovatelab.com
                    "type": MessageType.TEXT.value,
                    "content": "Hello! We're looking for talented developers for our new project. Can you help us find some candidates?",
                },
                {
                    "sender_id": users[2][0].id,  # recruiter@innovatelab.com
                    "recipient_id": users[1][0].id,  # admin@techcorp.com
                    "type": MessageType.TEXT.value,
                    "content": "Absolutely! I'd be happy to help. What specific skills are you looking for?",
                },
                {
                    "sender_id": users[1][0].id,  # admin@techcorp.com
                    "recipient_id": users[2][0].id,  # recruiter@innovatelab.com
                    "type": MessageType.TEXT.value,
                    "content": "We need full-stack developers with React and Node.js experience. 3+ years preferred.",
                },

                # DataDriven and NextGen partnership
                {
                    "sender_id": users[3][0].id,  # hr@datadriven.com
                    "recipient_id": users[5][0].id,  # lead@nextgenrecruiting.com
                    "type": MessageType.TEXT.value,
                    "content": "Hi! I saw your recruitment services and I'm interested in partnering with you.",
                },
                {
                    "sender_id": users[5][0].id,  # lead@nextgenrecruiting.com
                    "recipient_id": users[3][0].id,  # hr@datadriven.com
                    "type": MessageType.TEXT.value,
                    "content": "Great to hear from you! We specialize in data science and analytics roles. What positions are you looking to fill?",
                },

                # CloudScale team coordination
                {
                    "sender_id": users[4][0].id,  # manager@cloudscale.com
                    "recipient_id": users[2][0].id,  # recruiter@innovatelab.com
                    "type": MessageType.TEXT.value,
                    "content": "Welcome to our collaboration! Let's coordinate our hiring efforts.",
                },
                {
                    "sender_id": users[0][0].id,  # superadmin@miraiworks.com
                    "recipient_id": users[4][0].id,  # manager@cloudscale.com
                    "type": MessageType.TEXT.value,
                    "content": "Welcome to MiraiWorks! Let me know if you need any platform assistance.",
                },
            ]

            for msg_data in messages_data:
                message = Message(**msg_data)
                db.add(message)

            print(f"   - Created {len(messages_data)} direct messages")

            # Create interviews
            print("\nCreating interviews...")

            from datetime import datetime, timedelta
            base_time = datetime.now()

            interviews_data = [
                {
                    "candidate_id": users[1][0].id,  # Will use company user as mock candidate
                    "recruiter_id": users[2][0].id,  # recruiter@innovatelab.com
                    "employer_company_id": companies[1].id,  # TechCorp Solutions
                    "recruiter_company_id": companies[2].id,  # InnovateLab Inc
                    "title": "Senior Full-Stack Developer Interview",
                    "description": "Technical interview for senior full-stack developer position focusing on React and Node.js",
                    "position_title": "Senior Full-Stack Developer",
                    "status": InterviewStatus.SCHEDULED.value,
                    "interview_type": "video",
                    "scheduled_start": base_time + timedelta(days=3, hours=10),
                    "scheduled_end": base_time + timedelta(days=3, hours=11),
                    "timezone": "America/New_York",
                    "meeting_url": "https://meet.techcorp.com/interview-001",
                    "meeting_id": "tcorp-001",
                },
                {
                    "candidate_id": users[3][0].id,  # Will use company user as mock candidate
                    "recruiter_id": users[5][0].id,  # lead@nextgenrecruiting.com
                    "employer_company_id": companies[3].id,  # DataDriven Analytics
                    "recruiter_company_id": companies[5].id,  # NextGen Recruiting
                    "title": "Data Scientist Position Interview",
                    "description": "Interview for data scientist role with focus on machine learning and analytics",
                    "position_title": "Senior Data Scientist",
                    "status": InterviewStatus.CONFIRMED.value,
                    "interview_type": "video",
                    "scheduled_start": base_time + timedelta(days=5, hours=14),
                    "scheduled_end": base_time + timedelta(days=5, hours=15, minutes=30),
                    "timezone": "America/Los_Angeles",
                    "meeting_url": "https://zoom.us/j/datadriven123",
                    "meeting_id": "zoom-dd-123",
                },
                {
                    "candidate_id": users[4][0].id,  # Will use company user as mock candidate
                    "recruiter_id": users[2][0].id,  # recruiter@innovatelab.com
                    "employer_company_id": companies[4].id,  # CloudScale Systems
                    "recruiter_company_id": companies[2].id,  # InnovateLab Inc
                    "title": "DevOps Engineer Interview",
                    "description": "Technical interview for DevOps engineer position with focus on cloud infrastructure",
                    "position_title": "Senior DevOps Engineer",
                    "status": InterviewStatus.PENDING_SCHEDULE.value,
                    "interview_type": "video",
                    "timezone": "America/Chicago",
                },
            ]

            for interview_data in interviews_data:
                interview = Interview(**interview_data)
                db.add(interview)
                print(f"   - Created interview '{interview_data['title']}'")

            # Commit all changes
            await db.commit()

            print("SUCCESS: Fresh seed data created successfully!")
            print("=" * 50)
            print("FRESH DATA SUMMARY:")
            print(f"   - {len(roles_data)} roles")
            print(f"   - {len(companies)} companies")
            print(f"   - {len(users)} users")
            print(f"   - {len(users)} user roles")
            print(f"   - {len(users)} user settings")
            print(f"   - {len(companies)} company profiles")
            print(f"   - {len(messages_data)} messages")
            print(f"   - {len(interviews_data)} interviews")

            print("\nLOGIN CREDENTIALS (All passwords: 'password'):")
            print("=" * 50)
            print("Super Admin:")
            print("   Email: superadmin@miraiworks.com")
            print("   Password: password")

            print("\nCompany Users:")
            for user, role_name in users[1:]:
                company_name = next(c.name for c in companies if c.id == user.company_id)
                print(f"   - {user.email} (password) - {role_name} at {company_name}")

            print("\n> Database has been refreshed with clean seed data!")

        except Exception as e:
            await db.rollback()
            print(f"ERROR: Error creating seed data: {e}")
            print("\nTroubleshooting:")
            print("1. Ensure database tables exist (run migrations)")
            print("2. Check database connection settings")
            print("3. Verify all required dependencies are installed")
            raise


async def main():
    """Main function to run seed data creation."""
    await create_seed_data()


if __name__ == "__main__":
    asyncio.run(main())

