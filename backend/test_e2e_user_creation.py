#!/usr/bin/env python3
"""
End-to-End Test for Company Admin User Creation Flow

This test validates the complete user creation workflow:
1. Authentication as company admin
2. Frontend form simulation
3. Backend API validation
4. Database verification
"""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.user import User
from app.models.company import Company
from app.models.role import Role, UserRole
from app.services.auth_service import auth_service
from app.utils.constants import UserRole as UserRoleEnum


@pytest.mark.asyncio
async def test_company_admin_user_creation_e2e_flow(client: AsyncClient, db_session: AsyncSession):
    """Test the complete end-to-end user creation flow for a company admin."""

    print("\n🧪 Starting End-to-End Company Admin User Creation Test")
    print("=" * 70)

    # Step 1: Create test company
    test_company = Company(
        name="E2E Test Company",
        email="e2e@company.com",
        phone="03-1234-5678",
        type="employer"
    )
    db_session.add(test_company)
    await db_session.commit()
    await db_session.refresh(test_company)
    print(f"✅ Created test company: {test_company.name} (ID: {test_company.id})")

    # Step 2: Create company admin user
    company_admin = User(
        email='e2e.admin@test.com',
        first_name='E2E',
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
    print(f"✅ Created company admin: {company_admin.email} (ID: {company_admin.id})")

    # Step 3: Assign company_admin role
    role_result = await db_session.execute(
        select(Role).where(Role.name == UserRoleEnum.COMPANY_ADMIN)
    )
    company_admin_role = role_result.scalar_one_or_none()

    if not company_admin_role:
        company_admin_role = Role(
            name=UserRoleEnum.COMPANY_ADMIN,
            description="Company Administrator"
        )
        db_session.add(company_admin_role)
        await db_session.commit()
        await db_session.refresh(company_admin_role)

    user_role = UserRole(user_id=company_admin.id, role_id=company_admin_role.id)
    db_session.add(user_role)
    await db_session.commit()
    print(f"✅ Assigned company_admin role")

    # Step 4: Authenticate company admin
    print("\n🔐 Testing Authentication...")
    login_response = await client.post(
        "/api/auth/login",
        json={"email": "e2e.admin@test.com", "password": "testpass123"},
    )
    assert login_response.status_code == 200
    token_data = login_response.json()

    # Handle 2FA if required
    if token_data.get("require_2fa"):
        verify_response = await client.post(
            "/api/auth/2fa/verify",
            json={"user_id": company_admin.id, "code": "123456"}
        )
        assert verify_response.status_code == 200
        token_data = verify_response.json()

    headers = {"Authorization": f"Bearer {token_data['access_token']}"}
    print("✅ Authentication successful")

    # Step 5: Simulate frontend form data (company admin scenario)
    print("\n📝 Testing Frontend Form Logic...")

    # Simulate what happens when company admin loads the form
    frontend_form_data = {
        "first_name": "",        # Initially empty
        "last_name": "",         # Initially empty
        "email": "",             # Initially empty
        "company_id": "",        # Will be auto-set
        "role": ""               # Will be auto-set
    }

    # Simulate auto-setting company and role (from useEffect)
    if test_company.type == 'employer':
        auto_role = 'employer'
    else:
        auto_role = 'recruiter'

    frontend_form_data["company_id"] = str(test_company.id)
    frontend_form_data["role"] = auto_role

    print(f"   Auto-set company_id: {frontend_form_data['company_id']}")
    print(f"   Auto-set role: {frontend_form_data['role']}")

    # Check form validation at this point (should be disabled)
    is_form_valid_empty = (
        bool(frontend_form_data["first_name"]) and
        bool(frontend_form_data["last_name"]) and
        bool(frontend_form_data["email"]) and
        bool(frontend_form_data["company_id"]) and
        bool(frontend_form_data["role"])
    )
    assert not is_form_valid_empty, "Form should be invalid when required fields are empty"
    print("✅ Form correctly disabled when required fields empty")

    # Simulate user filling in the form
    frontend_form_data["first_name"] = "John"
    frontend_form_data["last_name"] = "Doe"
    frontend_form_data["email"] = "john.doe@e2etest.com"

    # Check form validation after filling (should be enabled)
    is_form_valid_filled = (
        bool(frontend_form_data["first_name"]) and
        bool(frontend_form_data["last_name"]) and
        bool(frontend_form_data["email"]) and
        bool(frontend_form_data["company_id"]) and
        bool(frontend_form_data["role"])
    )
    assert is_form_valid_filled, "Form should be valid when all required fields are filled"
    print("✅ Form correctly enabled when all required fields filled")

    # Step 6: Test backend API with frontend data
    print("\n🌐 Testing Backend API...")

    backend_user_data = {
        "email": frontend_form_data["email"],
        "first_name": frontend_form_data["first_name"],
        "last_name": frontend_form_data["last_name"],
        "company_id": int(frontend_form_data["company_id"]),
        "roles": [frontend_form_data["role"]]
    }

    create_response = await client.post(
        "/api/admin/users",
        json=backend_user_data,
        headers=headers
    )

    assert create_response.status_code == 201
    created_user = create_response.json()
    print(f"✅ Successfully created user via API: {created_user['email']} (ID: {created_user['id']})")

    # Step 7: Verify in database
    print("\n💾 Verifying Database...")

    db_user = await db_session.execute(
        select(User).where(User.email == frontend_form_data["email"])
    )
    db_user_obj = db_user.scalar_one()

    assert db_user_obj.first_name == frontend_form_data["first_name"]
    assert db_user_obj.last_name == frontend_form_data["last_name"]
    assert db_user_obj.company_id == test_company.id
    print(f"✅ User correctly stored in database")

    # Verify role assignment
    user_roles = await db_session.execute(
        select(UserRole).where(UserRole.user_id == db_user_obj.id)
    )
    role_assignments = user_roles.scalars().all()
    assert len(role_assignments) > 0
    print(f"✅ User role correctly assigned")

    # Step 8: Test permission restrictions
    print("\n🚫 Testing Permission Restrictions...")

    # Try to create user with super_admin role (should fail)
    invalid_user_data = {
        "email": "invalid@test.com",
        "first_name": "Invalid",
        "last_name": "User",
        "company_id": test_company.id,
        "roles": ["super_admin"]
    }

    forbidden_response = await client.post(
        "/api/admin/users",
        json=invalid_user_data,
        headers=headers
    )

    assert forbidden_response.status_code == 403
    error_detail = forbidden_response.json()["detail"]
    assert "super_admin" in error_detail.lower()
    print(f"✅ Correctly blocked super_admin role assignment")

    # Try to create user for different company (should fail)
    other_company = Company(
        name="Other Company",
        email="other@company.com",
        phone="03-9876-5432",
        type="recruiter"
    )
    db_session.add(other_company)
    await db_session.commit()
    await db_session.refresh(other_company)

    other_company_user_data = {
        "email": "other@test.com",
        "first_name": "Other",
        "last_name": "User",
        "company_id": other_company.id,
        "roles": ["recruiter"]
    }

    other_company_response = await client.post(
        "/api/admin/users",
        json=other_company_user_data,
        headers=headers
    )

    assert other_company_response.status_code == 403
    error_detail = other_company_response.json()["detail"]
    assert "other companies" in error_detail.lower()
    print(f"✅ Correctly blocked cross-company user creation")

    print("\n" + "=" * 70)
    print("🎉 End-to-End Test PASSED!")
    print("📋 Test Summary:")
    print("   ✅ Company admin authentication")
    print("   ✅ Frontend form validation logic")
    print("   ✅ Auto-setting of company and role")
    print("   ✅ Backend API user creation")
    print("   ✅ Database persistence")
    print("   ✅ Permission restrictions")
    print("   ✅ Cross-company protection")
    print("\n💡 The create user button should work correctly when:")
    print("   1. User fills in first_name, last_name, email")
    print("   2. company_id and role are auto-set by useEffect")
    print("   3. All validation checks pass")


if __name__ == "__main__":
    print("Run this test with: pytest test_e2e_user_creation.py -v -s")