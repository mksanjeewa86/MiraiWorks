"""
Simple verification script for user role migration using direct SQL.
Checks that all roles have been properly updated in the database.
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from app.config import settings


async def verify_roles():
    """Verify that roles have been migrated correctly using raw SQL."""
    # Create async engine
    engine = create_async_engine(
        settings.DATABASE_URL,
        echo=False,
    )

    async with engine.connect() as conn:
        # Check roles table
        print("\n[*] Checking Roles Table...")
        print("=" * 60)

        result = await conn.execute(
            text("SELECT id, name, description FROM roles ORDER BY id")
        )
        roles = result.fetchall()

        expected_roles = {"system_admin", "admin", "member", "candidate"}
        actual_roles = {role[1] for role in roles}

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
        for role_id, role_name, role_desc in sorted(roles, key=lambda r: r[0]):
            print(f"  {role_id}: {role_name:15s} - {role_desc}")

        # Check user_roles distribution
        print("\n[*] User Role Distribution:")
        print("=" * 60)

        result = await conn.execute(
            text(
                """
            SELECT r.name, COUNT(ur.user_id) as user_count
            FROM roles r
            LEFT JOIN user_roles ur ON r.id = ur.role_id
            GROUP BY r.id, r.name
            ORDER BY r.name
        """
            )
        )
        role_counts = result.fetchall()

        for role_name, count in role_counts:
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
        print("\n[*] Sample User Checks (first 5):")
        print("=" * 60)

        result = await conn.execute(
            text(
                """
            SELECT u.email, r.name as role_name
            FROM users u
            JOIN user_roles ur ON u.id = ur.user_id
            JOIN roles r ON ur.role_id = r.id
            LIMIT 5
        """
            )
        )
        user_roles = result.fetchall()

        for email, role_name in user_roles:
            print(f"  {email:30s} -> {role_name}")

        print("\n" + "=" * 60)
        print("[OK] Verification complete!")
        print("=" * 60)

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(verify_roles())
