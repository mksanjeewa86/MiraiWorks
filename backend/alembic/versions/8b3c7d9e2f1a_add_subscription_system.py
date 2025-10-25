"""Add subscription plan system with hierarchical features

Revision ID: 8b3c7d9e2f1a
Revises: 7aa585326f05
Create Date: 2025-10-05 18:00:00.000000

"""
from collections.abc import Sequence
from typing import Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "8b3c7d9e2f1a"
down_revision: Union[str, None] = "7aa585326f05"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create subscription_plans table
    op.create_table(
        "subscription_plans",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=50), nullable=False),
        sa.Column("display_name", sa.String(length=100), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("price_monthly", sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column("price_yearly", sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column(
            "currency", sa.String(length=3), nullable=False, server_default="JPY"
        ),
        sa.Column("max_users", sa.Integer(), nullable=True),
        sa.Column("max_exams", sa.Integer(), nullable=True),
        sa.Column("max_workflows", sa.Integer(), nullable=True),
        sa.Column("max_storage_gb", sa.Integer(), nullable=True),
        sa.Column(
            "is_active", sa.Boolean(), nullable=False, server_default=sa.text("1")
        ),
        sa.Column(
            "is_public", sa.Boolean(), nullable=False, server_default=sa.text("1")
        ),
        sa.Column(
            "display_order", sa.Integer(), nullable=False, server_default=sa.text("0")
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_subscription_plans_name"), "subscription_plans", ["name"], unique=True
    )
    op.create_index(
        op.f("ix_subscription_plans_is_active"),
        "subscription_plans",
        ["is_active"],
        unique=False,
    )

    # Create features table with hierarchical support
    op.create_table(
        "features",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=50), nullable=False),
        sa.Column("display_name", sa.String(length=100), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("parent_feature_id", sa.Integer(), nullable=True),
        sa.Column("permission_key", sa.String(length=100), nullable=True),
        sa.Column("category", sa.String(length=50), nullable=True),
        sa.Column(
            "is_active", sa.Boolean(), nullable=False, server_default=sa.text("1")
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["parent_feature_id"], ["features.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_features_name"), "features", ["name"], unique=True)
    op.create_index(
        op.f("ix_features_parent_feature_id"),
        "features",
        ["parent_feature_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_features_permission_key"), "features", ["permission_key"], unique=False
    )
    op.create_index(
        op.f("ix_features_category"), "features", ["category"], unique=False
    )
    op.create_index(
        op.f("ix_features_is_active"), "features", ["is_active"], unique=False
    )

    # Create plan_features junction table
    op.create_table(
        "plan_features",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("plan_id", sa.Integer(), nullable=False),
        sa.Column("feature_id", sa.Integer(), nullable=False),
        sa.Column("added_by", sa.Integer(), nullable=True),
        sa.Column(
            "added_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["plan_id"], ["subscription_plans.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(["feature_id"], ["features.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["added_by"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("plan_id", "feature_id", name="uq_plan_feature"),
    )
    op.create_index(
        op.f("ix_plan_features_plan_id"), "plan_features", ["plan_id"], unique=False
    )
    op.create_index(
        op.f("ix_plan_features_feature_id"),
        "plan_features",
        ["feature_id"],
        unique=False,
    )

    # Create company_subscriptions table
    op.create_table(
        "company_subscriptions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("company_id", sa.Integer(), nullable=False),
        sa.Column("plan_id", sa.Integer(), nullable=False),
        sa.Column(
            "is_active", sa.Boolean(), nullable=False, server_default=sa.text("1")
        ),
        sa.Column(
            "is_trial", sa.Boolean(), nullable=False, server_default=sa.text("0")
        ),
        sa.Column(
            "start_date",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column("end_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("trial_end_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "billing_cycle",
            sa.String(length=20),
            nullable=False,
            server_default="monthly",
        ),
        sa.Column("next_billing_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "auto_renew", sa.Boolean(), nullable=False, server_default=sa.text("1")
        ),
        sa.Column("cancelled_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("cancellation_reason", sa.String(length=255), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["company_id"], ["companies.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["plan_id"], ["subscription_plans.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_company_subscriptions_company_id"),
        "company_subscriptions",
        ["company_id"],
        unique=True,
    )
    op.create_index(
        op.f("ix_company_subscriptions_plan_id"),
        "company_subscriptions",
        ["plan_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_company_subscriptions_is_active"),
        "company_subscriptions",
        ["is_active"],
        unique=False,
    )

    # Create plan_change_requests table
    op.create_table(
        "plan_change_requests",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("company_id", sa.Integer(), nullable=False),
        sa.Column("subscription_id", sa.Integer(), nullable=False),
        sa.Column("current_plan_id", sa.Integer(), nullable=False),
        sa.Column("requested_plan_id", sa.Integer(), nullable=False),
        sa.Column("request_type", sa.String(length=20), nullable=False),
        sa.Column("requested_by", sa.Integer(), nullable=False),
        sa.Column("request_message", sa.Text(), nullable=True),
        sa.Column(
            "status", sa.String(length=20), nullable=False, server_default="pending"
        ),
        sa.Column("reviewed_by", sa.Integer(), nullable=True),
        sa.Column("review_message", sa.Text(), nullable=True),
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["company_id"], ["companies.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["subscription_id"], ["company_subscriptions.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(["current_plan_id"], ["subscription_plans.id"]),
        sa.ForeignKeyConstraint(["requested_plan_id"], ["subscription_plans.id"]),
        sa.ForeignKeyConstraint(["requested_by"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["reviewed_by"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_plan_change_requests_company_id"),
        "plan_change_requests",
        ["company_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_plan_change_requests_subscription_id"),
        "plan_change_requests",
        ["subscription_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_plan_change_requests_request_type"),
        "plan_change_requests",
        ["request_type"],
        unique=False,
    )
    op.create_index(
        op.f("ix_plan_change_requests_status"),
        "plan_change_requests",
        ["status"],
        unique=False,
    )


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_table("plan_change_requests")
    op.drop_table("company_subscriptions")
    op.drop_table("plan_features")
    op.drop_table("features")
    op.drop_table("subscription_plans")
