from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class CompanySubscription(Base):
    """
    Company subscription to a plan.
    One company can only have one active subscription at a time.
    """
    __tablename__ = "company_subscriptions"

    id = Column(Integer, primary_key=True, index=True)

    # Foreign keys
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, unique=True, index=True)
    plan_id = Column(Integer, ForeignKey("subscription_plans.id"), nullable=False, index=True)

    # Subscription status
    is_active = Column(Boolean, nullable=False, default=True, index=True)
    is_trial = Column(Boolean, nullable=False, default=False)

    # Subscription period
    start_date = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    end_date = Column(DateTime(timezone=True), nullable=True)  # NULL = no expiration
    trial_end_date = Column(DateTime(timezone=True), nullable=True)

    # Billing
    billing_cycle = Column(String(20), nullable=False, default='monthly')  # 'monthly', 'yearly'
    next_billing_date = Column(DateTime(timezone=True), nullable=True)
    auto_renew = Column(Boolean, nullable=False, default=True)

    # Cancellation
    cancelled_at = Column(DateTime(timezone=True), nullable=True)
    cancellation_reason = Column(String(255), nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Relationships
    company = relationship("Company", backref="subscription")
    plan = relationship("SubscriptionPlan", back_populates="subscriptions")

    def __repr__(self):
        return f"<CompanySubscription(id={self.id}, company_id={self.company_id}, plan_id={self.plan_id}, is_active={self.is_active})>"
