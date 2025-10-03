"""
Test API endpoints for workflow creation with interviews and todos.
Tests permission-based access control at the API level.
"""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import status

from app.models.user import User
from app.models.company import Company
from app.models.recruitment_process import RecruitmentProcess
from app.services.auth_service import auth_service


class TestWorkflowAPIPermissions:
    """Test API endpoints with different user permissions."""

    async def test_admin_create_workflow_with_interviews_todos_api(
        self,
        client: AsyncClient,
        db: AsyncSession,
        admin_user: User,
        test_company: Company,
        candidate_user: User,
        recruiter_user: User
    ):
        """Test admin can create workflow and related items via API."""
        # Login as admin
        auth_token = await auth_service.create_access_token(admin_user.id)
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        # Create workflow
        workflow_data = {
            "name": "API Test Workflow",
            "description": "Created via API",
            "employer_company_id": test_company.id,
            "status": "active"
        }
        
        response = await client.post(
            "/api/recruitment-workflows/",
            json=workflow_data,
            headers=headers
        )
        assert response.status_code == status.HTTP_201_CREATED
        workflow = response.json()
        workflow_id = workflow["id"]
        
        # Create interview linked to workflow
        interview_data = {
            "candidate_id": candidate_user.id,
            "recruiter_id": recruiter_user.id,
            "employer_company_id": test_company.id,
            "workflow_id": workflow_id,  # Link to workflow
            "title": "API Created Interview",
            "interview_type": "video",
            "status": "scheduled"
        }
        
        response = await client.post(
            "/api/interviews/",
            json=interview_data,
            headers=headers
        )
        assert response.status_code == status.HTTP_201_CREATED
        interview = response.json()
        assert interview["workflow_id"] == workflow_id
        
        # Create todo linked to workflow
        todo_data = {
            "title": "API Created Todo",
            "description": "Created via API",
            "workflow_id": workflow_id,  # Link to workflow
            "status": "pending"
        }
        
        response = await client.post(
            "/api/todos/",
            json=todo_data,
            headers=headers
        )
        assert response.status_code == status.HTTP_201_CREATED
        todo = response.json()
        assert todo["workflow_id"] == workflow_id

    async def test_employer_create_workflow_api(
        self,
        client: AsyncClient,
        db: AsyncSession,
        employer_user: User,
        test_company: Company
    ):
        """Test employer can create workflow via API."""
        auth_token = await auth_service.create_access_token(employer_user.id)
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        workflow_data = {
            "name": "Employer API Workflow",
            "description": "Created by employer",
            "employer_company_id": test_company.id,
            "status": "active"
        }
        
        response = await client.post(
            "/api/recruitment-workflows/",
            json=workflow_data,
            headers=headers
        )
        assert response.status_code == status.HTTP_201_CREATED
        workflow = response.json()
        assert workflow["created_by"] == employer_user.id

    async def test_recruiter_cannot_create_workflow_api(
        self,
        client: AsyncClient,
        db: AsyncSession,
        recruiter_user: User,
        test_company: Company
    ):
        """Test recruiter cannot create workflow via API."""
        auth_token = await auth_service.create_access_token(recruiter_user.id)
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        workflow_data = {
            "name": "Recruiter Attempt Workflow",
            "employer_company_id": test_company.id,
            "status": "active"
        }
        
        response = await client.post(
            "/api/recruitment-workflows/",
            json=workflow_data,
            headers=headers
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    async def test_recruiter_create_interview_with_workflow_api(
        self,
        client: AsyncClient,
        db: AsyncSession,
        recruiter_user: User,
        employer_user: User,
        test_company: Company,
        candidate_user: User
    ):
        """Test recruiter can create interview linked to existing workflow."""
        # First, employer creates workflow
        employer_token = await auth_service.create_access_token(employer_user.id)
        employer_headers = {"Authorization": f"Bearer {employer_token}"}
        
        workflow_data = {
            "name": "Employer Workflow for Recruiter",
            "employer_company_id": test_company.id,
            "status": "active"
        }
        
        response = await client.post(
            "/api/recruitment-workflows/",
            json=workflow_data,
            headers=employer_headers
        )
        assert response.status_code == status.HTTP_201_CREATED
        workflow = response.json()
        workflow_id = workflow["id"]
        
        # Now recruiter creates interview
        recruiter_token = await auth_service.create_access_token(recruiter_user.id)
        recruiter_headers = {"Authorization": f"Bearer {recruiter_token}"}
        
        interview_data = {
            "candidate_id": candidate_user.id,
            "recruiter_id": recruiter_user.id,
            "employer_company_id": test_company.id,
            "workflow_id": workflow_id,
            "title": "Recruiter Interview",
            "interview_type": "video",
            "status": "scheduled"
        }
        
        response = await client.post(
            "/api/interviews/",
            json=interview_data,
            headers=recruiter_headers
        )
        assert response.status_code == status.HTTP_201_CREATED
        interview = response.json()
        assert interview["workflow_id"] == workflow_id

    async def test_candidate_cannot_create_content_api(
        self,
        client: AsyncClient,
        db: AsyncSession,
        candidate_user: User,
        test_company: Company
    ):
        """Test candidate cannot create workflows, interviews, or todos."""
        auth_token = await auth_service.create_access_token(candidate_user.id)
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        # Try to create workflow
        workflow_data = {
            "name": "Candidate Workflow",
            "employer_company_id": test_company.id,
            "status": "active"
        }
        
        response = await client.post(
            "/api/recruitment-workflows/",
            json=workflow_data,
            headers=headers
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN
        
        # Try to create interview
        interview_data = {
            "candidate_id": candidate_user.id,
            "recruiter_id": candidate_user.id,
            "employer_company_id": test_company.id,
            "title": "Candidate Interview",
            "interview_type": "video"
        }
        
        response = await client.post(
            "/api/interviews/",
            json=interview_data,
            headers=headers
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN
        
        # Try to create todo
        todo_data = {
            "title": "Candidate Todo",
            "status": "pending"
        }
        
        response = await client.post(
            "/api/todos/",
            json=todo_data,
            headers=headers
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    async def test_filter_interviews_by_workflow_api(
        self,
        client: AsyncClient,
        db: AsyncSession,
        admin_user: User,
        test_company: Company,
        candidate_user: User,
        recruiter_user: User
    ):
        """Test filtering interviews by workflow_id via API."""
        auth_token = await auth_service.create_access_token(admin_user.id)
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        # Create two workflows
        workflow1_data = {
            "name": "Workflow 1",
            "employer_company_id": test_company.id,
            "status": "active"
        }
        response = await client.post(
            "/api/recruitment-workflows/",
            json=workflow1_data,
            headers=headers
        )
        workflow1 = response.json()
        
        workflow2_data = {
            "name": "Workflow 2",
            "employer_company_id": test_company.id,
            "status": "active"
        }
        response = await client.post(
            "/api/recruitment-workflows/",
            json=workflow2_data,
            headers=headers
        )
        workflow2 = response.json()
        
        # Create interviews for each workflow
        for i in range(3):
            interview_data = {
                "candidate_id": candidate_user.id,
                "recruiter_id": recruiter_user.id,
                "employer_company_id": test_company.id,
                "workflow_id": workflow1["id"],
                "title": f"Workflow 1 Interview {i+1}",
                "interview_type": "video",
                "status": "scheduled"
            }
            await client.post("/api/interviews/", json=interview_data, headers=headers)
        
        for i in range(2):
            interview_data = {
                "candidate_id": candidate_user.id,
                "recruiter_id": recruiter_user.id,
                "employer_company_id": test_company.id,
                "workflow_id": workflow2["id"],
                "title": f"Workflow 2 Interview {i+1}",
                "interview_type": "video",
                "status": "scheduled"
            }
            await client.post("/api/interviews/", json=interview_data, headers=headers)
        
        # Filter interviews by workflow1
        response = await client.get(
            f"/api/interviews/?workflow_id={workflow1['id']}",
            headers=headers
        )
        assert response.status_code == status.HTTP_200_OK
        interviews = response.json()
        assert len(interviews["interviews"]) == 3
        
        # Filter interviews by workflow2
        response = await client.get(
            f"/api/interviews/?workflow_id={workflow2['id']}",
            headers=headers
        )
        assert response.status_code == status.HTTP_200_OK
        interviews = response.json()
        assert len(interviews["interviews"]) == 2

    async def test_filter_todos_by_workflow_api(
        self,
        client: AsyncClient,
        db: AsyncSession,
        admin_user: User,
        test_company: Company
    ):
        """Test filtering todos by workflow_id via API."""
        auth_token = await auth_service.create_access_token(admin_user.id)
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        # Create workflow
        workflow_data = {
            "name": "Todo Workflow",
            "employer_company_id": test_company.id,
            "status": "active"
        }
        response = await client.post(
            "/api/recruitment-workflows/",
            json=workflow_data,
            headers=headers
        )
        workflow = response.json()
        
        # Create todos with and without workflow
        workflow_todos = []
        for i in range(4):
            todo_data = {
                "title": f"Workflow Todo {i+1}",
                "workflow_id": workflow["id"],
                "status": "pending"
            }
            response = await client.post("/api/todos/", json=todo_data, headers=headers)
            workflow_todos.append(response.json())
        
        standalone_todos = []
        for i in range(2):
            todo_data = {
                "title": f"Standalone Todo {i+1}",
                "status": "pending"
            }
            response = await client.post("/api/todos/", json=todo_data, headers=headers)
            standalone_todos.append(response.json())
        
        # Filter todos by workflow
        response = await client.get(
            f"/api/todos/?workflow_id={workflow['id']}",
            headers=headers
        )
        assert response.status_code == status.HTTP_200_OK
        todos = response.json()
        assert len(todos["items"]) == 4
        
        # Get all todos (should include both workflow and standalone)
        response = await client.get("/api/todos/", headers=headers)
        assert response.status_code == status.HTTP_200_OK
        all_todos = response.json()
        assert len(all_todos["items"]) == 6

    async def test_soft_delete_workflow_cascades_api(
        self,
        client: AsyncClient,
        db: AsyncSession,
        admin_user: User,
        test_company: Company,
        candidate_user: User,
        recruiter_user: User
    ):
        """Test soft deleting workflow cascades to interviews and todos via API."""
        auth_token = await auth_service.create_access_token(admin_user.id)
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        # Create workflow
        workflow_data = {
            "name": "Cascade Test Workflow",
            "employer_company_id": test_company.id,
            "status": "active"
        }
        response = await client.post(
            "/api/recruitment-workflows/",
            json=workflow_data,
            headers=headers
        )
        workflow = response.json()
        workflow_id = workflow["id"]
        
        # Create interviews and todos
        interview_ids = []
        for i in range(2):
            interview_data = {
                "candidate_id": candidate_user.id,
                "recruiter_id": recruiter_user.id,
                "employer_company_id": test_company.id,
                "workflow_id": workflow_id,
                "title": f"Cascade Interview {i+1}",
                "interview_type": "video",
                "status": "scheduled"
            }
            response = await client.post("/api/interviews/", json=interview_data, headers=headers)
            interview_ids.append(response.json()["id"])
        
        todo_ids = []
        for i in range(3):
            todo_data = {
                "title": f"Cascade Todo {i+1}",
                "workflow_id": workflow_id,
                "status": "pending"
            }
            response = await client.post("/api/todos/", json=todo_data, headers=headers)
            todo_ids.append(response.json()["id"])
        
        # Soft delete workflow
        response = await client.delete(
            f"/api/recruitment-workflows/{workflow_id}",
            headers=headers
        )
        assert response.status_code == status.HTTP_200_OK
        
        # Verify workflow is soft deleted
        response = await client.get(
            f"/api/recruitment-workflows/{workflow_id}",
            headers=headers
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND
        
        # Verify interviews are soft deleted
        for interview_id in interview_ids:
            response = await client.get(
                f"/api/interviews/{interview_id}",
                headers=headers
            )
            assert response.status_code == status.HTTP_404_NOT_FOUND
        
        # Verify todos are soft deleted
        for todo_id in todo_ids:
            response = await client.get(
                f"/api/todos/{todo_id}",
                headers=headers
            )
            assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_unauthorized_access_api(
        self,
        client: AsyncClient,
        db: AsyncSession
    ):
        """Test unauthorized access to workflow endpoints."""
        # Try to access endpoints without authentication
        response = await client.get("/api/recruitment-workflows/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        
        response = await client.post("/api/recruitment-workflows/", json={})
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        
        response = await client.get("/api/interviews/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        
        response = await client.post("/api/interviews/", json={})
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        
        response = await client.get("/api/todos/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        
        response = await client.post("/api/todos/", json={})
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_invalid_workflow_id_api(
        self,
        client: AsyncClient,
        db: AsyncSession,
        admin_user: User,
        test_company: Company,
        candidate_user: User,
        recruiter_user: User
    ):
        """Test creating interviews/todos with invalid workflow_id via API."""
        auth_token = await auth_service.create_access_token(admin_user.id)
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        # Try to create interview with non-existent workflow
        interview_data = {
            "candidate_id": candidate_user.id,
            "recruiter_id": recruiter_user.id,
            "employer_company_id": test_company.id,
            "workflow_id": 99999,  # Non-existent
            "title": "Invalid Workflow Interview",
            "interview_type": "video",
            "status": "scheduled"
        }
        
        response = await client.post(
            "/api/interviews/",
            json=interview_data,
            headers=headers
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        
        # Try to create todo with non-existent workflow
        todo_data = {
            "title": "Invalid Workflow Todo",
            "workflow_id": 99999,  # Non-existent
            "status": "pending"
        }
        
        response = await client.post(
            "/api/todos/",
            json=todo_data,
            headers=headers
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST


class TestWorkflowAPIEdgeCases:
    """Test edge cases in API workflow operations."""

    async def test_create_workflow_with_invalid_company_api(
        self,
        client: AsyncClient,
        db: AsyncSession,
        admin_user: User
    ):
        """Test creating workflow with non-existent company."""
        auth_token = await auth_service.create_access_token(admin_user.id)
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        workflow_data = {
            "name": "Invalid Company Workflow",
            "employer_company_id": 99999,  # Non-existent company
            "status": "active"
        }
        
        response = await client.post(
            "/api/recruitment-workflows/",
            json=workflow_data,
            headers=headers
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    async def test_update_workflow_remove_relationships_api(
        self,
        client: AsyncClient,
        db: AsyncSession,
        admin_user: User,
        test_company: Company,
        candidate_user: User,
        recruiter_user: User
    ):
        """Test updating interviews/todos to remove workflow relationships."""
        auth_token = await auth_service.create_access_token(admin_user.id)
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        # Create workflow with interview and todo
        workflow_data = {
            "name": "Relationship Removal Test",
            "employer_company_id": test_company.id,
            "status": "active"
        }
        response = await client.post(
            "/api/recruitment-workflows/",
            json=workflow_data,
            headers=headers
        )
        workflow = response.json()
        
        interview_data = {
            "candidate_id": candidate_user.id,
            "recruiter_id": recruiter_user.id,
            "employer_company_id": test_company.id,
            "workflow_id": workflow["id"],
            "title": "Test Interview",
            "interview_type": "video",
            "status": "scheduled"
        }
        response = await client.post("/api/interviews/", json=interview_data, headers=headers)
        interview = response.json()
        
        # Update interview to remove workflow relationship
        update_data = {
            "workflow_id": None,
            "title": "Updated Interview - No Workflow"
        }
        response = await client.put(
            f"/api/interviews/{interview['id']}",
            json=update_data,
            headers=headers
        )
        assert response.status_code == status.HTTP_200_OK
        updated_interview = response.json()
        assert updated_interview["workflow_id"] is None

    async def test_concurrent_workflow_operations_api(
        self,
        client: AsyncClient,
        db: AsyncSession,
        admin_user: User,
        test_company: Company
    ):
        """Test concurrent workflow creation and operations."""
        auth_token = await auth_service.create_access_token(admin_user.id)
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        import asyncio
        
        # Create multiple workflows concurrently
        async def create_workflow(i):
            workflow_data = {
                "name": f"Concurrent Workflow {i}",
                "employer_company_id": test_company.id,
                "status": "active"
            }
            return await client.post(
                "/api/recruitment-workflows/",
                json=workflow_data,
                headers=headers
            )
        
        # Create 5 workflows concurrently
        tasks = [create_workflow(i) for i in range(5)]
        responses = await asyncio.gather(*tasks)
        
        # Verify all were created successfully
        for response in responses:
            assert response.status_code == status.HTTP_201_CREATED
        
        # Get all workflows
        response = await client.get("/api/recruitment-workflows/", headers=headers)
        workflows = response.json()
        assert len(workflows) >= 5