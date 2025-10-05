"""Create recruitment workflow tables

Revision ID: recruitment_workflow_001
Revises:
Create Date: 2024-01-15 10:00:00.000000

"""
import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "recruitment_workflow_001"
down_revision = "37a8bb883c3b"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create workflows table
    op.create_table(
        "workflows",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column(
            "employer_company_id",
            sa.Integer(),
            sa.ForeignKey("companies.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column(
            "position_id",
            sa.Integer(),
            sa.ForeignKey("positions.id", ondelete="SET NULL"),
            nullable=True,
            index=True,
        ),
        sa.Column(
            "created_by",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column(
            "updated_by",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("status", sa.String(50), nullable=False, default="draft", index=True),
        sa.Column("version", sa.Integer(), nullable=False, default=1),
        sa.Column("is_template", sa.Boolean(), nullable=False, default=False),
        sa.Column("template_name", sa.String(255), nullable=True),
        sa.Column("settings", sa.JSON(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
            index=True,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            onupdate=sa.func.now(),
            nullable=False,
        ),
        sa.Column("activated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("archived_at", sa.DateTime(timezone=True), nullable=True),
    )

    # Create process_nodes table
    op.create_table(
        "process_nodes",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column(
            "process_id",
            sa.Integer(),
            sa.ForeignKey("workflows.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column("node_type", sa.String(50), nullable=False, index=True),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("sequence_order", sa.Integer(), nullable=False, index=True),
        sa.Column("position_x", sa.Float(), nullable=False, default=0.0),
        sa.Column("position_y", sa.Float(), nullable=False, default=0.0),
        sa.Column("config", sa.JSON(), nullable=True),
        sa.Column("requirements", sa.JSON(), nullable=True),
        sa.Column("instructions", sa.Text(), nullable=True),
        sa.Column("estimated_duration_minutes", sa.Integer(), nullable=True),
        sa.Column("status", sa.String(50), nullable=False, default="draft", index=True),
        sa.Column("is_required", sa.Boolean(), nullable=False, default=True),
        sa.Column("can_skip", sa.Boolean(), nullable=False, default=False),
        sa.Column("auto_advance", sa.Boolean(), nullable=False, default=False),
        sa.Column(
            "created_by",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column(
            "updated_by",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
            index=True,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            onupdate=sa.func.now(),
            nullable=False,
        ),
        sa.UniqueConstraint(
            "process_id", "sequence_order", name="uq_process_node_sequence"
        ),
    )

    # Create node_connections table
    op.create_table(
        "node_connections",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column(
            "process_id",
            sa.Integer(),
            sa.ForeignKey("workflows.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column(
            "source_node_id",
            sa.Integer(),
            sa.ForeignKey("workflow_nodes.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column(
            "target_node_id",
            sa.Integer(),
            sa.ForeignKey("workflow_nodes.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column(
            "condition_type",
            sa.String(50),
            nullable=False,
            default="success",
            index=True,
        ),
        sa.Column("condition_config", sa.JSON(), nullable=True),
        sa.Column("label", sa.String(255), nullable=True),
        sa.Column("description", sa.String(500), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
            index=True,
        ),
    )

    # Create candidate_workflows table
    op.create_table(
        "candidate_workflows",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column(
            "candidate_id",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column(
            "process_id",
            sa.Integer(),
            sa.ForeignKey("workflows.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column(
            "current_node_id",
            sa.Integer(),
            sa.ForeignKey("workflow_nodes.id", ondelete="SET NULL"),
            nullable=True,
            index=True,
        ),
        sa.Column(
            "status", sa.String(50), nullable=False, default="not_started", index=True
        ),
        sa.Column(
            "assigned_recruiter_id",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
            index=True,
        ),
        sa.Column("assigned_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("failed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("withdrawn_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("overall_score", sa.DECIMAL(5, 2), nullable=True),
        sa.Column("final_result", sa.String(50), nullable=True, index=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
            index=True,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            onupdate=sa.func.now(),
            nullable=False,
        ),
        sa.UniqueConstraint("candidate_id", "process_id", name="uq_candidate_process"),
    )

    # Create node_executions table
    op.create_table(
        "node_executions",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column(
            "candidate_process_id",
            sa.Integer(),
            sa.ForeignKey("candidate_workflows.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column(
            "node_id",
            sa.Integer(),
            sa.ForeignKey("workflow_nodes.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column(
            "status", sa.String(50), nullable=False, default="pending", index=True
        ),
        sa.Column("result", sa.String(50), nullable=True, index=True),
        sa.Column("score", sa.DECIMAL(5, 2), nullable=True),
        sa.Column("feedback", sa.Text(), nullable=True),
        sa.Column("assessor_notes", sa.Text(), nullable=True),
        sa.Column("execution_data", sa.JSON(), nullable=True),
        sa.Column(
            "interview_id",
            sa.Integer(),
            sa.ForeignKey("interviews.id", ondelete="SET NULL"),
            nullable=True,
            index=True,
        ),
        sa.Column(
            "todo_id",
            sa.Integer(),
            sa.ForeignKey("todos.id", ondelete="SET NULL"),
            nullable=True,
            index=True,
        ),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("due_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "assigned_to",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
            index=True,
        ),
        sa.Column(
            "completed_by",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column(
            "reviewed_by",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
            index=True,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            onupdate=sa.func.now(),
            nullable=False,
        ),
        sa.UniqueConstraint(
            "candidate_process_id", "node_id", name="uq_candidate_node_execution"
        ),
    )

    # Create process_viewers table
    op.create_table(
        "process_viewers",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column(
            "process_id",
            sa.Integer(),
            sa.ForeignKey("workflows.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column(
            "user_id",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column("role", sa.String(50), nullable=False, index=True),
        sa.Column("permissions", sa.JSON(), nullable=True),
        sa.Column(
            "added_by",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column(
            "added_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
            index=True,
        ),
        sa.UniqueConstraint("process_id", "user_id", name="uq_process_viewer"),
    )

    # Create indexes for better performance
    op.create_index(
        "ix_workflows_status_company",
        "workflows",
        ["status", "employer_company_id"],
    )
    op.create_index(
        "ix_process_nodes_process_sequence",
        "process_nodes",
        ["process_id", "sequence_order"],
    )
    op.create_index(
        "ix_candidate_workflows_status_recruiter",
        "candidate_workflows",
        ["status", "assigned_recruiter_id"],
    )
    op.create_index(
        "ix_node_executions_status_assigned",
        "node_executions",
        ["status", "assigned_to"],
    )
    op.create_index("ix_node_executions_due_date", "node_executions", ["due_date"])


def downgrade() -> None:
    # Drop indexes
    op.drop_index("ix_node_executions_due_date")
    op.drop_index("ix_node_executions_status_assigned")
    op.drop_index("ix_candidate_workflows_status_recruiter")
    op.drop_index("ix_process_nodes_process_sequence")
    op.drop_index("ix_workflows_status_company")

    # Drop tables in reverse order (to handle foreign key constraints)
    op.drop_table("process_viewers")
    op.drop_table("node_executions")
    op.drop_table("candidate_workflows")
    op.drop_table("node_connections")
    op.drop_table("process_nodes")
    op.drop_table("workflows")
