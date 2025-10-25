import logging
import re
import secrets
import string
from datetime import timedelta

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.resume import resume as resume_crud
from app.models.resume import (
    Education,
    Project,
    Resume,
    ResumeMessageAttachment,
    ResumeSection,
    ResumeShare,
    ResumeTemplate,
    Skill,
    WorkExperience,
)
from app.schemas.resume import (
    EducationCreate,
    ResumeCreate,
    ResumeUpdate,
    SkillCreate,
    WorkExperienceCreate,
)
from app.utils.constants import ResumeStatus, ResumeVisibility
from app.utils.datetime_utils import get_utc_now

logger = logging.getLogger(__name__)


class ResumeService:
    async def create_resume(
        self, db: AsyncSession, resume_data: ResumeCreate, user_id: int
    ) -> Resume:
        """Create a new resume."""
        try:
            # Generate unique slug
            slug = await self._generate_unique_slug(db, resume_data.title, user_id)

            # Set status-based visibility and public settings
            status = getattr(resume_data, "status", ResumeStatus.DRAFT)
            is_published = status == ResumeStatus.PUBLISHED

            # Create resume
            resume = Resume(
                user_id=user_id,
                title=resume_data.title,
                description=resume_data.description,
                full_name=resume_data.full_name,
                email=resume_data.email,
                phone=resume_data.phone,
                location=resume_data.location,
                website=resume_data.website,
                linkedin_url=resume_data.linkedin_url,
                github_url=resume_data.github_url,
                professional_summary=resume_data.professional_summary,
                objective=resume_data.objective,
                template_id=resume_data.template_id or "modern",
                theme_color=resume_data.theme_color or "#2563eb",
                font_family=resume_data.font_family or "Inter",
                slug=slug,
                share_token=self._generate_share_token(),
                # Status-based settings
                status=status,
                visibility=ResumeVisibility.PUBLIC
                if is_published
                else ResumeVisibility.PRIVATE,
                is_public=is_published,
                can_download_pdf=is_published,
                public_url_slug=slug if is_published else None,
            )

            db.add(resume)
            await db.commit()
            await db.refresh(resume)

            logger.info(f"Created resume {resume.id} for user {user_id}")
            return resume

        except Exception as e:
            logger.error(f"Error creating resume: {str(e)}")
            await db.rollback()
            raise

    async def get_resume(
        self, db: AsyncSession, resume_id: int, user_id: int
    ) -> Resume | None:
        """Get a resume by ID (with user ownership check)."""
        return await resume_crud.get_with_details(db, id=resume_id, user_id=user_id)

    async def get_resume_by_slug(self, db: AsyncSession, slug: str) -> Resume | None:
        """Get a resume by slug (public access)."""
        result = await db.execute(
            select(Resume).where(
                and_(
                    Resume.slug == slug,
                    Resume.visibility.in_(
                        [ResumeVisibility.PUBLIC, ResumeVisibility.UNLISTED]
                    ),
                )
            )
        )
        resume = result.scalars().first()

        if resume:
            # Increment view count
            resume.increment_view_count()
            await db.commit()

        return resume

    async def get_user_resumes(
        self,
        db: AsyncSession,
        user_id: int,
        limit: int = 10,
        offset: int = 0,
        status: ResumeStatus | None = None,
    ) -> list[Resume]:
        """Get all resumes for a user."""
        return await resume_crud.get_by_user(
            db, user_id=user_id, skip=offset, limit=limit, status=status
        )

    async def update_resume(
        self, db: AsyncSession, resume_id: int, user_id: int, update_data: ResumeUpdate
    ) -> Resume | None:
        """Update a resume."""
        try:
            resume = await self.get_resume(db, resume_id, user_id)
            if not resume:
                return None

            # Update fields
            update_dict = update_data.dict(exclude_unset=True)
            for field, value in update_dict.items():
                if hasattr(resume, field):
                    setattr(resume, field, value)

            # Auto-update visibility settings if status changed
            if "status" in update_dict:
                is_published = update_dict["status"] == ResumeStatus.PUBLISHED
                resume.visibility = (
                    ResumeVisibility.PUBLIC
                    if is_published
                    else ResumeVisibility.PRIVATE
                )
                resume.is_public = is_published
                resume.can_download_pdf = is_published
                # Set public URL slug when publishing
                if is_published and not resume.public_url_slug:
                    resume.public_url_slug = resume.slug

            # Update slug if title changed
            if "title" in update_dict:
                new_slug = await self._generate_unique_slug(
                    db, update_data.title, user_id, resume.id
                )
                resume.slug = new_slug

            await db.commit()
            await db.refresh(resume)

            logger.info(f"Updated resume {resume_id}")
            return resume

        except Exception as e:
            logger.error(f"Error updating resume: {str(e)}")
            await db.rollback()
            raise

    async def delete_resume(
        self, db: AsyncSession, resume_id: int, user_id: int
    ) -> bool:
        """Delete a resume."""
        try:
            resume = await self.get_resume(db, resume_id, user_id)
            if not resume:
                return False

            await db.delete(resume)
            await db.commit()

            logger.info(f"Deleted resume {resume_id}")
            return True

        except Exception as e:
            logger.error(f"Error deleting resume: {str(e)}")
            await db.rollback()
            raise

    async def duplicate_resume(
        self, db: AsyncSession, resume_id: int, user_id: int
    ) -> Resume | None:
        """Duplicate an existing resume."""
        try:
            original = await self.get_resume(db, resume_id, user_id)
            if not original:
                return None

            # Create duplicate
            duplicate = Resume(
                user_id=user_id,
                title=f"{original.title} (Copy)",
                description=original.description,
                full_name=original.full_name,
                email=original.email,
                phone=original.phone,
                location=original.location,
                website=original.website,
                linkedin_url=original.linkedin_url,
                github_url=original.github_url,
                professional_summary=original.professional_summary,
                objective=original.objective,
                template_id=original.template_id,
                theme_color=original.theme_color,
                font_family=original.font_family,
                custom_css=original.custom_css,
                slug=await self._generate_unique_slug(
                    db, f"{original.title} (Copy)", user_id
                ),
                share_token=self._generate_share_token(),
                status=ResumeStatus.DRAFT,
            )

            db.add(duplicate)
            await db.flush()

            # Duplicate all sections
            for section in original.sections:
                new_section = ResumeSection(
                    resume_id=duplicate.id,
                    section_type=section.section_type,
                    title=section.title,
                    content=section.content,
                    is_visible=section.is_visible,
                    display_order=section.display_order,
                    custom_css=section.custom_css,
                )
                db.add(new_section)

            # Duplicate experiences
            for exp in original.experiences:
                new_exp = WorkExperience(
                    resume_id=duplicate.id,
                    company_name=exp.company_name,
                    position_title=exp.position_title,
                    location=exp.location,
                    company_website=exp.company_website,
                    start_date=exp.start_date,
                    end_date=exp.end_date,
                    is_current=exp.is_current,
                    description=exp.description,
                    achievements=exp.achievements,
                    technologies=exp.technologies,
                    display_order=exp.display_order,
                )
                db.add(new_exp)

            # Duplicate other sections similarly...
            await self._duplicate_related_data(db, original, duplicate)

            await db.commit()
            await db.refresh(duplicate)

            logger.info(f"Duplicated resume {resume_id} to {duplicate.id}")
            return duplicate

        except Exception as e:
            logger.error(f"Error duplicating resume: {str(e)}")
            await db.rollback()
            raise

    # Work Experience methods
    async def add_work_experience(
        self,
        db: AsyncSession,
        resume_id: int,
        user_id: int,
        exp_data: WorkExperienceCreate,
    ) -> WorkExperience | None:
        """Add work experience to a resume."""
        try:
            # Verify ownership
            resume = await self.get_resume(db, resume_id, user_id)
            if not resume:
                return None

            experience = WorkExperience(
                resume_id=resume_id,
                company_name=exp_data.company_name,
                position_title=exp_data.position_title,
                location=exp_data.location,
                company_website=exp_data.company_website,
                start_date=exp_data.start_date,
                end_date=exp_data.end_date,
                is_current=exp_data.is_current,
                description=exp_data.description,
                achievements=exp_data.achievements,
                technologies=exp_data.technologies,
                display_order=exp_data.display_order or 0,
            )

            db.add(experience)
            await db.commit()
            await db.refresh(experience)

            return experience

        except Exception as e:
            logger.error(f"Error adding work experience: {str(e)}")
            await db.rollback()
            raise

    async def update_work_experience(
        self,
        db: AsyncSession,
        exp_id: int,
        user_id: int,
        exp_data: WorkExperienceCreate,
    ) -> WorkExperience | None:
        """Update work experience."""
        try:
            # Get experience and verify ownership
            result = await db.execute(
                select(WorkExperience)
                .join(Resume)
                .where(and_(WorkExperience.id == exp_id, Resume.user_id == user_id))
            )
            experience = result.scalars().first()

            if not experience:
                return None

            # Update fields
            for field, value in exp_data.dict(exclude_unset=True).items():
                if hasattr(experience, field):
                    setattr(experience, field, value)

            await db.commit()
            await db.refresh(experience)

            return experience

        except Exception as e:
            logger.error(f"Error updating work experience: {str(e)}")
            await db.rollback()
            raise

    # Similar methods for Education, Skills, etc.
    async def add_education(
        self, db: AsyncSession, resume_id: int, user_id: int, edu_data: EducationCreate
    ) -> Education | None:
        """Add education to a resume."""
        try:
            resume = await self.get_resume(db, resume_id, user_id)
            if not resume:
                return None

            education = Education(
                resume_id=resume_id,
                institution_name=edu_data.institution_name,
                degree=edu_data.degree,
                field_of_study=edu_data.field_of_study,
                location=edu_data.location,
                start_date=edu_data.start_date,
                end_date=edu_data.end_date,
                is_current=edu_data.is_current,
                gpa=edu_data.gpa,
                honors=edu_data.honors,
                description=edu_data.description,
                courses=edu_data.courses,
                display_order=edu_data.display_order or 0,
            )

            db.add(education)
            await db.commit()
            await db.refresh(education)

            return education

        except Exception as e:
            logger.error(f"Error adding education: {str(e)}")
            await db.rollback()
            raise

    async def add_skill(
        self, db: AsyncSession, resume_id: int, user_id: int, skill_data: SkillCreate
    ) -> Skill | None:
        """Add skill to a resume."""
        try:
            resume = await self.get_resume(db, resume_id, user_id)
            if not resume:
                return None

            skill = Skill(
                resume_id=resume_id,
                name=skill_data.name,
                category=skill_data.category,
                proficiency_level=skill_data.proficiency_level,
                proficiency_label=skill_data.proficiency_label,
                display_order=skill_data.display_order or 0,
            )

            db.add(skill)
            await db.commit()
            await db.refresh(skill)

            return skill

        except Exception as e:
            logger.error(f"Error adding skill: {str(e)}")
            await db.rollback()
            raise

    # Resume sharing methods
    async def create_share_link(
        self,
        db: AsyncSession,
        resume_id: int,
        user_id: int,
        recipient_email: str | None = None,
        password: str | None = None,
        expires_in_days: int | None = None,
        max_views: int | None = None,
    ) -> str | None:
        """Create a shareable link for a resume."""
        try:
            resume = await self.get_resume(db, resume_id, user_id)
            if not resume:
                return None

            share_token = self._generate_share_token()

            share = ResumeShare(
                resume_id=resume_id,
                share_token=share_token,
                recipient_email=recipient_email,
                password_protected=password is not None,
                password_hash=self._hash_password(password) if password else None,
                expires_at=get_utc_now() + timedelta(days=expires_in_days)
                if expires_in_days
                else None,
                max_views=max_views,
            )

            db.add(share)
            await db.commit()

            return share_token

        except Exception as e:
            logger.error(f"Error creating share link: {str(e)}")
            await db.rollback()
            raise

    async def get_shared_resume(
        self, db: AsyncSession, share_token: str, password: str | None = None
    ) -> Resume | None:
        """Get a resume via share token."""
        try:
            share = await ResumeShare.get_by_token(db, share_token)
            if not share or share.is_expired():
                return None

            # Check password if required
            if share.password_protected and (
                not password or not self._verify_password(password, share.password_hash)
            ):
                return None

            # Increment view count
            share.view_count += 1
            share.last_viewed_at = get_utc_now()

            # Get the resume
            result = await db.execute(
                select(Resume).where(Resume.id == share.resume_id)
            )
            resume = result.scalars().first()

            await db.commit()
            return resume

        except Exception as e:
            logger.error(f"Error getting shared resume: {str(e)}")
            raise

    # Template methods
    async def get_templates(
        self, db: AsyncSession, include_premium: bool = False
    ) -> list[ResumeTemplate]:
        """Get available resume templates."""
        return await ResumeTemplate.get_active_templates(db, include_premium)

    async def apply_template(
        self, db: AsyncSession, resume_id: int, user_id: int, template_id: str
    ) -> Resume | None:
        """Apply a template to a resume."""
        try:
            resume = await self.get_resume(db, resume_id, user_id)
            if not resume:
                return None

            # Verify template exists
            result = await db.execute(
                select(ResumeTemplate).where(ResumeTemplate.name == template_id)
            )
            template = result.scalars().first()
            if not template:
                raise ValueError(f"Template {template_id} not found")

            resume.template_id = template_id
            template.usage_count += 1

            await db.commit()
            await db.refresh(resume)

            return resume

        except Exception as e:
            logger.error(f"Error applying template: {str(e)}")
            await db.rollback()
            raise

    # Utility methods
    async def _generate_unique_slug(
        self,
        db: AsyncSession,
        title: str,
        user_id: int,
        exclude_id: int | None = None,
    ) -> str:
        """Generate a unique slug for a resume."""
        base_slug = self._slugify(title)
        slug = base_slug
        counter = 1

        while True:
            query = select(Resume).where(
                and_(Resume.user_id == user_id, Resume.slug == slug)
            )
            if exclude_id:
                query = query.where(Resume.id != exclude_id)

            result = await db.execute(query)
            if not result.scalars().first():
                break

            slug = f"{base_slug}-{counter}"
            counter += 1

        return slug

    def _slugify(self, text: str) -> str:
        """Convert text to URL-friendly slug."""
        text = text.lower()
        text = re.sub(r"[^\w\s-]", "", text)
        text = re.sub(r"[-\s]+", "-", text)
        return text.strip("-")[:50]

    def _generate_share_token(self) -> str:
        """Generate a secure share token."""
        return "".join(
            secrets.choice(string.ascii_letters + string.digits) for _ in range(32)
        )

    def _hash_password(self, password: str) -> str:
        """Hash password for share protection."""
        import bcrypt

        return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    def _verify_password(self, password: str, hashed: str) -> bool:
        """Verify password against hash."""
        import bcrypt

        return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))

    async def _duplicate_related_data(
        self, db: AsyncSession, original: Resume, duplicate: Resume
    ):
        """Helper method to duplicate all related data."""
        # Education
        for edu in original.educations:
            new_edu = Education(
                resume_id=duplicate.id,
                institution_name=edu.institution_name,
                degree=edu.degree,
                field_of_study=edu.field_of_study,
                location=edu.location,
                start_date=edu.start_date,
                end_date=edu.end_date,
                is_current=edu.is_current,
                gpa=edu.gpa,
                honors=edu.honors,
                description=edu.description,
                courses=edu.courses,
                display_order=edu.display_order,
            )
            db.add(new_edu)

        # Skills
        for skill in original.skills:
            new_skill = Skill(
                resume_id=duplicate.id,
                name=skill.name,
                category=skill.category,
                proficiency_level=skill.proficiency_level,
                proficiency_label=skill.proficiency_label,
                display_order=skill.display_order,
            )
            db.add(new_skill)

        # Projects
        for project in original.projects:
            new_project = Project(
                resume_id=duplicate.id,
                name=project.name,
                description=project.description,
                project_url=project.project_url,
                github_url=project.github_url,
                demo_url=project.demo_url,
                start_date=project.start_date,
                end_date=project.end_date,
                is_ongoing=project.is_ongoing,
                technologies=project.technologies,
                role=project.role,
                display_order=project.display_order,
            )
            db.add(new_project)

        # Continue for other related entities...

    def generate_pdf(self, resume_data: dict) -> bytes:
        """Generate PDF from resume data."""
        # Placeholder implementation for PDF generation
        return b"PDF content placeholder"

    def validate_resume_data(self, resume_data: dict) -> bool:
        """Validate resume data structure."""
        required_fields = ["title", "full_name", "email"]
        return all(field in resume_data for field in required_fields)

    async def update_public_settings(
        self,
        db: AsyncSession,
        resume_id: int,
        user_id: int,
        is_public: bool,
        custom_slug: str | None = None,
        can_download_pdf: bool = True,
    ) -> Resume | None:
        """Update public sharing settings for a resume."""
        try:
            return await resume_crud.update_public_settings(
                db,
                resume_id=resume_id,
                user_id=user_id,
                is_public=is_public,
                custom_slug=custom_slug,
                can_download_pdf=can_download_pdf,
            )
        except Exception as e:
            logger.error(f"Error updating public settings: {str(e)}")
            raise

    async def get_public_resume(self, db: AsyncSession, slug: str) -> Resume | None:
        """Get public resume by slug."""
        try:
            return await resume_crud.get_public_by_slug(db, slug=slug)
        except Exception as e:
            logger.error(f"Error getting public resume: {str(e)}")
            raise

    async def track_public_view(self, db: AsyncSession, slug: str) -> bool:
        """Increment view count for a public resume."""
        try:
            return await resume_crud.increment_public_view(db, slug=slug)
        except Exception as e:
            logger.error(f"Error tracking public resume view: {str(e)}")
            raise

    async def increment_download_count(self, db: AsyncSession, resume_id: int) -> bool:
        """Increment download count for a resume."""
        try:
            return await resume_crud.increment_download(db, resume_id=resume_id)
        except Exception as e:
            logger.error(f"Error incrementing download count: {str(e)}")
            raise

    async def send_resume_email(
        self,
        db: AsyncSession,
        resume: Resume,
        recipient_emails: list[str],
        subject: str,
        message: str,
        include_pdf: bool = True,
        sender_name: str | None = None,
    ) -> bool:
        """Send resume via email (background task)."""
        try:
            # Import email service (would need to be implemented)
            # from app.services.email_service import email_service

            logger.info(
                f"Sending resume {resume.id} to {len(recipient_emails)} recipients"
            )

            # For now, just log the action
            # In a real implementation, this would:
            # 1. Generate PDF if include_pdf is True
            # 2. Compose email with resume content
            # 3. Send via email service (SMTP, SendGrid, etc.)

            return True
        except Exception as e:
            logger.error(f"Error sending resume email: {str(e)}")
            return False

    async def attach_to_message(
        self,
        db: AsyncSession,
        resume_id: int,
        message_id: int,
        include_pdf: bool = True,
        auto_attach: bool = False,
    ) -> ResumeMessageAttachment:
        """Attach resume to a message."""
        try:
            attachment_format = "pdf" if include_pdf else "json"

            attachment = ResumeMessageAttachment(
                resume_id=resume_id,
                message_id=message_id,
                auto_attached=auto_attach,
                attachment_format=attachment_format,
            )

            db.add(attachment)
            await db.commit()
            await db.refresh(attachment)

            logger.info(f"Attached resume {resume_id} to message {message_id}")
            return attachment

        except Exception as e:
            logger.error(f"Error attaching resume to message: {str(e)}")
            await db.rollback()
            raise
