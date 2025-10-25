"""CRUD operations for profile views."""

from datetime import timedelta
from typing import Any

from sqlalchemy import and_, desc, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app.models.company import Company
from app.models.profile_view import ProfileView
from app.models.user import User
from app.utils.datetime_utils import get_utc_now


class CRUDProfileView:
    """CRUD operations for profile views."""

    async def create_profile_view(
        self,
        db: AsyncSession,
        *,
        profile_user_id: int,
        viewer_user_id: int | None = None,
        viewer_company_id: int | None = None,
        viewer_ip: str | None = None,
        viewer_user_agent: str | None = None,
        view_duration: int | None = None,
        referrer: str | None = None,
    ) -> ProfileView:
        """
        Record a new profile view.

        Args:
            db: Database session
            profile_user_id: ID of the user whose profile was viewed
            viewer_user_id: ID of the viewer (null for anonymous)
            viewer_company_id: ID of the viewer's company
            viewer_ip: IP address of the viewer
            viewer_user_agent: User agent string
            view_duration: Duration of the view in seconds
            referrer: Referrer URL

        Returns:
            The created ProfileView instance
        """
        profile_view = ProfileView(
            profile_user_id=profile_user_id,
            viewer_user_id=viewer_user_id,
            viewer_company_id=viewer_company_id,
            viewer_ip=viewer_ip,
            viewer_user_agent=viewer_user_agent,
            view_duration=view_duration,
            referrer=referrer,
            created_at=get_utc_now(),
        )

        db.add(profile_view)
        await db.commit()
        await db.refresh(profile_view)

        return profile_view

    async def get_profile_views_by_user(
        self,
        db: AsyncSession,
        *,
        profile_user_id: int,
        skip: int = 0,
        limit: int = 100,
        include_anonymous: bool = True,
    ) -> list[ProfileView]:
        """
        Get all profile views for a specific user.

        Args:
            db: Database session
            profile_user_id: ID of the user whose profile views to retrieve
            skip: Number of records to skip
            limit: Maximum number of records to return
            include_anonymous: Whether to include anonymous views

        Returns:
            List of ProfileView instances
        """
        query = select(ProfileView).where(
            ProfileView.profile_user_id == profile_user_id
        )

        if not include_anonymous:
            query = query.where(ProfileView.viewer_user_id.isnot(None))

        query = (
            query.options(
                selectinload(ProfileView.viewer_user),
                selectinload(ProfileView.profile_user),
            )
            .order_by(desc(ProfileView.created_at))
            .offset(skip)
            .limit(limit)
        )

        result = await db.execute(query)
        return result.scalars().all()

    async def get_profile_views_stats(
        self,
        db: AsyncSession,
        *,
        profile_user_id: int,
        days: int | None = None,
    ) -> dict[str, Any]:
        """
        Get aggregated statistics for profile views.

        Args:
            db: Database session
            profile_user_id: ID of the user whose profile stats to retrieve
            days: Number of days to look back (None for all time)

        Returns:
            Dictionary with view statistics
        """
        # Base query
        query = select(ProfileView).where(
            ProfileView.profile_user_id == profile_user_id
        )

        # Filter by date range if specified
        if days:
            cutoff_date = get_utc_now() - timedelta(days=days)
            query = query.where(ProfileView.created_at >= cutoff_date)

        # Total views
        total_views_query = select(func.count()).select_from(query.subquery())
        total_views_result = await db.execute(total_views_query)
        total_views = total_views_result.scalar() or 0

        # Unique viewers
        unique_viewers_query = (
            select(func.count(func.distinct(ProfileView.viewer_user_id)))
            .select_from(query.subquery())
            .where(ProfileView.viewer_user_id.isnot(None))
        )
        unique_viewers_result = await db.execute(unique_viewers_query)
        unique_viewers = unique_viewers_result.scalar() or 0

        # Views by company (top 5)
        base_filter = ProfileView.profile_user_id == profile_user_id
        if days:
            cutoff_date = get_utc_now() - timedelta(days=days)
            base_filter = and_(base_filter, ProfileView.created_at >= cutoff_date)

        views_by_company_query = (
            select(
                ProfileView.viewer_company_id,
                Company.name.label("company_name"),
                func.count(ProfileView.id).label("view_count"),
            )
            .join(Company, ProfileView.viewer_company_id == Company.id)
            .where(and_(base_filter, ProfileView.viewer_company_id.isnot(None)))
            .group_by(ProfileView.viewer_company_id, Company.name)
            .order_by(desc("view_count"))
            .limit(5)
        )
        views_by_company_result = await db.execute(views_by_company_query)
        views_by_company = [
            {"company_id": row[0], "company_name": row[1], "view_count": row[2]}
            for row in views_by_company_result.all()
        ]

        # Views over time (last 30 days, grouped by day)
        if days and days <= 30:
            views_over_time_query = (
                select(
                    func.date(ProfileView.created_at).label("date"),
                    func.count(ProfileView.id).label("count"),
                )
                .where(base_filter)
                .group_by(func.date(ProfileView.created_at))
                .order_by("date")
            )
            views_over_time_result = await db.execute(views_over_time_query)
            views_over_time = [
                {"date": str(row[0]), "count": row[1]}
                for row in views_over_time_result.all()
            ]
        else:
            views_over_time = []

        return {
            "total_views": total_views,
            "unique_viewers": unique_viewers,
            "views_by_company": views_by_company,
            "views_over_time": views_over_time,
        }

    async def get_recent_viewers(
        self,
        db: AsyncSession,
        *,
        profile_user_id: int,
        limit: int = 10,
        days: int | None = 30,
    ) -> list[dict[str, Any]]:
        """
        Get list of recent profile viewers with details.

        Args:
            db: Database session
            profile_user_id: ID of the user whose profile viewers to retrieve
            limit: Maximum number of viewers to return
            days: Number of days to look back

        Returns:
            List of viewer details
        """
        query = (
            select(
                ProfileView.viewer_user_id,
                User.first_name,
                User.last_name,
                User.email,
                User.company_id,
                Company.name.label("company_name"),
                func.max(ProfileView.created_at).label("last_viewed"),
                func.count(ProfileView.id).label("view_count"),
            )
            .join(User, ProfileView.viewer_user_id == User.id)
            .outerjoin(Company, User.company_id == Company.id)
            .where(
                and_(
                    ProfileView.profile_user_id == profile_user_id,
                    ProfileView.viewer_user_id.isnot(None),
                )
            )
        )

        # Filter by date range if specified
        if days:
            cutoff_date = get_utc_now() - timedelta(days=days)
            query = query.where(ProfileView.created_at >= cutoff_date)

        query = (
            query.group_by(
                ProfileView.viewer_user_id,
                User.first_name,
                User.last_name,
                User.email,
                User.company_id,
                Company.name,
            )
            .order_by(desc("last_viewed"))
            .limit(limit)
        )

        result = await db.execute(query)
        viewers = []
        for row in result.all():
            viewers.append(
                {
                    "viewer_user_id": row[0],
                    "first_name": row[1],
                    "last_name": row[2],
                    "email": row[3],
                    "company_id": row[4],
                    "company_name": row[5],
                    "last_viewed": row[6],
                    "view_count": row[7],
                }
            )

        return viewers

    async def get_profile_view_count(
        self,
        db: AsyncSession,
        *,
        profile_user_id: int,
        days: int | None = None,
    ) -> int:
        """
        Get total view count for a profile.

        Args:
            db: Database session
            profile_user_id: ID of the user whose profile view count to retrieve
            days: Number of days to look back (None for all time)

        Returns:
            Total view count
        """
        query = select(func.count()).where(
            ProfileView.profile_user_id == profile_user_id
        )

        # Filter by date range if specified
        if days:
            cutoff_date = get_utc_now() - timedelta(days=days)
            query = query.where(ProfileView.created_at >= cutoff_date)

        result = await db.execute(query)
        return result.scalar() or 0

    async def delete_old_views(
        self,
        db: AsyncSession,
        *,
        days: int = 365,
    ) -> int:
        """
        Delete profile views older than specified days (for data retention).

        Args:
            db: Database session
            days: Delete views older than this many days

        Returns:
            Number of deleted records
        """
        cutoff_date = get_utc_now() - timedelta(days=days)

        result = await db.execute(
            select(ProfileView).where(ProfileView.created_at < cutoff_date)
        )
        views_to_delete = result.scalars().all()

        for view in views_to_delete:
            await db.delete(view)

        await db.commit()

        return len(views_to_delete)


# Create singleton instance
profile_view = CRUDProfileView()
