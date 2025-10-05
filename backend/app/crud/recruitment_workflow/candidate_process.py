from datetime import datetime
from typing import Any

from sqlalchemy import and_, desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.crud.base import CRUDBase
from app.models.candidate_process import CandidateProcess
from app.models.node_execution import NodeExecution


class CRUDCandidateProcess(CRUDBase[CandidateProcess, dict, dict]):
    async def create(
        self, db: AsyncSession, *, obj_in: dict[str, Any]
    ) -> CandidateProcess:
        """Create a new candidate process"""
        db_obj = CandidateProcess(**obj_in)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def get_by_candidate_and_process(
        self, db: AsyncSession, *, candidate_id: int, workflow_id: int
    ) -> CandidateProcess | None:
        """Get candidate process by candidate and process IDs"""
        result = await db.execute(
            select(CandidateProcess).where(
                and_(
                    CandidateProcess.candidate_id == candidate_id,
                    CandidateProcess.workflow_id == workflow_id,
                )
            )
        )
        return result.scalars().first()

    async def get_by_process_id(
        self,
        db: AsyncSession,
        *,
        workflow_id: int,
        status: str | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[CandidateProcess]:
        """Get all candidate processes for a recruitment process"""
        conditions = [CandidateProcess.workflow_id == process_id]

        if status:
            conditions.append(CandidateProcess.status == status)

        result = await db.execute(
            select(CandidateProcess)
            .options(
                selectinload(CandidateProcess.candidate),
                selectinload(CandidateProcess.assigned_recruiter),
                selectinload(CandidateProcess.executions),
            )
            .where(and_(*conditions))
            .order_by(desc(CandidateProcess.created_at))
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
    ) -> list[CandidateProcess]:
        """Get all processes for a candidate"""
        conditions = [CandidateProcess.candidate_id == candidate_id]

        if status:
            conditions.append(CandidateProcess.status == status)

        result = await db.execute(
            select(CandidateProcess)
            .options(
                selectinload(CandidateProcess.process),
                selectinload(CandidateProcess.assigned_recruiter),
                selectinload(CandidateProcess.executions),
            )
            .where(and_(*conditions))
            .order_by(desc(CandidateProcess.created_at))
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
    ) -> list[CandidateProcess]:
        """Get all candidate processes assigned to a recruiter"""
        conditions = [CandidateProcess.assigned_recruiter_id == recruiter_id]

        if status:
            conditions.append(CandidateProcess.status == status)

        result = await db.execute(
            select(CandidateProcess)
            .options(
                selectinload(CandidateProcess.candidate),
                selectinload(CandidateProcess.process),
                selectinload(CandidateProcess.executions),
            )
            .where(and_(*conditions))
            .order_by(desc(CandidateProcess.updated_at))
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def get_with_details(
        self, db: AsyncSession, *, id: int
    ) -> CandidateProcess | None:
        """Get candidate process with full details"""
        result = await db.execute(
            select(CandidateProcess)
            .options(
                selectinload(CandidateProcess.candidate),
                selectinload(CandidateProcess.process),
                selectinload(CandidateProcess.current_node),
                selectinload(CandidateProcess.assigned_recruiter),
                selectinload(CandidateProcess.executions).selectinload(
                    NodeExecution.node
                ),
            )
            .where(CandidateProcess.id == id)
        )
        return result.scalars().first()

    async def assign_recruiter(
        self,
        db: AsyncSession,
        *,
        candidate_process: CandidateProcess,
        recruiter_id: int,
    ) -> CandidateProcess:
        """Assign a recruiter to a candidate process"""
        candidate_process.assign_recruiter(recruiter_id)
        await db.commit()
        await db.refresh(candidate_process)
        return candidate_process

    async def start_process(
        self,
        db: AsyncSession,
        *,
        candidate_process: CandidateProcess,
        first_node_id: int,
    ) -> CandidateProcess:
        """Start a candidate process"""
        candidate_process.start(first_node_id)
        await db.commit()
        await db.refresh(candidate_process)
        return candidate_process

    async def advance_to_node(
        self,
        db: AsyncSession,
        *,
        candidate_process: CandidateProcess,
        next_node_id: int | None,
    ) -> CandidateProcess:
        """Advance candidate to next node"""
        candidate_process.advance_to_node(next_node_id)
        await db.commit()
        await db.refresh(candidate_process)
        return candidate_process

    async def complete_process(
        self,
        db: AsyncSession,
        *,
        candidate_process: CandidateProcess,
        final_result: str,
        overall_score: float | None = None,
        notes: str | None = None,
    ) -> CandidateProcess:
        """Complete a candidate process"""
        candidate_process.complete(final_result, overall_score, notes)
        await db.commit()
        await db.refresh(candidate_process)
        return candidate_process

    async def fail_process(
        self,
        db: AsyncSession,
        *,
        candidate_process: CandidateProcess,
        reason: str | None = None,
        failed_at_node_id: int | None = None,
    ) -> CandidateProcess:
        """Fail a candidate process"""
        candidate_process.fail(reason, failed_at_node_id)
        await db.commit()
        await db.refresh(candidate_process)
        return candidate_process

    async def withdraw_process(
        self,
        db: AsyncSession,
        *,
        candidate_process: CandidateProcess,
        reason: str | None = None,
    ) -> CandidateProcess:
        """Withdraw a candidate from the process"""
        candidate_process.withdraw(reason)
        await db.commit()
        await db.refresh(candidate_process)
        return candidate_process

    async def put_on_hold(
        self, db: AsyncSession, *, candidate_process: CandidateProcess
    ) -> CandidateProcess:
        """Put candidate process on hold"""
        candidate_process.put_on_hold()
        await db.commit()
        await db.refresh(candidate_process)
        return candidate_process

    async def resume_process(
        self, db: AsyncSession, *, candidate_process: CandidateProcess
    ) -> CandidateProcess:
        """Resume a candidate process from hold"""
        candidate_process.resume()
        await db.commit()
        await db.refresh(candidate_process)
        return candidate_process

    async def bulk_assign_candidates(
        self,
        db: AsyncSession,
        *,
        workflow_id: int,
        candidate_ids: list[int],
        assigned_recruiter_id: int | None = None,
    ) -> list[CandidateProcess]:
        """Bulk assign candidates to a process"""
        candidate_workflows = []

        for candidate_id in candidate_ids:
            # Check if already exists
            existing = await self.get_by_candidate_and_process(
                db, candidate_id=candidate_id, process_id=process_id
            )

            if not existing:
                candidate_process_data = {
                    "candidate_id": candidate_id,
                    "process_id": workflow_id,
                    "assigned_recruiter_id": assigned_recruiter_id,
                    "assigned_at": datetime.utcnow() if assigned_recruiter_id else None,
                }

                candidate_process = CandidateProcess(**candidate_process_data)
                db.add(candidate_process)
                candidate_workflows.append(candidate_process)

        if candidate_workflows:
            await db.commit()
            for cp in candidate_workflows:
                await db.refresh(cp)

        return candidate_workflows

    async def get_timeline(
        self, db: AsyncSession, *, candidate_workflow_id: int
    ) -> list[dict[str, Any]]:
        """Get timeline for a candidate process"""
        candidate_process = await self.get_with_details(db, id=candidate_process_id)
        if not candidate_process:
            return []

        timeline = []

        # Add process start event
        if candidate_process.started_at:
            timeline.append(
                {
                    "timestamp": candidate_process.started_at,
                    "event_type": "process_started",
                    "title": "Process Started",
                    "description": f"Started recruitment process: {candidate_process.process.name}",
                    "icon": "play",
                }
            )

        # Add execution events
        for execution in sorted(
            candidate_process.executions, key=lambda x: x.created_at
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
        if candidate_process.completed_at:
            timeline.append(
                {
                    "timestamp": candidate_process.completed_at,
                    "event_type": "process_completed",
                    "title": "Process Completed",
                    "description": f"Process completed with result: {candidate_process.final_result}",
                    "result": candidate_process.final_result,
                    "score": candidate_process.overall_score,
                    "icon": "flag",
                }
            )

        # Sort by timestamp
        return sorted(timeline, key=lambda x: x["timestamp"])

    async def get_statistics_by_process(
        self, db: AsyncSession, *, workflow_id: int
    ) -> dict[str, Any]:
        """Get statistics for candidate processes in a specific recruitment process"""
        # Count candidates by status
        status_counts = await db.execute(
            select(
                CandidateProcess.status, func.count(CandidateProcess.id).label("count")
            )
            .where(CandidateProcess.workflow_id == process_id)
            .group_by(CandidateProcess.status)
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
                        CandidateProcess.completed_at - CandidateProcess.started_at,
                    )
                    / 86400
                )
            ).where(
                and_(
                    CandidateProcess.workflow_id == workflow_id,
                    CandidateProcess.status == "completed",
                    CandidateProcess.started_at.isnot(None),
                    CandidateProcess.completed_at.isnot(None),
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
            select(func.count(CandidateProcess.id)).where(
                and_(
                    CandidateProcess.assigned_recruiter_id == recruiter_id,
                    CandidateProcess.status == "in_progress",
                )
            )
        )

        # Count pending tasks (executions)
        pending_tasks = await db.execute(
            select(func.count(NodeExecution.id))
            .join(CandidateProcess)
            .where(
                and_(
                    CandidateProcess.assigned_recruiter_id == recruiter_id,
                    NodeExecution.status.in_(["pending", "scheduled", "in_progress"]),
                )
            )
        )

        # Count overdue tasks
        overdue_tasks = await db.execute(
            select(func.count(NodeExecution.id))
            .join(CandidateProcess)
            .where(
                and_(
                    CandidateProcess.assigned_recruiter_id == recruiter_id,
                    NodeExecution.status.in_(["pending", "scheduled", "in_progress"]),
                    NodeExecution.due_date < datetime.utcnow(),
                )
            )
        )

        # Calculate completion rate
        total_executions = await db.execute(
            select(func.count(NodeExecution.id))
            .join(CandidateProcess)
            .where(CandidateProcess.assigned_recruiter_id == recruiter_id)
        )

        completed_executions = await db.execute(
            select(func.count(NodeExecution.id))
            .join(CandidateProcess)
            .where(
                and_(
                    CandidateProcess.assigned_recruiter_id == recruiter_id,
                    NodeExecution.status == "completed",
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


candidate_process = CRUDCandidateProcess(CandidateProcess)
