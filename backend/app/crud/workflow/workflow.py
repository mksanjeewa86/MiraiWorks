from typing import Any

from sqlalchemy import and_, desc, func, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.crud.base import CRUDBase
from app.models.candidate_workflow import CandidateWorkflow
from app.models.interview import Interview
from app.models.todo import Todo
from app.models.workflow import Workflow
from app.models.workflow_node import WorkflowNode
from app.models.workflow_viewer import WorkflowViewer
from app.utils.datetime_utils import get_utc_now


class CRUDWorkflow(CRUDBase[Workflow, Any, Any]):
    async def get(self, db: AsyncSession, id: int) -> Workflow | None:
        """Get workflow by id, excluding soft-deleted records."""
        result = await db.execute(
            select(Workflow).where(Workflow.id == id, ~Workflow.is_deleted)
        )
        return result.scalar_one_or_none()

    async def get_multi(
        self, db: AsyncSession, *, skip: int = 0, limit: int = 100
    ) -> list[Workflow]:
        """Get multiple workflowes, excluding soft-deleted records."""
        result = await db.execute(
            select(Workflow).where(~Workflow.is_deleted).offset(skip).limit(limit)
        )
        return list(result.scalars().all())

    async def soft_delete(self, db: AsyncSession, *, id: int) -> Workflow:
        """
        Soft delete workflow and cascade to related interviews and todos.

        When a workflow is soft deleted, all associated interviews and todos
        are automatically soft deleted as well.
        """
        # Get the workflow
        workflow = await self.get(db, id)
        if not workflow:
            return None  # type: ignore[return-value]

        # Soft delete the workflow
        workflow.is_deleted = True
        workflow.deleted_at = get_utc_now()
        db.add(workflow)

        # Cascade soft delete to related interviews
        await db.execute(
            update(Interview)
            .where(Interview.workflow_id == id, ~Interview.is_deleted)
            .values(is_deleted=True, deleted_at=get_utc_now())
        )

        # Cascade soft delete to related todos
        await db.execute(
            update(Todo)
            .where(Todo.workflow_id == id, ~Todo.is_deleted)
            .values(is_deleted=True, deleted_at=get_utc_now())
        )

        await db.commit()
        await db.refresh(workflow)
        return workflow

    async def create(  # type: ignore[override]
        self, db: AsyncSession, *, obj_in: dict[str, Any], created_by: int
    ) -> Workflow:
        """Create a new workflow"""
        obj_data = obj_in.copy()
        obj_data["created_by"] = created_by

        db_obj = Workflow(**obj_data)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def get_by_company_id(
        self, db: AsyncSession, *, company_id: int, skip: int = 0, limit: int = 100
    ) -> list[Workflow]:
        """Get all processes for a company, excluding soft-deleted."""
        result = await db.execute(
            select(Workflow)
            .where(
                Workflow.employer_company_id == company_id,
                ~Workflow.is_deleted,
            )
            .order_by(desc(Workflow.created_at))
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_active_by_company_id(
        self, db: AsyncSession, *, company_id: int
    ) -> list[Workflow]:
        """Get active processes for a company, excluding soft-deleted."""
        result = await db.execute(
            select(Workflow)
            .where(
                and_(
                    Workflow.employer_company_id == company_id,
                    Workflow.status == "active",
                    ~Workflow.is_deleted,
                )
            )
            .order_by(desc(Workflow.activated_at))
        )
        return list(result.scalars().all())

    async def get_with_nodes(self, db: AsyncSession, *, id: int) -> Workflow | None:
        """Get process with its nodes, excluding soft-deleted."""
        result = await db.execute(
            select(Workflow)
            .options(
                selectinload(Workflow.nodes),
                selectinload(Workflow.candidate_workflows),
                selectinload(Workflow.viewers),
            )
            .where(Workflow.id == id, ~Workflow.is_deleted)
        )
        return result.scalars().first()

    async def get_by_job_id(self, db: AsyncSession, *, job_id: int) -> list[Workflow]:
        """Get processes associated with a job, excluding soft-deleted."""
        result = await db.execute(
            select(Workflow)
            .where(
                Workflow.job_id == job_id,  # type: ignore[attr-defined]
                ~Workflow.is_deleted,
            )
            .order_by(desc(Workflow.created_at))
        )
        return list(result.scalars().all())

    async def get_templates(
        self,
        db: AsyncSession,
        *,
        company_id: int | None = None,
        is_public: bool = False,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Workflow]:
        """Get process templates, excluding soft-deleted."""
        conditions = [
            Workflow.is_template is True,
            ~Workflow.is_deleted,
        ]

        if company_id is not None:
            conditions.append(
                or_(
                    Workflow.employer_company_id == company_id,
                    Workflow.employer_company_id.is_(None) if is_public else False,  # type: ignore[arg-type]
                )
            )

        result = await db.execute(
            select(Workflow)
            .where(and_(*conditions))
            .order_by(desc(Workflow.created_at))
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def update(  # type: ignore[override]
        self,
        db: AsyncSession,
        *,
        db_obj: Workflow,
        obj_in: dict[str, Any],
        updated_by: int,
    ) -> Workflow:
        """Update a workflow"""
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)

        update_data["updated_by"] = updated_by
        update_data["updated_at"] = get_utc_now()

        return await super().update(db, db_obj=db_obj, obj_in=update_data)

    async def activate(
        self, db: AsyncSession, *, db_obj: Workflow, activated_by: int
    ) -> Workflow:
        """Activate a process"""
        if db_obj.status != "draft":
            raise ValueError("Only draft processes can be activated")

        db_obj.activate(activated_by)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def archive(
        self, db: AsyncSession, *, db_obj: Workflow, archived_by: int
    ) -> Workflow:
        """Archive a process"""
        db_obj.archive(archived_by)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def deactivate(
        self, db: AsyncSession, *, db_obj: Workflow, deactivated_by: int
    ) -> Workflow:
        """Deactivate a process"""
        db_obj.deactivate(deactivated_by)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def clone(
        self,
        db: AsyncSession,
        *,
        source_process: Workflow,
        new_name: str,
        created_by: int,
        clone_nodes: bool = True,
        clone_viewers: bool = True,
    ) -> Workflow:
        """Clone a process"""
        # Create new process
        clone_data = {
            "name": new_name,
            "description": source_process.description,
            "employer_company_id": source_process.employer_company_id,
            "job_id": source_process.job_id,  # type: ignore[attr-defined]
            "settings": source_process.settings,
            "created_by": created_by,
            "status": "draft",
            "version": 1,
        }

        cloned_process = Workflow(**clone_data)
        db.add(cloned_process)
        await db.flush()

        if clone_nodes:
            # Load source nodes
            source_with_nodes = await self.get_with_nodes(db, id=source_process.id)
            if source_with_nodes and source_with_nodes.nodes:
                for node in source_with_nodes.nodes:
                    cloned_node = WorkflowNode(
                        process_id=cloned_process.id,
                        node_type=node.node_type,
                        title=node.title,
                        description=node.description,
                        sequence_order=node.sequence_order,
                        position_x=node.position_x,
                        position_y=node.position_y,
                        config=node.config,
                        requirements=node.requirements,
                        instructions=node.instructions,
                        estimated_duration_minutes=node.estimated_duration_minutes,
                        is_required=node.is_required,
                        can_skip=node.can_skip,
                        auto_advance=node.auto_advance,
                        created_by=created_by,
                        status="draft",
                    )
                    db.add(cloned_node)

        if clone_viewers and source_process.viewers:
            # Load source viewers
            for viewer in source_process.viewers:
                cloned_viewer = WorkflowViewer(
                    process_id=cloned_process.id,
                    user_id=viewer.user_id,
                    role=viewer.role,
                    permissions=viewer.permissions,
                    added_by=created_by,
                )
                db.add(cloned_viewer)

        await db.commit()
        await db.refresh(cloned_process)
        return cloned_process

    async def get_statistics(
        self, db: AsyncSession, *, company_id: int
    ) -> dict[str, Any]:
        """Get process statistics for a company, excluding soft-deleted."""
        # Count processes by status
        status_counts = await db.execute(
            select(
                Workflow.status,
                func.count(Workflow.id).label("count"),
            )
            .where(
                Workflow.employer_company_id == company_id,
                ~Workflow.is_deleted,
            )
            .group_by(Workflow.status)
        )

        status_dict = {row[0]: row[1] for row in status_counts.all()}

        # Count candidates by status
        candidate_counts = await db.execute(
            select(
                CandidateWorkflow.status,
                func.count(CandidateWorkflow.id).label("count"),
            )
            .join(Workflow)
            .where(
                Workflow.employer_company_id == company_id,
                ~Workflow.is_deleted,
            )
            .group_by(CandidateWorkflow.status)
        )

        candidate_dict = {row[0]: row[1] for row in candidate_counts.all()}

        # Calculate completion rate
        total_candidates = sum(candidate_dict.values())
        completed_candidates = candidate_dict.get("completed", 0)
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
            )
            .join(Workflow)
            .where(
                and_(
                    Workflow.employer_company_id == company_id,
                    ~Workflow.is_deleted,
                    CandidateWorkflow.status == "completed",
                    CandidateWorkflow.started_at.isnot(None),
                    CandidateWorkflow.completed_at.isnot(None),
                )
            )
        )

        avg_duration = avg_duration_result.scalar() or 0

        return {
            "total_processes": sum(status_dict.values()),
            "active_processes": status_dict.get("active", 0),
            "draft_processes": status_dict.get("draft", 0),
            "archived_processes": status_dict.get("archived", 0),
            "total_candidates": total_candidates,
            "active_candidates": candidate_dict.get("in_progress", 0),
            "completed_candidates": completed_candidates,
            "average_completion_rate": completion_rate,
            "average_duration_days": avg_duration,
        }

    async def search(
        self,
        db: AsyncSession,
        *,
        company_id: int,
        query: str,
        status: str | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Workflow]:
        """Search processes by name or description, excluding soft-deleted."""
        conditions = [
            Workflow.employer_company_id == company_id,
            ~Workflow.is_deleted,
        ]

        if query:
            search_filter = or_(
                Workflow.name.ilike(f"%{query}%"),
                Workflow.description.ilike(f"%{query}%"),
            )
            conditions.append(search_filter)

        if status:
            conditions.append(Workflow.status == status)

        result = await db.execute(
            select(Workflow)
            .where(and_(*conditions))
            .order_by(desc(Workflow.updated_at))
            .offset(skip)
            .limit(limit)
        )

        return list(result.scalars().all())

    async def get_for_user(
        self,
        db: AsyncSession,
        *,
        user_id: int,
        role: str,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Workflow]:
        """Get processes accessible to a user based on their role, excluding soft-deleted."""
        if role == "employer":
            # Employer can see their company's processes
            result = await db.execute(
                select(Workflow)
                .join(Workflow.employer_company)
                .where(
                    Workflow.created_by == user_id,
                    ~Workflow.is_deleted,
                )
                .order_by(desc(Workflow.created_at))
                .offset(skip)
                .limit(limit)
            )
        else:
            # Recruiter/viewer can see processes they have access to
            result = await db.execute(
                select(Workflow)
                .join(WorkflowViewer)
                .where(
                    WorkflowViewer.user_id == user_id,
                    ~Workflow.is_deleted,
                )
                .order_by(desc(Workflow.created_at))
                .offset(skip)
                .limit(limit)
            )

        return list(result.scalars().all())


workflow = CRUDWorkflow(Workflow)
