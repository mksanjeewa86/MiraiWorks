from typing import Any, Dict, List, Optional, Union
from datetime import datetime, timedelta

from sqlalchemy import and_, desc, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.crud.base import CRUDBase
from app.models.job import Job
from app.schemas.job import JobCreate, JobUpdate


class CRUDJob(CRUDBase[Job, JobCreate, JobUpdate]):
    async def get_by_slug(self, db: AsyncSession, *, slug: str) -> Optional[Job]:
        """Get job by slug."""
        result = await db.execute(
            select(Job).where(Job.slug == slug).options(selectinload(Job.company))
        )
        return result.scalar_one_or_none()

    async def get_published_jobs(
        self,
        db: AsyncSession,
        *,
        skip: int = 0,
        limit: int = 100,
        location: Optional[str] = None,
        job_type: Optional[str] = None,
        salary_min: Optional[int] = None,
        salary_max: Optional[int] = None,
        company_id: Optional[int] = None,
        search: Optional[str] = None,
    ) -> List[Job]:
        """Get published jobs with optional filters."""
        query = select(Job).where(Job.status == "published")

        # Apply filters
        if location:
            query = query.where(Job.location.ilike(f"%{location}%"))

        if job_type:
            query = query.where(Job.job_type == job_type)

        if salary_min:
            query = query.where(Job.salary_min >= salary_min)

        if salary_max:
            query = query.where(Job.salary_max <= salary_max)

        if company_id:
            query = query.where(Job.company_id == company_id)

        if search:
            search_filter = or_(
                Job.title.ilike(f"%{search}%"),
                Job.description.ilike(f"%{search}%"),
                Job.requirements.ilike(f"%{search}%"),
            )
            query = query.where(search_filter)

        # Order by most recent
        query = query.order_by(desc(Job.created_at))

        # Apply pagination
        query = query.offset(skip).limit(limit)

        # Load company relationship
        query = query.options(selectinload(Job.company))

        result = await db.execute(query)
        return result.scalars().all()

    async def get_by_company(
        self, db: AsyncSession, *, company_id: int, skip: int = 0, limit: int = 100
    ) -> List[Job]:
        """Get jobs by company."""
        result = await db.execute(
            select(Job)
            .where(Job.company_id == company_id)
            .order_by(desc(Job.created_at))
            .offset(skip)
            .limit(limit)
            .options(selectinload(Job.company))
        )
        return result.scalars().all()

    async def search_jobs(
        self, db: AsyncSession, *, query_text: str, skip: int = 0, limit: int = 100
    ) -> List[Job]:
        """Search jobs by text."""
        search_filter = or_(
            Job.title.ilike(f"%{query_text}%"),
            Job.description.ilike(f"%{query_text}%"),
            Job.requirements.ilike(f"%{query_text}%"),
            Job.location.ilike(f"%{query_text}%"),
        )

        result = await db.execute(
            select(Job)
            .where(and_(Job.status == "published", search_filter))
            .order_by(desc(Job.created_at))
            .offset(skip)
            .limit(limit)
            .options(selectinload(Job.company))
        )
        return result.scalars().all()

    async def get_jobs_by_status(
        self, db: AsyncSession, *, status: str, skip: int = 0, limit: int = 100
    ) -> List[Job]:
        """Get jobs by status."""
        result = await db.execute(
            select(Job)
            .where(Job.status == status)
            .order_by(desc(Job.created_at))
            .offset(skip)
            .limit(limit)
            .options(selectinload(Job.company))
        )
        return result.scalars().all()

    async def increment_view_count(
        self, db: AsyncSession, *, job_id: int
    ) -> Optional[Job]:
        """Increment job view count."""
        job = await self.get(db, id=job_id)
        if job:
            job.view_count = (job.view_count or 0) + 1
            await db.commit()
            await db.refresh(job)
        return job

    async def get_popular_jobs(
        self, db: AsyncSession, *, skip: int = 0, limit: int = 10
    ) -> List[Job]:
        """Get most popular jobs by view count."""
        result = await db.execute(
            select(Job)
            .where(Job.status == "published")
            .order_by(desc(Job.view_count), desc(Job.created_at))
            .offset(skip)
            .limit(limit)
            .options(selectinload(Job.company))
        )
        return result.scalars().all()

    async def get_recent_jobs(
        self, db: AsyncSession, *, days: int = 7, skip: int = 0, limit: int = 100
    ) -> List[Job]:
        """Get jobs posted in the last N days."""
        cutoff_date = datetime.utcnow() - timedelta(days=days)

        result = await db.execute(
            select(Job)
            .where(and_(Job.status == "published", Job.created_at >= cutoff_date))
            .order_by(desc(Job.created_at))
            .offset(skip)
            .limit(limit)
            .options(selectinload(Job.company))
        )
        return result.scalars().all()

    async def get_jobs_expiring_soon(
        self, db: AsyncSession, *, days: int = 7, skip: int = 0, limit: int = 100
    ) -> List[Job]:
        """Get jobs expiring in the next N days."""
        cutoff_date = datetime.utcnow() + timedelta(days=days)

        result = await db.execute(
            select(Job)
            .where(
                and_(
                    Job.status == "published",
                    Job.expires_at.isnot(None),
                    Job.expires_at <= cutoff_date,
                )
            )
            .order_by(Job.expires_at)
            .offset(skip)
            .limit(limit)
            .options(selectinload(Job.company))
        )
        return result.scalars().all()

    async def get_job_statistics(self, db: AsyncSession) -> Dict[str, Any]:
        """Get job posting statistics."""
        # Total jobs by status
        status_counts = await db.execute(
            select(Job.status, func.count(Job.id)).group_by(Job.status)
        )
        status_stats = dict(status_counts.all())

        # Total applications
        total_applications = await db.execute(select(func.sum(Job.application_count)))
        total_app_count = total_applications.scalar() or 0

        # Jobs by type
        type_counts = await db.execute(
            select(Job.job_type, func.count(Job.id))
            .where(Job.status == "published")
            .group_by(Job.job_type)
        )
        type_stats = dict(type_counts.all())

        # Average salary by type
        salary_stats = await db.execute(
            select(
                Job.job_type,
                func.avg((Job.salary_min + Job.salary_max) / 2).label("avg_salary"),
            )
            .where(
                and_(
                    Job.status == "published",
                    Job.salary_min.isnot(None),
                    Job.salary_max.isnot(None),
                )
            )
            .group_by(Job.job_type)
        )
        avg_salaries = {row[0]: float(row[1]) for row in salary_stats.all()}

        return {
            "total_jobs": sum(status_stats.values()),
            "jobs_by_status": status_stats,
            "total_applications": total_app_count,
            "jobs_by_type": type_stats,
            "average_salaries": avg_salaries,
            "published_jobs": status_stats.get("published", 0),
            "draft_jobs": status_stats.get("draft", 0),
            "closed_jobs": status_stats.get("closed", 0),
        }

    async def bulk_update_status(
        self, db: AsyncSession, *, job_ids: List[int], status: str
    ) -> List[Job]:
        """Bulk update job status."""
        result = await db.execute(select(Job).where(Job.id.in_(job_ids)))
        jobs = result.scalars().all()

        for job in jobs:
            job.status = status
            if status == "published" and not job.published_at:
                job.published_at = datetime.utcnow()
            elif status == "closed":
                job.closed_at = datetime.utcnow()

        await db.commit()
        return jobs

    async def create_with_slug(self, db: AsyncSession, *, obj_in: JobCreate) -> Job:
        """Create job with auto-generated slug."""
        # Generate slug from title
        import re

        slug_base = re.sub(r"[^a-zA-Z0-9\s-]", "", obj_in.title.lower())
        slug_base = re.sub(r"\s+", "-", slug_base.strip())

        # Ensure slug uniqueness
        slug = slug_base
        counter = 1
        while True:
            existing = await self.get_by_slug(db, slug=slug)
            if not existing:
                break
            slug = f"{slug_base}-{counter}"
            counter += 1

        # Create job with slug
        obj_data = obj_in.model_dump()
        obj_data["slug"] = slug

        db_obj = Job(**obj_data)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj


# Create instance
job = CRUDJob(Job)
