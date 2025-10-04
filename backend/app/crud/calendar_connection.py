from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models.calendar_connection import CalendarConnection
from app.schemas.calendar_connection import (
    CalendarConnectionCreate,
    CalendarConnectionUpdate,
)


class CRUDCalendarConnection(
    CRUDBase[CalendarConnection, CalendarConnectionCreate, CalendarConnectionUpdate]
):
    """Calendar connection CRUD operations."""

    async def get_by_user(
        self, db: AsyncSession, user_id: int
    ) -> list[CalendarConnection]:
        """Get all calendar connections for a user."""
        result = await db.execute(
            select(CalendarConnection).where(CalendarConnection.user_id == user_id)
        )
        return result.scalars().all()

    async def get_by_user_and_id(
        self, db: AsyncSession, user_id: int, connection_id: int
    ) -> CalendarConnection | None:
        """Get a specific calendar connection for a user."""
        result = await db.execute(
            select(CalendarConnection).where(
                CalendarConnection.id == connection_id,
                CalendarConnection.user_id == user_id,
            )
        )
        return result.scalar_one_or_none()

    async def get_enabled_by_user(
        self, db: AsyncSession, user_id: int
    ) -> list[CalendarConnection]:
        """Get enabled calendar connections for a user."""
        result = await db.execute(
            select(CalendarConnection).where(
                CalendarConnection.user_id == user_id,
                CalendarConnection.is_enabled is True,
            )
        )
        return result.scalars().all()

    async def get_by_provider_and_user(
        self, db: AsyncSession, user_id: int, provider: str
    ) -> CalendarConnection | None:
        """Get calendar connection by provider and user."""
        result = await db.execute(
            select(CalendarConnection).where(
                CalendarConnection.user_id == user_id,
                CalendarConnection.provider == provider,
            )
        )
        return result.scalar_one_or_none()


# Create the CRUD instance
calendar_connection = CRUDCalendarConnection(CalendarConnection)
