"""Add exam system tables

Revision ID: add_exam_system_tables  
Revises: HEAD
Create Date: 2024-12-27 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_exam_system_tables'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create exam_type enum
    exam_type_enum = postgresql.ENUM(
        'aptitude', 'skill', 'knowledge', 'personality', 'custom',
        name='examtype'
    )
    exam_type_enum.create(op.get_bind())

    # Create exam_status enum
    exam_status_enum = postgresql.ENUM(
        'draft', 'active', 'archived',
        name='examstatus'
    )
    exam_status_enum.create(op.get_bind())

    # Create question_type enum
    question_type_enum = postgresql.ENUM(
        'multiple_choice', 'single_choice', 'text_input', 'essay', 
        'true_false', 'rating', 'matching',
        name='questiontype'
    )
    question_type_enum.create(op.get_bind())

    # Create session_status enum
    session_status_enum = postgresql.ENUM(
        'not_started', 'in_progress', 'completed', 'expired', 'suspended',
        name='sessionstatus'
    )
    session_status_enum.create(op.get_bind())

    # Create exams table
    op.create_table(
        'exams',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('exam_type', exam_type_enum, nullable=False),
        sa.Column('status', exam_status_enum, nullable=False),
        sa.Column('company_id', sa.Integer(), nullable=False),
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.Column('time_limit_minutes', sa.Integer(), nullable=True),
        sa.Column('max_attempts', sa.Integer(), nullable=False),
        sa.Column('passing_score', sa.Float(), nullable=True),
        sa.Column('is_randomized', sa.Boolean(), nullable=False),
        sa.Column('allow_web_usage', sa.Boolean(), nullable=False),
        sa.Column('monitor_web_usage', sa.Boolean(), nullable=False),
        sa.Column('require_face_verification', sa.Boolean(), nullable=False),
        sa.Column('face_check_interval_minutes', sa.Integer(), nullable=False),
        sa.Column('show_results_immediately', sa.Boolean(), nullable=False),
        sa.Column('show_correct_answers', sa.Boolean(), nullable=False),
        sa.Column('show_score', sa.Boolean(), nullable=False),
        sa.Column('instructions', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_exams_id'), 'exams', ['id'], unique=False)
    op.create_index(op.f('ix_exams_company_id'), 'exams', ['company_id'], unique=False)

    # Create exam_questions table
    op.create_table(
        'exam_questions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('exam_id', sa.Integer(), nullable=False),
        sa.Column('question_text', sa.Text(), nullable=False),
        sa.Column('question_type', question_type_enum, nullable=False),
        sa.Column('order_index', sa.Integer(), nullable=False),
        sa.Column('points', sa.Float(), nullable=False),
        sa.Column('time_limit_seconds', sa.Integer(), nullable=True),
        sa.Column('is_required', sa.Boolean(), nullable=False),
        sa.Column('options', sa.JSON(), nullable=True),
        sa.Column('correct_answers', sa.JSON(), nullable=True),
        sa.Column('max_length', sa.Integer(), nullable=True),
        sa.Column('min_length', sa.Integer(), nullable=True),
        sa.Column('rating_scale', sa.Integer(), nullable=True),
        sa.Column('explanation', sa.Text(), nullable=True),
        sa.Column('tags', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['exam_id'], ['exams.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_exam_questions_id'), 'exam_questions', ['id'], unique=False)
    op.create_index(op.f('ix_exam_questions_exam_id'), 'exam_questions', ['exam_id'], unique=False)

    # Create exam_assignments table
    op.create_table(
        'exam_assignments',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('exam_id', sa.Integer(), nullable=False),
        sa.Column('candidate_id', sa.Integer(), nullable=False),
        sa.Column('assigned_by', sa.Integer(), nullable=True),
        sa.Column('due_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('custom_time_limit_minutes', sa.Integer(), nullable=True),
        sa.Column('custom_max_attempts', sa.Integer(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('completed', sa.Boolean(), nullable=False),
        sa.Column('notification_sent', sa.Boolean(), nullable=False),
        sa.Column('reminder_sent', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['assigned_by'], ['users.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['candidate_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['exam_id'], ['exams.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_exam_assignments_id'), 'exam_assignments', ['id'], unique=False)
    op.create_index(op.f('ix_exam_assignments_exam_id'), 'exam_assignments', ['exam_id'], unique=False)
    op.create_index(op.f('ix_exam_assignments_candidate_id'), 'exam_assignments', ['candidate_id'], unique=False)

    # Create exam_sessions table
    op.create_table(
        'exam_sessions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('exam_id', sa.Integer(), nullable=False),
        sa.Column('candidate_id', sa.Integer(), nullable=False),
        sa.Column('assignment_id', sa.Integer(), nullable=True),
        sa.Column('status', session_status_enum, nullable=False),
        sa.Column('attempt_number', sa.Integer(), nullable=False),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('time_remaining_seconds', sa.Integer(), nullable=True),
        sa.Column('current_question_index', sa.Integer(), nullable=False),
        sa.Column('total_questions', sa.Integer(), nullable=False),
        sa.Column('questions_answered', sa.Integer(), nullable=False),
        sa.Column('score', sa.Float(), nullable=True),
        sa.Column('max_score', sa.Float(), nullable=True),
        sa.Column('percentage', sa.Float(), nullable=True),
        sa.Column('passed', sa.Boolean(), nullable=True),
        sa.Column('web_usage_detected', sa.Boolean(), nullable=False),
        sa.Column('web_usage_count', sa.Integer(), nullable=False),
        sa.Column('face_verification_failed', sa.Boolean(), nullable=False),
        sa.Column('face_check_count', sa.Integer(), nullable=False),
        sa.Column('face_verification_data', sa.JSON(), nullable=True),
        sa.Column('user_agent', sa.Text(), nullable=True),
        sa.Column('ip_address', sa.String(length=45), nullable=True),
        sa.Column('screen_resolution', sa.String(length=20), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['assignment_id'], ['exam_assignments.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['candidate_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['exam_id'], ['exams.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_exam_sessions_id'), 'exam_sessions', ['id'], unique=False)
    op.create_index(op.f('ix_exam_sessions_exam_id'), 'exam_sessions', ['exam_id'], unique=False)
    op.create_index(op.f('ix_exam_sessions_candidate_id'), 'exam_sessions', ['candidate_id'], unique=False)

    # Create exam_answers table
    op.create_table(
        'exam_answers',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('session_id', sa.Integer(), nullable=False),
        sa.Column('question_id', sa.Integer(), nullable=False),
        sa.Column('answer_data', sa.JSON(), nullable=True),
        sa.Column('answer_text', sa.Text(), nullable=True),
        sa.Column('selected_options', sa.JSON(), nullable=True),
        sa.Column('is_correct', sa.Boolean(), nullable=True),
        sa.Column('points_earned', sa.Float(), nullable=False),
        sa.Column('points_possible', sa.Float(), nullable=False),
        sa.Column('time_spent_seconds', sa.Integer(), nullable=True),
        sa.Column('answered_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['question_id'], ['exam_questions.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['session_id'], ['exam_sessions.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_exam_answers_id'), 'exam_answers', ['id'], unique=False)
    op.create_index(op.f('ix_exam_answers_session_id'), 'exam_answers', ['session_id'], unique=False)
    op.create_index(op.f('ix_exam_answers_question_id'), 'exam_answers', ['question_id'], unique=False)

    # Create exam_monitoring_events table
    op.create_table(
        'exam_monitoring_events',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('session_id', sa.Integer(), nullable=False),
        sa.Column('event_type', sa.String(length=50), nullable=False),
        sa.Column('event_data', sa.JSON(), nullable=True),
        sa.Column('severity', sa.String(length=20), nullable=False),
        sa.Column('timestamp', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['session_id'], ['exam_sessions.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_exam_monitoring_events_id'), 'exam_monitoring_events', ['id'], unique=False)
    op.create_index(op.f('ix_exam_monitoring_events_session_id'), 'exam_monitoring_events', ['session_id'], unique=False)


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_table('exam_monitoring_events')
    op.drop_table('exam_answers')
    op.drop_table('exam_sessions')
    op.drop_table('exam_assignments')
    op.drop_table('exam_questions')
    op.drop_table('exams')

    # Drop enums
    postgresql.ENUM(name='sessionstatus').drop(op.get_bind())
    postgresql.ENUM(name='questiontype').drop(op.get_bind())
    postgresql.ENUM(name='examstatus').drop(op.get_bind())
    postgresql.ENUM(name='examtype').drop(op.get_bind())