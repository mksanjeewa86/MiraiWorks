from datetime import timedelta
from typing import Any

from sqlalchemy import and_, desc, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.crud.base import CRUDBase
from app.models.position import Position
from app.schemas.position import PositionCreate, PositionUpdate
from app.utils.datetime_utils import get_utc_now


class CRUDPosition(CRUDBase[Position, PositionCreate, PositionUpdate]):
    async def get_by_slug(self, db: AsyncSession, *, slug: str) -> Position | None:
        """Get position by slug."""
        result = await db.execute(
            select(Position)
            .where(Position.slug == slug)
            .options(selectinload(Position.company))
        )
        return result.scalar_one_or_none()

    async def get_published_positions(
        self,
        db: AsyncSession,
        *,
        skip: int = 0,
        limit: int = 100,
        location: str | None = None,
        job_type: str | None = None,
        salary_min: int | None = None,
        salary_max: int | None = None,
        company_id: int | None = None,
        search: str | None = None,
    ) -> list[Position]:
        """Get published positions with optional filters."""
        query = select(Position).where(Position.status == "published")

        # Apply filters
        if location:
            query = query.where(Position.location.ilike(f"%{location}%"))

        if job_type:
            query = query.where(Position.job_type == job_type)

        if salary_min:
            query = query.where(Position.salary_min >= salary_min)

        if salary_max:
            query = query.where(Position.salary_max <= salary_max)

        if company_id:
            query = query.where(Position.company_id == company_id)

        if search:
            search_filter = or_(
                Position.title.ilike(f"%{search}%"),
                Position.description.ilike(f"%{search}%"),
                Position.requirements.ilike(f"%{search}%"),
            )
            query = query.where(search_filter)

        # Order by most recent
        query = query.order_by(desc(Position.created_at))

        # Apply pagination
        query = query.offset(skip).limit(limit)

        # Load company relationship
        query = query.options(selectinload(Position.company))

        result = await db.execute(query)
        return list(result.scalars().all())

    async def get_published_positions_with_count(
        self,
        db: AsyncSession,
        *,
        skip: int = 0,
        limit: int = 100,
        location: str | None = None,
        job_type: str | None = None,
        salary_min: int | None = None,
        salary_max: int | None = None,
        company_id: int | None = None,
        search: str | None = None,
        days_since_posted: int | None = None,
    ) -> tuple[list[Position], int]:
        """Get published positions with optional filters and total count."""
        # Base query for filtering
        base_query = select(Position).where(Position.status == "published")

        # Apply filters
        if location:
            base_query = base_query.where(Position.location.ilike(f"%{location}%"))

        if job_type:
            base_query = base_query.where(Position.job_type == job_type)

        if salary_min:
            base_query = base_query.where(Position.salary_min >= salary_min)

        if salary_max:
            base_query = base_query.where(Position.salary_max <= salary_max)

        if company_id:
            base_query = base_query.where(Position.company_id == company_id)

        if search:
            search_filter = or_(
                Position.title.ilike(f"%{search}%"),
                Position.description.ilike(f"%{search}%"),
                Position.requirements.ilike(f"%{search}%"),
            )
            base_query = base_query.where(search_filter)

        if days_since_posted:
            from datetime import timedelta

            cutoff_date = get_utc_now() - timedelta(days=days_since_posted)
            base_query = base_query.where(Position.published_at >= cutoff_date)

        # Get total count by rebuilding the filter conditions without pagination
        count_query = select(func.count(Position.id)).where(
            Position.status == "published"
        )

        # Apply the same filters for counting
        if location:
            count_query = count_query.where(Position.location.ilike(f"%{location}%"))
        if job_type:
            count_query = count_query.where(Position.job_type == job_type)
        if salary_min:
            count_query = count_query.where(Position.salary_min >= salary_min)
        if salary_max:
            count_query = count_query.where(Position.salary_max <= salary_max)
        if company_id:
            count_query = count_query.where(Position.company_id == company_id)
        if search:
            search_filter = or_(
                Position.title.ilike(f"%{search}%"),
                Position.description.ilike(f"%{search}%"),
                Position.requirements.ilike(f"%{search}%"),
            )
            count_query = count_query.where(search_filter)
        if days_since_posted:
            from datetime import timedelta

            cutoff_date = get_utc_now() - timedelta(days=days_since_posted)
            count_query = count_query.where(Position.published_at >= cutoff_date)

        count_result = await db.execute(count_query)
        total_count = count_result.scalar()

        # Get paginated results
        data_query = (
            base_query.order_by(desc(Position.created_at))
            .offset(skip)
            .limit(limit)
            .options(selectinload(Position.company))
        )
        data_result = await db.execute(data_query)
        positions = list(data_result.scalars().all())

        return positions, total_count or 0

    async def get_by_company(
        self, db: AsyncSession, *, company_id: int, skip: int = 0, limit: int = 100
    ) -> list[Position]:
        """Get positions by company."""
        result = await db.execute(
            select(Position)
            .where(Position.company_id == company_id)
            .order_by(desc(Position.created_at))
            .offset(skip)
            .limit(limit)
            .options(selectinload(Position.company))
        )
        return list(result.scalars().all())

    async def search_positions(
        self, db: AsyncSession, *, query_text: str, skip: int = 0, limit: int = 100
    ) -> list[Position]:
        """Search positions by text."""
        search_filter = or_(
            Position.title.ilike(f"%{query_text}%"),
            Position.description.ilike(f"%{query_text}%"),
            Position.requirements.ilike(f"%{query_text}%"),
            Position.location.ilike(f"%{query_text}%"),
        )

        result = await db.execute(
            select(Position)
            .where(and_(Position.status == "published", search_filter))
            .order_by(desc(Position.created_at))
            .offset(skip)
            .limit(limit)
            .options(selectinload(Position.company))
        )
        return list(result.scalars().all())

    async def get_positions_by_status(
        self, db: AsyncSession, *, status: str, skip: int = 0, limit: int = 100
    ) -> list[Position]:
        """Get positions by status."""
        result = await db.execute(
            select(Position)
            .where(Position.status == status)
            .order_by(desc(Position.created_at))
            .offset(skip)
            .limit(limit)
            .options(selectinload(Position.company))
        )
        return list(result.scalars().all())

    async def increment_view_count(
        self, db: AsyncSession, *, position_id: int
    ) -> Position | None:
        """Increment position view count."""
        position = await self.get(db, id=position_id)
        if position:
            position.view_count = (position.view_count or 0) + 1
            await db.commit()
            await db.refresh(position)
        return position

    async def increment_position_view_count(
        self, db: AsyncSession, *, position_id: int
    ) -> Position | None:
        """Compatibility wrapper for new naming convention."""
        return await self.increment_view_count(db=db, position_id=position_id)

    async def get_popular_positions(
        self, db: AsyncSession, *, skip: int = 0, limit: int = 10
    ) -> list[Position]:
        """Get most popular positions by view count."""
        result = await db.execute(
            select(Position)
            .where(Position.status == "published")
            .order_by(desc(Position.view_count), desc(Position.created_at))
            .offset(skip)
            .limit(limit)
            .options(selectinload(Position.company))
        )
        return list(result.scalars().all())

    async def get_recent_positions(
        self, db: AsyncSession, *, days: int = 7, skip: int = 0, limit: int = 100
    ) -> list[Position]:
        """Get positions posted in the last N days."""
        cutoff_date = get_utc_now() - timedelta(days=days)

        result = await db.execute(
            select(Position)
            .where(
                and_(Position.status == "published", Position.created_at >= cutoff_date)
            )
            .order_by(desc(Position.created_at))
            .offset(skip)
            .limit(limit)
            .options(selectinload(Position.company))
        )
        return list(result.scalars().all())

    async def get_positions_expiring_soon(
        self, db: AsyncSession, *, days: int = 7, skip: int = 0, limit: int = 100
    ) -> list[Position]:
        """Get positions expiring in the next N days."""
        cutoff_date = get_utc_now() + timedelta(days=days)

        result = await db.execute(
            select(Position)
            .where(
                and_(
                    Position.status == "published",
                    Position.expires_at.isnot(None),
                    Position.expires_at <= cutoff_date,
                )
            )
            .order_by(Position.expires_at)
            .offset(skip)
            .limit(limit)
            .options(selectinload(Position.company))
        )
        return list(result.scalars().all())

    async def get_position_statistics(self, db: AsyncSession) -> dict[str, Any]:
        """Get position posting statistics."""
        # Total positions by status
        status_counts = await db.execute(
            select(Position.status, func.count(Position.id)).group_by(Position.status)
        )
        status_stats = {row[0]: row[1] for row in status_counts.all()}

        # Total applications
        total_applications = await db.execute(
            select(func.sum(Position.application_count))
        )
        total_app_count = total_applications.scalar() or 0

        # Positions by type
        type_counts = await db.execute(
            select(Position.job_type, func.count(Position.id))
            .where(Position.status == "published")
            .group_by(Position.job_type)
        )
        type_stats = {row[0]: row[1] for row in type_counts.all()}

        # Average salary by type
        salary_stats = await db.execute(
            select(
                Position.job_type,
                func.avg((Position.salary_min + Position.salary_max) / 2).label(  # type: ignore[operator]
                    "avg_salary"
                ),
            )
            .where(
                and_(
                    Position.status == "published",
                    Position.salary_min.isnot(None),
                    Position.salary_max.isnot(None),
                )
            )
            .group_by(Position.job_type)
        )
        avg_salaries = {row[0]: float(row[1]) for row in salary_stats.all()}

        total_positions = sum(list(status_stats.values()))
        published_positions = status_stats.get("published", 0)
        draft_positions = status_stats.get("draft", 0)
        closed_positions = status_stats.get("closed", 0)

        response = {
            "total_positions": total_positions,
            "positions_by_status": status_stats,
            "total_applications": total_app_count,
            "positions_by_type": type_stats,
            "average_salaries": avg_salaries,
            "published_positions": published_positions,
            "draft_positions": draft_positions,
            "closed_positions": closed_positions,
        }

        # Augment with position-specific keys for new API usage
        response.update(
            total_positions=total_positions,
            positions_by_status=status_stats,
            positions_by_type=type_stats,
            published_positions=published_positions,
            draft_positions=draft_positions,
            closed_positions=closed_positions,
        )

        return response

    async def bulk_update_status(
        self, db: AsyncSession, *, position_ids: list[int], status: str
    ) -> list[Position]:
        """Bulk update position status."""
        result = await db.execute(select(Position).where(Position.id.in_(position_ids)))
        positions = list(result.scalars().all())

        for position in positions:
            position.status = status
            if status == "published" and not position.published_at:
                position.published_at = get_utc_now()
            elif status == "closed":
                position.closed_at = get_utc_now()

        await db.commit()
        return positions

    async def bulk_update_position_status(
        self, db: AsyncSession, *, position_ids: list[int], status: str
    ) -> list[Position]:
        """Compatibility wrapper for new naming convention."""
        return await self.bulk_update_status(
            db=db, position_ids=position_ids, status=status
        )

    async def create_with_slug(
        self, db: AsyncSession, *, obj_in: PositionCreate
    ) -> Position:
        """Create position with auto-generated slug."""
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

        # Create position with slug
        obj_data = obj_in.model_dump()
        obj_data["slug"] = slug

        db_obj = Position(**obj_data)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj


# Create instance
position = CRUDPosition(Position)
