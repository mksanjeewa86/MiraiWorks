from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class User(BaseModel):
    __tablename__ = "users"
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
    created_by = Column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )  # ID of user who created this user (NULL for self-registration)
    # Logical deletion fields
    is_deleted = Column(Boolean, nullable=False, default=False, index=True)
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    deleted_by = Column(Integer, nullable=True)  # ID of user who deleted this user
    # Suspension fields
    is_suspended = Column(Boolean, nullable=False, default=False, index=True)
    suspended_at = Column(DateTime(timezone=True), nullable=True)
    suspended_by = Column(Integer, nullable=True)  # ID of user who suspended this user

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
    meeting_participations = relationship(
        "MeetingParticipant", back_populates="user", cascade="all, delete-orphan"
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
        cascade="all, delete-orphan",
    )
    extension_requests_to_review = relationship(
        "TodoExtensionRequest",
        foreign_keys="TodoExtensionRequest.creator_id",
        back_populates="creator",
        cascade="all, delete-orphan",
    )
    extension_responses = relationship(
        "TodoExtensionRequest",
        foreign_keys="TodoExtensionRequest.responded_by_id",
        back_populates="responded_by",
        cascade="all, delete-orphan",
    )
    mbti_test = relationship(
        "MBTITest", back_populates="user", cascade="all, delete-orphan", uselist=False
    )

    # User connections
    sent_connections = relationship(
        "UserConnection",
        foreign_keys="UserConnection.user_id",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    received_connections = relationship(
        "UserConnection",
        foreign_keys="UserConnection.connected_user_id",
        back_populates="connected_user",
        cascade="all, delete-orphan",
    )

    # Connection invitations
    sent_invitations = relationship(
        "ConnectionInvitation",
        foreign_keys="ConnectionInvitation.sender_id",
        back_populates="sender",
        cascade="all, delete-orphan",
    )
    received_invitations = relationship(
        "ConnectionInvitation",
        foreign_keys="ConnectionInvitation.receiver_id",
        back_populates="receiver",
        cascade="all, delete-orphan",
    )

    # Company connections (new system)
    company_connections_as_user = relationship(
        "CompanyConnection",
        foreign_keys="CompanyConnection.source_user_id",
        back_populates="source_user",
        cascade="all, delete-orphan",
    )

    # Note: created_by column exists above, but no relationship is defined
    # to avoid circular reference issues with self-referential User relationships
    # If needed, query User.created_by directly to get the creator's ID

    # Workflow relationships
    created_workflows = relationship(
        "Workflow",
        foreign_keys="Workflow.created_by",
        back_populates="creator",
        cascade="all, delete-orphan",
    )
    updated_workflows = relationship(
        "Workflow",
        foreign_keys="Workflow.updated_by",
        back_populates="updater",
        cascade="all, delete-orphan",
    )
    candidate_workflows = relationship(
        "CandidateWorkflow",
        foreign_keys="CandidateWorkflow.candidate_id",
        back_populates="candidate",
        cascade="all, delete-orphan",
    )
    assigned_candidate_workflows = relationship(
        "CandidateWorkflow",
        foreign_keys="CandidateWorkflow.assigned_recruiter_id",
        back_populates="assigned_recruiter",
        cascade="all, delete-orphan",
    )
    assigned_node_executions = relationship(
        "WorkflowNodeExecution",
        foreign_keys="WorkflowNodeExecution.assigned_to",
        back_populates="assignee",
        cascade="all, delete-orphan",
    )
    completed_node_executions = relationship(
        "WorkflowNodeExecution",
        foreign_keys="WorkflowNodeExecution.completed_by",
        back_populates="completer",
        cascade="all, delete-orphan",
    )
    reviewed_node_executions = relationship(
        "WorkflowNodeExecution",
        foreign_keys="WorkflowNodeExecution.reviewed_by",
        back_populates="reviewer",
        cascade="all, delete-orphan",
    )
    workflow_viewers = relationship(
        "WorkflowViewer",
        foreign_keys="WorkflowViewer.user_id",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    added_workflow_viewers = relationship(
        "WorkflowViewer",
        foreign_keys="WorkflowViewer.added_by",
        back_populates="added_by_user",
        cascade="all, delete-orphan",
    )
    created_workflow_nodes = relationship(
        "WorkflowNode",
        foreign_keys="WorkflowNode.created_by",
        back_populates="creator",
        cascade="all, delete-orphan",
    )
    updated_workflow_nodes = relationship(
        "WorkflowNode",
        foreign_keys="WorkflowNode.updated_by",
        back_populates="updater",
        cascade="all, delete-orphan",
    )
    system_updates_created = relationship(
        "SystemUpdate",
        foreign_keys="SystemUpdate.created_by_id",
        back_populates="created_by",
        cascade="all, delete-orphan",
    )

    # Profile-related relationships
    work_experiences = relationship(
        "ProfileWorkExperience",
        back_populates="user",
        cascade="all, delete-orphan",
        order_by="ProfileWorkExperience.display_order",
    )
    educations = relationship(
        "ProfileEducation",
        back_populates="user",
        cascade="all, delete-orphan",
        order_by="ProfileEducation.display_order",
    )
    skills = relationship(
        "ProfileSkill",
        back_populates="user",
        cascade="all, delete-orphan",
        order_by="ProfileSkill.display_order",
    )
    certifications = relationship(
        "ProfileCertification",
        back_populates="user",
        cascade="all, delete-orphan",
        order_by="ProfileCertification.display_order",
    )
    projects = relationship(
        "ProfileProject",
        back_populates="user",
        cascade="all, delete-orphan",
        order_by="ProfileProject.display_order",
    )
    job_preference = relationship(
        "JobPreference",
        back_populates="user",
        cascade="all, delete-orphan",
        uselist=False,  # One-to-one relationship
    )
    recruiter_profile = relationship(
        "RecruiterProfile",
        back_populates="user",
        cascade="all, delete-orphan",
        uselist=False,  # One-to-one relationship
    )
    privacy_settings = relationship(
        "PrivacySettings",
        back_populates="user",
        cascade="all, delete-orphan",
        uselist=False,  # One-to-one relationship
    )

    # Profile view tracking
    profile_views_received = relationship(
        "ProfileView",
        foreign_keys="ProfileView.profile_user_id",
        back_populates="profile_user",
        cascade="all, delete-orphan",
    )
    profile_views_made = relationship(
        "ProfileView",
        foreign_keys="ProfileView.viewer_user_id",
        back_populates="viewer_user",
        cascade="all, delete-orphan",
    )

    # Blocked companies relationship
    blocked_companies = relationship(
        "BlockedCompany",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def __repr__(self):
        return (
            f"<User(id={self.id}, email='{self.email}', company_id={self.company_id})>"
        )
