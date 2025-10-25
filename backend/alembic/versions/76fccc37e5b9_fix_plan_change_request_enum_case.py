"""fix_plan_change_request_enum_case

Revision ID: 76fccc37e5b9
Revises: 5e7a1b8c9d3f
Create Date: 2025-10-16 15:53:10.474369

"""
from collections.abc import Sequence
from typing import Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "76fccc37e5b9"
down_revision: Union[str, None] = "5e7a1b8c9d3f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Fix the enum case mismatch in plan_change_requests table.

    The MySQL enum was defined with uppercase values ('UPGRADE', 'DOWNGRADE')
    but the Python enum expects lowercase values ('upgrade', 'downgrade').

    This migration:
    1. Changes the column to VARCHAR temporarily
    2. Updates all existing data to lowercase
    3. Recreates the enum with lowercase values
    """
    # Step 1: Change column to VARCHAR to allow updates
    op.execute(
        "ALTER TABLE plan_change_requests MODIFY COLUMN request_type VARCHAR(20) NOT NULL"
    )

    # Step 2: Update existing data to lowercase
    op.execute("UPDATE plan_change_requests SET request_type = LOWER(request_type)")

    # Step 3: Recreate the enum with lowercase values
    op.execute(
        "ALTER TABLE plan_change_requests MODIFY COLUMN request_type ENUM('upgrade', 'downgrade') NOT NULL"
    )


def downgrade() -> None:
    """
    Revert to uppercase enum values.
    """
    # Change to VARCHAR
    op.execute(
        "ALTER TABLE plan_change_requests MODIFY COLUMN request_type VARCHAR(20) NOT NULL"
    )

    # Update data to uppercase
    op.execute("UPDATE plan_change_requests SET request_type = UPPER(request_type)")

    # Recreate enum with uppercase values
    op.execute(
        "ALTER TABLE plan_change_requests MODIFY COLUMN request_type ENUM('UPGRADE', 'DOWNGRADE') NOT NULL"
    )
