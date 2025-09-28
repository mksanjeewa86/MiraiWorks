from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.utils.constants import TodoStatus, TodoVisibility, TodoType, TodoPublishStatus, AssignmentStatus

if TYPE_CHECKING:
    from app.models.todo_extension_request import TodoExtensionRequest
    from app.models.todo_viewer import TodoViewer
    from app.models.user import User


class Todo(Base):
    __tablename__ = "todos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    owner_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    created_by: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    last_updated_by: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    assigned_user_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default=TodoStatus.PENDING.value, index=True
    )
    priority: Mapped[str | None] = mapped_column(String(20), nullable=True)
    visibility: Mapped[str] = mapped_column(
        String(20), nullable=False, default=TodoVisibility.PRIVATE.value, index=True
    )

    # Todo type and publishing
    todo_type: Mapped[str] = mapped_column(
        String(20), nullable=False, default=TodoType.REGULAR.value, index=True
    )
    publish_status: Mapped[str] = mapped_column(
        String(20), nullable=False, default=TodoPublishStatus.PUBLISHED.value, index=True
    )

    # Assignment specific fields
    assignment_status: Mapped[str | None] = mapped_column(
        String(20), nullable=True, index=True
    )
    assignment_assessment: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )
    assignment_score: Mapped[int | None] = mapped_column(
        Integer, nullable=True
    )
    submitted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    reviewed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    reviewed_by: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )

    is_deleted: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, index=True
    )
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    due_date: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    expired_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False, index=True
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    owner: Mapped[User] = relationship("User", foreign_keys=[owner_id], backref="todos")
    creator: Mapped[User | None] = relationship(
        "User", foreign_keys=[created_by], backref="created_todos"
    )
    updater: Mapped[User | None] = relationship(
        "User", foreign_keys=[last_updated_by], backref="updated_todos"
    )
    assigned_user: Mapped[User | None] = relationship(
        "User", foreign_keys=[assigned_user_id], backref="assigned_todos"
    )
    reviewer: Mapped[User | None] = relationship(
        "User", foreign_keys=[reviewed_by], backref="reviewed_todos"
    )
    viewers: Mapped[list[TodoViewer]] = relationship(
        "TodoViewer", back_populates="todo", cascade="all, delete-orphan"
    )
    extension_requests: Mapped[list[TodoExtensionRequest]] = relationship(
        "TodoExtensionRequest", back_populates="todo", cascade="all, delete-orphan"
    )

    @property
    def is_completed(self) -> bool:
        return self.status == TodoStatus.COMPLETED.value

    @property
    def is_expired(self) -> bool:
        if self.status == TodoStatus.COMPLETED.value:
            return False
        if self.expired_at:
            return True
        if self.due_date:
            return self.due_date < datetime.utcnow()
        return False

    def mark_completed(self) -> None:
        self.status = TodoStatus.COMPLETED.value
        self.completed_at = datetime.utcnow()
        self.expired_at = None

    def mark_pending(self) -> None:
        self.status = TodoStatus.PENDING.value
        self.completed_at = None
        self.expired_at = None

    def soft_delete(self) -> None:
        self.is_deleted = True
        self.deleted_at = datetime.utcnow()

    def restore(self) -> None:
        self.is_deleted = False
        self.deleted_at = None

    @property
    def is_assignment(self) -> bool:
        return self.todo_type == TodoType.ASSIGNMENT.value

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
            self.assignment_status = AssignmentStatus.SUBMITTED.value
            self.submitted_at = datetime.utcnow()
            self.status = TodoStatus.COMPLETED.value
            self.completed_at = datetime.utcnow()

    def start_review(self) -> None:
        """Start review process for assignment"""
        if self.is_assignment and self.assignment_status == AssignmentStatus.SUBMITTED.value:
            self.assignment_status = AssignmentStatus.UNDER_REVIEW.value

    def approve_assignment(self, reviewer_id: int, assessment: str = None, score: int = None) -> None:
        """Mark assignment as approved"""
        if self.is_assignment:
            self.assignment_status = AssignmentStatus.APPROVED.value
            self.reviewed_at = datetime.utcnow()
            self.reviewed_by = reviewer_id
            if assessment:
                self.assignment_assessment = assessment
            if score is not None:
                self.assignment_score = score

    def reject_assignment(self, reviewer_id: int, assessment: str = None, score: int = None) -> None:
        """Mark assignment as rejected"""
        if self.is_assignment:
            self.assignment_status = AssignmentStatus.REJECTED.value
            self.reviewed_at = datetime.utcnow()
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
        return self.assignment_status not in [
            AssignmentStatus.SUBMITTED.value,
            AssignmentStatus.UNDER_REVIEW.value,
            AssignmentStatus.APPROVED.value,
            AssignmentStatus.REJECTED.value
        ]
