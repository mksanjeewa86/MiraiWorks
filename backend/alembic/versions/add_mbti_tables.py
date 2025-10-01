"""add mbti tables

Revision ID: add_mbti_tables
Revises: create_todos_table
Create Date: 2025-09-22 00:00:00.000000

"""
import sqlalchemy as sa
from sqlalchemy.sql import func

from alembic import op

# revision identifiers, used by Alembic.
revision = "add_mbti_tables"
down_revision = "create_todos_table"
branch_labels = None
depends_on = None


def upgrade():
    # Create mbti_questions table
    op.create_table(
        "mbti_questions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("question_number", sa.Integer(), nullable=False),
        sa.Column("dimension", sa.String(length=3), nullable=False),
        sa.Column("question_text_en", sa.Text(), nullable=False),
        sa.Column("question_text_ja", sa.Text(), nullable=False),
        sa.Column("option_a_en", sa.String(length=500), nullable=False),
        sa.Column("option_a_ja", sa.String(length=500), nullable=False),
        sa.Column("option_b_en", sa.String(length=500), nullable=False),
        sa.Column("option_b_ja", sa.String(length=500), nullable=False),
        sa.Column("scoring_key", sa.String(length=1), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=func.now(),
            onupdate=func.now(),
        ),
    )

    # Create indexes for mbti_questions
    op.create_index("ix_mbti_questions_dimension", "mbti_questions", ["dimension"])
    op.create_index("ix_mbti_questions_number", "mbti_questions", ["question_number"])
    op.create_index("ix_mbti_questions_active", "mbti_questions", ["is_active"])

    # Create mbti_tests table
    op.create_table(
        "mbti_tests",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "user_id",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "status",
            sa.String(length=20),
            nullable=False,
            server_default="not_taken",
        ),
        sa.Column("language", sa.String(length=2), nullable=False, server_default="ja"),
        sa.Column("mbti_type", sa.String(length=4), nullable=True),
        sa.Column("extraversion_introversion_score", sa.Integer(), nullable=True),
        sa.Column("sensing_intuition_score", sa.Integer(), nullable=True),
        sa.Column("thinking_feeling_score", sa.Integer(), nullable=True),
        sa.Column("judging_perceiving_score", sa.Integer(), nullable=True),
        sa.Column("answers", sa.JSON(), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=func.now(),
            onupdate=func.now(),
        ),
    )

    # Create indexes for mbti_tests
    op.create_index("ix_mbti_tests_user", "mbti_tests", ["user_id"])
    op.create_index("ix_mbti_tests_status", "mbti_tests", ["status"])
    op.create_index("ix_mbti_tests_type", "mbti_tests", ["mbti_type"])
    op.create_index("ix_mbti_tests_user_status", "mbti_tests", ["user_id", "status"])

    # Add unique constraint for one active test per user
    op.create_index(
        "ix_mbti_tests_user_unique_active",
        "mbti_tests",
        ["user_id"],
        unique=True,
        postgresql_where=sa.text("status IN ('not_taken', 'in_progress')")
    )


def downgrade():
    # Drop mbti_tests table
    op.drop_index("ix_mbti_tests_user_unique_active", table_name="mbti_tests")
    op.drop_index("ix_mbti_tests_user_status", table_name="mbti_tests")
    op.drop_index("ix_mbti_tests_type", table_name="mbti_tests")
    op.drop_index("ix_mbti_tests_status", table_name="mbti_tests")
    op.drop_index("ix_mbti_tests_user", table_name="mbti_tests")
    op.drop_table("mbti_tests")

    # Drop mbti_questions table
    op.drop_index("ix_mbti_questions_active", table_name="mbti_questions")
    op.drop_index("ix_mbti_questions_number", table_name="mbti_questions")
    op.drop_index("ix_mbti_questions_dimension", table_name="mbti_questions")
    op.drop_table("mbti_questions")
