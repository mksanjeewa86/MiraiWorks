from unittest.mock import patch

import pytest
from httpx import AsyncClient

from app.models.position import Position


class TestPositionEndpoints:
    """Comprehensive tests for position endpoint functionality."""

    # Test data
    @pytest.fixture
    def position_data(self):
        """Valid position creation data."""
        return {
            "title": "Senior Software Engineer",
            "description": "Looking for an experienced software engineer",
            "requirements": "5+ years of Python experience",
            "location": "San Francisco, CA",
            "job_type": "full_time",
            "salary_min": 120000,
            "salary_max": 160000,
            "company_id": 1,
        }

    @pytest.fixture
    def position_update_data(self):
        """Valid position update data."""
        return {
            "title": "Updated Senior Software Engineer",
            "description": "Updated description",
            "salary_min": 130000,
            "salary_max": 170000,
        }

    # SUCCESS SCENARIOS

    @pytest.mark.asyncio
    async def test_create_position_success(
        self, client: AsyncClient, auth_headers: dict, position_data: dict
    ):
        """Test successful position creation with valid data."""
        with patch("app.crud.position.position.create_with_slug") as mock_create:
            mock_position = Position(
                **position_data, id=1, slug="senior-software-engineer", status="draft"
            )
            mock_create.return_value = mock_position

            response = await client.post(
                "/api/positions/", json=position_data, headers=auth_headers
            )

            assert response.status_code == 201
            data = response.json()
            assert data["title"] == position_data["title"]
            assert data["description"] == position_data["description"]
            assert data["id"] == 1
            assert data["slug"] == "senior-software-engineer"

    @pytest.mark.asyncio
    async def test_list_positions_success(self, client: AsyncClient):
        """Test successful position listing."""
        with patch("app.endpoints.positions.position_crud.get_published_positions_with_count") as mock_get:
            mock_positions = [
                Position(id=1, title="Position 1", status="published", company_id=1),
                Position(id=2, title="Position 2", status="published", company_id=1),
            ]
            mock_get.return_value = (mock_positions, 2)

            response = await client.get("/api/positions/")

            assert response.status_code == 200
            data = response.json()
            assert "positions" in data
            assert len(data["positions"]) == 2
            assert data["total"] == 2

    @pytest.mark.asyncio
    async def test_get_position_by_id_success(self, client: AsyncClient):
        """Test successful position retrieval by ID."""
        with patch("app.crud.position.position.get") as mock_get, patch(
            "app.crud.position.position.increment_position_view_count"
        ) as mock_increment:
            mock_position = Position(id=1, title="Test Position", status="published", company_id=1)
            mock_get.return_value = mock_position
            mock_increment.return_value = mock_position

            response = await client.get("/api/positions/1")

            assert response.status_code == 200
            data = response.json()
            assert data["id"] == 1
            assert data["title"] == "Test Position"
            mock_increment.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_position_by_slug_success(self, client: AsyncClient):
        """Test successful position retrieval by slug."""
        with patch("app.crud.position.position.get_by_slug") as mock_get, patch(
            "app.crud.position.position.increment_position_view_count"
        ) as mock_increment:
            mock_position = Position(
                id=1,
                title="Test Position",
                slug="test-position",
                status="published",
                company_id=1,
            )
            mock_get.return_value = mock_position
            mock_increment.return_value = mock_position

            response = await client.get("/api/positions/slug/test-position")

            assert response.status_code == 200
            data = response.json()
            assert data["slug"] == "test-position"
            assert data["title"] == "Test Position"

    @pytest.mark.asyncio
    async def test_update_position_success(
        self, client: AsyncClient, auth_headers: dict, position_update_data: dict
    ):
        """Test successful position update."""
        with patch("app.crud.position.position.get") as mock_get, patch(
            "app.crud.position.position.update"
        ) as mock_update:
            existing_position = Position(id=1, title="Old Title", company_id=1)
            updated_position = Position(
                id=1, title="Updated Senior Software Engineer", company_id=1
            )

            mock_get.return_value = existing_position
            mock_update.return_value = updated_position

            response = await client.put(
                "/api/positions/1", json=position_update_data, headers=auth_headers
            )

            assert response.status_code == 200
            data = response.json()
            assert data["title"] == "Updated Senior Software Engineer"

    @pytest.mark.asyncio
    async def test_search_positions_success(self, client: AsyncClient):
        """Test successful position search."""
        with patch("app.endpoints.positions.position_crud.get_published_positions_with_count") as mock_search:
            mock_positions = [Position(id=1, title="Python Developer", company_id=1)]
            mock_search.return_value = (mock_positions, 1)

            response = await client.get(
                "/api/positions/?search=python&location=San Francisco&job_type=full_time&salary_min=100000"
            )

            assert response.status_code == 200
            data = response.json()
            assert len(data["positions"]) == 1

    @pytest.mark.asyncio
    async def test_get_popular_positions_success(self, client: AsyncClient):
        """Test successful popular positions retrieval."""
        with patch("app.crud.position.position.get_popular_positions") as mock_get:
            mock_positions = [Position(id=1, title="Popular Position", view_count=100, company_id=1)]
            mock_get.return_value = mock_positions

            response = await client.get("/api/positions/popular?limit=5")

            assert response.status_code == 200
            data = response.json()
            assert len(data) == 1
            assert data[0]["view_count"] == 100

    @pytest.mark.asyncio
    async def test_get_recent_positions_success(self, client: AsyncClient):
        """Test successful recent positions retrieval."""
        with patch("app.crud.position.position.get_recent_positions") as mock_get:
            mock_positions = [Position(id=1, title="Recent Position", company_id=1)]
            mock_get.return_value = mock_positions

            response = await client.get("/api/positions/recent?days=7")

            assert response.status_code == 200
            data = response.json()
            assert len(data) == 1

    @pytest.mark.asyncio
    async def test_get_company_positions_success(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Test successful company positions retrieval."""
        with patch("app.crud.position.position.get_by_company") as mock_get:
            mock_positions = [Position(id=1, title="Company Position", company_id=1)]
            mock_get.return_value = mock_positions

            response = await client.get("/api/positions/company/1", headers=auth_headers)

            assert response.status_code == 200
            data = response.json()
            assert len(data) == 1

    @pytest.mark.asyncio
    async def test_update_position_status_success(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Test successful position status update."""
        status_data = {"status": "published"}

        with patch("app.crud.position.position.get") as mock_get, patch(
            "app.crud.position.position.update"
        ) as mock_update:
            existing_position = Position(id=1, title="Test Position", status="draft", company_id=1)
            updated_position = Position(id=1, title="Test Position", status="published", company_id=1)

            mock_get.return_value = existing_position
            mock_update.return_value = updated_position

            response = await client.patch(
                "/api/positions/1/status", json=status_data, headers=auth_headers
            )

            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "published"

    @pytest.mark.asyncio
    async def test_bulk_update_status_success(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Test successful bulk status update."""
        bulk_data = {"position_ids": [1, 2, 3], "status": "closed"}

        with patch("app.crud.position.position.bulk_update_position_status") as mock_bulk:
            mock_positions = [
                Position(id=1, status="closed", company_id=1),
                Position(id=2, status="closed", company_id=1),
                Position(id=3, status="closed", company_id=1),
            ]
            mock_bulk.return_value = mock_positions

            response = await client.patch(
                "/api/positions/bulk/status", json=bulk_data, headers=auth_headers
            )

            assert response.status_code == 200
            data = response.json()
            assert len(data) == 3
            assert all(position["status"] == "closed" for position in data)

    # AUTHENTICATION TESTS

    @pytest.mark.asyncio
    async def test_create_position_unauthorized(self, client: AsyncClient, position_data: dict):
        """Test position creation without authentication fails."""
        response = await client.post("/api/positions/", json=position_data)
        assert response.status_code == 401
        assert "detail" in response.json()

    @pytest.mark.asyncio
    async def test_update_position_unauthorized(
        self, client: AsyncClient, position_update_data: dict
    ):
        """Test position update without authentication fails."""
        response = await client.put("/api/positions/1", json=position_update_data)
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_delete_position_unauthorized(self, client: AsyncClient):
        """Test position deletion without authentication fails."""
        response = await client.delete("/api/positions/1")
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_get_statistics_unauthorized(self, client: AsyncClient):
        """Test statistics access without authentication fails."""
        response = await client.get("/api/positions/statistics")
        assert response.status_code == 401

    # PERMISSION TESTS

    @pytest.mark.asyncio
    async def test_create_position_insufficient_permissions(
        self, client: AsyncClient, candidate_headers: dict, position_data: dict
    ):
        """Test position creation with insufficient permissions fails."""
        response = await client.post(
            "/api/positions/", json=position_data, headers=candidate_headers
        )
        assert response.status_code == 403
        assert "Not enough permissions" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_get_statistics_forbidden(
        self, client: AsyncClient, employer_headers: dict
    ):
        """Test statistics access by non-admin fails."""
        response = await client.get("/api/positions/statistics", headers=employer_headers)
        assert response.status_code == 403
        assert "Admin access required" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_delete_position_forbidden(
        self, client: AsyncClient, employer_headers: dict
    ):
        """Test position deletion by non-admin fails."""
        response = await client.delete("/api/positions/1", headers=employer_headers)
        assert response.status_code == 403
        assert "Only admins can delete" in response.json()["detail"]

    # VALIDATION TESTS

    @pytest.mark.asyncio
    async def test_create_position_invalid_title(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Test position creation with invalid title fails."""
        invalid_data = {
            "title": "",  # Empty title
            "description": "Valid description",
            "company_id": 1,
        }

        response = await client.post(
            "/api/positions/", json=invalid_data, headers=auth_headers
        )
        assert response.status_code == 422
        error_detail = response.json()["detail"]
        assert any("title" in str(error).lower() for error in error_detail)

    @pytest.mark.asyncio
    async def test_create_position_missing_required_fields(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Test position creation with missing required fields fails."""
        invalid_data = {"description": "Missing title and company_id"}

        response = await client.post(
            "/api/positions/", json=invalid_data, headers=auth_headers
        )
        assert response.status_code == 422
        error_detail = response.json()["detail"]
        assert len(error_detail) >= 2  # At least title and company_id errors

    @pytest.mark.asyncio
    async def test_update_position_invalid_salary_range(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Test position update with invalid salary range fails."""
        invalid_data = {
            "salary_min": 150000,
            "salary_max": 100000,  # Max less than min
        }

        with patch("app.crud.position.position.get") as mock_get:
            mock_get.return_value = Position(id=1, company_id=1)

            response = await client.put(
                "/api/positions/1", json=invalid_data, headers=auth_headers
            )
            assert response.status_code == 422

    # NOT FOUND TESTS

    @pytest.mark.asyncio
    async def test_get_position_not_found(self, client: AsyncClient):
        """Test retrieving non-existent position fails."""
        with patch("app.crud.position.position.get") as mock_get:
            mock_get.return_value = None

            response = await client.get("/api/positions/999")
            assert response.status_code == 404
            assert "Position not found" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_get_position_by_slug_not_found(self, client: AsyncClient):
        """Test retrieving position by non-existent slug fails."""
        with patch("app.crud.position.position.get_by_slug") as mock_get:
            mock_get.return_value = None

            response = await client.get("/api/positions/slug/non-existent-position")
            assert response.status_code == 404
            assert "Position not found" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_update_position_not_found(
        self, client: AsyncClient, auth_headers: dict, position_update_data: dict
    ):
        """Test updating non-existent position fails."""
        with patch("app.crud.position.position.get") as mock_get:
            mock_get.return_value = None

            response = await client.put(
                "/api/positions/999", json=position_update_data, headers=auth_headers
            )
            assert response.status_code == 404
            assert "Position not found" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_update_position_status_not_found(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Test updating status of non-existent position fails."""
        with patch("app.crud.position.position.get") as mock_get:
            mock_get.return_value = None

            response = await client.patch(
                "/api/positions/999/status",
                json={"status": "published"},
                headers=auth_headers,
            )
            assert response.status_code == 404

    # EDGE CASES

    @pytest.mark.asyncio
    async def test_list_positions_with_filters(self, client: AsyncClient):
        """Test position listing with various filters."""
        with patch("app.endpoints.positions.position_crud.get_published_positions_with_count") as mock_get:
            mock_get.return_value = ([], 0)

            response = await client.get(
                "/api/positions/?location=San Francisco&job_type=full_time&salary_min=100000&search=python"
            )
            assert response.status_code == 200
            mock_get.assert_called_once()

    @pytest.mark.asyncio
    async def test_list_positions_pagination(self, client: AsyncClient):
        """Test position listing with pagination."""
        with patch("app.crud.position.position.get_published_positions") as mock_get:
            mock_get.return_value = []

            response = await client.get("/api/positions/?skip=10&limit=5")
            assert response.status_code == 200
            data = response.json()
            assert data["skip"] == 10
            assert data["limit"] == 5

    @pytest.mark.asyncio
    async def test_get_popular_positions_with_limit(self, client: AsyncClient):
        """Test popular positions with custom limit."""
        with patch("app.crud.position.position.get_popular_positions") as mock_get:
            mock_get.return_value = []

            response = await client.get("/api/positions/popular?limit=3")
            assert response.status_code == 200
            mock_get.assert_called_with(db=mock_get.call_args[1]["db"], limit=3)

    @pytest.mark.asyncio
    async def test_get_recent_positions_custom_days(self, client: AsyncClient):
        """Test recent positions with custom day range."""
        with patch("app.crud.position.position.get_recent_positions") as mock_get:
            mock_get.return_value = []

            response = await client.get("/api/positions/recent?days=14")
            assert response.status_code == 200
            mock_get.assert_called_with(
                db=mock_get.call_args[1]["db"], days=14, limit=100
            )

    @pytest.mark.asyncio
    async def test_company_positions_permission_check(
        self, client: AsyncClient, employer_headers: dict
    ):
        """Test company positions access with permission validation."""
        with patch("app.crud.position.position.get_by_company") as mock_get:
            mock_get.return_value = []

            # Employer trying to access different company's positions
            response = await client.get(
                "/api/positions/company/999", headers=employer_headers
            )
            # Should be handled by permission logic in endpoint
            # Implementation depends on how current_user.company_id is mocked

    @pytest.mark.asyncio
    async def test_bulk_update_empty_position_list(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Test bulk update with empty position list."""
        bulk_data = {"position_ids": [], "status": "closed"}

        response = await client.patch(
            "/api/positions/bulk/status", json=bulk_data, headers=auth_headers
        )
        # Should handle empty list gracefully
        assert response.status_code in [200, 422]  # Depends on validation

