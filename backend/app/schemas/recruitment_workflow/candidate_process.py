from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field, field_validator

from app.schemas.recruitment_workflow.enums import CandidateProcessStatus, FinalResult
from app.schemas.recruitment_workflow.node_execution import NodeExecutionInfo


class CandidateProcessBase(BaseModel):
    """Base schema for candidate process"""

    notes: Optional[str] = Field(
        None, description="General notes about the candidate's process"
    )


class CandidateProcessCreate(CandidateProcessBase):
    """Schema for creating a candidate process (assignment)"""

    candidate_id: int = Field(..., description="Candidate user ID")
    assigned_recruiter_id: Optional[int] = Field(
        None, description="Assigned recruiter user ID"
    )
    start_immediately: bool = Field(
        False, description="Whether to start the process immediately"
    )


class CandidateProcessUpdate(BaseModel):
    """Schema for updating a candidate process"""

    notes: Optional[str] = None
    assigned_recruiter_id: Optional[int] = None


class CandidateProcessAssignment(BaseModel):
    """Schema for assigning/reassigning a recruiter"""

    assigned_recruiter_id: int = Field(
        ..., description="New assigned recruiter user ID"
    )


class CandidateProcessStatusChange(BaseModel):
    """Schema for changing candidate process status"""

    status: CandidateProcessStatus = Field(..., description="New status")
    reason: Optional[str] = Field(
        None, max_length=500, description="Reason for status change"
    )
    final_result: Optional[FinalResult] = Field(
        None, description="Final result if completing/failing"
    )
    overall_score: Optional[float] = Field(
        None, ge=0, le=100, description="Overall score if completing"
    )


class CandidateProcessInfo(CandidateProcessBase):
    """Schema for candidate process information"""

    id: int
    candidate_id: int
    process_id: int
    current_node_id: Optional[int]
    status: CandidateProcessStatus
    assigned_recruiter_id: Optional[int]
    assigned_at: Optional[datetime]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    failed_at: Optional[datetime]
    withdrawn_at: Optional[datetime]
    overall_score: Optional[float]
    final_result: Optional[FinalResult]
    created_at: datetime
    updated_at: datetime

    # Computed fields
    progress_percentage: Optional[float] = Field(
        None, description="Progress as percentage"
    )
    current_step_title: Optional[str] = Field(None, description="Title of current step")
    days_in_process: Optional[int] = Field(
        None, description="Number of days in the process"
    )

    class Config:
        from_attributes = True

    @field_validator("progress_percentage")
    @classmethod
    def validate_progress_percentage(cls, v):
        if v is not None and (v < 0 or v > 100):
            raise ValueError("Progress percentage must be between 0 and 100")
        return v


class CandidateProcessDetails(CandidateProcessInfo):
    """Detailed schema for candidate process with executions"""

    executions: list[NodeExecutionInfo] = Field(
        default_factory=list, description="Node executions"
    )
    timeline: list[dict[str, Any]] = Field(
        default_factory=list, description="Process timeline"
    )

    # Statistics
    completed_nodes: int = Field(0, description="Number of completed nodes")
    total_nodes: int = Field(0, description="Total number of nodes in process")
    average_node_duration_days: Optional[float] = Field(
        None, description="Average time per node in days"
    )


class CandidateTimeline(BaseModel):
    """Schema for candidate process timeline"""

    candidate_process_id: int
    candidate_name: str
    process_name: str
    current_status: CandidateProcessStatus
    timeline_items: list[dict[str, Any]] = Field(default_factory=list)


class TimelineItem(BaseModel):
    """Schema for individual timeline items"""

    node_id: int
    node_title: str
    node_type: str
    sequence_order: int
    status: str
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    result: Optional[str]
    score: Optional[float]
    feedback: Optional[str]
    is_current: bool = Field(False, description="Whether this is the current step")
    is_completed: bool = Field(False, description="Whether this step is completed")
    can_access: bool = Field(
        False, description="Whether candidate can access this step"
    )


class CandidateProcessAdvance(BaseModel):
    """Schema for advancing a candidate to a specific node"""

    target_node_id: Optional[int] = Field(
        None, description="Target node ID (None for completion)"
    )
    reason: str = Field(
        ..., min_length=1, max_length=500, description="Reason for manual advancement"
    )
    skip_validations: bool = Field(
        False, description="Skip normal advancement validations"
    )


class CandidateProcessStart(BaseModel):
    """Schema for starting a candidate process"""

    send_notification: bool = Field(
        True, description="Whether to send notification to candidate"
    )
    custom_message: Optional[str] = Field(
        None, max_length=1000, description="Custom welcome message"
    )


class CandidateProcessCompletion(BaseModel):
    """Schema for completing a candidate process"""

    final_result: FinalResult = Field(..., description="Final result of the process")
    overall_score: Optional[float] = Field(
        None, ge=0, le=100, description="Overall score"
    )
    completion_notes: Optional[str] = Field(
        None, max_length=1000, description="Completion notes"
    )
    send_notification: bool = Field(True, description="Whether to notify the candidate")


class CandidateProcessFailure(BaseModel):
    """Schema for failing a candidate process"""

    failure_reason: str = Field(
        ..., min_length=1, max_length=500, description="Reason for failure"
    )
    failed_at_node_id: Optional[int] = Field(
        None, description="Node where failure occurred"
    )
    send_notification: bool = Field(True, description="Whether to notify the candidate")


class CandidateProcessWithdrawal(BaseModel):
    """Schema for withdrawing from a process"""

    withdrawal_reason: Optional[str] = Field(
        None, max_length=500, description="Reason for withdrawal"
    )
    initiated_by_candidate: bool = Field(
        True, description="Whether withdrawal was initiated by candidate"
    )


class BulkCandidateAssignment(BaseModel):
    """Schema for bulk assigning candidates to a process"""

    candidate_ids: list[int] = Field(
        ..., min_items=1, description="List of candidate user IDs"
    )
    assigned_recruiter_id: Optional[int] = Field(
        None, description="Recruiter to assign to all candidates"
    )
    start_immediately: bool = Field(
        False, description="Whether to start all processes immediately"
    )
    send_notifications: bool = Field(True, description="Whether to send notifications")

    @field_validator("candidate_ids")
    @classmethod
    def validate_candidate_ids(cls, v):
        if len(v) != len(set(v)):
            raise ValueError("Duplicate candidate IDs are not allowed")
        return v


class CandidateProcessStatistics(BaseModel):
    """Schema for candidate process statistics"""

    total_candidates: int
    by_status: dict[str, int]
    completion_rate: float
    average_duration_days: float
    drop_off_by_node: list[dict[str, Any]]


class RecruiterWorkload(BaseModel):
    """Schema for recruiter workload information"""

    recruiter_id: int
    recruiter_name: str
    active_processes: int
    pending_tasks: int
    overdue_tasks: int
    completion_rate: float
    average_response_time_hours: float
