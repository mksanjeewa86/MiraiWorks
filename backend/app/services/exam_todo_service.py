"""Exam TODO Service - Orchestrates exam assignments within the workflow system."""

from datetime import datetime
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.exam import exam as exam_crud
from app.crud.exam import exam_assignment as exam_assignment_crud
from app.crud.todo import todo as todo_crud
from app.models.exam import ExamAssignment
from app.models.todo import Todo
from app.models.workflow_node_execution import WorkflowNodeExecution
from app.schemas.exam import ExamAssignmentCreate
from app.services.exam_email_service import exam_email_service
from app.utils.constants import TodoStatus, TodoType


class ExamTodoService:
    """Service for managing exam TODOs within workflows."""

    async def create_exam_todo_from_workflow(
        self,
        db: AsyncSession,
        workflow_node_execution: WorkflowNodeExecution,
        candidate_id: int,
        exam_config: dict[str, Any],
        created_by_id: int,
    ) -> tuple[Todo, ExamAssignment]:
        """
        Create an exam TODO from a workflow node execution.

        Args:
            db: Database session
            workflow_node_execution: The workflow node execution that triggered this exam
            candidate_id: The candidate who should take the exam
            exam_config: Configuration for the exam (contains exam_id or exam selection rules)
            created_by_id: User ID of the workflow creator

        Returns:
            tuple[Todo, ExamAssignment]: The created TODO and exam assignment

        Example exam_config:
            {
                "exam_id": 5,  # Direct exam ID
                "due_date": "2025-01-20T00:00:00Z",  # Optional
                "custom_time_limit_minutes": 60,  # Optional override
                "custom_max_attempts": 2,  # Optional override
            }

        OR for dynamic exam selection:
            {
                "exam_type": "spi",  # Select from available exams
                "exam_name": "SPI Aptitude Test",  # Optional filter
                "due_date": "2025-01-20T00:00:00Z",
            }
        """
        # 1. Resolve exam_id from config
        exam_id = await self._resolve_exam_id(db, exam_config)
        if not exam_id:
            raise ValueError("Could not resolve exam_id from exam_config")

        # Get exam details
        exam = await exam_crud.get(db, id=exam_id)
        if not exam:
            raise ValueError(f"Exam {exam_id} not found")

        # 2. Parse configuration
        due_date = None
        if exam_config.get("due_date"):
            if isinstance(exam_config["due_date"], str):
                due_date = datetime.fromisoformat(
                    exam_config["due_date"].replace("Z", "+00:00")
                )
            else:
                due_date = exam_config["due_date"]

        custom_time_limit = exam_config.get("custom_time_limit_minutes")
        custom_max_attempts = exam_config.get("custom_max_attempts")

        # 3. Create exam assignment
        assignment_data = ExamAssignmentCreate(
            exam_id=exam_id,
            candidate_ids=[candidate_id],
            due_date=due_date,
            custom_time_limit_minutes=custom_time_limit,
            custom_max_attempts=custom_max_attempts,
        )

        assignments = await exam_assignment_crud.create_assignments(
            db=db,
            assignment_data=assignment_data,
            assigned_by_id=created_by_id,
        )

        if not assignments:
            raise ValueError("Failed to create exam assignment")

        exam_assignment = assignments[0]

        # 4. Create TODO
        todo_data = {
            "owner_id": candidate_id,
            "created_by": created_by_id,
            "assignee_id": candidate_id,
            "workflow_id": workflow_node_execution.workflow_id,
            "title": f"Complete Exam: {exam.title}",
            "description": exam.description
            or f"You have been assigned the {exam.title} exam.",
            "status": TodoStatus.PENDING.value,
            "todo_type": TodoType.EXAM.value,
            "due_date": due_date,
            "exam_id": exam_id,
            "exam_assignment_id": exam_assignment.id,
            "exam_config": exam_config,
        }

        todo = await todo_crud.create(db, obj_in=todo_data)

        # 5. Link assignment back to TODO and workflow node execution
        exam_assignment.todo_id = todo.id
        exam_assignment.workflow_node_execution_id = workflow_node_execution.id
        await db.commit()
        await db.refresh(exam_assignment)
        await db.refresh(todo)

        # 6. Send notification email to candidate
        try:
            await exam_email_service.send_exam_assignment_notification(
                db=db,
                exam_assignment_id=exam_assignment.id,
            )
            exam_assignment.notification_sent = True
            await db.commit()
        except Exception as e:
            # Log error but don't fail the TODO creation
            print(f"Failed to send exam notification email: {str(e)}")

        return todo, exam_assignment

    async def _resolve_exam_id(
        self, db: AsyncSession, exam_config: dict[str, Any]
    ) -> int | None:
        """
        Resolve exam_id from exam configuration.

        Supports:
        1. Direct exam_id: {"exam_id": 5}
        2. Dynamic selection: {"exam_type": "spi", "exam_name": "SPI Test"}
        """
        # Direct exam_id
        if "exam_id" in exam_config:
            return exam_config["exam_id"]

        # Dynamic exam selection
        exam_type = exam_config.get("exam_type")
        exam_name = exam_config.get("exam_name")

        if not exam_type:
            return None

        # Find exam by type and optionally by name
        from sqlalchemy import and_, select

        from app.models.exam import Exam
        from app.schemas.exam import ExamStatus

        query = select(Exam).where(
            and_(
                Exam.exam_type == exam_type,
                Exam.status == ExamStatus.ACTIVE,
            )
        )

        if exam_name:
            query = query.where(Exam.title.ilike(f"%{exam_name}%"))

        result = await db.execute(query)
        exam = result.scalar_one_or_none()

        return exam.id if exam else None

    async def on_exam_completed(
        self,
        db: AsyncSession,
        exam_assignment_id: int,
    ) -> None:
        """
        Handle exam completion - auto-complete the TODO and advance workflow.

        This should be called when an exam session is completed.

        Args:
            db: Database session
            exam_assignment_id: The exam assignment that was completed
        """
        # Get exam assignment
        assignment = await exam_assignment_crud.get(db, id=exam_assignment_id)
        if not assignment:
            return

        # Mark assignment as completed
        assignment.completed = True
        await db.commit()

        # If there's a linked TODO, mark it as completed
        if assignment.todo_id:
            todo = await todo_crud.get(db, id=assignment.todo_id)
            if todo and todo.status != TodoStatus.COMPLETED.value:
                todo.mark_completed()
                await db.commit()

                # Trigger workflow progression if needed
                # The workflow engine will automatically advance when it detects the TODO is completed
                # This is handled by the workflow engine's polling or event system


exam_todo_service = ExamTodoService()
