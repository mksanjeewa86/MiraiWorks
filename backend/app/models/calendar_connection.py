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
from sqlalchemy.sql import func

from app.models.base import BaseModel


class CalendarConnection(BaseModel):
    __tablename__ = "calendar_connections"

    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Provider information
    provider: Mapped[str] = mapped_column(String(20), nullable=False)
    provider_account_id: Mapped[str] = mapped_column(String(255), nullable=False)
    provider_email: Mapped[str] = mapped_column(
        String(255), nullable=False
    )  # Email associated with the provider account

    # OAuth tokens (encrypted)
    access_token: Mapped[str] = mapped_column(Text, nullable=False)
    refresh_token: Mapped[str | None] = mapped_column(Text, nullable=True)
    token_expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Calendar sync settings
    is_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    sync_events: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    sync_reminders: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    auto_create_meetings: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False
    )

    # Sync preferences
    calendar_ids: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    default_calendar_id: Mapped[str | None] = mapped_column(
        String(255), nullable=True
    )  # Default calendar for creating events

    # Connection metadata
    display_name: Mapped[str | None] = mapped_column(
        String(255), nullable=True
    )  # User-friendly name for this connection
    last_sync_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    sync_error: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    user = relationship("User", back_populates="calendar_connections")

    def __repr__(self):
        return f"<CalendarConnection(id={self.id}, user_id={self.user_id}, provider={self.provider})>"

    @property
    def is_token_expired(self):
        """Check if the access token is expired"""
        if not self.token_expires_at:
            return False
        return self.token_expires_at < func.now()

    @property
    def status(self):
        """Get the connection status"""
        if not self.is_enabled:
            return "disabled"
        elif self.sync_error:
            return "error"
        elif self.token_expires_at and self.token_expires_at < func.now():  # type: ignore[operator]
            return "expired"
        else:
            return "connected"
