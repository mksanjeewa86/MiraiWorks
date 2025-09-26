"""
Seeds package for MiraiWorks

This package contains all seed data organized into separate modules:
- auth_data: Authentication data (roles, companies, users)
- mbti_questions: MBTI personality test questions
- sample_data: Sample application data (messages, interviews, positions)
"""

from .assessment_and_exam_system import seed_exam_data
from .notification_data import seed_notification_data
from .personality_test_questions import seed_mbti_questions
from .resume_data import seed_resume_data
from .test_messages_interviews_jobs import seed_sample_data
from .todo_data import seed_todo_data
from .users_and_companies import seed_auth_data

__all__ = [
    "seed_auth_data",
    "seed_mbti_questions",
    "seed_sample_data",
    "seed_exam_data",
    "seed_resume_data",
    "seed_todo_data",
    "seed_notification_data",
]
