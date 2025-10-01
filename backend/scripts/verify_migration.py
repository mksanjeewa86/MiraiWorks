#!/usr/bin/env python3
"""
Verification script for jobs to positions migration.
Run this after the database migration to verify data integrity.
"""

import asyncio
import os
import sys
from typing import Any

# Add the parent directory to the path so we can import from app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text

from app.database import AsyncSessionLocal


async def verify_tables_exist() -> dict[str, Any]:
    """Verify that the new tables exist and old tables are gone."""
    results = {
        "tables_renamed": False,
        "positions_table_exists": False,
        "position_applications_table_exists": False,
        "jobs_table_exists": False,
        "job_applications_table_exists": False,
        "error": None
    }

    try:
        async with AsyncSessionLocal() as db:
            # Check if new tables exist
            positions_check = await db.execute(
                text("SELECT COUNT(*) FROM information_schema.tables WHERE table_name = 'positions'")
            )
            results["positions_table_exists"] = positions_check.scalar() > 0

            position_applications_check = await db.execute(
                text("SELECT COUNT(*) FROM information_schema.tables WHERE table_name = 'position_applications'")
            )
            results["position_applications_table_exists"] = position_applications_check.scalar() > 0

            # Check if old tables are gone
            jobs_check = await db.execute(
                text("SELECT COUNT(*) FROM information_schema.tables WHERE table_name = 'jobs'")
            )
            results["jobs_table_exists"] = jobs_check.scalar() > 0

            job_applications_check = await db.execute(
                text("SELECT COUNT(*) FROM information_schema.tables WHERE table_name = 'job_applications'")
            )
            results["job_applications_table_exists"] = job_applications_check.scalar() > 0

            # Overall success check
            results["tables_renamed"] = (
                results["positions_table_exists"] and
                results["position_applications_table_exists"] and
                not results["jobs_table_exists"] and
                not results["job_applications_table_exists"]
            )

    except Exception as e:
        results["error"] = str(e)

    return results


async def verify_data_integrity() -> dict[str, Any]:
    """Verify that data was preserved during migration."""
    results = {
        "data_preserved": False,
        "positions_count": 0,
        "position_applications_count": 0,
        "foreign_keys_working": False,
        "error": None
    }

    try:
        async with AsyncSessionLocal() as db:
            # Count records in new tables
            positions_count = await db.execute(text("SELECT COUNT(*) FROM positions"))
            results["positions_count"] = positions_count.scalar()

            applications_count = await db.execute(text("SELECT COUNT(*) FROM position_applications"))
            results["position_applications_count"] = applications_count.scalar()

            # Test foreign key relationship
            fk_test = await db.execute(
                text("""
                    SELECT COUNT(*)
                    FROM position_applications pa
                    JOIN positions p ON pa.position_id = p.id
                """)
            )
            fk_count = fk_test.scalar()
            results["foreign_keys_working"] = fk_count == results["position_applications_count"]

            results["data_preserved"] = results["positions_count"] > 0

    except Exception as e:
        results["error"] = str(e)

    return results


async def verify_indexes() -> dict[str, Any]:
    """Verify that indexes were updated correctly."""
    results = {
        "indexes_updated": False,
        "new_indexes_exist": [],
        "old_indexes_exist": [],
        "error": None
    }

    try:
        async with AsyncSessionLocal() as db:
            # Check for new indexes
            new_indexes = [
                'idx_positions_company_status',
                'idx_positions_published',
                'idx_positions_location_type',
                'idx_positions_experience_remote',
                'idx_positions_featured_status',
                'idx_applications_position_status'
            ]

            for index_name in new_indexes:
                index_check = await db.execute(
                    text(f"SELECT COUNT(*) FROM information_schema.statistics WHERE index_name = '{index_name}'")
                )
                if index_check.scalar() > 0:
                    results["new_indexes_exist"].append(index_name)

            # Check for old indexes (should not exist)
            old_indexes = [
                'idx_jobs_company_status',
                'idx_jobs_published',
                'idx_jobs_location_type',
                'idx_jobs_experience_remote',
                'idx_jobs_featured_status',
                'idx_applications_job_status'
            ]

            for index_name in old_indexes:
                index_check = await db.execute(
                    text(f"SELECT COUNT(*) FROM information_schema.statistics WHERE index_name = '{index_name}'")
                )
                if index_check.scalar() > 0:
                    results["old_indexes_exist"].append(index_name)

            results["indexes_updated"] = (
                len(results["new_indexes_exist"]) == len(new_indexes) and
                len(results["old_indexes_exist"]) == 0
            )

    except Exception as e:
        results["error"] = str(e)

    return results


async def main():
    """Run all verification checks."""
    print("🔍 Verifying jobs to positions migration...")
    print("=" * 50)

    # Check 1: Tables renamed
    print("\n1. Checking table renaming...")
    table_results = await verify_tables_exist()

    if table_results["error"]:
        print(f"❌ Error checking tables: {table_results['error']}")
        return False

    if table_results["tables_renamed"]:
        print("✅ Tables successfully renamed")
        print(f"   - positions table exists: {table_results['positions_table_exists']}")
        print(f"   - position_applications table exists: {table_results['position_applications_table_exists']}")
        print(f"   - jobs table removed: {not table_results['jobs_table_exists']}")
        print(f"   - job_applications table removed: {not table_results['job_applications_table_exists']}")
    else:
        print("❌ Table renaming failed")
        print(f"   - positions table exists: {table_results['positions_table_exists']}")
        print(f"   - position_applications table exists: {table_results['position_applications_table_exists']}")
        print(f"   - jobs table still exists: {table_results['jobs_table_exists']}")
        print(f"   - job_applications table still exists: {table_results['job_applications_table_exists']}")
        return False

    # Check 2: Data integrity
    print("\n2. Checking data integrity...")
    data_results = await verify_data_integrity()

    if data_results["error"]:
        print(f"❌ Error checking data: {data_results['error']}")
        return False

    if data_results["data_preserved"] and data_results["foreign_keys_working"]:
        print("✅ Data integrity verified")
        print(f"   - Positions count: {data_results['positions_count']}")
        print(f"   - Position applications count: {data_results['position_applications_count']}")
        print(f"   - Foreign key relationships working: {data_results['foreign_keys_working']}")
    else:
        print("❌ Data integrity issues found")
        print(f"   - Positions count: {data_results['positions_count']}")
        print(f"   - Position applications count: {data_results['position_applications_count']}")
        print(f"   - Foreign key relationships working: {data_results['foreign_keys_working']}")
        return False

    # Check 3: Indexes
    print("\n3. Checking indexes...")
    index_results = await verify_indexes()

    if index_results["error"]:
        print(f"❌ Error checking indexes: {index_results['error']}")
        return False

    if index_results["indexes_updated"]:
        print("✅ Indexes successfully updated")
        print(f"   - New indexes created: {len(index_results['new_indexes_exist'])}")
        print(f"   - Old indexes removed: {len(index_results['old_indexes_exist']) == 0}")
    else:
        print("❌ Index update issues found")
        print(f"   - New indexes created: {index_results['new_indexes_exist']}")
        print(f"   - Old indexes still exist: {index_results['old_indexes_exist']}")
        return False

    print("\n" + "=" * 50)
    print("🎉 Migration verification completed successfully!")
    print("\nNext steps:")
    print("1. Test the new positions API endpoints")
    print("2. Run backend tests: python -m pytest app/tests/test_positions.py -v")
    print("3. Update frontend to use new positions API")

    return True


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
