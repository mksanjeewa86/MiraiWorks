#!/usr/bin/env python3
"""
Simple calendar API server that exactly matches frontend types.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, field_validator
from datetime import datetime
from typing import Optional, List
import uuid
import uvicorn


# Schemas that exactly match frontend CalendarEvent interface
class EventCreate(BaseModel):
    title: str
    description: Optional[str] = None
    location: Optional[str] = None
    startDatetime: str  # Frontend sends as ISO string
    endDatetime: str  # Frontend sends as ISO string
    timezone: Optional[str] = "UTC"
    isAllDay: Optional[bool] = False
    attendees: Optional[List[str]] = []
    status: Optional[str] = None

    @field_validator("title")
    def title_must_not_be_empty(cls, v):
        if not v or not v.strip():
            raise ValueError("Title cannot be empty")
        return v.strip()

    @field_validator("startDatetime", "endDatetime")
    def datetime_must_be_valid(cls, v):
        try:
            datetime.fromisoformat(v.replace("Z", "+00:00"))
        except ValueError:
            raise ValueError("Invalid datetime format")
        return v


class EventInfo(BaseModel):
    id: str
    title: str
    description: Optional[str]
    location: Optional[str]
    startDatetime: str
    endDatetime: str
    timezone: Optional[str]
    isAllDay: bool
    isRecurring: bool
    organizerEmail: Optional[str]
    attendees: List[str]
    status: Optional[str]
    createdAt: str
    updatedAt: str


class EventsListResponse(BaseModel):
    events: List[EventInfo]
    has_more: bool = False


# Create FastAPI app
app = FastAPI(title="Simple Calendar API v2")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3001",
        "http://localhost:3002",
        "http://localhost:3003",
        "http://localhost:3004",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage for events
events_storage = []


@app.get("/")
async def root():
    return {"message": "Simple Calendar API v2 Server"}


@app.get("/api/calendar/events", response_model=EventsListResponse)
async def get_events(startDate: Optional[str] = None, endDate: Optional[str] = None):
    """Get calendar events."""
    print(f"GET /api/calendar/events - startDate: {startDate}, endDate: {endDate}")
    return EventsListResponse(events=events_storage, has_more=False)


@app.post("/api/calendar/events", response_model=EventInfo, status_code=201)
async def create_event(event_data: EventCreate):
    """Create a new calendar event."""
    print(f"POST /api/calendar/events - Received: {event_data}")

    event_id = str(uuid.uuid4())
    now = datetime.utcnow().isoformat() + "Z"

    # Convert to EventInfo format matching frontend exactly
    event_info = EventInfo(
        id=event_id,
        title=event_data.title,
        description=event_data.description,
        location=event_data.location,
        startDatetime=event_data.startDatetime,
        endDatetime=event_data.endDatetime,
        timezone=event_data.timezone or "UTC",
        isAllDay=event_data.isAllDay or False,
        isRecurring=False,
        organizerEmail="test@example.com",
        attendees=event_data.attendees or [],
        status=event_data.status or "tentative",
        createdAt=now,
        updatedAt=now,
    )

    # Store in memory
    events_storage.append(event_info)

    print(f"Created event: {event_info}")
    return event_info


@app.put("/api/calendar/events/{event_id}", response_model=EventInfo)
async def update_event(event_id: str, event_data: EventCreate):
    """Update a calendar event."""
    print(f"PUT /api/calendar/events/{event_id} - Received: {event_data}")

    # Find and update event
    for i, event in enumerate(events_storage):
        if event.id == event_id:
            now = datetime.utcnow().isoformat() + "Z"
            updated_event = EventInfo(
                id=event_id,
                title=event_data.title,
                description=event_data.description,
                location=event_data.location,
                startDatetime=event_data.startDatetime,
                endDatetime=event_data.endDatetime,
                timezone=event_data.timezone or "UTC",
                isAllDay=event_data.isAllDay or False,
                isRecurring=False,
                organizerEmail="test@example.com",
                attendees=event_data.attendees or [],
                status=event_data.status or "tentative",
                createdAt=event.createdAt,
                updatedAt=now,
            )
            events_storage[i] = updated_event
            print(f"Updated event: {updated_event}")
            return updated_event

    # If not found, create new
    return await create_event(event_data)


@app.delete("/api/calendar/events/{event_id}")
async def delete_event(event_id: str):
    """Delete a calendar event."""
    print(f"DELETE /api/calendar/events/{event_id}")

    global events_storage
    initial_count = len(events_storage)
    events_storage = [event for event in events_storage if event.id != event_id]
    deleted_count = initial_count - len(events_storage)

    if deleted_count > 0:
        print(f"Deleted {deleted_count} event(s)")
        return {"message": "Event deleted successfully"}
    else:
        print("Event not found")
        return {"message": "Event not found"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
