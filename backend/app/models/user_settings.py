from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class UserSettings(Base):
    __tablename__ = "user_settings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    
    # Profile settings
    job_title = Column(String(200), nullable=True)
    bio = Column(Text, nullable=True)
    
    # Notification preferences
    email_notifications = Column(Boolean, nullable=False, default=True)
    push_notifications = Column(Boolean, nullable=False, default=True)
    sms_notifications = Column(Boolean, nullable=False, default=False)
    interview_reminders = Column(Boolean, nullable=False, default=True)
    application_updates = Column(Boolean, nullable=False, default=True)
    message_notifications = Column(Boolean, nullable=False, default=True)
    
    # UI preferences
    language = Column(String(10), nullable=False, default="en")
    timezone = Column(String(50), nullable=False, default="America/New_York")
    date_format = Column(String(20), nullable=False, default="MM/DD/YYYY")
    
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
    user = relationship("User", back_populates="settings")

    def __repr__(self):
        return f"<UserSettings(id={self.id}, user_id={self.user_id})>"