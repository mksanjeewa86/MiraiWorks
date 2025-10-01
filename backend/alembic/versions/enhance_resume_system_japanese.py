"""Enhance resume system with Japanese formats and sharing features

Revision ID: enhance_resume_system_japanese
Revises: f1413e5cffd1
Create Date: 2024-12-19 12:00:00.000000

"""
import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = 'enhance_resume_system_japanese'
down_revision = 'f1413e5cffd1'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add new columns to resumes table
    op.add_column('resumes', sa.Column('resume_format', sa.Enum('RIREKISHO', 'SHOKUMU_KEIREKISHO', 'INTERNATIONAL', 'MODERN', 'CREATIVE', name='resumeformat'), nullable=True))
    op.add_column('resumes', sa.Column('resume_language', sa.Enum('JAPANESE', 'ENGLISH', 'BILINGUAL', name='resumelanguage'), nullable=True))
    op.add_column('resumes', sa.Column('furigana_name', sa.String(length=100), nullable=True))
    op.add_column('resumes', sa.Column('birth_date', sa.DateTime(), nullable=True))
    op.add_column('resumes', sa.Column('gender', sa.String(length=10), nullable=True))
    op.add_column('resumes', sa.Column('nationality', sa.String(length=50), nullable=True))
    op.add_column('resumes', sa.Column('marital_status', sa.String(length=20), nullable=True))
    op.add_column('resumes', sa.Column('emergency_contact', sa.JSON(), nullable=True))
    op.add_column('resumes', sa.Column('photo_path', sa.String(length=500), nullable=True))
    op.add_column('resumes', sa.Column('is_public', sa.Boolean(), nullable=True))
    op.add_column('resumes', sa.Column('public_url_slug', sa.String(length=100), nullable=True))
    op.add_column('resumes', sa.Column('can_download_pdf', sa.Boolean(), nullable=True))
    op.add_column('resumes', sa.Column('can_edit', sa.Boolean(), nullable=True))
    op.add_column('resumes', sa.Column('can_delete', sa.Boolean(), nullable=True))

    # Create indexes
    op.create_index(op.f('ix_resumes_public_url_slug'), 'resumes', ['public_url_slug'], unique=True)

    # Create resume_message_attachments table
    op.create_table('resume_message_attachments',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('resume_id', sa.Integer(), nullable=False),
        sa.Column('message_id', sa.Integer(), nullable=False),
        sa.Column('auto_attached', sa.Boolean(), nullable=True),
        sa.Column('attachment_format', sa.String(length=20), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['message_id'], ['messages.id'], ),
        sa.ForeignKeyConstraint(['resume_id'], ['resumes.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_resume_message_attachments_id'), 'resume_message_attachments', ['id'], unique=False)

    # Set default values for new columns
    op.execute("UPDATE resumes SET resume_format = 'INTERNATIONAL' WHERE resume_format IS NULL")
    op.execute("UPDATE resumes SET resume_language = 'ENGLISH' WHERE resume_language IS NULL")
    op.execute("UPDATE resumes SET is_public = false WHERE is_public IS NULL")
    op.execute("UPDATE resumes SET can_download_pdf = true WHERE can_download_pdf IS NULL")
    op.execute("UPDATE resumes SET can_edit = true WHERE can_edit IS NULL")
    op.execute("UPDATE resumes SET can_delete = true WHERE can_delete IS NULL")

    # Make columns non-nullable after setting defaults
    op.alter_column('resumes', 'resume_format', nullable=False)
    op.alter_column('resumes', 'resume_language', nullable=False)
    op.alter_column('resumes', 'is_public', nullable=False)
    op.alter_column('resumes', 'can_download_pdf', nullable=False)
    op.alter_column('resumes', 'can_edit', nullable=False)
    op.alter_column('resumes', 'can_delete', nullable=False)


def downgrade() -> None:
    # Drop resume_message_attachments table
    op.drop_index(op.f('ix_resume_message_attachments_id'), table_name='resume_message_attachments')
    op.drop_table('resume_message_attachments')

    # Drop indexes
    op.drop_index(op.f('ix_resumes_public_url_slug'), table_name='resumes')

    # Drop columns from resumes table
    op.drop_column('resumes', 'can_delete')
    op.drop_column('resumes', 'can_edit')
    op.drop_column('resumes', 'can_download_pdf')
    op.drop_column('resumes', 'public_url_slug')
    op.drop_column('resumes', 'is_public')
    op.drop_column('resumes', 'photo_path')
    op.drop_column('resumes', 'emergency_contact')
    op.drop_column('resumes', 'marital_status')
    op.drop_column('resumes', 'nationality')
    op.drop_column('resumes', 'gender')
    op.drop_column('resumes', 'birth_date')
    op.drop_column('resumes', 'furigana_name')
    op.drop_column('resumes', 'resume_language')
    op.drop_column('resumes', 'resume_format')

    # Drop enums
    op.execute('DROP TYPE IF EXISTS resumelanguage')
    op.execute('DROP TYPE IF EXISTS resumeformat')
