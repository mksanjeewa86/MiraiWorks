"""Recruiter profile endpoints"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.endpoints import API_ROUTES
from app.crud.recruiter_profile import recruiter_profile as recruiter_profile_crud
from app.database import get_db
from app.endpoints.auth import get_current_active_user
from app.models.user import User
from app.schemas.recruiter_profile import (
    RecruiterProfileCreate,
    RecruiterProfileInfo,
    RecruiterProfileUpdate,
)

router = APIRouter()


@router.get(API_ROUTES.RECRUITER_PROFILE.ME, response_model=RecruiterProfileInfo)
async def get_my_recruiter_profile(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get current user's recruiter profile"""
    profile = await recruiter_profile_crud.get_by_user(db, user_id=current_user.id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recruiter profile not found"
        )
    return profile


@router.post(API_ROUTES.RECRUITER_PROFILE.ME, response_model=RecruiterProfileInfo, status_code=status.HTTP_201_CREATED)
async def create_my_recruiter_profile(
    profile_data: RecruiterProfileCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Create recruiter profile for current user"""
    # Check if profile already exists
    existing = await recruiter_profile_crud.get_by_user(db, user_id=current_user.id)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Recruiter profile already exists"
        )

    profile = await recruiter_profile_crud.create_for_user(
        db, obj_in=profile_data, user_id=current_user.id
    )
    return profile


@router.put(API_ROUTES.RECRUITER_PROFILE.ME, response_model=RecruiterProfileInfo)
async def update_my_recruiter_profile(
    profile_data: RecruiterProfileUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Update current user's recruiter profile"""
    profile = await recruiter_profile_crud.update_by_user(
        db, user_id=current_user.id, obj_in=profile_data
    )
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recruiter profile not found"
        )
    return profile


@router.delete(API_ROUTES.RECRUITER_PROFILE.ME, status_code=status.HTTP_204_NO_CONTENT)
async def delete_my_recruiter_profile(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Delete current user's recruiter profile"""
    success = await recruiter_profile_crud.delete_by_user(db, user_id=current_user.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recruiter profile not found"
        )
    return None


@router.get(API_ROUTES.RECRUITER_PROFILE.BY_USER_ID, response_model=RecruiterProfileInfo)
async def get_recruiter_profile_by_id(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get recruiter profile by user ID (public view with privacy respected)"""
    profile = await recruiter_profile_crud.get_by_user(db, user_id=user_id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recruiter profile not found"
        )
    return profile
