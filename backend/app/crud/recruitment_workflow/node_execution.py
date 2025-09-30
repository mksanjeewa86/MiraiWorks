from typing import Any, Dict, List, Optional
from datetime import datetime

from sqlalchemy import and_, select, func, desc, asc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.crud.base import CRUDBase
from app.models.node_execution import NodeExecution


class CRUDNodeExecution(CRUDBase[NodeExecution, dict, dict]):

    async def create(
        self,
        db: AsyncSession,
        *,
        obj_in: Dict[str, Any]
    ) -> NodeExecution:
        """Create a new node execution"""
        db_obj = NodeExecution(**obj_in)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def get_by_candidate_process_and_node(
        self,
        db: AsyncSession,
        *,
        candidate_process_id: int,
        node_id: int
    ) -> Optional[NodeExecution]:
        """Get execution by candidate process and node"""
        result = await db.execute(
            select(NodeExecution)
            .where(
                and_(
                    NodeExecution.candidate_process_id == candidate_process_id,
                    NodeExecution.node_id == node_id
                )
            )
        )
        return result.scalars().first()

    async def get_by_candidate_process_id(
        self,
        db: AsyncSession,
        *,
        candidate_process_id: int,
        status: Optional[str] = None
    ) -> List[NodeExecution]:
        """Get all executions for a candidate process"""
        conditions = [NodeExecution.candidate_process_id == candidate_process_id]

        if status:
            conditions.append(NodeExecution.status == status)

        result = await db.execute(
            select(NodeExecution)
            .options(selectinload(NodeExecution.node))
            .where(and_(*conditions))
            .order_by(asc(NodeExecution.node.sequence_order))
        )
        return result.scalars().all()

    async def get_by_node_id(
        self,
        db: AsyncSession,
        *,
        node_id: int,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[NodeExecution]:
        """Get all executions for a specific node"""
        conditions = [NodeExecution.node_id == node_id]

        if status:
            conditions.append(NodeExecution.status == status)

        result = await db.execute(
            select(NodeExecution)
            .options(
                selectinload(NodeExecution.candidate_process).selectinload(CandidateProcess.candidate),
                selectinload(NodeExecution.assignee)
            )
            .where(and_(*conditions))
            .order_by(desc(NodeExecution.created_at))
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def get_assigned_to_user(
        self,
        db: AsyncSession,
        *,
        user_id: int,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[NodeExecution]:
        """Get executions assigned to a specific user"""
        conditions = [NodeExecution.assigned_to == user_id]

        if status:
            conditions.append(NodeExecution.status == status)

        result = await db.execute(
            select(NodeExecution)
            .options(
                selectinload(NodeExecution.node),
                selectinload(NodeExecution.candidate_process).selectinload(CandidateProcess.candidate)
            )
            .where(and_(*conditions))
            .order_by(asc(NodeExecution.due_date))
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def get_overdue_executions(
        self,
        db: AsyncSession,
        *,
        assigned_to: Optional[int] = None,
        limit: int = 100
    ) -> List[NodeExecution]:
        """Get overdue executions"""
        conditions = [
            NodeExecution.due_date < datetime.utcnow(),
            NodeExecution.status.in_(["pending", "scheduled", "in_progress"])
        ]

        if assigned_to:
            conditions.append(NodeExecution.assigned_to == assigned_to)

        result = await db.execute(
            select(NodeExecution)
            .options(
                selectinload(NodeExecution.node),
                selectinload(NodeExecution.candidate_process).selectinload(CandidateProcess.candidate),
                selectinload(NodeExecution.assignee)
            )
            .where(and_(*conditions))
            .order_by(asc(NodeExecution.due_date))
            .limit(limit)
        )
        return result.scalars().all()

    async def get_with_details(
        self,
        db: AsyncSession,
        *,
        id: int
    ) -> Optional[NodeExecution]:
        """Get execution with full details"""
        result = await db.execute(
            select(NodeExecution)
            .options(
                selectinload(NodeExecution.node),
                selectinload(NodeExecution.candidate_process).selectinload(CandidateProcess.candidate),
                selectinload(NodeExecution.candidate_process).selectinload(CandidateProcess.process),
                selectinload(NodeExecution.assignee),
                selectinload(NodeExecution.completer),
                selectinload(NodeExecution.reviewer),
                selectinload(NodeExecution.interview),
                selectinload(NodeExecution.todo)
            )
            .where(NodeExecution.id == id)
        )
        return result.scalars().first()

    async def start_execution(
        self,
        db: AsyncSession,
        *,
        execution: NodeExecution,
        assigned_to: Optional[int] = None
    ) -> NodeExecution:
        """Start an execution"""
        execution.start(assigned_to)
        await db.commit()
        await db.refresh(execution)
        return execution

    async def complete_execution(
        self,
        db: AsyncSession,
        *,
        execution: NodeExecution,
        result: str,
        completed_by: int,
        score: Optional[float] = None,
        feedback: Optional[str] = None,
        execution_data: Optional[Dict[str, Any]] = None
    ) -> NodeExecution:
        """Complete an execution"""
        execution.complete(result, completed_by, score, feedback, execution_data)
        await db.commit()
        await db.refresh(execution)
        return execution

    async def fail_execution(
        self,
        db: AsyncSession,
        *,
        execution: NodeExecution,
        completed_by: int,
        reason: Optional[str] = None
    ) -> NodeExecution:
        """Fail an execution"""
        execution.fail(completed_by, reason)
        await db.commit()
        await db.refresh(execution)
        return execution

    async def skip_execution(
        self,
        db: AsyncSession,
        *,
        execution: NodeExecution,
        completed_by: int,
        reason: Optional[str] = None
    ) -> NodeExecution:
        """Skip an execution"""
        execution.skip(completed_by, reason)
        await db.commit()
        await db.refresh(execution)
        return execution

    async def schedule_execution(
        self,
        db: AsyncSession,
        *,
        execution: NodeExecution,
        due_date: datetime
    ) -> NodeExecution:
        """Schedule an execution"""
        execution.schedule(due_date)
        await db.commit()
        await db.refresh(execution)
        return execution

    async def link_interview(
        self,
        db: AsyncSession,
        *,
        execution: NodeExecution,
        interview_id: int
    ) -> NodeExecution:
        """Link an interview to an execution"""
        execution.link_interview(interview_id)
        await db.commit()
        await db.refresh(execution)
        return execution

    async def link_todo(
        self,
        db: AsyncSession,
        *,
        execution: NodeExecution,
        todo_id: int
    ) -> NodeExecution:
        """Link a todo to an execution"""
        execution.link_todo(todo_id)
        await db.commit()
        await db.refresh(execution)
        return execution

    async def bulk_update_status(
        self,
        db: AsyncSession,
        *,
        execution_ids: List[int],
        status: str,
        assigned_to: Optional[int] = None
    ) -> List[NodeExecution]:
        """Bulk update execution status"""
        executions = await db.execute(
            select(NodeExecution)
            .where(NodeExecution.id.in_(execution_ids))
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
        self,
        db: AsyncSession,
        *,
        completions: List[Dict[str, Any]],
        completed_by: int
    ) -> List[NodeExecution]:
        """Bulk complete executions"""
        execution_ids = [c["execution_id"] for c in completions]
        executions = await db.execute(
            select(NodeExecution)
            .where(NodeExecution.id.in_(execution_ids))
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
                    execution_data=completion.get("execution_data")
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
        node_id: Optional[int] = None,
        process_id: Optional[int] = None,
        candidate_process_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """Get execution statistics"""
        conditions = []

        if node_id:
            conditions.append(NodeExecution.node_id == node_id)

        if process_id:
            conditions.append(NodeExecution.candidate_process.has(process_id=process_id))

        if candidate_process_id:
            conditions.append(NodeExecution.candidate_process_id == candidate_process_id)

        # Count by status
        status_counts = await db.execute(
            select(
                NodeExecution.status,
                func.count(NodeExecution.id).label("count")
            )
            .where(and_(*conditions) if conditions else True)
            .group_by(NodeExecution.status)
        )

        status_dict = {row.status: row.count for row in status_counts}

        # Count by result
        result_counts = await db.execute(
            select(
                NodeExecution.result,
                func.count(NodeExecution.id).label("count")
            )
            .where(
                and_(
                    *conditions,
                    NodeExecution.result.isnot(None)
                ) if conditions else NodeExecution.result.isnot(None)
            )
            .group_by(NodeExecution.result)
        )

        result_dict = {row.result: row.count for row in result_counts}

        # Calculate averages
        avg_duration_result = await db.execute(
            select(
                func.avg(
                    func.extract('epoch', NodeExecution.completed_at - NodeExecution.started_at) / 60
                )
            )
            .where(
                and_(
                    *conditions,
                    NodeExecution.started_at.isnot(None),
                    NodeExecution.completed_at.isnot(None)
                ) if conditions else and_(
                    NodeExecution.started_at.isnot(None),
                    NodeExecution.completed_at.isnot(None)
                )
            )
        )

        avg_score_result = await db.execute(
            select(func.avg(NodeExecution.score))
            .where(
                and_(
                    *conditions,
                    NodeExecution.score.isnot(None)
                ) if conditions else NodeExecution.score.isnot(None)
            )
        )

        total_executions = sum(status_dict.values())
        completed_executions = status_dict.get("completed", 0)
        completion_rate = (completed_executions / total_executions * 100) if total_executions > 0 else 0

        return {
            "total_executions": total_executions,
            "by_status": status_dict,
            "by_result": result_dict,
            "completion_rate": completion_rate,
            "average_duration_minutes": avg_duration_result.scalar() or 0,
            "average_score": avg_score_result.scalar()
        }

    async def get_workload_by_assignee(
        self,
        db: AsyncSession,
        *,
        process_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Get workload distribution by assignee"""
        conditions = [NodeExecution.assigned_to.isnot(None)]

        if process_id:
            conditions.append(NodeExecution.candidate_process.has(process_id=process_id))

        result = await db.execute(
            select(
                NodeExecution.assigned_to,
                func.count(NodeExecution.id).label("total_assigned"),
                func.sum(
                    func.case(
                        (NodeExecution.status == "pending", 1),
                        else_=0
                    )
                ).label("pending"),
                func.sum(
                    func.case(
                        (NodeExecution.status == "in_progress", 1),
                        else_=0
                    )
                ).label("in_progress"),
                func.sum(
                    func.case(
                        (and_(
                            NodeExecution.due_date < datetime.utcnow(),
                            NodeExecution.status.in_(["pending", "scheduled", "in_progress"])
                        ), 1),
                        else_=0
                    )
                ).label("overdue"),
                func.sum(
                    func.case(
                        (NodeExecution.status == "completed", 1),
                        else_=0
                    )
                ).label("completed"),
                func.avg(
                    func.extract('epoch', NodeExecution.completed_at - NodeExecution.started_at) / 3600
                ).label("avg_completion_hours")
            )
            .where(and_(*conditions))
            .group_by(NodeExecution.assigned_to)
            .order_by(desc("total_assigned"))
        )

        workload = []
        for row in result:
            completion_rate = (row.completed / row.total_assigned * 100) if row.total_assigned > 0 else 0

            workload.append({
                "assignee_id": row.assigned_to,
                "total_assigned": row.total_assigned,
                "pending": row.pending or 0,
                "in_progress": row.in_progress or 0,
                "overdue": row.overdue or 0,
                "completed": row.completed or 0,
                "completion_rate": completion_rate,
                "average_completion_hours": row.avg_completion_hours or 0,
                "workload_score": (row.pending or 0) + (row.in_progress or 0) * 1.5 + (row.overdue or 0) * 2
            })

        return workload


node_execution = CRUDNodeExecution(NodeExecution)