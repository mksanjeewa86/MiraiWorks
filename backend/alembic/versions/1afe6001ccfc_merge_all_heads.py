"""merge_all_heads

Revision ID: 1afe6001ccfc
Revises: add_soft_delete_to_todos, add_video_call_tables, migrate_simple, migrate_to_messages, optimize_messages
Create Date: 2025-09-22 21:01:47.217808

"""
from collections.abc import Sequence

# revision identifiers, used by Alembic.
revision: str = "1afe6001ccfc"
down_revision: str | None = (  # type: ignore[assignment]
    "add_soft_delete_to_todos",
    "add_video_call_tables",
    "migrate_simple",
    "migrate_to_messages",
    "optimize_messages",
)
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
