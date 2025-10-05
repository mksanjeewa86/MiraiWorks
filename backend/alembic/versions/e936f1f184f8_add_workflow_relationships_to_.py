"""add_workflow_relationships_to_interviews_and_todos

Revision ID: e936f1f184f8
Revises: 3caefaa119d8
Create Date: 2025-10-01 23:57:03.405120

"""
from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "e936f1f184f8"
down_revision: Union[str, None] = "3caefaa119d8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add workflow_id column to interviews table
    op.add_column("interviews", sa.Column("workflow_id", sa.Integer(), nullable=True))
    op.create_index("ix_interviews_workflow_id", "interviews", ["workflow_id"])
    op.create_foreign_key(
        "fk_interviews_workflow_id",
        "interviews",
        "workflows",
        ["workflow_id"],
        ["id"],
        ondelete="SET NULL",
    )

    # Add workflow_id column to todos table
    op.add_column("todos", sa.Column("workflow_id", sa.Integer(), nullable=True))
    op.create_index("ix_todos_workflow_id", "todos", ["workflow_id"])
    op.create_foreign_key(
        "fk_todos_workflow_id",
        "todos",
        "workflows",
        ["workflow_id"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    # Remove workflow_id from todos table
    op.drop_constraint("fk_todos_workflow_id", "todos", type_="foreignkey")
    op.drop_index("ix_todos_workflow_id", "todos")
    op.drop_column("todos", "workflow_id")

    # Remove workflow_id from interviews table
    op.drop_constraint("fk_interviews_workflow_id", "interviews", type_="foreignkey")
    op.drop_index("ix_interviews_workflow_id", "interviews")
    op.drop_column("interviews", "workflow_id")
