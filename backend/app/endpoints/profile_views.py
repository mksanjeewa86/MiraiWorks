"""Profile views API endpoints."""

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.endpoints import API_ROUTES
from app.crud.profile_views import profile_view as profile_view_crud
from app.database import get_db
from app.endpoints.auth import get_current_active_user
from app.models.user import User
from app.schemas.profile_view import (
    ProfileViewCreate,
    ProfileViewInfo,
    ProfileViewStats,
    RecentViewer,
)

router = APIRouter(prefix="/profile-views", tags=["profile-views"])


@router.post(
    API_ROUTES.PROFILE_VIEWS.BASE, response_model=ProfileViewInfo, status_code=201
)
async def record_profile_view(
    *,
    db: AsyncSession = Depends(get_db),
    profile_view_data: ProfileViewCreate,
    request: Request,
    current_user: User | None = Depends(get_current_active_user),
) -> ProfileViewInfo:
    """
    Record a profile view.

    This endpoint is called when someone views a profile.
    Can be called by authenticated users or anonymously.
    """
    # Prevent self-views
    if current_user and current_user.id == profile_view_data.profile_user_id:
        raise HTTPException(
            status_code=400,
            detail="Cannot record view of own profile",
        )

    # Extract viewer information
    viewer_user_id = current_user.id if current_user else None
    viewer_company_id = current_user.company_id if current_user else None

    # Get IP address from request
    viewer_ip = request.client.host if request.client else None

    # Get user agent from headers
    viewer_user_agent = request.headers.get("user-agent")

    # Create the profile view
    profile_view = await profile_view_crud.create_profile_view(
        db,
        profile_user_id=profile_view_data.profile_user_id,
        viewer_user_id=viewer_user_id,
        viewer_company_id=viewer_company_id,
        viewer_ip=viewer_ip,
        viewer_user_agent=viewer_user_agent,
        view_duration=profile_view_data.view_duration,
        referrer=profile_view_data.referrer,
    )

    return ProfileViewInfo(
        id=profile_view.id,
        profile_user_id=profile_view.profile_user_id,
        viewer_user_id=profile_view.viewer_user_id,
        viewer_company_id=profile_view.viewer_company_id,
        viewer_ip=profile_view.viewer_ip,
        viewer_user_agent=profile_view.viewer_user_agent,
        view_duration=profile_view.view_duration,
        referrer=profile_view.referrer,
        created_at=profile_view.created_at,
    )


@router.get(API_ROUTES.PROFILE_VIEWS.MY_VIEWS, response_model=list[ProfileViewInfo])
async def get_my_profile_views(
    *,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    skip: int = 0,
    limit: int = 100,
    include_anonymous: bool = True,
) -> list[ProfileViewInfo]:
    """
    Get all profile views for the current user's profile.

    Returns a list of views with viewer information.
    """
    views = await profile_view_crud.get_profile_views_by_user(
        db,
        profile_user_id=current_user.id,
        skip=skip,
        limit=limit,
        include_anonymous=include_anonymous,
    )

    return [
        ProfileViewInfo(
            id=view.id,
            profile_user_id=view.profile_user_id,
            viewer_user_id=view.viewer_user_id,
            viewer_company_id=view.viewer_company_id,
            viewer_ip=view.viewer_ip,
            viewer_user_agent=view.viewer_user_agent,
            view_duration=view.view_duration,
            referrer=view.referrer,
            created_at=view.created_at,
        )
        for view in views
    ]


@router.get(API_ROUTES.PROFILE_VIEWS.STATS, response_model=ProfileViewStats)
async def get_profile_view_stats(
    *,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    days: int | None = None,
) -> ProfileViewStats:
    """
    Get aggregated statistics for the current user's profile views.

    Args:
        days: Number of days to look back (None for all time)

    Returns:
        Statistics including total views, unique viewers, views by company, etc.
    """
    stats = await profile_view_crud.get_profile_views_stats(
        db,
        profile_user_id=current_user.id,
        days=days,
    )

    return ProfileViewStats(**stats)


@router.get(API_ROUTES.PROFILE_VIEWS.RECENT_VIEWERS, response_model=list[RecentViewer])
async def get_recent_viewers(
    *,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    limit: int = 10,
    days: int | None = 30,
) -> list[RecentViewer]:
    """
    Get list of recent profile viewers with details.

    Args:
        limit: Maximum number of viewers to return
        days: Number of days to look back

    Returns:
        List of recent viewers with their information
    """
    viewers = await profile_view_crud.get_recent_viewers(
        db,
        profile_user_id=current_user.id,
        limit=limit,
        days=days,
    )

    return [RecentViewer(**viewer) for viewer in viewers]


@router.get(API_ROUTES.PROFILE_VIEWS.COUNT)
async def get_profile_view_count(
    *,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    days: int | None = None,
) -> dict:
    """
    Get total view count for the current user's profile.

    Args:
        days: Number of days to look back (None for all time)

    Returns:
        Dictionary with the view count
    """
    count = await profile_view_crud.get_profile_view_count(
        db,
        profile_user_id=current_user.id,
        days=days,
    )

    return {"count": count}
