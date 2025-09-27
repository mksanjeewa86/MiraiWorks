"""
Notification System Seed Data

Creates sample notifications to demonstrate the notification system functionality.
"""

from datetime import datetime, timedelta
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.notification import Notification


async def seed_notification_data(db: AsyncSession, auth_result: dict[str, Any]) -> dict[str, int]:
    """
    Seed notification data for testing the notification system.

    Args:
        db: Database session
        auth_result: Result from auth seeding containing user IDs

    Returns:
        Dictionary with counts of created notifications
    """
    print("   Creating notification data...")

    # Get user IDs from auth result
    admin_user_id = auth_result["user_ids"]["admin"]
    recruiter_user_id = auth_result["user_ids"]["recruiter"]
    candidate_user_id = auth_result["user_ids"]["candidate"]
    hr_manager_user_id = auth_result["user_ids"]["hr_manager"]

    # Sample notifications with different types and scenarios
    notifications_data = [
        # Admin notifications
        {
            "user_id": admin_user_id,
            "type": "system",
            "title": "System Maintenance Scheduled",
            "message": "Scheduled maintenance will occur tonight from 2:00 AM to 4:00 AM EST.",
            "payload": {
                "maintenance_window": "2024-01-15T02:00:00Z to 2024-01-15T04:00:00Z",
                "affected_services": ["API", "Database"],
                "severity": "low",
            },
            "is_read": False,
            "created_at": datetime.utcnow() - timedelta(hours=2),
        },
        {
            "user_id": admin_user_id,
            "type": "alert",
            "title": "High Priority Todo Overdue",
            "message": "The todo 'Review Q4 Recruitment Metrics' is now overdue.",
            "payload": {"todo_id": 1, "priority": "high", "days_overdue": 1},
            "is_read": True,
            "created_at": datetime.utcnow() - timedelta(days=1),
            "read_at": datetime.utcnow() - timedelta(hours=12),
        },
        # Recruiter notifications
        {
            "user_id": recruiter_user_id,
            "type": "interview",
            "title": "Interview Scheduled",
            "message": "New interview scheduled with John Doe for Frontend Developer position.",
            "payload": {
                "interview_id": 1,
                "candidate_name": "John Doe",
                "position": "Frontend Developer",
                "scheduled_time": "2024-01-16T14:00:00Z",
            },
            "is_read": False,
            "created_at": datetime.utcnow() - timedelta(hours=6),
        },
        {
            "user_id": recruiter_user_id,
            "type": "application",
            "title": "New Job Application",
            "message": "Sarah Johnson has applied for the Backend Developer position.",
            "payload": {
                "application_id": 2,
                "candidate_name": "Sarah Johnson",
                "position": "Backend Developer",
                "resume_score": 85,
            },
            "is_read": False,
            "created_at": datetime.utcnow() - timedelta(hours=4),
        },
        {
            "user_id": recruiter_user_id,
            "type": "reminder",
            "title": "Follow-up Reminder",
            "message": "Don't forget to follow up with candidates from last week's interviews.",
            "payload": {"reminder_type": "follow_up", "candidate_count": 3, "interview_date": "2024-01-08"},
            "is_read": True,
            "created_at": datetime.utcnow() - timedelta(days=2),
            "read_at": datetime.utcnow() - timedelta(days=1),
        },
        # HR Manager notifications
        {
            "user_id": hr_manager_user_id,
            "type": "onboarding",
            "title": "New Employee Onboarding",
            "message": "3 new employees are starting next week. Prepare onboarding materials.",
            "payload": {
                "new_employee_count": 3,
                "start_date": "2024-01-22",
                "departments": ["Engineering", "Marketing"],
            },
            "is_read": False,
            "created_at": datetime.utcnow() - timedelta(hours=8),
        },
        {
            "user_id": hr_manager_user_id,
            "type": "policy",
            "title": "Policy Update Required",
            "message": "Employee handbook needs to be updated for compliance with new regulations.",
            "payload": {"policy_type": "compliance", "deadline": "2024-02-01", "priority": "medium"},
            "is_read": False,
            "created_at": datetime.utcnow() - timedelta(days=1),
        },
        # Candidate notifications
        {
            "user_id": candidate_user_id,
            "type": "interview",
            "title": "Interview Confirmation",
            "message": "Your interview for Frontend Developer position is confirmed for tomorrow at 2:00 PM.",
            "payload": {
                "interview_id": 1,
                "position": "Frontend Developer",
                "interview_time": "2024-01-16T14:00:00Z",
                "interviewer": "Jane Smith",
                "location": "Virtual - Zoom",
            },
            "is_read": False,
            "created_at": datetime.utcnow() - timedelta(hours=12),
        },
        {
            "user_id": candidate_user_id,
            "type": "assessment",
            "title": "Technical Assessment Assigned",
            "message": "You have been assigned a technical assessment. Please complete it within 48 hours.",
            "payload": {
                "assessment_id": 1,
                "assessment_type": "coding_challenge",
                "deadline": "2024-01-17T23:59:59Z",
                "estimated_duration": "2-3 hours",
            },
            "is_read": True,
            "created_at": datetime.utcnow() - timedelta(days=1),
            "read_at": datetime.utcnow() - timedelta(hours=18),
        },
        {
            "user_id": candidate_user_id,
            "type": "application",
            "title": "Application Status Update",
            "message": "Your application for Frontend Developer position has been moved to the next stage.",
            "payload": {
                "application_id": 1,
                "position": "Frontend Developer",
                "previous_stage": "Initial Screening",
                "current_stage": "Technical Interview",
                "next_steps": "Complete technical assessment",
            },
            "is_read": False,
            "created_at": datetime.utcnow() - timedelta(hours=3),
        },
        # System-wide notifications
        {
            "user_id": admin_user_id,
            "type": "system",
            "title": "Weekly Report Available",
            "message": "Your weekly recruitment metrics report is ready for review.",
            "payload": {
                "report_type": "weekly_metrics",
                "report_period": "2024-01-08 to 2024-01-14",
                "key_metrics": {"applications": 25, "interviews": 8, "hires": 2},
            },
            "is_read": False,
            "created_at": datetime.utcnow() - timedelta(hours=1),
        },
        {
            "user_id": recruiter_user_id,
            "type": "system",
            "title": "Weekly Report Available",
            "message": "Your weekly recruitment metrics report is ready for review.",
            "payload": {
                "report_type": "weekly_metrics",
                "report_period": "2024-01-08 to 2024-01-14",
                "key_metrics": {"applications_reviewed": 15, "interviews_conducted": 6, "candidates_advanced": 4},
            },
            "is_read": False,
            "created_at": datetime.utcnow() - timedelta(hours=1),
        },
        # Urgent notifications
        {
            "user_id": admin_user_id,
            "type": "urgent",
            "title": "Security Alert",
            "message": "Multiple failed login attempts detected for admin account.",
            "payload": {
                "alert_type": "security",
                "failed_attempts": 5,
                "source_ip": "192.168.1.100",
                "timestamp": datetime.utcnow() - timedelta(minutes=30),
                "action_required": "Review and secure account",
            },
            "is_read": False,
            "created_at": datetime.utcnow() - timedelta(minutes=30),
        },
    ]

    # Create notifications
    created_notifications = []
    for notification_data in notifications_data:
        notification = Notification(**notification_data)
        db.add(notification)
        created_notifications.append(notification)

    await db.commit()

    # Refresh to get IDs
    for notification in created_notifications:
        await db.refresh(notification)

    print(f"   ✓ Created {len(created_notifications)} notifications")
    print(f"     - Unread: {len([n for n in created_notifications if not n.is_read])}")
    print(f"     - Read: {len([n for n in created_notifications if n.is_read])}")

    # Count by type
    type_counts = {}
    for notification in created_notifications:
        type_counts[notification.type] = type_counts.get(notification.type, 0) + 1

    for notification_type, count in type_counts.items():
        print(f"     - {notification_type.title()}: {count}")

    return {
        "notifications": len(created_notifications),
        "unread": len([n for n in created_notifications if not n.is_read]),
        "read": len([n for n in created_notifications if n.is_read]),
        "types": type_counts,
    }
