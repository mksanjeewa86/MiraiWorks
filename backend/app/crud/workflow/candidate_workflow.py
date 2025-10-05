from datetime import datetime
from typing import Any

from sqlalchemy import and_, desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.crud.base import CRUDBase
from app.models.candidate_workflow import CandidateWorkflow
from app.models.workflow_node_execution import WorkflowNodeExecution


class CRUDCandidateWorkflow(CRUDBase[CandidateWorkflow, dict, dict]):
    async def create(
        self, db: AsyncSession, *, obj_in: dict[str, Any]
    ) -> CandidateWorkflow:
        """Create a new candidate process"""
        db_obj = CandidateWorkflow(**obj_in)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def get_by_candidate_and_workflow(
        self, db: AsyncSession, *, candidate_id: int, workflow_id: int
    ) -> CandidateWorkflow | None:
        """Get candidate process by candidate and workflow IDs"""
        result = await db.execute(
            select(CandidateWorkflow).where(
                and_(
                    CandidateWorkflow.candidate_id == candidate_id,
                    CandidateWorkflow.workflow_id == workflow_id,
                )
            )
        )
        return result.scalars().first()

    async def get_by_workflow_id(
        self,
        db: AsyncSession,
        *,
        workflow_id: int,
        status: str | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[CandidateWorkflow]:
        """Get all candidate workflows for a workflow"""
        conditions = [CandidateWorkflow.workflow_id == workflow_id]

        if status:
            conditions.append(CandidateWorkflow.status == status)

        result = await db.execute(
            select(CandidateWorkflow)
            .options(
                selectinload(CandidateWorkflow.candidate),
                selectinload(CandidateWorkflow.assigned_recruiter),
                selectinload(CandidateWorkflow.executions),
            )
            .where(and_(*conditions))
            .order_by(desc(CandidateWorkflow.created_at))
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def get_by_candidate_id(
        self,
        db: AsyncSession,
        *,
        candidate_id: int,
        status: str | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[CandidateWorkflow]:
        """Get all processes for a candidate"""
        conditions = [CandidateWorkflow.candidate_id == candidate_id]

        if status:
            conditions.append(CandidateWorkflow.status == status)

        result = await db.execute(
            select(CandidateWorkflow)
            .options(
                selectinload(CandidateWorkflow.process),
                selectinload(CandidateWorkflow.assigned_recruiter),
                selectinload(CandidateWorkflow.executions),
            )
            .where(and_(*conditions))
            .order_by(desc(CandidateWorkflow.created_at))
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def get_by_recruiter_id(
        self,
        db: AsyncSession,
        *,
        recruiter_id: int,
        status: str | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[CandidateWorkflow]:
        """Get all candidate workflows assigned to a recruiter"""
        conditions = [CandidateWorkflow.assigned_recruiter_id == recruiter_id]

        if status:
            conditions.append(CandidateWorkflow.status == status)

        result = await db.execute(
            select(CandidateWorkflow)
            .options(
                selectinload(CandidateWorkflow.candidate),
                selectinload(CandidateWorkflow.process),
                selectinload(CandidateWorkflow.executions),
            )
            .where(and_(*conditions))
            .order_by(desc(CandidateWorkflow.updated_at))
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def get_with_details(
        self, db: AsyncSession, *, id: int
    ) -> CandidateWorkflow | None:
        """Get candidate process with full details"""
        result = await db.execute(
            select(CandidateWorkflow)
            .options(
                selectinload(CandidateWorkflow.candidate),
                selectinload(CandidateWorkflow.process),
                selectinload(CandidateWorkflow.current_node),
                selectinload(CandidateWorkflow.assigned_recruiter),
                selectinload(CandidateWorkflow.executions).selectinload(
                    WorkflowNodeExecution.node
                ),
            )
            .where(CandidateWorkflow.id == id)
        )
        return result.scalars().first()

    async def assign_recruiter(
        self,
        db: AsyncSession,
        *,
        candidate_workflow: CandidateWorkflow,
        recruiter_id: int,
    ) -> CandidateWorkflow:
        """Assign a recruiter to a candidate process"""
        candidate_workflow.assign_recruiter(recruiter_id)
        await db.commit()
        await db.refresh(candidate_workflow)
        return candidate_workflow

    async def start_workflow(
        self,
        db: AsyncSession,
        *,
        candidate_workflow: CandidateWorkflow,
        first_node_id: int,
    ) -> CandidateWorkflow:
        """Start a candidate workflow"""
        candidate_workflow.start(first_node_id)
        await db.commit()
        await db.refresh(candidate_workflow)
        return candidate_workflow

    async def advance_to_node(
        self,
        db: AsyncSession,
        *,
        candidate_workflow: CandidateWorkflow,
        next_node_id: int | None,
    ) -> CandidateWorkflow:
        """Advance candidate to next node"""
        candidate_workflow.advance_to_node(next_node_id)
        await db.commit()
        await db.refresh(candidate_workflow)
        return candidate_workflow

    async def complete_workflow(
        self,
        db: AsyncSession,
        *,
        candidate_workflow: CandidateWorkflow,
        final_result: str,
        overall_score: float | None = None,
        notes: str | None = None,
    ) -> CandidateWorkflow:
        """Complete a candidate workflow"""
        candidate_workflow.complete(final_result, overall_score, notes)
        await db.commit()
        await db.refresh(candidate_workflow)
        return candidate_workflow

    async def fail_workflow(
        self,
        db: AsyncSession,
        *,
        candidate_workflow: CandidateWorkflow,
        reason: str | None = None,
        failed_at_node_id: int | None = None,
    ) -> CandidateWorkflow:
        """Fail a candidate workflow"""
        candidate_workflow.fail(reason, failed_at_node_id)
        await db.commit()
        await db.refresh(candidate_workflow)
        return candidate_workflow

    async def withdraw_workflow(
        self,
        db: AsyncSession,
        *,
        candidate_workflow: CandidateWorkflow,
        reason: str | None = None,
    ) -> CandidateWorkflow:
        """Withdraw a candidate from the workflow"""
        candidate_workflow.withdraw(reason)
        await db.commit()
        await db.refresh(candidate_workflow)
        return candidate_workflow

    async def put_on_hold(
        self, db: AsyncSession, *, candidate_workflow: CandidateWorkflow
    ) -> CandidateWorkflow:
        """Put candidate process on hold"""
        candidate_workflow.put_on_hold()
        await db.commit()
        await db.refresh(candidate_workflow)
        return candidate_workflow

    async def resume_workflow(
        self, db: AsyncSession, *, candidate_workflow: CandidateWorkflow
    ) -> CandidateWorkflow:
        """Resume a candidate workflow from hold"""
        candidate_workflow.resume()
        await db.commit()
        await db.refresh(candidate_workflow)
        return candidate_workflow

    async def bulk_assign_candidates(
        self,
        db: AsyncSession,
        *,
        workflow_id: int,
        candidate_ids: list[int],
        assigned_recruiter_id: int | None = None,
    ) -> list[CandidateWorkflow]:
        """Bulk assign candidates to a process"""
        candidate_workflows = []

        for candidate_id in candidate_ids:
            # Check if already exists
            existing = await self.get_by_candidate_and_workflow(
                db, candidate_id=candidate_id, workflow_id=workflow_id
            )

            if not existing:
                candidate_workflow_data = {
                    "candidate_id": candidate_id,
                    "workflow_id": workflow_id,
                    "assigned_recruiter_id": assigned_recruiter_id,
                    "assigned_at": datetime.utcnow() if assigned_recruiter_id else None,
                }

                candidate_workflow = CandidateWorkflow(**candidate_workflow_data)
                db.add(candidate_workflow)
                candidate_workflows.append(candidate_workflow)

        if candidate_workflows:
            await db.commit()
            for cp in candidate_workflows:
                await db.refresh(cp)

        return candidate_workflows

    async def get_timeline(
        self, db: AsyncSession, *, candidate_workflow_id: int
    ) -> list[dict[str, Any]]:
        """Get timeline for a candidate process"""
        candidate_workflow = await self.get_with_details(db, id=candidate_workflow_id)
        if not candidate_workflow:
            return []

        timeline = []

        # Add process start event
        if candidate_workflow.started_at:
            timeline.append(
                {
                    "timestamp": candidate_workflow.started_at,
                    "event_type": "process_started",
                    "title": "Process Started",
                    "description": f"Started workflow: {candidate_workflow.process.name}",
                    "icon": "play",
                }
            )

        # Add execution events
        for execution in sorted(
            candidate_workflow.executions, key=lambda x: x.created_at
        ):
            # Node started
            if execution.started_at:
                timeline.append(
                    {
                        "timestamp": execution.started_at,
                        "event_type": "node_started",
                        "node_id": execution.node_id,
                        "title": f"Started: {execution.node.title}",
                        "description": f"Started {execution.node.node_type}: {execution.node.title}",
                        "icon": "play-circle",
                    }
                )

            # Node completed
            if execution.completed_at:
                timeline.append(
                    {
                        "timestamp": execution.completed_at,
                        "event_type": "node_completed",
                        "node_id": execution.node_id,
                        "title": f"Completed: {execution.node.title}",
                        "description": f"Completed with result: {execution.result}",
                        "result": execution.result,
                        "score": execution.score,
                        "feedback": execution.feedback,
                        "icon": "check-circle"
                        if execution.result in ["pass", "approved"]
                        else "x-circle",
                    }
                )

        # Add process completion event
        if candidate_workflow.completed_at:
            timeline.append(
                {
                    "timestamp": candidate_workflow.completed_at,
                    "event_type": "process_completed",
                    "title": "Process Completed",
                    "description": f"Process completed with result: {candidate_workflow.final_result}",
                    "result": candidate_workflow.final_result,
                    "score": candidate_workflow.overall_score,
                    "icon": "flag",
                }
            )

        # Sort by timestamp
        return sorted(timeline, key=lambda x: x["timestamp"])

    async def get_statistics_by_workflow(
        self, db: AsyncSession, *, workflow_id: int
    ) -> dict[str, Any]:
        """Get statistics for candidate workflows in a specific workflow"""
        # Count candidates by status
        status_counts = await db.execute(
            select(
                CandidateWorkflow.status,
                func.count(CandidateWorkflow.id).label("count"),
            )
            .where(CandidateWorkflow.workflow_id == workflow_id)
            .group_by(CandidateWorkflow.status)
        )

        status_dict = {row.status: row.count for row in status_counts}

        # Calculate completion rate
        total_candidates = sum(status_dict.values())
        completed_candidates = status_dict.get("completed", 0)
        completion_rate = (
            (completed_candidates / total_candidates * 100)
            if total_candidates > 0
            else 0
        )

        # Calculate average duration
        avg_duration_result = await db.execute(
            select(
                func.avg(
                    func.extract(
                        "epoch",
                        CandidateWorkflow.completed_at - CandidateWorkflow.started_at,
                    )
                    / 86400
                )
            ).where(
                and_(
                    CandidateWorkflow.workflow_id == workflow_id,
                    CandidateWorkflow.status == "completed",
                    CandidateWorkflow.started_at.isnot(None),
                    CandidateWorkflow.completed_at.isnot(None),
                )
            )
        )

        avg_duration = avg_duration_result.scalar() or 0

        return {
            "total_candidates": total_candidates,
            "by_status": status_dict,
            "completion_rate": completion_rate,
            "average_duration_days": avg_duration,
        }

    async def get_recruiter_workload(
        self, db: AsyncSession, *, recruiter_id: int
    ) -> dict[str, Any]:
        """Get workload statistics for a recruiter"""
        # Count active processes
        active_count = await db.execute(
            select(func.count(CandidateWorkflow.id)).where(
                and_(
                    CandidateWorkflow.assigned_recruiter_id == recruiter_id,
                    CandidateWorkflow.status == "in_progress",
                )
            )
        )

        # Count pending tasks (executions)
        pending_tasks = await db.execute(
            select(func.count(WorkflowNodeExecution.id))
            .join(CandidateWorkflow)
            .where(
                and_(
                    CandidateWorkflow.assigned_recruiter_id == recruiter_id,
                    WorkflowNodeExecution.status.in_(
                        ["pending", "scheduled", "in_progress"]
                    ),
                )
            )
        )

        # Count overdue tasks
        overdue_tasks = await db.execute(
            select(func.count(WorkflowNodeExecution.id))
            .join(CandidateWorkflow)
            .where(
                and_(
                    CandidateWorkflow.assigned_recruiter_id == recruiter_id,
                    WorkflowNodeExecution.status.in_(
                        ["pending", "scheduled", "in_progress"]
                    ),
                    WorkflowNodeExecution.due_date < datetime.utcnow(),
                )
            )
        )

        # Calculate completion rate
        total_executions = await db.execute(
            select(func.count(WorkflowNodeExecution.id))
            .join(CandidateWorkflow)
            .where(CandidateWorkflow.assigned_recruiter_id == recruiter_id)
        )

        completed_executions = await db.execute(
            select(func.count(WorkflowNodeExecution.id))
            .join(CandidateWorkflow)
            .where(
                and_(
                    CandidateWorkflow.assigned_recruiter_id == recruiter_id,
                    WorkflowNodeExecution.status == "completed",
                )
            )
        )

        total_count = total_executions.scalar() or 0
        completed_count = completed_executions.scalar() or 0
        completion_rate = (
            (completed_count / total_count * 100) if total_count > 0 else 0
        )

        return {
            "recruiter_id": recruiter_id,
            "active_processes": active_count.scalar() or 0,
            "pending_tasks": pending_tasks.scalar() or 0,
            "overdue_tasks": overdue_tasks.scalar() or 0,
            "completion_rate": completion_rate,
            "total_executions": total_count,
            "completed_executions": completed_count,
        }


candidate_workflow = CRUDCandidateWorkflow(CandidateWorkflow)
