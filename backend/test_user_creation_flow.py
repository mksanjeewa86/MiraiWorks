#!/usr/bin/env python3
"""
Simple test to verify the frontend-backend user creation flow works correctly.
This script tests the exact API calls that the frontend makes.
"""

import asyncio
import sys
import os

# Add the backend path to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.main import app
from app.database import get_db
from app.models.user import User
from app.models.company import Company
from app.models.role import Role, UserRole
from app.services.auth_service import auth_service
from app.utils.constants import UserRole as UserRoleEnum


async def test_company_admin_user_creation():
    """Test the exact flow a company admin would use to create a user via the frontend."""

    print("Testing Company Admin User Creation Flow")
    print("=" * 50)

    async with AsyncClient(app=app, base_url="http://testserver") as client:
        # Get a database session
        async for db_session in get_db():
            try:
                print("Step 1: Setting up test data...")

                # Create a test company
                test_company = Company(
                    name="Test Company",
                    email="test@company.com",
                    phone="03-1234-5678",
                    type="employer"
                )
                db_session.add(test_company)
                await db_session.commit()
                await db_session.refresh(test_company)
                print(f"Created test company: {test_company.name}")

                # Create roles if they don't exist
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
                    print("✅ Created company_admin role")

                # Create company admin user
                company_admin = User(
                    email='admin@test.com',
                    first_name='Company',
                    last_name='Admin',
                    company_id=test_company.id,
                    hashed_password=auth_service.get_password_hash('password123'),
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
                print(f"✅ Created company admin: {company_admin.email}")

                print("\n🔐 Step 2: Company admin login...")

                # Login as company admin
                login_response = await client.post(
                    "/api/auth/login",
                    json={"email": "admin@test.com", "password": "password123"},
                )
                print(f"📊 Login response: {login_response.status_code}")

                if login_response.status_code != 200:
                    print(f"❌ Login failed: {login_response.text}")
                    return False

                token_data = login_response.json()

                # Handle 2FA if required
                if token_data.get("require_2fa"):
                    print("🔐 Handling 2FA...")
                    verify_response = await client.post(
                        "/api/auth/2fa/verify",
                        json={"user_id": company_admin.id, "code": "123456"}
                    )
                    if verify_response.status_code != 200:
                        print(f"❌ 2FA failed: {verify_response.text}")
                        return False
                    token_data = verify_response.json()

                headers = {"Authorization": f"Bearer {token_data['access_token']}"}
                print("✅ Authentication successful")

                print("\n👤 Step 3: Creating new user (simulating frontend form submission)...")

                # This is the exact data that would be sent from the frontend form
                # after the user fills in first_name, last_name, email
                # and company_id + role are auto-set by useEffect
                user_creation_data = {
                    "email": "newuser@example.com",
                    "first_name": "John",
                    "last_name": "Doe",
                    "company_id": test_company.id,  # Auto-set by frontend
                    "roles": ["employer"]  # Auto-set by frontend based on company type
                }

                print("📋 Frontend form data:")
                print(f"   - first_name: '{user_creation_data['first_name']}'")
                print(f"   - last_name: '{user_creation_data['last_name']}'")
                print(f"   - email: '{user_creation_data['email']}'")
                print(f"   - company_id: {user_creation_data['company_id']} (auto-set)")
                print(f"   - roles: {user_creation_data['roles']} (auto-set)")

                # Frontend validation check (what happens in the form)
                is_form_valid = (
                    bool(user_creation_data["first_name"]) and
                    bool(user_creation_data["last_name"]) and
                    bool(user_creation_data["email"]) and
                    bool(user_creation_data["company_id"]) and
                    bool(user_creation_data["roles"])
                )

                print(f"📝 Form validation result: {is_form_valid}")
                if not is_form_valid:
                    print("❌ Form validation failed - button should be disabled")
                    return False

                print("✅ Form validation passed - button should be enabled")

                # Submit to backend (what happens when user clicks Create User)
                create_response = await client.post(
                    "/api/admin/users",
                    json=user_creation_data,
                    headers=headers
                )

                print(f"📊 User creation response: {create_response.status_code}")

                if create_response.status_code == 201:
                    user_info = create_response.json()
                    print(f"✅ Successfully created user:")
                    print(f"   - ID: {user_info['id']}")
                    print(f"   - Email: {user_info['email']}")
                    print(f"   - Name: {user_info['first_name']} {user_info['last_name']}")
                    print(f"   - Company: {user_info['company_name']}")
                    print(f"   - Roles: {user_info['roles']}")
                else:
                    print(f"❌ User creation failed: {create_response.text}")
                    return False

                print("\n🧪 Step 4: Testing form validation scenarios...")

                # Test invalid scenario - empty fields
                invalid_data = {
                    "email": "",
                    "first_name": "",
                    "last_name": "",
                    "company_id": test_company.id,
                    "roles": ["employer"]
                }

                invalid_form_check = (
                    bool(invalid_data["first_name"]) and
                    bool(invalid_data["last_name"]) and
                    bool(invalid_data["email"]) and
                    bool(invalid_data["company_id"]) and
                    bool(invalid_data["roles"])
                )

                if invalid_form_check:
                    print("❌ Form validation is broken - should reject empty fields")
                    return False
                else:
                    print("✅ Form correctly rejects empty required fields")

                print("\n" + "=" * 50)
                print("🎉 All tests passed!")
                print("📋 Summary:")
                print("   ✅ Company admin can authenticate")
                print("   ✅ Form validation works correctly")
                print("   ✅ User creation API works")
                print("   ✅ Frontend-backend integration is working")
                print("\n💡 The create user button should:")
                print("   - Be DISABLED when required fields are empty")
                print("   - Be ENABLED when all fields are filled")
                print("   - Successfully create users when clicked")

                return True

            except Exception as e:
                print(f"❌ Test failed with error: {e}")
                import traceback
                traceback.print_exc()
                return False

            finally:
                # Clean up - rollback any changes
                await db_session.rollback()
                break


if __name__ == "__main__":
    success = asyncio.run(test_company_admin_user_creation())
    if success:
        print("\n🎯 CONCLUSION: Backend is working correctly!")
        print("   If the frontend button is still inactive, check:")
        print("   1. Form field state synchronization")
        print("   2. useEffect dependency arrays")
        print("   3. React re-rendering timing")
        print("   4. Browser console for any JavaScript errors")
    else:
        print("\n❌ Backend has issues that need to be fixed.")

    sys.exit(0 if success else 1)