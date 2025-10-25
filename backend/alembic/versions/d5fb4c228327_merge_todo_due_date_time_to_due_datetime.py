"""merge_todo_due_date_time_to_due_datetime

Revision ID: d5fb4c228327
Revises: e8b5e6296ba3
Create Date: 2025-10-18 16:47:14.048242

"""
from collections.abc import Sequence
from typing import Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "d5fb4c228327"
down_revision: Union[str, None] = "e8b5e6296ba3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Check if due_datetime column exists from previous failed attempt
    from sqlalchemy import inspect

    bind = op.get_bind()
    inspector = inspect(bind)
    columns = [col["name"] for col in inspector.get_columns("todos")]

    # Check what columns exist
    has_due_date = "due_date" in columns
    has_due_time = "due_time" in columns
    has_due_datetime = "due_datetime" in columns

    print(
        f"Current state: due_date={has_due_date}, due_time={has_due_time}, due_datetime={has_due_datetime}"
    )

    # Drop due_datetime column if it exists from a previous failed migration
    if has_due_datetime:
        print("Dropping existing due_datetime column from previous failed migration...")
        op.drop_column("todos", "due_datetime")
        has_due_datetime = False

    # Only proceed if we have the old columns
    if not has_due_date and not has_due_time:
        print("Migration already applied - old columns don't exist")
        return

    # Add new due_datetime column (timezone-aware)
    print("Adding due_datetime column...")
    op.add_column(
        "todos", sa.Column("due_datetime", sa.DateTime(timezone=True), nullable=True)
    )

    # Migrate data in smaller batches to avoid timeout
    # Using Python code instead of one big SQL UPDATE
    print("Migrating data...")
    connection = op.get_bind()

    # Get total count
    result = connection.execute(
        sa.text("SELECT COUNT(*) FROM todos WHERE due_date IS NOT NULL")
    )
    total = result.scalar() or 0
    print(f"Found {total} todos with due_date to migrate")

    if total > 0:
        # Migrate in batches
        batch_size = 100
        for offset in range(0, total, batch_size):
            print(f"Processing batch {offset}-{offset+batch_size}...")
            connection.execute(
                sa.text(
                    """
                UPDATE todos
                SET due_datetime = CASE
                    WHEN due_date IS NOT NULL AND due_time IS NOT NULL THEN
                        CAST(CONCAT(due_date, ' ', due_time) AS DATETIME)
                    WHEN due_date IS NOT NULL AND due_time IS NULL THEN
                        CAST(CONCAT(due_date, ' 23:59:59') AS DATETIME)
                    ELSE NULL
                END
                WHERE due_date IS NOT NULL
                LIMIT :batch_size
            """
                ),
                {"batch_size": batch_size},
            )
            connection.commit()

    print("Data migration complete")

    # Drop old columns
    if has_due_time:
        print("Dropping due_time column...")
        op.drop_column("todos", "due_time")

    if has_due_date:
        print("Dropping due_date column...")
        op.drop_column("todos", "due_date")

    print("Migration complete!")


def downgrade() -> None:
    # Add back the old columns
    op.add_column("todos", sa.Column("due_date", sa.Date(), nullable=True))
    op.add_column("todos", sa.Column("due_time", sa.Time(), nullable=True))

    # Migrate data back: split due_datetime into date and time
    # MySQL syntax: Use DATE() and TIME() functions
    op.execute(
        """
        UPDATE todos
        SET
            due_date = CASE
                WHEN due_datetime IS NOT NULL THEN DATE(due_datetime)
                ELSE NULL
            END,
            due_time = CASE
                WHEN due_datetime IS NOT NULL THEN TIME(due_datetime)
                ELSE NULL
            END
    """
    )

    # Drop new column
    op.drop_column("todos", "due_datetime")
