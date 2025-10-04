from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import JSON, DateTime, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.recruitment_process import RecruitmentProcess
    from app.models.user import User


class ProcessViewer(Base):
    __tablename__ = "process_viewers"
    __table_args__ = (
        UniqueConstraint("process_id", "user_id", name="uq_process_viewer"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    # Core relationships
    process_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("recruitment_processes.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # Role and permissions
    role: Mapped[str] = mapped_column(
        String(50), nullable=False, index=True
    )  # recruiter, observer, admin, assistant
    permissions: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    # Audit
    added_by: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    added_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False, index=True
    )

    # Relationships
    process: Mapped[RecruitmentProcess] = relationship(
        "RecruitmentProcess", back_populates="viewers"
    )
    user: Mapped[User] = relationship(
        "User", foreign_keys=[user_id], back_populates="process_viewers"
    )
    added_by_user: Mapped[User] = relationship(
        "User", foreign_keys=[added_by], back_populates="added_process_viewers"
    )

    @property
    def is_recruiter(self) -> bool:
        return self.role == "recruiter"

    @property
    def is_observer(self) -> bool:
        return self.role == "observer"

    @property
    def is_admin(self) -> bool:
        return self.role == "admin"

    @property
    def can_execute(self) -> bool:
        """Check if this viewer can execute process nodes"""
        return self.role in ["recruiter", "admin"]

    @property
    def can_view_all_candidates(self) -> bool:
        """Check if this viewer can see all candidates in the process"""
        return self.role in ["recruiter", "admin", "observer"]

    @property
    def can_schedule_interviews(self) -> bool:
        """Check if this viewer can schedule interviews"""
        return self.role in ["recruiter", "admin"]

    @property
    def can_record_results(self) -> bool:
        """Check if this viewer can record node execution results"""
        return self.role in ["recruiter", "admin"]

    def has_permission(self, permission: str) -> bool:
        """Check if this viewer has a specific permission"""
        if not self.permissions:
            # Use role-based defaults
            default_permissions = self._get_default_permissions()
            return permission in default_permissions

        return self.permissions.get(permission, False)

    def _get_default_permissions(self) -> list[str]:
        """Get default permissions based on role"""
        if self.role == "recruiter":
            return [
                "view_process",
                "view_candidates",
                "execute_nodes",
                "schedule_interviews",
                "record_results",
                "view_results",
                "add_notes",
            ]
        elif self.role == "admin":
            return [
                "view_process",
                "view_candidates",
                "execute_nodes",
                "schedule_interviews",
                "record_results",
                "view_results",
                "add_notes",
                "override_results",
                "manage_assignments",
            ]
        elif self.role == "observer":
            return ["view_process", "view_candidates", "view_results"]
        elif self.role == "assistant":
            return ["view_process", "schedule_interviews", "add_notes"]
        else:
            return ["view_process"]

    def grant_permission(self, permission: str) -> None:
        """Grant a specific permission to this viewer"""
        if not self.permissions:
            self.permissions = {}

        self.permissions[permission] = True

    def revoke_permission(self, permission: str) -> None:
        """Revoke a specific permission from this viewer"""
        if not self.permissions:
            self.permissions = {}

        self.permissions[permission] = False

    def __repr__(self) -> str:
        return f"<ProcessViewer(id={self.id}, process_id={self.process_id}, user_id={self.user_id}, role='{self.role}')>"
