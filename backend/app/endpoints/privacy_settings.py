"""Privacy settings endpoints"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.endpoints import API_ROUTES
from app.crud.privacy_settings import privacy_settings as privacy_settings_crud
from app.database import get_db
from app.endpoints.auth import get_current_active_user
from app.models.user import User
from app.schemas.privacy_settings import (
    PrivacySettingsCreate,
    PrivacySettingsInfo,
    PrivacySettingsUpdate,
)

router = APIRouter()


@router.get(API_ROUTES.PRIVACY_SETTINGS.ME, response_model=PrivacySettingsInfo)
async def get_my_privacy_settings(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get current user's privacy settings (creates default if not exists)"""
    settings = await privacy_settings_crud.get_or_create(db, user_id=current_user.id)
    return settings


@router.put(API_ROUTES.PRIVACY_SETTINGS.ME, response_model=PrivacySettingsInfo)
async def update_my_privacy_settings(
    settings_data: PrivacySettingsUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Update current user's privacy settings"""
    # Get or create settings first
    await privacy_settings_crud.get_or_create(db, user_id=current_user.id)

    # Update settings
    settings = await privacy_settings_crud.update_by_user(
        db, user_id=current_user.id, obj_in=settings_data
    )

    if not settings:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Privacy settings not found"
        )

    return settings


@router.post(API_ROUTES.PRIVACY_SETTINGS.ME, response_model=PrivacySettingsInfo, status_code=status.HTTP_201_CREATED)
async def create_my_privacy_settings(
    settings_data: PrivacySettingsCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Create privacy settings for current user (if not exists)"""
    # Check if settings already exist
    existing = await privacy_settings_crud.get_by_user(db, user_id=current_user.id)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Privacy settings already exist"
        )

    settings = await privacy_settings_crud.create_for_user(
        db, user_id=current_user.id, obj_in=settings_data
    )
    return settings


@router.delete(API_ROUTES.PRIVACY_SETTINGS.ME, status_code=status.HTTP_204_NO_CONTENT)
async def delete_my_privacy_settings(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Delete current user's privacy settings (resets to default)"""
    success = await privacy_settings_crud.delete_by_user(db, user_id=current_user.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Privacy settings not found"
        )
    return None
