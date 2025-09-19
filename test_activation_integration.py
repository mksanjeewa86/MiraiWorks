#!/usr/bin/env python3
"""
Integration Tests for Complete Activation Flow
Tests the integration between frontend, backend, database, and email services.
"""

import asyncio
import sys
import json
import secrets
import string
from datetime import datetime, timedelta

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


class ActivationIntegrationTests:
    """Integration tests for complete activation system."""

    def __init__(self):
        self.client = None
        self.db_session = None

    async def setup(self):
        """Set up test environment."""
        self.client = AsyncClient(app=app, base_url="http://testserver")

        # Get database session
        async for db_session in get_db():
            self.db_session = db_session
            break

    async def cleanup(self):
        """Clean up test environment."""
        if self.db_session:
            await self.db_session.rollback()
        if self.client:
            await self.client.aclose()

    async def test_complete_user_lifecycle(self):
        """Test complete user lifecycle from creation to dashboard access."""
        print("🔄 Testing Complete User Lifecycle")
        print("-" * 50)

        try:
            # 1. Create company and admin
            company = Company(
                name="Integration Test Co",
                email="integration@test.com",
                phone="03-1111-2222",
                type="employer"
            )
            self.db_session.add(company)
            await self.db_session.commit()
            await self.db_session.refresh(company)
            print("✅ Company created")

            # Create admin role
            admin_role = Role(
                name=UserRoleEnum.COMPANY_ADMIN,
                description="Company Administrator"
            )
            self.db_session.add(admin_role)
            await self.db_session.commit()
            await self.db_session.refresh(admin_role)

            # Create admin user
            admin = User(
                email="admin@integration.com",
                first_name="Integration",
                last_name="Admin",
                company_id=company.id,
                hashed_password=auth_service.get_password_hash("AdminPass123"),
                is_active=True,
                is_admin=True,
                require_2fa=False,
            )
            self.db_session.add(admin)
            await self.db_session.commit()
            await self.db_session.refresh(admin)

            user_role = UserRole(user_id=admin.id, role_id=admin_role.id)
            self.db_session.add(user_role)
            await self.db_session.commit()
            print("✅ Admin user created")

            # 2. Admin authentication
            login_response = await self.client.post(
                "/api/auth/login",
                json={"email": "admin@integration.com", "password": "AdminPass123"}
            )
            assert login_response.status_code == 200
            admin_token = login_response.json()["access_token"]
            admin_headers = {"Authorization": f"Bearer {admin_token}"}
            print("✅ Admin authenticated")

            # 3. Admin creates new user
            new_user_data = {
                "email": "newuser@integration.com",
                "first_name": "New",
                "last_name": "User",
                "company_id": company.id,
                "roles": ["employer"]
            }

            create_response = await self.client.post(
                "/api/admin/users",
                json=new_user_data,
                headers=admin_headers
            )
            assert create_response.status_code == 201
            created_user = create_response.json()
            new_user_id = created_user["id"]
            print("✅ New user created via API")

            # 4. Verify user is inactive and has temporary password
            user_result = await self.db_session.execute(
                select(User).where(User.id == new_user_id)
            )
            new_user = user_result.scalar_one()
            assert not new_user.is_active
            assert new_user.hashed_password is not None
            print("✅ User properly configured for activation")

            # 5. Simulate receiving temporary password (normally from email)
            temp_password = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(12))
            hashed_temp = auth_service.get_password_hash(temp_password)
            await self.db_session.execute(
                update(User).where(User.id == new_user_id).values(hashed_password=hashed_temp)
            )
            await self.db_session.commit()
            print(f"✅ Temporary password set: {temp_password}")

            # 6. User activates account
            activation_data = {
                "userId": new_user_id,
                "email": "newuser@integration.com",
                "temporaryPassword": temp_password,
                "newPassword": "UserSecure@123"
            }

            activation_response = await self.client.post(
                "/api/auth/activate",
                json=activation_data
            )
            assert activation_response.status_code == 200
            activation_result = activation_response.json()
            assert activation_result["success"] is True
            print("✅ Account activated successfully")

            # 7. Verify user can login
            user_login_response = await self.client.post(
                "/api/auth/login",
                json={"email": "newuser@integration.com", "password": "UserSecure@123"}
            )
            assert user_login_response.status_code == 200
            user_token = user_login_response.json()["access_token"]
            user_headers = {"Authorization": f"Bearer {user_token}"}
            print("✅ User can login with new password")

            # 8. Test API access
            me_response = await self.client.get("/api/auth/me", headers=user_headers)
            assert me_response.status_code == 200
            user_info = me_response.json()
            assert user_info["email"] == "newuser@integration.com"
            assert user_info["is_active"] is True
            print("✅ User can access protected APIs")

            # 9. Verify user settings were created
            settings_result = await self.db_session.execute(
                select(UserSettings).where(UserSettings.user_id == new_user_id)
            )
            user_settings = settings_result.scalar_one()
            assert user_settings is not None
            print("✅ User settings created")

            # 10. Test token refresh
            refresh_token = user_login_response.json()["refresh_token"]
            refresh_response = await self.client.post(
                "/api/auth/refresh",
                json={"refresh_token": refresh_token}
            )
            assert refresh_response.status_code == 200
            print("✅ Token refresh works")

            print("\n🎉 Complete User Lifecycle Test PASSED!")
            return True

        except Exception as e:
            print(f"\n❌ Complete User Lifecycle Test FAILED: {e}")
            import traceback
            traceback.print_exc()
            return False

    async def test_activation_error_scenarios(self):
        """Test various error scenarios in activation flow."""
        print("\n🚨 Testing Activation Error Scenarios")
        print("-" * 50)

        try:
            # Test 1: Non-existent user
            activation_data = {
                "userId": 99999,
                "email": "nonexistent@test.com",
                "temporaryPassword": "temp123",
                "newPassword": "new123"
            }

            response = await self.client.post("/api/auth/activate", json=activation_data)
            assert response.status_code == 404
            print("✅ Non-existent user properly rejected")

            # Test 2: Create user for further tests
            test_user = User(
                email="errortest@integration.com",
                first_name="Error",
                last_name="Test",
                hashed_password=auth_service.get_password_hash("CorrectTemp123"),
                is_active=False,
            )
            self.db_session.add(test_user)
            await self.db_session.commit()
            await self.db_session.refresh(test_user)

            # Test 3: Email mismatch
            wrong_email_data = {
                "userId": test_user.id,
                "email": "wrong@test.com",
                "temporaryPassword": "CorrectTemp123",
                "newPassword": "NewSecure@123"
            }

            response = await self.client.post("/api/auth/activate", json=wrong_email_data)
            assert response.status_code == 400
            assert "Email does not match" in response.json()["detail"]
            print("✅ Email mismatch properly rejected")

            # Test 4: Wrong temporary password
            wrong_password_data = {
                "userId": test_user.id,
                "email": "errortest@integration.com",
                "temporaryPassword": "WrongTemp123",
                "newPassword": "NewSecure@123"
            }

            response = await self.client.post("/api/auth/activate", json=wrong_password_data)
            assert response.status_code == 401
            assert "Invalid temporary password" in response.json()["detail"]
            print("✅ Wrong temporary password properly rejected")

            # Test 5: Short new password
            short_password_data = {
                "userId": test_user.id,
                "email": "errortest@integration.com",
                "temporaryPassword": "CorrectTemp123",
                "newPassword": "short"
            }

            response = await self.client.post("/api/auth/activate", json=short_password_data)
            assert response.status_code == 422
            print("✅ Short password properly rejected")

            # Test 6: Successful activation
            correct_data = {
                "userId": test_user.id,
                "email": "errortest@integration.com",
                "temporaryPassword": "CorrectTemp123",
                "newPassword": "NewSecure@123"
            }

            response = await self.client.post("/api/auth/activate", json=correct_data)
            assert response.status_code == 200
            print("✅ Correct data accepted")

            # Test 7: Try to activate again (should fail)
            response = await self.client.post("/api/auth/activate", json=correct_data)
            assert response.status_code == 400
            assert "already activated" in response.json()["detail"]
            print("✅ Duplicate activation properly rejected")

            print("\n🎉 Activation Error Scenarios Test PASSED!")
            return True

        except Exception as e:
            print(f"\n❌ Activation Error Scenarios Test FAILED: {e}")
            import traceback
            traceback.print_exc()
            return False

    async def test_authentication_flow_integration(self):
        """Test complete authentication flow integration."""
        print("\n🔐 Testing Authentication Flow Integration")
        print("-" * 50)

        try:
            # 1. Create test user
            test_user = User(
                email="authtest@integration.com",
                first_name="Auth",
                last_name="Test",
                hashed_password=auth_service.get_password_hash("TempAuth123"),
                is_active=False,
            )
            self.db_session.add(test_user)
            await self.db_session.commit()
            await self.db_session.refresh(test_user)

            # 2. Activate user
            activation_data = {
                "userId": test_user.id,
                "email": "authtest@integration.com",
                "temporaryPassword": "TempAuth123",
                "newPassword": "AuthSecure@123"
            }

            activation_response = await self.client.post("/api/auth/activate", json=activation_data)
            assert activation_response.status_code == 200
            activation_result = activation_response.json()

            # Verify tokens are returned
            assert "access_token" in activation_result
            assert "refresh_token" in activation_result
            assert "expires_in" in activation_result
            print("✅ Activation returns proper authentication tokens")

            # 3. Test immediate API access with activation tokens
            access_token = activation_result["access_token"]
            headers = {"Authorization": f"Bearer {access_token}"}

            me_response = await self.client.get("/api/auth/me", headers=headers)
            assert me_response.status_code == 200
            user_data = me_response.json()
            assert user_data["email"] == "authtest@integration.com"
            print("✅ Activation tokens work for immediate API access")

            # 4. Test login with new password
            login_response = await self.client.post(
                "/api/auth/login",
                json={"email": "authtest@integration.com", "password": "AuthSecure@123"}
            )
            assert login_response.status_code == 200
            print("✅ Login works with new password")

            # 5. Test that old temporary password no longer works
            old_login_response = await self.client.post(
                "/api/auth/login",
                json={"email": "authtest@integration.com", "password": "TempAuth123"}
            )
            assert old_login_response.status_code == 401
            print("✅ Old temporary password no longer works")

            # 6. Test token refresh
            refresh_token = activation_result["refresh_token"]
            refresh_response = await self.client.post(
                "/api/auth/refresh",
                json={"refresh_token": refresh_token}
            )
            assert refresh_response.status_code == 200
            refresh_result = refresh_response.json()
            assert "access_token" in refresh_result
            print("✅ Token refresh works with activation tokens")

            # 7. Test logout
            logout_response = await self.client.post(
                "/api/auth/logout",
                json={"refresh_token": refresh_token}
            )
            assert logout_response.status_code == 200
            print("✅ Logout works")

            # 8. Test that tokens are invalidated after logout
            invalidated_refresh_response = await self.client.post(
                "/api/auth/refresh",
                json={"refresh_token": refresh_token}
            )
            assert invalidated_refresh_response.status_code == 401
            print("✅ Tokens properly invalidated after logout")

            print("\n🎉 Authentication Flow Integration Test PASSED!")
            return True

        except Exception as e:
            print(f"\n❌ Authentication Flow Integration Test FAILED: {e}")
            import traceback
            traceback.print_exc()
            return False

    async def test_database_consistency(self):
        """Test database consistency during activation process."""
        print("\n💾 Testing Database Consistency")
        print("-" * 50)

        try:
            # 1. Create test user with specific state
            original_created_at = datetime.utcnow() - timedelta(hours=1)
            test_user = User(
                email="dbtest@integration.com",
                first_name="DB",
                last_name="Test",
                hashed_password=auth_service.get_password_hash("DBTemp123"),
                is_active=False,
                is_admin=False,
                require_2fa=False,
                created_at=original_created_at,
                phone=None,  # Test default phone assignment
            )
            self.db_session.add(test_user)
            await self.db_session.commit()
            await self.db_session.refresh(test_user)
            print("✅ Test user created with specific state")

            # Record original state
            original_password_hash = test_user.hashed_password

            # 2. Activate user
            activation_data = {
                "userId": test_user.id,
                "email": "dbtest@integration.com",
                "temporaryPassword": "DBTemp123",
                "newPassword": "DBSecure@123"
            }

            activation_response = await self.client.post("/api/auth/activate", json=activation_data)
            assert activation_response.status_code == 200
            print("✅ User activated")

            # 3. Verify database changes
            await self.db_session.refresh(test_user)

            # Check activation status
            assert test_user.is_active is True
            print("✅ User is_active set to True")

            # Check password change
            assert test_user.hashed_password != original_password_hash
            new_password_valid = auth_service.verify_password("DBSecure@123", test_user.hashed_password)
            assert new_password_valid is True
            print("✅ Password properly updated")

            # Check last_login set
            assert test_user.last_login is not None
            assert test_user.last_login > original_created_at
            print("✅ last_login timestamp set")

            # Check default phone added
            assert test_user.phone == "+1-555-0100"
            print("✅ Default phone number added")

            # Check created_at preserved
            assert test_user.created_at == original_created_at
            print("✅ Original created_at preserved")

            # Check updated_at changed
            assert test_user.updated_at is not None
            assert test_user.updated_at > original_created_at
            print("✅ updated_at timestamp updated")

            # 4. Verify user settings created
            settings_result = await self.db_session.execute(
                select(UserSettings).where(UserSettings.user_id == test_user.id)
            )
            user_settings = settings_result.scalar_one()
            assert user_settings is not None
            assert user_settings.email_notifications is True
            assert user_settings.language == "en"
            print("✅ User settings created with defaults")

            # 5. Test user with existing phone
            existing_phone_user = User(
                email="phonetest@integration.com",
                first_name="Phone",
                last_name="Test",
                hashed_password=auth_service.get_password_hash("PhoneTemp123"),
                is_active=False,
                phone="+81-90-1234-5678",  # Existing phone
            )
            self.db_session.add(existing_phone_user)
            await self.db_session.commit()
            await self.db_session.refresh(existing_phone_user)

            phone_activation_data = {
                "userId": existing_phone_user.id,
                "email": "phonetest@integration.com",
                "temporaryPassword": "PhoneTemp123",
                "newPassword": "PhoneSecure@123"
            }

            phone_response = await self.client.post("/api/auth/activate", json=phone_activation_data)
            assert phone_response.status_code == 200

            await self.db_session.refresh(existing_phone_user)
            assert existing_phone_user.phone == "+81-90-1234-5678"  # Preserved
            print("✅ Existing phone number preserved")

            print("\n🎉 Database Consistency Test PASSED!")
            return True

        except Exception as e:
            print(f"\n❌ Database Consistency Test FAILED: {e}")
            import traceback
            traceback.print_exc()
            return False

    async def run_all_integration_tests(self):
        """Run all integration tests."""
        print("🚀 STARTING ACTIVATION INTEGRATION TESTS")
        print("=" * 80)

        await self.setup()

        tests = [
            ("Complete User Lifecycle", self.test_complete_user_lifecycle),
            ("Activation Error Scenarios", self.test_activation_error_scenarios),
            ("Authentication Flow Integration", self.test_authentication_flow_integration),
            ("Database Consistency", self.test_database_consistency),
        ]

        results = []
        for test_name, test_func in tests:
            print(f"\n🎯 Running: {test_name}")
            try:
                result = await test_func()
                results.append((test_name, result))
            except Exception as e:
                print(f"❌ Test failed with exception: {e}")
                results.append((test_name, False))

        await self.cleanup()

        # Print summary
        print("\n" + "=" * 80)
        print("📊 INTEGRATION TESTS SUMMARY")
        print("=" * 80)

        passed = 0
        total = len(results)

        for test_name, success in results:
            status = "✅ PASS" if success else "❌ FAIL"
            print(f"{status}: {test_name}")
            if success:
                passed += 1

        print(f"\nResults: {passed}/{total} tests passed ({(passed/total)*100:.1f}%)")

        overall_success = all(result for _, result in results)
        if overall_success:
            print("🎉 ALL INTEGRATION TESTS PASSED!")
        else:
            print("⚠️  SOME INTEGRATION TESTS FAILED")

        return overall_success


if __name__ == "__main__":
    test_runner = ActivationIntegrationTests()
    success = asyncio.run(test_runner.run_all_integration_tests())
    sys.exit(0 if success else 1)