"""add_missing_exam_workflow_columns

Revision ID: 504e237d4188
Revises: 7b40e9699400
Create Date: 2025-10-05 14:59:10.753239

"""
from collections.abc import Sequence
from typing import Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "504e237d4188"
down_revision: Union[str, None] = "7b40e9699400"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Fix question_banks table - rename created_by to created_by_id
    op.alter_column(
        "question_banks",
        "created_by",
        new_column_name="created_by_id",
        existing_type=sa.Integer(),
        existing_nullable=True,
    )

    # Add source tracking columns to exam_questions
    op.add_column(
        "exam_questions",
        sa.Column(
            "source_type", sa.String(length=20), nullable=False, server_default="custom"
        ),
    )
    op.add_column(
        "exam_questions", sa.Column("source_bank_id", sa.Integer(), nullable=True)
    )
    op.add_column(
        "exam_questions", sa.Column("source_question_id", sa.Integer(), nullable=True)
    )

    # Create foreign keys for source tracking
    op.create_foreign_key(
        "fk_exam_questions_source_bank",
        "exam_questions",
        "question_banks",
        ["source_bank_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_foreign_key(
        "fk_exam_questions_source_question",
        "exam_questions",
        "question_bank_items",
        ["source_question_id"],
        ["id"],
        ondelete="SET NULL",
    )

    # Create indexes
    op.create_index("ix_exam_questions_source_type", "exam_questions", ["source_type"])
    op.create_index(
        "ix_exam_questions_source_bank_id", "exam_questions", ["source_bank_id"]
    )

    # Add question_selection_rules to exams
    op.add_column(
        "exams", sa.Column("question_selection_rules", sa.JSON(), nullable=True)
    )

    # Add exam fields to todos
    op.add_column("todos", sa.Column("exam_id", sa.Integer(), nullable=True))
    op.add_column("todos", sa.Column("exam_assignment_id", sa.Integer(), nullable=True))
    op.add_column("todos", sa.Column("exam_config", sa.JSON(), nullable=True))

    # Create foreign keys for todos
    op.create_foreign_key(
        "fk_todos_exam", "todos", "exams", ["exam_id"], ["id"], ondelete="SET NULL"
    )
    op.create_foreign_key(
        "fk_todos_exam_assignment",
        "todos",
        "exam_assignments",
        ["exam_assignment_id"],
        ["id"],
        ondelete="SET NULL",
    )

    # Create indexes for todos
    op.create_index("ix_todos_exam_id", "todos", ["exam_id"])
    op.create_index("ix_todos_exam_assignment_id", "todos", ["exam_assignment_id"])

    # Add workflow fields to exam_assignments
    op.add_column("exam_assignments", sa.Column("todo_id", sa.Integer(), nullable=True))
    op.add_column(
        "exam_assignments",
        sa.Column("workflow_node_execution_id", sa.Integer(), nullable=True),
    )

    # Create foreign keys for exam_assignments
    op.create_foreign_key(
        "fk_exam_assignments_todo",
        "exam_assignments",
        "todos",
        ["todo_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_foreign_key(
        "fk_exam_assignments_workflow_execution",
        "exam_assignments",
        "workflow_node_executions",
        ["workflow_node_execution_id"],
        ["id"],
        ondelete="SET NULL",
    )

    # Create indexes for exam_assignments
    op.create_index("ix_exam_assignments_todo_id", "exam_assignments", ["todo_id"])
    op.create_index(
        "ix_exam_assignments_workflow_node_execution_id",
        "exam_assignments",
        ["workflow_node_execution_id"],
    )


def downgrade() -> None:
    # Drop indexes from exam_assignments
    op.drop_index("ix_exam_assignments_workflow_node_execution_id", "exam_assignments")
    op.drop_index("ix_exam_assignments_todo_id", "exam_assignments")

    # Drop foreign keys from exam_assignments
    op.drop_constraint(
        "fk_exam_assignments_workflow_execution", "exam_assignments", type_="foreignkey"
    )
    op.drop_constraint(
        "fk_exam_assignments_todo", "exam_assignments", type_="foreignkey"
    )

    # Drop columns from exam_assignments
    op.drop_column("exam_assignments", "workflow_node_execution_id")
    op.drop_column("exam_assignments", "todo_id")

    # Drop indexes from todos
    op.drop_index("ix_todos_exam_assignment_id", "todos")
    op.drop_index("ix_todos_exam_id", "todos")

    # Drop foreign keys from todos
    op.drop_constraint("fk_todos_exam_assignment", "todos", type_="foreignkey")
    op.drop_constraint("fk_todos_exam", "todos", type_="foreignkey")

    # Drop columns from todos
    op.drop_column("todos", "exam_config")
    op.drop_column("todos", "exam_assignment_id")
    op.drop_column("todos", "exam_id")

    # Drop question_selection_rules from exams
    op.drop_column("exams", "question_selection_rules")

    # Drop indexes from exam_questions
    op.drop_index("ix_exam_questions_source_bank_id", "exam_questions")
    op.drop_index("ix_exam_questions_source_type", "exam_questions")

    # Drop foreign keys from exam_questions
    op.drop_constraint(
        "fk_exam_questions_source_question", "exam_questions", type_="foreignkey"
    )
    op.drop_constraint(
        "fk_exam_questions_source_bank", "exam_questions", type_="foreignkey"
    )

    # Drop columns from exam_questions
    op.drop_column("exam_questions", "source_question_id")
    op.drop_column("exam_questions", "source_bank_id")
    op.drop_column("exam_questions", "source_type")

    # Revert question_banks column name
    op.alter_column(
        "question_banks",
        "created_by_id",
        new_column_name="created_by",
        existing_type=sa.Integer(),
        existing_nullable=True,
    )
