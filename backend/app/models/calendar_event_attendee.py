from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel


class CalendarEventAttendee(BaseModel):
    """
    Calendar Event Attendee model.
    Links users to calendar events they are invited to attend.
    """

    __tablename__ = "calendar_event_attendees"

    event_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("calendar_events.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    email: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    response_status: Mapped[str] = mapped_column(
        String(20), default="pending", nullable=False
    )  # pending, accepted, declined, tentative

    # Relationships
    event = relationship("CalendarEvent", back_populates="attendees")
    user = relationship("User", backref="calendar_event_attendances")

    def __str__(self) -> str:
        return f"CalendarEventAttendee(event_id={self.event_id}, user_id={self.user_id}, email='{self.email}')"

    def __repr__(self) -> str:
        return self.__str__()
