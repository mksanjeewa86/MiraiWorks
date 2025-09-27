
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User, UserSettings


async def get_user_settings(db: AsyncSession, user_id: int) -> UserSettings | None:
    """Get user settings by user ID."""
    result = await db.execute(
        select(UserSettings).where(UserSettings.user_id == user_id)
    )
    return result.scalar_one_or_none()


async def create_user_settings(
    db: AsyncSession, user_id: int, settings_data: dict
) -> UserSettings:
    """Create user settings."""
    settings = UserSettings(user_id=user_id, **settings_data)
    db.add(settings)
    await db.commit()
    await db.refresh(settings)
    return settings


async def update_user_settings(
    db: AsyncSession, settings: UserSettings, update_data: dict
) -> UserSettings:
    """Update user settings."""
    for field, value in update_data.items():
        if value is not None:
            setattr(settings, field, value)

    await db.commit()
    await db.refresh(settings)
    return settings


async def get_or_create_user_settings(db: AsyncSession, user_id: int) -> UserSettings:
    """Get user settings or create with defaults if not exists."""
    settings = await get_user_settings(db, user_id)
    if not settings:
        settings = await create_user_settings(db, user_id, {})
    return settings


async def update_user_profile(db: AsyncSession, user: User, profile_data: dict) -> User:
    """Update user profile information."""
    for field, value in profile_data.items():
        if value is not None:
            setattr(user, field, value)

    await db.commit()
    await db.refresh(user)
    return user


# Alias for backward compatibility
async def get_user_settings_by_user_id(
    db: AsyncSession, user_id: int
) -> UserSettings | None:
    """Get user settings by user ID (alias for get_user_settings)."""
    return await get_user_settings(db, user_id)
