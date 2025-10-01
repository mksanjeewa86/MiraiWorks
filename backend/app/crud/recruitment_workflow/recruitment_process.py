from datetime import datetime
from typing import Any

from sqlalchemy import and_, desc, func, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.crud.base import CRUDBase
from app.models.candidate_process import CandidateProcess
from app.models.interview import Interview
from app.models.process_node import ProcessNode
from app.models.process_viewer import ProcessViewer
from app.models.recruitment_process import RecruitmentProcess
from app.models.todo import Todo


class CRUDRecruitmentProcess(CRUDBase[RecruitmentProcess, dict, dict]):

    async def get(self, db: AsyncSession, id: int) -> RecruitmentProcess | None:
        """Get recruitment process by id, excluding soft-deleted records."""
        result = await db.execute(
            select(RecruitmentProcess).where(
                RecruitmentProcess.id == id,
                RecruitmentProcess.is_deleted == False
            )
        )
        return result.scalar_one_or_none()

    async def get_multi(
        self, db: AsyncSession, *, skip: int = 0, limit: int = 100
    ) -> list[RecruitmentProcess]:
        """Get multiple recruitment processes, excluding soft-deleted records."""
        result = await db.execute(
            select(RecruitmentProcess)
            .where(RecruitmentProcess.is_deleted == False)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def soft_delete(self, db: AsyncSession, *, id: int) -> RecruitmentProcess:
        """
        Soft delete workflow and cascade to related interviews and todos.

        When a workflow is soft deleted, all associated interviews and todos
        are automatically soft deleted as well.
        """
        # Get the workflow
        workflow = await self.get(db, id)
        if not workflow:
            return None

        # Soft delete the workflow
        workflow.is_deleted = True
        workflow.deleted_at = datetime.utcnow()
        db.add(workflow)

        # Cascade soft delete to related interviews
        await db.execute(
            update(Interview)
            .where(
                Interview.workflow_id == id,
                Interview.is_deleted == False
            )
            .values(
                is_deleted=True,
                deleted_at=datetime.utcnow()
            )
        )

        # Cascade soft delete to related todos
        await db.execute(
            update(Todo)
            .where(
                Todo.workflow_id == id,
                Todo.is_deleted == False
            )
            .values(
                is_deleted=True,
                deleted_at=datetime.utcnow()
            )
        )

        await db.commit()
        await db.refresh(workflow)
        return workflow

    async def create(
        self,
        db: AsyncSession,
        *,
        obj_in: dict[str, Any],
        created_by: int
    ) -> RecruitmentProcess:
        """Create a new recruitment process"""
        obj_data = obj_in.copy()
        obj_data["created_by"] = created_by

        db_obj = RecruitmentProcess(**obj_data)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def get_by_company_id(
        self,
        db: AsyncSession,
        *,
        company_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> list[RecruitmentProcess]:
        """Get all processes for a company, excluding soft-deleted."""
        result = await db.execute(
            select(RecruitmentProcess)
            .where(
                RecruitmentProcess.employer_company_id == company_id,
                RecruitmentProcess.is_deleted == False
            )
            .order_by(desc(RecruitmentProcess.created_at))
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def get_active_by_company_id(
        self,
        db: AsyncSession,
        *,
        company_id: int
    ) -> list[RecruitmentProcess]:
        """Get active processes for a company, excluding soft-deleted."""
        result = await db.execute(
            select(RecruitmentProcess)
            .where(
                and_(
                    RecruitmentProcess.employer_company_id == company_id,
                    RecruitmentProcess.status == "active",
                    RecruitmentProcess.is_deleted == False
                )
            )
            .order_by(desc(RecruitmentProcess.activated_at))
        )
        return result.scalars().all()

    async def get_with_nodes(
        self,
        db: AsyncSession,
        *,
        id: int
    ) -> RecruitmentProcess | None:
        """Get process with its nodes, excluding soft-deleted."""
        result = await db.execute(
            select(RecruitmentProcess)
            .options(
                selectinload(RecruitmentProcess.nodes),
                selectinload(RecruitmentProcess.candidate_processes),
                selectinload(RecruitmentProcess.viewers)
            )
            .where(
                RecruitmentProcess.id == id,
                RecruitmentProcess.is_deleted == False
            )
        )
        return result.scalars().first()

    async def get_by_job_id(
        self,
        db: AsyncSession,
        *,
        job_id: int
    ) -> list[RecruitmentProcess]:
        """Get processes associated with a job, excluding soft-deleted."""
        result = await db.execute(
            select(RecruitmentProcess)
            .where(
                RecruitmentProcess.job_id == job_id,
                RecruitmentProcess.is_deleted == False
            )
            .order_by(desc(RecruitmentProcess.created_at))
        )
        return result.scalars().all()

    async def get_templates(
        self,
        db: AsyncSession,
        *,
        company_id: int | None = None,
        is_public: bool = False,
        skip: int = 0,
        limit: int = 100
    ) -> list[RecruitmentProcess]:
        """Get process templates, excluding soft-deleted."""
        conditions = [
            RecruitmentProcess.is_template is True,
            RecruitmentProcess.is_deleted == False
        ]

        if company_id is not None:
            conditions.append(
                or_(
                    RecruitmentProcess.employer_company_id == company_id,
                    RecruitmentProcess.employer_company_id.is_(None) if is_public else False
                )
            )

        result = await db.execute(
            select(RecruitmentProcess)
            .where(and_(*conditions))
            .order_by(desc(RecruitmentProcess.created_at))
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def update(
        self,
        db: AsyncSession,
        *,
        db_obj: RecruitmentProcess,
        obj_in: dict[str, Any],
        updated_by: int
    ) -> RecruitmentProcess:
        """Update a recruitment process"""
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)

        update_data["updated_by"] = updated_by
        update_data["updated_at"] = datetime.utcnow()

        return await super().update(db, db_obj=db_obj, obj_in=update_data)

    async def activate(
        self,
        db: AsyncSession,
        *,
        db_obj: RecruitmentProcess,
        activated_by: int
    ) -> RecruitmentProcess:
        """Activate a process"""
        if db_obj.status != "draft":
            raise ValueError("Only draft processes can be activated")

        db_obj.activate(activated_by)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def archive(
        self,
        db: AsyncSession,
        *,
        db_obj: RecruitmentProcess,
        archived_by: int
    ) -> RecruitmentProcess:
        """Archive a process"""
        db_obj.archive(archived_by)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def deactivate(
        self,
        db: AsyncSession,
        *,
        db_obj: RecruitmentProcess,
        deactivated_by: int
    ) -> RecruitmentProcess:
        """Deactivate a process"""
        db_obj.deactivate(deactivated_by)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def clone(
        self,
        db: AsyncSession,
        *,
        source_process: RecruitmentProcess,
        new_name: str,
        created_by: int,
        clone_nodes: bool = True,
        clone_viewers: bool = True
    ) -> RecruitmentProcess:
        """Clone a process"""
        # Create new process
        clone_data = {
            "name": new_name,
            "description": source_process.description,
            "employer_company_id": source_process.employer_company_id,
            "job_id": source_process.job_id,
            "settings": source_process.settings,
            "created_by": created_by,
            "status": "draft",
            "version": 1
        }

        cloned_process = RecruitmentProcess(**clone_data)
        db.add(cloned_process)
        await db.flush()

        if clone_nodes:
            # Load source nodes
            source_with_nodes = await self.get_with_nodes(db, id=source_process.id)
            if source_with_nodes and source_with_nodes.nodes:
                for node in source_with_nodes.nodes:
                    cloned_node = ProcessNode(
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
                        status="draft"
                    )
                    db.add(cloned_node)

        if clone_viewers:
            # Load source viewers
            if source_process.viewers:
                for viewer in source_process.viewers:
                    cloned_viewer = ProcessViewer(
                        process_id=cloned_process.id,
                        user_id=viewer.user_id,
                        role=viewer.role,
                        permissions=viewer.permissions,
                        added_by=created_by
                    )
                    db.add(cloned_viewer)

        await db.commit()
        await db.refresh(cloned_process)
        return cloned_process

    async def get_statistics(
        self,
        db: AsyncSession,
        *,
        company_id: int
    ) -> dict[str, Any]:
        """Get process statistics for a company, excluding soft-deleted."""
        # Count processes by status
        status_counts = await db.execute(
            select(
                RecruitmentProcess.status,
                func.count(RecruitmentProcess.id).label("count")
            )
            .where(
                RecruitmentProcess.employer_company_id == company_id,
                RecruitmentProcess.is_deleted == False
            )
            .group_by(RecruitmentProcess.status)
        )

        status_dict = {row.status: row.count for row in status_counts}

        # Count candidates by status
        candidate_counts = await db.execute(
            select(
                CandidateProcess.status,
                func.count(CandidateProcess.id).label("count")
            )
            .join(RecruitmentProcess)
            .where(
                RecruitmentProcess.employer_company_id == company_id,
                RecruitmentProcess.is_deleted == False
            )
            .group_by(CandidateProcess.status)
        )

        candidate_dict = {row.status: row.count for row in candidate_counts}

        # Calculate completion rate
        total_candidates = sum(candidate_dict.values())
        completed_candidates = candidate_dict.get("completed", 0)
        completion_rate = (completed_candidates / total_candidates * 100) if total_candidates > 0 else 0

        # Calculate average duration
        avg_duration_result = await db.execute(
            select(
                func.avg(
                    func.extract('epoch', CandidateProcess.completed_at - CandidateProcess.started_at) / 86400
                )
            )
            .join(RecruitmentProcess)
            .where(
                and_(
                    RecruitmentProcess.employer_company_id == company_id,
                    RecruitmentProcess.is_deleted == False,
                    CandidateProcess.status == "completed",
                    CandidateProcess.started_at.isnot(None),
                    CandidateProcess.completed_at.isnot(None)
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
            "average_duration_days": avg_duration
        }

    async def search(
        self,
        db: AsyncSession,
        *,
        company_id: int,
        query: str,
        status: str | None = None,
        skip: int = 0,
        limit: int = 100
    ) -> list[RecruitmentProcess]:
        """Search processes by name or description, excluding soft-deleted."""
        conditions = [
            RecruitmentProcess.employer_company_id == company_id,
            RecruitmentProcess.is_deleted == False
        ]

        if query:
            search_filter = or_(
                RecruitmentProcess.name.ilike(f"%{query}%"),
                RecruitmentProcess.description.ilike(f"%{query}%")
            )
            conditions.append(search_filter)

        if status:
            conditions.append(RecruitmentProcess.status == status)

        result = await db.execute(
            select(RecruitmentProcess)
            .where(and_(*conditions))
            .order_by(desc(RecruitmentProcess.updated_at))
            .offset(skip)
            .limit(limit)
        )

        return result.scalars().all()

    async def get_for_user(
        self,
        db: AsyncSession,
        *,
        user_id: int,
        role: str,
        skip: int = 0,
        limit: int = 100
    ) -> list[RecruitmentProcess]:
        """Get processes accessible to a user based on their role, excluding soft-deleted."""
        if role == "employer":
            # Employer can see their company's processes
            result = await db.execute(
                select(RecruitmentProcess)
                .join(RecruitmentProcess.employer_company)
                .where(
                    RecruitmentProcess.created_by == user_id,
                    RecruitmentProcess.is_deleted == False
                )
                .order_by(desc(RecruitmentProcess.created_at))
                .offset(skip)
                .limit(limit)
            )
        else:
            # Recruiter/viewer can see processes they have access to
            result = await db.execute(
                select(RecruitmentProcess)
                .join(ProcessViewer)
                .where(
                    ProcessViewer.user_id == user_id,
                    RecruitmentProcess.is_deleted == False
                )
                .order_by(desc(RecruitmentProcess.created_at))
                .offset(skip)
                .limit(limit)
            )

        return result.scalars().all()


recruitment_process = CRUDRecruitmentProcess(RecruitmentProcess)
