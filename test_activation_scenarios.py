#!/usr/bin/env python3
"""
End-to-End Scenario Tests for Complete Activation Flow
Tests the entire user journey from creation to successful activation.
"""

import asyncio
import sys
import secrets
import string
from datetime import datetime

# Add backend to path
sys.path.insert(0, './backend')

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from sqlalchemy.orm import selectinload

from app.main import app
from app.database import get_db
from app.models.user import User
from app.models.company import Company
from app.models.role import Role, UserRole
from app.models.user_settings import UserSettings
from app.services.auth_service import auth_service
from app.services.email_service import email_service
from app.utils.constants import UserRole as UserRoleEnum


class ActivationScenarioTests:
    """Complete scenario tests for activation flow."""

    def __init__(self):
        self.test_results = []
        self.total_tests = 0
        self.passed_tests = 0

    def log_test(self, test_name: str, success: bool, message: str = ""):
        """Log test result."""
        self.total_tests += 1
        if success:
            self.passed_tests += 1
            status = "✅ PASS"
        else:
            status = "❌ FAIL"

        result = f"{status}: {test_name}"
        if message:
            result += f" - {message}"

        print(result)
        self.test_results.append((test_name, success, message))

    async def scenario_1_new_user_creation_and_activation(self):
        """
        Scenario 1: Complete New User Journey
        1. Admin creates new user
        2. User receives activation email with temporary password
        3. User activates account successfully
        4. User can login with new password
        """
        print("\n" + "="*60)
        print("🧪 SCENARIO 1: New User Creation and Activation")
        print("="*60)

        async with AsyncClient(app=app, base_url="http://testserver") as client:
            async for db_session in get_db():
                try:
                    # Step 1: Create test company
                    print("Step 1: Creating test company...")
                    company = Company(
                        name="Scenario Test Company",
                        email="scenario@test.com",
                        phone="03-1234-5678",
                        type="employer"
                    )
                    db_session.add(company)
                    await db_session.commit()
                    await db_session.refresh(company)

                    # Step 2: Create company admin
                    print("Step 2: Creating company admin...")
                    admin_role = Role(
                        name=UserRoleEnum.COMPANY_ADMIN,
                        description="Company Administrator"
                    )
                    db_session.add(admin_role)
                    await db_session.commit()
                    await db_session.refresh(admin_role)

                    admin_user = User(
                        email="admin@scenario.com",
                        first_name="Scenario",
                        last_name="Admin",
                        company_id=company.id,
                        hashed_password=auth_service.get_password_hash("AdminPass123"),
                        is_active=True,
                        is_admin=True,
                        require_2fa=False,
                    )
                    db_session.add(admin_user)
                    await db_session.commit()
                    await db_session.refresh(admin_user)

                    user_role = UserRole(user_id=admin_user.id, role_id=admin_role.id)
                    db_session.add(user_role)
                    await db_session.commit()

                    # Step 3: Admin logs in
                    print("Step 3: Admin authentication...")
                    login_response = await client.post(
                        "/api/auth/login",
                        json={"email": "admin@scenario.com", "password": "AdminPass123"}
                    )

                    if login_response.status_code != 200:
                        self.log_test("Admin Login", False, f"Status: {login_response.status_code}")
                        return False

                    admin_token = login_response.json()["access_token"]
                    admin_headers = {"Authorization": f"Bearer {admin_token}"}
                    self.log_test("Admin Login", True)

                    # Step 4: Admin creates new user
                    print("Step 4: Creating new user via API...")
                    new_user_data = {
                        "email": "newuser@scenario.com",
                        "first_name": "New",
                        "last_name": "User",
                        "company_id": company.id,
                        "roles": ["employer"],
                        "phone": "+81-90-1234-5678"
                    }

                    create_response = await client.post(
                        "/api/admin/users",
                        json=new_user_data,
                        headers=admin_headers
                    )

                    if create_response.status_code != 201:
                        self.log_test("User Creation", False, f"Status: {create_response.status_code}")
                        return False

                    created_user_info = create_response.json()
                    new_user_id = created_user_info["id"]
                    self.log_test("User Creation", True)

                    # Step 5: Verify user was created with proper settings
                    print("Step 5: Verifying user creation...")
                    user_result = await db_session.execute(
                        select(User).where(User.id == new_user_id)
                    )
                    new_user = user_result.scalar_one()

                    if new_user.is_active:
                        self.log_test("User Inactive State", False, "User should be inactive initially")
                        return False

                    if not new_user.hashed_password:
                        self.log_test("Temporary Password Set", False, "No temporary password set")
                        return False

                    self.log_test("User Inactive State", True)
                    self.log_test("Temporary Password Set", True)

                    # Step 6: Simulate getting temporary password from email
                    print("Step 6: Generating temporary password for testing...")
                    # In real scenario, this would come from email
                    temp_password = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(12))
                    hashed_temp = auth_service.get_password_hash(temp_password)

                    await db_session.execute(
                        update(User).where(User.id == new_user_id).values(hashed_password=hashed_temp)
                    )
                    await db_session.commit()

                    print(f"   Temporary password for testing: {temp_password}")

                    # Step 7: User activates account
                    print("Step 7: User activation...")
                    activation_data = {
                        "userId": new_user_id,
                        "email": "newuser@scenario.com",
                        "temporaryPassword": temp_password,
                        "newPassword": "UserSecure@123"
                    }

                    activation_response = await client.post(
                        "/api/auth/activate",
                        json=activation_data
                    )

                    if activation_response.status_code != 200:
                        self.log_test("Account Activation", False, f"Status: {activation_response.status_code}")
                        return False

                    activation_result = activation_response.json()
                    if not activation_result.get("success"):
                        self.log_test("Account Activation", False, "Success flag not set")
                        return False

                    self.log_test("Account Activation", True)

                    # Step 8: Verify account is now active
                    print("Step 8: Verifying activation...")
                    await db_session.refresh(new_user)

                    if not new_user.is_active:
                        self.log_test("User Active Status", False, "User not activated")
                        return False

                    if not new_user.last_login:
                        self.log_test("Last Login Set", False, "Last login not set")
                        return False

                    self.log_test("User Active Status", True)
                    self.log_test("Last Login Set", True)

                    # Step 9: Verify user can login with new password
                    print("Step 9: Testing login with new password...")
                    login_test_response = await client.post(
                        "/api/auth/login",
                        json={"email": "newuser@scenario.com", "password": "UserSecure@123"}
                    )

                    if login_test_response.status_code != 200:
                        self.log_test("New Password Login", False, f"Status: {login_test_response.status_code}")
                        return False

                    self.log_test("New Password Login", True)

                    # Step 10: Verify user settings were created
                    print("Step 10: Verifying user settings...")
                    settings_result = await db_session.execute(
                        select(UserSettings).where(UserSettings.user_id == new_user_id)
                    )
                    user_settings = settings_result.scalar_one_or_none()

                    if not user_settings:
                        self.log_test("User Settings Created", False, "No user settings found")
                        return False

                    self.log_test("User Settings Created", True)

                    # Step 11: Test API access with new user
                    print("Step 11: Testing API access...")
                    new_user_token = login_test_response.json()["access_token"]
                    new_user_headers = {"Authorization": f"Bearer {new_user_token}"}

                    me_response = await client.get("/api/auth/me", headers=new_user_headers)
                    if me_response.status_code != 200:
                        self.log_test("API Access", False, f"Status: {me_response.status_code}")
                        return False

                    me_data = me_response.json()
                    if me_data["email"] != "newuser@scenario.com":
                        self.log_test("API Access", False, "Wrong user data returned")
                        return False

                    self.log_test("API Access", True)

                    print("\n✅ SCENARIO 1 COMPLETED SUCCESSFULLY!")
                    return True

                except Exception as e:
                    self.log_test("Scenario 1 Exception", False, str(e))
                    import traceback
                    traceback.print_exc()
                    return False
                finally:
                    await db_session.rollback()
                    break

    async def scenario_2_password_mismatch_handling(self):
        """
        Scenario 2: Password Mismatch Error Handling
        1. User attempts activation with wrong temporary password
        2. System provides helpful error message
        3. User tries again with correct password
        4. Activation succeeds
        """
        print("\n" + "="*60)
        print("🧪 SCENARIO 2: Password Mismatch Handling")
        print("="*60)

        async with AsyncClient(app=app, base_url="http://testserver") as client:
            async for db_session in get_db():
                try:
                    # Create test user
                    correct_temp_password = "CorrectTemp123"
                    user = User(
                        email="mismatch@scenario.com",
                        first_name="Mismatch",
                        last_name="Test",
                        hashed_password=auth_service.get_password_hash(correct_temp_password),
                        is_active=False,
                    )
                    db_session.add(user)
                    await db_session.commit()
                    await db_session.refresh(user)

                    # Step 1: Try with wrong password
                    print("Step 1: Testing wrong temporary password...")
                    wrong_activation_data = {
                        "userId": user.id,
                        "email": "mismatch@scenario.com",
                        "temporaryPassword": "WrongTemp123",
                        "newPassword": "NewSecure@123"
                    }

                    wrong_response = await client.post(
                        "/api/auth/activate",
                        json=wrong_activation_data
                    )

                    if wrong_response.status_code != 401:
                        self.log_test("Wrong Password Rejection", False, f"Expected 401, got {wrong_response.status_code}")
                        return False

                    error_detail = wrong_response.json().get("detail", "")
                    if "Invalid temporary password" not in error_detail:
                        self.log_test("Error Message Content", False, f"Wrong error message: {error_detail}")
                        return False

                    self.log_test("Wrong Password Rejection", True)
                    self.log_test("Error Message Content", True)

                    # Step 2: Verify user is still inactive
                    print("Step 2: Verifying user remains inactive...")
                    await db_session.refresh(user)
                    if user.is_active:
                        self.log_test("User Remains Inactive", False, "User was activated by wrong password")
                        return False

                    self.log_test("User Remains Inactive", True)

                    # Step 3: Try with correct password
                    print("Step 3: Testing correct temporary password...")
                    correct_activation_data = {
                        "userId": user.id,
                        "email": "mismatch@scenario.com",
                        "temporaryPassword": correct_temp_password,
                        "newPassword": "NewSecure@123"
                    }

                    correct_response = await client.post(
                        "/api/auth/activate",
                        json=correct_activation_data
                    )

                    if correct_response.status_code != 200:
                        self.log_test("Correct Password Success", False, f"Status: {correct_response.status_code}")
                        return False

                    self.log_test("Correct Password Success", True)

                    # Step 4: Verify activation succeeded
                    await db_session.refresh(user)
                    if not user.is_active:
                        self.log_test("Final Activation Status", False, "User not activated")
                        return False

                    self.log_test("Final Activation Status", True)

                    print("\n✅ SCENARIO 2 COMPLETED SUCCESSFULLY!")
                    return True

                except Exception as e:
                    self.log_test("Scenario 2 Exception", False, str(e))
                    return False
                finally:
                    await db_session.rollback()
                    break

    async def scenario_3_already_activated_user(self):
        """
        Scenario 3: Already Activated User
        1. User account is already active
        2. User tries to activate again
        3. System prevents duplicate activation
        4. User can still login normally
        """
        print("\n" + "="*60)
        print("🧪 SCENARIO 3: Already Activated User")
        print("="*60)

        async with AsyncClient(app=app, base_url="http://testserver") as client:
            async for db_session in get_db():
                try:
                    # Create already active user
                    active_user = User(
                        email="active@scenario.com",
                        first_name="Already",
                        last_name="Active",
                        hashed_password=auth_service.get_password_hash("ActivePassword123"),
                        is_active=True,  # Already active
                        last_login=datetime.utcnow(),
                    )
                    db_session.add(active_user)
                    await db_session.commit()
                    await db_session.refresh(active_user)

                    # Step 1: Try to activate already active user
                    print("Step 1: Attempting to activate already active user...")
                    activation_data = {
                        "userId": active_user.id,
                        "email": "active@scenario.com",
                        "temporaryPassword": "ActivePassword123",
                        "newPassword": "NewPassword123"
                    }

                    response = await client.post("/api/auth/activate", json=activation_data)

                    if response.status_code != 400:
                        self.log_test("Already Active Rejection", False, f"Expected 400, got {response.status_code}")
                        return False

                    error_detail = response.json().get("detail", "")
                    if "already activated" not in error_detail:
                        self.log_test("Already Active Error Message", False, f"Wrong error: {error_detail}")
                        return False

                    self.log_test("Already Active Rejection", True)
                    self.log_test("Already Active Error Message", True)

                    # Step 2: Verify user can still login normally
                    print("Step 2: Testing normal login...")
                    login_response = await client.post(
                        "/api/auth/login",
                        json={"email": "active@scenario.com", "password": "ActivePassword123"}
                    )

                    if login_response.status_code != 200:
                        self.log_test("Normal Login Works", False, f"Status: {login_response.status_code}")
                        return False

                    self.log_test("Normal Login Works", True)

                    print("\n✅ SCENARIO 3 COMPLETED SUCCESSFULLY!")
                    return True

                except Exception as e:
                    self.log_test("Scenario 3 Exception", False, str(e))
                    return False
                finally:
                    await db_session.rollback()
                    break

    async def scenario_4_company_admin_activation(self):
        """
        Scenario 4: Company Admin Activation
        1. Company admin account is created
        2. Admin activates their account
        3. Company becomes active when admin activates
        4. Admin can create other users
        """
        print("\n" + "="*60)
        print("🧪 SCENARIO 4: Company Admin Activation")
        print("="*60)

        async with AsyncClient(app=app, base_url="http://testserver") as client:
            async for db_session in get_db():
                try:
                    # Step 1: Create inactive company
                    print("Step 1: Creating inactive company...")
                    company = Company(
                        name="Admin Test Company",
                        email="admintest@company.com",
                        phone="03-9876-5432",
                        type="recruiter",
                        is_active=False  # Company starts inactive
                    )
                    db_session.add(company)
                    await db_session.commit()
                    await db_session.refresh(company)

                    # Step 2: Create company admin user
                    print("Step 2: Creating company admin...")
                    admin_role = Role(
                        name=UserRoleEnum.COMPANY_ADMIN,
                        description="Company Administrator"
                    )
                    db_session.add(admin_role)
                    await db_session.commit()
                    await db_session.refresh(admin_role)

                    temp_password = "AdminTemp456"
                    admin_user = User(
                        email="companyadmin@scenario.com",
                        first_name="Company",
                        last_name="Admin",
                        company_id=company.id,
                        hashed_password=auth_service.get_password_hash(temp_password),
                        is_active=False,
                        is_admin=True,
                        require_2fa=False,
                    )
                    db_session.add(admin_user)
                    await db_session.commit()
                    await db_session.refresh(admin_user)

                    user_role = UserRole(user_id=admin_user.id, role_id=admin_role.id)
                    db_session.add(user_role)
                    await db_session.commit()

                    # Step 3: Admin activates account
                    print("Step 3: Admin account activation...")
                    activation_data = {
                        "userId": admin_user.id,
                        "email": "companyadmin@scenario.com",
                        "temporaryPassword": temp_password,
                        "newPassword": "AdminSecure@789"
                    }

                    response = await client.post("/api/auth/activate", json=activation_data)

                    if response.status_code != 200:
                        self.log_test("Admin Activation", False, f"Status: {response.status_code}")
                        return False

                    self.log_test("Admin Activation", True)

                    # Step 4: Verify company is now active
                    print("Step 4: Verifying company activation...")
                    await db_session.refresh(company)
                    if not company.is_active:
                        self.log_test("Company Auto-Activation", False, "Company not activated")
                        return False

                    self.log_test("Company Auto-Activation", True)

                    # Step 5: Admin can login
                    print("Step 5: Testing admin login...")
                    login_response = await client.post(
                        "/api/auth/login",
                        json={"email": "companyadmin@scenario.com", "password": "AdminSecure@789"}
                    )

                    if login_response.status_code != 200:
                        self.log_test("Admin Login", False, f"Status: {login_response.status_code}")
                        return False

                    admin_token = login_response.json()["access_token"]
                    admin_headers = {"Authorization": f"Bearer {admin_token}"}
                    self.log_test("Admin Login", True)

                    # Step 6: Admin can create users
                    print("Step 6: Testing admin user creation...")
                    new_user_data = {
                        "email": "employee@scenario.com",
                        "first_name": "Employee",
                        "last_name": "User",
                        "company_id": company.id,
                        "roles": ["recruiter"]
                    }

                    create_response = await client.post(
                        "/api/admin/users",
                        json=new_user_data,
                        headers=admin_headers
                    )

                    if create_response.status_code != 201:
                        self.log_test("Admin User Creation", False, f"Status: {create_response.status_code}")
                        return False

                    self.log_test("Admin User Creation", True)

                    print("\n✅ SCENARIO 4 COMPLETED SUCCESSFULLY!")
                    return True

                except Exception as e:
                    self.log_test("Scenario 4 Exception", False, str(e))
                    return False
                finally:
                    await db_session.rollback()
                    break

    async def run_all_scenarios(self):
        """Run all test scenarios."""
        print("🚀 STARTING ACTIVATION SCENARIO TESTS")
        print("="*80)

        scenarios = [
            ("New User Creation and Activation", self.scenario_1_new_user_creation_and_activation),
            ("Password Mismatch Handling", self.scenario_2_password_mismatch_handling),
            ("Already Activated User", self.scenario_3_already_activated_user),
            ("Company Admin Activation", self.scenario_4_company_admin_activation),
        ]

        scenario_results = []

        for scenario_name, scenario_func in scenarios:
            print(f"\n🎯 Running: {scenario_name}")
            try:
                result = await scenario_func()
                scenario_results.append((scenario_name, result))
            except Exception as e:
                print(f"❌ Scenario failed with exception: {e}")
                scenario_results.append((scenario_name, False))

        # Print summary
        print("\n" + "="*80)
        print("📊 TEST SUMMARY")
        print("="*80)

        for scenario_name, success in scenario_results:
            status = "✅ PASS" if success else "❌ FAIL"
            print(f"{status}: {scenario_name}")

        print(f"\n📈 DETAILED RESULTS:")
        print(f"   Total Tests: {self.total_tests}")
        print(f"   Passed: {self.passed_tests}")
        print(f"   Failed: {self.total_tests - self.passed_tests}")
        print(f"   Success Rate: {(self.passed_tests/self.total_tests)*100:.1f}%")

        # Print failed tests
        failed_tests = [test for test in self.test_results if not test[1]]
        if failed_tests:
            print(f"\n❌ FAILED TESTS:")
            for test_name, _, message in failed_tests:
                print(f"   - {test_name}: {message}")

        overall_success = all(result for _, result in scenario_results)
        if overall_success:
            print(f"\n🎉 ALL SCENARIOS PASSED!")
        else:
            print(f"\n⚠️  SOME SCENARIOS FAILED - REVIEW ABOVE")

        return overall_success


if __name__ == "__main__":
    test_runner = ActivationScenarioTests()
    success = asyncio.run(test_runner.run_all_scenarios())
    sys.exit(0 if success else 1)