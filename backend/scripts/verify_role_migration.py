"""
Verification script for user role migration.
Checks that all roles have been properly updated in the database.
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.config import settings
from app.models.role import Role, UserRole
from app.models.user import User


async def verify_roles():
    """Verify that roles have been migrated correctly."""
    # Create async engine
    engine = create_async_engine(
        settings.DATABASE_URL,
        echo=False,
    )

    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        # Check roles table
        print("\n[*] Checking Roles Table...")
        print("=" * 60)

        result = await session.execute(select(Role))
        roles = result.scalars().all()

        expected_roles = {"system_admin", "admin", "member", "candidate"}
        actual_roles = {role.name for role in roles}

        print(f"Expected roles: {expected_roles}")
        print(f"Actual roles:   {actual_roles}")

        if expected_roles == actual_roles:
            print("[OK] All expected roles present!")
        else:
            missing = expected_roles - actual_roles
            extra = actual_roles - expected_roles
            if missing:
                print(f"[ERROR] Missing roles: {missing}")
            if extra:
                print(f"[WARN] Extra roles: {extra}")

        # Display role details
        print("\n[*] Role Details:")
        print("-" * 60)
        for role in sorted(roles, key=lambda r: r.id):
            print(f"  {role.id}: {role.name:15s} - {role.description}")

        # Check user_roles distribution
        print("\n[*] User Role Distribution:")
        print("=" * 60)

        result = await session.execute(select(Role.name, Role.id))
        role_map = {row[1]: row[0] for row in result}

        result = await session.execute(select(UserRole.role_id, UserRole.user_id))
        user_roles_data = result.all()

        role_counts = {}
        for role_id, user_id in user_roles_data:
            role_name = role_map.get(role_id, "unknown")
            role_counts[role_name] = role_counts.get(role_name, 0) + 1

        for role_name in sorted(role_counts.keys()):
            count = role_counts[role_name]
            print(f"  {role_name:15s}: {count} user(s)")

        # Check for any old role references
        print("\n[*] Checking for Old Role References...")
        print("=" * 60)

        old_roles = {"super_admin", "company_admin", "recruiter", "employer"}
        found_old = actual_roles.intersection(old_roles)

        if found_old:
            print(f"[ERROR] Found old roles still in database: {found_old}")
            print("   Migration may not have completed successfully!")
        else:
            print("[OK] No old role references found!")

        # Sample user checks
        print("\n[*] Sample User Checks:")
        print("=" * 60)

        result = await session.execute(
            select(User, Role)
            .join(UserRole, User.id == UserRole.user_id)
            .join(Role, UserRole.role_id == Role.id)
            .limit(5)
        )

        for user, role in result:
            print(f"  {user.email:30s} → {role.name}")

        print("\n" + "=" * 60)
        print("[OK] Verification complete!")
        print("=" * 60)

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(verify_roles())
