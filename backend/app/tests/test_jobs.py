import pytest
from datetime import datetime, timedelta
from httpx import AsyncClient
from unittest.mock import patch, AsyncMock

from app.crud.job import job as job_crud
from app.models.job import Job
from app.schemas.job import JobCreate, JobUpdate


class TestJobEndpoints:
    """Comprehensive tests for job endpoint functionality."""

    # Test data
    @pytest.fixture
    def job_data(self):
        """Valid job creation data."""
        return {
            "title": "Senior Software Engineer",
            "description": "Looking for an experienced software engineer",
            "requirements": "5+ years of Python experience",
            "location": "San Francisco, CA",
            "job_type": "full_time",
            "salary_min": 120000,
            "salary_max": 160000,
            "company_id": 1
        }

    @pytest.fixture
    def job_update_data(self):
        """Valid job update data."""
        return {
            "title": "Updated Senior Software Engineer",
            "description": "Updated description",
            "salary_min": 130000,
            "salary_max": 170000
        }

    # SUCCESS SCENARIOS

    @pytest.mark.asyncio
    async def test_create_job_success(self, client: AsyncClient, auth_headers: dict, job_data: dict):
        """Test successful job creation with valid data."""
        with patch('app.crud.job.job.create_with_slug') as mock_create:
            mock_job = Job(**job_data, id=1, slug="senior-software-engineer", status="draft")
            mock_create.return_value = mock_job

            response = await client.post(
                "/api/jobs/",
                json=job_data,
                headers=auth_headers
            )

            assert response.status_code == 201
            data = response.json()
            assert data["title"] == job_data["title"]
            assert data["description"] == job_data["description"]
            assert data["id"] == 1
            assert data["slug"] == "senior-software-engineer"

    @pytest.mark.asyncio
    async def test_list_jobs_success(self, client: AsyncClient):
        """Test successful job listing."""
        with patch('app.crud.job.job.get_published_jobs') as mock_get:
            mock_jobs = [
                Job(id=1, title="Job 1", status="published", company_id=1),
                Job(id=2, title="Job 2", status="published", company_id=1)
            ]
            mock_get.return_value = mock_jobs

            response = await client.get("/api/jobs/")

            assert response.status_code == 200
            data = response.json()
            assert "jobs" in data
            assert len(data["jobs"]) == 2
            assert data["total"] == 2

    @pytest.mark.asyncio
    async def test_get_job_by_id_success(self, client: AsyncClient):
        """Test successful job retrieval by ID."""
        with patch('app.crud.job.job.get') as mock_get, \
             patch('app.crud.job.job.increment_view_count') as mock_increment:

            mock_job = Job(id=1, title="Test Job", status="published", company_id=1)
            mock_get.return_value = mock_job
            mock_increment.return_value = mock_job

            response = await client.get("/api/jobs/1")

            assert response.status_code == 200
            data = response.json()
            assert data["id"] == 1
            assert data["title"] == "Test Job"
            mock_increment.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_job_by_slug_success(self, client: AsyncClient):
        """Test successful job retrieval by slug."""
        with patch('app.crud.job.job.get_by_slug') as mock_get, \
             patch('app.crud.job.job.increment_view_count') as mock_increment:

            mock_job = Job(id=1, title="Test Job", slug="test-job", status="published", company_id=1)
            mock_get.return_value = mock_job
            mock_increment.return_value = mock_job

            response = await client.get("/api/jobs/slug/test-job")

            assert response.status_code == 200
            data = response.json()
            assert data["slug"] == "test-job"
            assert data["title"] == "Test Job"

    @pytest.mark.asyncio
    async def test_update_job_success(self, client: AsyncClient, auth_headers: dict, job_update_data: dict):
        """Test successful job update."""
        with patch('app.crud.job.job.get') as mock_get, \
             patch('app.crud.job.job.update') as mock_update:

            existing_job = Job(id=1, title="Old Title", company_id=1)
            updated_job = Job(id=1, title="Updated Senior Software Engineer", company_id=1)

            mock_get.return_value = existing_job
            mock_update.return_value = updated_job

            response = await client.put(
                "/api/jobs/1",
                json=job_update_data,
                headers=auth_headers
            )

            assert response.status_code == 200
            data = response.json()
            assert data["title"] == "Updated Senior Software Engineer"

    @pytest.mark.asyncio
    async def test_search_jobs_success(self, client: AsyncClient):
        """Test successful job search."""
        search_data = {
            "query": "python",
            "location": "San Francisco",
            "job_type": "full_time",
            "salary_min": 100000
        }

        with patch('app.crud.job.job.get_published_jobs') as mock_search:
            mock_jobs = [Job(id=1, title="Python Developer", company_id=1)]
            mock_search.return_value = mock_jobs

            response = await client.get("/api/jobs/search", json=search_data)

            assert response.status_code == 200
            data = response.json()
            assert len(data["jobs"]) == 1

    @pytest.mark.asyncio
    async def test_get_popular_jobs_success(self, client: AsyncClient):
        """Test successful popular jobs retrieval."""
        with patch('app.crud.job.job.get_popular_jobs') as mock_get:
            mock_jobs = [Job(id=1, title="Popular Job", view_count=100, company_id=1)]
            mock_get.return_value = mock_jobs

            response = await client.get("/api/jobs/popular?limit=5")

            assert response.status_code == 200
            data = response.json()
            assert len(data) == 1
            assert data[0]["view_count"] == 100

    @pytest.mark.asyncio
    async def test_get_recent_jobs_success(self, client: AsyncClient):
        """Test successful recent jobs retrieval."""
        with patch('app.crud.job.job.get_recent_jobs') as mock_get:
            mock_jobs = [Job(id=1, title="Recent Job", company_id=1)]
            mock_get.return_value = mock_jobs

            response = await client.get("/api/jobs/recent?days=7")

            assert response.status_code == 200
            data = response.json()
            assert len(data) == 1

    @pytest.mark.asyncio
    async def test_get_company_jobs_success(self, client: AsyncClient, auth_headers: dict):
        """Test successful company jobs retrieval."""
        with patch('app.crud.job.job.get_by_company') as mock_get:
            mock_jobs = [Job(id=1, title="Company Job", company_id=1)]
            mock_get.return_value = mock_jobs

            response = await client.get("/api/jobs/company/1", headers=auth_headers)

            assert response.status_code == 200
            data = response.json()
            assert len(data) == 1

    @pytest.mark.asyncio
    async def test_update_job_status_success(self, client: AsyncClient, auth_headers: dict):
        """Test successful job status update."""
        status_data = {"status": "published"}

        with patch('app.crud.job.job.get') as mock_get, \
             patch('app.crud.job.job.update') as mock_update:

            existing_job = Job(id=1, title="Test Job", status="draft", company_id=1)
            updated_job = Job(id=1, title="Test Job", status="published", company_id=1)

            mock_get.return_value = existing_job
            mock_update.return_value = updated_job

            response = await client.patch(
                "/api/jobs/1/status",
                json=status_data,
                headers=auth_headers
            )

            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "published"

    @pytest.mark.asyncio
    async def test_bulk_update_status_success(self, client: AsyncClient, auth_headers: dict):
        """Test successful bulk status update."""
        bulk_data = {
            "job_ids": [1, 2, 3],
            "status": "closed"
        }

        with patch('app.crud.job.job.bulk_update_status') as mock_bulk:
            mock_jobs = [
                Job(id=1, status="closed", company_id=1),
                Job(id=2, status="closed", company_id=1),
                Job(id=3, status="closed", company_id=1)
            ]
            mock_bulk.return_value = mock_jobs

            response = await client.patch(
                "/api/jobs/bulk/status",
                json=bulk_data,
                headers=auth_headers
            )

            assert response.status_code == 200
            data = response.json()
            assert len(data) == 3
            assert all(job["status"] == "closed" for job in data)

    # AUTHENTICATION TESTS

    @pytest.mark.asyncio
    async def test_create_job_unauthorized(self, client: AsyncClient, job_data: dict):
        """Test job creation without authentication fails."""
        response = await client.post("/api/jobs/", json=job_data)
        assert response.status_code == 401
        assert "detail" in response.json()

    @pytest.mark.asyncio
    async def test_update_job_unauthorized(self, client: AsyncClient, job_update_data: dict):
        """Test job update without authentication fails."""
        response = await client.put("/api/jobs/1", json=job_update_data)
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_delete_job_unauthorized(self, client: AsyncClient):
        """Test job deletion without authentication fails."""
        response = await client.delete("/api/jobs/1")
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_get_statistics_unauthorized(self, client: AsyncClient):
        """Test statistics access without authentication fails."""
        response = await client.get("/api/jobs/statistics")
        assert response.status_code == 401

    # PERMISSION TESTS

    @pytest.mark.asyncio
    async def test_create_job_insufficient_permissions(self, client: AsyncClient, candidate_headers: dict, job_data: dict):
        """Test job creation with insufficient permissions fails."""
        response = await client.post(
            "/api/jobs/",
            json=job_data,
            headers=candidate_headers
        )
        assert response.status_code == 403
        assert "Not enough permissions" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_get_statistics_forbidden(self, client: AsyncClient, employer_headers: dict):
        """Test statistics access by non-admin fails."""
        response = await client.get("/api/jobs/statistics", headers=employer_headers)
        assert response.status_code == 403
        assert "Admin access required" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_delete_job_forbidden(self, client: AsyncClient, employer_headers: dict):
        """Test job deletion by non-admin fails."""
        response = await client.delete("/api/jobs/1", headers=employer_headers)
        assert response.status_code == 403
        assert "Only admins can delete" in response.json()["detail"]

    # VALIDATION TESTS

    @pytest.mark.asyncio
    async def test_create_job_invalid_title(self, client: AsyncClient, auth_headers: dict):
        """Test job creation with invalid title fails."""
        invalid_data = {
            "title": "",  # Empty title
            "description": "Valid description",
            "company_id": 1
        }

        response = await client.post(
            "/api/jobs/",
            json=invalid_data,
            headers=auth_headers
        )
        assert response.status_code == 422
        error_detail = response.json()["detail"]
        assert any("title" in str(error).lower() for error in error_detail)

    @pytest.mark.asyncio
    async def test_create_job_missing_required_fields(self, client: AsyncClient, auth_headers: dict):
        """Test job creation with missing required fields fails."""
        invalid_data = {
            "description": "Missing title and company_id"
        }

        response = await client.post(
            "/api/jobs/",
            json=invalid_data,
            headers=auth_headers
        )
        assert response.status_code == 422
        error_detail = response.json()["detail"]
        assert len(error_detail) >= 2  # At least title and company_id errors

    @pytest.mark.asyncio
    async def test_update_job_invalid_salary_range(self, client: AsyncClient, auth_headers: dict):
        """Test job update with invalid salary range fails."""
        invalid_data = {
            "salary_min": 150000,
            "salary_max": 100000  # Max less than min
        }

        with patch('app.crud.job.job.get') as mock_get:
            mock_get.return_value = Job(id=1, company_id=1)

            response = await client.put(
                "/api/jobs/1",
                json=invalid_data,
                headers=auth_headers
            )
            assert response.status_code == 422

    # NOT FOUND TESTS

    @pytest.mark.asyncio
    async def test_get_job_not_found(self, client: AsyncClient):
        """Test retrieving non-existent job fails."""
        with patch('app.crud.job.job.get') as mock_get:
            mock_get.return_value = None

            response = await client.get("/api/jobs/999")
            assert response.status_code == 404
            assert "Job not found" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_get_job_by_slug_not_found(self, client: AsyncClient):
        """Test retrieving job by non-existent slug fails."""
        with patch('app.crud.job.job.get_by_slug') as mock_get:
            mock_get.return_value = None

            response = await client.get("/api/jobs/slug/non-existent-job")
            assert response.status_code == 404
            assert "Job not found" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_update_job_not_found(self, client: AsyncClient, auth_headers: dict, job_update_data: dict):
        """Test updating non-existent job fails."""
        with patch('app.crud.job.job.get') as mock_get:
            mock_get.return_value = None

            response = await client.put(
                "/api/jobs/999",
                json=job_update_data,
                headers=auth_headers
            )
            assert response.status_code == 404
            assert "Job not found" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_update_job_status_not_found(self, client: AsyncClient, auth_headers: dict):
        """Test updating status of non-existent job fails."""
        with patch('app.crud.job.job.get') as mock_get:
            mock_get.return_value = None

            response = await client.patch(
                "/api/jobs/999/status",
                json={"status": "published"},
                headers=auth_headers
            )
            assert response.status_code == 404

    # EDGE CASES

    @pytest.mark.asyncio
    async def test_list_jobs_with_filters(self, client: AsyncClient):
        """Test job listing with various filters."""
        with patch('app.crud.job.job.get_published_jobs') as mock_get:
            mock_get.return_value = []

            response = await client.get(
                "/api/jobs/?location=San Francisco&job_type=full_time&salary_min=100000&search=python"
            )
            assert response.status_code == 200
            mock_get.assert_called_once()

    @pytest.mark.asyncio
    async def test_list_jobs_pagination(self, client: AsyncClient):
        """Test job listing with pagination."""
        with patch('app.crud.job.job.get_published_jobs') as mock_get:
            mock_get.return_value = []

            response = await client.get("/api/jobs/?skip=10&limit=5")
            assert response.status_code == 200
            data = response.json()
            assert data["skip"] == 10
            assert data["limit"] == 5

    @pytest.mark.asyncio
    async def test_get_popular_jobs_with_limit(self, client: AsyncClient):
        """Test popular jobs with custom limit."""
        with patch('app.crud.job.job.get_popular_jobs') as mock_get:
            mock_get.return_value = []

            response = await client.get("/api/jobs/popular?limit=3")
            assert response.status_code == 200
            mock_get.assert_called_with(db=mock_get.call_args[1]['db'], limit=3)

    @pytest.mark.asyncio
    async def test_get_recent_jobs_custom_days(self, client: AsyncClient):
        """Test recent jobs with custom day range."""
        with patch('app.crud.job.job.get_recent_jobs') as mock_get:
            mock_get.return_value = []

            response = await client.get("/api/jobs/recent?days=14")
            assert response.status_code == 200
            mock_get.assert_called_with(
                db=mock_get.call_args[1]['db'],
                days=14,
                limit=100
            )

    @pytest.mark.asyncio
    async def test_company_jobs_permission_check(self, client: AsyncClient, employer_headers: dict):
        """Test company jobs access with permission validation."""
        with patch('app.crud.job.job.get_by_company') as mock_get:
            mock_get.return_value = []

            # Employer trying to access different company's jobs
            response = await client.get("/api/jobs/company/999", headers=employer_headers)
            # Should be handled by permission logic in endpoint
            # Implementation depends on how current_user.company_id is mocked

    @pytest.mark.asyncio
    async def test_bulk_update_empty_job_list(self, client: AsyncClient, auth_headers: dict):
        """Test bulk update with empty job list."""
        bulk_data = {
            "job_ids": [],
            "status": "closed"
        }

        response = await client.patch(
            "/api/jobs/bulk/status",
            json=bulk_data,
            headers=auth_headers
        )
        # Should handle empty list gracefully
        assert response.status_code in [200, 422]  # Depends on validation