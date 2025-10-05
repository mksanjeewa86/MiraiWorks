from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field, field_validator

from app.schemas.workflow.enums import (
    InterviewNodeType,
    NodeStatus,
    NodeType,
    SubmissionType,
    TodoNodeType,
)


class WorkflowNodePosition(BaseModel):
    """Position of a node in the visual editor"""

    x: float = Field(..., description="X coordinate")
    y: float = Field(..., description="Y coordinate")


class InterviewNodeConfig(BaseModel):
    """Configuration for interview nodes"""

    interview_type: InterviewNodeType = Field(
        InterviewNodeType.VIDEO, description="Type of interview"
    )
    duration_minutes: int = Field(
        60, ge=15, le=480, description="Interview duration in minutes"
    )
    interviewers: list[int] = Field(
        default_factory=list, description="List of interviewer user IDs"
    )
    evaluation_criteria: list[str] = Field(
        default_factory=list, description="List of evaluation criteria"
    )
    preparation_notes: Optional[str] = Field(
        None, description="Notes for interview preparation"
    )
    scheduling_buffer_hours: int = Field(
        24, ge=1, description="Minimum hours between scheduling and interview"
    )


class TodoNodeConfig(BaseModel):
    """Configuration for todo/assignment nodes"""

    todo_type: TodoNodeType = Field(
        TodoNodeType.ASSIGNMENT, description="Type of todo/assignment"
    )
    submission_type: SubmissionType = Field(
        SubmissionType.FILE, description="Expected submission type"
    )
    requirements: list[str] = Field(
        default_factory=list, description="List of requirements"
    )
    due_in_days: int = Field(3, ge=1, le=30, description="Days to complete the todo")
    evaluation_rubric: list[str] = Field(
        default_factory=list, description="Evaluation criteria"
    )
    file_size_limit_mb: Optional[int] = Field(
        10, ge=1, le=100, description="File size limit in MB"
    )
    allowed_file_types: list[str] = Field(
        default_factory=list, description="Allowed file extensions"
    )


class AssessmentNodeConfig(BaseModel):
    """Configuration for assessment nodes"""

    assessment_type: str = Field(..., description="Type of assessment")
    provider: Optional[str] = Field(None, description="Assessment provider")
    duration_minutes: int = Field(30, ge=10, le=240, description="Assessment duration")
    passing_score: Optional[float] = Field(
        None, ge=0, le=100, description="Minimum passing score"
    )
    instructions: Optional[str] = Field(None, description="Special instructions")


class DecisionNodeConfig(BaseModel):
    """Configuration for decision nodes"""

    decision_makers: list[int] = Field(
        ..., min_items=1, description="List of decision maker user IDs"
    )
    decision_criteria: list[str] = Field(
        default_factory=list, description="Decision criteria"
    )
    auto_advance_on_approval: bool = Field(
        True, description="Auto advance when approved"
    )
    require_unanimous: bool = Field(False, description="Require unanimous decision")


class NodeIntegrationInterview(BaseModel):
    """Optional payload to create an interview alongside the node."""

    candidate_id: Optional[int] = Field(
        None, description="Candidate user ID to associate with the new interview"
    )
    recruiter_id: Optional[int] = Field(
        None, description="Recruiter user ID who will own the interview"
    )
    scheduled_at: Optional[datetime] = Field(
        None, description="Planned start datetime for the interview"
    )
    duration_minutes: Optional[int] = Field(
        None, ge=15, le=480, description="Length of the interview in minutes"
    )
    location: Optional[str] = Field(
        None, description="Interview location or meeting link"
    )
    meeting_link: Optional[str] = Field(None, description="Video meeting URL")
    interview_type: Optional[str] = Field(
        None, description="Type of interview (video, phone, in_person)"
    )
    notes: Optional[str] = Field(
        None, description="Additional notes for interviewer or candidate"
    )

    @field_validator("scheduled_at", mode="before")
    @classmethod
    def validate_datetime(cls, value):
        """Ensure scheduled_at is parsed from ISO strings when provided."""
        if value in (None, ""):
            return None
        if isinstance(value, datetime):
            return value
        try:
            return datetime.fromisoformat(value)
        except ValueError as exc:
            raise ValueError(
                "scheduled_at must be a valid ISO datetime string"
            ) from exc


class NodeIntegrationTodo(BaseModel):
    """Optional payload to create a todo/assignment alongside the node."""

    assigned_to: Optional[int] = Field(
        None, description="User ID that should complete the todo"
    )
    due_in_days: Optional[int] = Field(
        None, ge=1, le=60, description="Number of days until the todo is due"
    )
    priority: Optional[str] = Field(
        None, description="Todo priority (low, medium, high, urgent)"
    )
    is_assignment: Optional[bool] = Field(
        True, description="Whether the todo should be treated as an assignment"
    )
    assignment_type: Optional[str] = Field(
        None, description="Assignment type label (e.g. coding)"
    )
    category: Optional[str] = Field(None, description="Optional category slug")
    title: Optional[str] = Field(
        None, description="Override title for the generated todo"
    )
    description: Optional[str] = Field(
        None, description="Override description for the generated todo"
    )


class WorkflowNodeBase(BaseModel):
    """Base schema for process nodes"""

    node_type: NodeType = Field(..., description="Type of the node")
    title: str = Field(..., min_length=1, max_length=255, description="Node title")
    description: Optional[str] = Field(None, description="Node description")
    instructions: Optional[str] = Field(
        None, description="Instructions for participants"
    )
    estimated_duration_minutes: Optional[int] = Field(
        None, ge=5, le=1440, description="Estimated duration in minutes"
    )
    is_required: bool = Field(True, description="Whether this node is required")
    can_skip: bool = Field(False, description="Whether this node can be skipped")
    auto_advance: bool = Field(
        False, description="Whether to auto-advance after completion"
    )

    @field_validator("title")
    @classmethod
    def validate_title(cls, v):
        return v.strip()


class WorkflowNodeCreate(WorkflowNodeBase):
    """Schema for creating a process node"""

    sequence_order: int = Field(
        ..., ge=0, description="Order of the node in the sequence"
    )
    position: WorkflowNodePosition = Field(..., description="Position in visual editor")
    config: dict[str, Any] = Field(
        default_factory=dict, description="Node-specific configuration"
    )
    requirements: list[str] | None = Field(
        default_factory=list, description="Requirements for this node"
    )

    @field_validator("config")
    @classmethod
    def validate_config(cls, v, info):
        node_type = info.data.get("node_type")
        if not node_type:
            return v

        # Validate config based on node type
        try:
            if node_type == NodeType.INTERVIEW:
                InterviewNodeConfig(**v)
            elif node_type == NodeType.TODO:
                TodoNodeConfig(**v)
            elif node_type == NodeType.ASSESSMENT:
                AssessmentNodeConfig(**v)
            elif node_type == NodeType.DECISION:
                DecisionNodeConfig(**v)
        except Exception as e:
            raise ValueError(f"Invalid config for node type {node_type}: {str(e)}")

        return v


class WorkflowNodeCreateWithIntegration(WorkflowNodeCreate):
    """Schema for creating a node with optional interview/todo integration."""

    create_interview: Optional[NodeIntegrationInterview] = Field(default=None)
    create_todo: Optional[NodeIntegrationTodo] = Field(default=None)


class WorkflowNodeUpdate(BaseModel):
    """Schema for updating a process node"""

    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    instructions: Optional[str] = None
    estimated_duration_minutes: Optional[int] = Field(None, ge=5, le=1440)
    position: Optional[WorkflowNodePosition] = None
    config: dict[str, Any] | None = None
    requirements: list[str] | None = None
    is_required: Optional[bool] = None
    can_skip: Optional[bool] = None
    auto_advance: Optional[bool] = None

    @field_validator("title")
    @classmethod
    def validate_title(cls, v):
        if v is not None:
            return v.strip()
        return v


class WorkflowNodeInfo(WorkflowNodeBase):
    """Schema for process node information"""

    id: int
    workflow_id: int
    sequence_order: int
    position_x: float
    position_y: float
    config: dict[str, Any]
    requirements: list[str] | None
    status: NodeStatus
    created_by: int
    updated_by: Optional[int]
    created_at: datetime
    updated_at: datetime

    # Computed fields
    execution_count: Optional[int] = Field(
        None, description="Number of executions for this node"
    )
    completion_rate: Optional[float] = Field(
        None, description="Completion rate for this node"
    )
    average_duration_minutes: Optional[float] = Field(
        None, description="Average execution duration"
    )

    class Config:
        from_attributes = True


class WorkflowNodeDetails(WorkflowNodeInfo):
    """Detailed schema for process node with execution statistics"""

    pending_executions: int = Field(0, description="Number of pending executions")
    in_progress_executions: int = Field(
        0, description="Number of in-progress executions"
    )
    completed_executions: int = Field(0, description="Number of completed executions")
    failed_executions: int = Field(0, description="Number of failed executions")


class WorkflowNodeConnectionCreate(BaseModel):
    """Schema for creating a node connection"""

    source_node_id: int = Field(..., description="Source node ID")
    target_node_id: int = Field(..., description="Target node ID")
    condition_type: str = Field("success", description="Connection condition type")
    condition_config: dict[str, Any] | None = Field(
        default_factory=dict, description="Condition configuration"
    )
    label: Optional[str] = Field(None, max_length=255, description="Connection label")
    description: Optional[str] = Field(
        None, max_length=500, description="Connection description"
    )

    @field_validator("source_node_id", "target_node_id")
    @classmethod
    def validate_node_ids(cls, v):
        if v <= 0:
            raise ValueError("Node ID must be positive")
        return v

    @field_validator("condition_config")
    @classmethod
    def validate_condition_config(cls, v, info):
        condition_type = info.data.get("condition_type")
        if condition_type == "conditional" and not v:
            raise ValueError("Conditional connections require condition_config")
        return v


class WorkflowNodeConnectionInfo(BaseModel):
    """Schema for node connection information"""

    id: int
    workflow_id: int
    source_node_id: int
    target_node_id: int
    condition_type: str
    condition_config: dict[str, Any] | None
    label: Optional[str]
    description: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class NodeReorder(BaseModel):
    """Schema for reordering nodes"""

    node_sequence_updates: list[dict[str, int]] = Field(
        ..., description="List of {node_id: new_sequence_order} mappings"
    )

    @field_validator("node_sequence_updates")
    @classmethod
    def validate_node_sequence_updates(cls, v):
        if not v:
            raise ValueError("At least one node sequence update is required")

        # Check for duplicate sequence orders
        sequences = [update.get("sequence_order") for update in v]
        if len(sequences) != len(set(sequences)):
            raise ValueError("Duplicate sequence orders are not allowed")

        return v


class BulkNodeUpdate(BaseModel):
    """Schema for bulk updating nodes"""

    node_updates: list[dict[str, Any]] = Field(..., description="List of node updates")

    @field_validator("node_updates")
    @classmethod
    def validate_node_updates(cls, v):
        if not v:
            raise ValueError("At least one node update is required")

        # Validate each update has an id
        for update in v:
            if "id" not in update:
                raise ValueError("Each node update must include an 'id' field")

        return v
