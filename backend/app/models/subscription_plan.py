from decimal import Decimal

from sqlalchemy import Boolean, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel


class SubscriptionPlan(BaseModel):
    """
    Subscription plans (Basic, Premium, etc.).
    Features are managed dynamically via PlanFeature junction table.
    """

    __tablename__ = "subscription_plans"

    # Plan identification
    name: Mapped[str] = mapped_column(
        String(50), nullable=False, unique=True, index=True
    )  # 'basic', 'premium'
    display_name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Pricing
    price_monthly: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    price_yearly: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    currency: Mapped[str] = mapped_column(
        String(3), nullable=False, default="JPY"
    )  # ISO 4217 currency code

    # Limits (optional)
    max_users: Mapped[int | None] = mapped_column(Integer, nullable=True)
    max_exams: Mapped[int | None] = mapped_column(Integer, nullable=True)
    max_workflows: Mapped[int | None] = mapped_column(Integer, nullable=True)
    max_storage_gb: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Plan status
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, index=True)
    is_public: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True
    )  # Show in public pricing page

    # Display order
    display_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # Relationships
    plan_features = relationship(
        "PlanFeature", back_populates="plan", cascade="all, delete-orphan"
    )
    subscriptions = relationship(
        "CompanySubscription", back_populates="plan", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<SubscriptionPlan(id={self.id}, name='{self.name}', price_monthly={self.price_monthly})>"
