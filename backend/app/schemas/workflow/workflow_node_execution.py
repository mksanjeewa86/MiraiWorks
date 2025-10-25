from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field, field_validator

from app.schemas.workflow.enums import ExecutionResult, ExecutionStatus


class WorkflowNodeExecutionBase(BaseModel):
    """Base schema for node execution"""

    feedback: str | None = Field(None, description="Feedback for the execution")
    assessor_notes: str | None = Field(None, description="Internal notes from assessor")


class WorkflowNodeExecutionCreate(WorkflowNodeExecutionBase):
    """Schema for creating a node execution"""

    candidate_workflow_id: int = Field(..., description="Candidate process ID")
    node_id: int = Field(..., description="Process node ID")
    assigned_to: int | None = Field(
        None, description="User ID to assign this execution to"
    )
    due_date: datetime | None = Field(None, description="Due date for completion")


class WorkflowNodeExecutionUpdate(BaseModel):
    """Schema for updating a node execution"""

    status: ExecutionStatus | None = None
    assigned_to: int | None = None
    due_date: datetime | None = None
    feedback: str | None = None
    assessor_notes: str | None = None


class WorkflowNodeExecutionCompletion(BaseModel):
    """Schema for completing a node execution"""

    result: ExecutionResult = Field(..., description="Execution result")
    score: float | None = Field(None, ge=0, le=100, description="Score (0-100)")
    feedback: str | None = Field(
        None, max_length=2000, description="Feedback for the candidate"
    )
    assessor_notes: str | None = Field(
        None, max_length=2000, description="Internal assessor notes"
    )
    execution_data: dict[str, Any] | None = Field(
        default_factory=dict, description="Additional execution data"
    )

    @field_validator("score")
    @classmethod
    def validate_score(cls, v):
        if v is not None and (v < 0 or v > 100):
            raise ValueError("Score must be between 0 and 100")
        return v


class WorkflowNodeExecutionFailure(BaseModel):
    """Schema for failing a node execution"""

    reason: str = Field(
        ..., min_length=1, max_length=500, description="Reason for failure"
    )
    allow_retry: bool = Field(False, description="Whether to allow retry")
    retry_instructions: str | None = Field(
        None, max_length=1000, description="Instructions for retry"
    )


class WorkflowNodeExecutionSkip(BaseModel):
    """Schema for skipping a node execution"""

    reason: str = Field(
        ..., min_length=1, max_length=500, description="Reason for skipping"
    )
    notify_stakeholders: bool = Field(
        True, description="Whether to notify relevant stakeholders"
    )


class WorkflowNodeExecutionSchedule(BaseModel):
    """Schema for scheduling a node execution"""

    due_date: datetime = Field(..., description="Due date for the execution")
    assigned_to: int | None = Field(None, description="User to assign the execution to")
    send_notification: bool = Field(True, description="Whether to send notification")
    custom_instructions: str | None = Field(
        None, max_length=1000, description="Custom instructions"
    )


class WorkflowNodeExecutionInfo(WorkflowNodeExecutionBase):
    """Schema for node execution information"""

    id: int
    candidate_workflow_id: int
    node_id: int
    status: ExecutionStatus
    result: ExecutionResult | None
    score: float | None
    execution_data: dict[str, Any] | None
    interview_id: int | None
    todo_id: int | None
    started_at: datetime | None
    completed_at: datetime | None
    due_date: datetime | None
    assigned_to: int | None
    completed_by: int | None
    reviewed_by: int | None
    created_at: datetime
    updated_at: datetime

    # Computed fields
    duration_minutes: int | None = Field(
        None, description="Execution duration in minutes"
    )
    is_overdue: bool | None = Field(
        None, description="Whether the execution is overdue"
    )

    class Config:
        from_attributes = True


class WorkflowNodeExecutionDetails(WorkflowNodeExecutionInfo):
    """Detailed schema for node execution with relationships"""

    # Node information
    node_title: str | None = Field(None, description="Title of the associated node")
    node_type: str | None = Field(None, description="Type of the associated node")
    node_sequence_order: int | None = Field(
        None, description="Sequence order of the node"
    )

    # Actor information
    assignee_name: str | None = Field(None, description="Name of assigned user")
    completer_name: str | None = Field(None, description="Name of user who completed")
    reviewer_name: str | None = Field(None, description="Name of reviewer")

    # Linked resource information
    interview_title: str | None = Field(None, description="Title of linked interview")
    interview_status: str | None = Field(None, description="Status of linked interview")
    todo_title: str | None = Field(None, description="Title of linked todo")
    todo_status: str | None = Field(None, description="Status of linked todo")


class WorkflowNodeExecutionTimeline(BaseModel):
    """Schema for execution timeline/history"""

    execution_id: int
    timeline_events: list[dict[str, Any]] = Field(default_factory=list)


class ExecutionTimelineEvent(BaseModel):
    """Schema for individual timeline events"""

    timestamp: datetime
    event_type: str  # created, assigned, started, updated, completed, failed, etc.
    actor_id: int | None
    actor_name: str | None
    description: str
    metadata: dict[str, Any] | None = Field(default_factory=dict)


class BulkExecutionUpdate(BaseModel):
    """Schema for bulk updating executions"""

    execution_ids: list[int] = Field(
        ..., min_items=1, description="List of execution IDs to update"
    )
    status: ExecutionStatus | None = None
    assigned_to: int | None = None
    due_date: datetime | None = None

    @field_validator("execution_ids")
    @classmethod
    def validate_execution_ids(cls, v):
        if len(v) != len(set(v)):
            raise ValueError("Duplicate execution IDs are not allowed")
        return v


class ExecutionBatchCompletion(BaseModel):
    """Schema for batch completing executions"""

    completions: list[dict[str, Any]] = Field(
        ...,
        min_items=1,
        description="List of {execution_id, result, score, feedback} objects",
    )

    @field_validator("completions")
    @classmethod
    def validate_completions(cls, v):
        execution_ids = [c.get("execution_id") for c in v]
        if len(execution_ids) != len(set(execution_ids)):
            raise ValueError("Duplicate execution IDs in batch completion")

        for completion in v:
            if "execution_id" not in completion or "result" not in completion:
                raise ValueError("Each completion must have execution_id and result")

        return v


class ExecutionStatistics(BaseModel):
    """Schema for execution statistics"""

    total_executions: int
    by_status: dict[str, int]
    by_result: dict[str, int]
    average_duration_minutes: float
    completion_rate: float
    on_time_completion_rate: float


class WorkflowNodeExecutionMetrics(BaseModel):
    """Schema for node-specific execution metrics"""

    node_id: int
    node_title: str
    node_type: str
    total_executions: int
    completed_executions: int
    failed_executions: int
    average_duration_minutes: float
    completion_rate: float
    average_score: float | None
    bottleneck_score: float  # How much this node slows down the process


class ExecutionWorkload(BaseModel):
    """Schema for execution workload by assignee"""

    assignee_id: int
    assignee_name: str
    pending_executions: int
    in_progress_executions: int
    overdue_executions: int
    completed_this_week: int
    average_completion_time_hours: float
    workload_score: float  # Relative workload compared to other assignees
