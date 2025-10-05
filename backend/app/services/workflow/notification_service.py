from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.candidate_workflow import CandidateWorkflow
from app.models.workflow import Workflow
from app.models.workflow_node import WorkflowNode
from app.models.workflow_node_execution import WorkflowNodeExecution


class RecruitmentWorkflowNotificationService:
    """Service for handling notifications in recruitment workflows"""

    async def notify_process_activated(
        self, db: AsyncSession, process: Workflow
    ) -> None:
        """Send notification when a process is activated"""
        # Get all viewers/recruiters who should be notified
        notifications = []

        # Notify process viewers
        for viewer in process.viewers:
            if viewer.can_execute:
                notifications.append(
                    {
                        "user_id": viewer.user_id,
                        "type": "process_activated",
                        "title": "Recruitment Process Activated",
                        "message": f"Process '{process.name}' has been activated and is ready for candidates.",
                        "data": {
                            "process_id": process.id,
                            "process_name": process.name,
                            "activated_at": process.activated_at.isoformat()
                            if process.activated_at
                            else None,
                        },
                    }
                )

        await self._send_notifications(db, notifications)

    async def notify_candidate_assigned(
        self, db: AsyncSession, candidate_process: CandidateWorkflow
    ) -> None:
        """Send notification when a candidate is assigned to a process"""
        notifications = []

        # Notify assigned recruiter
        if candidate_process.assigned_recruiter_id:
            notifications.append(
                {
                    "user_id": candidate_process.assigned_recruiter_id,
                    "type": "candidate_assigned",
                    "title": "New Candidate Assigned",
                    "message": f"You have been assigned a new candidate in '{candidate_process.process.name}'.",
                    "data": {
                        "candidate_process_id": candidate_process.id,
                        "candidate_id": candidate_process.candidate_id,
                        "process_id": candidate_process.workflow_id,
                        "process_name": candidate_process.process.name,
                    },
                }
            )

        # Notify candidate
        notifications.append(
            {
                "user_id": candidate_process.candidate_id,
                "type": "process_assigned",
                "title": "Application Process Started",
                "message": f"You have been entered into the recruitment process for '{candidate_process.process.name}'.",
                "data": {
                    "candidate_process_id": candidate_process.id,
                    "process_id": candidate_process.workflow_id,
                    "process_name": candidate_process.process.name,
                },
            }
        )

        await self._send_notifications(db, notifications)

    async def notify_process_started(
        self,
        db: AsyncSession,
        candidate_process: CandidateWorkflow,
        first_node: WorkflowNode,
    ) -> None:
        """Send notification when a candidate process starts"""
        notifications = []

        # Notify candidate
        notifications.append(
            {
                "user_id": candidate_process.candidate_id,
                "type": "process_started",
                "title": "Your Application Process Has Started",
                "message": f"Your application process for '{candidate_process.process.name}' has begun with: {first_node.title}",
                "data": {
                    "candidate_process_id": candidate_process.id,
                    "process_id": candidate_process.workflow_id,
                    "process_name": candidate_process.process.name,
                    "first_node_id": first_node.id,
                    "first_node_title": first_node.title,
                },
            }
        )

        # Notify assigned recruiter
        if candidate_process.assigned_recruiter_id:
            notifications.append(
                {
                    "user_id": candidate_process.assigned_recruiter_id,
                    "type": "candidate_process_started",
                    "title": "Candidate Process Started",
                    "message": f"Process started for candidate in '{candidate_process.process.name}'",
                    "data": {
                        "candidate_process_id": candidate_process.id,
                        "candidate_id": candidate_process.candidate_id,
                        "process_id": candidate_process.workflow_id,
                        "process_name": candidate_process.process.name,
                    },
                }
            )

        await self._send_notifications(db, notifications)

    async def notify_node_assigned(
        self,
        db: AsyncSession,
        execution: WorkflowNodeExecution,
        node: WorkflowNode,
        candidate_process: CandidateWorkflow,
    ) -> None:
        """Send notification when a node is assigned"""
        notifications = []

        # Notify assignee
        if execution.assigned_to:
            notifications.append(
                {
                    "user_id": execution.assigned_to,
                    "type": "node_assigned",
                    "title": f"New Task: {node.title}",
                    "message": f"You have been assigned '{node.title}' for a candidate in '{candidate_process.process.name}'",
                    "data": {
                        "execution_id": execution.id,
                        "node_id": node.id,
                        "node_title": node.title,
                        "node_type": node.node_type,
                        "candidate_process_id": candidate_process.id,
                        "process_name": candidate_process.process.name,
                        "due_date": execution.due_date.isoformat()
                        if execution.due_date
                        else None,
                    },
                }
            )

        # Notify candidate if it's their action (like a todo/assessment)
        if node.node_type in ["todo", "assessment"] and candidate_process.candidate_id:
            notifications.append(
                {
                    "user_id": candidate_process.candidate_id,
                    "type": "task_available",
                    "title": f"New Task: {node.title}",
                    "message": f"A new task is available in your application process: {node.title}",
                    "data": {
                        "execution_id": execution.id,
                        "node_id": node.id,
                        "node_title": node.title,
                        "node_type": node.node_type,
                        "candidate_process_id": candidate_process.id,
                        "process_name": candidate_process.process.name,
                        "instructions": node.instructions,
                    },
                }
            )

        await self._send_notifications(db, notifications)

    async def notify_node_completed(
        self,
        db: AsyncSession,
        execution: WorkflowNodeExecution,
        node: WorkflowNode,
        candidate_process: CandidateWorkflow,
    ) -> None:
        """Send notification when a node is completed"""
        notifications = []

        # Notify process stakeholders
        if (
            candidate_process.assigned_recruiter_id
            and execution.completed_by != candidate_process.assigned_recruiter_id
        ):
            notifications.append(
                {
                    "user_id": candidate_process.assigned_recruiter_id,
                    "type": "node_completed",
                    "title": f"Task Completed: {node.title}",
                    "message": f"'{node.title}' has been completed for candidate in '{candidate_process.process.name}'",
                    "data": {
                        "execution_id": execution.id,
                        "node_id": node.id,
                        "node_title": node.title,
                        "result": execution.result,
                        "score": execution.score,
                        "completed_by": execution.completed_by,
                        "candidate_process_id": candidate_process.id,
                        "process_name": candidate_process.process.name,
                    },
                }
            )

        # Notify candidate of their progress (if feedback is available)
        if (
            execution.feedback
            and candidate_process.candidate_id != execution.completed_by
        ):
            notifications.append(
                {
                    "user_id": candidate_process.candidate_id,
                    "type": "feedback_available",
                    "title": f"Feedback for {node.title}",
                    "message": f"Feedback is available for your completed task: {node.title}",
                    "data": {
                        "execution_id": execution.id,
                        "node_id": node.id,
                        "node_title": node.title,
                        "feedback": execution.feedback,
                        "score": execution.score,
                        "candidate_process_id": candidate_process.id,
                        "process_name": candidate_process.process.name,
                    },
                }
            )

        await self._send_notifications(db, notifications)

    async def notify_process_completed(
        self, db: AsyncSession, candidate_process: CandidateWorkflow
    ) -> None:
        """Send notification when a process is completed"""
        notifications = []

        # Notify candidate
        status_message = {
            "hired": "Congratulations! You have been selected.",
            "rejected": "Thank you for your interest. We have decided to move forward with other candidates.",
            "withdrawn": "Your application has been withdrawn as requested.",
        }.get(
            candidate_process.final_result,
            "Your application process has been completed.",
        )

        notifications.append(
            {
                "user_id": candidate_process.candidate_id,
                "type": "process_completed",
                "title": f"Application Process Complete - {candidate_process.process.name}",
                "message": status_message,
                "data": {
                    "candidate_process_id": candidate_process.id,
                    "process_id": candidate_process.workflow_id,
                    "process_name": candidate_process.process.name,
                    "final_result": candidate_process.final_result,
                    "overall_score": candidate_process.overall_score,
                },
            }
        )

        # Notify assigned recruiter
        if candidate_process.assigned_recruiter_id:
            notifications.append(
                {
                    "user_id": candidate_process.assigned_recruiter_id,
                    "type": "candidate_process_completed",
                    "title": "Candidate Process Completed",
                    "message": f"Process completed for candidate in '{candidate_process.process.name}' with result: {candidate_process.final_result}",
                    "data": {
                        "candidate_process_id": candidate_process.id,
                        "candidate_id": candidate_process.candidate_id,
                        "process_id": candidate_process.workflow_id,
                        "process_name": candidate_process.process.name,
                        "final_result": candidate_process.final_result,
                        "overall_score": candidate_process.overall_score,
                    },
                }
            )

        await self._send_notifications(db, notifications)

    async def notify_deadline_approaching(
        self,
        db: AsyncSession,
        execution: WorkflowNodeExecution,
        node: WorkflowNode,
        candidate_process: CandidateWorkflow,
        hours_remaining: int,
    ) -> None:
        """Send notification when deadline is approaching"""
        notifications = []

        # Notify assignee
        if execution.assigned_to:
            notifications.append(
                {
                    "user_id": execution.assigned_to,
                    "type": "deadline_approaching",
                    "title": f"Deadline Approaching: {node.title}",
                    "message": f"Task '{node.title}' is due in {hours_remaining} hours",
                    "data": {
                        "execution_id": execution.id,
                        "node_id": node.id,
                        "node_title": node.title,
                        "due_date": execution.due_date.isoformat()
                        if execution.due_date
                        else None,
                        "hours_remaining": hours_remaining,
                        "candidate_process_id": candidate_process.id,
                        "process_name": candidate_process.process.name,
                    },
                }
            )

        # Notify candidate if it's their task
        if (
            node.node_type in ["todo", "assessment"]
            and candidate_process.candidate_id != execution.assigned_to
        ):
            notifications.append(
                {
                    "user_id": candidate_process.candidate_id,
                    "type": "submission_deadline_approaching",
                    "title": f"Submission Due Soon: {node.title}",
                    "message": f"Your submission for '{node.title}' is due in {hours_remaining} hours",
                    "data": {
                        "execution_id": execution.id,
                        "node_id": node.id,
                        "node_title": node.title,
                        "due_date": execution.due_date.isoformat()
                        if execution.due_date
                        else None,
                        "hours_remaining": hours_remaining,
                        "candidate_process_id": candidate_process.id,
                        "process_name": candidate_process.process.name,
                    },
                }
            )

        await self._send_notifications(db, notifications)

    async def notify_task_overdue(
        self,
        db: AsyncSession,
        execution: WorkflowNodeExecution,
        node: WorkflowNode,
        candidate_process: CandidateWorkflow,
    ) -> None:
        """Send notification when a task becomes overdue"""
        notifications = []

        # Notify assignee
        if execution.assigned_to:
            notifications.append(
                {
                    "user_id": execution.assigned_to,
                    "type": "task_overdue",
                    "title": f"Overdue Task: {node.title}",
                    "message": f"Task '{node.title}' is now overdue",
                    "data": {
                        "execution_id": execution.id,
                        "node_id": node.id,
                        "node_title": node.title,
                        "due_date": execution.due_date.isoformat()
                        if execution.due_date
                        else None,
                        "candidate_process_id": candidate_process.id,
                        "process_name": candidate_process.process.name,
                    },
                }
            )

        # Notify assigned recruiter if different from assignee
        if (
            candidate_process.assigned_recruiter_id
            and candidate_process.assigned_recruiter_id != execution.assigned_to
        ):
            notifications.append(
                {
                    "user_id": candidate_process.assigned_recruiter_id,
                    "type": "candidate_task_overdue",
                    "title": "Candidate Task Overdue",
                    "message": f"Task '{node.title}' is overdue for candidate in '{candidate_process.process.name}'",
                    "data": {
                        "execution_id": execution.id,
                        "node_id": node.id,
                        "node_title": node.title,
                        "candidate_process_id": candidate_process.id,
                        "candidate_id": candidate_process.candidate_id,
                        "process_name": candidate_process.process.name,
                    },
                }
            )

        await self._send_notifications(db, notifications)

    async def notify_interview_scheduled(
        self,
        db: AsyncSession,
        execution: WorkflowNodeExecution,
        interview_data: dict[str, Any],
        candidate_process: CandidateWorkflow,
    ) -> None:
        """Send notification when an interview is scheduled"""
        notifications = []

        # Notify candidate
        notifications.append(
            {
                "user_id": candidate_process.candidate_id,
                "type": "interview_scheduled",
                "title": "Interview Scheduled",
                "message": f"Your interview '{interview_data['title']}' has been scheduled",
                "data": {
                    "execution_id": execution.id,
                    "interview_id": execution.interview_id,
                    "interview_title": interview_data["title"],
                    "scheduled_start": interview_data.get("scheduled_start"),
                    "meeting_url": interview_data.get("meeting_url"),
                    "location": interview_data.get("location"),
                    "candidate_process_id": candidate_process.id,
                    "process_name": candidate_process.process.name,
                },
            }
        )

        # Notify interviewer/recruiter
        if (
            execution.assigned_to
            and execution.assigned_to != candidate_process.candidate_id
        ):
            notifications.append(
                {
                    "user_id": execution.assigned_to,
                    "type": "interview_assigned",
                    "title": "Interview Assigned",
                    "message": f"You have been assigned to conduct interview: {interview_data['title']}",
                    "data": {
                        "execution_id": execution.id,
                        "interview_id": execution.interview_id,
                        "interview_title": interview_data["title"],
                        "candidate_id": candidate_process.candidate_id,
                        "scheduled_start": interview_data.get("scheduled_start"),
                        "candidate_process_id": candidate_process.id,
                        "process_name": candidate_process.process.name,
                    },
                }
            )

        await self._send_notifications(db, notifications)

    async def get_user_notifications(
        self,
        db: AsyncSession,
        user_id: int,
        notification_type: str | None = None,
        unread_only: bool = False,
        limit: int = 50,
    ) -> list[dict[str, Any]]:
        """Get notifications for a user (placeholder - would integrate with notification system)"""
        # This would typically query a notifications table
        # For now, return empty list as placeholder
        return []

    async def mark_notification_read(
        self, db: AsyncSession, notification_id: int, user_id: int
    ) -> bool:
        """Mark a notification as read (placeholder)"""
        # This would typically update a notifications table
        return True

    async def _send_notifications(
        self, db: AsyncSession, notifications: list[dict[str, Any]]
    ) -> None:
        """Send notifications (placeholder - would integrate with notification system)"""
        # This would typically:
        # 1. Store notifications in database
        # 2. Send email notifications
        # 3. Send push notifications
        # 4. Update in-app notification counts

        # For now, just log the notifications
        for notification in notifications:
            print(
                f"NOTIFICATION: {notification['type']} to user {notification['user_id']}: {notification['message']}"
            )

    async def get_notification_preferences(
        self, db: AsyncSession, user_id: int
    ) -> dict[str, Any]:
        """Get user notification preferences"""
        # This would typically query user preferences
        # Return default preferences for now
        return {
            "email_notifications": True,
            "push_notifications": True,
            "sms_notifications": False,
            "frequency": "immediate",
            "types": {
                "process_activated": True,
                "candidate_assigned": True,
                "node_assigned": True,
                "deadline_approaching": True,
                "task_overdue": True,
                "process_completed": True,
            },
        }

    async def update_notification_preferences(
        self, db: AsyncSession, user_id: int, preferences: dict[str, Any]
    ) -> dict[str, Any]:
        """Update user notification preferences"""
        # This would typically update user preferences in database
        return preferences


notification_service = RecruitmentWorkflowNotificationService()
