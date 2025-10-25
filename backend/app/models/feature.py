from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class Feature(BaseModel):
    """
    Feature catalog for subscription plans.
    Supports hierarchical features with parent-child relationships.

    Examples:
    - Main Feature: "user_management" (parent_feature_id = NULL)
      - Sub-feature: "deactivate_user" (parent_feature_id = user_management.id)
      - Sub-feature: "suspend_user" (parent_feature_id = user_management.id)
    """

    __tablename__ = "features"

    # Feature identification
    name = Column(String(50), nullable=False, unique=True, index=True)
    display_name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)

    # Hierarchical support
    parent_feature_id = Column(
        Integer, ForeignKey("features.id"), nullable=True, index=True
    )
    permission_key = Column(
        String(100), nullable=True, index=True
    )  # e.g., 'user_management.deactivate'

    # Feature categorization
    category = Column(
        String(50), nullable=True, index=True
    )  # 'core', 'premium', 'integrations'

    # Status
    is_active = Column(Boolean, nullable=False, default=True, index=True)

    # Relationships
    parent = relationship(
        "Feature",
        remote_side="features.c.id",
        back_populates="children",
        foreign_keys=[parent_feature_id],
    )
    children = relationship(
        "Feature",
        back_populates="parent",
        cascade="all, delete-orphan",
        foreign_keys=[parent_feature_id],
    )
    plan_features = relationship(
        "PlanFeature", back_populates="feature", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Feature(id={self.id}, name='{self.name}', permission_key='{self.permission_key}')>"
