from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class CalendarEvent(BaseModel):
    __tablename__ = "calendar_events"
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    start_datetime = Column(DateTime(timezone=True), nullable=False, index=True)
    end_datetime = Column(DateTime(timezone=True), nullable=True)
    is_all_day = Column(Boolean, default=False, nullable=False)
    location = Column(String(255), nullable=True)
    event_type = Column(String(50), default="event", nullable=False, index=True)
    status = Column(String(20), default="confirmed", nullable=False, index=True)
    creator_id = Column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    recurrence_rule = Column(String(255), nullable=True)
    parent_event_id = Column(
        Integer, ForeignKey("calendar_events.id", ondelete="CASCADE"), nullable=True
    )
    timezone = Column(String(50), default="UTC", nullable=False)

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
