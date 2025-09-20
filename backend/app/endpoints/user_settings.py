from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import user_settings as user_settings_crud
from app.database import get_db
from app.dependencies import get_current_user
from app.models import User
from app.schemas.user_settings import (
    UserProfileResponse,
    UserProfileUpdate,
    UserSettingsResponse,
    UserSettingsUpdate,
)

router = APIRouter()


@router.get("/settings", response_model=UserSettingsResponse)
async def get_user_settings(
    current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    """Get current user's settings."""
    settings = await user_settings_crud.get_or_create_user_settings(db, current_user.id)

    # Combine settings from UserSettings and User models
    # SMS notifications should be false if user has no phone number
    sms_notifications = settings.sms_notifications
    if not current_user.phone or not current_user.phone.strip():
        sms_notifications = False

    return UserSettingsResponse(
        # Profile settings (from UserSettings)
        job_title=settings.job_title,
        bio=settings.bio,
        avatar_url=settings.avatar_url,
        # Notification preferences (from UserSettings)
        email_notifications=settings.email_notifications,
        push_notifications=settings.push_notifications,
        sms_notifications=sms_notifications,
        interview_reminders=settings.interview_reminders,
        application_updates=settings.application_updates,
        message_notifications=settings.message_notifications,
        # UI preferences (from UserSettings)
        language=settings.language,
        timezone=settings.timezone,
        date_format=settings.date_format,
        # Security settings (from User)
        require_2fa=current_user.require_2fa,
    )


@router.put("/settings", response_model=UserSettingsResponse)
async def update_user_settings(
    settings_update: UserSettingsUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update current user's settings."""
    update_data = settings_update.model_dump(exclude_unset=True)

    # Validate SMS notifications require a phone number
    if "sms_notifications" in update_data and update_data["sms_notifications"]:
        if not current_user.phone or not current_user.phone.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="SMS notifications require a phone number. Please add your phone number in your profile first.",
            )

    # Separate UserSettings fields and User fields
    user_fields = {"require_2fa"}
    settings_fields = {k: v for k, v in update_data.items() if k not in user_fields}
    user_field_updates = {k: v for k, v in update_data.items() if k in user_fields}

    # Update user settings
    settings = await user_settings_crud.get_or_create_user_settings(db, current_user.id)
    if settings_fields:
        settings = await user_settings_crud.update_user_settings(
            db, settings, settings_fields
        )

    # Update user profile fields if needed
    if user_field_updates:
        current_user = await user_settings_crud.update_user_profile(
            db, current_user, user_field_updates
        )

    # Return combined response
    # SMS notifications should be false if user has no phone number
    sms_notifications = settings.sms_notifications
    if not current_user.phone or not current_user.phone.strip():
        sms_notifications = False

    return UserSettingsResponse(
        # Profile settings (from UserSettings)
        job_title=settings.job_title,
        bio=settings.bio,
        avatar_url=settings.avatar_url,
        # Notification preferences (from UserSettings)
        email_notifications=settings.email_notifications,
        push_notifications=settings.push_notifications,
        sms_notifications=sms_notifications,
        interview_reminders=settings.interview_reminders,
        application_updates=settings.application_updates,
        message_notifications=settings.message_notifications,
        # UI preferences (from UserSettings)
        language=settings.language,
        timezone=settings.timezone,
        date_format=settings.date_format,
        # Security settings (from User)
        require_2fa=current_user.require_2fa,
    )


@router.get("/profile", response_model=UserProfileResponse)
async def get_user_profile(
    current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    """Get current user's profile information."""
    user_settings = await user_settings_crud.get_user_settings_by_user_id(
        db, current_user.id
    )

    return UserProfileResponse(
        id=current_user.id,
        email=current_user.email,
        first_name=current_user.first_name,
        last_name=current_user.last_name,
        phone=current_user.phone,
        full_name=current_user.full_name,
        job_title=user_settings.job_title if user_settings else None,
        bio=user_settings.bio if user_settings else None,
        avatar_url=user_settings.avatar_url if user_settings else None,
    )


@router.put("/profile", response_model=UserProfileResponse)
async def update_user_profile(
    profile_update: UserProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update current user's profile information."""
    update_data = profile_update.model_dump(exclude_unset=True)

    # Separate user fields and settings fields
    user_fields = {"first_name", "last_name", "phone"}
    settings_fields = {"job_title", "bio", "avatar_url"}

    user_data = {k: v for k, v in update_data.items() if k in user_fields}
    settings_data = {k: v for k, v in update_data.items() if k in settings_fields}

    # Update user fields if any
    if user_data:
        current_user = await user_settings_crud.update_user_profile(
            db, current_user, user_data
        )

    # Update settings fields if any
    user_settings = None
    if settings_data:
        user_settings = await user_settings_crud.get_or_create_user_settings(
            db, current_user.id
        )
        user_settings = await user_settings_crud.update_user_settings(
            db, user_settings, settings_data
        )
    else:
        user_settings = await user_settings_crud.get_user_settings_by_user_id(
            db, current_user.id
        )

    return UserProfileResponse(
        id=current_user.id,
        email=current_user.email,
        first_name=current_user.first_name,
        last_name=current_user.last_name,
        phone=current_user.phone,
        full_name=current_user.full_name,
        job_title=user_settings.job_title if user_settings else None,
        bio=user_settings.bio if user_settings else None,
        avatar_url=user_settings.avatar_url if user_settings else None,
    )
