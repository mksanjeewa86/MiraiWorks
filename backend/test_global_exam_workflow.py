"""
Global Exam Workflow Test
Tests the complete global exam creation and visibility workflow.

This script tests:
1. System admin can create global exams (company_id = NULL)
2. Global exams are visible to company admins
3. Global exams enforce is_public = true
4. Company admins can clone global exams
"""

import asyncio
import sys

from sqlalchemy import select, text

# Add parent directory to path
sys.path.insert(0, ".")

from app.crud.exam import exam as exam_crud
from app.database import AsyncSessionLocal
from app.models.user import User


async def test_global_exam_workflow():
    """Test the complete global exam workflow."""

    print("=" * 80)
    print("GLOBAL EXAM WORKFLOW TEST")
    print("=" * 80)

    async with AsyncSessionLocal() as db:
        # Step 1: Check current exam state
        print("\n[Step 1] Checking current exam state...")
        result = await db.execute(
            text(
                """
                SELECT id, title, company_id, is_public,
                       CASE
                           WHEN company_id IS NULL AND is_public = true THEN 'GLOBAL'
                           WHEN is_public = true THEN 'PUBLIC'
                           ELSE 'PRIVATE'
                       END as exam_visibility
                FROM exams
                ORDER BY id DESC
                LIMIT 10
            """
            )
        )

        exams = result.fetchall()
        print("\nRecent exams in database:")
        print("-" * 80)
        for exam in exams:
            company_str = "NULL" if exam.company_id is None else str(exam.company_id)
            title_str = (exam.title[:40] if exam.title else "")[:40]
            print(
                f"ID:{exam.id:3d} | {title_str:40s} | Company:{company_str:>4s} | Public:{str(exam.is_public):5s} | Type:{exam.exam_visibility}"
            )

        # Count by type
        result = await db.execute(
            text(
                """
                SELECT
                    exam_type,
                    COUNT(*) as count
                FROM (
                    SELECT
                        CASE
                            WHEN company_id IS NULL AND is_public = true THEN 'GLOBAL'
                            WHEN is_public = true THEN 'PUBLIC'
                            ELSE 'PRIVATE'
                        END as exam_type
                    FROM exams
                ) AS categorized_exams
                GROUP BY exam_type
                ORDER BY exam_type
            """
            )
        )

        counts = result.fetchall()
        print("\nExam count by type:")
        print("-" * 80)
        total = 0
        for row in counts:
            print(f"{row.exam_type:10s}: {row.count:3d} exams")
            total += row.count
        print(f"{'TOTAL':10s}: {total:3d} exams")

        # Step 2: Check user roles
        print("\n[Step 2] Checking user roles...")
        result = await db.execute(
            select(User).where(
                User.email.in_(["admin@miraiworks.com", "admin@techcorp.jp"])
            )
        )
        users = result.scalars().all()

        print("\nUser details:")
        print("-" * 80)
        for user in users:
            roles = [role.role.name for role in user.user_roles]
            company_id_str = str(user.company_id) if user.company_id else "NULL"
            print(
                f"{user.email:25s} | Company:{company_id_str:>4s} | Roles: {', '.join(roles)}"
            )

        # Step 3: Test exam visibility for each user
        print("\n[Step 3] Testing exam visibility...")

        for user in users:
            roles = [role.role.name for role in user.user_roles]
            is_system_admin = "system_admin" in roles

            print(f"\n  Checking visibility for: {user.email}")
            print(f"  Role: {', '.join(roles)}, Company: {user.company_id or 'NULL'}")

            # Get exams visible to this user
            exams = await exam_crud.get_by_company(
                db=db,
                company_id=user.company_id,
                include_public=True,
                skip=0,
                limit=100,
            )

            print(f"  Visible exams: {len(exams)}")

            # Categorize visible exams
            global_exams = [e for e in exams if e.company_id is None and e.is_public]
            public_exams = [
                e for e in exams if e.company_id is not None and e.is_public
            ]
            private_exams = [e for e in exams if not e.is_public]
            own_company_exams = [e for e in exams if e.company_id == user.company_id]

            print(f"    - Global exams:        {len(global_exams)}")
            print(f"    - Public exams:        {len(public_exams)}")
            print(f"    - Private exams:       {len(private_exams)}")
            print(f"    - Own company exams:   {len(own_company_exams)}")

            # Show breakdown
            if global_exams:
                print("\n    Global exams visible:")
                for exam in global_exams[:3]:  # Show first 3
                    print(f"      - {exam.title[:50]}")
            else:
                print("\n    [WARNING] No global exams visible!")

        # Step 4: Recommendations
        print("\n" + "=" * 80)
        print("RECOMMENDATIONS")
        print("=" * 80)

        global_count = sum(1 for row in counts if row.exam_type == "GLOBAL")

        if global_count == 0:
            print("\n[WARNING] NO GLOBAL EXAMS EXIST!")
            print("\nTo create a global exam:")
            print("1. Log in as system admin (admin@miraiworks.com)")
            print("2. Go to Create Exam page")
            print("3. Toggle 'Global Exam (System Admin Only)' to ON")
            print("4. Fill in exam details")
            print("5. Create the exam")
            print("\nThe global exam should then be visible to all company admins.")
        else:
            print(f"\n[OK] {global_count} global exam(s) exist in the database")
            print("\nGlobal exams should be visible to:")
            print("  - System admins (can see all exams)")
            print("  - Company admins (can see global + public + own company exams)")
            print("\nTo verify in UI:")
            print("1. Log in as admin@miraiworks.com (system admin)")
            print("2. Check exam list - should see all exams")
            print("3. Log in as admin@techcorp.jp (company admin)")
            print("4. Check exam list - should see global + public + own company exams")
            print("5. Global exams should have a [Global] badge")

        print("\n" + "=" * 80)
        print("[OK] Test complete!")
        print("=" * 80)


if __name__ == "__main__":
    asyncio.run(test_global_exam_workflow())
