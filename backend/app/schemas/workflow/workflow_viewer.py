from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator

from app.schemas.recruitment_workflow.enums import ViewerRole


class WorkflowViewerBase(BaseModel):
    """Base schema for process viewer"""

    role: ViewerRole = Field(..., description="Role of the viewer")
    permissions: dict[str, bool] | None = Field(
        default_factory=dict, description="Custom permissions"
    )


class WorkflowViewerCreate(WorkflowViewerBase):
    """Schema for adding a viewer to a process"""

    user_id: int = Field(..., description="User ID of the viewer")

    @field_validator("permissions")
    @classmethod
    def validate_permissions(cls, v, info):
        role = info.data.get("role")
        if role and v:
            valid_permissions = cls._get_valid_permissions_for_role(role)
            invalid_perms = [p for p in v if p not in valid_permissions]
            if invalid_perms:
                raise ValueError(
                    f"Invalid permissions for role {role}: {invalid_perms}"
                )
        return v

    @staticmethod
    def _get_valid_permissions_for_role(role: ViewerRole) -> list[str]:
        """Get valid permissions for a role"""
        base_permissions = [
            "view_process",
            "view_candidates",
            "view_results",
            "execute_nodes",
            "schedule_interviews",
            "record_results",
            "add_notes",
            "override_results",
            "manage_assignments",
            "view_analytics",
        ]
        return base_permissions


class WorkflowViewerUpdate(BaseModel):
    """Schema for updating a process viewer"""

    role: Optional[ViewerRole] = None
    permissions: dict[str, bool] | None = None


class WorkflowViewerInfo(WorkflowViewerBase):
    """Schema for process viewer information"""

    id: int
    workflow_id: int
    user_id: int
    added_by: int
    added_at: datetime

    # User information (from relationship)
    user_name: Optional[str] = Field(None, description="Name of the viewer")
    user_email: Optional[str] = Field(None, description="Email of the viewer")
    added_by_name: Optional[str] = Field(
        None, description="Name of user who added this viewer"
    )

    # Computed permissions
    effective_permissions: list[str] | None = Field(
        None, description="All effective permissions"
    )
    can_execute: Optional[bool] = Field(None, description="Whether can execute nodes")
    can_view_all_candidates: Optional[bool] = Field(
        None, description="Whether can view all candidates"
    )

    class Config:
        from_attributes = True


class BulkViewerAdd(BaseModel):
    """Schema for adding multiple viewers to a process"""

    viewers: list[WorkflowViewerCreate] = Field(
        ..., min_items=1, description="List of viewers to add"
    )

    @field_validator("viewers")
    @classmethod
    def validate_viewers(cls, v):
        user_ids = [viewer.user_id for viewer in v]
        if len(user_ids) != len(set(user_ids)):
            raise ValueError("Duplicate user IDs in viewer list")
        return v


class ViewerRoleChange(BaseModel):
    """Schema for changing a viewer's role"""

    new_role: ViewerRole = Field(..., description="New role for the viewer")
    reason: Optional[str] = Field(
        None, max_length=500, description="Reason for role change"
    )


class ViewerPermissionChange(BaseModel):
    """Schema for changing specific viewer permissions"""

    permission_updates: dict[str, bool] = Field(..., description="Permission updates")

    @field_validator("permission_updates")
    @classmethod
    def validate_permission_updates(cls, v):
        if not v:
            raise ValueError("At least one permission update is required")

        valid_permissions = [
            "view_process",
            "view_candidates",
            "view_results",
            "execute_nodes",
            "schedule_interviews",
            "record_results",
            "add_notes",
            "override_results",
            "manage_assignments",
            "view_analytics",
        ]

        invalid_perms = [p for p in v if p not in valid_permissions]
        if invalid_perms:
            raise ValueError(f"Invalid permissions: {invalid_perms}")

        return v


class ViewerActivity(BaseModel):
    """Schema for viewer activity tracking"""

    viewer_id: int
    user_id: int
    user_name: str
    role: ViewerRole
    last_activity: Optional[datetime]
    actions_count: int = Field(0, description="Number of actions performed")
    executions_completed: int = Field(0, description="Number of executions completed")
    interviews_scheduled: int = Field(0, description="Number of interviews scheduled")
    notes_added: int = Field(0, description="Number of notes added")


class ViewerWorkload(BaseModel):
    """Schema for viewer workload statistics"""

    viewer_id: int
    user_id: int
    user_name: str
    role: ViewerRole
    assigned_processes: int
    active_executions: int
    pending_tasks: int
    overdue_tasks: int
    completion_rate: float
    average_response_time_hours: float


class WorkflowViewerStatistics(BaseModel):
    """Schema for overall process viewer statistics"""

    total_viewers: int
    by_role: dict[str, int]
    active_viewers: int
    viewer_activity: list[ViewerActivity]
    workload_distribution: list[ViewerWorkload]


class ViewerInvitation(BaseModel):
    """Schema for inviting a viewer to a process"""

    email: str = Field(..., description="Email of the user to invite")
    role: ViewerRole = Field(..., description="Role to assign")
    message: Optional[str] = Field(
        None, max_length=1000, description="Custom invitation message"
    )
    permissions: dict[str, bool] | None = Field(
        default_factory=dict, description="Custom permissions"
    )

    @field_validator("email")
    @classmethod
    def validate_email(cls, v):
        # Basic email validation
        if "@" not in v or "." not in v.split("@")[1]:
            raise ValueError("Invalid email address")
        return v.lower()


class ViewerInvitationResponse(BaseModel):
    """Schema for responding to a viewer invitation"""

    accept: bool = Field(..., description="Whether to accept the invitation")
    message: Optional[str] = Field(None, max_length=500, description="Response message")


class ViewerNotificationSettings(BaseModel):
    """Schema for viewer notification preferences"""

    viewer_id: int
    email_notifications: bool = Field(True, description="Receive email notifications")
    sms_notifications: bool = Field(False, description="Receive SMS notifications")
    in_app_notifications: bool = Field(True, description="Receive in-app notifications")
    notification_frequency: str = Field(
        "immediate", description="Notification frequency (immediate, daily, weekly)"
    )
    notification_types: list[str] = Field(
        default_factory=list, description="Types of notifications to receive"
    )

    @field_validator("notification_frequency")
    @classmethod
    def validate_frequency(cls, v):
        valid_frequencies = ["immediate", "hourly", "daily", "weekly"]
        if v not in valid_frequencies:
            raise ValueError(f"Invalid frequency. Must be one of: {valid_frequencies}")
        return v
