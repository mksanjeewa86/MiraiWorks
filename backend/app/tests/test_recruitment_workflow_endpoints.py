import pytest
from httpx import AsyncClient
from datetime import datetime

from app.main import app
from app.schemas.recruitment_workflow.enums import ProcessStatus, NodeType


class TestRecruitmentProcessEndpoints:
    """Test recruitment process API endpoints"""

    @pytest.mark.asyncio
    async def test_create_recruitment_process_success(self):
        """Test successful recruitment process creation"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            process_data = {
                "name": "Software Engineer Process",
                "description": "Technical interview process for software engineers",
                "settings": {
                    "category": "engineering",
                    "difficulty": "senior"
                }
            }

            response = await client.post(
                "/api/recruitment-processes/",
                json=process_data,
                headers={"Authorization": "Bearer employer_token"}
            )

            assert response.status_code == 201
            data = response.json()
            assert data["name"] == process_data["name"]
            assert data["description"] == process_data["description"]
            assert data["status"] == ProcessStatus.DRAFT
            assert data["version"] == 1
            assert "id" in data
            assert "created_at" in data

    @pytest.mark.asyncio
    async def test_create_recruitment_process_unauthorized(self):
        """Test recruitment process creation without proper authorization"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            process_data = {
                "name": "Test Process",
                "description": "Test description"
            }

            # No authorization header
            response = await client.post(
                "/api/recruitment-processes/",
                json=process_data
            )
            assert response.status_code == 401

            # Recruiter trying to create (should fail)
            response = await client.post(
                "/api/recruitment-processes/",
                json=process_data,
                headers={"Authorization": "Bearer recruiter_token"}
            )
            assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_create_recruitment_process_invalid_data(self):
        """Test recruitment process creation with invalid data"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            # Missing required fields
            response = await client.post(
                "/api/recruitment-processes/",
                json={},
                headers={"Authorization": "Bearer employer_token"}
            )
            assert response.status_code == 422

            # Empty name
            response = await client.post(
                "/api/recruitment-processes/",
                json={"name": ""},
                headers={"Authorization": "Bearer employer_token"}
            )
            assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_list_recruitment_processes_success(self):
        """Test listing recruitment processes"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get(
                "/api/recruitment-processes/",
                headers={"Authorization": "Bearer employer_token"}
            )

            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, list)

            # Test with pagination
            response = await client.get(
                "/api/recruitment-processes/?skip=0&limit=10",
                headers={"Authorization": "Bearer employer_token"}
            )
            assert response.status_code == 200

            # Test with status filter
            response = await client.get(
                "/api/recruitment-processes/?status=draft",
                headers={"Authorization": "Bearer employer_token"}
            )
            assert response.status_code == 200

            # Test with search
            response = await client.get(
                "/api/recruitment-processes/?search=engineer",
                headers={"Authorization": "Bearer employer_token"}
            )
            assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_get_recruitment_process_success(self):
        """Test getting a specific recruitment process"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            process_id = 1
            response = await client.get(
                f"/api/recruitment-processes/{process_id}",
                headers={"Authorization": "Bearer employer_token"}
            )

            assert response.status_code == 200
            data = response.json()
            assert data["id"] == process_id
            assert "name" in data
            assert "nodes" in data
            assert "candidate_processes" in data
            assert "viewers" in data

    @pytest.mark.asyncio
    async def test_get_recruitment_process_not_found(self):
        """Test getting non-existent recruitment process"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get(
                "/api/recruitment-processes/999999",
                headers={"Authorization": "Bearer employer_token"}
            )

            assert response.status_code == 404
            assert "not found" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_get_recruitment_process_access_denied(self):
        """Test access control for recruitment process"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            process_id = 1

            # Recruiter without access
            response = await client.get(
                f"/api/recruitment-processes/{process_id}",
                headers={"Authorization": "Bearer unauthorized_recruiter_token"}
            )
            assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_update_recruitment_process_success(self):
        """Test updating a recruitment process"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            process_id = 1
            update_data = {
                "name": "Updated Process Name",
                "description": "Updated description",
                "settings": {"updated": True}
            }

            response = await client.put(
                f"/api/recruitment-processes/{process_id}",
                json=update_data,
                headers={"Authorization": "Bearer employer_token"}
            )

            assert response.status_code == 200
            data = response.json()
            assert data["name"] == update_data["name"]
            assert data["description"] == update_data["description"]

    @pytest.mark.asyncio
    async def test_update_active_process_requires_force(self):
        """Test that updating active processes requires force flag"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            process_id = 1  # Assume this is an active process
            update_data = {
                "name": "Updated Name"
            }

            response = await client.put(
                f"/api/recruitment-processes/{process_id}",
                json=update_data,
                headers={"Authorization": "Bearer employer_token"}
            )

            assert response.status_code == 409  # Conflict for active process

    @pytest.mark.asyncio
    async def test_activate_recruitment_process_success(self):
        """Test activating a recruitment process"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            process_id = 1  # Assume this is a valid draft process
            activation_data = {"force_activate": False}

            response = await client.post(
                f"/api/recruitment-processes/{process_id}/activate",
                json=activation_data,
                headers={"Authorization": "Bearer employer_token"}
            )

            assert response.status_code == 200
            data = response.json()
            assert data["status"] == ProcessStatus.ACTIVE
            assert "activated_at" in data

    @pytest.mark.asyncio
    async def test_activate_recruitment_process_validation_failed(self):
        """Test activating process with validation issues"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            process_id = 1  # Process with validation issues
            activation_data = {"force_activate": False}

            response = await client.post(
                f"/api/recruitment-processes/{process_id}/activate",
                json=activation_data,
                headers={"Authorization": "Bearer employer_token"}
            )

            assert response.status_code == 422
            assert "validation" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_force_activate_recruitment_process(self):
        """Test force activating process despite validation issues"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            process_id = 1
            activation_data = {"force_activate": True}

            response = await client.post(
                f"/api/recruitment-processes/{process_id}/activate",
                json=activation_data,
                headers={"Authorization": "Bearer employer_token"}
            )

            assert response.status_code == 200
            data = response.json()
            assert data["status"] == ProcessStatus.ACTIVE

    @pytest.mark.asyncio
    async def test_archive_recruitment_process_success(self):
        """Test archiving a recruitment process"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            process_id = 1
            archive_data = {"reason": "No longer needed"}

            response = await client.post(
                f"/api/recruitment-processes/{process_id}/archive",
                json=archive_data,
                headers={"Authorization": "Bearer employer_token"}
            )

            assert response.status_code == 200
            data = response.json()
            assert data["status"] == ProcessStatus.ARCHIVED
            assert "archived_at" in data

    @pytest.mark.asyncio
    async def test_clone_recruitment_process_success(self):
        """Test cloning a recruitment process"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            process_id = 1
            clone_data = {
                "new_name": "Cloned Process",
                "clone_candidates": False,
                "clone_viewers": True
            }

            response = await client.post(
                f"/api/recruitment-processes/{process_id}/clone",
                json=clone_data,
                headers={"Authorization": "Bearer employer_token"}
            )

            assert response.status_code == 200
            data = response.json()
            assert data["name"] == clone_data["new_name"]
            assert data["status"] == ProcessStatus.DRAFT
            assert data["id"] != process_id  # New process

    @pytest.mark.asyncio
    async def test_delete_recruitment_process_success(self):
        """Test deleting a draft recruitment process"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            process_id = 1  # Assume this is a draft process

            response = await client.delete(
                f"/api/recruitment-processes/{process_id}",
                headers={"Authorization": "Bearer employer_token"}
            )

            assert response.status_code == 204

    @pytest.mark.asyncio
    async def test_delete_active_process_fails(self):
        """Test that active processes cannot be deleted"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            process_id = 1  # Assume this is an active process

            response = await client.delete(
                f"/api/recruitment-processes/{process_id}",
                headers={"Authorization": "Bearer employer_token"}
            )

            assert response.status_code == 409
            assert "draft" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_validate_recruitment_process(self):
        """Test validating a recruitment process"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            process_id = 1

            response = await client.get(
                f"/api/recruitment-processes/{process_id}/validate",
                headers={"Authorization": "Bearer employer_token"}
            )

            assert response.status_code == 200
            data = response.json()
            assert "is_valid" in data
            assert "issues" in data
            assert "warnings" in data
            assert isinstance(data["is_valid"], bool)
            assert isinstance(data["issues"], list)
            assert isinstance(data["warnings"], list)

    @pytest.mark.asyncio
    async def test_get_process_analytics(self):
        """Test getting process analytics"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            process_id = 1

            response = await client.get(
                f"/api/recruitment-processes/{process_id}/analytics",
                headers={"Authorization": "Bearer employer_token"}
            )

            assert response.status_code == 200
            data = response.json()
            assert "process_id" in data
            assert "process_name" in data
            assert "total_candidates" in data
            assert "completion_rate" in data
            assert "node_statistics" in data
            assert "bottleneck_nodes" in data
            assert "recruiter_workload" in data

    @pytest.mark.asyncio
    async def test_get_company_statistics(self):
        """Test getting company process statistics"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            company_id = 1

            response = await client.get(
                f"/api/recruitment-processes/company/{company_id}/statistics",
                headers={"Authorization": "Bearer employer_token"}
            )

            assert response.status_code == 200
            data = response.json()
            assert "total_processes" in data
            assert "active_processes" in data
            assert "total_candidates" in data
            assert "completion_rate" in data

    @pytest.mark.asyncio
    async def test_list_process_templates(self):
        """Test listing process templates"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get(
                "/api/recruitment-processes/templates/",
                headers={"Authorization": "Bearer employer_token"}
            )

            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, list)

            # Test with filters
            response = await client.get(
                "/api/recruitment-processes/templates/?category=engineering&public_only=true",
                headers={"Authorization": "Bearer employer_token"}
            )
            assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_apply_process_template(self):
        """Test applying a process template"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            template_id = 1
            process_data = {
                "name": "New Process from Template",
                "description": "Created from template",
                "clone_viewers": True
            }

            response = await client.post(
                f"/api/recruitment-processes/templates/{template_id}/apply",
                json=process_data,
                headers={"Authorization": "Bearer employer_token"}
            )

            assert response.status_code == 200
            data = response.json()
            assert data["name"] == process_data["name"]
            assert data["status"] == ProcessStatus.DRAFT

    @pytest.mark.asyncio
    async def test_apply_nonexistent_template(self):
        """Test applying non-existent template"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            template_id = 999999
            process_data = {
                "name": "New Process from Template"
            }

            response = await client.post(
                f"/api/recruitment-processes/templates/{template_id}/apply",
                json=process_data,
                headers={"Authorization": "Bearer employer_token"}
            )

            assert response.status_code == 404


class TestCandidateProcessEndpoints:
    """Test candidate process API endpoints"""

    @pytest.mark.asyncio
    async def test_assign_candidate_to_process_success(self):
        """Test successfully assigning candidate to process"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            process_id = 1
            assignment_data = {
                "candidate_id": 100,
                "assigned_recruiter_id": 50,
                "start_immediately": False
            }

            response = await client.post(
                f"/api/recruitment-processes/{process_id}/candidates",
                json=assignment_data,
                headers={"Authorization": "Bearer employer_token"}
            )

            assert response.status_code == 201
            data = response.json()
            assert data["candidate_id"] == assignment_data["candidate_id"]
            assert data["process_id"] == process_id
            assert data["assigned_recruiter_id"] == assignment_data["assigned_recruiter_id"]
            assert data["status"] == "not_started"

    @pytest.mark.asyncio
    async def test_assign_candidate_with_immediate_start(self):
        """Test assigning candidate with immediate start"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            process_id = 1
            assignment_data = {
                "candidate_id": 101,
                "assigned_recruiter_id": 50,
                "start_immediately": True
            }

            response = await client.post(
                f"/api/recruitment-processes/{process_id}/candidates",
                json=assignment_data,
                headers={"Authorization": "Bearer employer_token"}
            )

            assert response.status_code == 201
            data = response.json()
            assert data["status"] == "in_progress"  # Should be started
            assert "started_at" in data

    @pytest.mark.asyncio
    async def test_assign_duplicate_candidate_fails(self):
        """Test that assigning duplicate candidate fails"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            process_id = 1
            assignment_data = {
                "candidate_id": 100,  # Same candidate as previous test
                "assigned_recruiter_id": 50
            }

            response = await client.post(
                f"/api/recruitment-processes/{process_id}/candidates",
                json=assignment_data,
                headers={"Authorization": "Bearer employer_token"}
            )

            assert response.status_code == 409
            assert "already assigned" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_bulk_assign_candidates_success(self):
        """Test bulk assigning candidates to process"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            process_id = 1
            bulk_data = {
                "candidate_ids": [200, 201, 202],
                "assigned_recruiter_id": 50,
                "start_immediately": False,
                "send_notifications": True
            }

            response = await client.post(
                f"/api/recruitment-processes/{process_id}/candidates/bulk",
                json=bulk_data,
                headers={"Authorization": "Bearer employer_token"}
            )

            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, list)
            assert len(data) == len(bulk_data["candidate_ids"])

            for candidate_process in data:
                assert candidate_process["process_id"] == process_id
                assert candidate_process["candidate_id"] in bulk_data["candidate_ids"]
                assert candidate_process["assigned_recruiter_id"] == bulk_data["assigned_recruiter_id"]

    @pytest.mark.asyncio
    async def test_bulk_assign_invalid_data(self):
        """Test bulk assign with invalid data"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            process_id = 1

            # Empty candidate list
            response = await client.post(
                f"/api/recruitment-processes/{process_id}/candidates/bulk",
                json={"candidate_ids": []},
                headers={"Authorization": "Bearer employer_token"}
            )
            assert response.status_code == 422

            # Duplicate candidate IDs
            response = await client.post(
                f"/api/recruitment-processes/{process_id}/candidates/bulk",
                json={"candidate_ids": [100, 100, 101]},
                headers={"Authorization": "Bearer employer_token"}
            )
            assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_list_process_candidates(self):
        """Test listing candidates in a process"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            process_id = 1

            response = await client.get(
                f"/api/recruitment-processes/{process_id}/candidates",
                headers={"Authorization": "Bearer employer_token"}
            )

            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, list)

            # Test with status filter
            response = await client.get(
                f"/api/recruitment-processes/{process_id}/candidates?status=in_progress",
                headers={"Authorization": "Bearer employer_token"}
            )
            assert response.status_code == 200

            # Test with pagination
            response = await client.get(
                f"/api/recruitment-processes/{process_id}/candidates?skip=0&limit=10",
                headers={"Authorization": "Bearer employer_token"}
            )
            assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_get_candidate_process_success(self):
        """Test getting candidate process details"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            candidate_process_id = 1

            response = await client.get(
                f"/api/recruitment-processes/candidate-processes/{candidate_process_id}",
                headers={"Authorization": "Bearer employer_token"}
            )

            assert response.status_code == 200
            data = response.json()
            assert data["id"] == candidate_process_id
            assert "candidate_id" in data
            assert "process_id" in data
            assert "status" in data
            assert "executions" in data
            assert "timeline" in data

    @pytest.mark.asyncio
    async def test_candidate_can_view_own_process(self):
        """Test that candidates can view their own processes"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            candidate_process_id = 1

            response = await client.get(
                f"/api/recruitment-processes/candidate-processes/{candidate_process_id}",
                headers={"Authorization": "Bearer candidate_token"}
            )

            assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_candidate_cannot_view_other_process(self):
        """Test that candidates cannot view other candidate's processes"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            candidate_process_id = 1  # Belongs to different candidate

            response = await client.get(
                f"/api/recruitment-processes/candidate-processes/{candidate_process_id}",
                headers={"Authorization": "Bearer other_candidate_token"}
            )

            assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_start_candidate_process_success(self):
        """Test starting a candidate process"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            candidate_process_id = 1
            start_data = {
                "send_notification": True,
                "custom_message": "Welcome to our recruitment process!"
            }

            response = await client.post(
                f"/api/recruitment-processes/candidate-processes/{candidate_process_id}/start",
                json=start_data,
                headers={"Authorization": "Bearer recruiter_token"}
            )

            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "in_progress"
            assert "started_at" in data
            assert "current_node_id" in data

    @pytest.mark.asyncio
    async def test_start_already_started_process_fails(self):
        """Test starting already started process fails"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            candidate_process_id = 1  # Already started
            start_data = {"send_notification": True}

            response = await client.post(
                f"/api/recruitment-processes/candidate-processes/{candidate_process_id}/start",
                json=start_data,
                headers={"Authorization": "Bearer recruiter_token"}
            )

            assert response.status_code == 409
            assert "already been started" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_update_candidate_process_status_complete(self):
        """Test completing a candidate process"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            candidate_process_id = 1
            status_data = {
                "status": "completed",
                "final_result": "hired",
                "overall_score": 88.5,
                "reason": "Excellent performance throughout the process"
            }

            response = await client.put(
                f"/api/recruitment-processes/candidate-processes/{candidate_process_id}/status",
                json=status_data,
                headers={"Authorization": "Bearer employer_token"}
            )

            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "completed"
            assert data["final_result"] == "hired"
            assert data["overall_score"] == 88.5

    @pytest.mark.asyncio
    async def test_update_candidate_process_status_fail(self):
        """Test failing a candidate process"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            candidate_process_id = 2
            status_data = {
                "status": "failed",
                "reason": "Did not meet technical requirements"
            }

            response = await client.put(
                f"/api/recruitment-processes/candidate-processes/{candidate_process_id}/status",
                json=status_data,
                headers={"Authorization": "Bearer employer_token"}
            )

            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "failed"
            assert data["final_result"] == "failed"

    @pytest.mark.asyncio
    async def test_complete_without_final_result_fails(self):
        """Test that completing without final_result fails"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            candidate_process_id = 1
            status_data = {
                "status": "completed"
                # Missing final_result
            }

            response = await client.put(
                f"/api/recruitment-processes/candidate-processes/{candidate_process_id}/status",
                json=status_data,
                headers={"Authorization": "Bearer employer_token"}
            )

            assert response.status_code == 422
            assert "final result" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_get_candidate_timeline(self):
        """Test getting candidate process timeline"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            candidate_process_id = 1

            response = await client.get(
                f"/api/recruitment-processes/candidate-processes/{candidate_process_id}/timeline",
                headers={"Authorization": "Bearer employer_token"}
            )

            assert response.status_code == 200
            data = response.json()
            assert "candidate_process_id" in data
            assert "candidate_name" in data
            assert "process_name" in data
            assert "current_status" in data
            assert "timeline_items" in data
            assert isinstance(data["timeline_items"], list)

    @pytest.mark.asyncio
    async def test_get_my_candidate_processes_as_candidate(self):
        """Test getting own processes as candidate"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get(
                "/api/recruitment-processes/my-processes",
                headers={"Authorization": "Bearer candidate_token"}
            )

            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, list)

            # All processes should belong to the candidate
            for process in data:
                assert "candidate_id" in process
                assert "process_id" in process
                assert "status" in process

    @pytest.mark.asyncio
    async def test_get_my_candidate_processes_as_recruiter(self):
        """Test getting assigned processes as recruiter"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get(
                "/api/recruitment-processes/my-processes",
                headers={"Authorization": "Bearer recruiter_token"}
            )

            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, list)

            # All processes should be assigned to the recruiter
            for process in data:
                assert "assigned_recruiter_id" in process

    @pytest.mark.asyncio
    async def test_get_recruiter_workload(self):
        """Test getting recruiter workload information"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            recruiter_id = 50

            response = await client.get(
                f"/api/recruitment-processes/recruiters/{recruiter_id}/workload",
                headers={"Authorization": "Bearer employer_token"}
            )

            assert response.status_code == 200
            data = response.json()
            assert data["recruiter_id"] == recruiter_id
            assert "recruiter_name" in data
            assert "active_processes" in data
            assert "pending_tasks" in data
            assert "overdue_tasks" in data
            assert "completion_rate" in data

    @pytest.mark.asyncio
    async def test_recruiter_can_view_own_workload(self):
        """Test that recruiters can view their own workload"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            recruiter_id = 50

            response = await client.get(
                f"/api/recruitment-processes/recruiters/{recruiter_id}/workload",
                headers={"Authorization": f"Bearer recruiter_{recruiter_id}_token"}
            )

            assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_recruiter_cannot_view_other_workload(self):
        """Test that recruiters cannot view other recruiter's workload"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            recruiter_id = 50

            response = await client.get(
                f"/api/recruitment-processes/recruiters/{recruiter_id}/workload",
                headers={"Authorization": "Bearer other_recruiter_token"}
            )

            assert response.status_code == 403


if __name__ == "__main__":
    pytest.main([__file__])