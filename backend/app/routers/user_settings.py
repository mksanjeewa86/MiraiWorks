from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.models import User, UserSettings

router = APIRouter()


class UserSettingsResponse(BaseModel):
    # Profile settings
    job_title: Optional[str] = None
    bio: Optional[str] = None
    
    # Notification preferences
    email_notifications: bool = True
    push_notifications: bool = True
    sms_notifications: bool = False
    interview_reminders: bool = True
    application_updates: bool = True
    message_notifications: bool = True
    
    # UI preferences
    theme: str = "system"
    language: str = "en"
    timezone: str = "America/New_York"
    date_format: str = "MM/DD/YYYY"
    
    # Security settings (from User model)
    require_2fa: bool = False

    class Config:
        from_attributes = True


class UserSettingsUpdate(BaseModel):
    # Profile settings
    job_title: Optional[str] = None
    bio: Optional[str] = None
    
    # Notification preferences
    email_notifications: Optional[bool] = None
    push_notifications: Optional[bool] = None
    sms_notifications: Optional[bool] = None
    interview_reminders: Optional[bool] = None
    application_updates: Optional[bool] = None
    message_notifications: Optional[bool] = None
    
    # UI preferences
    theme: Optional[str] = None
    language: Optional[str] = None
    timezone: Optional[str] = None
    date_format: Optional[str] = None
    
    # Security settings (from User model)
    require_2fa: Optional[bool] = None


class UserProfileUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    job_title: Optional[str] = None
    bio: Optional[str] = None


class UserProfileResponse(BaseModel):
    id: int
    email: str
    first_name: str
    last_name: str
    phone: Optional[str] = None
    full_name: str
    job_title: Optional[str] = None
    bio: Optional[str] = None

    class Config:
        from_attributes = True


@router.get("/settings", response_model=UserSettingsResponse)
async def get_user_settings(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get current user's settings."""
    result = await db.execute(
        select(UserSettings).where(UserSettings.user_id == current_user.id)
    )
    settings = result.scalar_one_or_none()
    
    if not settings:
        # Create default settings if they don't exist
        settings = UserSettings(user_id=current_user.id)
        db.add(settings)
        await db.commit()
        await db.refresh(settings)
    
    # Combine settings from UserSettings and User models
    # SMS notifications should be false if user has no phone number
    sms_notifications = settings.sms_notifications
    if not current_user.phone or not current_user.phone.strip():
        sms_notifications = False
    
    return UserSettingsResponse(
        # Profile settings (from UserSettings)
        job_title=settings.job_title,
        bio=settings.bio,
        # Notification preferences (from UserSettings)
        email_notifications=settings.email_notifications,
        push_notifications=settings.push_notifications,
        sms_notifications=sms_notifications,
        interview_reminders=settings.interview_reminders,
        application_updates=settings.application_updates,
        message_notifications=settings.message_notifications,
        # UI preferences (from UserSettings)
        theme=settings.theme,
        language=settings.language,
        timezone=settings.timezone,
        date_format=settings.date_format,
        # Security settings (from User)
        require_2fa=current_user.require_2fa
    )


@router.put("/settings", response_model=UserSettingsResponse)
async def update_user_settings(
    settings_update: UserSettingsUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update current user's settings."""
    result = await db.execute(
        select(UserSettings).where(UserSettings.user_id == current_user.id)
    )
    settings = result.scalar_one_or_none()
    
    if not settings:
        settings = UserSettings(user_id=current_user.id)
        db.add(settings)
    
    # Update only provided fields
    update_data = settings_update.model_dump(exclude_unset=True)
    
    # Validate SMS notifications require a phone number
    if 'sms_notifications' in update_data and update_data['sms_notifications']:
        if not current_user.phone or not current_user.phone.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="SMS notifications require a phone number. Please add your phone number in your profile first."
            )
    
    # Separate UserSettings fields and User fields
    user_fields = {'require_2fa'}
    settings_fields = {k: v for k, v in update_data.items() if k not in user_fields}
    user_field_updates = {k: v for k, v in update_data.items() if k in user_fields}
    
    # Update UserSettings fields
    for field, value in settings_fields.items():
        if hasattr(settings, field):
            setattr(settings, field, value)
    
    # Update User fields
    for field, value in user_field_updates.items():
        if hasattr(current_user, field):
            setattr(current_user, field, value)
    
    await db.commit()
    await db.refresh(settings)
    await db.refresh(current_user)
    
    # Return combined response
    # SMS notifications should be false if user has no phone number
    sms_notifications = settings.sms_notifications
    if not current_user.phone or not current_user.phone.strip():
        sms_notifications = False
        
    return UserSettingsResponse(
        # Profile settings (from UserSettings)
        job_title=settings.job_title,
        bio=settings.bio,
        # Notification preferences (from UserSettings)
        email_notifications=settings.email_notifications,
        push_notifications=settings.push_notifications,
        sms_notifications=sms_notifications,
        interview_reminders=settings.interview_reminders,
        application_updates=settings.application_updates,
        message_notifications=settings.message_notifications,
        # UI preferences (from UserSettings)
        theme=settings.theme,
        language=settings.language,
        timezone=settings.timezone,
        date_format=settings.date_format,
        # Security settings (from User)
        require_2fa=current_user.require_2fa
    )


@router.get("/profile", response_model=UserProfileResponse)
async def get_user_profile(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get current user's profile information."""
    # Get user with settings
    result = await db.execute(
        select(UserSettings).where(UserSettings.user_id == current_user.id)
    )
    user_settings = result.scalar_one_or_none()
    
    return {
        "id": current_user.id,
        "email": current_user.email,
        "first_name": current_user.first_name,
        "last_name": current_user.last_name,
        "phone": current_user.phone,
        "full_name": current_user.full_name,
        "job_title": user_settings.job_title if user_settings else None,
        "bio": user_settings.bio if user_settings else None,
    }


@router.put("/profile", response_model=UserProfileResponse)
async def update_user_profile(
    profile_update: UserProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update current user's profile information."""
    update_data = profile_update.model_dump(exclude_unset=True)
    
    # Update user fields
    user_fields = {"first_name", "last_name", "phone"}
    for field, value in update_data.items():
        if field in user_fields and hasattr(current_user, field):
            setattr(current_user, field, value)
    
    # Update settings fields (job_title, bio)
    settings_fields = {"job_title", "bio"}
    settings_data = {k: v for k, v in update_data.items() if k in settings_fields}
    
    if settings_data:
        result = await db.execute(
            select(UserSettings).where(UserSettings.user_id == current_user.id)
        )
        settings = result.scalar_one_or_none()
        if not settings:
            settings = UserSettings(user_id=current_user.id)
            db.add(settings)
        
        for field, value in settings_data.items():
            setattr(settings, field, value)
    
    await db.commit()
    await db.refresh(current_user)
    
    # Return updated profile
    result = await db.execute(
        select(UserSettings).where(UserSettings.user_id == current_user.id)
    )
    user_settings = result.scalar_one_or_none()
    
    return {
        "id": current_user.id,
        "email": current_user.email,
        "first_name": current_user.first_name,
        "last_name": current_user.last_name,
        "phone": current_user.phone,
        "full_name": current_user.full_name,
        "job_title": user_settings.job_title if user_settings else None,
        "bio": user_settings.bio if user_settings else None,
    }