"""
Todo System Seed Data

Creates sample todos with different statuses, priorities, and visibility levels
to demonstrate the todo management system functionality.
"""

from datetime import datetime, timedelta
from typing import Any, Dict

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.todo import Todo
from app.utils.constants import TodoStatus, TodoVisibility


async def seed_todo_data(db: AsyncSession, auth_result: Dict[str, Any]) -> Dict[str, int]:
    """
    Seed todo data for testing the todo management system.

    Args:
        db: Database session
        auth_result: Result from auth seeding containing user IDs

    Returns:
        Dictionary with counts of created todos
    """
    print("   Creating todo data...")

    # Get user IDs from auth result
    admin_user_id = auth_result["user_ids"]["admin"]
    recruiter_user_id = auth_result["user_ids"]["recruiter"]
    candidate_user_id = auth_result["user_ids"]["candidate"]
    hr_manager_user_id = auth_result["user_ids"]["hr_manager"]

    # Sample todos with different scenarios
    todos_data = [
        # Admin todos
        {
            "owner_id": admin_user_id,
            "created_by": admin_user_id,
            "title": "Review Q4 Recruitment Metrics",
            "description": "Analyze hiring performance and identify areas for improvement",
            "notes": "Focus on time-to-hire and candidate satisfaction scores",
            "status": TodoStatus.PENDING.value,
            "priority": "high",
            "visibility": TodoVisibility.COMPANY.value,
            "due_date": datetime.utcnow() + timedelta(days=7),
        },
        {
            "owner_id": admin_user_id,
            "created_by": admin_user_id,
            "title": "Update Company Policies",
            "description": "Review and update remote work and diversity policies",
            "status": TodoStatus.IN_PROGRESS.value,
            "priority": "medium",
            "visibility": TodoVisibility.PRIVATE.value,
            "due_date": datetime.utcnow() + timedelta(days=14),
        },
        {
            "owner_id": admin_user_id,
            "created_by": admin_user_id,
            "title": "Prepare Board Presentation",
            "description": "Create quarterly report for board meeting",
            "status": TodoStatus.COMPLETED.value,
            "priority": "high",
            "visibility": TodoVisibility.PRIVATE.value,
            "completed_at": datetime.utcnow() - timedelta(days=2),
            "due_date": datetime.utcnow() - timedelta(days=1),
        },
        # Recruiter todos
        {
            "owner_id": recruiter_user_id,
            "created_by": recruiter_user_id,
            "title": "Screen Frontend Developer Candidates",
            "description": "Initial screening for React developer position",
            "notes": "Focus on React, TypeScript, and testing experience",
            "status": TodoStatus.PENDING.value,
            "priority": "high",
            "visibility": TodoVisibility.TEAM.value,
            "due_date": datetime.utcnow() + timedelta(days=3),
        },
        {
            "owner_id": recruiter_user_id,
            "created_by": admin_user_id,
            "assigned_user_id": recruiter_user_id,
            "title": "Follow up with Backend Developer Candidates",
            "description": "Send follow-up emails to candidates from last week's interviews",
            "status": TodoStatus.IN_PROGRESS.value,
            "priority": "medium",
            "visibility": TodoVisibility.COMPANY.value,
            "due_date": datetime.utcnow() + timedelta(days=2),
        },
        {
            "owner_id": recruiter_user_id,
            "created_by": recruiter_user_id,
            "title": "Update Job Descriptions",
            "description": "Revise job descriptions based on hiring manager feedback",
            "status": TodoStatus.COMPLETED.value,
            "priority": "low",
            "visibility": TodoVisibility.PRIVATE.value,
            "completed_at": datetime.utcnow() - timedelta(days=1),
            "due_date": datetime.utcnow() - timedelta(days=1),
        },
        # HR Manager todos
        {
            "owner_id": hr_manager_user_id,
            "created_by": hr_manager_user_id,
            "title": "Conduct New Employee Orientation",
            "description": "Prepare orientation materials for new hires starting next week",
            "notes": "Include company culture presentation and IT setup checklist",
            "status": TodoStatus.PENDING.value,
            "priority": "high",
            "visibility": TodoVisibility.TEAM.value,
            "due_date": datetime.utcnow() + timedelta(days=5),
        },
        {
            "owner_id": hr_manager_user_id,
            "created_by": admin_user_id,
            "assigned_user_id": hr_manager_user_id,
            "title": "Review Employee Handbook",
            "description": "Annual review of employee handbook for compliance updates",
            "status": TodoStatus.IN_PROGRESS.value,
            "priority": "medium",
            "visibility": TodoVisibility.COMPANY.value,
            "due_date": datetime.utcnow() + timedelta(days=21),
        },
        # Candidate todos (self-assigned)
        {
            "owner_id": candidate_user_id,
            "created_by": candidate_user_id,
            "title": "Complete Technical Assessment",
            "description": "Finish the React coding challenge for MiraiWorks position",
            "notes": "Focus on clean code and proper testing",
            "status": TodoStatus.IN_PROGRESS.value,
            "priority": "high",
            "visibility": TodoVisibility.PRIVATE.value,
            "due_date": datetime.utcnow() + timedelta(days=2),
        },
        {
            "owner_id": candidate_user_id,
            "created_by": candidate_user_id,
            "title": "Prepare for Final Interview",
            "description": "Research company culture and prepare questions for the team",
            "status": TodoStatus.PENDING.value,
            "priority": "high",
            "visibility": TodoVisibility.PRIVATE.value,
            "due_date": datetime.utcnow() + timedelta(days=4),
        },
        # Overdue todos for testing
        {
            "owner_id": recruiter_user_id,
            "created_by": recruiter_user_id,
            "title": "Submit Monthly Report",
            "description": "Monthly recruitment metrics report",
            "status": TodoStatus.PENDING.value,
            "priority": "high",
            "visibility": TodoVisibility.PRIVATE.value,
            "due_date": datetime.utcnow() - timedelta(days=3),
            "expired_at": datetime.utcnow() - timedelta(days=1),
        },
        # Team collaboration todos
        {
            "owner_id": admin_user_id,
            "created_by": admin_user_id,
            "assigned_user_id": recruiter_user_id,
            "title": "Plan Q1 Hiring Strategy",
            "description": "Collaborate on hiring goals and resource allocation for Q1",
            "notes": "Include budget considerations and team expansion plans",
            "status": TodoStatus.PENDING.value,
            "priority": "medium",
            "visibility": TodoVisibility.TEAM.value,
            "due_date": datetime.utcnow() + timedelta(days=10),
        },
    ]

    # Create todos
    created_todos = []
    for todo_data in todos_data:
        todo = Todo(**todo_data)
        db.add(todo)
        created_todos.append(todo)

    await db.commit()

    # Refresh to get IDs
    for todo in created_todos:
        await db.refresh(todo)

    print(f"   ✓ Created {len(created_todos)} todos")
    print(f"     - Pending: {len([t for t in created_todos if t.status == TodoStatus.PENDING.value])}")
    print(f"     - In Progress: {len([t for t in created_todos if t.status == TodoStatus.IN_PROGRESS.value])}")
    print(f"     - Completed: {len([t for t in created_todos if t.status == TodoStatus.COMPLETED.value])}")
    print(f"     - Overdue: {len([t for t in created_todos if t.expired_at])}")

    return {
        "todos": len(created_todos),
        "pending": len([t for t in created_todos if t.status == TodoStatus.PENDING.value]),
        "in_progress": len([t for t in created_todos if t.status == TodoStatus.IN_PROGRESS.value]),
        "completed": len([t for t in created_todos if t.status == TodoStatus.COMPLETED.value]),
        "overdue": len([t for t in created_todos if t.expired_at]),
    }
