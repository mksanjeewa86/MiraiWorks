"""
Quick verification script to check if global exam was created correctly.
Run after creating a global exam via UI.
"""

import asyncio

from sqlalchemy import select, text

from app.database import AsyncSessionLocal
from app.models.exam import Exam
from app.models.user import User


async def verify_global_exam():
    """Verify the latest exam created is a global exam."""

    print("\n" + "=" * 80)
    print("GLOBAL EXAM VERIFICATION")
    print("=" * 80)

    async with AsyncSessionLocal() as db:
        # Get the most recent exam
        result = await db.execute(select(Exam).order_by(Exam.id.desc()).limit(1))
        latest_exam = result.scalar_one_or_none()

        if not latest_exam:
            print("\n[ERROR] No exams found in database!")
            return False

        print("\n[Latest Exam Created]")
        print(f"ID: {latest_exam.id}")
        print(f"Title: {latest_exam.title}")
        print(
            f"Company ID: {latest_exam.company_id if latest_exam.company_id else 'NULL'}"
        )
        print(f"Is Public: {latest_exam.is_public}")
        print(f"Created At: {latest_exam.created_at}")

        # Check if it's a global exam
        is_global = latest_exam.company_id is None and latest_exam.is_public

        print("\n" + "-" * 80)
        if is_global:
            print("[SUCCESS] This is a GLOBAL EXAM!")
            print("  - company_id = NULL")
            print("  - is_public = True")
            print("  - Visible to all companies")
        else:
            print("[WARNING] This is NOT a global exam!")
            if latest_exam.company_id is not None:
                print(f"  - company_id = {latest_exam.company_id} (should be NULL)")
            if not latest_exam.is_public:
                print("  - is_public = False (should be True)")

        # Get exam statistics
        print("\n[Database Statistics]")
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
        total = 0
        for row in counts:
            exam_type = row.exam_type  # type: ignore[attr-defined]
            count = row.count  # type: ignore[attr-defined]
            print(f"  {exam_type:10s}: {count:3d} exams")
            total += count  # type: ignore[operator]
        print(f"  {'TOTAL':10s}: {total:3d} exams")

        # Check which users can see this exam
        print("\n[Visibility Test]")
        result = await db.execute(
            select(User).where(
                User.email.in_(["admin@miraiworks.com", "admin@techcorp.jp"])
            )
        )
        users = result.scalars().all()

        for user in users:
            # Simulate visibility check
            can_see = (
                latest_exam.company_id == user.company_id  # Own company
                or (latest_exam.company_id is None and latest_exam.is_public)  # Global
                or latest_exam.is_public  # Public
            )

            status = "[CAN SEE]" if can_see else "[CANNOT SEE]"
            print(f"  {status} {user.email:25s} (company_id: {user.company_id})")

        print("\n" + "=" * 80)

        return is_global


if __name__ == "__main__":
    success = asyncio.run(verify_global_exam())
    exit(0 if success else 1)
