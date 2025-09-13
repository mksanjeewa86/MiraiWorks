from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from enum import Enum
import enum

from app.database import Base


class CalendarProvider(str, enum.Enum):
    GOOGLE = "google"
    OUTLOOK = "outlook"


class CalendarConnection(Base):
    __tablename__ = "calendar_connections"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Provider information
    provider = Column(String(20), nullable=False)  # 'google' or 'outlook'
    provider_account_id = Column(String(255), nullable=False)  # External account ID
    provider_email = Column(String(255), nullable=False)  # Email associated with the provider account
    
    # OAuth tokens (encrypted)
    access_token = Column(Text, nullable=False)
    refresh_token = Column(Text, nullable=True)
    token_expires_at = Column(DateTime(timezone=True), nullable=True)
    
    # Calendar sync settings
    is_enabled = Column(Boolean, nullable=False, default=True)
    sync_events = Column(Boolean, nullable=False, default=True)
    sync_reminders = Column(Boolean, nullable=False, default=True)
    auto_create_meetings = Column(Boolean, nullable=False, default=False)
    
    # Sync preferences
    calendar_ids = Column(JSON, nullable=True)  # List of calendar IDs to sync
    default_calendar_id = Column(String(255), nullable=True)  # Default calendar for creating events
    
    # Connection metadata
    display_name = Column(String(255), nullable=True)  # User-friendly name for this connection
    last_sync_at = Column(DateTime(timezone=True), nullable=True)
    sync_error = Column(Text, nullable=True)  # Last sync error message
    
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

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
        elif self.is_token_expired:
            return "expired"
        else:
            return "connected"