from sqlalchemy import Boolean, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel


class UserSettings(BaseModel):
    __tablename__ = "user_settings"
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )

    # Profile settings
    job_title: Mapped[str | None] = mapped_column(String(200), nullable=True)
    bio: Mapped[str | None] = mapped_column(Text, nullable=True)
    avatar_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    cover_photo_url: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # Notification preferences
    email_notifications: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    push_notifications: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    sms_notifications: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    interview_reminders: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    application_updates: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    message_notifications: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    # UI preferences
    language: Mapped[str] = mapped_column(String(10), nullable=False, default="en")
    timezone: Mapped[str] = mapped_column(String(50), nullable=False, default="America/New_York")
    date_format: Mapped[str] = mapped_column(String(20), nullable=False, default="MM/DD/YYYY")

    # Relationships
    user = relationship("User", back_populates="settings")

    def __repr__(self):
        return f"<UserSettings(id={self.id}, user_id={self.user_id})>"
