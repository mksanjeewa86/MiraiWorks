#!/usr/bin/env python3
"""Reset all user passwords to 'password' for easier development testing."""
import asyncio
import os
import sys

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import select, text, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import AsyncSessionLocal
from app.models.user import User
from app.services.auth_service import auth_service


async def reset_all_passwords(db: AsyncSession):
    """Reset all user passwords to 'password'."""
    print("Resetting all user passwords to 'password'...")

    # Hash the new password
    new_password_hash = auth_service.get_password_hash("password")

    # Update all users
    result = await db.execute(update(User).values(hashed_password=new_password_hash))

    await db.commit()

    # Get count of updated users
    users_result = await db.execute(select(User))
    users = users_result.scalars().all()

    print(f"Updated passwords for {len(users)} users:")
    for user in users:
        print(f"  - {user.email}")

    return len(users)


async def create_basic_users_directly(db: AsyncSession):
    """Create users directly using raw SQL to avoid model relationship issues."""
    print("Creating basic users with direct SQL...")

    # First, ensure companies exist
    companies_sql = """
    INSERT IGNORE INTO companies (name, domain, type, email, description, is_active, created_at, updated_at) VALUES
    ('TechCorp Solutions', 'techcorp.com', 'employer', 'hr@techcorp.com', 'Leading technology solutions provider', '1', NOW(), NOW()),
    ('Global Recruiters Inc', 'globalrecruiters.com', 'recruiter', 'info@globalrecruiters.com', 'Premier recruitment agency', '1', NOW(), NOW());
    """

    await db.execute(text(companies_sql))

    # Get company IDs
    techcorp_result = await db.execute(
        text("SELECT id FROM companies WHERE name = 'TechCorp Solutions'")
    )
    techcorp_id = techcorp_result.scalar()

    recruiters_result = await db.execute(
        text("SELECT id FROM companies WHERE name = 'Global Recruiters Inc'")
    )
    recruiters_id = recruiters_result.scalar()

    # Hash password
    password_hash = auth_service.get_password_hash("password")

    # Create users
    users_data = [
        ("admin@techcorp.com", password_hash, "Alice", "Johnson", techcorp_id, True),
        (
            "recruiter@globalrecruiters.com",
            password_hash,
            "Sarah",
            "Wilson",
            recruiters_id,
            False,
        ),
        ("jane.candidate@email.com", password_hash, "Jane", "Developer", None, False),
        ("john.candidate@email.com", password_hash, "John", "Engineer", None, False),
        ("admin@miraiworks.com", password_hash, "Super", "Admin", None, True),
    ]

    for email, hashed_pwd, first_name, last_name, company_id, is_admin in users_data:
        # Check if user exists
        existing_user = await db.execute(
            text("SELECT id FROM users WHERE email = :email"), {"email": email}
        )
        if existing_user.scalar():
            # Update existing user
            await db.execute(
                text(
                    """
                UPDATE users SET
                    hashed_password = :password,
                    first_name = :first_name,
                    last_name = :last_name,
                    company_id = :company_id,
                    is_admin = :is_admin,
                    is_active = 1,
                    updated_at = NOW()
                WHERE email = :email
            """
                ),
                {
                    "email": email,
                    "password": hashed_pwd,
                    "first_name": first_name,
                    "last_name": last_name,
                    "company_id": company_id,
                    "is_admin": is_admin,
                },
            )
            print(f"  Updated: {email}")
        else:
            # Create new user
            await db.execute(
                text(
                    """
                INSERT INTO users (email, hashed_password, first_name, last_name, company_id, is_admin, is_active, created_at, updated_at)
                VALUES (:email, :password, :first_name, :last_name, :company_id, :is_admin, 1, NOW(), NOW())
            """
                ),
                {
                    "email": email,
                    "password": hashed_pwd,
                    "first_name": first_name,
                    "last_name": last_name,
                    "company_id": company_id,
                    "is_admin": is_admin,
                },
            )
            print(f"  Created: {email}")

    await db.commit()
    return len(users_data)


async def main():
    """Main function."""
    print("Password Reset Script for MiraiWorks")
    print("===================================")

    try:
        async with AsyncSessionLocal() as db:
            # Check if any users exist
            users_result = await db.execute(select(User))
            existing_users = users_result.scalars().all()

            if existing_users:
                print(
                    f"Found {len(existing_users)} existing users. Resetting passwords..."
                )
                count = await reset_all_passwords(db)
            else:
                print("No existing users found. Creating basic users...")
                count = await create_basic_users_directly(db)

        print("\n✅ Password reset completed successfully!")
        print(f"Processed {count} users")

        print("\n🔑 All users now have password: 'password'")
        print("\nTest credentials:")
        print("  - admin@techcorp.com / password (Company Admin)")
        print("  - recruiter@globalrecruiters.com / password (Recruiter)")
        print("  - jane.candidate@email.com / password (Candidate)")
        print("  - john.candidate@email.com / password (Candidate)")
        print("  - admin@miraiworks.com / password (Super Admin)")

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
