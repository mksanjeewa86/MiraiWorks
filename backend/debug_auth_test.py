"""Debug auth test to understand database session issues."""

import asyncio
import os
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

os.environ["ENVIRONMENT"] = "test"


async def debug_auth_flow():
    from sqlalchemy import select

    from app.models.company import Company
    from app.models.role import Role, UserRole
    from app.models.user import User
    from app.services.auth_service import auth_service
    from app.tests.conftest import TestingSessionLocal, fast_clear_data
    from app.utils.constants import CompanyType
    from app.utils.constants import UserRole as UserRoleEnum

    # Clear data first
    await fast_clear_data()
    print("1. Data cleared")

    # Create test data step by step
    async with TestingSessionLocal() as session:
        try:
            # Create company
            company = Company(
                name="Test Company",
                type=CompanyType.EMPLOYER.value,
                email="test@company.com",
                is_active=True,
            )
            session.add(company)
            await session.flush()  # Get the ID
            print(f"2. Company created: {company.id}")

            # Create role
            role = Role(name=UserRoleEnum.CANDIDATE.value, description="Test role")
            session.add(role)
            await session.flush()
            print(f"3. Role created: {role.id}")

            # Create user
            user = User(
                email="test@example.com",
                first_name="Test",
                last_name="User",
                company_id=company.id,
                hashed_password=auth_service.get_password_hash("testpassword123"),
                is_active=True,
            )
            session.add(user)
            await session.flush()
            print(f"4. User created: {user.id}")

            # Create user role
            user_role = UserRole(user_id=user.id, role_id=role.id)
            session.add(user_role)

            # Commit everything
            await session.commit()
            print("5. All data committed")

        except Exception as e:
            print(f"Error creating test data: {e}")
            await session.rollback()
            return

    # Now test authentication in a separate session
    async with TestingSessionLocal() as session:
        try:
            # Check if user exists
            result = await session.execute(
                select(User).where(User.email == "test@example.com")
            )
            user = result.scalar_one_or_none()

            if user:
                print(f"6. User found: {user.email}, active: {user.is_active}")

                # Test password verification
                password_valid = auth_service.verify_password(
                    "testpassword123", user.hashed_password
                )
                print(f"7. Password verification: {password_valid}")

                # Test full authentication
                auth_user = await auth_service.authenticate_user(
                    session, "test@example.com", "testpassword123"
                )
                print(f"8. Authentication result: {auth_user is not None}")

                if auth_user:
                    print(f"   Authenticated user: {auth_user.email}")
                else:
                    print("   Authentication failed")

            else:
                print("6. User not found!")

        except Exception as e:
            print(f"Error during authentication test: {e}")


if __name__ == "__main__":
    asyncio.run(debug_auth_flow())
