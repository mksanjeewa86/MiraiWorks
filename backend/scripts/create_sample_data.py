#!/usr/bin/env python3
"""Create sample data for MiraiWorks database."""
import asyncio
import sys
import os
from datetime import datetime, timedelta
from typing import List
import random

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import AsyncSessionLocal
from app.models.user import User
from app.models.company import Company
from app.models.role import Role, UserRole
from app.models.job import Job, JobApplication
from app.models.resume import Resume, WorkExperience, Education, Skill, Language, Certification, Project
from app.models.interview import Interview
from app.models.message import Conversation, Message
from app.models.notification import Notification
from app.services.auth_service import auth_service
from app.utils.constants import (
    UserRole as UserRoleEnum, 
    CompanyType, 
    InterviewStatus,
    ResumeStatus,
    ResumeVisibility,
    MessageType
)


# Sample data constants
SAMPLE_COMPANIES = [
    {
        "name": "TechCorp Solutions",
        "domain": "techcorp.com",
        "type": CompanyType.EMPLOYER,
        "email": "hr@techcorp.com",
        "phone": "+1-555-0101",
        "website": "https://techcorp.com",
        "address": "123 Tech Street, Silicon Valley, CA 94000",
        "description": "Leading technology solutions provider specializing in cloud infrastructure and AI."
    },
    {
        "name": "Global Recruiters Inc",
        "domain": "globalrecruiters.com",
        "type": CompanyType.RECRUITER,
        "email": "info@globalrecruiters.com",
        "phone": "+1-555-0202",
        "website": "https://globalrecruiters.com",
        "address": "456 Business Ave, New York, NY 10001",
        "description": "Premier recruitment agency connecting top talent with leading companies worldwide."
    },
    {
        "name": "StartupX",
        "domain": "startupx.io",
        "type": CompanyType.EMPLOYER,
        "email": "team@startupx.io",
        "phone": "+1-555-0303",
        "website": "https://startupx.io",
        "address": "789 Innovation Blvd, Austin, TX 73301",
        "description": "Fast-growing fintech startup revolutionizing digital payments."
    },
    {
        "name": "Elite Talent Partners",
        "domain": "elitetalent.com",
        "type": CompanyType.RECRUITER,
        "email": "contact@elitetalent.com",
        "phone": "+1-555-0404",
        "website": "https://elitetalent.com",
        "address": "321 Executive Plaza, Chicago, IL 60601",
        "description": "Executive search firm specializing in C-level and senior technical positions."
    }
]

SAMPLE_USERS = [
    # Company Admins
    {
        "email": "admin@techcorp.com",
        "password": "admin123!",
        "first_name": "Alice",
        "last_name": "Johnson",
        "phone": "+1-555-1001",
        "role": UserRoleEnum.COMPANY_ADMIN,
        "company": "TechCorp Solutions"
    },
    {
        "email": "admin@globalrecruiters.com",
        "password": "admin123!",
        "first_name": "Bob",
        "last_name": "Smith",
        "phone": "+1-555-1002",
        "role": UserRoleEnum.COMPANY_ADMIN,
        "company": "Global Recruiters Inc"
    },
    # Recruiters
    {
        "email": "sarah.recruiter@globalrecruiters.com",
        "password": "recruiter123!",
        "first_name": "Sarah",
        "last_name": "Wilson",
        "phone": "+1-555-2001",
        "role": UserRoleEnum.RECRUITER,
        "company": "Global Recruiters Inc"
    },
    {
        "email": "mike.recruiter@elitetalent.com",
        "password": "recruiter123!",
        "first_name": "Mike",
        "last_name": "Davis",
        "phone": "+1-555-2002",
        "role": UserRoleEnum.RECRUITER,
        "company": "Elite Talent Partners"
    },
    # Employers
    {
        "email": "john.manager@techcorp.com",
        "password": "employer123!",
        "first_name": "John",
        "last_name": "Manager",
        "phone": "+1-555-3001",
        "role": UserRoleEnum.EMPLOYER,
        "company": "TechCorp Solutions"
    },
    {
        "email": "lisa.lead@startupx.io",
        "password": "employer123!",
        "first_name": "Lisa",
        "last_name": "Chen",
        "phone": "+1-555-3002",
        "role": UserRoleEnum.EMPLOYER,
        "company": "StartupX"
    },
    # Candidates
    {
        "email": "jane.developer@email.com",
        "password": "candidate123!",
        "first_name": "Jane",
        "last_name": "Developer",
        "phone": "+1-555-4001",
        "role": UserRoleEnum.CANDIDATE,
        "company": None
    },
    {
        "email": "alex.engineer@email.com",
        "password": "candidate123!",
        "first_name": "Alex",
        "last_name": "Rodriguez",
        "phone": "+1-555-4002",
        "role": UserRoleEnum.CANDIDATE,
        "company": None
    },
    {
        "email": "emily.designer@email.com",
        "password": "candidate123!",
        "first_name": "Emily",
        "last_name": "Thompson",
        "phone": "+1-555-4003",
        "role": UserRoleEnum.CANDIDATE,
        "company": None
    },
    {
        "email": "david.analyst@email.com",
        "password": "candidate123!",
        "first_name": "David",
        "last_name": "Kumar",
        "phone": "+1-555-4004",
        "role": UserRoleEnum.CANDIDATE,
        "company": None
    }
]

SAMPLE_JOBS = [
    {
        "title": "Senior Full Stack Developer",
        "slug": "senior-full-stack-developer-techcorp",
        "description": "We are seeking a talented Senior Full Stack Developer to join our growing team...",
        "requirements": "5+ years of experience with React, Node.js, Python, and cloud platforms.",
        "location": "San Francisco, CA",
        "salary_min": 12000000,  # In cents
        "salary_max": 18000000,  # In cents
        "company": "TechCorp Solutions"
    },
    {
        "title": "DevOps Engineer",
        "slug": "devops-engineer-startupx",
        "description": "Join our infrastructure team to build and maintain scalable cloud solutions...",
        "requirements": "Experience with AWS/Azure, Kubernetes, Docker, and CI/CD pipelines.",
        "location": "Austin, TX",
        "salary_min": 10000000,  # In cents
        "salary_max": 14000000,  # In cents
        "company": "StartupX"
    },
    {
        "title": "UX/UI Designer",
        "slug": "ux-ui-designer-techcorp",
        "description": "Looking for a creative UX/UI Designer to enhance our user experience...",
        "requirements": "3+ years of experience with Figma, Adobe Creative Suite, user research.",
        "location": "Remote",
        "salary_min": 8000000,  # In cents
        "salary_max": 12000000,  # In cents
        "company": "TechCorp Solutions"
    },
    {
        "title": "Data Scientist",
        "slug": "data-scientist-techcorp",
        "description": "Join our data team to build machine learning models and analytics solutions...",
        "requirements": "PhD in Statistics/CS or equivalent, Python, SQL, ML frameworks.",
        "location": "New York, NY",
        "salary_min": 13000000,  # In cents
        "salary_max": 20000000,  # In cents
        "company": "TechCorp Solutions"
    }
]


async def create_companies(db: AsyncSession) -> dict:
    """Create sample companies."""
    print("Creating sample companies...")
    
    companies = {}
    for company_data in SAMPLE_COMPANIES:
        company = Company(
            name=company_data["name"],
            domain=company_data["domain"],
            type=company_data["type"],
            email=company_data["email"],
            phone=company_data["phone"],
            website=company_data["website"],
            address=company_data["address"],
            description=company_data["description"],
            is_active="1"
        )
        db.add(company)
        companies[company_data["name"]] = company
        print(f"  Created company: {company_data['name']}")
    
    await db.commit()
    
    # Refresh to get IDs
    for company in companies.values():
        await db.refresh(company)
    
    return companies


async def create_users(db: AsyncSession, companies: dict) -> dict:
    """Create sample users."""
    print("Creating sample users...")
    
    # Get roles
    roles_result = await db.execute(select(Role))
    roles = {role.name: role for role in roles_result.scalars().all()}
    
    users = {}
    for user_data in SAMPLE_USERS:
        # Create user
        hashed_password = auth_service.get_password_hash(user_data["password"])
        company = companies.get(user_data["company"]) if user_data["company"] else None
        
        user = User(
            email=user_data["email"],
            hashed_password=hashed_password,
            first_name=user_data["first_name"],
            last_name=user_data["last_name"],
            phone=user_data["phone"],
            company_id=company.id if company else None,
            is_active=True,
            is_admin=user_data["role"] in [UserRoleEnum.SUPER_ADMIN, UserRoleEnum.COMPANY_ADMIN]
        )
        
        db.add(user)
        await db.commit()
        await db.refresh(user)
        
        # Assign role
        user_role = UserRole(
            user_id=user.id,
            role_id=roles[user_data["role"].value].id
        )
        db.add(user_role)
        
        users[user_data["email"]] = user
        print(f"  Created user: {user_data['email']} ({user_data['role']})")
    
    await db.commit()
    return users


async def create_jobs(db: AsyncSession, companies: dict, users: dict) -> List[Job]:
    """Create sample jobs."""
    print("Creating sample jobs...")
    
    jobs = []
    for job_data in SAMPLE_JOBS:
        company = companies[job_data["company"]]
        
        job = Job(
            title=job_data["title"],
            slug=job_data["slug"],
            description=job_data["description"],
            requirements=job_data["requirements"],
            location=job_data["location"],
            salary_min=job_data["salary_min"],
            salary_max=job_data["salary_max"],
            company_id=company.id,
            status="published"
        )
        
        db.add(job)
        jobs.append(job)
        print(f"  Created job: {job_data['title']} at {job_data['company']}")
    
    await db.commit()
    
    # Refresh to get IDs
    for job in jobs:
        await db.refresh(job)
    
    return jobs


async def create_resumes_and_applications(db: AsyncSession, jobs: List[Job], users: dict) -> None:
    """Create sample resumes and job applications."""
    print("Creating sample resumes and applications...")
    
    # Get candidate users
    candidates = [user for user in users.values() if any(
        ur.role.name == UserRoleEnum.CANDIDATE.value 
        for ur in user.user_roles
    )]
    
    for candidate in candidates:
        # Create resume
        resume = Resume(
            user_id=candidate.id,
            title=f"{candidate.first_name} {candidate.last_name} - Software Engineer",
            description=f"Experienced software engineer passionate about building scalable solutions.",
            template_id="modern",
            theme_color="#3b82f6",
            font_family="Inter",
            status=ResumeStatus.PUBLISHED,
            visibility=ResumeVisibility.PUBLIC,
            slug=f"{candidate.first_name.lower()}-{candidate.last_name.lower()}-resume",
            share_token=f"share_{candidate.id}_{random.randint(1000, 9999)}",
            view_count=random.randint(5, 50),
            download_count=random.randint(1, 10)
        )
        
        db.add(resume)
        await db.commit()
        await db.refresh(resume)
        
        # Add work experience
        experiences = [
            {
                "company_name": "Previous Tech Co",
                "position_title": "Software Engineer",
                "location": "San Francisco, CA",
                "start_date": "2022-01-01",
                "end_date": "2024-01-01",
                "is_current": False,
                "description": "Developed and maintained web applications using React and Node.js."
            },
            {
                "company_name": "Startup Inc",
                "position_title": "Junior Developer",
                "location": "Remote",
                "start_date": "2020-06-01",
                "end_date": "2021-12-01",
                "is_current": False,
                "description": "Built mobile applications and REST APIs."
            }
        ]
        
        for exp_data in experiences:
            experience = WorkExperience(
                resume_id=resume.id,
                company_name=exp_data["company_name"],
                position_title=exp_data["position_title"],
                location=exp_data["location"],
                start_date=exp_data["start_date"],
                end_date=exp_data["end_date"],
                is_current=exp_data["is_current"],
                description=exp_data["description"]
            )
            db.add(experience)
        
        # Add education
        education = Education(
            resume_id=resume.id,
            institution_name="University of Technology",
            degree_type="Bachelor of Science",
            field_of_study="Computer Science",
            location="California, USA",
            start_date="2016-09-01",
            end_date="2020-05-01",
            gpa="3.8"
        )
        db.add(education)
        
        # Add skills
        skills_data = ["Python", "JavaScript", "React", "Node.js", "SQL", "AWS"]
        for skill_name in skills_data:
            skill = Skill(
                resume_id=resume.id,
                name=skill_name,
                proficiency_level="Advanced",
                years_of_experience=random.randint(2, 5)
            )
            db.add(skill)
        
        # Add languages
        languages_data = [("English", "Native"), ("Spanish", "Intermediate")]
        for lang_name, proficiency in languages_data:
            language = Language(
                resume_id=resume.id,
                name=lang_name,
                proficiency_level=proficiency
            )
            db.add(language)
        
        # Apply to some jobs
        applied_jobs = random.sample(jobs, min(len(jobs), 2))
        for job in applied_jobs:
            application = JobApplication(
                job_id=job.id,
                applicant_id=candidate.id,
                cover_letter=f"I am very interested in the {job.title} position...",
                status="submitted"
            )
            db.add(application)
        
        print(f"  Created resume and applications for: {candidate.full_name}")
    
    await db.commit()


async def create_notifications(db: AsyncSession, users: dict) -> None:
    """Create sample notifications."""
    print("Creating sample notifications...")
    
    notification_templates = [
        ("job_application", "New application received", "You have received a new job application."),
        ("interview_scheduled", "Interview scheduled", "An interview has been scheduled for tomorrow."),
        ("message_received", "New message", "You have received a new message from a candidate."),
        ("resume_viewed", "Resume viewed", "Your resume has been viewed by an employer."),
    ]
    
    for user in users.values():
        for i, (notif_type, title, message) in enumerate(notification_templates):
            if random.random() > 0.7:  # 30% chance for each notification
                notification = Notification(
                    user_id=user.id,
                    type=notif_type,
                    title=title,
                    message=message,
                    is_read=random.choice([True, False]),
                    created_at=datetime.utcnow() - timedelta(days=random.randint(0, 7))
                )
                db.add(notification)
        
        print(f"  Created notifications for: {user.full_name}")
    
    await db.commit()


async def main():
    """Main function to create all sample data."""
    print("Creating sample data for MiraiWorks database...")
    
    try:
        async with AsyncSessionLocal() as db:
            # Check if data already exists
            result = await db.execute(select(Company).limit(1))
            if result.scalar_one_or_none():
                print("❌ Sample data already exists. Please clear the database first.")
                return
            
            # Create sample data
            companies = await create_companies(db)
            users = await create_users(db, companies)
            jobs = await create_jobs(db, companies, users)
            await create_resumes_and_applications(db, jobs, users)
            await create_notifications(db, users)
        
        print("\n✅ Sample data creation completed successfully!")
        print("\n📊 Created:")
        print(f"   • {len(SAMPLE_COMPANIES)} companies")
        print(f"   • {len(SAMPLE_USERS)} users (various roles)")
        print(f"   • {len(SAMPLE_JOBS)} job postings")
        print("   • Resumes with work experience, education, and skills")
        print("   • Job applications and notifications")
        
        print("\n🔑 Sample Login Credentials:")
        print("   Super Admin: admin@miraiworks.com / admin123!@#")
        print("   Company Admin: admin@techcorp.com / admin123!")
        print("   Recruiter: sarah.recruiter@globalrecruiters.com / recruiter123!")
        print("   Employer: john.manager@techcorp.com / employer123!")
        print("   Candidate: jane.developer@email.com / candidate123!")
        
    except Exception as e:
        print(f"❌ Sample data creation failed: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())