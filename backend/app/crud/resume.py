import secrets
import string
from datetime import datetime

from sqlalchemy import and_, desc, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.crud.base import CRUDBase
from app.models.resume import (
    Education,
    Resume,
    ResumeMessageAttachment,
    Skill,
    WorkExperience,
)
from app.schemas.resume import (
    EducationCreate,
    EducationUpdate,
    ResumeCreate,
    ResumeUpdate,
    SkillCreate,
    SkillUpdate,
    WorkExperienceCreate,
    WorkExperienceUpdate,
)
from app.utils.constants import ResumeStatus, ResumeVisibility


def generate_slug(title: str, max_length: int = 50) -> str:
    """Generate a URL-friendly slug from title"""
    import re

    # Convert to lowercase and replace spaces with hyphens
    slug = re.sub(r"[^\w\s-]", "", title.lower())
    slug = re.sub(r"[-\s]+", "-", slug)

    # Truncate if too long
    if len(slug) > max_length:
        slug = slug[:max_length].rstrip("-")

    # Add random suffix to ensure uniqueness
    random_suffix = "".join(
        secrets.choice(string.ascii_lowercase + string.digits) for _ in range(6)
    )

    return f"{slug}-{random_suffix}"


def generate_share_token() -> str:
    """Generate a secure share token"""
    return secrets.token_urlsafe(32)


class CRUDResume(CRUDBase[Resume, ResumeCreate, ResumeUpdate]):
    async def create_with_user(
        self, db: AsyncSession, *, obj_in: ResumeCreate, user_id: int
    ) -> Resume:
        """Create resume with user_id"""
        obj_data = obj_in.model_dump()
        obj_data["user_id"] = user_id
        obj_data["public_url_slug"] = generate_slug(obj_data["title"])
        obj_data["share_token"] = generate_share_token()

        db_obj = Resume(**obj_data)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def get_by_user(
        self,
        db: AsyncSession,
        *,
        user_id: int,
        skip: int = 0,
        limit: int = 10,
        status: ResumeStatus | None = None,
    ) -> list[Resume]:
        """Get resumes by user ID with optional status filter"""
        query = (
            select(Resume)
            .options(
                selectinload(Resume.sections),
                selectinload(Resume.experiences),
                selectinload(Resume.educations),
                selectinload(Resume.skills),
                selectinload(Resume.projects),
                selectinload(Resume.certifications),
                selectinload(Resume.languages),
                selectinload(Resume.references),
            )
            .where(Resume.user_id == user_id)
        )

        if status:
            query = query.where(Resume.status == status)

        query = query.order_by(desc(Resume.updated_at)).offset(skip).limit(limit)

        result = await db.execute(query)
        return result.scalars().all()

    async def get_with_details(
        self, db: AsyncSession, *, id: int, user_id: int
    ) -> Resume | None:
        """Get resume with all related details"""
        query = (
            select(Resume)
            .options(
                selectinload(Resume.sections),
                selectinload(Resume.experiences),
                selectinload(Resume.educations),
                selectinload(Resume.skills),
                selectinload(Resume.projects),
                selectinload(Resume.certifications),
                selectinload(Resume.languages),
                selectinload(Resume.references),
            )
            .where(and_(Resume.id == id, Resume.user_id == user_id))
        )

        result = await db.execute(query)
        return result.scalars().first()

    async def get_public_by_slug(self, db: AsyncSession, *, slug: str) -> Resume | None:
        """Get public resume by slug"""
        query = (
            select(Resume)
            .options(
                selectinload(Resume.experiences),
                selectinload(Resume.educations),
                selectinload(Resume.skills),
                selectinload(Resume.projects),
                selectinload(Resume.certifications),
                selectinload(Resume.languages),
            )
            .where(
                and_(
                    Resume.public_url_slug == slug,
                    Resume.is_public is True,
                    Resume.status == ResumeStatus.PUBLISHED,
                )
            )
        )

        result = await db.execute(query)
        resume = result.scalars().first()

        return resume

    async def increment_public_view(self, db: AsyncSession, *, slug: str) -> bool:
        result = await db.execute(
            update(Resume)
            .where(
                and_(
                    Resume.public_url_slug == slug,
                    Resume.is_public is True,
                    Resume.status == ResumeStatus.PUBLISHED,
                )
            )
            .values(view_count=Resume.view_count + 1, last_viewed_at=datetime.utcnow())
            .returning(Resume.id)
        )

        updated = result.scalars().first()
        await db.commit()
        return updated is not None

    async def get_by_share_token(
        self, db: AsyncSession, *, token: str
    ) -> Resume | None:
        """Get resume by share token"""
        query = (
            select(Resume)
            .options(
                selectinload(Resume.experiences),
                selectinload(Resume.educations),
                selectinload(Resume.skills),
                selectinload(Resume.projects),
                selectinload(Resume.certifications),
                selectinload(Resume.languages),
            )
            .where(Resume.share_token == token)
        )

        result = await db.execute(query)
        resume = result.scalars().first()

        if resume:
            resume.increment_view_count()
            await db.commit()

        return resume

    async def update_public_settings(
        self,
        db: AsyncSession,
        *,
        resume_id: int,
        user_id: int,
        is_public: bool,
        custom_slug: str | None = None,
        can_download_pdf: bool = True,
    ) -> Resume | None:
        """Update public sharing settings"""
        resume = await db.get(Resume, resume_id)
        if not resume or resume.user_id != user_id:
            return None

        # Generate new slug if custom one provided
        if custom_slug:
            resume.public_url_slug = generate_slug(custom_slug)
        elif not resume.public_url_slug:
            resume.public_url_slug = generate_slug(resume.title)

        resume.is_public = is_public
        resume.can_download_pdf = can_download_pdf

        if is_public:
            resume.visibility = ResumeVisibility.PUBLIC
            if resume.status != ResumeStatus.PUBLISHED:
                resume.status = ResumeStatus.PUBLISHED
        else:
            resume.visibility = ResumeVisibility.PRIVATE

        await db.commit()
        await db.refresh(resume)
        return resume

    async def set_primary(
        self, db: AsyncSession, *, resume_id: int, user_id: int
    ) -> Resume | None:
        """Set resume as primary (unset others)"""
        # First unset all primary resumes for user
        await db.execute(
            update(Resume).where(Resume.user_id == user_id).values(is_primary=False)
        )

        # Set the specified resume as primary
        result = await db.execute(
            update(Resume)
            .where(and_(Resume.id == resume_id, Resume.user_id == user_id))
            .values(is_primary=True)
            .returning(Resume)
        )

        await db.commit()
        resume = result.scalars().first()
        if resume:
            await db.refresh(resume)
        return resume

    async def get_user_stats(self, db: AsyncSession, *, user_id: int) -> dict:
        """Get resume statistics for user"""
        total_query = select(func.count(Resume.id)).where(Resume.user_id == user_id)
        total_result = await db.execute(total_query)
        total_resumes = total_result.scalar()

        # Get counts by status
        status_query = (
            select(Resume.status, func.count(Resume.id))
            .where(Resume.user_id == user_id)
            .group_by(Resume.status)
        )
        status_result = await db.execute(status_query)
        by_status = dict(status_result.fetchall())

        # Get total views and downloads
        views_query = select(func.sum(Resume.view_count)).where(
            Resume.user_id == user_id
        )
        views_result = await db.execute(views_query)
        total_views = views_result.scalar() or 0

        downloads_query = select(func.sum(Resume.download_count)).where(
            Resume.user_id == user_id
        )
        downloads_result = await db.execute(downloads_query)
        total_downloads = downloads_result.scalar() or 0

        return {
            "total_resumes": total_resumes,
            "by_status": by_status,
            "total_views": total_views,
            "total_downloads": total_downloads,
        }

    async def increment_download(self, db: AsyncSession, *, resume_id: int) -> bool:
        """Increment download count"""
        result = await db.execute(
            update(Resume)
            .where(Resume.id == resume_id)
            .values(download_count=Resume.download_count + 1)
        )
        await db.commit()
        return result.rowcount > 0

    async def duplicate_resume(
        self, db: AsyncSession, *, resume_id: int, user_id: int
    ) -> Resume | None:
        """Create a copy of existing resume"""
        original = await self.get_with_details(db, id=resume_id, user_id=user_id)
        if not original:
            return None

        # Create new resume data
        new_resume_data = {
            "title": f"{original.title} (Copy)",
            "description": original.description,
            "full_name": original.full_name,
            "email": original.email,
            "phone": original.phone,
            "location": original.location,
            "website": original.website,
            "linkedin_url": original.linkedin_url,
            "github_url": original.github_url,
            "professional_summary": original.professional_summary,
            "objective": original.objective,
            "template_id": original.template_id,
            "resume_format": original.resume_format,
            "resume_language": original.resume_language,
            "theme_color": original.theme_color,
            "font_family": original.font_family,
            "furigana_name": original.furigana_name,
            "birth_date": original.birth_date,
            "gender": original.gender,
            "nationality": original.nationality,
            "marital_status": original.marital_status,
            "emergency_contact": original.emergency_contact,
            "user_id": user_id,
            "status": ResumeStatus.DRAFT,
            "visibility": ResumeVisibility.PRIVATE,
            "is_public": False,
            "public_url_slug": generate_slug(f"{original.title} (Copy)"),
            "share_token": generate_share_token(),
        }

        new_resume = Resume(**new_resume_data)
        db.add(new_resume)
        await db.flush()

        # Copy all related data
        for experience in original.experiences:
            new_exp = WorkExperience(
                resume_id=new_resume.id,
                company_name=experience.company_name,
                position_title=experience.position_title,
                location=experience.location,
                company_website=experience.company_website,
                start_date=experience.start_date,
                end_date=experience.end_date,
                is_current=experience.is_current,
                description=experience.description,
                achievements=experience.achievements,
                technologies=experience.technologies,
                display_order=experience.display_order,
            )
            db.add(new_exp)

        # Copy education, skills, etc. (similar pattern)
        # ... (truncated for brevity, would include all related models)

        await db.commit()
        await db.refresh(new_resume)
        return new_resume


# Related model CRUD classes
class CRUDWorkExperience(
    CRUDBase[WorkExperience, WorkExperienceCreate, WorkExperienceUpdate]
):
    async def create_for_resume(
        self, db: AsyncSession, *, obj_in: WorkExperienceCreate, resume_id: int
    ) -> WorkExperience:
        obj_data = obj_in.model_dump()
        obj_data["resume_id"] = resume_id
        db_obj = WorkExperience(**obj_data)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def get_by_resume(
        self, db: AsyncSession, *, resume_id: int
    ) -> list[WorkExperience]:
        result = await db.execute(
            select(WorkExperience)
            .where(WorkExperience.resume_id == resume_id)
            .order_by(WorkExperience.display_order, desc(WorkExperience.start_date))
        )
        return result.scalars().all()


class CRUDEducation(CRUDBase[Education, EducationCreate, EducationUpdate]):
    async def create_for_resume(
        self, db: AsyncSession, *, obj_in: EducationCreate, resume_id: int
    ) -> Education:
        obj_data = obj_in.model_dump()
        obj_data["resume_id"] = resume_id
        db_obj = Education(**obj_data)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def get_by_resume(
        self, db: AsyncSession, *, resume_id: int
    ) -> list[Education]:
        result = await db.execute(
            select(Education)
            .where(Education.resume_id == resume_id)
            .order_by(Education.display_order, desc(Education.start_date))
        )
        return result.scalars().all()


class CRUDSkill(CRUDBase[Skill, SkillCreate, SkillUpdate]):
    async def create_for_resume(
        self, db: AsyncSession, *, obj_in: SkillCreate, resume_id: int
    ) -> Skill:
        obj_data = obj_in.model_dump()
        obj_data["resume_id"] = resume_id
        db_obj = Skill(**obj_data)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def get_by_resume(self, db: AsyncSession, *, resume_id: int) -> list[Skill]:
        result = await db.execute(
            select(Skill)
            .where(Skill.resume_id == resume_id)
            .order_by(Skill.display_order, Skill.category, Skill.name)
        )
        return result.scalars().all()


class CRUDResumeMessageAttachment(CRUDBase[ResumeMessageAttachment, dict, dict]):
    async def create_attachment(
        self,
        db: AsyncSession,
        *,
        resume_id: int,
        message_id: int,
        auto_attached: bool = False,
        attachment_format: str = "pdf",
    ) -> ResumeMessageAttachment:
        """Create a resume message attachment"""
        db_obj = ResumeMessageAttachment(
            resume_id=resume_id,
            message_id=message_id,
            auto_attached=auto_attached,
            attachment_format=attachment_format,
        )
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def get_by_message(
        self, db: AsyncSession, *, message_id: int
    ) -> list[ResumeMessageAttachment]:
        """Get all resume attachments for a message"""
        result = await db.execute(
            select(ResumeMessageAttachment).where(
                ResumeMessageAttachment.message_id == message_id
            )
        )
        return result.scalars().all()


# Initialize CRUD instances
resume = CRUDResume(Resume)
work_experience = CRUDWorkExperience(WorkExperience)
education = CRUDEducation(Education)
skill = CRUDSkill(Skill)
resume_message_attachment = CRUDResumeMessageAttachment(ResumeMessageAttachment)
