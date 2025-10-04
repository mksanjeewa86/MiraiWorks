from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.node_connection import NodeConnection
    from app.models.node_execution import NodeExecution
    from app.models.recruitment_process import RecruitmentProcess
    from app.models.user import User


class ProcessNode(Base):
    __tablename__ = "process_nodes"
    __table_args__ = (
        UniqueConstraint(
            "process_id", "sequence_order", name="uq_process_node_sequence"
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    # Process relationship
    process_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("recruitment_processes.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Node configuration
    node_type: Mapped[str] = mapped_column(
        String(50), nullable=False, index=True
    )  # interview, todo, assessment, decision
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Ordering and positioning
    sequence_order: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    position_x: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    position_y: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)

    # Configuration and requirements
    config: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    requirements: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    instructions: Mapped[str | None] = mapped_column(Text, nullable=True)
    estimated_duration_minutes: Mapped[int | None] = mapped_column(
        Integer, nullable=True
    )

    # Node behavior
    status: Mapped[str] = mapped_column(
        String(50), nullable=False, default="draft", index=True
    )  # draft, active, inactive
    is_required: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    can_skip: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    auto_advance: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    # Audit fields
    created_by: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    updated_by: Mapped[int | None] = mapped_column(
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
    process: Mapped[RecruitmentProcess] = relationship(
        "RecruitmentProcess", back_populates="nodes"
    )
    creator: Mapped[User] = relationship(
        "User", foreign_keys=[created_by], back_populates="created_process_nodes"
    )
    updater: Mapped[User | None] = relationship(
        "User", foreign_keys=[updated_by], back_populates="updated_process_nodes"
    )

    # Connections
    outgoing_connections: Mapped[list[NodeConnection]] = relationship(
        "NodeConnection",
        foreign_keys="NodeConnection.source_node_id",
        back_populates="source_node",
        cascade="all, delete-orphan",
    )
    incoming_connections: Mapped[list[NodeConnection]] = relationship(
        "NodeConnection",
        foreign_keys="NodeConnection.target_node_id",
        back_populates="target_node",
        cascade="all, delete-orphan",
    )

    # Executions
    executions: Mapped[list[NodeExecution]] = relationship(
        "NodeExecution", back_populates="node", cascade="all, delete-orphan"
    )

    @property
    def is_active(self) -> bool:
        return self.status == "active"

    @property
    def is_start_node(self) -> bool:
        return self.sequence_order == 1 or len(self.incoming_connections) == 0

    @property
    def is_end_node(self) -> bool:
        return len(self.outgoing_connections) == 0

    @property
    def next_nodes(self) -> list[ProcessNode]:
        """Get all nodes that can follow this node"""
        return [conn.target_node for conn in self.outgoing_connections]

    @property
    def previous_nodes(self) -> list[ProcessNode]:
        """Get all nodes that precede this node"""
        return [conn.source_node for conn in self.incoming_connections]

    def activate(self, updated_by: int) -> None:
        """Activate this node"""
        self.status = "active"
        self.updated_by = updated_by

    def deactivate(self, updated_by: int) -> None:
        """Deactivate this node"""
        self.status = "inactive"
        self.updated_by = updated_by

    def can_be_deleted(self) -> bool:
        """Check if this node can be safely deleted"""
        # Cannot delete if there are any executions
        return len(self.executions) == 0

    def __repr__(self) -> str:
        return f"<ProcessNode(id={self.id}, title='{self.title}', type='{self.node_type}', sequence={self.sequence_order})>"
