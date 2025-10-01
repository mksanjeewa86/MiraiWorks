"""Add connection invitations table

Revision ID: eb618b540b0d
Revises: 473c2bfd58b0
Create Date: 2025-09-27 23:41:08.786211

"""
from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = 'eb618b540b0d'
down_revision: str | None = '473c2bfd58b0'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Create connection_invitations table
    op.create_table(
        'connection_invitations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('sender_id', sa.Integer(), nullable=False),
        sa.Column('receiver_id', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('message', sa.Text(), nullable=True),
        sa.Column('sent_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('responded_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['receiver_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['sender_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('sender_id', 'receiver_id', name='unique_sender_receiver')
    )
    op.create_index(op.f('ix_connection_invitations_id'), 'connection_invitations', ['id'], unique=False)
    op.create_index(op.f('ix_connection_invitations_receiver_id'), 'connection_invitations', ['receiver_id'], unique=False)
    op.create_index(op.f('ix_connection_invitations_sender_id'), 'connection_invitations', ['sender_id'], unique=False)
    op.create_index(op.f('ix_connection_invitations_status'), 'connection_invitations', ['status'], unique=False)


def downgrade() -> None:
    # Drop connection_invitations table
    op.drop_index(op.f('ix_connection_invitations_status'), table_name='connection_invitations')
    op.drop_index(op.f('ix_connection_invitations_sender_id'), table_name='connection_invitations')
    op.drop_index(op.f('ix_connection_invitations_receiver_id'), table_name='connection_invitations')
    op.drop_index(op.f('ix_connection_invitations_id'), table_name='connection_invitations')
    op.drop_table('connection_invitations')
