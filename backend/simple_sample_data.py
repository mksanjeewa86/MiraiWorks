#!/usr/bin/env python3
"""
Simplified script to create sample data using only basic models.
This avoids complex SQLAlchemy model relationships and type issues.
"""

import json
from datetime import datetime, timedelta

from passlib.context import CryptContext

# Simple in-memory data structure to demonstrate the system
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def create_sample_json_data():
    """Create sample data as JSON for frontend demonstration"""

    # Sample users
    users = [
        {
            "id": 1,
            "email": "admin@miraiworks.com",
            "username": "admin",
            "first_name": "System",
            "last_name": "Administrator",
            "role": "super_admin",
            "is_active": True,
            "email_verified": True,
        },
        {
            "id": 2,
            "email": "admin@techcorp.jp",
            "username": "techcorp_admin",
            "first_name": "Takeshi",
            "last_name": "Yamamoto",
            "role": "company_admin",
            "company_id": 1,
            "is_active": True,
            "email_verified": True,
        },
        {
            "id": 3,
            "email": "recruiter1@techcorp.jp",
            "username": "recruiter1",
            "first_name": "Hiroshi",
            "last_name": "Tanaka",
            "role": "recruiter",
            "company_id": 1,
            "is_active": True,
            "email_verified": True,
        },
        {
            "id": 4,
            "email": "john.doe@email.com",
            "username": "johndoe",
            "first_name": "John",
            "last_name": "Doe",
            "role": "candidate",
            "is_active": True,
            "email_verified": True,
        },
        {
            "id": 5,
            "email": "jane.smith@email.com",
            "username": "janesmith",
            "first_name": "Jane",
            "last_name": "Smith",
            "role": "candidate",
            "is_active": True,
            "email_verified": True,
        },
    ]

    # Sample companies
    companies = [
        {
            "id": 1,
            "name": "TechCorp Japan",
            "description": "Leading technology company in Japan",
            "website": "https://techcorp.jp",
            "industry": "Technology",
            "size_category": "large",
            "location": "Tokyo, Japan",
        },
        {
            "id": 2,
            "name": "StartupInc",
            "description": "Innovative startup focused on AI solutions",
            "website": "https://startup.com",
            "industry": "AI/Machine Learning",
            "size_category": "small",
            "location": "Osaka, Japan",
        },
    ]

    # Sample jobs
    jobs = [
        {
            "id": 1,
            "title": "Senior Python Developer",
            "description": "We are looking for an experienced Python developer to join our team.",
            "requirements": "5+ years Python experience, Django, FastAPI, SQL",
            "company_id": 1,
            "posted_by": 3,
            "location": "Tokyo, Japan",
            "employment_type": "full_time",
            "salary_min": 6000000,
            "salary_max": 9000000,
            "salary_currency": "JPY",
            "status": "active",
            "created_at": datetime.utcnow().isoformat(),
            "application_deadline": (
                datetime.utcnow() + timedelta(days=30)
            ).isoformat(),
        },
        {
            "id": 2,
            "title": "AI Engineer",
            "description": "Join our AI team to develop cutting-edge machine learning solutions.",
            "requirements": "ML/AI experience, Python, TensorFlow, PyTorch",
            "company_id": 2,
            "posted_by": 2,
            "location": "Osaka, Japan",
            "employment_type": "full_time",
            "salary_min": 5000000,
            "salary_max": 8000000,
            "salary_currency": "JPY",
            "status": "active",
            "created_at": datetime.utcnow().isoformat(),
            "application_deadline": (
                datetime.utcnow() + timedelta(days=45)
            ).isoformat(),
        },
    ]

    # Sample interviews
    interviews = [
        {
            "id": 1,
            "candidate_id": 4,
            "recruiter_id": 3,
            "title": "Technical Interview - Senior Python Developer",
            "scheduled_at": (
                datetime.utcnow() + timedelta(days=3, hours=14)
            ).isoformat(),
            "duration_minutes": 60,
            "interview_type": "technical",
            "status": "scheduled",
            "meeting_link": "https://meet.example.com/interview1",
            "notes": "Technical interview focusing on Python and system design",
        },
        {
            "id": 2,
            "candidate_id": 5,
            "recruiter_id": 3,
            "title": "Behavioral Interview - AI Engineer",
            "scheduled_at": (
                datetime.utcnow() + timedelta(days=5, hours=10)
            ).isoformat(),
            "duration_minutes": 45,
            "interview_type": "behavioral",
            "status": "scheduled",
            "meeting_link": "https://meet.example.com/interview2",
            "notes": "Behavioral and cultural fit interview",
        },
    ]

    # Sample messages
    messages = [
        {
            "id": 1,
            "sender_id": 3,
            "recipient_id": 4,
            "subject": "Interview Invitation - Senior Python Developer",
            "content": "Hello John, we would like to invite you for an interview for the Senior Python Developer position.",
            "thread_id": "thread_1",
            "is_read": False,
            "created_at": datetime.utcnow().isoformat(),
        },
        {
            "id": 2,
            "sender_id": 4,
            "recipient_id": 3,
            "subject": "Re: Interview Invitation - Senior Python Developer",
            "content": "Thank you for the invitation. I am available for the interview.",
            "thread_id": "thread_1",
            "is_read": True,
            "created_at": (datetime.utcnow() + timedelta(minutes=30)).isoformat(),
        },
    ]

    # Sample data structure
    sample_data = {
        "users": users,
        "companies": companies,
        "jobs": jobs,
        "interviews": interviews,
        "messages": messages,
        "meta": {
            "created_at": datetime.utcnow().isoformat(),
            "total_users": len(users),
            "total_companies": len(companies),
            "total_jobs": len(jobs),
            "total_interviews": len(interviews),
            "total_messages": len(messages),
        },
    }

    return sample_data


def main():
    """Generate and save sample data"""
    print("Creating sample data for MiraiWorks HRMS...")

    # Create sample data
    data = create_sample_json_data()

    # Save to JSON file for frontend demonstration
    with open("sample_data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print("Sample data created successfully!")
    print(f"Generated {data['meta']['total_users']} users")
    print(f"Generated {data['meta']['total_companies']} companies")
    print(f"Generated {data['meta']['total_jobs']} jobs")
    print(f"Generated {data['meta']['total_interviews']} interviews")
    print(f"Generated {data['meta']['total_messages']} messages")

    print("\nTest accounts for frontend:")
    print("Super Admin: admin@miraiworks.com / admin123")
    print("Company Admin: admin@techcorp.jp / password123")
    print("Recruiter: recruiter1@techcorp.jp / password123")
    print("Candidate 1: john.doe@email.com / password123")
    print("Candidate 2: jane.smith@email.com / password123")

    print("\nSample data saved to 'sample_data.json'")
    print("Frontend can now load this data for demonstration purposes.")


if __name__ == "__main__":
    main()
