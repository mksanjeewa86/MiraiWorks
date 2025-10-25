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
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import *  # noqa: F403, F405  # Import all models to ensure table creation
from app.services.auth_service import auth_service
from app.utils.constants import UserRole as UserRoleEnum


@pytest.mark.asyncio
async def test_company_admin_user_creation_e2e_flow(
    client: AsyncClient, db_session: AsyncSession
):
    """Test the complete end-to-end user creation flow for a company admin."""

    print("\n🧪 Starting End-to-End Company Admin User Creation Test")
    print("=" * 70)

    # Step 0: Create test roles first
    print("📋 Creating test roles...")
    roles = {}
    for role_name in UserRoleEnum:
        role = Role(name=role_name.value, description=f"Test {role_name.value} role")
        db_session.add(role)
        roles[role_name.value] = role

    await db_session.commit()

    # Refresh all roles
    for role in roles.values():
        await db_session.refresh(role)

    print(f"✅ Created {len(roles)} test roles")

    # Step 1: Create test company
    test_company = Company(
        name="E2E Test Company",
        email="e2e@company.com",
        phone="03-1234-5678",
        type="member",
    )
    db_session.add(test_company)
    await db_session.commit()
    await db_session.refresh(test_company)

    # Step 2: Create company admin user
    company_admin = User(
        email="e2e.admin@test.com",
        first_name="E2E",
        last_name="Admin",
        company_id=test_company.id,
        hashed_password=auth_service.get_password_hash("testpass123"),
        is_active=True,
        is_admin=True,
        require_2fa=False,
    )
    db_session.add(company_admin)
    await db_session.commit()
    await db_session.refresh(company_admin)

    # Step 3: Assign company_admin role
    company_admin_role = roles[UserRoleEnum.ADMIN.value]
    user_role = UserRole(user_id=company_admin.id, role_id=company_admin_role.id)
    db_session.add(user_role)
    await db_session.commit()

    # Step 4: Authenticate company admin
    login_response = await client.post(
        "/api/auth/login",
        json={"email": "e2e.admin@test.com", "password": "testpass123"},
    )
    assert login_response.status_code == 200
    token_data = login_response.json()

    # Handle 2FA if required
    if token_data.get("require_2fa"):
        verify_response = await client.post(
            "/api/auth/2fa/verify", json={"user_id": company_admin.id, "code": "123456"}
        )
        assert verify_response.status_code == 200
        token_data = verify_response.json()

    headers = {"Authorization": f"Bearer {token_data['access_token']}"}

    # Step 5: Simulate frontend form data (company admin scenario)

    # Simulate what happens when company admin loads the form
    frontend_form_data = {
        "first_name": "",  # Initially empty
        "last_name": "",  # Initially empty
        "email": "",  # Initially empty
        "company_id": "",  # Will be auto-set
        "role": "",  # Will be auto-set
    }

    # Simulate auto-setting company and role (from useEffect)
    auto_role = "member" if test_company.type == "member" else "member"

    frontend_form_data["company_id"] = str(test_company.id)
    frontend_form_data["role"] = auto_role

    # Check form validation at this point (should be disabled)
    is_form_valid_empty = (
        bool(frontend_form_data["first_name"])
        and bool(frontend_form_data["last_name"])
        and bool(frontend_form_data["email"])
        and bool(frontend_form_data["company_id"])
        and bool(frontend_form_data["role"])
    )
    assert (
        not is_form_valid_empty
    ), "Form should be invalid when required fields are empty"

    # Simulate user filling in the form
    frontend_form_data["first_name"] = "John"
    frontend_form_data["last_name"] = "Doe"
    frontend_form_data["email"] = "john.doe@e2etest.com"

    # Check form validation after filling (should be enabled)
    is_form_valid_filled = (
        bool(frontend_form_data["first_name"])
        and bool(frontend_form_data["last_name"])
        and bool(frontend_form_data["email"])
        and bool(frontend_form_data["company_id"])
        and bool(frontend_form_data["role"])
    )
    assert (
        is_form_valid_filled
    ), "Form should be valid when all required fields are filled"

    # Step 6: Test backend API with frontend data

    backend_user_data = {
        "email": frontend_form_data["email"],
        "first_name": frontend_form_data["first_name"],
        "last_name": frontend_form_data["last_name"],
        "company_id": int(frontend_form_data["company_id"]),
        "roles": [frontend_form_data["role"]],
    }

    create_response = await client.post(
        "/api/admin/users", json=backend_user_data, headers=headers
    )

    assert create_response.status_code == 201
    create_response.json()

    # Step 7: Verify in database

    db_user = await db_session.execute(
        select(User).where(User.email == frontend_form_data["email"])
    )
    db_user_obj = db_user.scalar_one()

    assert db_user_obj.first_name == frontend_form_data["first_name"]
    assert db_user_obj.last_name == frontend_form_data["last_name"]
    assert db_user_obj.company_id == test_company.id

    # Verify role assignment
    user_roles = await db_session.execute(
        select(UserRole).where(UserRole.user_id == db_user_obj.id)
    )
    role_assignments = user_roles.scalars().all()
    assert len(role_assignments) > 0

    # Step 8: Test permission restrictions

    # Try to create user with super_admin role (should fail)
    invalid_user_data = {
        "email": "invalid@test.com",
        "first_name": "Invalid",
        "last_name": "User",
        "company_id": test_company.id,
        "roles": ["system_admin"],
    }

    forbidden_response = await client.post(
        "/api/admin/users", json=invalid_user_data, headers=headers
    )

    assert forbidden_response.status_code == 403
    error_detail = forbidden_response.json()["detail"]
    assert "system_admin" in error_detail.lower()

    # Try to create user for different company (should fail)
    other_company = Company(
        name="Other Company",
        email="other@company.com",
        phone="03-9876-5432",
        type="member",
    )
    db_session.add(other_company)
    await db_session.commit()
    await db_session.refresh(other_company)

    other_company_user_data = {
        "email": "other@test.com",
        "first_name": "Other",
        "last_name": "User",
        "company_id": other_company.id,
        "roles": ["member"],
    }

    other_company_response = await client.post(
        "/api/admin/users", json=other_company_user_data, headers=headers
    )

    assert other_company_response.status_code == 403
    error_detail = other_company_response.json()["detail"]
    assert "other companies" in error_detail.lower()


if __name__ == "__main__":
    print("Run this test with: pytest test_e2e_user_creation.py -v -s")
