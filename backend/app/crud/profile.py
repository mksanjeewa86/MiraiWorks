"""CRUD operations for user profile models."""

from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models.certification import ProfileCertification
from app.models.education import ProfileEducation
from app.models.job_preference import JobPreference
from app.models.project import ProfileProject
from app.models.skill import ProfileSkill
from app.models.work_experience import ProfileWorkExperience
from app.schemas.certification import (
    CertificationCreate,
    CertificationUpdate,
)
from app.schemas.education import EducationCreate, EducationUpdate
from app.schemas.job_preference import JobPreferenceCreate, JobPreferenceUpdate
from app.schemas.project import ProjectCreate, ProjectUpdate
from app.schemas.skill import SkillCreate, SkillUpdate
from app.schemas.work_experience import WorkExperienceCreate, WorkExperienceUpdate


# Work Experience CRUD
class CRUDWorkExperience(
    CRUDBase[ProfileWorkExperience, WorkExperienceCreate, WorkExperienceUpdate]
):
    """CRUD operations for work experience."""

    async def create_for_user(
        self, db: AsyncSession, *, obj_in: WorkExperienceCreate, user_id: int
    ) -> ProfileWorkExperience:
        """Create work experience entry for a user."""
        obj_data = obj_in.model_dump()
        obj_data["user_id"] = user_id
        db_obj = ProfileWorkExperience(**obj_data)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def get_by_user(
        self, db: AsyncSession, *, user_id: int
    ) -> list[ProfileWorkExperience]:
        """Get all work experiences for a user, ordered by display order."""
        result = await db.execute(
            select(ProfileWorkExperience)
            .where(ProfileWorkExperience.user_id == user_id)
            .order_by(
                ProfileWorkExperience.display_order,
                desc(ProfileWorkExperience.start_date),
            )
        )
        return list(result.scalars().all())

    async def get_user_experience(
        self, db: AsyncSession, *, id: int, user_id: int
    ) -> ProfileWorkExperience | None:
        """Get a specific work experience entry for a user."""
        result = await db.execute(
            select(ProfileWorkExperience).where(
                ProfileWorkExperience.id == id, ProfileWorkExperience.user_id == user_id
            )
        )
        return result.scalar_one_or_none()


# Education CRUD
class CRUDEducation(CRUDBase[ProfileEducation, EducationCreate, EducationUpdate]):
    """CRUD operations for education."""

    async def create_for_user(
        self, db: AsyncSession, *, obj_in: EducationCreate, user_id: int
    ) -> ProfileEducation:
        """Create education entry for a user."""
        obj_data = obj_in.model_dump()
        obj_data["user_id"] = user_id
        db_obj = ProfileEducation(**obj_data)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def get_by_user(
        self, db: AsyncSession, *, user_id: int
    ) -> list[ProfileEducation]:
        """Get all education entries for a user, ordered by display order."""
        result = await db.execute(
            select(ProfileEducation)
            .where(ProfileEducation.user_id == user_id)
            .order_by(ProfileEducation.display_order, desc(ProfileEducation.start_date))
        )
        return list(result.scalars().all())

    async def get_user_education(
        self, db: AsyncSession, *, id: int, user_id: int
    ) -> ProfileEducation | None:
        """Get a specific education entry for a user."""
        result = await db.execute(
            select(ProfileEducation).where(
                ProfileEducation.id == id, ProfileEducation.user_id == user_id
            )
        )
        return result.scalar_one_or_none()


# ProfileSkill CRUD
class CRUDSkill(CRUDBase[ProfileSkill, SkillCreate, SkillUpdate]):
    """CRUD operations for skills."""

    async def create_for_user(
        self, db: AsyncSession, *, obj_in: SkillCreate, user_id: int
    ) -> ProfileSkill:
        """Create skill entry for a user."""
        obj_data = obj_in.model_dump()
        obj_data["user_id"] = user_id
        db_obj = ProfileSkill(**obj_data)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def get_by_user(
        self, db: AsyncSession, *, user_id: int
    ) -> list[ProfileSkill]:
        """Get all skills for a user, ordered by display order and category."""
        result = await db.execute(
            select(ProfileSkill)
            .where(ProfileSkill.user_id == user_id)
            .order_by(
                ProfileSkill.display_order,
                ProfileSkill.category,
                ProfileSkill.skill_name,
            )
        )
        return list(result.scalars().all())

    async def get_by_category(
        self, db: AsyncSession, *, user_id: int, category: str
    ) -> list[ProfileSkill]:
        """Get skills for a user filtered by category."""
        result = await db.execute(
            select(ProfileSkill)
            .where(ProfileSkill.user_id == user_id, ProfileSkill.category == category)
            .order_by(ProfileSkill.display_order, ProfileSkill.skill_name)
        )
        return list(result.scalars().all())

    async def get_user_skill(
        self, db: AsyncSession, *, id: int, user_id: int
    ) -> ProfileSkill | None:
        """Get a specific skill entry for a user."""
        result = await db.execute(
            select(ProfileSkill).where(
                ProfileSkill.id == id, ProfileSkill.user_id == user_id
            )
        )
        return result.scalar_one_or_none()


# ProfileCertification CRUD
class CRUDCertification(
    CRUDBase[ProfileCertification, CertificationCreate, CertificationUpdate]
):
    """CRUD operations for certifications."""

    async def create_for_user(
        self, db: AsyncSession, *, obj_in: CertificationCreate, user_id: int
    ) -> ProfileCertification:
        """Create certification entry for a user."""
        obj_data = obj_in.model_dump()
        obj_data["user_id"] = user_id
        db_obj = ProfileCertification(**obj_data)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def get_by_user(
        self, db: AsyncSession, *, user_id: int
    ) -> list[ProfileCertification]:
        """Get all certifications for a user, ordered by display order."""
        result = await db.execute(
            select(ProfileCertification)
            .where(ProfileCertification.user_id == user_id)
            .order_by(
                ProfileCertification.display_order,
                desc(ProfileCertification.issue_date),
            )
        )
        return list(result.scalars().all())

    async def get_user_certification(
        self, db: AsyncSession, *, id: int, user_id: int
    ) -> ProfileCertification | None:
        """Get a specific certification entry for a user."""
        result = await db.execute(
            select(ProfileCertification).where(
                ProfileCertification.id == id, ProfileCertification.user_id == user_id
            )
        )
        return result.scalar_one_or_none()


# ProfileProject CRUD
class CRUDProject(CRUDBase[ProfileProject, ProjectCreate, ProjectUpdate]):
    """CRUD operations for projects."""

    async def create_for_user(
        self, db: AsyncSession, *, obj_in: ProjectCreate, user_id: int
    ) -> ProfileProject:
        """Create project entry for a user."""
        obj_data = obj_in.model_dump()
        obj_data["user_id"] = user_id
        db_obj = ProfileProject(**obj_data)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def get_by_user(
        self, db: AsyncSession, *, user_id: int
    ) -> list[ProfileProject]:
        """Get all projects for a user, ordered by display order."""
        result = await db.execute(
            select(ProfileProject)
            .where(ProfileProject.user_id == user_id)
            .order_by(ProfileProject.display_order, desc(ProfileProject.start_date))
        )
        return list(result.scalars().all())

    async def get_user_project(
        self, db: AsyncSession, *, id: int, user_id: int
    ) -> ProfileProject | None:
        """Get a specific project entry for a user."""
        result = await db.execute(
            select(ProfileProject).where(
                ProfileProject.id == id, ProfileProject.user_id == user_id
            )
        )
        return result.scalar_one_or_none()


# Job Preference CRUD
class CRUDJobPreference(
    CRUDBase[JobPreference, JobPreferenceCreate, JobPreferenceUpdate]
):
    """CRUD operations for job preferences."""

    async def get_by_user(
        self, db: AsyncSession, *, user_id: int
    ) -> JobPreference | None:
        """Get job preference for a user (one-to-one relationship)."""
        result = await db.execute(
            select(JobPreference).where(JobPreference.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def create_for_user(
        self, db: AsyncSession, *, obj_in: JobPreferenceCreate, user_id: int
    ) -> JobPreference:
        """Create job preference for a user."""
        obj_data = obj_in.model_dump()
        obj_data["user_id"] = user_id
        db_obj = JobPreference(**obj_data)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def get_or_create(self, db: AsyncSession, *, user_id: int) -> JobPreference:
        """Get existing job preference or create with defaults."""
        preference = await self.get_by_user(db, user_id=user_id)
        if not preference:
            preference = await self.create_for_user(
                db, obj_in=JobPreferenceCreate(), user_id=user_id  # type: ignore[call-arg]
            )
        return preference

    async def update_for_user(
        self,
        db: AsyncSession,
        *,
        user_id: int,
        obj_in: JobPreferenceUpdate,
    ) -> JobPreference:
        """Update job preference for a user (create if doesn't exist)."""
        preference = await self.get_by_user(db, user_id=user_id)
        if not preference:
            # Create new if doesn't exist
            return await self.create_for_user(
                db, obj_in=JobPreferenceCreate(**obj_in.model_dump()), user_id=user_id
            )
        # Update existing
        return await self.update(db, db_obj=preference, obj_in=obj_in)


# Initialize CRUD instances
work_experience = CRUDWorkExperience(ProfileWorkExperience)
education = CRUDEducation(ProfileEducation)
skill = CRUDSkill(ProfileSkill)
certification = CRUDCertification(ProfileCertification)
project = CRUDProject(ProfileProject)
job_preference = CRUDJobPreference(JobPreference)
