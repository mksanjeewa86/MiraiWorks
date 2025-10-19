"""Schemas for todo extension requests."""

from datetime import datetime, timezone
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_serializer, field_validator

from app.schemas.todo import TodoRead, UserInfo
from app.utils.constants import ExtensionRequestStatus


class TodoExtensionRequestCreate(BaseModel):
    """Schema for creating a todo extension request."""

    requested_due_date: datetime = Field(
        ..., description="Requested new due date (max 3 days from current due date)"
    )
    reason: str = Field(
        ...,
        min_length=10,
        max_length=1000,
        description="Reason for requesting extension",
    )

    @field_validator("requested_due_date", mode="before")
    @classmethod
    def ensure_utc_requested_date(cls, value):
        """Ensure requested_due_date is converted to UTC."""
        if value is None:
            return value
        if isinstance(value, str):
            from datetime import UTC
            value = datetime.fromisoformat(value)
        if isinstance(value, datetime):
            if value.tzinfo is None:
                # Assume UTC if naive
                return value.replace(tzinfo=timezone.utc)
            # Convert to UTC if timezone-aware
            return value.astimezone(timezone.utc)
        return value

    @field_validator("reason")
    @classmethod
    def validate_reason(cls, v):
        if not v or not v.strip():
            raise ValueError("Reason cannot be empty")
        return v.strip()


class TodoExtensionRequestResponse(BaseModel):
    """Schema for responding to a todo extension request."""

    status: ExtensionRequestStatus = Field(
        ..., description="Response status (approved or rejected)"
    )
    response_reason: Optional[str] = Field(
        None, max_length=1000, description="Optional reason for the response"
    )
    new_due_date: Optional[datetime] = Field(
        None, description="Optional new due date (for approval with date change)"
    )

    @field_validator("new_due_date", mode="before")
    @classmethod
    def ensure_utc_new_date(cls, value):
        """Ensure new_due_date is converted to UTC."""
        if value is None:
            return value
        if isinstance(value, str):
            from datetime import UTC
            value = datetime.fromisoformat(value)
        if isinstance(value, datetime):
            if value.tzinfo is None:
                # Assume UTC if naive
                return value.replace(tzinfo=timezone.utc)
            # Convert to UTC if timezone-aware
            return value.astimezone(timezone.utc)
        return value

    @field_validator("status")
    @classmethod
    def validate_status(cls, v):
        if v == ExtensionRequestStatus.PENDING:
            raise ValueError("Cannot set status to pending in response")
        return v

    @field_validator("response_reason")
    @classmethod
    def validate_response_reason(cls, v):
        if v is not None:
            return v.strip() if v.strip() else None
        return v


class TodoExtensionRequestRead(BaseModel):
    """Schema for reading todo extension request data."""

    id: int
    todo_id: int
    requested_by_id: int
    creator_id: int
    requested_due_date: datetime
    reason: str
    status: ExtensionRequestStatus
    response_reason: Optional[str] = None
    responded_at: Optional[datetime] = None
    responded_by_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    # Related objects
    requested_by: UserInfo
    creator: UserInfo
    responded_by: Optional[UserInfo] = None
    todo: TodoRead

    model_config = ConfigDict(from_attributes=True)

    @field_serializer('requested_due_date', 'responded_at', 'created_at', 'updated_at')
    def serialize_datetime(self, dt: Optional[datetime], _info) -> Optional[str]:
        """Ensure datetime fields are serialized with UTC timezone information."""
        if dt is None:
            return None
        # If datetime is naive, assume it's UTC and add timezone
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        # Serialize to ISO format
        return dt.isoformat()


class TodoExtensionRequestList(BaseModel):
    """Schema for listing todo extension requests."""

    items: list[TodoExtensionRequestRead]
    total: int
    pending_count: int
    approved_count: int
    rejected_count: int


class TodoExtensionValidation(BaseModel):
    """Schema for validating extension request constraints."""

    can_request_extension: bool
    max_allowed_due_date: Optional[datetime] = None
    days_extension_allowed: int = 3
    reason: Optional[str] = None  # Reason why extension cannot be requested

    model_config = ConfigDict(from_attributes=True)


class TodoExtensionNotification(BaseModel):
    """Schema for extension request notifications."""

    request_id: int
    todo_id: int
    todo_title: str
    requester_name: str
    creator_name: str
    requested_due_date: datetime
    reason: str
    status: ExtensionRequestStatus
    response_reason: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

    @field_serializer('requested_due_date')
    def serialize_datetime(self, dt: Optional[datetime], _info) -> Optional[str]:
        """Ensure datetime fields are serialized with UTC timezone information."""
        if dt is None:
            return None
        # If datetime is naive, assume it's UTC and add timezone
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        # Serialize to ISO format
        return dt.isoformat()
