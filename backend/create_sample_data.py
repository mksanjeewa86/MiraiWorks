#!/usr/bin/env python3
"""
Script to create sample data for the MiraiWorks HRMS system.
This script creates sample users, companies, jobs, interviews, and messages for demonstration purposes.
"""

import asyncio
import os
import sys
from datetime import datetime, timedelta

from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))

from app.database import Base
from app.models.company import Company
from app.models.interview import Interview
from app.models.job import Job
from app.models.message import Message
from app.models.resume import Resume
from app.models.user import User
from app.utils.constants import InterviewStatus, UserRole

# Database URL - use MySQL (existing service)
DATABASE_URL = "mysql+asyncmy://hrms:hrms123@localhost:3306/hrms"

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


async def create_sample_data():
    """Create all sample data"""

    # Create async engine and session
    engine = create_async_engine(DATABASE_URL, echo=True)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    try:
        # Create all tables
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        async with async_session() as session:
            print("Creating sample data...")

            # 1. Create sample companies
            companies = [
                Company(
                    name="TechCorp Japan",
                    description="Leading technology company in Japan",
                    website="https://techcorp.jp",
                    industry="Technology",
                    size_category="large",
                    location="Tokyo, Japan",
                ),
                Company(
                    name="StartupInc",
                    description="Innovative startup focused on AI solutions",
                    website="https://startup.com",
                    industry="AI/Machine Learning",
                    size_category="small",
                    location="Osaka, Japan",
                ),
                Company(
                    name="GlobalSoft Solutions",
                    description="International software development company",
                    website="https://globalsoft.com",
                    industry="Software Development",
                    size_category="medium",
                    location="Yokohama, Japan",
                ),
            ]

            for company in companies:
                session.add(company)
            await session.flush()

            # 2. Create sample users
            users = [
                # Super Admin
                User(
                    email="admin@miraiworks.com",
                    username="admin",
                    password_hash=hash_password("admin123"),
                    first_name="System",
                    last_name="Administrator",
                    role=UserRole.SUPER_ADMIN,
                    is_active=True,
                    email_verified=True,
                ),
                # Company Admins
                User(
                    email="admin@techcorp.jp",
                    username="techcorp_admin",
                    password_hash=hash_password("password123"),
                    first_name="Takeshi",
                    last_name="Yamamoto",
                    role=UserRole.COMPANY_ADMIN,
                    company_id=companies[0].id,
                    is_active=True,
                    email_verified=True,
                ),
                User(
                    email="admin@startup.com",
                    username="startup_admin",
                    password_hash=hash_password("password123"),
                    first_name="Sarah",
                    last_name="Johnson",
                    role=UserRole.COMPANY_ADMIN,
                    company_id=companies[1].id,
                    is_active=True,
                    email_verified=True,
                ),
                # Recruiters
                User(
                    email="recruiter1@techcorp.jp",
                    username="recruiter1",
                    password_hash=hash_password("password123"),
                    first_name="Hiroshi",
                    last_name="Tanaka",
                    role=UserRole.RECRUITER,
                    company_id=companies[0].id,
                    is_active=True,
                    email_verified=True,
                ),
                User(
                    email="recruiter2@startup.com",
                    username="recruiter2",
                    password_hash=hash_password("password123"),
                    first_name="Emily",
                    last_name="Chen",
                    role=UserRole.RECRUITER,
                    company_id=companies[1].id,
                    is_active=True,
                    email_verified=True,
                ),
                # Job Seekers
                User(
                    email="john.doe@email.com",
                    username="johndoe",
                    password_hash=hash_password("password123"),
                    first_name="John",
                    last_name="Doe",
                    role="candidate",
                    is_active=True,
                    email_verified=True,
                ),
                User(
                    email="jane.smith@email.com",
                    username="janesmith",
                    password_hash=hash_password("password123"),
                    first_name="Jane",
                    last_name="Smith",
                    role="candidate",
                    is_active=True,
                    email_verified=True,
                ),
                User(
                    email="mike.wilson@email.com",
                    username="mikewilson",
                    password_hash=hash_password("password123"),
                    first_name="Mike",
                    last_name="Wilson",
                    role="candidate",
                    is_active=True,
                    email_verified=True,
                ),
            ]

            for user in users:
                session.add(user)
            await session.flush()

            # 3. Create sample jobs
            jobs = [
                Job(
                    title="Senior Python Developer",
                    description="We are looking for an experienced Python developer to join our team.",
                    requirements="5+ years Python experience, Django, FastAPI, SQL",
                    company_id=companies[0].id,
                    posted_by=users[3].id,  # recruiter1
                    location="Tokyo, Japan",
                    employment_type="full_time",
                    salary_min=6000000,
                    salary_max=9000000,
                    salary_currency="JPY",
                    status="active",
                    application_deadline=datetime.utcnow() + timedelta(days=30),
                ),
                Job(
                    title="AI Engineer",
                    description="Join our AI team to develop cutting-edge machine learning solutions.",
                    requirements="ML/AI experience, Python, TensorFlow, PyTorch",
                    company_id=companies[1].id,
                    posted_by=users[4].id,  # recruiter2
                    location="Osaka, Japan",
                    employment_type="full_time",
                    salary_min=5000000,
                    salary_max=8000000,
                    salary_currency="JPY",
                    status="active",
                    application_deadline=datetime.utcnow() + timedelta(days=45),
                ),
                Job(
                    title="Frontend Developer",
                    description="Build amazing user experiences with modern web technologies.",
                    requirements="React, TypeScript, CSS, 3+ years experience",
                    company_id=companies[2].id,
                    posted_by=users[1].id,  # techcorp_admin
                    location="Yokohama, Japan",
                    employment_type="full_time",
                    salary_min=4500000,
                    salary_max=7000000,
                    salary_currency="JPY",
                    status="active",
                    application_deadline=datetime.utcnow() + timedelta(days=20),
                ),
            ]

            for job in jobs:
                session.add(job)
            await session.flush()

            # 4. Create sample resumes
            resumes = [
                Resume(
                    user_id=users[5].id,  # John Doe
                    title="Software Engineer Resume",
                    full_name="John Doe",
                    email="john.doe@email.com",
                    phone="+81-80-1234-5678",
                    location="Tokyo, Japan",
                    professional_summary="Experienced software engineer with 5+ years in web development",
                    status="published",
                    visibility="public",
                ),
                Resume(
                    user_id=users[6].id,  # Jane Smith
                    title="Data Scientist Resume",
                    full_name="Jane Smith",
                    email="jane.smith@email.com",
                    phone="+81-80-2345-6789",
                    location="Osaka, Japan",
                    professional_summary="Data scientist with expertise in machine learning and analytics",
                    status="published",
                    visibility="public",
                ),
                Resume(
                    user_id=users[7].id,  # Mike Wilson
                    title="Frontend Developer Resume",
                    full_name="Mike Wilson",
                    email="mike.wilson@email.com",
                    phone="+81-80-3456-7890",
                    location="Yokohama, Japan",
                    professional_summary="Creative frontend developer specializing in React and modern UI/UX",
                    status="published",
                    visibility="public",
                ),
            ]

            for resume in resumes:
                session.add(resume)
            await session.flush()

            # 5. Skip job applications for now (model doesn't exist)

            # 6. Create sample interviews (simplified without application_id)
            interviews = [
                Interview(
                    interviewer_id=users[4].id,  # recruiter2
                    interviewee_id=users[6].id,  # Jane Smith
                    scheduled_at=datetime.utcnow() + timedelta(days=3, hours=14),
                    duration_minutes=60,
                    interview_type="technical",
                    status=InterviewStatus.SCHEDULED,
                    meeting_link="https://meet.example.com/interview1",
                    notes="Technical interview focusing on ML algorithms",
                ),
                Interview(
                    interviewer_id=users[3].id,  # recruiter1
                    interviewee_id=users[5].id,  # John Doe
                    scheduled_at=datetime.utcnow() + timedelta(days=5, hours=10),
                    duration_minutes=45,
                    interview_type="behavioral",
                    status=InterviewStatus.SCHEDULED,
                    meeting_link="https://meet.example.com/interview2",
                    notes="Behavioral and cultural fit interview",
                ),
            ]

            for interview in interviews:
                session.add(interview)
            await session.flush()

            # 7. Create sample messages
            messages = [
                Message(
                    sender_id=users[3].id,  # recruiter1
                    recipient_id=users[5].id,  # John Doe
                    subject="Interview Invitation - Senior Python Developer",
                    content="Hello John, we would like to invite you for an interview for the Senior Python Developer position.",
                    thread_id="thread_1",
                    is_read=False,
                ),
                Message(
                    sender_id=users[5].id,  # John Doe
                    recipient_id=users[3].id,  # recruiter1
                    subject="Re: Interview Invitation - Senior Python Developer",
                    content="Thank you for the invitation. I am available for the interview.",
                    thread_id="thread_1",
                    is_read=True,
                ),
                Message(
                    sender_id=users[4].id,  # recruiter2
                    recipient_id=users[6].id,  # Jane Smith
                    subject="Technical Interview - AI Engineer Position",
                    content="Hi Jane, your technical interview is scheduled for next Tuesday. Please prepare for ML algorithm questions.",
                    thread_id="thread_2",
                    is_read=False,
                ),
            ]

            for message in messages:
                session.add(message)

            # Commit all changes
            await session.commit()
            print("Sample data created successfully!")
            print("\nTest accounts created:")
            print("Super Admin: admin@miraiworks.com / admin123")
            print("Company Admin (TechCorp): admin@techcorp.jp / password123")
            print("Company Admin (StartupInc): admin@startup.com / password123")
            print("Recruiter 1: recruiter1@techcorp.jp / password123")
            print("Recruiter 2: recruiter2@startup.com / password123")
            print("Job Seeker 1: john.doe@email.com / password123")
            print("Job Seeker 2: jane.smith@email.com / password123")
            print("Job Seeker 3: mike.wilson@email.com / password123")

    except Exception as e:
        print(f"Error creating sample data: {e}")
        raise
    finally:
        await engine.dispose()


if __name__ == "__main__":
    print("Creating sample data for MiraiWorks HRMS...")
    asyncio.run(create_sample_data())
