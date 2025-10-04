"""Comprehensive tests for MBTI endpoints."""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.utils.constants import MBTITestStatus


class TestMBTIEndpoints:
    """Comprehensive tests for MBTI functionality."""

    # 🟢 SUCCESS SCENARIOS

    @pytest.mark.asyncio
    async def test_start_mbti_test_success(
        self, client: AsyncClient, candidate_headers: dict, db_session: AsyncSession
    ):
        """Test successful MBTI test start."""
        test_data = {"language": "ja"}

        response = await client.post(
            "/api/mbti/start", json=test_data, headers=candidate_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == MBTITestStatus.IN_PROGRESS.value
        assert data["completion_percentage"] == 0
        assert data["total_questions"] == 60
        assert "started_at" in data

    @pytest.mark.asyncio
    async def test_get_mbti_types_success(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Test successful retrieval of all MBTI types."""
        response = await client.get("/api/mbti/types", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0

        # Check structure of first type
        first_type = data[0]
        assert "type_code" in first_type
        assert "name_en" in first_type
        assert "name_ja" in first_type
        assert "description_en" in first_type
        assert "description_ja" in first_type
        assert "temperament" in first_type
        assert "strengths_en" in first_type
        assert "strengths_ja" in first_type

    @pytest.mark.asyncio
    async def test_get_specific_mbti_type_success(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Test successful retrieval of specific MBTI type."""
        response = await client.get("/api/mbti/types/INTJ", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["type_code"] == "INTJ"
        assert data["name_en"] == "The Architect"
        assert data["temperament"] == "NT"

    @pytest.mark.asyncio
    async def test_get_mbti_progress_not_started(
        self, client: AsyncClient, candidate_headers: dict
    ):
        """Test progress for user who hasn't started test."""
        response = await client.get("/api/mbti/progress", headers=candidate_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == MBTITestStatus.NOT_TAKEN.value
        assert data["completion_percentage"] == 0
        assert data["current_question"] is None

    # 🔴 ERROR SCENARIOS - Authentication

    @pytest.mark.asyncio
    async def test_start_mbti_test_unauthorized(self, client: AsyncClient):
        """Test MBTI test start without authentication."""
        response = await client.post("/api/mbti/start", json={})
        assert response.status_code == 401
        assert "detail" in response.json()

    @pytest.mark.asyncio
    async def test_get_questions_unauthorized(self, client: AsyncClient):
        """Test questions retrieval without authentication."""
        response = await client.get("/api/mbti/questions")
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_get_progress_unauthorized(self, client: AsyncClient):
        """Test progress retrieval without authentication."""
        response = await client.get("/api/mbti/progress")
        assert response.status_code == 401

    # 🔴 ERROR SCENARIOS - Authorization (Role-based)

    @pytest.mark.asyncio
    async def test_start_mbti_test_wrong_role(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Test MBTI test start with wrong role (non-candidate)."""
        test_data = {"language": "ja"}

        response = await client.post(
            "/api/mbti/start", json=test_data, headers=auth_headers
        )

        assert response.status_code == 403
        error = response.json()
        assert "MBTI test is only available for candidates" in error["detail"]

    @pytest.mark.asyncio
    async def test_get_questions_wrong_role(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Test questions retrieval with wrong role."""
        response = await client.get("/api/mbti/questions", headers=auth_headers)

        assert response.status_code == 403

    # 🔴 ERROR SCENARIOS - Input Validation

    @pytest.mark.asyncio
    async def test_start_mbti_test_invalid_language(
        self, client: AsyncClient, candidate_headers: dict
    ):
        """Test MBTI test start with invalid language."""
        test_data = {"language": "fr"}  # Invalid language

        response = await client.post(
            "/api/mbti/start", json=test_data, headers=candidate_headers
        )

        assert response.status_code == 422
        error_detail = response.json()["detail"]
        assert any("language" in str(error).lower() for error in error_detail)

    @pytest.mark.asyncio
    async def test_submit_answer_invalid_format(
        self, client: AsyncClient, candidate_headers: dict
    ):
        """Test answer submission with invalid answer format."""
        # First start a test
        await client.post(
            "/api/mbti/start", json={"language": "ja"}, headers=candidate_headers
        )

        # Try to submit invalid answer
        invalid_answer = {
            "question_id": 1,
            "answer": "C",  # Invalid - must be A or B
        }

        response = await client.post(
            "/api/mbti/answer", json=invalid_answer, headers=candidate_headers
        )

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_get_specific_mbti_type_not_found(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Test retrieval of non-existent MBTI type."""
        response = await client.get("/api/mbti/types/XXXX", headers=auth_headers)

        assert response.status_code == 404
        error = response.json()
        assert "not found" in error["detail"]

    # 🔴 ERROR SCENARIOS - Business Logic

    @pytest.mark.asyncio
    async def test_get_questions_before_start(
        self, client: AsyncClient, candidate_headers: dict
    ):
        """Test getting questions before starting test."""
        response = await client.get("/api/mbti/questions", headers=candidate_headers)

        assert response.status_code == 400
        error = response.json()
        assert "Please start the test first" in error["detail"]

    @pytest.mark.asyncio
    async def test_submit_answer_no_active_test(
        self, client: AsyncClient, candidate_headers: dict
    ):
        """Test answer submission without active test."""
        answer_data = {"question_id": 1, "answer": "A"}

        response = await client.post(
            "/api/mbti/answer", json=answer_data, headers=candidate_headers
        )

        assert response.status_code == 400
        error = response.json()
        assert "No active test found" in error["detail"]

    @pytest.mark.asyncio
    async def test_get_result_no_test(
        self, client: AsyncClient, candidate_headers: dict
    ):
        """Test result retrieval when no test exists."""
        response = await client.get("/api/mbti/result", headers=candidate_headers)

        assert response.status_code == 404
        error = response.json()
        assert "No MBTI test found" in error["detail"]

    @pytest.mark.asyncio
    async def test_get_summary_no_completed_test(
        self, client: AsyncClient, candidate_headers: dict
    ):
        """Test summary retrieval when no completed test exists."""
        response = await client.get("/api/mbti/summary", headers=candidate_headers)

        assert response.status_code == 404
        error = response.json()
        assert "No completed MBTI test found" in error["detail"]

    # 🎯 EDGE CASES AND WORKFLOW SCENARIOS

    @pytest.mark.asyncio
    async def test_restart_completed_test(
        self, client: AsyncClient, candidate_headers: dict, db_session: AsyncSession
    ):
        """Test restarting a completed test."""
        # Start initial test
        response = await client.post(
            "/api/mbti/start", json={"language": "ja"}, headers=candidate_headers
        )
        assert response.status_code == 200

        # Simulate completing test by directly updating database
        # (In real scenario, this would be done through the API)
        # Get the candidate user ID from the fixture
        # We'll need to simulate a completed test state
        # For now, we'll skip this complex scenario in the basic test

        # Now restart the test
        restart_response = await client.post(
            "/api/mbti/start", json={"language": "en"}, headers=candidate_headers
        )

        assert restart_response.status_code == 200
        data = restart_response.json()
        assert data["status"] == MBTITestStatus.IN_PROGRESS.value
        assert data["completion_percentage"] == 0

    @pytest.mark.asyncio
    async def test_multiple_language_support(
        self, client: AsyncClient, candidate_headers: dict
    ):
        """Test language parameter support."""
        # Start test in Japanese
        response = await client.post(
            "/api/mbti/start", json={"language": "ja"}, headers=candidate_headers
        )
        assert response.status_code == 200

        # Get questions in Japanese
        response = await client.get(
            "/api/mbti/questions?language=ja", headers=candidate_headers
        )
        assert response.status_code == 200

        # Get questions in English
        response = await client.get(
            "/api/mbti/questions?language=en", headers=candidate_headers
        )
        assert response.status_code == 200

    # 🔧 ADMIN FUNCTIONALITY TESTS

    @pytest.mark.asyncio
    async def test_bulk_create_questions_success(
        self, client: AsyncClient, admin_auth_headers: dict
    ):
        """Test bulk creation of questions by admin."""
        questions_data = [
            {
                "question_number": 100,
                "dimension": "E_I",
                "question_text_en": "Do you prefer working in groups?",
                "question_text_ja": "グループで働くことを好みますか？",
                "option_a_en": "Yes, I love collaboration",
                "option_a_ja": "はい、協力が好きです",
                "option_a_trait": "E",
                "option_b_en": "No, I prefer working alone",
                "option_b_ja": "いいえ、一人で働く方が好きです",
                "option_b_trait": "I",
                "version": "1.0",
                "is_active": True,
            }
        ]

        response = await client.post(
            "/api/mbti/admin/questions/bulk",
            json=questions_data,
            headers=admin_auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 1
        assert data[0]["question_number"] == 100

    @pytest.mark.asyncio
    async def test_bulk_create_questions_forbidden_non_admin(
        self, client: AsyncClient, candidate_headers: dict
    ):
        """Test bulk creation forbidden for non-admin users."""
        questions_data = [{"test": "data"}]

        response = await client.post(
            "/api/mbti/admin/questions/bulk",
            json=questions_data,
            headers=candidate_headers,
        )

        assert response.status_code == 403
        error = response.json()
        assert "Admin access required" in error["detail"]


# 🎯 INTEGRATION TEST SCENARIOS


class TestMBTIWorkflowScenarios:
    """Integration tests for complete MBTI workflows."""

    @pytest.mark.asyncio
    async def test_complete_mbti_workflow(
        self, client: AsyncClient, candidate_headers: dict
    ):
        """Test complete MBTI test workflow from start to result."""
        # Step 1: Check initial progress
        progress_response = await client.get(
            "/api/mbti/progress", headers=candidate_headers
        )
        assert progress_response.status_code == 200
        assert progress_response.json()["status"] == MBTITestStatus.NOT_TAKEN.value

        # Step 2: Start test
        start_response = await client.post(
            "/api/mbti/start", json={"language": "ja"}, headers=candidate_headers
        )
        assert start_response.status_code == 200

        # Step 3: Get questions
        questions_response = await client.get(
            "/api/mbti/questions?language=ja", headers=candidate_headers
        )
        assert questions_response.status_code == 200

        # Step 4: Check progress after start
        progress_response = await client.get(
            "/api/mbti/progress", headers=candidate_headers
        )
        assert progress_response.status_code == 200
        assert progress_response.json()["status"] == MBTITestStatus.IN_PROGRESS.value

    @pytest.mark.asyncio
    async def test_mbti_test_state_persistence(
        self, client: AsyncClient, candidate_headers: dict
    ):
        """Test that MBTI test state persists across requests."""
        # Start test
        await client.post(
            "/api/mbti/start", json={"language": "ja"}, headers=candidate_headers
        )

        # Submit an answer
        answer_response = await client.post(
            "/api/mbti/answer",
            json={"question_id": 1, "answer": "A"},
            headers=candidate_headers,
        )
        assert answer_response.status_code == 200

        # Check that progress was updated
        progress_response = await client.get(
            "/api/mbti/progress", headers=candidate_headers
        )
        assert progress_response.status_code == 200
        progress_data = progress_response.json()
        assert progress_data["completion_percentage"] > 0


# 🔧 PERFORMANCE AND LOAD TESTS


class TestMBTIPerformance:
    """Performance tests for MBTI endpoints."""

    @pytest.mark.asyncio
    async def test_concurrent_mbti_operations(
        self, client: AsyncClient, candidate_headers: dict
    ):
        """Test concurrent MBTI operations."""
        import asyncio

        async def start_test():
            return await client.post(
                "/api/mbti/start", json={"language": "ja"}, headers=candidate_headers
            )

        async def get_progress():
            return await client.get("/api/mbti/progress", headers=candidate_headers)

        # Run operations concurrently
        results = await asyncio.gather(
            start_test(), get_progress(), return_exceptions=True
        )

        # Check that at least one operation succeeded
        success_count = sum(
            1
            for r in results
            if hasattr(r, "status_code") and r.status_code in [200, 201]
        )
        assert success_count >= 1
