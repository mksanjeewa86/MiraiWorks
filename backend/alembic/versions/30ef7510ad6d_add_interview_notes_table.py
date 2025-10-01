"""Add interview notes table

Revision ID: 30ef7510ad6d
Revises: 903e6731d7d2
Create Date: 2025-09-23 09:33:25.147122

"""
from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = '30ef7510ad6d'
down_revision: str | None = '903e6731d7d2'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Create interview_notes table
    op.create_table('interview_notes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('interview_id', sa.Integer(), nullable=False),
        sa.Column('participant_id', sa.Integer(), nullable=False),
        sa.Column('content', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['interview_id'], ['interviews.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['participant_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('interview_id', 'participant_id', name='uq_interview_participant_note')
    )
    op.create_index(op.f('ix_interview_notes_id'), 'interview_notes', ['id'], unique=False)
    op.create_index(op.f('ix_interview_notes_interview_id'), 'interview_notes', ['interview_id'], unique=False)
    op.create_index(op.f('ix_interview_notes_participant_id'), 'interview_notes', ['participant_id'], unique=False)


def downgrade() -> None:
    # Drop interview_notes table
    op.drop_index(op.f('ix_interview_notes_participant_id'), table_name='interview_notes')
    op.drop_index(op.f('ix_interview_notes_interview_id'), table_name='interview_notes')
    op.drop_index(op.f('ix_interview_notes_id'), table_name='interview_notes')
    op.drop_table('interview_notes')
