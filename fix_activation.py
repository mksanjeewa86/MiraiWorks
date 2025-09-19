#!/usr/bin/env python3
"""
Comprehensive Activation Fix Utility
This script will diagnose and fix activation issues automatically.
"""

import asyncio
import sys
import secrets
import string
from datetime import datetime

# Add backend to path
sys.path.insert(0, './backend')

from app.database import get_db
from app.models.user import User
from app.models.company import Company
from app.models.role import Role, UserRole
from app.models.user_settings import UserSettings
from app.services.auth_service import auth_service
from app.services.email_service import email_service
from app.utils.constants import UserRole as UserRoleEnum
from sqlalchemy import select, update
from sqlalchemy.orm import selectinload

async def fix_user_activation(email: str, desired_password: str = "Password@123"):
    """Fix activation issues for a specific user."""

    print("=" * 60)
    print("🔧 ACTIVATION FIX UTILITY")
    print("=" * 60)
    print(f"Target Email: {email}")
    print(f"Desired Password: {desired_password}")
    print()

    async for db_session in get_db():
        try:
            # Step 1: Find the user
            print("Step 1: Locating user...")
            result = await db_session.execute(
                select(User)
                .options(
                    selectinload(User.company),
                    selectinload(User.user_roles).selectinload(UserRole.role)
                )
                .where(User.email == email)
            )
            user = result.scalar_one_or_none()

            if not user:
                print(f"❌ ERROR: No user found with email '{email}'")
                print("📝 SOLUTION: Create the user first, then run this script.")
                return False

            print(f"✅ User found: {user.first_name} {user.last_name}")
            print(f"   - User ID: {user.id}")
            print(f"   - Email: {user.email}")
            print(f"   - Active: {user.is_active}")
            print(f"   - Admin: {user.is_admin}")
            print(f"   - Company: {user.company.name if user.company else 'None'}")
            print(f"   - Has Password: {bool(user.hashed_password)}")
            print()

            # Step 2: Check current status
            print("Step 2: Analyzing account status...")

            if user.is_active:
                print("⚠️  WARNING: User account is already activated!")
                print(f"💡 SOLUTION: User should login normally at /login")
                print(f"   Email: {email}")
                print(f"   Try existing password or request password reset")

                # Ask if we should update password anyway
                print("\n🔄 Updating password for already active user...")
                hashed_password = auth_service.get_password_hash(desired_password)
                await db_session.execute(
                    update(User)
                    .where(User.id == user.id)
                    .values(hashed_password=hashed_password)
                )
                await db_session.commit()
                print(f"✅ Password updated! User can now login with: {desired_password}")
                return True

            if not user.hashed_password:
                print("❌ ISSUE: User has no temporary password set")
                print("🔧 FIXING: Setting temporary password...")
            else:
                print("✅ User has temporary password set")
                print("🔧 FIXING: Replacing with new password for activation...")

            # Step 3: Set new password and activate
            print("\nStep 3: Activating account...")

            hashed_password = auth_service.get_password_hash(desired_password)
            update_values = {
                "hashed_password": hashed_password,
                "is_active": True,
                "last_login": datetime.utcnow(),
            }

            # Add default phone if missing
            if not user.phone:
                update_values["phone"] = "+1-555-0100"
                print("📞 Added default phone number")

            await db_session.execute(
                update(User)
                .where(User.id == user.id)
                .values(**update_values)
            )

            # Step 4: Create user settings if missing
            print("Step 4: Setting up user preferences...")

            existing_settings = await db_session.execute(
                select(UserSettings).where(UserSettings.user_id == user.id)
            )
            if not existing_settings.scalar_one_or_none():
                default_settings = UserSettings(
                    user_id=user.id,
                    job_title="User" if not user.is_admin else "Administrator",
                    bio=f"Welcome to {user.company.name if user.company else 'MiraiWorks'}!",
                    email_notifications=True,
                    push_notifications=True,
                    sms_notifications=False,
                    interview_reminders=True,
                    application_updates=True,
                    message_notifications=True,
                    language="en",
                    timezone="America/New_York",
                    date_format="MM/DD/YYYY",
                )
                db_session.add(default_settings)
                print("⚙️  Created default user settings")

            # Step 5: Activate company if needed
            if user.is_admin and user.company_id and user.company:
                if not user.company.is_active:
                    await db_session.execute(
                        update(Company)
                        .where(Company.id == user.company_id)
                        .values(is_active=True)
                    )
                    print(f"🏢 Activated company: {user.company.name}")

            await db_session.commit()

            # Step 6: Success message
            print("\n" + "=" * 60)
            print("🎉 ACTIVATION COMPLETED SUCCESSFULLY!")
            print("=" * 60)
            print(f"✅ User: {user.first_name} {user.last_name}")
            print(f"✅ Email: {email}")
            print(f"✅ Password: {desired_password}")
            print(f"✅ Status: Active")
            print(f"✅ Login URL: /login")
            print()
            print("📝 USER CAN NOW:")
            print("   1. Go to the login page")
            print(f"   2. Enter email: {email}")
            print(f"   3. Enter password: {desired_password}")
            print("   4. Access the dashboard")
            print("=" * 60)

            return True

        except Exception as e:
            print(f"❌ ERROR during activation: {e}")
            import traceback
            traceback.print_exc()
            await db_session.rollback()
            return False
        finally:
            break

async def create_temp_password_for_user(email: str):
    """Generate a new temporary password for activation."""

    print("=" * 60)
    print("🔑 TEMPORARY PASSWORD GENERATOR")
    print("=" * 60)
    print(f"Target Email: {email}")
    print()

    async for db_session in get_db():
        try:
            # Find user
            result = await db_session.execute(
                select(User).where(User.email == email)
            )
            user = result.scalar_one_or_none()

            if not user:
                print(f"❌ ERROR: No user found with email '{email}'")
                return False

            if user.is_active:
                print("⚠️  User is already activated! Use regular login.")
                return False

            # Generate new temporary password
            temp_password = ''.join(
                secrets.choice(string.ascii_letters + string.digits)
                for _ in range(12)
            )

            # Update user with temporary password
            hashed_password = auth_service.get_password_hash(temp_password)
            await db_session.execute(
                update(User)
                .where(User.id == user.id)
                .values(hashed_password=hashed_password)
            )
            await db_session.commit()

            print("✅ NEW TEMPORARY PASSWORD GENERATED!")
            print("=" * 40)
            print(f"Email: {email}")
            print(f"Temporary Password: {temp_password}")
            print(f"User ID: {user.id}")
            print(f"Activation URL: /activate/{user.id}")
            print("=" * 40)
            print("📝 INSTRUCTIONS:")
            print("1. Use the activation page with the new temporary password")
            print("2. Enter your desired new password")
            print("3. Complete the activation process")

            return True

        except Exception as e:
            print(f"❌ ERROR: {e}")
            await db_session.rollback()
            return False
        finally:
            break

async def diagnose_user(email: str):
    """Diagnose activation issues for a user."""

    print("=" * 60)
    print("🔍 USER ACTIVATION DIAGNOSIS")
    print("=" * 60)
    print(f"Target Email: {email}")
    print()

    async for db_session in get_db():
        try:
            result = await db_session.execute(
                select(User)
                .options(
                    selectinload(User.company),
                    selectinload(User.user_roles).selectinload(UserRole.role)
                )
                .where(User.email == email)
            )
            user = result.scalar_one_or_none()

            if not user:
                print(f"❌ No user found with email '{email}'")
                print("📝 Action: Create user account first")
                return

            print("👤 USER DETAILS:")
            print(f"   ID: {user.id}")
            print(f"   Name: {user.first_name} {user.last_name}")
            print(f"   Email: {user.email}")
            print(f"   Active: {user.is_active}")
            print(f"   Admin: {user.is_admin}")
            print(f"   Phone: {user.phone or 'Not set'}")
            print(f"   Created: {user.created_at}")
            print(f"   Updated: {user.updated_at}")
            print()

            print("🏢 COMPANY DETAILS:")
            if user.company:
                print(f"   Name: {user.company.name}")
                print(f"   Type: {user.company.type}")
                print(f"   Active: {user.company.is_active}")
            else:
                print("   No company assigned")
            print()

            print("🔐 PASSWORD STATUS:")
            print(f"   Has Password: {bool(user.hashed_password)}")
            if user.hashed_password:
                print("   Password Hash: [SET]")
            else:
                print("   Password Hash: [NOT SET]")
            print()

            print("👥 ROLES:")
            if user.user_roles:
                for user_role in user.user_roles:
                    print(f"   - {user_role.role.name}: {user_role.role.description}")
            else:
                print("   No roles assigned")
            print()

            print("📋 DIAGNOSIS:")
            if user.is_active:
                print("   ✅ Account is already activated")
                print("   💡 User should use regular login page")
            elif not user.hashed_password:
                print("   ❌ No temporary password set")
                print("   💡 Need to generate temporary password")
            else:
                print("   ⚠️  Account ready for activation")
                print("   💡 User should be able to activate normally")

            return user

        except Exception as e:
            print(f"❌ ERROR: {e}")
            return None
        finally:
            break

# Main execution
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage:")
        print("  python fix_activation.py fix <email> [password]")
        print("  python fix_activation.py temp <email>")
        print("  python fix_activation.py diagnose <email>")
        print()
        print("Examples:")
        print("  python fix_activation.py fix ssss@aaa.com Password@123")
        print("  python fix_activation.py temp ssss@aaa.com")
        print("  python fix_activation.py diagnose ssss@aaa.com")
        sys.exit(1)

    command = sys.argv[1]

    if command == "fix":
        email = sys.argv[2] if len(sys.argv) > 2 else "ssss@aaa.com"
        password = sys.argv[3] if len(sys.argv) > 3 else "Password@123"
        success = asyncio.run(fix_user_activation(email, password))
        sys.exit(0 if success else 1)

    elif command == "temp":
        email = sys.argv[2] if len(sys.argv) > 2 else "ssss@aaa.com"
        success = asyncio.run(create_temp_password_for_user(email))
        sys.exit(0 if success else 1)

    elif command == "diagnose":
        email = sys.argv[2] if len(sys.argv) > 2 else "ssss@aaa.com"
        asyncio.run(diagnose_user(email))
        sys.exit(0)

    else:
        print(f"Unknown command: {command}")
        sys.exit(1)