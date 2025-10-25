"""Script to check profile data distribution across users."""

import asyncio

from sqlalchemy import select

from app.database import get_db
from app.models.certification import ProfileCertification
from app.models.education import ProfileEducation
from app.models.project import ProfileProject
from app.models.skill import ProfileSkill
from app.models.user import User
from app.models.work_experience import ProfileWorkExperience


async def check_profile_data():
    """Check how profile data is distributed across users."""
    async for session in get_db():
        # Get all users
        users_result = await session.execute(select(User))
        users = users_result.scalars().all()
        print(f"\n[USERS] Total users in database: {len(users)}")

        # Check each profile table
        tables = [
            ("Skills", ProfileSkill),
            ("Work Experiences", ProfileWorkExperience),
            ("Educations", ProfileEducation),
            ("Certifications", ProfileCertification),
            ("Projects", ProfileProject),
        ]

        for table_name, model in tables:
            result = await session.execute(select(model))
            records = result.scalars().all()
            print(f"\n[{table_name.upper()}] {len(records)} total records")

            if records:
                # Group by user_id
                user_counts = {}
                for record in records:
                    user_id = record.user_id
                    user_counts[user_id] = user_counts.get(user_id, 0) + 1

                print("   Distribution across users:")
                for user_id, count in user_counts.items():
                    # Find user
                    user = next((u for u in users if u.id == user_id), None)
                    user_email = user.email if user else "Unknown"
                    print(f"     User {user_id} ({user_email}): {count} records")

        break


if __name__ == "__main__":
    asyncio.run(check_profile_data())
