"""Update company address fields

Revision ID: c5a8b9e7f3d1
Revises: 95de50a27612
Create Date: 2025-01-20 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c5a8b9e7f3d1'
down_revision: Union[str, None] = '95de50a27612'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Check if domain column exists before dropping it
    connection = op.get_bind()
    inspector = sa.inspect(connection)
    columns = [col['name'] for col in inspector.get_columns('companies')]
    
    if 'domain' in columns:
        op.drop_column('companies', 'domain')
    
    if 'address' in columns:
        op.drop_column('companies', 'address')
    
    # Make email and phone required (remove nullable) - specify existing types for MySQL
    op.alter_column('companies', 'email', existing_type=sa.String(255), nullable=False)
    op.alter_column('companies', 'phone', existing_type=sa.String(50), nullable=False)
    
    # Add Japanese address fields if they don't exist
    if 'postal_code' not in columns:
        op.add_column('companies', sa.Column('postal_code', sa.String(10), nullable=True))
    if 'prefecture' not in columns:
        op.add_column('companies', sa.Column('prefecture', sa.String(50), nullable=True))
    if 'city' not in columns:
        op.add_column('companies', sa.Column('city', sa.String(100), nullable=True))


def downgrade() -> None:
    # Add back domain and address columns
    op.add_column('companies', sa.Column('domain', sa.String(255), nullable=True))
    op.add_column('companies', sa.Column('address', sa.Text(), nullable=True))
    
    # Make email and phone nullable again
    op.alter_column('companies', 'email', existing_type=sa.String(255), nullable=True)
    op.alter_column('companies', 'phone', existing_type=sa.String(50), nullable=True)
    
    # Remove Japanese address fields
    op.drop_column('companies', 'postal_code')
    op.drop_column('companies', 'prefecture')
    op.drop_column('companies', 'city')
    
    # Re-create unique index for domain
    op.create_unique_constraint(None, 'companies', ['domain'])