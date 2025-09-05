from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Boolean, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class ExternalCalendarAccount(Base):
    __tablename__ = "external_calendar_accounts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    provider = Column(String(50), nullable=False, index=True)  # 'google', 'microsoft'
    provider_account_id = Column(String(255), nullable=False, index=True)
    email = Column(String(255), nullable=False, index=True)
    display_name = Column(String(255), nullable=True)
    
    # OAuth tokens (encrypted in production)
    access_token = Column(Text, nullable=True)
    refresh_token = Column(Text, nullable=True)
    token_expires_at = Column(DateTime(timezone=True), nullable=True)
    
    # Calendar-specific data
    calendar_id = Column(String(255), nullable=True)  # Primary calendar ID
    calendar_timezone = Column(String(100), nullable=True, default='UTC')
    
    # Sync settings
    is_active = Column(Boolean, nullable=False, default=True, index=True)
    sync_enabled = Column(Boolean, nullable=False, default=True)
    last_sync_at = Column(DateTime(timezone=True), nullable=True)
    sync_token = Column(Text, nullable=True)  # For incremental sync
    
    # Webhook settings
    webhook_id = Column(String(255), nullable=True)  # Provider webhook/subscription ID
    webhook_expires_at = Column(DateTime(timezone=True), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    user = relationship("User")
    synced_events = relationship("SyncedEvent", back_populates="calendar_account", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<ExternalCalendarAccount(id={self.id}, user_id={self.user_id}, provider='{self.provider}', email='{self.email}')>"


class SyncedEvent(Base):
    __tablename__ = "synced_events"

    id = Column(Integer, primary_key=True, index=True)
    calendar_account_id = Column(Integer, ForeignKey("external_calendar_accounts.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # External event data
    external_event_id = Column(String(255), nullable=False, index=True)
    external_calendar_id = Column(String(255), nullable=False)
    
    # Event details
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    location = Column(String(500), nullable=True)
    
    # Timing
    start_datetime = Column(DateTime(timezone=True), nullable=False, index=True)
    end_datetime = Column(DateTime(timezone=True), nullable=False, index=True)
    timezone = Column(String(100), nullable=True)
    is_all_day = Column(Boolean, nullable=False, default=False)
    
    # Event metadata
    is_recurring = Column(Boolean, nullable=False, default=False)
    recurrence_rule = Column(Text, nullable=True)  # RRULE format
    organizer_email = Column(String(255), nullable=True)
    attendees = Column(JSON, nullable=True)  # List of attendee emails
    
    # Sync metadata
    event_status = Column(String(50), nullable=True)  # confirmed, cancelled, tentative
    visibility = Column(String(50), nullable=True, default='default')  # public, private, default
    last_modified = Column(DateTime(timezone=True), nullable=True)
    etag = Column(String(255), nullable=True)  # For conflict resolution
    
    # Internal linking
    interview_id = Column(Integer, ForeignKey("interviews.id", ondelete="SET NULL"), nullable=True, index=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    calendar_account = relationship("ExternalCalendarAccount", back_populates="synced_events")
    interview = relationship("Interview", back_populates="synced_events")
    
    def __repr__(self):
        return f"<SyncedEvent(id={self.id}, title='{self.title}', start={self.start_datetime})>"