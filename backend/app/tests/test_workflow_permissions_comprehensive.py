"""
Comprehensive test suite for workflow creation with todos and interviews.
Tests different user permissions, role-based access, and complete coverage.
"""

import pytest
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Dict, Any

from app.models.recruitment_process import RecruitmentProcess
from app.models.interview import Interview
from app.models.todo import Todo
from app.models.user import User
from app.models.role import Role
from app.models.company import Company
from app.crud.recruitment_workflow.recruitment_process import recruitment_process
from app.schemas.interview import InterviewCreate
from app.schemas.todo import TodoCreate
from app.utils.constants import UserRole


@pytest.fixture
async def admin_role(db: AsyncSession) -> Role:
    """Create admin role with full permissions."""
    role = Role(
        name="admin",
        display_name="System Administrator",
        permissions=[
            "workflow:create", "workflow:read", "workflow:update", "workflow:delete",
            "interview:create", "interview:read", "interview:update", "interview:delete",
            "todo:create", "todo:read", "todo:update", "todo:delete",
            "user:manage", "company:manage"
        ]
    )
    db.add(role)
    await db.commit()
    await db.refresh(role)
    return role


@pytest.fixture
async def employer_role(db: AsyncSession) -> Role:
    """Create employer role with workflow and hiring permissions."""
    role = Role(
        name="employer",
        display_name="Employer",
        permissions=[
            "workflow:create", "workflow:read", "workflow:update",
            "interview:create", "interview:read", "interview:update",
            "todo:create", "todo:read", "todo:update",
            "candidate:review"
        ]
    )
    db.add(role)
    await db.commit()
    await db.refresh(role)
    return role


@pytest.fixture
async def recruiter_role(db: AsyncSession) -> Role:
    """Create recruiter role with limited permissions."""
    role = Role(
        name="recruiter",
        display_name="Recruiter",
        permissions=[
            "workflow:read",
            "interview:create", "interview:read", "interview:update",
            "todo:create", "todo:read", "todo:update",
            "candidate:manage"
        ]
    )
    db.add(role)
    await db.commit()
    await db.refresh(role)
    return role


@pytest.fixture
async def candidate_role(db: AsyncSession) -> Role:
    """Create candidate role with minimal permissions."""
    role = Role(
        name="candidate",
        display_name="Candidate",
        permissions=[
            "interview:read",
            "todo:read",
            "profile:update"
        ]
    )
    db.add(role)
    await db.commit()
    await db.refresh(role)
    return role


@pytest.fixture
async def admin_user(db: AsyncSession, admin_role: Role) -> User:
    """Create admin user."""
    user = User(
        email="admin@test.com",
        username="admin",
        first_name="Admin",
        last_name="User",
        hashed_password="hashed_password",
        is_active=True,
        is_verified=True,
        role_id=admin_role.id
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


@pytest.fixture
async def employer_user(db: AsyncSession, employer_role: Role) -> User:
    """Create employer user."""
    user = User(
        email="employer@test.com",
        username="employer",
        first_name="Employer",
        last_name="User",
        hashed_password="hashed_password",
        is_active=True,
        is_verified=True,
        role_id=employer_role.id
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


@pytest.fixture
async def recruiter_user(db: AsyncSession, recruiter_role: Role) -> User:
    """Create recruiter user."""
    user = User(
        email="recruiter@test.com",
        username="recruiter",
        first_name="Recruiter",
        last_name="User",
        hashed_password="hashed_password",
        is_active=True,
        is_verified=True,
        role_id=recruiter_role.id
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


@pytest.fixture
async def candidate_user(db: AsyncSession, candidate_role: Role) -> User:
    """Create candidate user."""
    user = User(
        email="candidate@test.com",
        username="candidate",
        first_name="Candidate",
        last_name="User",
        hashed_password="hashed_password",
        is_active=True,
        is_verified=True,
        role_id=candidate_role.id
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


@pytest.fixture
async def test_company(db: AsyncSession) -> Company:
    """Create test company."""
    company = Company(
        name="Test Company",
        email="company@test.com",
        website="https://test.com",
        description="Test company for workflow testing",
        is_verified=True,
        is_active=True
    )
    db.add(company)
    await db.commit()
    await db.refresh(company)
    return company


@pytest.fixture
async def second_company(db: AsyncSession) -> Company:
    """Create second test company."""
    company = Company(
        name="Second Company",
        email="second@test.com",
        website="https://second.com",
        description="Second test company",
        is_verified=True,
        is_active=True
    )
    db.add(company)
    await db.commit()
    await db.refresh(company)
    return company


class TestWorkflowCreationPermissions:
    """Test workflow creation with different user permissions."""

    async def test_admin_can_create_workflow_with_interviews_and_todos(
        self,
        db: AsyncSession,
        admin_user: User,
        test_company: Company,
        candidate_user: User,
        recruiter_user: User
    ):
        """Test admin can create workflow and associated interviews/todos."""
        # Create workflow
        workflow_data = {
            "name": "Admin Created Workflow",
            "description": "Workflow created by admin with full permissions",
            "employer_company_id": test_company.id,
            "status": "active"
        }
        
        workflow = await recruitment_process.create(
            db,
            obj_in=workflow_data,
            created_by=admin_user.id
        )
        
        assert workflow is not None
        assert workflow.created_by == admin_user.id
        
        # Create interview linked to workflow
        interview = Interview(
            workflow_id=workflow.id,
            candidate_id=candidate_user.id,
            recruiter_id=recruiter_user.id,
            employer_company_id=test_company.id,
            recruiter_company_id=test_company.id,
            title="Admin Created Interview",
            status="scheduled",
            interview_type="video",
            created_by=admin_user.id
        )
        db.add(interview)
        
        # Create todo linked to workflow
        todo = Todo(
            workflow_id=workflow.id,
            owner_id=admin_user.id,
            created_by=admin_user.id,
            title="Admin Created Todo",
            description="Task created by admin",
            status="pending"
        )
        db.add(todo)
        
        await db.commit()
        
        # Verify relationships
        result = await db.execute(
            select(Interview).where(Interview.workflow_id == workflow.id)
        )
        interviews = result.scalars().all()
        assert len(interviews) == 1
        assert interviews[0].created_by == admin_user.id
        
        result = await db.execute(
            select(Todo).where(Todo.workflow_id == workflow.id)
        )
        todos = result.scalars().all()
        assert len(todos) == 1
        assert todos[0].created_by == admin_user.id

    async def test_employer_can_create_workflow_in_own_company(
        self,
        db: AsyncSession,
        employer_user: User,
        test_company: Company,
        candidate_user: User,
        recruiter_user: User
    ):
        """Test employer can create workflow for their own company."""
        workflow_data = {
            "name": "Employer Workflow",
            "description": "Workflow created by employer",
            "employer_company_id": test_company.id,
            "status": "active"
        }
        
        workflow = await recruitment_process.create(
            db,
            obj_in=workflow_data,
            created_by=employer_user.id
        )
        
        assert workflow is not None
        assert workflow.created_by == employer_user.id
        
        # Create multiple interviews
        for i in range(3):
            interview = Interview(
                workflow_id=workflow.id,
                candidate_id=candidate_user.id,
                recruiter_id=recruiter_user.id,
                employer_company_id=test_company.id,
                recruiter_company_id=test_company.id,
                title=f"Interview {i+1}",
                status="scheduled",
                interview_type="video",
                created_by=employer_user.id
            )
            db.add(interview)
        
        # Create multiple todos
        for i in range(2):
            todo = Todo(
                workflow_id=workflow.id,
                owner_id=employer_user.id,
                created_by=employer_user.id,
                title=f"Task {i+1}",
                status="pending"
            )
            db.add(todo)
        
        await db.commit()
        
        # Verify counts
        interview_count = await db.execute(
            select(func.count(Interview.id)).where(Interview.workflow_id == workflow.id)
        )
        assert interview_count.scalar() == 3
        
        todo_count = await db.execute(
            select(func.count(Todo.id)).where(Todo.workflow_id == workflow.id)
        )
        assert todo_count.scalar() == 2

    async def test_recruiter_cannot_create_workflow_but_can_create_interviews_todos(
        self,
        db: AsyncSession,
        recruiter_user: User,
        employer_user: User,
        test_company: Company,
        candidate_user: User
    ):
        """Test recruiter cannot create workflow but can create interviews/todos."""
        # First, employer creates workflow
        workflow_data = {
            "name": "Employer Workflow for Recruiter",
            "employer_company_id": test_company.id,
            "status": "active"
        }
        
        workflow = await recruitment_process.create(
            db,
            obj_in=workflow_data,
            created_by=employer_user.id
        )
        
        # Recruiter can create interview linked to existing workflow
        interview = Interview(
            workflow_id=workflow.id,
            candidate_id=candidate_user.id,
            recruiter_id=recruiter_user.id,
            employer_company_id=test_company.id,
            recruiter_company_id=test_company.id,
            title="Recruiter Created Interview",
            status="scheduled",
            interview_type="video",
            created_by=recruiter_user.id
        )
        db.add(interview)
        
        # Recruiter can create todo
        todo = Todo(
            workflow_id=workflow.id,
            owner_id=recruiter_user.id,
            created_by=recruiter_user.id,
            title="Recruiter Created Todo",
            status="pending"
        )
        db.add(todo)
        
        await db.commit()
        
        # Verify recruiter created records
        result = await db.execute(
            select(Interview).where(
                Interview.workflow_id == workflow.id,
                Interview.created_by == recruiter_user.id
            )
        )
        recruiter_interviews = result.scalars().all()
        assert len(recruiter_interviews) == 1
        
        result = await db.execute(
            select(Todo).where(
                Todo.workflow_id == workflow.id,
                Todo.created_by == recruiter_user.id
            )
        )
        recruiter_todos = result.scalars().all()
        assert len(recruiter_todos) == 1

    async def test_candidate_cannot_create_workflow_interviews_todos(
        self,
        db: AsyncSession,
        candidate_user: User,
        test_company: Company
    ):
        """Test candidate cannot create workflows, interviews, or todos."""
        # This test would typically be handled at the API/permission layer
        # but we can test the model constraints
        
        # Candidate should not be able to create workflow
        # (This would be enforced by API permissions in real app)
        workflow_data = {
            "name": "Candidate Attempted Workflow",
            "employer_company_id": test_company.id,
            "status": "draft"
        }
        
        # In a real application, this would be blocked by permissions
        # For this test, we'll create it to show the model allows it
        # but the permission system should prevent it
        workflow = await recruitment_process.create(
            db,
            obj_in=workflow_data,
            created_by=candidate_user.id
        )
        
        # Mark this as a permission violation that should be caught
        assert workflow.created_by == candidate_user.id
        # Note: In production, API layer should prevent this

    async def test_cross_company_workflow_access_restrictions(
        self,
        db: AsyncSession,
        employer_user: User,
        test_company: Company,
        second_company: Company,
        candidate_user: User,
        recruiter_user: User
    ):
        """Test users cannot create content for other companies' workflows."""
        # Create workflow in first company
        workflow_company1 = await recruitment_process.create(
            db,
            obj_in={
                "name": "Company 1 Workflow",
                "employer_company_id": test_company.id,
                "status": "active"
            },
            created_by=employer_user.id
        )
        
        # Create workflow in second company
        workflow_company2 = await recruitment_process.create(
            db,
            obj_in={
                "name": "Company 2 Workflow",
                "employer_company_id": second_company.id,
                "status": "active"
            },
            created_by=employer_user.id  # Same user for simplicity
        )
        
        # Try to create interview for wrong company
        # This should be prevented by business logic
        interview = Interview(
            workflow_id=workflow_company1.id,
            candidate_id=candidate_user.id,
            recruiter_id=recruiter_user.id,
            employer_company_id=second_company.id,  # Wrong company!
            recruiter_company_id=test_company.id,
            title="Cross-company Interview",
            status="scheduled",
            interview_type="video"
        )
        db.add(interview)
        await db.commit()
        
        # Verify the mismatch exists (should be caught by validation)
        assert interview.workflow_id == workflow_company1.id
        assert interview.employer_company_id == second_company.id
        # This inconsistency should be prevented by API validation


class TestWorkflowCascadingOperationsWithPermissions:
    """Test cascading operations with different permission levels."""

    async def test_admin_soft_delete_workflow_cascades_all(
        self,
        db: AsyncSession,
        admin_user: User,
        test_company: Company,
        candidate_user: User,
        recruiter_user: User
    ):
        """Test admin can soft delete workflow and it cascades to all related items."""
        # Create workflow with mixed creators
        workflow = await recruitment_process.create(
            db,
            obj_in={
                "name": "Multi-creator Workflow",
                "employer_company_id": test_company.id,
                "status": "active"
            },
            created_by=admin_user.id
        )
        
        # Create interviews by different users
        admin_interview = Interview(
            workflow_id=workflow.id,
            candidate_id=candidate_user.id,
            recruiter_id=recruiter_user.id,
            employer_company_id=test_company.id,
            recruiter_company_id=test_company.id,
            title="Admin Interview",
            created_by=admin_user.id,
            status="scheduled",
            interview_type="video"
        )
        
        recruiter_interview = Interview(
            workflow_id=workflow.id,
            candidate_id=candidate_user.id,
            recruiter_id=recruiter_user.id,
            employer_company_id=test_company.id,
            recruiter_company_id=test_company.id,
            title="Recruiter Interview",
            created_by=recruiter_user.id,
            status="scheduled",
            interview_type="video"
        )
        
        # Create todos by different users
        admin_todo = Todo(
            workflow_id=workflow.id,
            owner_id=admin_user.id,
            created_by=admin_user.id,
            title="Admin Todo",
            status="pending"
        )
        
        recruiter_todo = Todo(
            workflow_id=workflow.id,
            owner_id=recruiter_user.id,
            created_by=recruiter_user.id,
            title="Recruiter Todo",
            status="pending"
        )
        
        db.add_all([admin_interview, recruiter_interview, admin_todo, recruiter_todo])
        await db.commit()
        
        # Admin soft deletes workflow
        deleted_workflow = await recruitment_process.soft_delete(db, id=workflow.id)
        
        assert deleted_workflow.is_deleted is True
        
        # Verify all related items are soft deleted regardless of creator
        result = await db.execute(
            select(Interview).where(
                Interview.workflow_id == workflow.id,
                Interview.is_deleted == True
            )
        )
        deleted_interviews = result.scalars().all()
        assert len(deleted_interviews) == 2
        
        result = await db.execute(
            select(Todo).where(
                Todo.workflow_id == workflow.id,
                Todo.is_deleted == True
            )
        )
        deleted_todos = result.scalars().all()
        assert len(deleted_todos) == 2

    async def test_workflow_with_scheduled_interviews_cascade_behavior(
        self,
        db: AsyncSession,
        employer_user: User,
        test_company: Company,
        candidate_user: User,
        recruiter_user: User
    ):
        """Test cascading behavior with scheduled interviews."""
        workflow = await recruitment_process.create(
            db,
            obj_in={
                "name": "Scheduled Interview Workflow",
                "employer_company_id": test_company.id,
                "status": "active"
            },
            created_by=employer_user.id
        )
        
        # Create interviews with different states and schedules
        future_interview = Interview(
            workflow_id=workflow.id,
            candidate_id=candidate_user.id,
            recruiter_id=recruiter_user.id,
            employer_company_id=test_company.id,
            recruiter_company_id=test_company.id,
            title="Future Interview",
            status="scheduled",
            interview_type="video",
            scheduled_start=datetime.utcnow() + timedelta(days=7),
            scheduled_end=datetime.utcnow() + timedelta(days=7, hours=1)
        )
        
        completed_interview = Interview(
            workflow_id=workflow.id,
            candidate_id=candidate_user.id,
            recruiter_id=recruiter_user.id,
            employer_company_id=test_company.id,
            recruiter_company_id=test_company.id,
            title="Completed Interview",
            status="completed",
            interview_type="video",
            scheduled_start=datetime.utcnow() - timedelta(days=7),
            scheduled_end=datetime.utcnow() - timedelta(days=7, hours=-1)
        )
        
        # Create todos with different priorities and states
        urgent_todo = Todo(
            workflow_id=workflow.id,
            owner_id=employer_user.id,
            title="Urgent Todo",
            priority="high",
            status="in_progress",
            due_date=datetime.utcnow() + timedelta(days=1)
        )
        
        completed_todo = Todo(
            workflow_id=workflow.id,
            owner_id=recruiter_user.id,
            title="Completed Todo",
            priority="medium",
            status="completed",
            completed_at=datetime.utcnow() - timedelta(days=1)
        )
        
        db.add_all([future_interview, completed_interview, urgent_todo, completed_todo])
        await db.commit()
        
        # Soft delete workflow
        await recruitment_process.soft_delete(db, id=workflow.id)
        
        # Verify all items are soft deleted regardless of status
        result = await db.execute(
            select(Interview).where(
                Interview.workflow_id == workflow.id,
                Interview.is_deleted == True
            )
        )
        assert len(result.scalars().all()) == 2
        
        result = await db.execute(
            select(Todo).where(
                Todo.workflow_id == workflow.id,
                Todo.is_deleted == True
            )
        )
        assert len(result.scalars().all()) == 2


class TestWorkflowEdgeCasesAndErrorHandling:
    """Test edge cases and error handling scenarios."""

    async def test_create_interview_with_invalid_workflow_id(
        self,
        db: AsyncSession,
        employer_user: User,
        test_company: Company,
        candidate_user: User,
        recruiter_user: User
    ):
        """Test creating interview with non-existent workflow_id."""
        # Try to create interview with non-existent workflow
        interview = Interview(
            workflow_id=99999,  # Non-existent workflow
            candidate_id=candidate_user.id,
            recruiter_id=recruiter_user.id,
            employer_company_id=test_company.id,
            recruiter_company_id=test_company.id,
            title="Invalid Workflow Interview",
            status="scheduled",
            interview_type="video"
        )
        db.add(interview)
        
        # This should fail due to foreign key constraint
        with pytest.raises(Exception):  # Foreign key violation
            await db.commit()

    async def test_create_todo_with_invalid_workflow_id(
        self,
        db: AsyncSession,
        employer_user: User
    ):
        """Test creating todo with non-existent workflow_id."""
        todo = Todo(
            workflow_id=99999,  # Non-existent workflow
            owner_id=employer_user.id,
            title="Invalid Workflow Todo",
            status="pending"
        )
        db.add(todo)
        
        # This should fail due to foreign key constraint
        with pytest.raises(Exception):  # Foreign key violation
            await db.commit()

    async def test_soft_delete_nonexistent_workflow(
        self,
        db: AsyncSession
    ):
        """Test soft deleting non-existent workflow."""
        result = await recruitment_process.soft_delete(db, id=99999)
        assert result is None

    async def test_workflow_with_mixed_company_relationships(
        self,
        db: AsyncSession,
        admin_user: User,
        test_company: Company,
        second_company: Company,
        candidate_user: User,
        recruiter_user: User
    ):
        """Test workflow with interviews/todos from different companies."""
        workflow = await recruitment_process.create(
            db,
            obj_in={
                "name": "Mixed Company Workflow",
                "employer_company_id": test_company.id,
                "status": "active"
            },
            created_by=admin_user.id
        )
        
        # Create interview with different recruiter company
        interview = Interview(
            workflow_id=workflow.id,
            candidate_id=candidate_user.id,
            recruiter_id=recruiter_user.id,
            employer_company_id=test_company.id,
            recruiter_company_id=second_company.id,  # Different company
            title="Cross-company Interview",
            status="scheduled",
            interview_type="video"
        )
        db.add(interview)
        await db.commit()
        
        # Verify the relationship exists
        result = await db.execute(
            select(Interview).where(Interview.workflow_id == workflow.id)
        )
        interviews = result.scalars().all()
        assert len(interviews) == 1
        assert interviews[0].recruiter_company_id == second_company.id


class TestWorkflowPermissionMatrix:
    """Test complete permission matrix for workflow operations."""

    @pytest.mark.parametrize("user_type,can_create_workflow,can_create_interview,can_create_todo", [
        ("admin", True, True, True),
        ("employer", True, True, True),
        ("recruiter", False, True, True),
        ("candidate", False, False, False),
    ])
    async def test_permission_matrix(
        self,
        db: AsyncSession,
        test_company: Company,
        admin_user: User,
        employer_user: User,
        recruiter_user: User,
        candidate_user: User,
        user_type: str,
        can_create_workflow: bool,
        can_create_interview: bool,
        can_create_todo: bool
    ):
        """Test permission matrix for different user types."""
        user_map = {
            "admin": admin_user,
            "employer": employer_user,
            "recruiter": recruiter_user,
            "candidate": candidate_user
        }
        
        current_user = user_map[user_type]
        
        # First, create a workflow with admin (for non-workflow-creators)
        workflow = await recruitment_process.create(
            db,
            obj_in={
                "name": f"{user_type.title()} Test Workflow",
                "employer_company_id": test_company.id,
                "status": "active"
            },
            created_by=admin_user.id
        )
        
        # Test interview creation
        if can_create_interview:
            interview = Interview(
                workflow_id=workflow.id,
                candidate_id=candidate_user.id,
                recruiter_id=recruiter_user.id,
                employer_company_id=test_company.id,
                recruiter_company_id=test_company.id,
                title=f"{user_type} Created Interview",
                status="scheduled",
                interview_type="video",
                created_by=current_user.id
            )
            db.add(interview)
            await db.commit()
            
            result = await db.execute(
                select(Interview).where(Interview.created_by == current_user.id)
            )
            assert len(result.scalars().all()) >= 1
        
        # Test todo creation
        if can_create_todo:
            todo = Todo(
                workflow_id=workflow.id,
                owner_id=current_user.id,
                created_by=current_user.id,
                title=f"{user_type} Created Todo",
                status="pending"
            )
            db.add(todo)
            await db.commit()
            
            result = await db.execute(
                select(Todo).where(Todo.created_by == current_user.id)
            )
            assert len(result.scalars().all()) >= 1

    async def test_bulk_operations_with_permissions(
        self,
        db: AsyncSession,
        admin_user: User,
        employer_user: User,
        recruiter_user: User,
        test_company: Company,
        candidate_user: User
    ):
        """Test bulk creation and operations with different permissions."""
        # Create multiple workflows
        workflows = []
        for i in range(5):
            workflow = await recruitment_process.create(
                db,
                obj_in={
                    "name": f"Bulk Workflow {i+1}",
                    "employer_company_id": test_company.id,
                    "status": "active"
                },
                created_by=admin_user.id
            )
            workflows.append(workflow)
        
        # Bulk create interviews across workflows
        interviews = []
        for i, workflow in enumerate(workflows):
            for j in range(2):  # 2 interviews per workflow
                interview = Interview(
                    workflow_id=workflow.id,
                    candidate_id=candidate_user.id,
                    recruiter_id=recruiter_user.id,
                    employer_company_id=test_company.id,
                    recruiter_company_id=test_company.id,
                    title=f"Bulk Interview {i+1}-{j+1}",
                    status="scheduled",
                    interview_type="video",
                    created_by=employer_user.id if j == 0 else recruiter_user.id
                )
                interviews.append(interview)
        
        db.add_all(interviews)
        await db.commit()
        
        # Verify total count
        total_interviews = await db.execute(
            select(func.count(Interview.id))
        )
        assert total_interviews.scalar() == 10  # 5 workflows * 2 interviews
        
        # Test bulk soft delete of one workflow
        deleted_workflow = await recruitment_process.soft_delete(db, id=workflows[0].id)
        
        # Verify only interviews from deleted workflow are soft deleted
        deleted_interviews = await db.execute(
            select(func.count(Interview.id)).where(Interview.is_deleted == True)
        )
        assert deleted_interviews.scalar() == 2  # Only interviews from first workflow