"""Add profile tables for work experience, education, skills, certifications, projects, and job preferences

Revision ID: 20251012_profile
Revises: 9a38cdd9c320
Create Date: 2025-10-12 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = '20251012_profile'
down_revision: Union[str, None] = '9a38cdd9c320'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create profile_work_experiences table
    op.create_table(
        'profile_work_experiences',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('company_name', sa.String(length=255), nullable=False),
        sa.Column('company_logo_url', sa.String(length=500), nullable=True),
        sa.Column('position_title', sa.String(length=255), nullable=False),
        sa.Column('employment_type', sa.String(length=50), nullable=True),
        sa.Column('location', sa.String(length=255), nullable=True),
        sa.Column('start_date', sa.Date(), nullable=False),
        sa.Column('end_date', sa.Date(), nullable=True),
        sa.Column('is_current', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('skills', sa.Text(), nullable=True),
        sa.Column('display_order', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_profile_work_experiences_id'), 'profile_work_experiences', ['id'], unique=False)
    op.create_index(op.f('ix_profile_work_experiences_user_id'), 'profile_work_experiences', ['user_id'], unique=False)

    # Create profile_educations table
    op.create_table(
        'profile_educations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('institution_name', sa.String(length=255), nullable=False),
        sa.Column('institution_logo_url', sa.String(length=500), nullable=True),
        sa.Column('degree_type', sa.String(length=100), nullable=False),
        sa.Column('field_of_study', sa.String(length=255), nullable=False),
        sa.Column('start_date', sa.Date(), nullable=True),
        sa.Column('end_date', sa.Date(), nullable=True),
        sa.Column('graduation_year', sa.Integer(), nullable=True),
        sa.Column('gpa', sa.Numeric(precision=3, scale=2), nullable=True),
        sa.Column('gpa_max', sa.Numeric(precision=3, scale=2), nullable=True),
        sa.Column('honors_awards', sa.Text(), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('display_order', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_profile_educations_id'), 'profile_educations', ['id'], unique=False)
    op.create_index(op.f('ix_profile_educations_user_id'), 'profile_educations', ['user_id'], unique=False)

    # Create profile_skills table
    op.create_table(
        'profile_skills',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('skill_name', sa.String(length=100), nullable=False),
        sa.Column('category', sa.String(length=50), nullable=True),
        sa.Column('proficiency_level', sa.String(length=50), nullable=True),
        sa.Column('years_of_experience', sa.Integer(), nullable=True),
        sa.Column('endorsement_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('display_order', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_profile_skills_id'), 'profile_skills', ['id'], unique=False)
    op.create_index(op.f('ix_profile_skills_user_id'), 'profile_skills', ['user_id'], unique=False)

    # Create profile_certifications table
    op.create_table(
        'profile_certifications',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('certification_name', sa.String(length=255), nullable=False),
        sa.Column('issuing_organization', sa.String(length=255), nullable=False),
        sa.Column('issue_date', sa.Date(), nullable=True),
        sa.Column('expiry_date', sa.Date(), nullable=True),
        sa.Column('does_not_expire', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('credential_id', sa.String(length=100), nullable=True),
        sa.Column('credential_url', sa.String(length=500), nullable=True),
        sa.Column('certificate_image_url', sa.String(length=500), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('display_order', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_profile_certifications_id'), 'profile_certifications', ['id'], unique=False)
    op.create_index(op.f('ix_profile_certifications_user_id'), 'profile_certifications', ['user_id'], unique=False)

    # Create profile_projects table
    op.create_table(
        'profile_projects',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('project_name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('role', sa.String(length=100), nullable=True),
        sa.Column('technologies', sa.Text(), nullable=True),
        sa.Column('project_url', sa.String(length=500), nullable=True),
        sa.Column('github_url', sa.String(length=500), nullable=True),
        sa.Column('image_urls', sa.Text(), nullable=True),
        sa.Column('start_date', sa.Date(), nullable=True),
        sa.Column('end_date', sa.Date(), nullable=True),
        sa.Column('display_order', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_profile_projects_id'), 'profile_projects', ['id'], unique=False)
    op.create_index(op.f('ix_profile_projects_user_id'), 'profile_projects', ['user_id'], unique=False)

    # Create profile_job_preferences table
    op.create_table(
        'profile_job_preferences',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('desired_job_types', sa.Text(), nullable=True),
        sa.Column('desired_salary_min', sa.Integer(), nullable=True),
        sa.Column('desired_salary_max', sa.Integer(), nullable=True),
        sa.Column('salary_currency', sa.String(length=10), nullable=False, server_default='USD'),
        sa.Column('salary_period', sa.String(length=20), nullable=False, server_default='yearly'),
        sa.Column('willing_to_relocate', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('preferred_locations', sa.Text(), nullable=True),
        sa.Column('work_mode_preferences', sa.Text(), nullable=True),
        sa.Column('available_from', sa.Date(), nullable=True),
        sa.Column('notice_period_days', sa.Integer(), nullable=True),
        sa.Column('job_search_status', sa.String(length=50), nullable=False, server_default='not_looking'),
        sa.Column('preferred_industries', sa.Text(), nullable=True),
        sa.Column('preferred_company_sizes', sa.Text(), nullable=True),
        sa.Column('other_preferences', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_profile_job_preferences_id'), 'profile_job_preferences', ['id'], unique=False)
    op.create_index(op.f('ix_profile_job_preferences_user_id'), 'profile_job_preferences', ['user_id'], unique=True)


def downgrade() -> None:
    # Drop profile_job_preferences table
    op.drop_index(op.f('ix_profile_job_preferences_user_id'), table_name='profile_job_preferences')
    op.drop_index(op.f('ix_profile_job_preferences_id'), table_name='profile_job_preferences')
    op.drop_table('profile_job_preferences')

    # Drop profile_projects table
    op.drop_index(op.f('ix_profile_projects_user_id'), table_name='profile_projects')
    op.drop_index(op.f('ix_profile_projects_id'), table_name='profile_projects')
    op.drop_table('profile_projects')

    # Drop profile_certifications table
    op.drop_index(op.f('ix_profile_certifications_user_id'), table_name='profile_certifications')
    op.drop_index(op.f('ix_profile_certifications_id'), table_name='profile_certifications')
    op.drop_table('profile_certifications')

    # Drop profile_skills table
    op.drop_index(op.f('ix_profile_skills_user_id'), table_name='profile_skills')
    op.drop_index(op.f('ix_profile_skills_id'), table_name='profile_skills')
    op.drop_table('profile_skills')

    # Drop profile_educations table
    op.drop_index(op.f('ix_profile_educations_user_id'), table_name='profile_educations')
    op.drop_index(op.f('ix_profile_educations_id'), table_name='profile_educations')
    op.drop_table('profile_educations')

    # Drop profile_work_experiences table
    op.drop_index(op.f('ix_profile_work_experiences_user_id'), table_name='profile_work_experiences')
    op.drop_index(op.f('ix_profile_work_experiences_id'), table_name='profile_work_experiences')
    op.drop_table('profile_work_experiences')
