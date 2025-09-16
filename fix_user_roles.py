#!/usr/bin/env python3
"""
Fix user roles in the database to enable messaging functionality.
Based on the test patterns in backend/app/tests/test_direct_messages.py
"""
import asyncio
import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from app.database import get_db
from app.models.user import User
from app.models.role import Role, UserRole
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


async def setup_roles_and_users():
    """Set up roles and assign them to existing users."""

    # Get database session
    async for db in get_db():
        try:
            print("=== SETTING UP USER ROLES ===")

            # 1. Ensure roles exist
            print("\n1. Creating roles if they don't exist...")

            # Check/create super_admin role
            result = await db.execute(select(Role).where(Role.name == "super_admin"))
            super_admin_role = result.scalar_one_or_none()
            if not super_admin_role:
                super_admin_role = Role(name="super_admin", description="Super Administrator")
                db.add(super_admin_role)
                await db.commit()
                await db.refresh(super_admin_role)
                print("   ✓ Created super_admin role")
            else:
                print("   ✓ super_admin role already exists")

            # Check/create company_admin role
            result = await db.execute(select(Role).where(Role.name == "company_admin"))
            company_admin_role = result.scalar_one_or_none()
            if not company_admin_role:
                company_admin_role = Role(name="company_admin", description="Company Administrator")
                db.add(company_admin_role)
                await db.commit()
                await db.refresh(company_admin_role)
                print("   ✓ Created company_admin role")
            else:
                print("   ✓ company_admin role already exists")

            # 2. Get all users
            print("\n2. Getting existing users...")
            result = await db.execute(select(User))
            users = result.scalars().all()
            print(f"   Found {len(users)} users")

            # 3. Assign roles based on email patterns (like the real system would)
            print("\n3. Assigning roles to users...")

            for user in users:
                print(f"\n   Processing user: {user.full_name} ({user.email})")

                # Check if user already has a role
                result = await db.execute(
                    select(UserRole).where(UserRole.user_id == user.id)
                )
                existing_role = result.scalar_one_or_none()

                if existing_role:
                    print(f"      ✓ User already has role assigned")
                    continue

                # Assign role based on email pattern
                if user.email == "admin@example.com" or "superadmin" in user.email:
                    # Assign super_admin role
                    user_role = UserRole(user_id=user.id, role_id=super_admin_role.id)
                    db.add(user_role)
                    print(f"      ✓ Assigned super_admin role")
                elif "admin" in user.email or user.email.endswith("@company.com"):
                    # Assign company_admin role
                    user_role = UserRole(user_id=user.id, role_id=company_admin_role.id)
                    db.add(user_role)
                    print(f"      ✓ Assigned company_admin role")
                else:
                    # For demo purposes, make first user super_admin if no pattern matches
                    if user.id == users[0].id:
                        user_role = UserRole(user_id=user.id, role_id=super_admin_role.id)
                        db.add(user_role)
                        print(f"      ✓ Assigned super_admin role (first user fallback)")
                    else:
                        print(f"      - No role pattern match, skipping")

            # Commit all changes
            await db.commit()
            print("\n✓ All role assignments committed to database")

            # 4. Verify assignments
            print("\n4. Verifying role assignments...")
            for user in users:
                result = await db.execute(
                    select(UserRole, Role).join(Role).where(UserRole.user_id == user.id)
                )
                user_role_info = result.first()

                if user_role_info:
                    role_name = user_role_info[1].name
                    print(f"   ✓ {user.full_name} ({user.email}) → {role_name}")
                else:
                    print(f"   - {user.full_name} ({user.email}) → NO ROLE")

            print("\n=== ROLE SETUP COMPLETE ===")

        except Exception as e:
            print(f"Error: {e}")
            await db.rollback()
        finally:
            await db.close()
        break


if __name__ == "__main__":
    asyncio.run(setup_roles_and_users())