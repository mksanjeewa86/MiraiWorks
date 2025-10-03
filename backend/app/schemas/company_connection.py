"""Company Connection schemas for company-to-company relationships."""

from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field


class ConnectionStatus(str, Enum):
    """Connection status options."""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    BLOCKED = "blocked"


class ConnectionType(str, Enum):
    """Connection type options."""
    PARTNERSHIP = "partnership"
    CLIENT = "client"
    VENDOR = "vendor"
    REFERRAL = "referral"


class CompanyConnectionBase(BaseModel):
    """Base schema for company connections."""
    connection_type: ConnectionType = ConnectionType.PARTNERSHIP
    message: str | None = None
    allow_messaging: bool = True
    allow_candidate_sharing: bool = False
    allow_position_sharing: bool = False
    allow_interview_coordination: bool = False
    expires_at: datetime | None = None


class CompanyConnectionCreate(CompanyConnectionBase):
    """Schema for creating a company connection request."""
    target_company_id: int


class CompanyConnectionUpdate(BaseModel):
    """Schema for updating connection permissions."""
    allow_messaging: bool | None = None
    allow_candidate_sharing: bool | None = None
    allow_position_sharing: bool | None = None
    allow_interview_coordination: bool | None = None
    expires_at: datetime | None = None


class CompanyConnectionResponse(BaseModel):
    """Schema for responding to a connection request."""
    action: str = Field(..., regex="^(approve|reject|block)$")
    response_message: str | None = None


class CompanyConnectionInfo(CompanyConnectionBase):
    """Schema for company connection information."""
    id: int
    requesting_company_id: int
    target_company_id: int
    status: ConnectionStatus
    response_message: str | None = None
    requested_by: int | None = None
    responded_by: int | None = None
    requested_at: datetime
    responded_at: datetime | None = None

    class Config:
        from_attributes = True


class CompanyConnectionWithDetails(CompanyConnectionInfo):
    """Schema for company connection with company details."""
    requesting_company: dict  # Basic company info
    target_company: dict      # Basic company info
    requester: dict | None = None      # Basic user info
    responder: dict | None = None      # Basic user info

    class Config:
        from_attributes = True


class CompanyConnectionSummary(BaseModel):
    """Schema for connection summary statistics."""
    total_connections: int
    active_connections: int
    pending_requests_sent: int
    pending_requests_received: int
    rejected_requests: int
    blocked_connections: int