from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(
        Integer,
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    email = Column(String(255), nullable=False, unique=True, index=True)
    hashed_password = Column(String(255), nullable=True)  # Nullable for SSO-only users
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    phone = Column(String(50), nullable=True)
    is_active = Column(Boolean, nullable=False, default=False, index=True)
    is_admin = Column(Boolean, nullable=False, default=False, index=True)
    require_2fa = Column(Boolean, nullable=False, default=False, index=True)
    last_login = Column(DateTime(timezone=True), nullable=True)
    # Creation tracking
    created_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)  # ID of user who created this user (NULL for self-registration)
    # Logical deletion fields
    is_deleted = Column(Boolean, nullable=False, default=False, index=True)
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    deleted_by = Column(Integer, nullable=True)  # ID of user who deleted this user
    # Suspension fields
    is_suspended = Column(Boolean, nullable=False, default=False, index=True)
    suspended_at = Column(DateTime(timezone=True), nullable=True)
    suspended_by = Column(Integer, nullable=True)  # ID of user who suspended this user
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Relationships
    company = relationship("Company", back_populates="users", lazy="noload")
    user_roles = relationship(
        "UserRole", back_populates="user", cascade="all, delete-orphan", lazy="noload"
    )
    refresh_tokens = relationship(
        "RefreshToken", back_populates="user", cascade="all, delete-orphan"
    )
    password_reset_requests = relationship(
        "PasswordResetRequest",
        back_populates="user",
        foreign_keys="PasswordResetRequest.user_id",
        cascade="all, delete-orphan",
    )
    oauth_accounts = relationship(
        "OauthAccount", back_populates="user", cascade="all, delete-orphan"
    )
    audit_logs = relationship(
        "AuditLog", back_populates="actor", cascade="all, delete-orphan"
    )
    notifications = relationship(
        "Notification", back_populates="user", cascade="all, delete-orphan"
    )
    resumes = relationship(
        "Resume", back_populates="user", cascade="all, delete-orphan"
    )
    meetings = relationship(
        "Meeting", secondary="meeting_participants", back_populates="participants"
    )
    settings = relationship(
        "UserSettings",
        back_populates="user",
        cascade="all, delete-orphan",
        uselist=False,
    )
    calendar_connections = relationship(
        "CalendarConnection", back_populates="user", cascade="all, delete-orphan"
    )
    calendar_events = relationship(
        "CalendarEvent", back_populates="creator", cascade="all, delete-orphan"
    )
    # Todo extension request relationships
    requested_extensions = relationship(
        "TodoExtensionRequest",
        foreign_keys="TodoExtensionRequest.requested_by_id",
        back_populates="requested_by",
        cascade="all, delete-orphan"
    )
    extension_requests_to_review = relationship(
        "TodoExtensionRequest",
        foreign_keys="TodoExtensionRequest.creator_id",
        back_populates="creator",
        cascade="all, delete-orphan"
    )
    extension_responses = relationship(
        "TodoExtensionRequest",
        foreign_keys="TodoExtensionRequest.responded_by_id",
        back_populates="responded_by",
        cascade="all, delete-orphan"
    )
    mbti_test = relationship(
        "MBTITest", back_populates="user", cascade="all, delete-orphan", uselist=False
    )

    # User connections
    sent_connections = relationship(
        "UserConnection",
        foreign_keys="UserConnection.user_id",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    received_connections = relationship(
        "UserConnection",
        foreign_keys="UserConnection.connected_user_id",
        back_populates="connected_user",
        cascade="all, delete-orphan"
    )

    # Connection invitations
    sent_invitations = relationship(
        "ConnectionInvitation",
        foreign_keys="ConnectionInvitation.sender_id",
        back_populates="sender",
        cascade="all, delete-orphan"
    )
    received_invitations = relationship(
        "ConnectionInvitation",
        foreign_keys="ConnectionInvitation.receiver_id",
        back_populates="receiver",
        cascade="all, delete-orphan"
    )

    # Company follows (candidates following companies)
    followed_companies = relationship(
        "CompanyFollow",
        foreign_keys="CompanyFollow.candidate_id",
        back_populates="candidate",
        cascade="all, delete-orphan"
    )

    # Creator relationship (who created this user)
    creator = relationship("User", remote_side="User.id", post_update=True)

    # Recruitment process relationships
    created_recruitment_processes = relationship(
        "RecruitmentProcess",
        foreign_keys="RecruitmentProcess.created_by",
        back_populates="creator",
        cascade="all, delete-orphan"
    )
    updated_recruitment_processes = relationship(
        "RecruitmentProcess",
        foreign_keys="RecruitmentProcess.updated_by",
        back_populates="updater",
        cascade="all, delete-orphan"
    )
    candidate_processes = relationship(
        "CandidateProcess",
        foreign_keys="CandidateProcess.candidate_id",
        back_populates="candidate",
        cascade="all, delete-orphan"
    )
    assigned_candidate_processes = relationship(
        "CandidateProcess",
        foreign_keys="CandidateProcess.assigned_recruiter_id",
        back_populates="assigned_recruiter",
        cascade="all, delete-orphan"
    )
    assigned_node_executions = relationship(
        "NodeExecution",
        foreign_keys="NodeExecution.assigned_to",
        back_populates="assignee",
        cascade="all, delete-orphan"
    )
    completed_node_executions = relationship(
        "NodeExecution",
        foreign_keys="NodeExecution.completed_by",
        back_populates="completer",
        cascade="all, delete-orphan"
    )
    reviewed_node_executions = relationship(
        "NodeExecution",
        foreign_keys="NodeExecution.reviewed_by",
        back_populates="reviewer",
        cascade="all, delete-orphan"
    )
    process_viewers = relationship(
        "ProcessViewer",
        foreign_keys="ProcessViewer.user_id",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    added_process_viewers = relationship(
        "ProcessViewer",
        foreign_keys="ProcessViewer.added_by",
        back_populates="added_by_user",
        cascade="all, delete-orphan"
    )
    created_process_nodes = relationship(
        "ProcessNode",
        foreign_keys="ProcessNode.created_by",
        back_populates="creator",
        cascade="all, delete-orphan"
    )
    updated_process_nodes = relationship(
        "ProcessNode",
        foreign_keys="ProcessNode.updated_by",
        back_populates="updater",
        cascade="all, delete-orphan"
    )

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def __repr__(self):
        return (
            f"<User(id={self.id}, email='{self.email}', company_id={self.company_id})>"
        )
