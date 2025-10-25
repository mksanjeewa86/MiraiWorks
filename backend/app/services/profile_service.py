"""Profile service for calculating profile completeness and other profile operations."""

from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import profile as profile_crud
from app.models.user import User


class ProfileCompletenessCalculator:
    """Calculate profile completeness percentage based on filled sections."""

    # Weights for each section (total should be 100)
    WEIGHTS = {
        "basic_info": 20,  # Name, email, etc. (from User model)
        "work_experience": 25,
        "education": 15,
        "skills": 15,
        "profile_picture": 5,
        "projects": 10,
        "certifications": 5,
        "job_preferences": 5,
    }

    @staticmethod
    async def calculate_completeness(db: AsyncSession, user: User) -> dict:
        """
        Calculate profile completeness percentage.

        Returns:
            dict with 'percentage' and 'missing_sections'
        """
        score = 0
        missing_sections = []

        # Basic info (20%)
        if user.first_name and user.last_name and user.email:
            score += ProfileCompletenessCalculator.WEIGHTS["basic_info"]
        else:
            missing_sections.append("basic_info")

        # Profile picture (5%)
        # Check avatar_url in user settings
        if user.settings and user.settings.avatar_url:
            score += ProfileCompletenessCalculator.WEIGHTS["profile_picture"]
        else:
            missing_sections.append("profile_picture")

        # Work experience (25%)
        work_experiences = await profile_crud.work_experience.get_by_user(
            db, user_id=user.id
        )
        if work_experiences and len(work_experiences) > 0:
            score += ProfileCompletenessCalculator.WEIGHTS["work_experience"]
        else:
            missing_sections.append("work_experience")

        # Education (15%)
        educations = await profile_crud.education.get_by_user(db, user_id=user.id)
        if educations and len(educations) > 0:
            score += ProfileCompletenessCalculator.WEIGHTS["education"]
        else:
            missing_sections.append("education")

        # Skills (15%)
        skills = await profile_crud.skill.get_by_user(db, user_id=user.id)
        if skills and len(skills) >= 3:  # At least 3 skills
            score += ProfileCompletenessCalculator.WEIGHTS["skills"]
        else:
            missing_sections.append("skills")

        # Projects (10%)
        projects = await profile_crud.project.get_by_user(db, user_id=user.id)
        if projects and len(projects) > 0:
            score += ProfileCompletenessCalculator.WEIGHTS["projects"]
        else:
            missing_sections.append("projects")

        # Certifications (5%)
        certifications = await profile_crud.certification.get_by_user(
            db, user_id=user.id
        )
        if certifications and len(certifications) > 0:
            score += ProfileCompletenessCalculator.WEIGHTS["certifications"]
        else:
            missing_sections.append("certifications")

        # Job preferences (5%)
        job_preference = await profile_crud.job_preference.get_by_user(
            db, user_id=user.id
        )
        if job_preference and job_preference.job_search_status:
            score += ProfileCompletenessCalculator.WEIGHTS["job_preferences"]
        else:
            missing_sections.append("job_preferences")

        return {
            "percentage": int(score),
            "missing_sections": missing_sections,
            "completed_sections": [
                section
                for section in ProfileCompletenessCalculator.WEIGHTS
                if section not in missing_sections
            ],
        }


# Service instance
profile_completeness_calculator = ProfileCompletenessCalculator()
