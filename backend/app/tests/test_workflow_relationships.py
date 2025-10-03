"""
Test workflow relationships between recruitment processes, interviews, and todos.
Tests the cascading soft delete functionality.
"""

import pytest
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.recruitment_process import RecruitmentProcess
from app.models.interview import Interview
from app.models.todo import Todo
from app.crud.recruitment_workflow.recruitment_process import recruitment_process


@pytest.mark.asyncio
class TestWorkflowRelationships:
    """Test suite for workflow relationships and cascading soft delete."""

    async def test_create_workflow_with_relationships(
        self,
        db_session: AsyncSession,
        test_company,
        test_user
    ):
        """Test creating a workflow and associating interviews and todos."""
        # Create workflow
        workflow_data = {
            "name": "Test Workflow with Relations",
            "description": "Testing workflow relationships",
            "employer_company_id": test_company.id,
            "status": "active"
        }
        
        workflow = await recruitment_process.create(
            db_session,
            obj_in=workflow_data,
            created_by=test_user.id
        )
        
        assert workflow.id is not None
        assert workflow.name == workflow_data["name"]
        
        # Create associated interview
        interview = Interview(
            workflow_id=workflow.id,
            candidate_id=test_user.id,
            recruiter_id=test_user.id,
            employer_company_id=test_company.id,
            recruiter_company_id=test_company.id,
            title="Technical Interview",
            status="scheduled",
            interview_type="video"
        )
        db_session.add(interview)
        
        # Create associated todo
        todo = Todo(
            workflow_id=workflow.id,
            owner_id=test_user.id,
            title="Review candidate resume",
            status="pending"
        )
        db_session.add(todo)
        
        await db_session.commit()
        
        # Verify relationships
        result = await db_session.execute(
            select(Interview).where(Interview.workflow_id == workflow.id)
        )
        interviews = result.scalars().all()
        assert len(interviews) == 1
        assert interviews[0].workflow_id == workflow.id
        
        result = await db_session.execute(
            select(Todo).where(Todo.workflow_id == workflow.id)
        )
        todos = result.scalars().all()
        assert len(todos) == 1
        assert todos[0].workflow_id == workflow.id

    async def test_cascading_soft_delete(
        self,
        db_session: AsyncSession,
        test_company,
        test_user
    ):
        """Test that soft deleting a workflow cascades to interviews and todos."""
        # Create workflow
        workflow_data = {
            "name": "Workflow for Cascade Test",
            "description": "Testing cascading soft delete",
            "employer_company_id": test_company.id,
            "status": "active"
        }
        
        workflow = await recruitment_process.create(
            db_session,
            obj_in=workflow_data,
            created_by=test_user.id
        )
        
        # Create multiple associated records
        interviews = []
        for i in range(3):
            interview = Interview(
                workflow_id=workflow.id,
                candidate_id=test_user.id,
                recruiter_id=test_user.id,
                employer_company_id=test_company.id,
                recruiter_company_id=test_company.id,
                title=f"Interview {i+1}",
                status="scheduled",
                interview_type="video"
            )
            db_session.add(interview)
            interviews.append(interview)
        
        todos = []
        for i in range(2):
            todo = Todo(
                workflow_id=workflow.id,
                owner_id=test_user.id,
                title=f"Task {i+1}",
                status="pending"
            )
            db_session.add(todo)
            todos.append(todo)
        
        await db_session.commit()
        
        # Verify all records are not deleted
        result = await db_session.execute(
            select(Interview).where(
                Interview.workflow_id == workflow.id,
                Interview.is_deleted == False
            )
        )
        assert len(result.scalars().all()) == 3
        
        result = await db_session.execute(
            select(Todo).where(
                Todo.workflow_id == workflow.id,
                Todo.is_deleted == False
            )
        )
        assert len(result.scalars().all()) == 2
        
        # Soft delete the workflow
        deleted_workflow = await recruitment_process.soft_delete(db, id=workflow.id)
        
        # Verify workflow is soft deleted
        assert deleted_workflow.is_deleted is True
        assert deleted_workflow.deleted_at is not None
        
        # Verify all interviews are soft deleted
        result = await db_session.execute(
            select(Interview).where(
                Interview.workflow_id == workflow.id,
                Interview.is_deleted == True
            )
        )
        deleted_interviews = result.scalars().all()
        assert len(deleted_interviews) == 3
        for interview in deleted_interviews:
            assert interview.deleted_at is not None
            assert interview.workflow_id == workflow.id  # Relationship preserved
        
        # Verify all todos are soft deleted
        result = await db_session.execute(
            select(Todo).where(
                Todo.workflow_id == workflow.id,
                Todo.is_deleted == True
            )
        )
        deleted_todos = result.scalars().all()
        assert len(deleted_todos) == 2
        for todo in deleted_todos:
            assert todo.deleted_at is not None
            assert todo.workflow_id == workflow.id  # Relationship preserved

    async def test_soft_delete_only_affects_related_records(
        self,
        db_session: AsyncSession,
        test_company,
        test_user
    ):
        """Test that soft delete only affects records related to the specific workflow."""
        # Create two workflows
        workflow1 = await recruitment_process.create(
            db_session,
            obj_in={
                "name": "Workflow 1",
                "employer_company_id": test_company.id,
                "status": "active"
            },
            created_by=test_user.id
        )
        
        workflow2 = await recruitment_process.create(
            db_session,
            obj_in={
                "name": "Workflow 2",
                "employer_company_id": test_company.id,
                "status": "active"
            },
            created_by=test_user.id
        )
        
        # Create interviews for both workflows
        interview1 = Interview(
            workflow_id=workflow1.id,
            candidate_id=test_user.id,
            recruiter_id=test_user.id,
            employer_company_id=test_company.id,
            recruiter_company_id=test_company.id,
            title="Interview for Workflow 1",
            status="scheduled",
            interview_type="video"
        )
        
        interview2 = Interview(
            workflow_id=workflow2.id,
            candidate_id=test_user.id,
            recruiter_id=test_user.id,
            employer_company_id=test_company.id,
            recruiter_company_id=test_company.id,
            title="Interview for Workflow 2",
            status="scheduled",
            interview_type="video"
        )
        
        # Create interview without workflow
        interview_no_workflow = Interview(
            workflow_id=None,
            candidate_id=test_user.id,
            recruiter_id=test_user.id,
            employer_company_id=test_company.id,
            recruiter_company_id=test_company.id,
            title="Interview without Workflow",
            status="scheduled",
            interview_type="video"
        )
        
        db.add_all([interview1, interview2, interview_no_workflow])
        await db_session.commit()
        
        # Soft delete workflow1
        await recruitment_process.soft_delete(db, id=workflow1.id)
        
        # Verify only workflow1's interview is deleted
        result = await db_session.execute(
            select(Interview).where(Interview.id == interview1.id)
        )
        deleted_interview = result.scalar_one()
        assert deleted_interview.is_deleted is True
        
        # Verify workflow2's interview is not deleted
        result = await db_session.execute(
            select(Interview).where(Interview.id == interview2.id)
        )
        active_interview = result.scalar_one()
        assert active_interview.is_deleted is False
        
        # Verify interview without workflow is not affected
        result = await db_session.execute(
            select(Interview).where(Interview.id == interview_no_workflow.id)
        )
        unrelated_interview = result.scalar_one()
        assert unrelated_interview.is_deleted is False

    async def test_workflow_relationships_in_schemas(
        self,
        db_session: AsyncSession,
        test_company,
        test_user
    ):
        """Test that workflow_id is properly handled in create/update schemas."""
        from app.schemas.interview import InterviewCreate
        from app.schemas.todo import TodoCreate
        
        # Create workflow
        workflow = await recruitment_process.create(
            db_session,
            obj_in={
                "name": "Schema Test Workflow",
                "employer_company_id": test_company.id,
                "status": "active"
            },
            created_by=test_user.id
        )
        
        # Test InterviewCreate with workflow_id
        interview_data = InterviewCreate(
            candidate_id=test_user.id,
            recruiter_id=test_user.id,
            employer_company_id=test_company.id,
            workflow_id=workflow.id,  # This should be accepted
            title="Schema Test Interview"
        )
        
        assert interview_data.workflow_id == workflow.id
        
        # Test TodoCreate with workflow_id
        todo_data = TodoCreate(
            title="Schema Test Todo",
            workflow_id=workflow.id  # This should be accepted
        )
        
        assert todo_data.workflow_id == workflow.id

    async def test_filter_by_workflow_id(
        self,
        db_session: AsyncSession,
        test_company,
        test_user
    ):
        """Test filtering interviews and todos by workflow_id."""
        # Create workflow
        workflow = await recruitment_process.create(
            db_session,
            obj_in={
                "name": "Filter Test Workflow",
                "employer_company_id": test_company.id,
                "status": "active"
            },
            created_by=test_user.id
        )
        
        # Create mixed records
        for i in range(5):
            interview = Interview(
                workflow_id=workflow.id if i < 3 else None,
                candidate_id=test_user.id,
                recruiter_id=test_user.id,
                employer_company_id=test_company.id,
                recruiter_company_id=test_company.id,
                title=f"Interview {i+1}",
                status="scheduled",
                interview_type="video"
            )
            db_session.add(interview)
        
        await db_session.commit()
        
        # Filter interviews by workflow_id
        result = await db_session.execute(
            select(Interview).where(
                Interview.workflow_id == workflow.id,
                Interview.is_deleted == False
            )
        )
        workflow_interviews = result.scalars().all()
        assert len(workflow_interviews) == 3
        
        # Filter interviews without workflow
        result = await db_session.execute(
            select(Interview).where(
                Interview.workflow_id.is_(None),
                Interview.is_deleted == False
            )
        )
        standalone_interviews = result.scalars().all()
        assert len(standalone_interviews) == 2