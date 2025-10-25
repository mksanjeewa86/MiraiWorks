from sqlalchemy import Column, DateTime, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class PlanFeature(Base):
    """
    Junction table linking subscription plans to features.
    Enables dynamic feature assignment to plans.

    When a feature is added to a plan, all companies subscribed to that plan
    immediately get access to that feature.
    """

    __tablename__ = "plan_features"
    __table_args__ = (
        UniqueConstraint("plan_id", "feature_id", name="uq_plan_feature"),
    )

    id = Column(Integer, primary_key=True, index=True)

    # Foreign keys
    plan_id = Column(
        Integer, ForeignKey("subscription_plans.id"), nullable=False, index=True
    )
    feature_id = Column(Integer, ForeignKey("features.id"), nullable=False, index=True)

    # Audit trail
    added_by = Column(
        Integer, ForeignKey("users.id"), nullable=True
    )  # System admin who added this feature

    # Timestamps
    added_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationships
    plan = relationship("SubscriptionPlan", back_populates="plan_features")
    feature = relationship("Feature", back_populates="plan_features")
    added_by_user = relationship("User", foreign_keys=[added_by])

    def __repr__(self):
        return f"<PlanFeature(plan_id={self.plan_id}, feature_id={self.feature_id})>"
