from typing import Any

from sqlalchemy import and_, desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.crud.base import CRUDBase
from app.models.workflow_viewer import WorkflowViewer


class CRUDWorkflowViewer(CRUDBase[WorkflowViewer, dict, dict]):
    async def create(
        self, db: AsyncSession, *, obj_in: dict[str, Any], added_by: int
    ) -> WorkflowViewer:
        """Add a viewer to a process"""
        obj_data = obj_in.copy()
        obj_data["added_by"] = added_by

        db_obj = WorkflowViewer(**obj_data)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def get_by_process_id(
        self, db: AsyncSession, *, workflow_id: int
    ) -> list[WorkflowViewer]:
        """Get all viewers for a process"""
        result = await db.execute(
            select(WorkflowViewer)
            .options(
                selectinload(WorkflowViewer.user),
                selectinload(WorkflowViewer.added_by_user),
            )
            .where(WorkflowViewer.workflow_id == process_id)
            .order_by(desc(WorkflowViewer.added_at))
        )
        return result.scalars().all()

    async def get_by_user_id(
        self, db: AsyncSession, *, user_id: int
    ) -> list[WorkflowViewer]:
        """Get all processes a user has access to"""
        result = await db.execute(
            select(WorkflowViewer)
            .options(
                selectinload(WorkflowViewer.process),
                selectinload(WorkflowViewer.added_by_user),
            )
            .where(WorkflowViewer.user_id == user_id)
            .order_by(desc(WorkflowViewer.added_at))
        )
        return result.scalars().all()

    async def get_by_process_and_user(
        self, db: AsyncSession, *, workflow_id: int, user_id: int
    ) -> WorkflowViewer | None:
        """Get specific process viewer"""
        result = await db.execute(
            select(WorkflowViewer).where(
                and_(
                    WorkflowViewer.workflow_id == workflow_id,
                    WorkflowViewer.user_id == user_id,
                )
            )
        )
        return result.scalars().first()

    async def get_by_role(
        self, db: AsyncSession, *, workflow_id: int, role: str
    ) -> list[WorkflowViewer]:
        """Get viewers by role for a process"""
        result = await db.execute(
            select(WorkflowViewer)
            .options(selectinload(WorkflowViewer.user))
            .where(
                and_(
                    WorkflowViewer.workflow_id == workflow_id,
                    WorkflowViewer.role == role,
                )
            )
            .order_by(desc(WorkflowViewer.added_at))
        )
        return result.scalars().all()

    async def get_recruiters(
        self, db: AsyncSession, *, workflow_id: int
    ) -> list[WorkflowViewer]:
        """Get all recruiters for a process"""
        return await self.get_by_role(db, process_id=workflow_id, role="recruiter")

    async def bulk_add_viewers(
        self,
        db: AsyncSession,
        *,
        workflow_id: int,
        viewers: list[dict[str, Any]],
        added_by: int,
    ) -> list[WorkflowViewer]:
        """Add multiple viewers to a process"""
        new_viewers = []

        for viewer_data in viewers:
            # Check if viewer already exists
            existing = await self.get_by_process_and_user(
                db, process_id=workflow_id, user_id=viewer_data["user_id"]
            )

            if not existing:
                viewer_obj = WorkflowViewer(
                    process_id=workflow_id,
                    user_id=viewer_data["user_id"],
                    role=viewer_data["role"],
                    permissions=viewer_data.get("permissions"),
                    added_by=added_by,
                )
                db.add(viewer_obj)
                new_viewers.append(viewer_obj)

        if new_viewers:
            await db.commit()
            for viewer in new_viewers:
                await db.refresh(viewer)

        return new_viewers

    async def update_role(
        self, db: AsyncSession, *, viewer: WorkflowViewer, new_role: str
    ) -> WorkflowViewer:
        """Update viewer role"""
        viewer.role = new_role
        # Reset permissions when role changes to use role defaults
        viewer.permissions = {}
        await db.commit()
        await db.refresh(viewer)
        return viewer

    async def update_permissions(
        self,
        db: AsyncSession,
        *,
        viewer: WorkflowViewer,
        permission_updates: dict[str, bool],
    ) -> WorkflowViewer:
        """Update specific permissions for a viewer"""
        if not viewer.permissions:
            viewer.permissions = {}

        for permission, value in permission_updates.items():
            viewer.permissions[permission] = value

        await db.commit()
        await db.refresh(viewer)
        return viewer

    async def grant_permission(
        self, db: AsyncSession, *, viewer: WorkflowViewer, permission: str
    ) -> WorkflowViewer:
        """Grant a specific permission to a viewer"""
        viewer.grant_permission(permission)
        await db.commit()
        await db.refresh(viewer)
        return viewer

    async def revoke_permission(
        self, db: AsyncSession, *, viewer: WorkflowViewer, permission: str
    ) -> WorkflowViewer:
        """Revoke a specific permission from a viewer"""
        viewer.revoke_permission(permission)
        await db.commit()
        await db.refresh(viewer)
        return viewer

    async def remove_viewer(self, db: AsyncSession, *, viewer: WorkflowViewer) -> bool:
        """Remove a viewer from a process"""
        await db.delete(viewer)
        await db.commit()
        return True

    async def get_viewer_activity(
        self,
        db: AsyncSession,
        *,
        workflow_id: int | None = None,
        user_id: int | None = None,
    ) -> list[dict[str, Any]]:
        """Get viewer activity statistics"""
        # This would typically involve joining with activity logs
        # For now, we'll return basic viewer information
        conditions = []

        if workflow_id:
            conditions.append(WorkflowViewer.workflow_id == process_id)

        if user_id:
            conditions.append(WorkflowViewer.user_id == user_id)

        result = await db.execute(
            select(WorkflowViewer)
            .options(selectinload(WorkflowViewer.user))
            .where(and_(*conditions) if conditions else True)
            .order_by(desc(WorkflowViewer.added_at))
        )

        activities = []
        for viewer in result.scalars().all():
            activities.append(
                {
                    "viewer_id": viewer.id,
                    "user_id": viewer.user_id,
                    "user_name": viewer.user.name if viewer.user else "Unknown",
                    "role": viewer.role,
                    "last_activity": None,  # Would come from activity logs
                    "actions_count": 0,  # Would come from activity logs
                    "executions_completed": 0,  # Would come from executions
                    "interviews_scheduled": 0,  # Would come from interviews
                    "notes_added": 0,  # Would come from notes
                }
            )

        return activities

    async def get_workload_distribution(
        self, db: AsyncSession, *, workflow_id: int | None = None
    ) -> list[dict[str, Any]]:
        """Get workload distribution among viewers"""
        # Import here to avoid circular imports
        from app.models.candidate_workflow import CandidateWorkflow
        from app.models.workflow_workflow_node_execution import WorkflowNodeExecution

        conditions = []
        if workflow_id:
            conditions.append(WorkflowViewer.workflow_id == process_id)

        # Get viewers with their workload
        result = await db.execute(
            select(
                WorkflowViewer.id,
                WorkflowViewer.user_id,
                WorkflowViewer.role,
                func.count(CandidateWorkflow.id).label("assigned_processes"),
                func.count(
                    func.case(
                        (CandidateWorkflow.status == "in_progress", 1), else_=None
                    )
                ).label("active_processes"),
            )
            .outerjoin(
                CandidateWorkflow,
                CandidateWorkflow.assigned_recruiter_id == WorkflowViewer.user_id,
            )
            .options(selectinload(WorkflowViewer.user))
            .where(and_(*conditions) if conditions else True)
            .group_by(WorkflowViewer.id, WorkflowViewer.user_id, WorkflowViewer.role)
            .order_by(desc("assigned_processes"))
        )

        workload = []
        for row in result:
            # Get execution counts for this user
            execution_counts = await db.execute(
                select(
                    func.count(WorkflowNodeExecution.id).label("total_tasks"),
                    func.count(
                        func.case(
                            (
                                WorkflowNodeExecution.status.in_(
                                    ["pending", "scheduled", "in_progress"]
                                ),
                                1,
                            ),
                            else_=None,
                        )
                    ).label("pending_tasks"),
                    func.count(
                        func.case(
                            (
                                and_(
                                    WorkflowNodeExecution.due_date < func.now(),
                                    WorkflowNodeExecution.status.in_(
                                        ["pending", "scheduled", "in_progress"]
                                    ),
                                ),
                                1,
                            ),
                            else_=None,
                        )
                    ).label("overdue_tasks"),
                )
                .join(CandidateWorkflow)
                .where(CandidateWorkflow.assigned_recruiter_id == row.user_id)
            )

            exec_row = execution_counts.first()

            workload.append(
                {
                    "viewer_id": row.id,
                    "user_id": row.user_id,
                    "user_name": "User Name",  # Would come from user relationship
                    "role": row.role,
                    "assigned_processes": row.assigned_processes or 0,
                    "active_executions": row.active_processes or 0,
                    "pending_tasks": exec_row.pending_tasks if exec_row else 0,
                    "overdue_tasks": exec_row.overdue_tasks if exec_row else 0,
                    "completion_rate": 0.0,  # Would be calculated from completed tasks
                    "average_response_time_hours": 0.0,  # Would be calculated from response times
                }
            )

        return workload

    async def get_statistics(
        self, db: AsyncSession, *, workflow_id: int
    ) -> dict[str, Any]:
        """Get overall viewer statistics for a process"""
        # Count viewers by role
        role_counts = await db.execute(
            select(WorkflowViewer.role, func.count(WorkflowViewer.id).label("count"))
            .where(WorkflowViewer.workflow_id == process_id)
            .group_by(WorkflowViewer.role)
        )

        role_dict = {row.role: row.count for row in role_counts}

        total_viewers = sum(role_dict.values())

        return {
            "total_viewers": total_viewers,
            "by_role": role_dict,
            "active_viewers": total_viewers,  # Would be calculated from activity
            "viewer_activity": await self.get_viewer_activity(
                db, process_id=process_id
            ),
            "workload_distribution": await self.get_workload_distribution(
                db, process_id=process_id
            ),
        }

    async def check_user_access(
        self,
        db: AsyncSession,
        *,
        workflow_id: int,
        user_id: int,
        required_permission: str,
    ) -> bool:
        """Check if a user has a specific permission for a process"""
        viewer = await self.get_by_process_and_user(
            db, process_id=workflow_id, user_id=user_id
        )

        if not viewer:
            return False

        return viewer.has_permission(required_permission)

    async def get_accessible_processes(
        self, db: AsyncSession, *, user_id: int, permission: str | None = None
    ) -> list[int]:
        """Get list of process IDs accessible to a user"""
        conditions = [WorkflowViewer.user_id == user_id]

        result = await db.execute(
            select(WorkflowViewer.process_id).where(and_(*conditions))
        )

        process_ids = [row.process_id for row in result]

        if permission:
            # Filter by permission
            accessible_ids = []
            for process_id in process_ids:
                if await self.check_user_access(
                    db,
                    process_id=workflow_id,
                    user_id=user_id,
                    required_permission=permission,
                ):
                    accessible_ids.append(process_id)
            return accessible_ids

        return process_ids


workflow_viewer = CRUDWorkflowViewer(WorkflowViewer)
