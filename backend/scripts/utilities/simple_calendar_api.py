#!/usr/bin/env python3
"""
Simple calendar API server for testing without dependencies.
"""

import uuid
from datetime import UTC, datetime

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field


# Simple schemas
class EventCreate(BaseModel):
    title: str
    description: str | None = None
    location: str | None = None
    startDatetime: datetime = Field(alias="startDatetime")
    endDatetime: datetime = Field(alias="endDatetime")
    timezone: str = Field(default="UTC")
    isAllDay: bool = Field(default=False, alias="isAllDay")
    attendees: list[str] = Field(default_factory=list)
    status: str | None = None
    organizerEmail: str | None = Field(None, alias="organizerEmail")
    isRecurring: bool | None = Field(None, alias="isRecurring")
    createdAt: str | None = Field(None, alias="createdAt")
    updatedAt: str | None = Field(None, alias="updatedAt")

    class Config:
        populate_by_name = True


class EventInfo(BaseModel):
    id: str
    title: str
    description: str | None
    location: str | None
    startDatetime: datetime = Field(alias="startDatetime")
    endDatetime: datetime = Field(alias="endDatetime")
    timezone: str
    isAllDay: bool = Field(alias="isAllDay")
    isRecurring: bool = Field(alias="isRecurring")
    organizerEmail: str | None = Field(alias="organizerEmail")
    attendees: list[str]
    status: str | None
    createdAt: datetime = Field(alias="createdAt")
    updatedAt: datetime = Field(alias="updatedAt")

    class Config:
        populate_by_name = True


class EventsListResponse(BaseModel):
    events: list[EventInfo]
    has_more: bool = False


# Create FastAPI app
app = FastAPI(title="Simple Calendar API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3001", "http://localhost:3002"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage for events
events_storage = []


@app.get("/")
async def root():
    return {"message": "Simple Calendar API Server"}


@app.get("/api/calendar/events", response_model=EventsListResponse)
async def get_events(startDate: str | None = None, endDate: str | None = None):
    """Get calendar events."""
    return EventsListResponse(events=events_storage, has_more=False)


@app.post("/api/calendar/events", response_model=EventInfo)
async def create_event(event_data: EventCreate):
    """Create a new calendar event."""
    print(f"Received event data: {event_data}")

    event_id = str(uuid.uuid4())
    now = datetime.now(UTC)

    # Convert field names to match frontend expectations
    event_info = EventInfo(
        id=event_id,
        title=event_data.title,
        description=event_data.description,
        location=event_data.location,
        startDatetime=event_data.startDatetime,
        endDatetime=event_data.endDatetime,
        timezone=event_data.timezone,
        isAllDay=event_data.isAllDay,
        isRecurring=False,
        organizerEmail="test@example.com",
        attendees=event_data.attendees,
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
    # Find and update event
    for i, event in enumerate(events_storage):
        if event.id == event_id:
            now = datetime.now(UTC)
            updated_event = EventInfo(
                id=event_id,
                title=event_data.title,
                description=event_data.description,
                location=event_data.location,
                startDatetime=event_data.startDatetime,
                endDatetime=event_data.endDatetime,
                timezone=event_data.timezone,
                isAllDay=event_data.isAllDay,
                isRecurring=False,
                organizerEmail="test@example.com",
                attendees=event_data.attendees,
                status="tentative",
                createdAt=event.createdAt,
                updatedAt=now,
            )
            events_storage[i] = updated_event
            return updated_event

    # If not found, create new
    return await create_event(event_data)


@app.delete("/api/calendar/events/{event_id}")
async def delete_event(event_id: str):
    """Delete a calendar event."""
    global events_storage
    events_storage = [event for event in events_storage if event.id != event_id]
    return {"message": "Event deleted successfully"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
