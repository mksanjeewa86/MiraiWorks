from typing import Any

from sqlalchemy import and_, asc, desc, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.crud.base import CRUDBase
from app.models.workflow_node import WorkflowNode
from app.models.workflow_node_connection import WorkflowNodeConnection
from app.models.workflow_node_execution import WorkflowNodeExecution
from app.utils.datetime_utils import get_utc_now


class CRUDWorkflowNode(CRUDBase[WorkflowNode, Any, Any]):
    async def create(  # type: ignore[override]
        self, db: AsyncSession, *, obj_in: dict[str, Any], created_by: int
    ) -> WorkflowNode:
        """Create a new process node"""
        obj_data = obj_in.copy()
        obj_data["created_by"] = created_by

        # Extract position from obj_in if it exists
        if "position" in obj_data:
            position = obj_data.pop("position")
            obj_data["position_x"] = position["x"]
            obj_data["position_y"] = position["y"]

        db_obj = WorkflowNode(**obj_data)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def get_by_workflow_id(
        self, db: AsyncSession, *, workflow_id: int, include_inactive: bool = False
    ) -> list[WorkflowNode]:
        """Get all nodes for a workflow"""
        conditions = [WorkflowNode.workflow_id == workflow_id]

        if not include_inactive:
            conditions.append(WorkflowNode.status != "inactive")

        result = await db.execute(
            select(WorkflowNode)
            .where(and_(*conditions))
            .order_by(asc(WorkflowNode.sequence_order))
        )
        return list(result.scalars().all())

    async def get_with_connections(
        self, db: AsyncSession, *, id: int
    ) -> WorkflowNode | None:
        """Get node with its connections"""
        result = await db.execute(
            select(WorkflowNode)
            .options(
                selectinload(WorkflowNode.outgoing_connections),
                selectinload(WorkflowNode.incoming_connections),
                selectinload(WorkflowNode.executions),
            )
            .where(WorkflowNode.id == id)
        )
        return result.scalars().first()

    async def get_start_nodes(
        self, db: AsyncSession, *, workflow_id: int
    ) -> list[WorkflowNode]:
        """Get start nodes for a workflow (nodes with no incoming connections or sequence_order = 1)"""
        # First try to get node with sequence_order = 1
        result = await db.execute(
            select(WorkflowNode).where(
                and_(
                    WorkflowNode.workflow_id == workflow_id,
                    WorkflowNode.sequence_order == 1,
                    WorkflowNode.status == "active",
                )
            )
        )
        start_node = result.scalars().first()

        if start_node:
            return [start_node]

        # If no node with sequence_order = 1, find nodes with no incoming connections
        subquery = (
            select(WorkflowNodeConnection.target_node_id).where(
                WorkflowNodeConnection.workflow_id == workflow_id
            )
        ).subquery()

        result = await db.execute(
            select(WorkflowNode)
            .where(
                and_(
                    WorkflowNode.workflow_id == workflow_id,
                    WorkflowNode.status == "active",
                    WorkflowNode.id.notin_(subquery),  # type: ignore[arg-type]
                )
            )
            .order_by(asc(WorkflowNode.sequence_order))
        )
        return list(result.scalars().all())

    async def get_next_nodes(
        self,
        db: AsyncSession,
        *,
        node_id: int,
        execution_result: str,
        execution_data: dict[str, Any] | None = None,
    ) -> list[WorkflowNode]:
        """Get next nodes based on execution result"""
        # Get outgoing connections
        result = await db.execute(
            select(WorkflowNodeConnection)
            .options(selectinload(WorkflowNodeConnection.target_node))
            .where(WorkflowNodeConnection.source_node_id == node_id)
        )
        connections = result.scalars().all()

        next_nodes = []
        for connection in connections:
            if (
                connection.evaluate_condition(execution_result, execution_data)
                and connection.target_node
                and connection.target_node.status == "active"
            ):
                next_nodes.append(connection.target_node)

        return next_nodes

    async def update(  # type: ignore[override]
        self,
        db: AsyncSession,
        *,
        db_obj: WorkflowNode,
        obj_in: dict[str, Any],
        updated_by: int,
    ) -> WorkflowNode:
        """Update a process node"""
        if isinstance(obj_in, dict):
            update_data = obj_in.copy()
        else:
            update_data = obj_in.dict(exclude_unset=True)

        # Handle position update
        if "position" in update_data:
            position = update_data.pop("position")
            update_data["position_x"] = position["x"]
            update_data["position_y"] = position["y"]

        update_data["updated_by"] = updated_by
        update_data["updated_at"] = get_utc_now()

        return await super().update(db, db_obj=db_obj, obj_in=update_data)

    async def reorder_nodes(
        self,
        db: AsyncSession,
        *,
        workflow_id: int,
        node_sequence_updates: list[dict[str, int]],
        updated_by: int,
    ) -> list[WorkflowNode]:
        """Reorder nodes in a workflow

        Uses a two-step update to avoid unique constraint violations:
        1. Set temporary negative values to avoid conflicts
        2. Update to final positive sequence_order values
        """
        updated_nodes = []
        timestamp = get_utc_now()

        # Step 1: Set all nodes to negative temporary values to avoid constraint conflicts
        for i, update in enumerate(node_sequence_updates):
            node_id = update["node_id"]
            node = await self.get(db, id=node_id)
            if node and node.workflow_id == workflow_id:
                node.sequence_order = -(i + 1000)  # Use negative values as temporary
                node.updated_by = updated_by
                node.updated_at = timestamp
                updated_nodes.append((node, update["sequence_order"]))

        await db.flush()  # Flush temporary values

        # Step 2: Update to final sequence_order values
        for node, final_sequence in updated_nodes:
            node.sequence_order = final_sequence

        await db.commit()

        # Refresh all nodes
        result_nodes = []
        for node, _ in updated_nodes:
            await db.refresh(node)
            result_nodes.append(node)

        return result_nodes

    async def activate_node(
        self, db: AsyncSession, *, db_obj: WorkflowNode, updated_by: int
    ) -> WorkflowNode:
        """Activate a node"""
        db_obj.activate(updated_by)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def deactivate_node(
        self, db: AsyncSession, *, db_obj: WorkflowNode, updated_by: int
    ) -> WorkflowNode:
        """Deactivate a node"""
        db_obj.deactivate(updated_by)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def get_node_statistics(
        self, db: AsyncSession, *, node_id: int
    ) -> dict[str, Any]:
        """Get statistics for a specific node"""
        # Count executions by status
        status_counts = await db.execute(
            select(
                WorkflowNodeExecution.status,
                func.count(WorkflowNodeExecution.id).label("count"),
            )
            .where(WorkflowNodeExecution.node_id == node_id)
            .group_by(WorkflowNodeExecution.status)
        )

        status_dict = {row[0]: row[1] for row in status_counts.all()}

        # Count executions by result
        result_counts = await db.execute(
            select(
                WorkflowNodeExecution.result,
                func.count(WorkflowNodeExecution.id).label("count"),
            )
            .where(
                and_(
                    WorkflowNodeExecution.node_id == node_id,
                    WorkflowNodeExecution.result.isnot(None),
                )
            )
            .group_by(WorkflowNodeExecution.result)
        )

        result_dict = {row[0]: row[1] for row in result_counts.all()}

        # Calculate average duration
        avg_duration_result = await db.execute(
            select(
                func.avg(
                    func.extract(
                        "epoch",
                        WorkflowNodeExecution.completed_at
                        - WorkflowNodeExecution.started_at,
                    )
                    / 60
                )
            ).where(
                and_(
                    WorkflowNodeExecution.node_id == node_id,
                    WorkflowNodeExecution.started_at.isnot(None),
                    WorkflowNodeExecution.completed_at.isnot(None),
                )
            )
        )

        avg_duration = avg_duration_result.scalar() or 0

        # Calculate average score
        avg_score_result = await db.execute(
            select(func.avg(WorkflowNodeExecution.score)).where(
                and_(
                    WorkflowNodeExecution.node_id == node_id,
                    WorkflowNodeExecution.score.isnot(None),
                )
            )
        )

        avg_score = avg_score_result.scalar()

        total_executions = sum(list(status_dict.values()))
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
            "average_duration_minutes": avg_duration,
            "average_score": avg_score,
        }

    async def get_bottleneck_nodes(
        self, db: AsyncSession, *, workflow_id: int, limit: int = 5
    ) -> list[dict[str, Any]]:
        """Get nodes that are bottlenecks in the workflow"""
        # Nodes with longest average execution time or lowest completion rate
        result = await db.execute(
            select(
                WorkflowNode.id,
                WorkflowNode.title,
                WorkflowNode.node_type,
                func.count(WorkflowNodeExecution.id).label("total_executions"),
                func.sum(
                    func.case((WorkflowNodeExecution.status == "completed", 1), else_=0)
                ).label("completed_executions"),
                func.avg(
                    func.extract(
                        "epoch",
                        WorkflowNodeExecution.completed_at
                        - WorkflowNodeExecution.started_at,
                    )
                    / 60
                ).label("avg_duration_minutes"),
            )
            .join(
                WorkflowNodeExecution,
                WorkflowNode.id == WorkflowNodeExecution.node_id,
                isouter=True,
            )
            .where(WorkflowNode.workflow_id == workflow_id)
            .group_by(WorkflowNode.id, WorkflowNode.title, WorkflowNode.node_type)
            .having(func.count(WorkflowNodeExecution.id) > 0)
            .order_by(desc("avg_duration_minutes"))
            .limit(limit)
        )

        bottlenecks = []
        for row in result:
            completion_rate = (
                (row.completed_executions / row.total_executions * 100)
                if row.total_executions > 0
                else 0
            )
            bottleneck_score = (row.avg_duration_minutes or 0) + (100 - completion_rate)

            bottlenecks.append(
                {
                    "node_id": row.id,
                    "node_title": row.title,
                    "node_type": row.node_type,
                    "total_executions": row.total_executions,
                    "completion_rate": completion_rate,
                    "avg_duration_minutes": row.avg_duration_minutes or 0,
                    "bottleneck_score": bottleneck_score,
                }
            )

        return sorted(bottlenecks, key=lambda x: x["bottleneck_score"], reverse=True)

    async def can_delete_node(self, db: AsyncSession, *, node_id: int) -> bool:
        """Check if a node can be safely deleted"""
        # Check if there are any executions
        result = await db.execute(
            select(func.count(WorkflowNodeExecution.id)).where(
                WorkflowNodeExecution.node_id == node_id
            )
        )

        execution_count = result.scalar() or 0
        return execution_count == 0

    async def delete_with_connections(self, db: AsyncSession, *, node_id: int) -> bool:
        """Delete a node and its connections"""
        if not await self.can_delete_node(db, node_id=node_id):
            return False

        # Delete connections
        await db.execute(
            select(WorkflowNodeConnection).where(
                or_(
                    WorkflowNodeConnection.source_node_id == node_id,
                    WorkflowNodeConnection.target_node_id == node_id,
                )
            )
        )

        # Delete the node
        node = await self.get(db, id=node_id)
        if node:
            await db.delete(node)
            await db.commit()

        return True

    async def duplicate_node(
        self,
        db: AsyncSession,
        *,
        source_node_id: int,
        new_sequence_order: int,
        created_by: int,
    ) -> WorkflowNode:
        """Duplicate a node within the same workflow"""
        source_node = await self.get(db, id=source_node_id)
        if not source_node:
            raise ValueError("Source node not found")

        duplicate_data = {
            "workflow_id": source_node.workflow_id,
            "node_type": source_node.node_type,
            "title": f"{source_node.title} (Copy)",
            "description": source_node.description,
            "sequence_order": new_sequence_order,
            "position_x": source_node.position_x + 50,  # Offset position
            "position_y": source_node.position_y + 50,
            "config": source_node.config,
            "requirements": source_node.requirements,
            "instructions": source_node.instructions,
            "estimated_duration_minutes": source_node.estimated_duration_minutes,
            "is_required": source_node.is_required,
            "can_skip": source_node.can_skip,
            "auto_advance": source_node.auto_advance,
            "status": "draft",
            "created_by": created_by,
        }

        duplicate_node = WorkflowNode(**duplicate_data)
        db.add(duplicate_node)
        await db.commit()
        await db.refresh(duplicate_node)
        return duplicate_node


workflow_node = CRUDWorkflowNode(WorkflowNode)
