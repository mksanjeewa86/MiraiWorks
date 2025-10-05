"""
Fix Resume Enum Values in Database

This script updates existing resume data from uppercase to lowercase enum values
to match the updated enum definitions in constants.py
"""

import asyncio
import sys

sys.path.append(".")

from sqlalchemy import text

from app.database import get_db


async def fix_resume_enum_values():
    """Update resume enum values from uppercase to lowercase."""
    print("Fixing resume enum values in database...")

    async for db in get_db():
        try:
            # Check current values
            print("\n=== BEFORE UPDATE ===")
            result = await db.execute(text("SELECT DISTINCT status FROM resumes"))
            statuses = [row[0] for row in result.fetchall()]
            print(f"Status values: {statuses}")

            result = await db.execute(text("SELECT DISTINCT visibility FROM resumes"))
            visibilities = [row[0] for row in result.fetchall()]
            print(f"Visibility values: {visibilities}")

            # Update status values
            print("\nUpdating status values...")
            status_updates = [
                (
                    "UPDATE resumes SET status = 'draft' WHERE status = 'DRAFT'",
                    "DRAFT → draft",
                ),
                (
                    "UPDATE resumes SET status = 'published' WHERE status = 'PUBLISHED'",
                    "PUBLISHED → published",
                ),
                (
                    "UPDATE resumes SET status = 'archived' WHERE status = 'ARCHIVED'",
                    "ARCHIVED → archived",
                ),
            ]

            for update_sql, description in status_updates:
                result = await db.execute(text(update_sql))
                if result.rowcount > 0:
                    print(f"  SUCCESS {description} - {result.rowcount} rows updated")
                else:
                    print(f"  SKIP {description} - no rows to update")

            # Update visibility values
            print("\nUpdating visibility values...")
            visibility_updates = [
                (
                    "UPDATE resumes SET visibility = 'private' WHERE visibility = 'PRIVATE'",
                    "PRIVATE → private",
                ),
                (
                    "UPDATE resumes SET visibility = 'public' WHERE visibility = 'PUBLIC'",
                    "PUBLIC → public",
                ),
                (
                    "UPDATE resumes SET visibility = 'unlisted' WHERE visibility = 'UNLISTED'",
                    "UNLISTED → unlisted",
                ),
            ]

            for update_sql, description in visibility_updates:
                result = await db.execute(text(update_sql))
                if result.rowcount > 0:
                    print(f"  SUCCESS {description} - {result.rowcount} rows updated")
                else:
                    print(f"  SKIP {description} - no rows to update")

            # Commit changes
            await db.commit()
            print("\nSUCCESS: All changes committed successfully!")

            # Verify changes
            print("\n=== AFTER UPDATE ===")
            result = await db.execute(text("SELECT DISTINCT status FROM resumes"))
            statuses = [row[0] for row in result.fetchall()]
            print(f"Status values: {statuses}")

            result = await db.execute(text("SELECT DISTINCT visibility FROM resumes"))
            visibilities = [row[0] for row in result.fetchall()]
            print(f"Visibility values: {visibilities}")

            # Count affected records
            result = await db.execute(text("SELECT COUNT(*) FROM resumes"))
            total_resumes = result.scalar()
            print(f"\nTotal resumes processed: {total_resumes}")

            print("\nSUCCESS: Resume enum values updated successfully!")
            print("All database values now match the lowercase enum definitions.")

        except Exception as e:
            print(f"\nERROR: {e}")
            await db.rollback()
            raise

        break


if __name__ == "__main__":
    asyncio.run(fix_resume_enum_values())
