"""
Test script to verify the exam endpoint works correctly.
"""
import asyncio

from sqlalchemy import select

from app.crud.exam import exam as exam_crud
from app.database import AsyncSessionLocal
from app.models.user import User


async def test_exam_retrieval():
    """Test exam retrieval for admin user."""
    async with AsyncSessionLocal() as db:
        # Get the admin user
        result = await db.execute(select(User).where(User.email == "admin@techcorp.jp"))
        user = result.scalar_one_or_none()

        if not user:
            print("[ERROR] User admin@techcorp.jp not found")
            return

        print(f"[OK] User found: {user.email}")
        print(f"     Company ID: {user.company_id}")

        # Test 1: Get exams for this user's company
        print(f"\nTest 1: Getting exams for company_id={user.company_id}")
        exams = await exam_crud.get_by_company(
            db=db, company_id=user.company_id, skip=0, limit=20
        )

        print(f"[OK] Found {len(exams)} exam(s)")
        for exam in exams:
            print(f"     - ID={exam.id}, Title='{exam.title}', Status={exam.status}")

        # Test 2: Get all exams (system admin view)
        print("\nTest 2: Getting all exams (company_id=None)")
        all_exams = await exam_crud.get_by_company(
            db=db, company_id=None, skip=0, limit=20
        )

        print(f"[OK] Found {len(all_exams)} exam(s) across all companies")

        if len(exams) == 0:
            print("\n[WARNING] No exams found for company_id=89")
            print("          This might be why the frontend is showing no exams")
        else:
            print("\n[SUCCESS] Exams exist and should be visible in frontend")


if __name__ == "__main__":
    asyncio.run(test_exam_retrieval())
