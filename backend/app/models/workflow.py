from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel
from app.utils.datetime_utils import get_utc_now

if TYPE_CHECKING:
    from app.models.candidate_workflow import CandidateWorkflow
    from app.models.company import Company
    from app.models.interview import Interview
    from app.models.position import Position
    from app.models.todo import Todo
    from app.models.user import User
    from app.models.workflow_node import WorkflowNode
    from app.models.workflow_viewer import WorkflowViewer


class Workflow(BaseModel):
    __tablename__ = "workflows"
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    employer_company_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    position_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("positions.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    created_by: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    updated_by: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )

    # Status and versioning
    status: Mapped[str] = mapped_column(
        String(50), nullable=False, default="draft", index=True
    )  # draft, active, archived, inactive
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    # Template related
    is_template: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    template_name: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Configuration
    settings: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    # Additional timestamps
    activated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    archived_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Soft delete
    is_deleted: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, index=True
    )
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Relationships
    employer_company: Mapped[Company] = relationship(
        "Company",
        foreign_keys=[employer_company_id],
        back_populates="workflows",
    )
    position: Mapped[Position | None] = relationship(
        "Position", foreign_keys=[position_id], back_populates="workflows"
    )
    creator: Mapped[User] = relationship(
        "User",
        foreign_keys=[created_by],
        back_populates="created_workflows",
    )
    updater: Mapped[User | None] = relationship(
        "User",
        foreign_keys=[updated_by],
        back_populates="updated_workflows",
    )

    nodes: Mapped[list[WorkflowNode]] = relationship(
        "WorkflowNode", back_populates="workflow", cascade="all, delete-orphan"
    )
    candidate_workflows: Mapped[list[CandidateWorkflow]] = relationship(
        "CandidateWorkflow", back_populates="workflow", cascade="all, delete-orphan"
    )
    viewers: Mapped[list[WorkflowViewer]] = relationship(
        "WorkflowViewer", back_populates="workflow", cascade="all, delete-orphan"
    )
    interviews: Mapped[list[Interview]] = relationship(
        "Interview", foreign_keys="Interview.workflow_id", back_populates="workflow"
    )
    todos: Mapped[list[Todo]] = relationship(
        "Todo", foreign_keys="Todo.workflow_id", back_populates="workflow"
    )

    @property
    def is_active(self) -> bool:
        return self.status == "active"

    @property
    def is_draft(self) -> bool:
        return self.status == "draft"

    @property
    def can_be_edited(self) -> bool:
        return self.status in ["draft", "inactive"]

    def activate(self, activated_by: int) -> None:
        """Activate the process"""
        if self.status != "draft":
            raise ValueError("Only draft processes can be activated")

        self.status = "active"
        self.activated_at = get_utc_now()
        self.updated_by = activated_by

    def archive(self, archived_by: int) -> None:
        """Archive the process"""
        self.status = "archived"
        self.archived_at = get_utc_now()
        self.updated_by = archived_by

    def deactivate(self, deactivated_by: int) -> None:
        """Deactivate the process"""
        self.status = "inactive"
        self.updated_by = deactivated_by

    def __repr__(self) -> str:
        return f"<Workflow(id={self.id}, name='{self.name}', status='{self.status}')>"
