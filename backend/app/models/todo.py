from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import JSON, Boolean, Date, DateTime, ForeignKey, Integer, String, Text, Time
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel
from app.utils.constants import (
    VisibilityStatus,
    TodoPriority,
    TodoPublishStatus,
    TodoStatus,
    TodoType,
)
from app.utils.datetime_utils import get_utc_now

if TYPE_CHECKING:
    from app.models.exam import Exam
    from app.models.todo_extension_request import TodoExtensionRequest
    from app.models.user import User
    from app.models.workflow import Workflow


class Todo(BaseModel):
    __tablename__ = "todos"
    owner_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    created_by: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    last_updated_by: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )

    # Workflow relationship
    workflow_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("workflows.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default=TodoStatus.PENDING.value, index=True
    )
    priority: Mapped[str | None] = mapped_column(
        String(20), nullable=True, default=TodoPriority.MID.value
    )

    # Todo type and publishing
    todo_type: Mapped[str] = mapped_column(
        String(20), nullable=False, default=TodoType.REGULAR.value, index=True
    )
    publish_status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default=TodoPublishStatus.PUBLISHED.value,
        index=True,
    )

    # Assignment specific fields
    assignee_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    visibility_status: Mapped[str | None] = mapped_column(
        String(20), nullable=True, index=True
    )
    assignment_assessment: Mapped[str | None] = mapped_column(Text, nullable=True)
    assignment_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    submitted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    reviewed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    reviewed_by: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )

    # Exam specific fields (for TodoType.EXAM)
    exam_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("exams.id", ondelete="SET NULL"), nullable=True, index=True
    )
    exam_assignment_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("exam_assignments.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    exam_config: Mapped[dict | None] = mapped_column(
        JSON, nullable=True
    )  # Stores exam-specific configuration

    is_deleted: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, index=True
    )
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    # Store due datetime in UTC
    due_datetime: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, index=True
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    expired_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    owner: Mapped[User] = relationship("User", foreign_keys=[owner_id], backref="todos")
    creator: Mapped[User | None] = relationship(
        "User", foreign_keys=[created_by], backref="created_todos"
    )
    updater: Mapped[User | None] = relationship(
        "User", foreign_keys=[last_updated_by], backref="updated_todos"
    )
    assignee: Mapped[User | None] = relationship(
        "User", foreign_keys=[assignee_id], backref="assigned_todos"
    )
    reviewer: Mapped[User | None] = relationship(
        "User", foreign_keys=[reviewed_by], backref="reviewed_todos"
    )
    workflow: Mapped[Optional[Workflow]] = relationship(
        "Workflow", foreign_keys=[workflow_id]
    )
    extension_requests: Mapped[list[TodoExtensionRequest]] = relationship(
        "TodoExtensionRequest", back_populates="todo", cascade="all, delete-orphan"
    )
    exam: Mapped[Optional[Exam]] = relationship(
        "Exam", foreign_keys=[exam_id], backref="todos"
    )
    # exam_assignment relationship is created by backref from ExamAssignment.todo

    @property
    def is_completed(self) -> bool:
        return self.status == TodoStatus.COMPLETED.value

    @property
    def is_expired(self) -> bool:
        """Check if todo is expired based on due datetime (stored in UTC)."""
        from datetime import timezone

        if self.status == TodoStatus.COMPLETED.value:
            return False
        if self.expired_at:
            return True
        if self.due_datetime:
            # Ensure due_datetime is timezone-aware (MySQL returns naive datetimes)
            due_dt = self.due_datetime
            if due_dt.tzinfo is None:
                due_dt = due_dt.replace(tzinfo=timezone.utc)
            return due_dt < get_utc_now()
        return False

    def mark_completed(self) -> None:
        self.status = TodoStatus.COMPLETED.value
        self.completed_at = get_utc_now()
        self.expired_at = None

    def mark_pending(self) -> None:
        self.status = TodoStatus.PENDING.value
        self.completed_at = None
        self.expired_at = None

    def soft_delete(self) -> None:
        self.is_deleted = True
        self.deleted_at = get_utc_now()

    def restore(self) -> None:
        self.is_deleted = False
        self.deleted_at = None

    @property
    def is_assignment(self) -> bool:
        return self.todo_type == TodoType.ASSIGNMENT.value

    @property
    def is_exam(self) -> bool:
        return self.todo_type == TodoType.EXAM.value

    @property
    def is_published(self) -> bool:
        return self.publish_status == TodoPublishStatus.PUBLISHED.value

    @property
    def is_draft(self) -> bool:
        return self.publish_status == TodoPublishStatus.DRAFT.value

    def publish(self) -> None:
        """Publish the todo (make it visible to assignee and viewers)"""
        self.publish_status = TodoPublishStatus.PUBLISHED.value

    def make_draft(self) -> None:
        """Make the todo a draft (hide from assignee and viewers)"""
        self.publish_status = TodoPublishStatus.DRAFT.value

    def submit_assignment(self) -> None:
        """Mark assignment as submitted"""
        if self.is_assignment:
            self.submitted_at = get_utc_now()
            self.status = TodoStatus.COMPLETED.value
            self.completed_at = get_utc_now()

    def start_review(self) -> None:
        """Start review process for assignment"""
        if self.is_assignment and self.submitted_at:
            # Review process can start after submission
            pass

    def approve_assignment(
        self, reviewer_id: int, assessment: str = None, score: int = None
    ) -> None:
        """Mark assignment as approved"""
        if self.is_assignment:
            self.reviewed_at = get_utc_now()
            self.reviewed_by = reviewer_id
            if assessment:
                self.assignment_assessment = assessment
            if score is not None:
                self.assignment_score = score

    def reject_assignment(
        self, reviewer_id: int, assessment: str = None, score: int = None
    ) -> None:
        """Mark assignment as rejected"""
        if self.is_assignment:
            self.reviewed_at = get_utc_now()
            self.reviewed_by = reviewer_id
            if assessment:
                self.assignment_assessment = assessment
            if score is not None:
                self.assignment_score = score

    @property
    def can_be_edited_by_assignee(self) -> bool:
        """Check if assignee can edit the todo"""
        if not self.is_assignment:
            return True
        # Assignee can edit until submission
        return self.submitted_at is None

    def set_visible(self) -> None:
        """Make todo visible to assignee"""
        self.visibility_status = VisibilityStatus.VISIBLE.value

    def set_hidden(self) -> None:
        """Hide todo from assignee"""
        self.visibility_status = VisibilityStatus.HIDDEN.value

    @property
    def is_visible_to_assignee(self) -> bool:
        """Check if todo is visible to assignee"""
        return self.visibility_status == VisibilityStatus.VISIBLE.value
