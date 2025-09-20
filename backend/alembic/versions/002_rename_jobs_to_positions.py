"""Rename jobs tables to positions

Revision ID: 002_rename_jobs_to_positions
Revises: c5a8b9e7f3d1, add_file_attachments, create_todos_table
Create Date: 2024-09-20 20:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '002_rename_jobs_to_positions'
down_revision: Union[str, None] = 'c5a8b9e7f3d1'  # Use the latest stable revision
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade: Rename jobs tables to positions tables"""

    # Step 1: Rename tables
    op.rename_table('jobs', 'positions')
    op.rename_table('job_applications', 'position_applications')

    # Step 2: Update foreign key column name in position_applications table
    # Drop the old foreign key constraint first
    op.drop_constraint('position_applications_ibfk_1', 'position_applications', type_='foreignkey')

    # Rename the column
    op.alter_column('position_applications', 'job_id', new_column_name='position_id')

    # Recreate the foreign key constraint with new names
    op.create_foreign_key(
        'position_applications_ibfk_1',  # constraint name
        'position_applications',         # source table
        'positions',                     # target table
        ['position_id'],                 # source columns
        ['id'],                          # target columns
        ondelete='CASCADE'
    )

    # Step 3: Update indexes with new table and column names

    # Drop old indexes
    op.drop_index('idx_jobs_company_status', table_name='positions')
    op.drop_index('idx_jobs_published', table_name='positions')
    op.drop_index('idx_jobs_location_type', table_name='positions')
    op.drop_index('idx_jobs_experience_remote', table_name='positions')
    op.drop_index('idx_jobs_featured_status', table_name='positions')

    # Create new indexes with updated names
    op.create_index('idx_positions_company_status', 'positions', ['company_id', 'status'])
    op.create_index('idx_positions_published', 'positions', ['published_at', 'status'])
    op.create_index('idx_positions_location_type', 'positions', ['country', 'city', 'job_type'])
    op.create_index('idx_positions_experience_remote', 'positions', ['experience_level', 'remote_type'])
    op.create_index('idx_positions_featured_status', 'positions', ['is_featured', 'status', 'published_at'])

    # Update position_applications indexes
    op.drop_index('idx_applications_job_status', table_name='position_applications')
    op.drop_index('idx_applications_candidate', table_name='position_applications')
    op.drop_index('idx_applications_status_date', table_name='position_applications')

    # Create new indexes for position_applications
    op.create_index('idx_applications_position_status', 'position_applications', ['position_id', 'status'])
    op.create_index('idx_applications_candidate', 'position_applications', ['candidate_id', 'applied_at'])
    op.create_index('idx_applications_status_date', 'position_applications', ['status', 'status_updated_at'])


def downgrade() -> None:
    """Downgrade: Revert positions tables back to jobs tables"""

    # Step 1: Update indexes back to original names

    # Drop new indexes
    op.drop_index('idx_positions_company_status', table_name='positions')
    op.drop_index('idx_positions_published', table_name='positions')
    op.drop_index('idx_positions_location_type', table_name='positions')
    op.drop_index('idx_positions_experience_remote', table_name='positions')
    op.drop_index('idx_positions_featured_status', table_name='positions')

    # Drop position_applications indexes
    op.drop_index('idx_applications_position_status', table_name='position_applications')
    op.drop_index('idx_applications_candidate', table_name='position_applications')
    op.drop_index('idx_applications_status_date', table_name='position_applications')

    # Step 2: Revert foreign key and column name

    # Drop the foreign key constraint
    op.drop_constraint('position_applications_ibfk_1', 'position_applications', type_='foreignkey')

    # Rename column back
    op.alter_column('position_applications', 'position_id', new_column_name='job_id')

    # Recreate original foreign key constraint
    op.create_foreign_key(
        'position_applications_ibfk_1',  # constraint name (will be renamed when table is renamed)
        'position_applications',         # source table (will be renamed)
        'positions',                     # target table (will be renamed)
        ['job_id'],                      # source columns
        ['id'],                          # target columns
        ondelete='CASCADE'
    )

    # Step 3: Rename tables back to original names
    op.rename_table('positions', 'jobs')
    op.rename_table('position_applications', 'job_applications')

    # Step 4: Recreate original indexes
    op.create_index('idx_jobs_company_status', 'jobs', ['company_id', 'status'])
    op.create_index('idx_jobs_published', 'jobs', ['published_at', 'status'])
    op.create_index('idx_jobs_location_type', 'jobs', ['country', 'city', 'job_type'])
    op.create_index('idx_jobs_experience_remote', 'jobs', ['experience_level', 'remote_type'])
    op.create_index('idx_jobs_featured_status', 'jobs', ['is_featured', 'status', 'published_at'])

    # Recreate job_applications indexes
    op.create_index('idx_applications_job_status', 'job_applications', ['job_id', 'status'])
    op.create_index('idx_applications_candidate', 'job_applications', ['candidate_id', 'applied_at'])
    op.create_index('idx_applications_status_date', 'job_applications', ['status', 'status_updated_at'])