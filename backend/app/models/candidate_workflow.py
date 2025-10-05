from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    DECIMAL,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.workflow import Workflow
    from app.models.workflow_node import WorkflowNode
    from app.models.workflow_node_execution import WorkflowNodeExecution


class CandidateWorkflow(Base):
    __tablename__ = "candidate_workflows"
    __table_args__ = (
        UniqueConstraint("candidate_id", "workflow_id", name="uq_candidate_workflow"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    # Core relationships
    candidate_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    workflow_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("workflows.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    current_node_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("workflow_nodes.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # Status tracking
    status: Mapped[str] = mapped_column(
        String(50), nullable=False, default="not_started", index=True
    )  # not_started, in_progress, completed, failed, withdrawn, on_hold

    # Assignment and ownership
    assigned_recruiter_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    assigned_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Progress tracking
    started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    failed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    withdrawn_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Evaluation
    overall_score: Mapped[float | None] = mapped_column(DECIMAL(5, 2), nullable=True)
    final_result: Mapped[str | None] = mapped_column(
        String(50), nullable=True, index=True
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False, index=True
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    # Relationships
    candidate: Mapped[User] = relationship(
        "User", foreign_keys=[candidate_id], back_populates="candidate_workflows"
    )
    workflow: Mapped[Workflow] = relationship(
        "Workflow", back_populates="candidate_workflows"
    )
    current_node: Mapped[WorkflowNode | None] = relationship(
        "WorkflowNode", foreign_keys=[current_node_id]
    )
    assigned_recruiter: Mapped[User | None] = relationship(
        "User",
        foreign_keys=[assigned_recruiter_id],
        back_populates="assigned_candidate_workflows",
    )

    executions: Mapped[list[WorkflowNodeExecution]] = relationship(
        "WorkflowNodeExecution",
        back_populates="candidate_workflow",
        cascade="all, delete-orphan",
    )

    @property
    def is_active(self) -> bool:
        return self.status == "in_progress"

    @property
    def is_completed(self) -> bool:
        return self.status == "completed"

    @property
    def is_failed(self) -> bool:
        return self.status == "failed"

    @property
    def is_withdrawn(self) -> bool:
        return self.status == "withdrawn"

    @property
    def progress_percentage(self) -> float:
        """Calculate progress as percentage of completed nodes"""
        if not self.executions:
            return 0.0

        total_nodes = len(self.workflow.nodes)
        if total_nodes == 0:
            return 0.0

        completed_executions = [
            execution
            for execution in self.executions
            if execution.status == "completed"
        ]

        return (len(completed_executions) / total_nodes) * 100.0

    @property
    def current_step_title(self) -> str | None:
        """Get the title of the current step"""
        if self.current_node:
            return self.current_node.title
        return None

    def start(self, first_node_id: int) -> None:
        """Start the candidate process"""
        if self.status != "not_started":
            raise ValueError("Process has already been started")

        self.status = "in_progress"
        self.current_node_id = first_node_id
        self.started_at = datetime.utcnow()

    def complete(
        self,
        final_result: str,
        overall_score: float | None = None,
        notes: str | None = None,
    ) -> None:
        """Mark the process as completed"""
        self.status = "completed"
        self.completed_at = datetime.utcnow()
        self.final_result = final_result
        self.current_node_id = None

        if overall_score is not None:
            self.overall_score = overall_score
        if notes:
            self.notes = notes

    def fail(
        self, reason: str | None = None, failed_at_node_id: int | None = None
    ) -> None:
        """Mark the process as failed"""
        self.status = "failed"
        self.failed_at = datetime.utcnow()
        self.final_result = "failed"

        if reason:
            self.notes = reason
        if failed_at_node_id:
            self.current_node_id = failed_at_node_id

    def withdraw(self, reason: str | None = None) -> None:
        """Mark the process as withdrawn"""
        self.status = "withdrawn"
        self.withdrawn_at = datetime.utcnow()
        self.final_result = "withdrawn"
        self.current_node_id = None

        if reason:
            self.notes = reason

    def put_on_hold(self) -> None:
        """Put the process on hold"""
        if self.status not in ["in_progress"]:
            raise ValueError("Only in-progress processes can be put on hold")
        self.status = "on_hold"

    def resume(self) -> None:
        """Resume a process that was on hold"""
        if self.status != "on_hold":
            raise ValueError("Only processes on hold can be resumed")
        self.status = "in_progress"

    def advance_to_node(self, next_node_id: int | None) -> None:
        """Advance to the next node"""
        self.current_node_id = next_node_id

    def assign_recruiter(self, recruiter_id: int) -> None:
        """Assign a recruiter to this process"""
        self.assigned_recruiter_id = recruiter_id
        self.assigned_at = datetime.utcnow()

    def __repr__(self) -> str:
        return f"<CandidateWorkflow(id={self.id}, candidate_id={self.candidate_id}, status='{self.status}')>"
