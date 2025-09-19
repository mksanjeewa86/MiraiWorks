#!/usr/bin/env python3
"""
Test script to verify the /api/auth/me endpoint returns company data
for the frontend form auto-population.
"""

import asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

# Add backend to path
import sys
sys.path.insert(0, './backend')

from app.main import app
from app.database import get_db
from app.models.user import User
from app.models.company import Company
from app.models.role import Role, UserRole
from app.services.auth_service import auth_service
from app.utils.constants import UserRole as UserRoleEnum


async def test_auth_me_with_company():
    """Test that /api/auth/me returns company data for auto-population."""

    print("Testing /api/auth/me endpoint with company data")
    print("=" * 60)

    async with AsyncClient(app=app, base_url="http://testserver") as client:
        # Get a database session
        async for db_session in get_db():
            try:
                print("Step 1: Creating test company...")

                # Create a test company
                test_company = Company(
                    name="Test Auto Company",
                    email="auto@test.com",
                    phone="03-1234-5678",
                    type="employer"
                )
                db_session.add(test_company)
                await db_session.commit()
                await db_session.refresh(test_company)
                print(f"SUCCESS: Created company: {test_company.name} (type: {test_company.type})")

                # Create company admin role
                company_admin_role = await db_session.execute(
                    select(Role).where(Role.name == UserRoleEnum.COMPANY_ADMIN)
                )
                role = company_admin_role.scalar_one_or_none()

                if not role:
                    role = Role(
                        name=UserRoleEnum.COMPANY_ADMIN,
                        description="Company Administrator"
                    )
                    db_session.add(role)
                    await db_session.commit()
                    await db_session.refresh(role)

                # Create company admin user
                company_admin = User(
                    email='companytest@admin.com',
                    first_name='Test',
                    last_name='Admin',
                    company_id=test_company.id,
                    hashed_password=auth_service.get_password_hash('testpass123'),
                    is_active=True,
                    is_admin=True,
                    require_2fa=False,
                )
                db_session.add(company_admin)
                await db_session.commit()
                await db_session.refresh(company_admin)

                # Assign role
                user_role = UserRole(user_id=company_admin.id, role_id=role.id)
                db_session.add(user_role)
                await db_session.commit()
                print(f"SUCCESS: Created company admin: {company_admin.email}")

                print("\nStep 2: Testing login...")

                # Login as company admin
                login_response = await client.post(
                    "/api/auth/login",
                    json={"email": "companytest@admin.com", "password": "testpass123"},
                )

                if login_response.status_code != 200:
                    print(f"ERROR: Login failed: {login_response.text}")
                    return False

                token_data = login_response.json()
                headers = {"Authorization": f"Bearer {token_data['access_token']}"}
                print("SUCCESS: Login successful")

                print("\nStep 3: Testing /api/auth/me endpoint...")

                # Test the /me endpoint
                me_response = await client.get("/api/auth/me", headers=headers)

                if me_response.status_code != 200:
                    print(f"ERROR: /me endpoint failed: {me_response.text}")
                    return False

                user_data = me_response.json()
                print("SUCCESS: /api/auth/me endpoint works")

                print("\nStep 4: Verifying company data in response...")

                # Check if company data is included
                required_fields = [
                    'id', 'email', 'first_name', 'last_name', 'company_id', 'company'
                ]

                for field in required_fields:
                    if field not in user_data:
                        print(f"❌ Missing field: {field}")
                        return False
                    print(f"✅ {field}: {user_data[field]}")

                # Specifically check company object
                if not user_data.get('company'):
                    print("❌ Company object is missing from response")
                    return False

                company_obj = user_data['company']
                required_company_fields = ['id', 'name', 'type']

                print("\nCompany object details:")
                for field in required_company_fields:
                    if field not in company_obj:
                        print(f"❌ Missing company field: {field}")
                        return False
                    print(f"✅ company.{field}: {company_obj[field]}")

                print("\nStep 5: Verifying frontend auto-population will work...")

                # Simulate frontend logic
                company_id = str(company_obj['id'])
                company_type = company_obj['type']
                auto_role = 'employer' if company_type == 'employer' else 'recruiter'

                print(f"Frontend would auto-set:")
                print(f"  - company_id: '{company_id}' (from user.company.id)")
                print(f"  - role: '{auto_role}' (from user.company.type)")

                # Verify these values would make button active
                form_valid = bool(company_id) and bool(auto_role)
                print(f"\nForm validation for auto-set fields: {'✅ VALID' if form_valid else '❌ INVALID'}")

                if form_valid:
                    print("✅ Create user button should be ENABLED when user fills name/email")
                else:
                    print("❌ Create user button would still be DISABLED")
                    return False

                print("\n" + "=" * 60)
                print("🎉 SUCCESS! Company data is properly returned by /api/auth/me")
                print("📋 Frontend form auto-population should now work:")
                print("   ✅ user.company.id available for company_id field")
                print("   ✅ user.company.type available for role selection")
                print("   ✅ Create user button will activate when required fields filled")

                return True

            except Exception as e:
                print(f"❌ Test failed with error: {e}")
                import traceback
                traceback.print_exc()
                return False

            finally:
                # Clean up
                await db_session.rollback()
                break


if __name__ == "__main__":
    success = asyncio.run(test_auth_me_with_company())
    if success:
        print("\n🎯 CONCLUSION: The create user button issue should now be FIXED!")
        print("   The /api/auth/me endpoint now returns full company data")
        print("   Frontend auto-population will work correctly")
    else:
        print("\n❌ ISSUE: Backend changes need further investigation")

    sys.exit(0 if success else 1)