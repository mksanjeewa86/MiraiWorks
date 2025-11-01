from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.models.base import BaseModel


class CompanySubscription(BaseModel):
    """
    Company subscription to a plan.
    One company can only have one active subscription at a time.
    """

    __tablename__ = "company_subscriptions"

    # Foreign keys
    company_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("companies.id"), nullable=False, unique=True, index=True
    )
    plan_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("subscription_plans.id"), nullable=False, index=True
    )

    # Subscription status
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, index=True)
    is_trial: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    # Subscription period
    start_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    end_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    trial_end_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Billing
    billing_cycle: Mapped[str] = mapped_column(
        String(20), nullable=False, default="monthly"
    )  # 'monthly', 'yearly'
    next_billing_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    auto_renew: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    # Cancellation
    cancelled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    cancellation_reason: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Relationships
    company = relationship("Company", backref="subscription")
    plan = relationship("SubscriptionPlan", back_populates="subscriptions")

    def __repr__(self):
        return f"<CompanySubscription(id={self.id}, company_id={self.company_id}, plan_id={self.plan_id}, is_active={self.is_active})>"
