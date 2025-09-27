"""
Seeds package for MiraiWorks

This package contains all seed data organized into separate modules:
- auth_data: Authentication data (roles, companies, users)
- mbti_questions: MBTI personality test questions
- sample_data: Sample application data (messages, interviews, positions)
"""

from app.seeds.assessment_and_exam_system import seed_exam_data
from app.seeds.notification_data import seed_notification_data
from app.seeds.personality_test_questions import seed_mbti_questions
from app.seeds.resume_data import seed_resume_data
from app.seeds.test_messages_interviews_jobs import seed_sample_data
from app.seeds.todo_data import seed_todo_data
from app.seeds.users_and_companies import seed_auth_data

__all__ = [
    "seed_auth_data",
    "seed_mbti_questions",
    "seed_sample_data",
    "seed_exam_data",
    "seed_resume_data",
    "seed_todo_data",
    "seed_notification_data",
]
