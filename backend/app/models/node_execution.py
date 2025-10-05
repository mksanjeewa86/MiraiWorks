from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    DECIMAL,
    JSON,
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
    from app.models.interview import Interview
    from app.models.todo import Todo
    from app.models.user import User


class WorkflowNodeExecution(Base):
    __tablename__ = "workflow_node_executions"
    __table_args__ = (
        UniqueConstraint(
            "candidate_process_id", "node_id", name="uq_candidate_node_execution"
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    # Core relationships
    candidate_workflow_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("candidate_workflows.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    node_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("workflow_nodes.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Execution status
    status: Mapped[str] = mapped_column(
        String(50), nullable=False, default="pending", index=True
    )  # pending, scheduled, in_progress, awaiting_input, completed, failed, skipped

    # Results and evaluation
    result: Mapped[str | None] = mapped_column(
        String(50), nullable=True, index=True
    )  # pass, fail, pending_review, approved, rejected
    score: Mapped[float | None] = mapped_column(DECIMAL(5, 2), nullable=True)
    feedback: Mapped[str | None] = mapped_column(Text, nullable=True)
    assessor_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    execution_data: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    # Linked resources (interviews/todos created for this execution)
    interview_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("interviews.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    todo_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("todos.id", ondelete="SET NULL"), nullable=True, index=True
    )

    # Timing
    started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    due_date: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Actors
    assigned_to: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    completed_by: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    reviewed_by: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )

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
    candidate_workflow: Mapped[CandidateProcess] = relationship(
        "CandidateProcess", back_populates="executions"
    )
    node: Mapped[ProcessNode] = relationship("ProcessNode", back_populates="executions")
    assignee: Mapped[User | None] = relationship(
        "User", foreign_keys=[assigned_to], back_populates="assigned_node_executions"
    )
    completer: Mapped[User | None] = relationship(
        "User", foreign_keys=[completed_by], back_populates="completed_node_executions"
    )
    reviewer: Mapped[User | None] = relationship(
        "User", foreign_keys=[reviewed_by], back_populates="reviewed_node_executions"
    )

    # Linked resources
    interview: Mapped[Interview | None] = relationship(
        "Interview", foreign_keys=[interview_id]
    )
    todo: Mapped[Todo | None] = relationship("Todo", foreign_keys=[todo_id])

    @property
    def is_pending(self) -> bool:
        return self.status == "pending"

    @property
    def is_in_progress(self) -> bool:
        return self.status == "in_progress"

    @property
    def is_completed(self) -> bool:
        return self.status == "completed"

    @property
    def is_failed(self) -> bool:
        return self.status == "failed"

    @property
    def is_overdue(self) -> bool:
        if not self.due_date or self.is_completed:
            return False
        return datetime.utcnow() > self.due_date

    @property
    def duration_minutes(self) -> int | None:
        """Calculate execution duration in minutes"""
        if not self.started_at or not self.completed_at:
            return None

        delta = self.completed_at - self.started_at
        return int(delta.total_seconds() / 60)

    def start(self, assigned_to: int | None = None) -> None:
        """Start the execution"""
        if self.status not in ["pending", "scheduled"]:
            raise ValueError(f"Cannot start execution with status '{self.status}'")

        self.status = "in_progress"
        self.started_at = datetime.utcnow()
        if assigned_to:
            self.assigned_to = assigned_to

    def complete(
        self,
        result: str,
        completed_by: int,
        score: float | None = None,
        feedback: str | None = None,
        execution_data: dict | None = None,
    ) -> None:
        """Complete the execution"""
        if self.status not in ["in_progress", "awaiting_input"]:
            raise ValueError(f"Cannot complete execution with status '{self.status}'")

        self.status = "completed"
        self.result = result
        self.completed_at = datetime.utcnow()
        self.completed_by = completed_by

        if score is not None:
            self.score = score
        if feedback:
            self.feedback = feedback
        if execution_data:
            self.execution_data = execution_data

    def fail(self, completed_by: int, reason: str | None = None) -> None:
        """Mark execution as failed"""
        self.status = "failed"
        self.result = "fail"
        self.completed_at = datetime.utcnow()
        self.completed_by = completed_by
        if reason:
            self.feedback = reason

    def skip(self, completed_by: int, reason: str | None = None) -> None:
        """Skip this execution"""
        self.status = "skipped"
        self.result = "skipped"
        self.completed_at = datetime.utcnow()
        self.completed_by = completed_by
        if reason:
            self.feedback = reason

    def schedule(self, due_date: datetime | None = None) -> None:
        """Schedule the execution"""
        if self.status != "pending":
            raise ValueError("Only pending executions can be scheduled")

        self.status = "scheduled"
        if due_date:
            self.due_date = due_date

    def await_input(self) -> None:
        """Mark as awaiting input (e.g., candidate submission)"""
        if self.status != "in_progress":
            raise ValueError("Only in-progress executions can await input")

        self.status = "awaiting_input"

    def link_interview(self, interview_id: int) -> None:
        """Link an interview to this execution"""
        self.interview_id = interview_id

    def link_todo(self, todo_id: int) -> None:
        """Link a todo to this execution"""
        self.todo_id = todo_id

    def add_review(self, reviewer_id: int, notes: str | None = None) -> None:
        """Add reviewer notes"""
        self.reviewed_by = reviewer_id
        if notes:
            self.assessor_notes = notes

    def __repr__(self) -> str:
        return f"<NodeExecution(id={self.id}, node_id={self.node_id}, status='{self.status}', result='{self.result}')>"
