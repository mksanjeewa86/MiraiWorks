"""Add video call tables for interview feature

Revision ID: add_video_call_tables
Revises:
Create Date: 2025-09-22 12:00:00.000000

"""
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

from alembic import op

# revision identifiers, used by Alembic.
revision = "add_video_call_tables"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create video_calls table
    op.create_table(
        "video_calls",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("job_id", sa.Integer(), nullable=True),
        sa.Column("interview_id", sa.Integer(), nullable=True),
        sa.Column("interviewer_id", sa.Integer(), nullable=False),
        sa.Column("candidate_id", sa.Integer(), nullable=False),
        sa.Column("scheduled_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("ended_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("status", sa.String(20), nullable=False, server_default="scheduled"),
        sa.Column("room_id", sa.String(255), nullable=False),
        sa.Column("recording_url", sa.String(255), nullable=True),
        sa.Column("transcription_enabled", sa.Boolean(), default=True),
        sa.Column("transcription_language", sa.String(10), default="ja"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["candidate_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["interview_id"], ["interviews.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(["interviewer_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["job_id"], ["positions.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("room_id"),
    )
    op.create_index(
        op.f("ix_video_calls_candidate_id"),
        "video_calls",
        ["candidate_id"],
        unique=False,
    )
    op.create_index(op.f("ix_video_calls_id"), "video_calls", ["id"], unique=False)
    op.create_index(
        op.f("ix_video_calls_interview_id"),
        "video_calls",
        ["interview_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_video_calls_interviewer_id"),
        "video_calls",
        ["interviewer_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_video_calls_job_id"), "video_calls", ["job_id"], unique=False
    )
    op.create_index(
        "idx_video_calls_scheduled_at", "video_calls", ["scheduled_at"], unique=False
    )
    op.create_index("idx_video_calls_status", "video_calls", ["status"], unique=False)

    # Create call_participants table
    op.create_table(
        "call_participants",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("video_call_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("joined_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("left_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("connection_quality", sa.String(20), nullable=True),
        sa.Column("device_info", mysql.JSON(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["video_call_id"], ["video_calls.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_call_participants_id"), "call_participants", ["id"], unique=False
    )
    op.create_index(
        op.f("ix_call_participants_user_id"),
        "call_participants",
        ["user_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_call_participants_video_call_id"),
        "call_participants",
        ["video_call_id"],
        unique=False,
    )
    op.create_index(
        "idx_call_participants_video_call_user",
        "call_participants",
        ["video_call_id", "user_id"],
        unique=True,
    )

    # Create recording_consents table
    op.create_table(
        "recording_consents",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("video_call_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("consented", sa.Boolean(), default=False),
        sa.Column("consented_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["video_call_id"], ["video_calls.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_recording_consents_id"), "recording_consents", ["id"], unique=False
    )
    op.create_index(
        op.f("ix_recording_consents_user_id"),
        "recording_consents",
        ["user_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_recording_consents_video_call_id"),
        "recording_consents",
        ["video_call_id"],
        unique=False,
    )
    op.create_index(
        "idx_recording_consents_video_call_user",
        "recording_consents",
        ["video_call_id", "user_id"],
        unique=True,
    )

    # Create call_transcriptions table
    op.create_table(
        "call_transcriptions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("video_call_id", sa.Integer(), nullable=False),
        sa.Column("transcript_url", sa.String(255), nullable=True),
        sa.Column("transcript_text", sa.Text(), nullable=True),
        sa.Column("language", sa.String(10), default="ja"),
        sa.Column(
            "processing_status", sa.String(20), nullable=False, server_default="pending"
        ),
        sa.Column("word_count", sa.Integer(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("processed_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["video_call_id"], ["video_calls.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("video_call_id"),
    )
    op.create_index(
        op.f("ix_call_transcriptions_id"), "call_transcriptions", ["id"], unique=False
    )
    op.create_index(
        op.f("ix_call_transcriptions_video_call_id"),
        "call_transcriptions",
        ["video_call_id"],
        unique=True,
    )

    # Create transcription_segments table
    op.create_table(
        "transcription_segments",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("video_call_id", sa.Integer(), nullable=False),
        sa.Column("speaker_id", sa.Integer(), nullable=False),
        sa.Column("segment_text", sa.Text(), nullable=False),
        sa.Column("start_time", sa.Float(), nullable=False),
        sa.Column("end_time", sa.Float(), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["speaker_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["video_call_id"], ["video_calls.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_transcription_segments_id"),
        "transcription_segments",
        ["id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_transcription_segments_speaker_id"),
        "transcription_segments",
        ["speaker_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_transcription_segments_video_call_id"),
        "transcription_segments",
        ["video_call_id"],
        unique=False,
    )
    op.create_index(
        "idx_transcription_segments_video_call_time",
        "transcription_segments",
        ["video_call_id", "start_time"],
        unique=False,
    )


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_index(
        "idx_transcription_segments_video_call_time",
        table_name="transcription_segments",
    )
    op.drop_index(
        op.f("ix_transcription_segments_video_call_id"),
        table_name="transcription_segments",
    )
    op.drop_index(
        op.f("ix_transcription_segments_speaker_id"),
        table_name="transcription_segments",
    )
    op.drop_index(
        op.f("ix_transcription_segments_id"), table_name="transcription_segments"
    )
    op.drop_table("transcription_segments")

    op.drop_index(
        op.f("ix_call_transcriptions_video_call_id"), table_name="call_transcriptions"
    )
    op.drop_index(op.f("ix_call_transcriptions_id"), table_name="call_transcriptions")
    op.drop_table("call_transcriptions")

    op.drop_index(
        "idx_recording_consents_video_call_user", table_name="recording_consents"
    )
    op.drop_index(
        op.f("ix_recording_consents_video_call_id"), table_name="recording_consents"
    )
    op.drop_index(
        op.f("ix_recording_consents_user_id"), table_name="recording_consents"
    )
    op.drop_index(op.f("ix_recording_consents_id"), table_name="recording_consents")
    op.drop_table("recording_consents")

    op.drop_index(
        "idx_call_participants_video_call_user", table_name="call_participants"
    )
    op.drop_index(
        op.f("ix_call_participants_video_call_id"), table_name="call_participants"
    )
    op.drop_index(op.f("ix_call_participants_user_id"), table_name="call_participants")
    op.drop_index(op.f("ix_call_participants_id"), table_name="call_participants")
    op.drop_table("call_participants")

    op.drop_index("idx_video_calls_status", table_name="video_calls")
    op.drop_index("idx_video_calls_scheduled_at", table_name="video_calls")
    op.drop_index(op.f("ix_video_calls_job_id"), table_name="video_calls")
    op.drop_index(op.f("ix_video_calls_interviewer_id"), table_name="video_calls")
    op.drop_index(op.f("ix_video_calls_interview_id"), table_name="video_calls")
    op.drop_index(op.f("ix_video_calls_id"), table_name="video_calls")
    op.drop_index(op.f("ix_video_calls_candidate_id"), table_name="video_calls")
    op.drop_table("video_calls")
