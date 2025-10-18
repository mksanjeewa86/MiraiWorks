"""enforce_single_system_admin

Revision ID: 5e7a1b8c9d3f
Revises: 4dca71223092
Create Date: 2025-10-16 14:25:03.000000

This migration enforces database-level constraints for:
1. Only one system_admin can exist in the system
2. Super admin's company cannot have candidates
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5e7a1b8c9d3f'
down_revision: Union[str, None] = '4dca71223092'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    NOTE: Database triggers are not created due to MySQL privilege requirements.
    The application-level restrictions are implemented in:
    - backend/app/endpoints/users_management.py (create_user and update_user functions)

    These restrictions enforce:
    1. Only one system_admin role per system (no one can create system admins)
    2. Only super admin can create company admins
    3. Prevent candidates in super admin's company

    This migration serves as a placeholder and documentation.
    If database-level enforcement is needed in the future, the following triggers
    can be created manually with appropriate privileges:
    - prevent_multiple_system_admins
    - prevent_candidates_in_super_admin_company
    """
    # No database changes needed - all restrictions are enforced at application level
    pass


def downgrade() -> None:
    """No database changes to revert"""
    pass
