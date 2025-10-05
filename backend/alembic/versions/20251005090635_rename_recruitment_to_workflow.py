"""Rename recruitment process tables to workflow

Revision ID: rename_recruitment_to_workflow
Revises: add_video_call_tables
Create Date: 2025-10-05

"""

from alembic import op

# revision identifiers, used by Alembic.
revision = "rename_recruitment_to_workflow"
down_revision = "add_video_call_tables"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Rename tables
    op.rename_table("recruitment_processes", "workflows")
    op.rename_table("process_nodes", "workflow_nodes")
    op.rename_table("process_viewers", "workflow_viewers")
    op.rename_table("candidate_recruitment_processes", "candidate_workflows")
    op.rename_table("node_connections", "workflow_node_connections")
    op.rename_table("node_executions", "workflow_node_executions")


def downgrade() -> None:
    # Revert table renames
    op.rename_table("workflows", "recruitment_processes")
    op.rename_table("workflow_nodes", "process_nodes")
    op.rename_table("workflow_viewers", "process_viewers")
    op.rename_table("candidate_workflows", "candidate_recruitment_processes")
    op.rename_table("workflow_node_connections", "node_connections")
    op.rename_table("workflow_node_executions", "node_executions")
