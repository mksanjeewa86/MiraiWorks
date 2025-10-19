"""separate_todo_due_date_time_and_standardize_priority

Revision ID: eeb10585ac49
Revises: 3048494cb683
Create Date: 2025-10-18 04:44:11.839221

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'eeb10585ac49'
down_revision: Union[str, None] = '3048494cb683'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add due_time column (optional time component, stored as TIME type)
    op.add_column('todos', sa.Column('due_time', sa.Time(), nullable=True))

    # Migrate existing data: Extract time from due_date if it exists
    # For existing records with due_date, extract the time component
    op.execute("""
        UPDATE todos
        SET due_time = TIME(due_date)
        WHERE due_date IS NOT NULL
        AND TIME(due_date) != '00:00:00'
    """)

    # Convert due_date to DATE only (remove time component)
    # This requires creating a new column, copying data, dropping old, renaming
    op.add_column('todos', sa.Column('due_date_temp', sa.Date(), nullable=True))
    op.execute("UPDATE todos SET due_date_temp = DATE(due_date) WHERE due_date IS NOT NULL")

    # Drop the old due_date column and rename the new one
    # MySQL requires specifying the type when using alter_column for rename
    op.drop_column('todos', 'due_date')
    op.alter_column('todos', 'due_date_temp',
                    new_column_name='due_date',
                    existing_type=sa.Date(),
                    existing_nullable=True)

    # Standardize priority values to enum (low, mid, high)
    # Convert any existing priority values to the new enum
    op.execute("""
        UPDATE todos
        SET priority = CASE
            WHEN LOWER(priority) IN ('low', 'l', '1', 'minor') THEN 'low'
            WHEN LOWER(priority) IN ('medium', 'mid', 'middle', 'm', '2', 'normal') THEN 'mid'
            WHEN LOWER(priority) IN ('high', 'h', '3', 'critical', 'urgent') THEN 'high'
            ELSE 'mid'
        END
        WHERE priority IS NOT NULL
    """)


def downgrade() -> None:
    # Combine due_date and due_time back into a single datetime column
    op.add_column('todos', sa.Column('due_date_temp', sa.DateTime(timezone=True), nullable=True))

    # Combine date and time if both exist, otherwise just use date
    op.execute("""
        UPDATE todos
        SET due_date_temp = CASE
            WHEN due_time IS NOT NULL THEN
                TIMESTAMP(due_date, due_time)
            WHEN due_date IS NOT NULL THEN
                TIMESTAMP(due_date, '00:00:00')
            ELSE NULL
        END
    """)

    # Drop the separate date and time columns
    op.drop_column('todos', 'due_date')
    op.drop_column('todos', 'due_time')

    # Rename temp column back to due_date
    op.alter_column('todos', 'due_date_temp', new_column_name='due_date')

    # Note: Priority downgrade is lossy - cannot perfectly reverse the standardization