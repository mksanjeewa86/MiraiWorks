from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel


class CalendarEvent(BaseModel):
    __tablename__ = "calendar_events"
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    start_datetime: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, index=True
    )
    end_datetime: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    is_all_day: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    location: Mapped[str | None] = mapped_column(String(255), nullable=True)
    event_type: Mapped[str] = mapped_column(
        String(50), default="event", nullable=False, index=True
    )
    status: Mapped[str] = mapped_column(
        String(20), default="confirmed", nullable=False, index=True
    )
    creator_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    recurrence_rule: Mapped[str | None] = mapped_column(String(255), nullable=True)
    parent_event_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("calendar_events.id", ondelete="CASCADE"), nullable=True
    )
    timezone: Mapped[str] = mapped_column(String(50), default="UTC", nullable=False)

    # Relationships
    creator = relationship("User", back_populates="calendar_events")
    attendees = relationship(
        "CalendarEventAttendee",
        back_populates="event",
        cascade="all, delete-orphan",
    )
    parent_event = relationship(
        "CalendarEvent",
        remote_side="calendar_events.c.id",
        back_populates="child_events",
        foreign_keys=[parent_event_id],
    )
    child_events = relationship(
        "CalendarEvent",
        back_populates="parent_event",
        foreign_keys="CalendarEvent.parent_event_id",
    )

    def __str__(self) -> str:
        return f"CalendarEvent(id={self.id}, title='{self.title}', start={self.start_datetime})"

    def __repr__(self) -> str:
        return self.__str__()

    @property
    def is_recurring(self) -> bool:
        """Check if this event has a recurrence rule."""
        return self.recurrence_rule is not None

    @property
    def is_instance(self) -> bool:
        """Check if this is an instance of a recurring event."""
        return self.parent_event_id is not None
