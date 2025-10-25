from sqlalchemy import Boolean, Column, Integer, Numeric, String, Text
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class SubscriptionPlan(BaseModel):
    """
    Subscription plans (Basic, Premium, etc.).
    Features are managed dynamically via PlanFeature junction table.
    """

    __tablename__ = "subscription_plans"

    # Plan identification
    name = Column(
        String(50), nullable=False, unique=True, index=True
    )  # 'basic', 'premium'
    display_name = Column(String(100), nullable=False)  # 'Basic Plan', 'Premium Plan'
    description = Column(Text, nullable=True)

    # Pricing
    price_monthly = Column(Numeric(10, 2), nullable=False)
    price_yearly = Column(Numeric(10, 2), nullable=True)
    currency = Column(
        String(3), nullable=False, default="JPY"
    )  # ISO 4217 currency code

    # Limits (optional)
    max_users = Column(Integer, nullable=True)
    max_exams = Column(Integer, nullable=True)
    max_workflows = Column(Integer, nullable=True)
    max_storage_gb = Column(Integer, nullable=True)

    # Plan status
    is_active = Column(Boolean, nullable=False, default=True, index=True)
    is_public = Column(
        Boolean, nullable=False, default=True
    )  # Show in public pricing page

    # Display order
    display_order = Column(Integer, nullable=False, default=0)

    # Relationships
    plan_features = relationship(
        "PlanFeature", back_populates="plan", cascade="all, delete-orphan"
    )
    subscriptions = relationship(
        "CompanySubscription", back_populates="plan", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<SubscriptionPlan(id={self.id}, name='{self.name}', price_monthly={self.price_monthly})>"
