from __future__ import annotations

from datetime import datetime, timezone

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.utils.constants import TodoStatus


class TodoBase(BaseModel):
    title: str = Field(..., max_length=255)
    description: str | None = None
    notes: str | None = None
    priority: str | None = Field(default=None, max_length=20)
    due_date: datetime | None = None
    status: str | None = Field(default=TodoStatus.PENDING.value)

    @field_validator("due_date", mode="before")
    @classmethod
    def ensure_timezone(cls, value: datetime | None) -> datetime | None:
        if value is None:
            return value
        if isinstance(value, str):
            try:
                value = datetime.fromisoformat(value)
            except ValueError as exc:
                raise ValueError("Invalid datetime format for due_date") from exc
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc)

    @field_validator("status")
    @classmethod
    def validate_status(cls, value: str | None) -> str:
        if value is None:
            return TodoStatus.PENDING.value
        allowed = {status.value for status in TodoStatus}
        if value not in allowed:
            raise ValueError(f"Status must be one of: {', '.join(sorted(allowed))}")
        return value

    @field_validator("title")
    @classmethod
    def validate_title(cls, value: str) -> str:
        if not value or not value.strip():
            raise ValueError("Title is required")
        return value.strip()


class TodoCreate(TodoBase):
    pass


class TodoUpdate(BaseModel):
    title: str | None = Field(default=None, max_length=255)
    description: str | None = None
    notes: str | None = None
    priority: str | None = Field(default=None, max_length=20)
    due_date: datetime | None = None
    status: str | None = None

    @field_validator("due_date", mode="before")
    @classmethod
    def ensure_timezone(cls, value: datetime | None) -> datetime | None:
        if value is None:
            return value
        if isinstance(value, str):
            try:
                value = datetime.fromisoformat(value)
            except ValueError as exc:
                raise ValueError("Invalid datetime format for due_date") from exc
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc)

    @field_validator("title")
    @classmethod
    def validate_title(cls, value: str | None) -> str | None:
        if value is not None and not value.strip():
            raise ValueError("Title cannot be empty")
        return value.strip() if value else value

    @field_validator("status")
    @classmethod
    def validate_status(cls, value: str | None) -> str | None:
        if value is None:
            return value
        allowed = {status.value for status in TodoStatus}
        if value not in allowed:
            raise ValueError(f"Status must be one of: {', '.join(sorted(allowed))}")
        return value


class TodoRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    owner_id: int
    title: str
    description: str | None = None
    notes: str | None = None
    status: str
    priority: str | None = None
    due_date: datetime | None = None
    completed_at: datetime | None = None
    expired_at: datetime | None = None
    created_at: datetime
    updated_at: datetime
    is_expired: bool


class TodoListResponse(BaseModel):
    items: list[TodoRead]
    total: int


class TodoStatusUpdate(BaseModel):
    status: str

    @field_validator("status")
    @classmethod
    def validate_status(cls, value: str) -> str:
        allowed = {status.value for status in TodoStatus}
        if value not in allowed:
            raise ValueError(f"Status must be one of: {', '.join(sorted(allowed))}")
        return value
