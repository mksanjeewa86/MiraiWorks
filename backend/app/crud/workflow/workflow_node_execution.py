from datetime import datetime
from typing import Any

from sqlalchemy import and_, asc, desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.crud.base import CRUDBase
from app.models.candidate_workflow import CandidateWorkflow
from app.models.workflow_workflow_node_execution import WorkflowNodeExecution


class CRUDWorkflowNodeExecution(CRUDBase[WorkflowNodeExecution, dict, dict]):
    async def create(
        self, db: AsyncSession, *, obj_in: dict[str, Any]
    ) -> WorkflowNodeExecution:
        """Create a new node execution"""
        db_obj = WorkflowNodeExecution(**obj_in)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def get_by_candidate_workflow_and_node(
        self, db: AsyncSession, *, candidate_workflow_id: int, node_id: int
    ) -> WorkflowNodeExecution | None:
        """Get execution by candidate process and node"""
        result = await db.execute(
            select(WorkflowNodeExecution).where(
                and_(
                    WorkflowNodeExecution.candidate_workflow_id == candidate_workflow_id,
                    WorkflowNodeExecution.node_id == node_id,
                )
            )
        )
        return result.scalars().first()

    async def get_by_candidate_workflow_id(
        self, db: AsyncSession, *, candidate_workflow_id: int, status: str | None = None
    ) -> list[WorkflowNodeExecution]:
        """Get all executions for a candidate process"""
        conditions = [WorkflowNodeExecution.candidate_workflow_id == candidate_workflow_id]

        if status:
            conditions.append(WorkflowNodeExecution.status == status)

        result = await db.execute(
            select(WorkflowNodeExecution)
            .options(selectinload(WorkflowNodeExecution.node))
            .where(and_(*conditions))
            .order_by(asc(WorkflowNodeExecution.node.sequence_order))
        )
        return result.scalars().all()

    async def get_by_node_id(
        self,
        db: AsyncSession,
        *,
        node_id: int,
        status: str | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[WorkflowNodeExecution]:
        """Get all executions for a specific node"""
        conditions = [WorkflowNodeExecution.node_id == node_id]

        if status:
            conditions.append(WorkflowNodeExecution.status == status)

        result = await db.execute(
            select(WorkflowNodeExecution)
            .options(
                selectinload(WorkflowNodeExecution.candidate_workflow).selectinload(
                    CandidateWorkflow.candidate
                ),
                selectinload(WorkflowNodeExecution.assignee),
            )
            .where(and_(*conditions))
            .order_by(desc(WorkflowNodeExecution.created_at))
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def get_assigned_to_user(
        self,
        db: AsyncSession,
        *,
        user_id: int,
        status: str | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[WorkflowNodeExecution]:
        """Get executions assigned to a specific user"""
        conditions = [WorkflowNodeExecution.assigned_to == user_id]

        if status:
            conditions.append(WorkflowNodeExecution.status == status)

        result = await db.execute(
            select(WorkflowNodeExecution)
            .options(
                selectinload(WorkflowNodeExecution.node),
                selectinload(WorkflowNodeExecution.candidate_workflow).selectinload(
                    CandidateWorkflow.candidate
                ),
            )
            .where(and_(*conditions))
            .order_by(asc(WorkflowNodeExecution.due_date))
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def get_overdue_executions(
        self, db: AsyncSession, *, assigned_to: int | None = None, limit: int = 100
    ) -> list[WorkflowNodeExecution]:
        """Get overdue executions"""
        conditions = [
            WorkflowNodeExecution.due_date < datetime.utcnow(),
            WorkflowNodeExecution.status.in_(["pending", "scheduled", "in_progress"]),
        ]

        if assigned_to:
            conditions.append(WorkflowNodeExecution.assigned_to == assigned_to)

        result = await db.execute(
            select(WorkflowNodeExecution)
            .options(
                selectinload(WorkflowNodeExecution.node),
                selectinload(WorkflowNodeExecution.candidate_workflow).selectinload(
                    CandidateWorkflow.candidate
                ),
                selectinload(WorkflowNodeExecution.assignee),
            )
            .where(and_(*conditions))
            .order_by(asc(WorkflowNodeExecution.due_date))
            .limit(limit)
        )
        return result.scalars().all()

    async def get_with_details(
        self, db: AsyncSession, *, id: int
    ) -> WorkflowNodeExecution | None:
        """Get execution with full details"""
        result = await db.execute(
            select(WorkflowNodeExecution)
            .options(
                selectinload(WorkflowNodeExecution.node),
                selectinload(WorkflowNodeExecution.candidate_workflow).selectinload(
                    CandidateWorkflow.candidate
                ),
                selectinload(WorkflowNodeExecution.candidate_workflow).selectinload(
                    CandidateWorkflow.process
                ),
                selectinload(WorkflowNodeExecution.assignee),
                selectinload(WorkflowNodeExecution.completer),
                selectinload(WorkflowNodeExecution.reviewer),
                selectinload(WorkflowNodeExecution.interview),
                selectinload(WorkflowNodeExecution.todo),
            )
            .where(WorkflowNodeExecution.id == id)
        )
        return result.scalars().first()

    async def start_execution(
        self,
        db: AsyncSession,
        *,
        execution: WorkflowNodeExecution,
        assigned_to: int | None = None,
    ) -> WorkflowNodeExecution:
        """Start an execution"""
        execution.start(assigned_to)
        await db.commit()
        await db.refresh(execution)
        return execution

    async def complete_execution(
        self,
        db: AsyncSession,
        *,
        execution: WorkflowNodeExecution,
        result: str,
        completed_by: int,
        score: float | None = None,
        feedback: str | None = None,
        execution_data: dict[str, Any] | None = None,
    ) -> WorkflowNodeExecution:
        """Complete an execution"""
        execution.complete(result, completed_by, score, feedback, execution_data)
        await db.commit()
        await db.refresh(execution)
        return execution

    async def fail_execution(
        self,
        db: AsyncSession,
        *,
        execution: WorkflowNodeExecution,
        completed_by: int,
        reason: str | None = None,
    ) -> WorkflowNodeExecution:
        """Fail an execution"""
        execution.fail(completed_by, reason)
        await db.commit()
        await db.refresh(execution)
        return execution

    async def skip_execution(
        self,
        db: AsyncSession,
        *,
        execution: WorkflowNodeExecution,
        completed_by: int,
        reason: str | None = None,
    ) -> WorkflowNodeExecution:
        """Skip an execution"""
        execution.skip(completed_by, reason)
        await db.commit()
        await db.refresh(execution)
        return execution

    async def schedule_execution(
        self, db: AsyncSession, *, execution: WorkflowNodeExecution, due_date: datetime
    ) -> WorkflowNodeExecution:
        """Schedule an execution"""
        execution.schedule(due_date)
        await db.commit()
        await db.refresh(execution)
        return execution

    async def link_interview(
        self, db: AsyncSession, *, execution: WorkflowNodeExecution, interview_id: int
    ) -> WorkflowNodeExecution:
        """Link an interview to an execution"""
        execution.link_interview(interview_id)
        await db.commit()
        await db.refresh(execution)
        return execution

    async def link_todo(
        self, db: AsyncSession, *, execution: WorkflowNodeExecution, todo_id: int
    ) -> WorkflowNodeExecution:
        """Link a todo to an execution"""
        execution.link_todo(todo_id)
        await db.commit()
        await db.refresh(execution)
        return execution

    async def bulk_update_status(
        self,
        db: AsyncSession,
        *,
        execution_ids: list[int],
        status: str,
        assigned_to: int | None = None,
    ) -> list[WorkflowNodeExecution]:
        """Bulk update execution status"""
        executions = await db.execute(
            select(WorkflowNodeExecution).where(WorkflowNodeExecution.id.in_(execution_ids))
        )

        updated_executions = []
        for execution in executions.scalars().all():
            execution.status = status
            if assigned_to is not None:
                execution.assigned_to = assigned_to
            updated_executions.append(execution)

        await db.commit()

        for execution in updated_executions:
            await db.refresh(execution)

        return updated_executions

    async def bulk_complete_executions(
        self, db: AsyncSession, *, completions: list[dict[str, Any]], completed_by: int
    ) -> list[WorkflowNodeExecution]:
        """Bulk complete executions"""
        execution_ids = [c["execution_id"] for c in completions]
        executions = await db.execute(
            select(WorkflowNodeExecution).where(WorkflowNodeExecution.id.in_(execution_ids))
        )

        execution_dict = {e.id: e for e in executions.scalars().all()}
        updated_executions = []

        for completion in completions:
            execution_id = completion["execution_id"]
            execution = execution_dict.get(execution_id)

            if execution:
                execution.complete(
                    result=completion["result"],
                    completed_by=completed_by,
                    score=completion.get("score"),
                    feedback=completion.get("feedback"),
                    execution_data=completion.get("execution_data"),
                )
                updated_executions.append(execution)

        await db.commit()

        for execution in updated_executions:
            await db.refresh(execution)

        return updated_executions

    async def get_execution_statistics(
        self,
        db: AsyncSession,
        *,
        node_id: int | None = None,
        workflow_id: int | None = None,
        candidate_workflow_id: int | None = None,
    ) -> dict[str, Any]:
        """Get execution statistics"""
        conditions = []

        if node_id:
            conditions.append(WorkflowNodeExecution.node_id == node_id)

        if workflow_id:
            conditions.append(
                WorkflowNodeExecution.candidate_workflow.has(process_id=process_id)
            )

        if candidate_workflow_id:
            conditions.append(
                WorkflowNodeExecution.candidate_workflow_id == candidate_workflow_id
            )

        # Count by status
        status_counts = await db.execute(
            select(WorkflowNodeExecution.status, func.count(WorkflowNodeExecution.id).label("count"))
            .where(and_(*conditions) if conditions else True)
            .group_by(WorkflowNodeExecution.status)
        )

        status_dict = {row.status: row.count for row in status_counts}

        # Count by result
        result_counts = await db.execute(
            select(WorkflowNodeExecution.result, func.count(WorkflowNodeExecution.id).label("count"))
            .where(
                and_(*conditions, WorkflowNodeExecution.result.isnot(None))
                if conditions
                else WorkflowNodeExecution.result.isnot(None)
            )
            .group_by(WorkflowNodeExecution.result)
        )

        result_dict = {row.result: row.count for row in result_counts}

        # Calculate averages
        avg_duration_result = await db.execute(
            select(
                func.avg(
                    func.extract(
                        "epoch", WorkflowNodeExecution.completed_at - WorkflowNodeExecution.started_at
                    )
                    / 60
                )
            ).where(
                and_(
                    *conditions,
                    WorkflowNodeExecution.started_at.isnot(None),
                    WorkflowNodeExecution.completed_at.isnot(None),
                )
                if conditions
                else and_(
                    WorkflowNodeExecution.started_at.isnot(None),
                    WorkflowNodeExecution.completed_at.isnot(None),
                )
            )
        )

        avg_score_result = await db.execute(
            select(func.avg(WorkflowNodeExecution.score)).where(
                and_(*conditions, WorkflowNodeExecution.score.isnot(None))
                if conditions
                else WorkflowNodeExecution.score.isnot(None)
            )
        )

        total_executions = sum(status_dict.values())
        completed_executions = status_dict.get("completed", 0)
        completion_rate = (
            (completed_executions / total_executions * 100)
            if total_executions > 0
            else 0
        )

        return {
            "total_executions": total_executions,
            "by_status": status_dict,
            "by_result": result_dict,
            "completion_rate": completion_rate,
            "average_duration_minutes": avg_duration_result.scalar() or 0,
            "average_score": avg_score_result.scalar(),
        }

    async def get_workload_by_assignee(
        self, db: AsyncSession, *, workflow_id: int | None = None
    ) -> list[dict[str, Any]]:
        """Get workload distribution by assignee"""
        conditions = [WorkflowNodeExecution.assigned_to.isnot(None)]

        if workflow_id:
            conditions.append(
                WorkflowNodeExecution.candidate_workflow.has(process_id=process_id)
            )

        result = await db.execute(
            select(
                WorkflowNodeExecution.assigned_to,
                func.count(WorkflowNodeExecution.id).label("total_assigned"),
                func.sum(
                    func.case((WorkflowNodeExecution.status == "pending", 1), else_=0)
                ).label("pending"),
                func.sum(
                    func.case((WorkflowNodeExecution.status == "in_progress", 1), else_=0)
                ).label("in_progress"),
                func.sum(
                    func.case(
                        (
                            and_(
                                WorkflowNodeExecution.due_date < datetime.utcnow(),
                                WorkflowNodeExecution.status.in_(
                                    ["pending", "scheduled", "in_progress"]
                                ),
                            ),
                            1,
                        ),
                        else_=0,
                    )
                ).label("overdue"),
                func.sum(
                    func.case((WorkflowNodeExecution.status == "completed", 1), else_=0)
                ).label("completed"),
                func.avg(
                    func.extract(
                        "epoch", WorkflowNodeExecution.completed_at - WorkflowNodeExecution.started_at
                    )
                    / 3600
                ).label("avg_completion_hours"),
            )
            .where(and_(*conditions))
            .group_by(WorkflowNodeExecution.assigned_to)
            .order_by(desc("total_assigned"))
        )

        workload = []
        for row in result:
            completion_rate = (
                (row.completed / row.total_assigned * 100)
                if row.total_assigned > 0
                else 0
            )

            workload.append(
                {
                    "assignee_id": row.assigned_to,
                    "total_assigned": row.total_assigned,
                    "pending": row.pending or 0,
                    "in_progress": row.in_progress or 0,
                    "overdue": row.overdue or 0,
                    "completed": row.completed or 0,
                    "completion_rate": completion_rate,
                    "average_completion_hours": row.avg_completion_hours or 0,
                    "workload_score": (row.pending or 0)
                    + (row.in_progress or 0) * 1.5
                    + (row.overdue or 0) * 2,
                }
            )

        return workload


workflow_node_execution = CRUDWorkflowNodeExecution(WorkflowNodeExecution)
