"""Integration tests for workflow relationships and cascading soft delete."""

from datetime import timedelta

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.workflow.workflow import workflow as workflow_crud
from app.models.interview import Interview
from app.models.todo import Todo
from app.models.user import User
from app.utils.datetime_utils import get_utc_now


@pytest.mark.asyncio
async def test_create_workflow_with_linked_interviews_and_todos(
    client: AsyncClient,
    db_session: AsyncSession,
    auth_headers: dict,
    test_employer_user: User,
):
    """Test creating a workflow and linking interviews and todos to it."""
    # Create workflow
    workflow_data = {
        "name": "Software Engineer Recruitment",
        "description": "Full recruitment workflow for engineering position",
        "employer_company_id": test_employer_user.company_id,
        "status": "draft",
    }

    workflow = await workflow_crud.create(
        db=db_session,
        obj_in=workflow_data,
        created_by=test_employer_user.id,
    )

    assert workflow.id is not None
    assert workflow.name == workflow_data["name"]

    # Create interview linked to workflow
    interview = Interview(
        title="Technical Interview",
        description="Review technical skills",
        workflow_id=workflow.id,
        employer_company_id=test_employer_user.company_id,
        created_by=test_employer_user.id,
        interview_type="video",
        status="pending_schedule",
        scheduled_start=get_utc_now() + timedelta(days=1),
        scheduled_end=get_utc_now() + timedelta(days=1, hours=1),
        timezone="UTC",
    )
    db_session.add(interview)

    # Create todo linked to workflow
    todo = Todo(
        title="Review Resume",
        description="Check candidate background",
        workflow_id=workflow.id,
        owner_id=test_employer_user.id,
        status="pending",
        priority="high",
    )
    db_session.add(todo)

    await db_session.commit()
    await db_session.refresh(interview)
    await db_session.refresh(todo)

    # Verify relationships
    assert interview.workflow_id == workflow.id
    assert todo.workflow_id == workflow.id

    # Verify we can query by workflow
    workflow_with_relations = await workflow.get_with_nodes(
        db=db_session, id=workflow.id
    )
    assert workflow_with_relations is not None


@pytest.mark.asyncio
async def test_workflow_soft_delete_cascades_to_interviews(
    client: AsyncClient,
    db_session: AsyncSession,
    auth_headers: dict,
    test_employer_user: User,
):
    """Test that soft deleting a workflow cascades to related interviews."""
    # Create workflow
    workflow = await workflow_crud.create(
        db=db_session,
        obj_in={
            "name": "Cascade Test Workflow",
            "employer_company_id": test_employer_user.company_id,
            "status": "draft",
        },
        created_by=test_employer_user.id,
    )

    # Create multiple interviews linked to workflow
    interviews = []
    for i in range(3):
        interview = Interview(
            title=f"Interview {i + 1}",
            workflow_id=workflow.id,
            employer_company_id=test_employer_user.company_id,
            created_by=test_employer_user.id,
            interview_type="video",
            status="pending_schedule",
            scheduled_start=get_utc_now() + timedelta(days=1),
            scheduled_end=get_utc_now() + timedelta(days=1, hours=1),
            timezone="UTC",
        )
        db_session.add(interview)
        interviews.append(interview)

    await db_session.commit()

    # Refresh to get IDs
    for interview in interviews:
        await db_session.refresh(interview)

    interview_ids = [interview.id for interview in interviews]

    # Soft delete the workflow
    deleted_workflow = await workflow.soft_delete(db=db_session, id=workflow.id)

    assert deleted_workflow is not None
    assert deleted_workflow.is_deleted is True
    assert deleted_workflow.deleted_at is not None

    # Verify all interviews are soft deleted
    result = await db_session.execute(
        select(Interview).where(Interview.id.in_(interview_ids))
    )
    cascade_deleted_interviews = result.scalars().all()

    assert len(cascade_deleted_interviews) == 3
    for interview in cascade_deleted_interviews:
        assert interview.is_deleted is True
        assert interview.deleted_at is not None
        assert interview.workflow_id == workflow.id


@pytest.mark.asyncio
async def test_workflow_soft_delete_cascades_to_todos(
    client: AsyncClient,
    db_session: AsyncSession,
    auth_headers: dict,
    test_employer_user: User,
):
    """Test that soft deleting a workflow cascades to related todos."""
    # Create workflow
    workflow = await workflow_crud.create(
        db=db_session,
        obj_in={
            "name": "Todo Cascade Workflow",
            "employer_company_id": test_employer_user.company_id,
            "status": "draft",
        },
        created_by=test_employer_user.id,
    )

    # Create multiple todos linked to workflow
    todos = []
    for i in range(4):
        todo = Todo(
            title=f"Task {i + 1}",
            workflow_id=workflow.id,
            owner_id=test_employer_user.id,
            status="pending",
            priority="medium",
        )
        db_session.add(todo)
        todos.append(todo)

    await db_session.commit()

    # Refresh to get IDs
    for todo in todos:
        await db_session.refresh(todo)

    todo_ids = [todo.id for todo in todos]

    # Soft delete the workflow
    deleted_workflow = await workflow.soft_delete(db=db_session, id=workflow.id)

    assert deleted_workflow is not None
    assert deleted_workflow.is_deleted is True

    # Verify all todos are soft deleted
    result = await db_session.execute(select(Todo).where(Todo.id.in_(todo_ids)))
    cascade_deleted_todos = result.scalars().all()

    assert len(cascade_deleted_todos) == 4
    for todo in cascade_deleted_todos:
        assert todo.is_deleted is True
        assert todo.deleted_at is not None
        assert todo.workflow_id == workflow.id


@pytest.mark.asyncio
async def test_workflow_soft_delete_cascades_to_both_interviews_and_todos(
    client: AsyncClient,
    db_session: AsyncSession,
    auth_headers: dict,
    test_employer_user: User,
):
    """Test that soft deleting a workflow cascades to both interviews and todos."""
    # Create workflow
    workflow = await workflow_crud.create(
        db=db_session,
        obj_in={
            "name": "Full Cascade Workflow",
            "employer_company_id": test_employer_user.company_id,
            "status": "draft",
        },
        created_by=test_employer_user.id,
    )

    # Create interviews
    interviews = []
    for i in range(2):
        interview = Interview(
            title=f"Interview {i + 1}",
            workflow_id=workflow.id,
            employer_company_id=test_employer_user.company_id,
            created_by=test_employer_user.id,
            interview_type="video",
            status="pending_schedule",
            scheduled_start=get_utc_now() + timedelta(days=1),
            scheduled_end=get_utc_now() + timedelta(days=1, hours=1),
            timezone="UTC",
        )
        db_session.add(interview)
        interviews.append(interview)

    # Create todos
    todos = []
    for i in range(3):
        todo = Todo(
            title=f"Task {i + 1}",
            workflow_id=workflow.id,
            owner_id=test_employer_user.id,
            status="pending",
            priority="medium",
        )
        db_session.add(todo)
        todos.append(todo)

    await db_session.commit()

    # Refresh to get IDs
    for interview in interviews:
        await db_session.refresh(interview)
    for todo in todos:
        await db_session.refresh(todo)

    # Soft delete the workflow
    await workflow.soft_delete(db=db_session, id=workflow.id)

    # Verify all interviews are soft deleted
    for interview in interviews:
        await db_session.refresh(interview)
        assert interview.is_deleted is True
        assert interview.deleted_at is not None

    # Verify all todos are soft deleted
    for todo in todos:
        await db_session.refresh(todo)
        assert todo.is_deleted is True
        assert todo.deleted_at is not None


@pytest.mark.asyncio
async def test_soft_deleted_workflow_not_in_get_query(
    client: AsyncClient,
    db_session: AsyncSession,
    auth_headers: dict,
    test_employer_user: User,
):
    """Test that soft deleted workflows are excluded from get queries."""
    # Create workflow
    workflow = await workflow_crud.create(
        db=db_session,
        obj_in={
            "name": "Test Exclusion Workflow",
            "employer_company_id": test_employer_user.company_id,
            "status": "draft",
        },
        created_by=test_employer_user.id,
    )

    workflow_id = workflow.id

    # Verify workflow is retrievable before deletion
    retrieved = await workflow.get(db=db_session, id=workflow_id)
    assert retrieved is not None

    # Soft delete the workflow
    await workflow.soft_delete(db=db_session, id=workflow_id)

    # Verify workflow is not retrievable after soft deletion
    not_found = await workflow.get(db=db_session, id=workflow_id)
    assert not_found is None


@pytest.mark.asyncio
async def test_only_non_deleted_interviews_affected_by_cascade(
    client: AsyncClient,
    db_session: AsyncSession,
    auth_headers: dict,
    test_employer_user: User,
):
    """Test that only non-deleted interviews are affected by cascade."""
    # Create workflow
    workflow = await workflow_crud.create(
        db=db_session,
        obj_in={
            "name": "Selective Cascade Workflow",
            "employer_company_id": test_employer_user.company_id,
            "status": "draft",
        },
        created_by=test_employer_user.id,
    )

    # Create interview 1 (will be kept active)
    interview1 = Interview(
        title="Active Interview",
        workflow_id=workflow.id,
        employer_company_id=test_employer_user.company_id,
        created_by=test_employer_user.id,
        interview_type="video",
        status="pending_schedule",
        scheduled_start=get_utc_now() + timedelta(days=1),
        scheduled_end=get_utc_now() + timedelta(days=1, hours=1),
        timezone="UTC",
        is_deleted=False,
    )
    db_session.add(interview1)

    # Create interview 2 (already soft deleted)
    interview2 = Interview(
        title="Already Deleted Interview",
        workflow_id=workflow.id,
        employer_company_id=test_employer_user.company_id,
        created_by=test_employer_user.id,
        interview_type="video",
        status="pending_schedule",
        scheduled_start=get_utc_now() + timedelta(days=1),
        scheduled_end=get_utc_now() + timedelta(days=1, hours=1),
        timezone="UTC",
        is_deleted=True,
        deleted_at=get_utc_now() - timedelta(days=1),
    )
    db_session.add(interview2)

    await db_session.commit()
    await db_session.refresh(interview1)
    await db_session.refresh(interview2)

    initial_deleted_at = interview2.deleted_at

    # Soft delete the workflow
    await workflow.soft_delete(db=db_session, id=workflow.id)

    # Verify interview1 is now soft deleted
    await db_session.refresh(interview1)
    assert interview1.is_deleted is True
    assert interview1.deleted_at is not None

    # Verify interview2's deleted_at timestamp is unchanged
    await db_session.refresh(interview2)
    assert interview2.is_deleted is True
    assert interview2.deleted_at == initial_deleted_at


@pytest.mark.asyncio
async def test_workflow_foreign_key_set_null_on_hard_delete(
    client: AsyncClient,
    db_session: AsyncSession,
    auth_headers: dict,
    test_employer_user: User,
):
    """Test that workflow_id is set to NULL when workflow is hard deleted from DB."""
    # Create workflow
    workflow = await workflow_crud.create(
        db=db_session,
        obj_in={
            "name": "Hard Delete Test Workflow",
            "employer_company_id": test_employer_user.company_id,
            "status": "draft",
        },
        created_by=test_employer_user.id,
    )

    # Create interview linked to workflow
    interview = Interview(
        title="Test Interview",
        workflow_id=workflow.id,
        employer_company_id=test_employer_user.company_id,
        created_by=test_employer_user.id,
        interview_type="video",
        status="pending_schedule",
        scheduled_start=get_utc_now() + timedelta(days=1),
        scheduled_end=get_utc_now() + timedelta(days=1, hours=1),
        timezone="UTC",
    )
    db_session.add(interview)

    await db_session.commit()
    await db_session.refresh(interview)

    interview_id = interview.id
    assert interview.workflow_id == workflow.id

    # Hard delete the workflow from database
    await db_session.delete(workflow)
    await db_session.commit()

    # Verify interview still exists but workflow_id is NULL
    result = await db_session.execute(
        select(Interview).where(Interview.id == interview_id)
    )
    remaining_interview = result.scalar_one_or_none()

    assert remaining_interview is not None
    assert remaining_interview.workflow_id is None
    assert remaining_interview.is_deleted is False  # Not soft deleted


@pytest.mark.asyncio
async def test_interviews_and_todos_without_workflow_unaffected(
    client: AsyncClient,
    db_session: AsyncSession,
    auth_headers: dict,
    test_employer_user: User,
):
    """Test that interviews and todos without workflow_id are unaffected."""
    # Create workflow
    workflow = await workflow_crud.create(
        db=db_session,
        obj_in={
            "name": "Isolated Workflow",
            "employer_company_id": test_employer_user.company_id,
            "status": "draft",
        },
        created_by=test_employer_user.id,
    )

    # Create interview WITHOUT workflow_id
    standalone_interview = Interview(
        title="Standalone Interview",
        workflow_id=None,
        employer_company_id=test_employer_user.company_id,
        created_by=test_employer_user.id,
        interview_type="video",
        status="pending_schedule",
        scheduled_start=get_utc_now() + timedelta(days=1),
        scheduled_end=get_utc_now() + timedelta(days=1, hours=1),
        timezone="UTC",
    )
    db_session.add(standalone_interview)

    # Create todo WITHOUT workflow_id
    standalone_todo = Todo(
        title="Standalone Task",
        workflow_id=None,
        owner_id=test_employer_user.id,
        status="pending",
        priority="low",
    )
    db_session.add(standalone_todo)

    await db_session.commit()
    await db_session.refresh(standalone_interview)
    await db_session.refresh(standalone_todo)

    # Soft delete the workflow
    await workflow.soft_delete(db=db_session, id=workflow.id)

    # Verify standalone records are unaffected
    await db_session.refresh(standalone_interview)
    await db_session.refresh(standalone_todo)

    assert standalone_interview.is_deleted is False
    assert standalone_interview.deleted_at is None
    assert standalone_todo.is_deleted is False
    assert standalone_todo.deleted_at is None


@pytest.mark.asyncio
async def test_query_workflows_with_interview_count(
    client: AsyncClient,
    db_session: AsyncSession,
    auth_headers: dict,
    test_employer_user: User,
):
    """Test querying workflows with counts of related interviews."""
    # Create workflow
    workflow = await workflow_crud.create(
        db=db_session,
        obj_in={
            "name": "Count Test Workflow",
            "employer_company_id": test_employer_user.company_id,
            "status": "draft",
        },
        created_by=test_employer_user.id,
    )

    # Create interviews
    for i in range(5):
        interview = Interview(
            title=f"Interview {i + 1}",
            workflow_id=workflow.id,
            employer_company_id=test_employer_user.company_id,
            created_by=test_employer_user.id,
            interview_type="video",
            status="pending_schedule",
            scheduled_start=get_utc_now() + timedelta(days=1),
            scheduled_end=get_utc_now() + timedelta(days=1, hours=1),
            timezone="UTC",
        )
        db_session.add(interview)

    await db_session.commit()

    # Query interviews linked to workflow
    result = await db_session.execute(
        select(Interview).where(
            Interview.workflow_id == workflow.id, Interview.is_deleted == False
        )
    )
    interviews = result.scalars().all()

    assert len(interviews) == 5


@pytest.mark.asyncio
async def test_query_workflows_with_todo_count(
    client: AsyncClient,
    db_session: AsyncSession,
    auth_headers: dict,
    test_employer_user: User,
):
    """Test querying workflows with counts of related todos."""
    # Create workflow
    workflow = await workflow_crud.create(
        db=db_session,
        obj_in={
            "name": "Todo Count Workflow",
            "employer_company_id": test_employer_user.company_id,
            "status": "draft",
        },
        created_by=test_employer_user.id,
    )

    # Create todos
    for i in range(7):
        todo = Todo(
            title=f"Task {i + 1}",
            workflow_id=workflow.id,
            owner_id=test_employer_user.id,
            status="pending",
            priority="medium",
        )
        db_session.add(todo)

    await db_session.commit()

    # Query todos linked to workflow
    result = await db_session.execute(
        select(Todo).where(Todo.workflow_id == workflow.id, Todo.is_deleted == False)
    )
    todos = result.scalars().all()

    assert len(todos) == 7
