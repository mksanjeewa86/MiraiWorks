from __future__ import annotations

import logging
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.recruitment_workflow.process_node import process_node
from app.crud.recruitment_workflow.recruitment_process import recruitment_process
from app.crud.todo import todo as todo_crud
from app.database import get_db
from app.dependencies import get_current_active_user
from app.models.user import User
from app.schemas.recruitment_workflow.enums import NodeType
from app.schemas.recruitment_workflow.process_node import (
    NodeIntegrationInterview,
    NodeIntegrationTodo,
    ProcessNodeCreate,
    ProcessNodeCreateWithIntegration,
    ProcessNodeInfo,
    ProcessNodeUpdate,
)
from app.schemas.todo import TodoCreate
from app.services.interview_service import interview_service
from app.utils.constants import TodoType, TodoVisibility

router = APIRouter()
logger = logging.getLogger(__name__)

ALLOWED_NODE_TYPES: set[str] = {NodeType.INTERVIEW.value, NodeType.TODO.value}


def _get_user_roles(user: User) -> set[str]:
    return {user_role.role.name for user_role in user.user_roles}


def _ensure_process_can_be_edited(process, user: User) -> Response:
    roles = _get_user_roles(user)
    if "super_admin" in roles:
        return

    if not roles.intersection({"employer", "company_admin"}):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only employers or company admins can modify recruitment workflows",
        )

    if process.employer_company_id != user.company_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this recruitment process",
        )

    if not process.can_be_edited:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Process can only be edited while in draft or inactive status",
        )


def _ensure_node_type_allowed(node_type: NodeType | str) -> Response:
    value = node_type.value if isinstance(node_type, NodeType) else str(node_type)
    if value not in ALLOWED_NODE_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only interview and todo nodes are supported in the visual editor",
        )


def _normalise_position(node_dict: dict[str, object]) -> Response:
    position = node_dict.pop("position", None)
    if isinstance(position, dict):
        node_dict["position_x"] = position.get("x", 0)
        node_dict["position_y"] = position.get("y", 0)


def _serialise_node(node) -> ProcessNodeInfo:
    return ProcessNodeInfo.model_validate(node, from_attributes=True)


async def _load_process(db: AsyncSession, process_id: int):
    process = await recruitment_process.get(db, id=process_id)
    if not process:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recruitment process not found",
        )
    return process


async def _shift_sequence_numbers(
    db: AsyncSession,
    *,
    process_id: int,
    starting_order: int,
    updated_by: int,
) -> Response:
    existing_nodes = await process_node.get_by_process_id(
        db, process_id=process_id, include_inactive=True
    )
    updates: list[dict[str, int]] = []
    for node in existing_nodes:
        if node.sequence_order >= starting_order:
            updates.append({"node_id": node.id, "sequence_order": node.sequence_order + 1})

    if updates:
        await process_node.reorder_nodes(
            db,
            process_id=process_id,
            node_sequence_updates=updates,
            updated_by=updated_by
        )

    return Response(status_code=status.HTTP_204_NO_CONTENT)

async def _create_node(
    db: AsyncSession,
    *,
    process_id: int,
    node_data: ProcessNodeCreate,
    actor: User,
):
    # Exclude integration fields (create_interview, create_todo) from node creation
    payload = node_data.model_dump(exclude={'create_interview', 'create_todo'})
    payload["process_id"] = process_id
    payload.setdefault("config", {})

    sequence_order = int(payload.get("sequence_order") or 0)
    if sequence_order <= 0:
        existing = await process_node.get_by_process_id(
            db, process_id=process_id, include_inactive=True
        )
        payload["sequence_order"] = len(existing) + 1
    else:
        await _shift_sequence_numbers(
            db,
            process_id=process_id,
            starting_order=sequence_order,
            updated_by=actor.id,
        )
        payload["sequence_order"] = sequence_order

    _normalise_position(payload)

    created_node = await process_node.create(
        db,
        obj_in=payload,
        created_by=actor.id,
    )
    return created_node


async def _create_interview_integration(
    db: AsyncSession,
    *,
    process,
    node,
    integration: NodeIntegrationInterview,
    actor: User,
):
    if not integration or not integration.candidate_id:
        return None

    scheduled_end: datetime | None = None
    if integration.scheduled_at and integration.duration_minutes:
        scheduled_end = integration.scheduled_at + timedelta(minutes=integration.duration_minutes)

    interview_type = integration.interview_type
    if not interview_type:
        interview_type = (node.config or {}).get("interview_type")

    try:
        interview = await interview_service.create_interview(
            db=db,
            candidate_id=integration.candidate_id,
            recruiter_id=integration.recruiter_id or actor.id,
            employer_company_id=process.employer_company_id,
            title=node.title,
            description=node.description,
            interview_type=interview_type or "video",
            created_by=actor.id,
            scheduled_start=integration.scheduled_at,
            scheduled_end=scheduled_end,
            location=integration.location,
            meeting_url=integration.meeting_link,
            notes=integration.notes,
        )
    except Exception as exc:  # pragma: no cover - defensive logging
        logger.warning("Failed to create interview integration: %s", exc)
        return None

    return jsonable_encoder(interview)


async def _create_todo_integration(
    db: AsyncSession,
    *,
    node,
    integration: NodeIntegrationTodo,
    actor: User,
):
    if not integration:
        return None

    due_in_days = integration.due_in_days
    if due_in_days is None:
        due_in_days = (node.config or {}).get("due_in_days")
    due_date: datetime | None = None
    if due_in_days:
        due_date = datetime.utcnow() + timedelta(days=due_in_days)

    todo_type = TodoType.ASSIGNMENT.value
    if integration.is_assignment is False:
        todo_type = TodoType.REGULAR.value

    todo_payload = TodoCreate(
        title=integration.title or node.title,
        description=integration.description or node.description,
        priority=integration.priority,
        due_date=due_date,
        assigned_user_id=integration.assigned_to,
        todo_type=todo_type,
        visibility=(
            TodoVisibility.PUBLIC.value
            if integration.assigned_to is not None
            else TodoVisibility.PRIVATE.value
        ),
    )

    try:
        todo = await todo_crud.create_for_user(
            db,
            owner_id=actor.id,
            created_by=actor.id,
            obj_in=todo_payload,
        )
    except Exception as exc:  # pragma: no cover - defensive logging
        logger.warning("Failed to create todo integration: %s", exc)
        return None

    return jsonable_encoder(todo)


@router.post(
    "/{process_id}/nodes",
    response_model=ProcessNodeInfo,
    status_code=status.HTTP_201_CREATED,
)
async def create_process_node_endpoint(
    process_id: int,
    node_data: ProcessNodeCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> ProcessNodeInfo:
    process = await _load_process(db, process_id)
    _ensure_process_can_be_edited(process, current_user)
    _ensure_node_type_allowed(node_data.node_type)

    node = await _create_node(
        db,
        process_id=process_id,
        node_data=node_data,
        actor=current_user,
    )
    return _serialise_node(node)


@router.post(
    "/{process_id}/nodes/create-with-integration",
    status_code=status.HTTP_201_CREATED,
)
async def create_process_node_with_integration(
    process_id: int,
    node_data: ProcessNodeCreateWithIntegration,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> dict[str, object]:
    process = await _load_process(db, process_id)
    _ensure_process_can_be_edited(process, current_user)
    _ensure_node_type_allowed(node_data.node_type)

    node = await _create_node(
        db,
        process_id=process_id,
        node_data=node_data,
        actor=current_user,
    )

    created_interview = None
    created_todo = None

    if node.node_type == NodeType.INTERVIEW.value:
        created_interview = await _create_interview_integration(
            db,
            process=process,
            node=node,
            integration=node_data.create_interview,
            actor=current_user,
        )
    elif node.node_type == NodeType.TODO.value:
        created_todo = await _create_todo_integration(
            db,
            node=node,
            integration=node_data.create_todo,
            actor=current_user,
        )

    return {
        "node": _serialise_node(node),
        "interview": created_interview,
        "todo": created_todo,
    }


@router.put(
    "/{process_id}/nodes/{node_id}",
    response_model=ProcessNodeInfo,
)
async def update_process_node_endpoint(
    process_id: int,
    node_id: int,
    node_update: ProcessNodeUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> ProcessNodeInfo:
    process = await _load_process(db, process_id)
    node = await process_node.get(db, id=node_id)
    if not node or node.process_id != process_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Process node not found",
        )

    _ensure_process_can_be_edited(process, current_user)

    update_data = node_update.model_dump(exclude_unset=True)
    _normalise_position(update_data)
    update_data["updated_by"] = current_user.id

    updated_node = await process_node.update(
        db,
        db_obj=node,
        obj_in=update_data,
    )

    return _serialise_node(updated_node)


@router.delete("/{process_id}/nodes/{node_id}", status_code=status.HTTP_204_NO_CONTENT, response_class=Response)
async def delete_process_node_endpoint(
    process_id: int,
    node_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Response:
    process = await _load_process(db, process_id)
    node = await process_node.get(db, id=node_id)
    if not node or node.process_id != process_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Process node not found",
        )

    _ensure_process_can_be_edited(process, current_user)

    can_delete = await process_node.can_delete_node(db, node_id=node_id)
    if not can_delete:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Node cannot be deleted because it has execution history",
        )

    success = await process_node.delete_with_connections(db, node_id=node_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete process node",
        )

    # Resequence remaining nodes to keep workflow linear
    remaining_nodes = await process_node.get_by_process_id(
        db,
        process_id=process_id,
        include_inactive=True,
    )
    updates: list[dict[str, int]] = []
    for order, workflow_node in enumerate(sorted(remaining_nodes, key=lambda n: n.sequence_order), start=1):
        if workflow_node.sequence_order != order:
            updates.append({"node_id": workflow_node.id, "sequence_order": order})

    if updates:
        await process_node.reorder_nodes(
            db,
            process_id=process_id,
            node_sequence_updates=updates,
            updated_by=current_user.id,
        )

    return Response(status_code=status.HTTP_204_NO_CONTENT)

