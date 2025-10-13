"""Privacy settings endpoints - Section-specific privacy controls"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.endpoints import API_ROUTES
from app.crud.privacy_settings import privacy_settings as privacy_settings_crud
from app.database import get_db
from app.endpoints.auth import get_current_active_user
from app.models.user import User
from app.schemas.privacy_settings import (
    PrivacySettingsInfo,
    PrivacySettingsUpdate,
)

router = APIRouter()


@router.get(API_ROUTES.PRIVACY_SETTINGS.ME, response_model=PrivacySettingsInfo)
async def get_my_privacy_settings(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Get current user's privacy settings.

    Automatically creates default settings if they don't exist yet.
    Used by section-specific privacy toggles in the profile page.
    """
    settings = await privacy_settings_crud.get_or_create(db, user_id=current_user.id)
    return settings


@router.put(API_ROUTES.PRIVACY_SETTINGS.ME, response_model=PrivacySettingsInfo)
async def update_my_privacy_settings(
    settings_data: PrivacySettingsUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Update current user's privacy settings.

    Supports partial updates - only the fields provided will be updated.
    This allows section-specific privacy toggles to update individual fields.

    Example: {"show_work_experience": false} will only update that field.
    """
    # Get or create settings first (ensures settings always exist)
    await privacy_settings_crud.get_or_create(db, user_id=current_user.id)

    # Update settings with partial data
    settings = await privacy_settings_crud.update_by_user(
        db, user_id=current_user.id, obj_in=settings_data
    )

    return settings
