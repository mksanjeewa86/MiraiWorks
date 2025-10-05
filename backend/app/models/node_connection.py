from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import JSON, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    pass


class WorkflowNodeConnection(Base):
    __tablename__ = "workflow_node_connections"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    # Process relationship
    workflow_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("workflows.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Connection endpoints
    source_node_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("workflow_nodes.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    target_node_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("workflow_nodes.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Connection configuration
    condition_type: Mapped[str] = mapped_column(
        String(50), nullable=False, default="success", index=True
    )  # success, failure, conditional, always
    condition_config: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    # Metadata
    label: Mapped[str | None] = mapped_column(String(255), nullable=True)
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False, index=True
    )

    # Relationships
    workflow: Mapped[RecruitmentProcess] = relationship("RecruitmentProcess")
    source_node: Mapped[ProcessNode] = relationship(
        "ProcessNode",
        foreign_keys=[source_node_id],
        back_populates="outgoing_connections",
    )
    target_node: Mapped[ProcessNode] = relationship(
        "ProcessNode",
        foreign_keys=[target_node_id],
        back_populates="incoming_connections",
    )

    @property
    def is_success_path(self) -> bool:
        return self.condition_type == "success"

    @property
    def is_failure_path(self) -> bool:
        return self.condition_type == "failure"

    @property
    def is_conditional(self) -> bool:
        return self.condition_type == "conditional"

    def evaluate_condition(
        self, execution_result: str, execution_data: dict | None = None
    ) -> bool:
        """Evaluate whether this connection should be taken based on execution result"""
        if self.condition_type == "always":
            return True

        if self.condition_type == "success":
            return execution_result in ["pass", "completed", "approved"]

        if self.condition_type == "failure":
            return execution_result in ["fail", "failed", "rejected"]

        if self.condition_type == "conditional" and self.condition_config:
            # Custom condition evaluation based on config
            return self._evaluate_custom_condition(execution_result, execution_data)

        return False

    def _evaluate_custom_condition(
        self, execution_result: str, execution_data: dict | None = None
    ) -> bool:
        """Evaluate custom conditions based on condition_config"""
        if not self.condition_config:
            return False

        # Simple condition evaluation
        required_result = self.condition_config.get("required_result")
        if required_result and execution_result == required_result:
            return True

        # Score-based conditions
        min_score = self.condition_config.get("min_score")
        if min_score and execution_data:
            score = execution_data.get("score")
            if score is not None and score >= min_score:
                return True

        return False

    def __repr__(self) -> str:
        return f"<NodeConnection(id={self.id}, {self.source_node_id}->{self.target_node_id}, condition='{self.condition_type}')>"
