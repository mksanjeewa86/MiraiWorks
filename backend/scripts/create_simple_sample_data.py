#!/usr/bin/env python3
"""Create simple sample data for MiraiWorks database."""
import asyncio
import os
import sys

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import AsyncSessionLocal
from app.models.company import Company
from app.models.role import Role, UserRole
from app.models.user import User
from app.services.auth_service import auth_service
from app.utils.constants import CompanyType
from app.utils.constants import UserRole as UserRoleEnum


async def test_db_connection():
    """Test database connection."""
    try:
        async with AsyncSessionLocal() as db:
            result = await db.execute(text("SELECT 1"))
            return True
    except Exception as e:
        print(f"Database connection failed: {str(e)}")
        return False


async def create_companies(db: AsyncSession):
    """Create sample companies."""
    print("Creating sample companies...")

    companies_data = [
        {
            "name": "TechCorp Solutions",
            "domain": "techcorp.com",
            "type": CompanyType.EMPLOYER,
            "email": "hr@techcorp.com",
            "description": "Leading technology solutions provider",
        },
        {
            "name": "Global Recruiters Inc",
            "domain": "globalrecruiters.com",
            "type": CompanyType.RECRUITER,
            "email": "info@globalrecruiters.com",
            "description": "Premier recruitment agency",
        },
    ]

    companies = {}
    for data in companies_data:
        company = Company(
            name=data["name"],
            domain=data["domain"],
            type=data["type"],
            email=data["email"],
            description=data["description"],
            is_active="1",
        )
        db.add(company)
        companies[data["name"]] = company
        print(f"  Created: {data['name']}")

    await db.commit()

    # Refresh to get IDs
    for company in companies.values():
        await db.refresh(company)

    return companies


async def create_sample_users(db: AsyncSession, companies: dict):
    """Create sample users."""
    print("Creating sample users...")

    # Get roles
    roles_result = await db.execute(select(Role))
    roles = {role.name: role for role in roles_result.scalars().all()}

    users_data = [
        {
            "email": "admin@techcorp.com",
            "password": "password",
            "first_name": "Alice",
            "last_name": "Johnson",
            "role": UserRoleEnum.COMPANY_ADMIN,
            "company": "TechCorp Solutions",
        },
        {
            "email": "recruiter@globalrecruiters.com",
            "password": "password",
            "first_name": "Sarah",
            "last_name": "Wilson",
            "role": UserRoleEnum.RECRUITER,
            "company": "Global Recruiters Inc",
        },
        {
            "email": "jane.candidate@email.com",
            "password": "password",
            "first_name": "Jane",
            "last_name": "Developer",
            "role": UserRoleEnum.CANDIDATE,
            "company": None,
        },
        {
            "email": "john.candidate@email.com",
            "password": "password",
            "first_name": "John",
            "last_name": "Engineer",
            "role": UserRoleEnum.CANDIDATE,
            "company": None,
        },
    ]

    created_users = {}
    for data in users_data:
        # Create user
        hashed_password = auth_service.get_password_hash(data["password"])
        company = companies.get(data["company"]) if data["company"] else None

        user = User(
            email=data["email"],
            hashed_password=hashed_password,
            first_name=data["first_name"],
            last_name=data["last_name"],
            company_id=company.id if company else None,
            is_active=True,
            is_admin=data["role"]
            in [UserRoleEnum.SUPER_ADMIN, UserRoleEnum.COMPANY_ADMIN],
        )

        db.add(user)
        await db.commit()
        await db.refresh(user)

        # Assign role
        user_role = UserRole(user_id=user.id, role_id=roles[data["role"].value].id)
        db.add(user_role)

        created_users[data["email"]] = user
        print(f"  Created: {data['email']} ({data['role'].value})")

    await db.commit()
    return created_users


async def main():
    """Main function."""
    print("Creating simple sample data for MiraiWorks...")
    print("Database: mysql://hrms:hrms@localhost:3306/miraiworks")

    # Test connection first
    if not await test_db_connection():
        print("Please ensure MySQL is running and accessible")
        print("Try: docker exec hrms_db mysql -u hrms -phrms -e 'SELECT 1;'")
        return

    try:
        # Check if companies already exist
        async with AsyncSessionLocal() as db:
            result = await db.execute(select(Company).limit(1))
            if result.scalar_one_or_none():
                print("Sample data already exists!")

                # Show existing data
                companies = await db.execute(select(Company))
                print("\nExisting companies:")
                for company in companies.scalars():
                    print(f"  - {company.name} ({company.type})")

                users = await db.execute(select(User))
                print("\nExisting users:")
                for user in users.scalars():
                    print(f"  - {user.email} ({user.first_name} {user.last_name})")

                return

            # Create sample data
            companies = await create_companies(db)
            users = await create_sample_users(db, companies)

        print("\nSample data created successfully!")
        print(f"Created {len(companies)} companies and {len(users)} users")

        print("\nLogin credentials:")
        print("  Company Admin: admin@techcorp.com / password")
        print("  Recruiter: recruiter@globalrecruiters.com / password")
        print("  Candidate: jane.candidate@email.com / password")
        print("  Candidate: john.candidate@email.com / password")

    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
