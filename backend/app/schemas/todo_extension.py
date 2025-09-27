"""Schemas for todo extension requests."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.schemas.todo import AssignableUser
from app.utils.constants import ExtensionRequestStatus


class TodoExtensionRequestCreate(BaseModel):
    """Schema for creating a todo extension request."""

    requested_due_date: datetime = Field(
        ..., description="Requested new due date (max 3 days from current due date)"
    )
    reason: str = Field(
        ..., min_length=10, max_length=1000,
        description="Reason for requesting extension"
    )

    @field_validator('reason')
    @classmethod
    def validate_reason(cls, v):
        if not v or not v.strip():
            raise ValueError('Reason cannot be empty')
        return v.strip()


class TodoExtensionRequestResponse(BaseModel):
    """Schema for responding to a todo extension request."""

    status: ExtensionRequestStatus = Field(
        ..., description="Response status (approved or rejected)"
    )
    response_reason: str | None = Field(
        None, max_length=1000,
        description="Optional reason for the response"
    )

    @field_validator('status')
    @classmethod
    def validate_status(cls, v):
        if v == ExtensionRequestStatus.PENDING:
            raise ValueError('Cannot set status to pending in response')
        return v

    @field_validator('response_reason')
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
    current_due_date: datetime
    requested_due_date: datetime
    reason: str
    status: ExtensionRequestStatus
    response_reason: str | None = None
    responded_at: datetime | None = None
    responded_by_id: int | None = None
    created_at: datetime
    updated_at: datetime

    # Related objects
    requested_by: AssignableUser
    creator: AssignableUser
    responded_by: AssignableUser | None = None

    model_config = ConfigDict(from_attributes=True)


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
    max_allowed_due_date: datetime | None = None
    days_extension_allowed: int = 3
    reason: str | None = None  # Reason why extension cannot be requested

    model_config = ConfigDict(from_attributes=True)


class TodoExtensionNotification(BaseModel):
    """Schema for extension request notifications."""

    request_id: int
    todo_id: int
    todo_title: str
    requester_name: str
    creator_name: str
    current_due_date: datetime
    requested_due_date: datetime
    reason: str
    status: ExtensionRequestStatus
    response_reason: str | None = None

    model_config = ConfigDict(from_attributes=True)
