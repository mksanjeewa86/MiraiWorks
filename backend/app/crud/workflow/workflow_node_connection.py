from typing import Any

from sqlalchemy import and_, desc, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.crud.base import CRUDBase
from app.models.workflow_node_connection import WorkflowNodeConnection


class CRUDWorkflowNodeConnection(CRUDBase[WorkflowNodeConnection, dict, dict]):
    async def create(
        self, db: AsyncSession, *, obj_in: dict[str, Any]
    ) -> WorkflowNodeConnection:
        """Create a new node connection"""
        db_obj = WorkflowNodeConnection(**obj_in)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def get_by_workflow_id(
        self, db: AsyncSession, *, workflow_id: int
    ) -> list[WorkflowNodeConnection]:
        """Get all connections for a workflow"""
        result = await db.execute(
            select(WorkflowNodeConnection)
            .options(
                selectinload(WorkflowNodeConnection.source_node),
                selectinload(WorkflowNodeConnection.target_node),
            )
            .where(WorkflowNodeConnection.workflow_id == workflow_id)
            .order_by(desc(WorkflowNodeConnection.created_at))
        )
        return result.scalars().all()

    async def get_outgoing_connections(
        self, db: AsyncSession, *, source_node_id: int
    ) -> list[WorkflowNodeConnection]:
        """Get outgoing connections from a node"""
        result = await db.execute(
            select(WorkflowNodeConnection)
            .options(selectinload(WorkflowNodeConnection.target_node))
            .where(WorkflowNodeConnection.source_node_id == source_node_id)
            .order_by(WorkflowNodeConnection.condition_type)
        )
        return result.scalars().all()

    async def get_incoming_connections(
        self, db: AsyncSession, *, target_node_id: int
    ) -> list[WorkflowNodeConnection]:
        """Get incoming connections to a node"""
        result = await db.execute(
            select(WorkflowNodeConnection)
            .options(selectinload(WorkflowNodeConnection.source_node))
            .where(WorkflowNodeConnection.target_node_id == target_node_id)
            .order_by(WorkflowNodeConnection.condition_type)
        )
        return result.scalars().all()

    async def get_connection(
        self, db: AsyncSession, *, source_node_id: int, target_node_id: int
    ) -> WorkflowNodeConnection | None:
        """Get specific connection between two nodes"""
        result = await db.execute(
            select(WorkflowNodeConnection).where(
                and_(
                    WorkflowNodeConnection.source_node_id == source_node_id,
                    WorkflowNodeConnection.target_node_id == target_node_id,
                )
            )
        )
        return result.scalars().first()

    async def create_connection(
        self,
        db: AsyncSession,
        *,
        workflow_id: int,
        source_node_id: int,
        target_node_id: int,
        condition_type: str = "success",
        condition_config: dict[str, Any] | None = None,
        label: str | None = None,
        description: str | None = None,
    ) -> WorkflowNodeConnection:
        """Create a connection between two nodes"""
        # Check if connection already exists
        existing = await self.get_connection(
            db, source_node_id=source_node_id, target_node_id=target_node_id
        )

        if existing:
            raise ValueError("Connection already exists between these nodes")

        connection_data = {
            "workflow_id": workflow_id,
            "source_node_id": source_node_id,
            "target_node_id": target_node_id,
            "condition_type": condition_type,
            "condition_config": condition_config,
            "label": label,
            "description": description,
        }

        return await self.create(db, obj_in=connection_data)

    async def update_connection(
        self,
        db: AsyncSession,
        *,
        connection: WorkflowNodeConnection,
        condition_type: str | None = None,
        condition_config: dict[str, Any] | None = None,
        label: str | None = None,
        description: str | None = None,
    ) -> WorkflowNodeConnection:
        """Update a node connection"""
        if condition_type is not None:
            connection.condition_type = condition_type

        if condition_config is not None:
            connection.condition_config = condition_config

        if label is not None:
            connection.label = label

        if description is not None:
            connection.description = description

        await db.commit()
        await db.refresh(connection)
        return connection

    async def delete_connection(
        self, db: AsyncSession, *, connection: WorkflowNodeConnection
    ) -> bool:
        """Delete a node connection"""
        await db.delete(connection)
        await db.commit()
        return True

    async def delete_connections_for_node(
        self, db: AsyncSession, *, node_id: int
    ) -> bool:
        """Delete all connections for a node (both incoming and outgoing)"""
        # Get all connections
        connections = await db.execute(
            select(WorkflowNodeConnection).where(
                or_(
                    WorkflowNodeConnection.source_node_id == node_id,
                    WorkflowNodeConnection.target_node_id == node_id,
                )
            )
        )

        # Delete them
        for connection in connections.scalars().all():
            await db.delete(connection)

        await db.commit()
        return True

    async def bulk_create_connections(
        self, db: AsyncSession, *, workflow_id: int, connections: list[dict[str, Any]]
    ) -> list[WorkflowNodeConnection]:
        """Create multiple connections at once"""
        new_connections = []

        for conn_data in connections:
            # Check if connection already exists
            existing = await self.get_connection(
                db,
                source_node_id=conn_data["source_node_id"],
                target_node_id=conn_data["target_node_id"],
            )

            if not existing:
                connection = WorkflowNodeConnection(
                    workflow_id=workflow_id,
                    source_node_id=conn_data["source_node_id"],
                    target_node_id=conn_data["target_node_id"],
                    condition_type=conn_data.get("condition_type", "success"),
                    condition_config=conn_data.get("condition_config"),
                    label=conn_data.get("label"),
                    description=conn_data.get("description"),
                )
                db.add(connection)
                new_connections.append(connection)

        if new_connections:
            await db.commit()
            for connection in new_connections:
                await db.refresh(connection)

        return new_connections

    async def validate_workflow_flow(
        self, db: AsyncSession, *, workflow_id: int
    ) -> dict[str, Any]:
        """Validate the flow of a workflow"""
        # Get all connections and nodes for the workflow
        connections = await self.get_by_workflow_id(db, workflow_id=workflow_id)

        # Import here to avoid circular imports
        from app.crud.workflow.workflow_node import workflow_node

        nodes = await workflow_node.get_by_workflow_id(db, workflow_id=workflow_id)

        issues = []
        warnings = []

        # Check for orphaned nodes (no incoming or outgoing connections)
        node_ids = {node.id for node in nodes}
        connected_nodes = set()

        for conn in connections:
            connected_nodes.add(conn.source_node_id)
            connected_nodes.add(conn.target_node_id)

        orphaned_nodes = node_ids - connected_nodes
        if len(orphaned_nodes) > 1:  # Allow one orphaned node (could be start or end)
            issues.append(
                {
                    "type": "orphaned_nodes",
                    "message": f"Found {len(orphaned_nodes)} orphaned nodes",
                    "node_ids": list(orphaned_nodes),
                }
            )

        # Check for cycles
        def has_cycle(node_id: int, visited: set, rec_stack: set) -> bool:
            visited.add(node_id)
            rec_stack.add(node_id)

            # Get outgoing connections
            outgoing = [c for c in connections if c.source_node_id == node_id]

            for conn in outgoing:
                target_id = conn.target_node_id
                if target_id not in visited:
                    if has_cycle(target_id, visited, rec_stack):
                        return True
                elif target_id in rec_stack:
                    return True

            rec_stack.remove(node_id)
            return False

        visited = set()
        for node in nodes:
            if node.id not in visited:
                if has_cycle(node.id, visited, set()):
                    issues.append(
                        {
                            "type": "cycle_detected",
                            "message": "Process contains cycles which may cause infinite loops",
                        }
                    )
                    break

        # Check for unreachable nodes
        # Find start nodes (no incoming connections or sequence_order = 1)
        start_nodes = [
            n
            for n in nodes
            if n.sequence_order == 1
            or not any(c.target_node_id == n.id for c in connections)
        ]

        if not start_nodes:
            issues.append(
                {"type": "no_start_node", "message": "Process has no clear start node"}
            )
        elif len(start_nodes) > 1:
            warnings.append(
                {
                    "type": "multiple_start_nodes",
                    "message": f"Process has {len(start_nodes)} potential start nodes",
                }
            )

        # Check for unreachable end states
        end_nodes = [
            n for n in nodes if not any(c.source_node_id == n.id for c in connections)
        ]

        if not end_nodes:
            warnings.append(
                {"type": "no_end_node", "message": "Process has no clear end node"}
            )

        return {
            "is_valid": len(issues) == 0,
            "issues": issues,
            "warnings": warnings,
            "total_nodes": len(nodes),
            "total_connections": len(connections),
            "start_nodes": len(start_nodes),
            "end_nodes": len(end_nodes),
        }

    async def get_workflow_paths(
        self, db: AsyncSession, *, workflow_id: int, start_node_id: int | None = None
    ) -> list[list[int]]:
        """Get all possible paths through the workflow"""
        connections = await self.get_by_workflow_id(db, workflow_id=workflow_id)

        # Build adjacency list
        adj_list = {}
        for conn in connections:
            if conn.source_node_id not in adj_list:
                adj_list[conn.source_node_id] = []
            adj_list[conn.source_node_id].append(conn.target_node_id)

        paths = []

        def find_paths(current_node: int, path: list[int], visited: set):
            if current_node in visited:
                return  # Cycle detected, stop this path

            visited.add(current_node)
            path.append(current_node)

            # If no outgoing connections, this is an end node
            if current_node not in adj_list:
                paths.append(path.copy())
            else:
                # Continue to next nodes
                for next_node in adj_list[current_node]:
                    find_paths(next_node, path, visited.copy())

            path.pop()

        # If start_node_id provided, use it, otherwise find start nodes
        if start_node_id:
            find_paths(start_node_id, [], set())
        else:
            # Find start nodes (nodes with no incoming connections)
            all_targets = {conn.target_node_id for conn in connections}
            all_sources = {conn.source_node_id for conn in connections}
            start_nodes = all_sources - all_targets

            for start_node in start_nodes:
                find_paths(start_node, [], set())

        return paths


workflow_node_connection = CRUDWorkflowNodeConnection(WorkflowNodeConnection)
