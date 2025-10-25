from sqlalchemy import Column, DateTime, ForeignKey, Integer, Text
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import relationship

from app.models.base import BaseModel
from app.utils.constants import PlanChangeRequestStatus, PlanChangeRequestType


class PlanChangeRequest(BaseModel):
    """
    Request for changing a company's subscription plan.
    Requires system admin approval.
    """

    __tablename__ = "plan_change_requests"

    # Foreign keys
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)
    subscription_id = Column(
        Integer, ForeignKey("company_subscriptions.id"), nullable=False, index=True
    )
    current_plan_id = Column(
        Integer, ForeignKey("subscription_plans.id"), nullable=False
    )
    requested_plan_id = Column(
        Integer, ForeignKey("subscription_plans.id"), nullable=False
    )

    # Request details
    request_type = Column(
        SQLEnum(PlanChangeRequestType, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        index=True,
    )  # 'upgrade', 'downgrade'
    requested_by = Column(
        Integer, ForeignKey("users.id"), nullable=False
    )  # Company admin user ID
    request_message = Column(Text, nullable=True)  # Message from company admin

    # Status and review
    status = Column(
        SQLEnum(
            PlanChangeRequestStatus, values_callable=lambda x: [e.value for e in x]
        ),
        nullable=False,
        default=PlanChangeRequestStatus.PENDING,
        index=True,
    )
    reviewed_by = Column(
        Integer, ForeignKey("users.id"), nullable=True
    )  # System admin user ID
    review_message = Column(Text, nullable=True)  # Response from system admin
    reviewed_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    company = relationship("Company", foreign_keys=[company_id])
    subscription = relationship("CompanySubscription", foreign_keys=[subscription_id])
    current_plan = relationship("SubscriptionPlan", foreign_keys=[current_plan_id])
    requested_plan = relationship("SubscriptionPlan", foreign_keys=[requested_plan_id])
    requester = relationship("User", foreign_keys=[requested_by])
    reviewer = relationship("User", foreign_keys=[reviewed_by])

    def __repr__(self):
        return f"<PlanChangeRequest(id={self.id}, company_id={self.company_id}, request_type='{self.request_type}', status='{self.status}')>"
