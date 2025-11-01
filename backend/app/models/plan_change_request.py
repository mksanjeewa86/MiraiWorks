from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, Text
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel
from app.utils.constants import PlanChangeRequestStatus, PlanChangeRequestType


class PlanChangeRequest(BaseModel):
    """
    Request for changing a company's subscription plan.
    Requires system admin approval.
    """

    __tablename__ = "plan_change_requests"

    # Foreign keys
    company_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("companies.id"), nullable=False, index=True
    )
    subscription_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("company_subscriptions.id"), nullable=False, index=True
    )
    current_plan_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("subscription_plans.id"), nullable=False
    )
    requested_plan_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("subscription_plans.id"), nullable=False
    )

    # Request details
    request_type: Mapped[PlanChangeRequestType] = mapped_column(
        SQLEnum(PlanChangeRequestType, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        index=True,
    )  # 'upgrade', 'downgrade'
    requested_by: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=False
    )  # Company admin user ID
    request_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Status and review
    status: Mapped[PlanChangeRequestStatus] = mapped_column(
        SQLEnum(
            PlanChangeRequestStatus, values_callable=lambda x: [e.value for e in x]
        ),
        nullable=False,
        default=PlanChangeRequestStatus.PENDING,
        index=True,
    )
    reviewed_by: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=True
    )  # System admin user ID
    review_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    reviewed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Relationships
    company = relationship("Company", foreign_keys=[company_id])
    subscription = relationship("CompanySubscription", foreign_keys=[subscription_id])
    current_plan = relationship("SubscriptionPlan", foreign_keys=[current_plan_id])
    requested_plan = relationship("SubscriptionPlan", foreign_keys=[requested_plan_id])
    requester = relationship("User", foreign_keys=[requested_by])
    reviewer = relationship("User", foreign_keys=[reviewed_by])

    def __repr__(self):
        return f"<PlanChangeRequest(id={self.id}, company_id={self.company_id}, request_type='{self.request_type}', status='{self.status}')>"
