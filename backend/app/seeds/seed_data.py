"""
MiraiWorks Database Seeding

Simple orchestrator that runs all seed modules in the correct order.
This is the main entry point for database seeding.

USAGE:
    cd backend
    PYTHONPATH=. python app/seeds/seed_data.py
"""

import asyncio
import os

# Set environment to avoid conflicts
os.environ.setdefault("ENVIRONMENT", "development")

from app.database import AsyncSessionLocal
from sqlalchemy import delete

# Import seed functions
from app.seeds.users_and_companies import seed_auth_data
from app.seeds.personality_test_questions import seed_mbti_questions
from app.seeds.test_messages_interviews_jobs import seed_sample_data
from app.seeds.assessment_and_exam_system import seed_exam_data
from app.seeds.resume_data import seed_resume_data

# Import models for cleanup
from app.models import User, Company, Role, UserRole, UserSettings, CompanyProfile
from app.models.message import Message
from app.models.interview import Interview
from app.models.position import Position
from app.models.mbti_model import MBTIQuestion
from app.models.calendar_integration import SyncedEvent, ExternalCalendarAccount
from app.models.calendar_connection import CalendarConnection
from app.models.exam import Exam, ExamQuestion, ExamAssignment
from app.models.resume import Resume, WorkExperience, Education, Skill, Project, Certification, Language, Reference, ResumeSection


async def clear_database(db):
    """Clear all existing data in correct order."""
    print("Clearing existing data...")

    # Clear in dependency order (children first, parents last)
    await db.execute(delete(MBTIQuestion))
    print("   - Cleared MBTI questions")

    await db.execute(delete(ExamAssignment))
    print("   - Cleared exam assignments")

    await db.execute(delete(ExamQuestion))
    print("   - Cleared exam questions")

    await db.execute(delete(Exam))
    print("   - Cleared exams")

    # Clear resume system data
    await db.execute(delete(ResumeSection))
    print("   - Cleared resume sections")

    await db.execute(delete(Reference))
    print("   - Cleared references")

    await db.execute(delete(Language))
    print("   - Cleared languages")

    await db.execute(delete(Certification))
    print("   - Cleared certifications")

    await db.execute(delete(Project))
    print("   - Cleared projects")

    await db.execute(delete(Skill))
    print("   - Cleared skills")

    await db.execute(delete(Education))
    print("   - Cleared education")

    await db.execute(delete(WorkExperience))
    print("   - Cleared work experience")

    await db.execute(delete(Resume))
    print("   - Cleared resumes")

    await db.execute(delete(SyncedEvent))
    print("   - Cleared synced events")

    await db.execute(delete(CalendarConnection))
    print("   - Cleared calendar connections")

    await db.execute(delete(ExternalCalendarAccount))
    print("   - Cleared external calendar accounts")

    await db.execute(delete(Message))
    print("   - Cleared messages")

    await db.execute(delete(Interview))
    print("   - Cleared interviews")

    await db.execute(delete(Position))
    print("   - Cleared positions")

    await db.execute(delete(CompanyProfile))
    print("   - Cleared company profiles")

    await db.execute(delete(UserSettings))
    print("   - Cleared user settings")

    await db.execute(delete(UserRole))
    print("   - Cleared user roles")

    await db.execute(delete(User))
    print("   - Cleared users")

    await db.execute(delete(Company))
    print("   - Cleared companies")

    await db.execute(delete(Role))
    print("   - Cleared roles")

    await db.commit()
    print("   > Database cleared!")


async def run_seeds():
    """Run all seed functions in order."""
    print("=" * 60)
    print("MiraiWorks Database Seeding")
    print("=" * 60)
    print("Creating fresh seed data for all modules...")
    print("=" * 60)

    async with AsyncSessionLocal() as db:
        try:
            # 1. Clear existing data
            await clear_database(db)

            # 2. Seed authentication data (roles, companies, users)
            print("\nStep 1: Authentication Data")
            auth_result = await seed_auth_data(db)

            # 3. Seed MBTI questions
            print("\nStep 2: MBTI Questions")
            mbti_count = await seed_mbti_questions(db)

            # 4. Seed sample data (messages, interviews, positions)
            print("\nStep 3: Sample Application Data")
            sample_result = await seed_sample_data(db, auth_result)

            # 5. Seed exam system data
            print("\nStep 4: Assessment and Exam System")
            exam_result = await seed_exam_data(db, auth_result)

            # 6. Seed resume system data
            print("\nStep 5: Resume System")
            resume_result = await seed_resume_data(db, auth_result)

            # 7. Summary
            print("\n" + "=" * 60)
            print("SUCCESS: All seed data created!")
            print("=" * 60)
            print("SUMMARY:")
            print(f"   - Roles: {auth_result['roles']}")
            print(f"   - Companies: {auth_result['companies']}")
            print(f"   - Users: {auth_result['users']}")
            print(f"   - User Roles: {auth_result['user_roles']}")
            print(f"   - User Settings: {auth_result['user_settings']}")
            print(f"   - Company Profiles: {auth_result['company_profiles']}")
            print(f"   - MBTI Questions: {mbti_count}")
            print(f"   - Messages: {sample_result['messages']}")
            print(f"   - Interviews: {sample_result['interviews']}")
            print(f"   - Positions: {sample_result['positions']}")
            print(f"   - Exams: {exam_result['exams']}")
            print(f"   - Exam Questions: {exam_result['questions']}")
            print(f"   - Exam Assignments: {exam_result['assignments']}")
            print(f"   - Resumes: {resume_result['resumes']}")
            print(f"   - Resume Formats: {', '.join(resume_result['formats'])}")

            print("\nESSENTIAL LOGIN CREDENTIALS:")
            print("=" * 60)
            print("ADMIN ACCESS:")
            print("   Email: admin@miraiworks.com")
            print("   Password: password")

            print("\nCANDIDATE ACCESS:")
            print("   Email: candidate@example.com")
            print("   Password: password")

            print("\nRECRUITER ACCESS:")
            print("   Email: recruiter@miraiworks.com")
            print("   Password: password")

            print("\nReady to use!")
            print("MBTI questions: Ready for testing")
            print("User roles: Properly assigned")
            print("Company data: Complete")

        except Exception as e:
            await db.rollback()
            print(f"\nERROR: {e}")
            print("\nTroubleshooting:")
            print("1. Ensure the database is running")
            print("2. Check database connection settings")
            print("3. Run database migrations: alembic upgrade head")
            raise


async def main():
    """Main entry point."""
    await run_seeds()


if __name__ == "__main__":
    asyncio.run(main())