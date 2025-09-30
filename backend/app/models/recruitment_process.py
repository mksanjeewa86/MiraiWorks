from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, JSON, DECIMAL
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.company import Company
    from app.models.position import Position
    from app.models.process_node import ProcessNode
    from app.models.candidate_process import CandidateProcess
    from app.models.process_viewer import ProcessViewer


class RecruitmentProcess(Base):
    __tablename__ = "recruitment_processes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    employer_company_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True
    )
    position_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("positions.id", ondelete="SET NULL"), nullable=True, index=True
    )
    created_by: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    updated_by: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )

    # Status and versioning
    status: Mapped[str] = mapped_column(
        String(50), nullable=False, default="draft", index=True
    )  # draft, active, archived, inactive
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    # Template related
    is_template: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    template_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Configuration
    settings: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False, index=True
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )
    activated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    archived_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Relationships
    employer_company: Mapped[Company] = relationship(
        "Company", foreign_keys=[employer_company_id], back_populates="recruitment_processes"
    )
    position: Mapped[Optional[Position]] = relationship(
        "Position", foreign_keys=[position_id], back_populates="recruitment_processes"
    )
    creator: Mapped[User] = relationship(
        "User", foreign_keys=[created_by], back_populates="created_recruitment_processes"
    )
    updater: Mapped[Optional[User]] = relationship(
        "User", foreign_keys=[updated_by], back_populates="updated_recruitment_processes"
    )

    nodes: Mapped[list[ProcessNode]] = relationship(
        "ProcessNode", back_populates="process", cascade="all, delete-orphan"
    )
    candidate_processes: Mapped[list[CandidateProcess]] = relationship(
        "CandidateProcess", back_populates="process", cascade="all, delete-orphan"
    )
    viewers: Mapped[list[ProcessViewer]] = relationship(
        "ProcessViewer", back_populates="process", cascade="all, delete-orphan"
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
        self.activated_at = datetime.utcnow()
        self.updated_by = activated_by

    def archive(self, archived_by: int) -> None:
        """Archive the process"""
        self.status = "archived"
        self.archived_at = datetime.utcnow()
        self.updated_by = archived_by

    def deactivate(self, deactivated_by: int) -> None:
        """Deactivate the process"""
        self.status = "inactive"
        self.updated_by = deactivated_by

    def __repr__(self) -> str:
        return f"<RecruitmentProcess(id={self.id}, name='{self.name}', status='{self.status}')>"