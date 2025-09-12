#!/usr/bin/env python3
"""
Setup test data for E2E tests
Creates necessary test users, companies, and initial data
"""

import asyncio
import os
import sys
from pathlib import Path

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.models.company import Company
from app.models.user import User
from app.models.role import Role, UserRole
from app.models.user_settings import UserSettings
from app.models.direct_message import DirectMessage
from app.utils.password import get_password_hash
from app.utils.constants import MessageType


async def setup_test_data():
    """Set up test data for E2E tests"""
    
    # Use test database URL
    DATABASE_URL = os.getenv(
        'TEST_DATABASE_URL',
        'postgresql+asyncpg://test_user:test_password@localhost:5432/test_miraiworks'
    )
    
    engine = create_async_engine(DATABASE_URL)
    
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    
    # Create session
    TestSession = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with TestSession() as session:
        # Create test company
        test_company = Company(
            name="Test Company Inc",
            domain="testcompany.com",
            industry="Technology",
            size="50-100",
            is_active=True
        )
        session.add(test_company)
        await session.flush()
        
        # Create another test company
        global_recruiters = Company(
            name="Global Recruiters",
            domain="globalrecruiters.com",
            industry="Recruiting",
            size="100-500",
            is_active=True
        )
        session.add(global_recruiters)
        await session.flush()
        
        # Create MiraiWorks company
        miraiworks = Company(
            name="MiraiWorks",
            domain="miraiworks.com",
            industry="Technology",
            size="10-50",
            is_active=True
        )
        session.add(miraiworks)
        await session.flush()
        
        # Create roles
        roles = {}
        role_names = [
            ("candidate", "Job seeker/candidate role"),
            ("recruiter", "Recruiter role"),
            ("employer", "Employer role"),
            ("company_admin", "Company administrator role"),
            ("super_admin", "Super administrator role")
        ]
        
        for name, description in role_names:
            role = Role(name=name, description=description)
            session.add(role)
            roles[name] = role
        
        await session.flush()
        
        # Create test users
        test_users = [
            {
                "email": "jane.candidate@email.com",
                "first_name": "Jane",
                "last_name": "Developer",
                "phone": "1234567890",
                "company_id": test_company.id,
                "role": "candidate",
                "password": "password"
            },
            {
                "email": "john.candidate@email.com", 
                "first_name": "John",
                "last_name": "Engineer",
                "phone": "1234567891",
                "company_id": test_company.id,
                "role": "candidate",
                "password": "password"
            },
            {
                "email": "recruiter@globalrecruiters.com",
                "first_name": "Sarah",
                "last_name": "Wilson",
                "phone": "1234567892",
                "company_id": global_recruiters.id,
                "role": "recruiter", 
                "password": "password"
            },
            {
                "email": "alice.johnson@testcompany.com",
                "first_name": "Alice",
                "last_name": "Johnson",
                "phone": "1234567893",
                "company_id": test_company.id,
                "role": "employer",
                "password": "password"
            },
            {
                "email": "admin@testcompany.com",
                "first_name": "Admin",
                "last_name": "User",
                "phone": "1234567894",
                "company_id": test_company.id,
                "role": "company_admin",
                "password": "password",
                "is_admin": True
            },
            {
                "email": "admin@miraiworks.com",
                "first_name": "Super",
                "last_name": "Admin",
                "phone": "1234567895",
                "company_id": miraiworks.id,
                "role": "super_admin",
                "password": "password",
                "is_admin": True
            }
        ]
        
        created_users = {}
        
        for user_data in test_users:
            user = User(
                email=user_data["email"],
                first_name=user_data["first_name"],
                last_name=user_data["last_name"],
                phone=user_data["phone"],
                company_id=user_data["company_id"],
                hashed_password=get_password_hash(user_data["password"]),
                is_active=True,
                is_admin=user_data.get("is_admin", False),
                require_2fa=False
            )
            session.add(user)
            await session.flush()
            
            # Add user role
            user_role = UserRole(
                user_id=user.id,
                role_id=roles[user_data["role"]].id,
                assigned_by=1
            )
            session.add(user_role)
            
            # Add user settings
            settings = UserSettings(
                user_id=user.id,
                message_notifications=True,
                email_notifications=True,
                browser_notifications=False,
                sound_notifications=True
            )
            session.add(settings)
            
            created_users[user_data["email"]] = user
        
        await session.flush()
        
        # Create some test messages for conversations
        jane = created_users["jane.candidate@email.com"]
        john = created_users["john.candidate@email.com"]
        recruiter = created_users["recruiter@globalrecruiters.com"]
        
        # Conversation between Jane and Recruiter
        jane_recruiter_messages = [
            {
                "sender_id": jane.id,
                "recipient_id": recruiter.id,
                "content": "Hello, I'm interested in the software engineer position.",
                "type": MessageType.TEXT.value
            },
            {
                "sender_id": recruiter.id,
                "recipient_id": jane.id,
                "content": "Thank you for your interest! I'd love to discuss the role with you.",
                "type": MessageType.TEXT.value
            },
            {
                "sender_id": jane.id,
                "recipient_id": recruiter.id,
                "content": "Great! When would be a good time for a call?",
                "type": MessageType.TEXT.value
            },
            {
                "sender_id": recruiter.id,
                "recipient_id": jane.id,
                "content": "How about tomorrow at 2 PM? I'll send you a calendar invite.",
                "type": MessageType.TEXT.value,
                "is_read": False  # Unread message
            }
        ]
        
        for msg_data in jane_recruiter_messages:
            message = DirectMessage(**msg_data)
            session.add(message)
        
        # Conversation between John and Recruiter
        john_recruiter_messages = [
            {
                "sender_id": recruiter.id,
                "recipient_id": john.id,
                "content": "Hi John, I came across your profile and think you'd be a great fit for a senior developer role.",
                "type": MessageType.TEXT.value,
                "is_read": False  # Unread message
            },
            {
                "sender_id": john.id,
                "recipient_id": recruiter.id,
                "content": "Hello! I'm definitely interested. Can you tell me more about the company and role?",
                "type": MessageType.TEXT.value
            }
        ]
        
        for msg_data in john_recruiter_messages:
            message = DirectMessage(**msg_data)
            session.add(message)
        
        # Some messages between candidates (for search testing)
        candidate_messages = [
            {
                "sender_id": jane.id,
                "recipient_id": john.id,
                "content": "Hey John! How's your job search going?",
                "type": MessageType.TEXT.value
            },
            {
                "sender_id": john.id,
                "recipient_id": jane.id,
                "content": "It's going well! Just had an integration test interview yesterday.",
                "type": MessageType.TEXT.value
            },
            {
                "sender_id": jane.id,
                "recipient_id": john.id,
                "content": "That's awesome! Integration tests can be tricky but they're so important.",
                "type": MessageType.TEXT.value
            }
        ]
        
        for msg_data in candidate_messages:
            message = DirectMessage(**msg_data)
            session.add(message)
        
        await session.commit()
        
        print("✅ Test data setup completed successfully!")
        print(f"Created {len(test_users)} test users")
        print(f"Created {len(jane_recruiter_messages) + len(john_recruiter_messages) + len(candidate_messages)} test messages")
        print("\nTest users created:")
        for user_data in test_users:
            print(f"  - {user_data['email']} ({user_data['role']})")
    
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(setup_test_data())