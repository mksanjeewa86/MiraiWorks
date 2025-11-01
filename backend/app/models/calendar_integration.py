from datetime import datetime

from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel


class ExternalCalendarAccount(BaseModel):
    __tablename__ = "external_calendar_accounts"

    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    provider: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    provider_account_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    email: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    display_name: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # OAuth tokens (encrypted in production)
    access_token: Mapped[str | None] = mapped_column(Text, nullable=True)
    refresh_token: Mapped[str | None] = mapped_column(Text, nullable=True)
    token_expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Calendar-specific data
    calendar_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    calendar_timezone: Mapped[str | None] = mapped_column(String(100), nullable=True, default="UTC")

    # Sync settings
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, index=True)
    sync_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    last_sync_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    sync_token: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Webhook settings
    webhook_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    webhook_expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    user = relationship("User")
    synced_events = relationship(
        "SyncedEvent", back_populates="calendar_account", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<ExternalCalendarAccount(id={self.id}, user_id={self.user_id}, provider='{self.provider}', email='{self.email}')>"

    @classmethod
    async def get_by_channel_id(cls, db, channel_id: str):
        """Get calendar account by webhook channel ID."""
        from sqlalchemy import select

        result = await db.execute(select(cls).where(cls.webhook_id == channel_id))
        return result.scalars().first()

    @classmethod
    async def get_by_subscription_id(cls, db, subscription_id: str):
        """Get calendar account by subscription ID."""
        from sqlalchemy import select

        result = await db.execute(select(cls).where(cls.webhook_id == subscription_id))
        return result.scalars().first()

    @classmethod
    async def get(cls, db, account_id: int):
        """Get calendar account by ID."""
        from sqlalchemy import select

        result = await db.execute(select(cls).where(cls.id == account_id))
        return result.scalars().first()

    async def save(self, db):
        """Save the calendar account to database."""
        db.add(self)
        await db.commit()
        await db.refresh(self)


class SyncedEvent(BaseModel):
    __tablename__ = "synced_events"

    calendar_account_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("external_calendar_accounts.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # External event data
    external_event_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    external_calendar_id: Mapped[str] = mapped_column(String(255), nullable=False)

    # Event details
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    location: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # Timing
    start_datetime: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    end_datetime: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    timezone: Mapped[str | None] = mapped_column(String(100), nullable=True)
    is_all_day: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    # Event metadata
    is_recurring: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    recurrence_rule: Mapped[str | None] = mapped_column(Text, nullable=True)
    organizer_email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    attendees: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    # Sync metadata
    event_status: Mapped[str | None] = mapped_column(String(50), nullable=True)
    visibility: Mapped[str | None] = mapped_column(
        String(50), nullable=True, default="default"
    )  # public, private, default
    last_modified: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    etag: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Internal linking
    interview_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("interviews.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # Relationships
    calendar_account = relationship(
        "ExternalCalendarAccount", back_populates="synced_events"
    )
    interview = relationship("Interview", back_populates="synced_events")

    def __repr__(self):
        return f"<SyncedEvent(id={self.id}, title='{self.title}', start={self.start_datetime})>"

    @classmethod
    async def get_by_external_id(cls, db, external_event_id: str):
        """Get synced event by external event ID."""
        from sqlalchemy import select

        result = await db.execute(
            select(cls).where(cls.external_event_id == external_event_id)
        )
        return result.scalars().first()

    @classmethod
    async def delete_by_external_id(cls, db, external_event_id: str):
        """Delete synced event by external event ID."""
        from sqlalchemy import delete

        await db.execute(delete(cls).where(cls.external_event_id == external_event_id))
        await db.commit()

    async def save(self, db):
        """Save the synced event to database."""
        db.add(self)
        await db.commit()
        await db.refresh(self)
