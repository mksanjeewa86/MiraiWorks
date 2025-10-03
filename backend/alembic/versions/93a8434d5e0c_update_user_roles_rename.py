"""update_user_roles_rename

Revision ID: 93a8434d5e0c
Revises: e936f1f184f8
Create Date: 2025-10-03 22:39:40.591095

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '93a8434d5e0c'
down_revision: Union[str, None] = 'e936f1f184f8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Update role names to new structure:
    - super_admin -> system_admin
    - company_admin -> admin
    - recruiter/employer -> member (based on company type)
    """
    # Update roles table - rename roles
    op.execute("""
        UPDATE roles
        SET name = 'system_admin',
            description = 'System-level administrator'
        WHERE name = 'super_admin'
    """)

    op.execute("""
        UPDATE roles
        SET name = 'admin',
            description = 'Company administrator (context: company type)'
        WHERE name = 'company_admin'
    """)

    # Merge recruiter and employer roles into member
    # First, update recruiter to member
    op.execute("""
        UPDATE roles
        SET name = 'member',
            description = 'Company member (context: company type)'
        WHERE name = 'recruiter'
    """)

    # Then, update user_roles that had employer role to use the member role
    op.execute("""
        UPDATE user_roles ur
        SET role_id = (SELECT id FROM roles WHERE name = 'member')
        WHERE role_id = (SELECT id FROM roles WHERE name = 'employer')
    """)

    # Delete the employer role
    op.execute("""
        DELETE FROM roles WHERE name = 'employer'
    """)


def downgrade() -> None:
    """
    Revert role names to old structure:
    - system_admin -> super_admin
    - admin -> company_admin
    - member -> recruiter (note: cannot perfectly restore recruiter/employer split)
    """
    # Revert system_admin to super_admin
    op.execute("""
        UPDATE roles
        SET name = 'super_admin',
            description = 'Super administrator'
        WHERE name = 'system_admin'
    """)

    # Revert admin to company_admin
    op.execute("""
        UPDATE roles
        SET name = 'company_admin',
            description = 'Company administrator'
        WHERE name = 'admin'
    """)

    # Revert member to recruiter (note: we cannot restore the employer/recruiter split without additional data)
    op.execute("""
        UPDATE roles
        SET name = 'recruiter',
            description = 'Recruiter'
        WHERE name = 'member'
    """)

    # Recreate employer role
    op.execute("""
        INSERT INTO roles (name, description)
        VALUES ('employer', 'Employer')
    """)