#!/usr/bin/env python3
"""
Complete User Journey Tests
Tests the entire user lifecycle from creation through full system usage.
"""

import asyncio
import sys
from datetime import datetime, timedelta
from httpx import AsyncClient

# Add backend to path
sys.path.insert(0, './backend')

from app.main import app
from app.database import get_db
from app.models.user import User
from app.models.company import Company
from app.models.role import Role, UserRole
from app.utils.constants import UserRole as UserRoleEnum, CompanyType
from sqlalchemy import select
from sqlalchemy.orm import selectinload

class UserJourneyTester:
    """Test complete user journeys through the system."""

    def __init__(self):
        self.base_url = "http://testserver"
        self.admin_token = None
        self.company_admin_token = None
        self.test_results = []

    async def setup_test_environment(self):
        """Set up the test environment with necessary data."""
        print("🔧 Setting up test environment...")

        async for db_session in get_db():
            try:
                # Ensure we have a super admin for testing
                admin_result = await db_session.execute(
                    select(User)
                    .options(selectinload(User.user_roles).selectinload(UserRole.role))
                    .where(User.email == "admin@miraiworks.com")
                )
                admin_user = admin_result.scalar_one_or_none()

                if not admin_user:
                    print("❌ No super admin found. Please create one first.")
                    return False

                # Login as admin to get token
                async with AsyncClient(app=app, base_url=self.base_url) as client:
                    login_response = await client.post("/api/auth/login", json={
                        "email": "admin@miraiworks.com",
                        "password": "admin123"  # Assuming this is the admin password
                    })

                    if login_response.status_code == 200:
                        self.admin_token = login_response.json()["access_token"]
                        print("✅ Admin authentication successful")
                    else:
                        print(f"❌ Admin login failed: {login_response.status_code}")
                        return False

                return True

            except Exception as e:
                print(f"❌ Setup error: {e}")
                return False
            finally:
                break

    async def journey_1_complete_company_setup(self):
        """Test complete company setup and user creation journey."""
        print("\n" + "="*60)
        print("🚀 JOURNEY 1: Complete Company Setup")
        print("="*60)

        journey_success = True

        async with AsyncClient(app=app, base_url=self.base_url) as client:
            try:
                # Step 1: Super admin creates a new company
                print("Step 1: Creating new company...")
                company_data = {
                    "name": f"Test Company Journey {datetime.now().strftime('%H%M%S')}",
                    "type": "recruitment",
                    "description": "Test company for journey testing",
                    "website": "https://testcompany.com",
                    "phone": "+1-555-0199",
                    "email": "contact@testcompany.com",
                    "address": "123 Test Street, Test City, TC 12345"
                }

                company_response = await client.post(
                    "/api/admin/companies",
                    json=company_data,
                    headers={"Authorization": f"Bearer {self.admin_token}"}
                )

                if company_response.status_code != 201:
                    print(f"❌ Company creation failed: {company_response.status_code}")
                    print(f"Response: {company_response.json()}")
                    journey_success = False
                    return journey_success

                company = company_response.json()
                company_id = company["id"]
                print(f"✅ Company created: {company['name']} (ID: {company_id})")

                # Step 2: Super admin creates company admin
                print("Step 2: Creating company admin...")
                admin_data = {
                    "first_name": "Test",
                    "last_name": "Admin",
                    "email": f"admin{datetime.now().strftime('%H%M%S')}@testcompany.com",
                    "company_id": company_id,
                    "role": "company_admin"
                }

                admin_response = await client.post(
                    "/api/admin/users",
                    json=admin_data,
                    headers={"Authorization": f"Bearer {self.admin_token}"}
                )

                if admin_response.status_code != 201:
                    print(f"❌ Company admin creation failed: {admin_response.status_code}")
                    print(f"Response: {admin_response.json()}")
                    journey_success = False
                    return journey_success

                admin_user = admin_response.json()
                admin_email = admin_user["email"]
                admin_id = admin_user["id"]
                temp_password = admin_user["temporary_password"]
                print(f"✅ Company admin created: {admin_email} (ID: {admin_id})")
                print(f"   Temporary password: {temp_password}")

                # Step 3: Company admin activates account
                print("Step 3: Activating company admin account...")
                activation_data = {
                    "temporary_password": temp_password,
                    "new_password": "AdminPass@123",
                    "confirm_password": "AdminPass@123"
                }

                activation_response = await client.post(
                    f"/api/auth/activate/{admin_id}",
                    json=activation_data
                )

                if activation_response.status_code != 200:
                    print(f"❌ Activation failed: {activation_response.status_code}")
                    print(f"Response: {activation_response.json()}")
                    journey_success = False
                    return journey_success

                print("✅ Company admin account activated")

                # Step 4: Company admin logs in
                print("Step 4: Company admin login...")
                login_response = await client.post("/api/auth/login", json={
                    "email": admin_email,
                    "password": "AdminPass@123"
                })

                if login_response.status_code != 200:
                    print(f"❌ Login failed: {login_response.status_code}")
                    print(f"Response: {login_response.json()}")
                    journey_success = False
                    return journey_success

                admin_token = login_response.json()["access_token"]
                print("✅ Company admin login successful")

                # Step 5: Company admin creates recruiters
                print("Step 5: Creating recruiters...")
                recruiter_data = {
                    "first_name": "Test",
                    "last_name": "Recruiter",
                    "email": f"recruiter{datetime.now().strftime('%H%M%S')}@testcompany.com",
                    "company_id": company_id,
                    "role": "recruiter"
                }

                recruiter_response = await client.post(
                    "/api/admin/users",
                    json=recruiter_data,
                    headers={"Authorization": f"Bearer {admin_token}"}
                )

                if recruiter_response.status_code != 201:
                    print(f"❌ Recruiter creation failed: {recruiter_response.status_code}")
                    print(f"Response: {recruiter_response.json()}")
                    journey_success = False
                    return journey_success

                recruiter_user = recruiter_response.json()
                print(f"✅ Recruiter created: {recruiter_user['email']}")

                # Step 6: Test company admin restrictions
                print("Step 6: Testing company admin restrictions...")

                # Try to create user for different company (should fail)
                other_company_user_data = {
                    "first_name": "Unauthorized",
                    "last_name": "User",
                    "email": f"unauthorized{datetime.now().strftime('%H%M%S')}@other.com",
                    "company_id": 999,  # Non-existent company
                    "role": "recruiter"
                }

                unauthorized_response = await client.post(
                    "/api/admin/users",
                    json=other_company_user_data,
                    headers={"Authorization": f"Bearer {admin_token}"}
                )

                if unauthorized_response.status_code == 403:
                    print("✅ Company admin properly restricted from creating users for other companies")
                else:
                    print(f"❌ Security violation: Company admin could create user for other company")
                    journey_success = False

                # Try to assign super_admin role (should fail)
                super_admin_data = {
                    "first_name": "Unauthorized",
                    "last_name": "Super",
                    "email": f"super{datetime.now().strftime('%H%M%S')}@testcompany.com",
                    "company_id": company_id,
                    "role": "super_admin"
                }

                super_admin_response = await client.post(
                    "/api/admin/users",
                    json=super_admin_data,
                    headers={"Authorization": f"Bearer {admin_token}"}
                )

                if super_admin_response.status_code == 403:
                    print("✅ Company admin properly restricted from assigning super_admin role")
                else:
                    print(f"❌ Security violation: Company admin could assign super_admin role")
                    journey_success = False

                return journey_success

            except Exception as e:
                print(f"❌ Journey 1 error: {e}")
                import traceback
                traceback.print_exc()
                return False

    async def journey_2_activation_error_handling(self):
        """Test activation error handling and recovery."""
        print("\n" + "="*60)
        print("🔧 JOURNEY 2: Activation Error Handling")
        print("="*60)

        journey_success = True

        async with AsyncClient(app=app, base_url=self.base_url) as client:
            try:
                # Create a test user
                user_data = {
                    "first_name": "Error",
                    "last_name": "Test",
                    "email": f"errortest{datetime.now().strftime('%H%M%S')}@test.com",
                    "company_id": 1,  # Assuming company exists
                    "role": "recruiter"
                }

                user_response = await client.post(
                    "/api/admin/users",
                    json=user_data,
                    headers={"Authorization": f"Bearer {self.admin_token}"}
                )

                if user_response.status_code != 201:
                    print(f"❌ Test user creation failed: {user_response.status_code}")
                    return False

                user = user_response.json()
                user_id = user["id"]
                temp_password = user["temporary_password"]

                # Test 1: Wrong temporary password
                print("Test 1: Wrong temporary password...")
                wrong_activation = await client.post(
                    f"/api/auth/activate/{user_id}",
                    json={
                        "temporary_password": "wrongpassword",
                        "new_password": "NewPass@123",
                        "confirm_password": "NewPass@123"
                    }
                )

                if wrong_activation.status_code == 400:
                    print("✅ Wrong temporary password properly rejected")
                else:
                    print(f"❌ Wrong temporary password not handled correctly")
                    journey_success = False

                # Test 2: Password mismatch
                print("Test 2: Password mismatch...")
                mismatch_activation = await client.post(
                    f"/api/auth/activate/{user_id}",
                    json={
                        "temporary_password": temp_password,
                        "new_password": "NewPass@123",
                        "confirm_password": "DifferentPass@123"
                    }
                )

                if mismatch_activation.status_code == 400:
                    print("✅ Password mismatch properly rejected")
                else:
                    print(f"❌ Password mismatch not handled correctly")
                    journey_success = False

                # Test 3: Weak password
                print("Test 3: Weak password...")
                weak_activation = await client.post(
                    f"/api/auth/activate/{user_id}",
                    json={
                        "temporary_password": temp_password,
                        "new_password": "weak",
                        "confirm_password": "weak"
                    }
                )

                if weak_activation.status_code == 422:  # Validation error
                    print("✅ Weak password properly rejected")
                else:
                    print(f"❌ Weak password not handled correctly")
                    journey_success = False

                # Test 4: Non-existent user
                print("Test 4: Non-existent user...")
                nonexistent_activation = await client.post(
                    "/api/auth/activate/99999",
                    json={
                        "temporary_password": "anypassword",
                        "new_password": "NewPass@123",
                        "confirm_password": "NewPass@123"
                    }
                )

                if nonexistent_activation.status_code == 404:
                    print("✅ Non-existent user properly handled")
                else:
                    print(f"❌ Non-existent user not handled correctly")
                    journey_success = False

                # Test 5: Successful activation after errors
                print("Test 5: Successful activation after errors...")
                success_activation = await client.post(
                    f"/api/auth/activate/{user_id}",
                    json={
                        "temporary_password": temp_password,
                        "new_password": "FinalPass@123",
                        "confirm_password": "FinalPass@123"
                    }
                )

                if success_activation.status_code == 200:
                    print("✅ Successful activation after errors")

                    # Test 6: Double activation attempt
                    print("Test 6: Double activation attempt...")
                    double_activation = await client.post(
                        f"/api/auth/activate/{user_id}",
                        json={
                            "temporary_password": temp_password,
                            "new_password": "AnotherPass@123",
                            "confirm_password": "AnotherPass@123"
                        }
                    )

                    if double_activation.status_code == 400:
                        print("✅ Double activation properly prevented")
                    else:
                        print(f"❌ Double activation not handled correctly")
                        journey_success = False

                else:
                    print(f"❌ Final activation failed: {success_activation.status_code}")
                    journey_success = False

                return journey_success

            except Exception as e:
                print(f"❌ Journey 2 error: {e}")
                import traceback
                traceback.print_exc()
                return False

    async def journey_3_complete_workflow_integration(self):
        """Test complete workflow from user creation to system usage."""
        print("\n" + "="*60)
        print("🔄 JOURNEY 3: Complete Workflow Integration")
        print("="*60)

        journey_success = True

        async with AsyncClient(app=app, base_url=self.base_url) as client:
            try:
                # Create and activate a complete user workflow
                workflow_email = f"workflow{datetime.now().strftime('%H%M%S')}@test.com"

                # Step 1: Create user
                print("Step 1: Creating user for workflow test...")
                user_data = {
                    "first_name": "Workflow",
                    "last_name": "User",
                    "email": workflow_email,
                    "company_id": 1,
                    "role": "recruiter"
                }

                user_response = await client.post(
                    "/api/admin/users",
                    json=user_data,
                    headers={"Authorization": f"Bearer {self.admin_token}"}
                )

                if user_response.status_code != 201:
                    print(f"❌ Workflow user creation failed")
                    return False

                user = user_response.json()
                user_id = user["id"]
                temp_password = user["temporary_password"]
                print(f"✅ User created: {workflow_email}")

                # Step 2: Activate account
                print("Step 2: Activating account...")
                activation_response = await client.post(
                    f"/api/auth/activate/{user_id}",
                    json={
                        "temporary_password": temp_password,
                        "new_password": "WorkflowPass@123",
                        "confirm_password": "WorkflowPass@123"
                    }
                )

                if activation_response.status_code != 200:
                    print(f"❌ Account activation failed")
                    return False

                print("✅ Account activated successfully")

                # Step 3: Login with new credentials
                print("Step 3: Logging in with new credentials...")
                login_response = await client.post("/api/auth/login", json={
                    "email": workflow_email,
                    "password": "WorkflowPass@123"
                })

                if login_response.status_code != 200:
                    print(f"❌ Login with new credentials failed")
                    return False

                login_data = login_response.json()
                user_token = login_data["access_token"]
                print("✅ Login successful")

                # Step 4: Test authenticated endpoints
                print("Step 4: Testing authenticated access...")

                # Test /api/auth/me
                me_response = await client.get(
                    "/api/auth/me",
                    headers={"Authorization": f"Bearer {user_token}"}
                )

                if me_response.status_code == 200:
                    me_data = me_response.json()
                    if me_data["email"] == workflow_email:
                        print("✅ /api/auth/me working correctly")
                    else:
                        print("❌ /api/auth/me returned wrong user data")
                        journey_success = False
                else:
                    print(f"❌ /api/auth/me failed: {me_response.status_code}")
                    journey_success = False

                # Step 5: Test token refresh
                print("Step 5: Testing token refresh...")
                refresh_token = login_data.get("refresh_token")
                if refresh_token:
                    refresh_response = await client.post(
                        "/api/auth/refresh",
                        headers={"Authorization": f"Bearer {refresh_token}"}
                    )

                    if refresh_response.status_code == 200:
                        print("✅ Token refresh working correctly")
                    else:
                        print(f"❌ Token refresh failed: {refresh_response.status_code}")
                        journey_success = False
                else:
                    print("⚠️ No refresh token provided (may be expected)")

                # Step 6: Test logout
                print("Step 6: Testing logout...")
                logout_response = await client.post(
                    "/api/auth/logout",
                    headers={"Authorization": f"Bearer {user_token}"}
                )

                if logout_response.status_code in [200, 204]:
                    print("✅ Logout successful")
                else:
                    print(f"❌ Logout failed: {logout_response.status_code}")
                    journey_success = False

                return journey_success

            except Exception as e:
                print(f"❌ Journey 3 error: {e}")
                import traceback
                traceback.print_exc()
                return False

    async def run_all_journeys(self):
        """Run all user journey tests."""
        print("🚀 STARTING COMPLETE USER JOURNEY TESTS")
        print("="*60)

        # Setup
        setup_success = await self.setup_test_environment()
        if not setup_success:
            print("❌ Test environment setup failed. Aborting journey tests.")
            return False

        # Run journeys
        journeys = [
            ("Complete Company Setup", self.journey_1_complete_company_setup),
            ("Activation Error Handling", self.journey_2_activation_error_handling),
            ("Complete Workflow Integration", self.journey_3_complete_workflow_integration),
        ]

        all_success = True
        results = []

        for journey_name, journey_func in journeys:
            print(f"\n🏃‍♂️ Running: {journey_name}")
            try:
                success = await journey_func()
                results.append((journey_name, success))
                if success:
                    print(f"✅ {journey_name}: PASSED")
                else:
                    print(f"❌ {journey_name}: FAILED")
                    all_success = False
            except Exception as e:
                print(f"❌ {journey_name}: ERROR - {e}")
                results.append((journey_name, False))
                all_success = False

        # Final report
        print("\n" + "="*60)
        print("📊 JOURNEY TEST RESULTS")
        print("="*60)

        for journey_name, success in results:
            status = "✅ PASSED" if success else "❌ FAILED"
            print(f"{status}: {journey_name}")

        print("\n" + "="*60)
        if all_success:
            print("🎉 ALL USER JOURNEYS COMPLETED SUCCESSFULLY!")
            print("🚀 The activation system is fully functional!")
        else:
            print("⚠️ Some user journeys failed. Please review the errors above.")
        print("="*60)

        return all_success

async def main():
    """Main entry point for user journey tests."""
    tester = UserJourneyTester()
    success = await tester.run_all_journeys()
    return 0 if success else 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)