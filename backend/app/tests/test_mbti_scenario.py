"""End-to-end scenario tests for MBTI workflow."""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.utils.constants import MBTITestStatus


class TestMBTIScenarios:
    """End-to-end scenario tests for MBTI functionality."""

    @pytest.mark.asyncio
    async def test_complete_mbti_test_workflow(
        self, client: AsyncClient, candidate_headers: dict
    ):
        """Test complete MBTI workflow from start to finish."""

        # Step 1: Check initial progress - should be NOT_TAKEN
        progress_response = await client.get(
            "/api/mbti/progress",
            headers=candidate_headers
        )
        assert progress_response.status_code == 200
        progress_data = progress_response.json()
        assert progress_data["status"] == MBTITestStatus.NOT_TAKEN.value
        assert progress_data["completion_percentage"] == 0
        assert progress_data["current_question"] is None

        # Step 2: Start the test
        start_response = await client.post(
            "/api/mbti/start",
            json={"language": "ja"},
            headers=candidate_headers
        )
        assert start_response.status_code == 200
        start_data = start_response.json()
        assert start_data["status"] == MBTITestStatus.IN_PROGRESS.value
        assert start_data["completion_percentage"] == 0
        assert start_data["total_questions"] == 60
        assert "started_at" in start_data

        # Step 3: Check progress after starting - should be IN_PROGRESS
        progress_response = await client.get(
            "/api/mbti/progress",
            headers=candidate_headers
        )
        assert progress_response.status_code == 200
        progress_data = progress_response.json()
        assert progress_data["status"] == MBTITestStatus.IN_PROGRESS.value
        assert "started_at" in progress_data

        # Step 4: Get test questions
        questions_response = await client.get(
            "/api/mbti/questions?language=ja",
            headers=candidate_headers
        )
        assert questions_response.status_code == 200
        questions_data = questions_response.json()
        assert isinstance(questions_data, list)

        # Step 5: Submit a few answers to test progress tracking
        if questions_data:
            # Submit first answer
            first_question = questions_data[0]
            answer_response = await client.post(
                "/api/mbti/answer",
                json={
                    "question_id": first_question["id"],
                    "answer": "A"
                },
                headers=candidate_headers
            )
            assert answer_response.status_code == 200
            answer_data = answer_response.json()
            assert answer_data["completion_percentage"] > 0

            # Submit second answer
            if len(questions_data) > 1:
                second_question = questions_data[1]
                answer_response = await client.post(
                    "/api/mbti/answer",
                    json={
                        "question_id": second_question["id"],
                        "answer": "B"
                    },
                    headers=candidate_headers
                )
                assert answer_response.status_code == 200

        # Step 6: Verify progress has been updated
        final_progress_response = await client.get(
            "/api/mbti/progress",
            headers=candidate_headers
        )
        assert final_progress_response.status_code == 200
        final_progress_data = final_progress_response.json()
        assert final_progress_data["completion_percentage"] > 0

    @pytest.mark.asyncio
    async def test_mbti_test_language_switching(
        self, client: AsyncClient, candidate_headers: dict
    ):
        """Test language switching during MBTI test."""

        # Start test in Japanese
        start_response = await client.post(
            "/api/mbti/start",
            json={"language": "ja"},
            headers=candidate_headers
        )
        assert start_response.status_code == 200

        # Get questions in Japanese
        questions_ja_response = await client.get(
            "/api/mbti/questions?language=ja",
            headers=candidate_headers
        )
        assert questions_ja_response.status_code == 200

        # Get questions in English
        questions_en_response = await client.get(
            "/api/mbti/questions?language=en",
            headers=candidate_headers
        )
        assert questions_en_response.status_code == 200

        # Verify both requests returned data
        ja_questions = questions_ja_response.json()
        en_questions = questions_en_response.json()
        assert isinstance(ja_questions, list)
        assert isinstance(en_questions, list)
        assert len(ja_questions) == len(en_questions)

    @pytest.mark.asyncio
    async def test_mbti_test_restart_functionality(
        self, client: AsyncClient, candidate_headers: dict
    ):
        """Test restarting MBTI test."""

        # Start initial test
        start_response = await client.post(
            "/api/mbti/start",
            json={"language": "ja"},
            headers=candidate_headers
        )
        assert start_response.status_code == 200

        # Submit an answer
        questions_response = await client.get(
            "/api/mbti/questions",
            headers=candidate_headers
        )
        assert questions_response.status_code == 200
        questions = questions_response.json()

        if questions:
            answer_response = await client.post(
                "/api/mbti/answer",
                json={
                    "question_id": questions[0]["id"],
                    "answer": "A"
                },
                headers=candidate_headers
            )
            assert answer_response.status_code == 200

        # Start test again (restart)
        restart_response = await client.post(
            "/api/mbti/start",
            json={"language": "en"},  # Different language
            headers=candidate_headers
        )
        assert restart_response.status_code == 200

        # Verify test can still be accessed
        progress_response = await client.get(
            "/api/mbti/progress",
            headers=candidate_headers
        )
        assert progress_response.status_code == 200
        progress_data = progress_response.json()
        assert progress_data["status"] == MBTITestStatus.IN_PROGRESS.value

    @pytest.mark.asyncio
    async def test_mbti_unauthorized_workflow(
        self, client: AsyncClient
    ):
        """Test MBTI workflow without authentication."""

        # All MBTI endpoints should require authentication
        endpoints = [
            "/api/mbti/start",
            "/api/mbti/progress",
            "/api/mbti/questions",
            "/api/mbti/result",
            "/api/mbti/summary"
        ]

        for endpoint in endpoints:
            if endpoint == "/api/mbti/start":
                response = await client.post(endpoint, json={})
            else:
                response = await client.get(endpoint)

            assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_mbti_role_based_access(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Test MBTI access with non-candidate role."""

        # Non-candidate users should be forbidden from MBTI endpoints
        test_endpoints = [
            ("/api/mbti/start", "post", {"language": "ja"}),
            ("/api/mbti/progress", "get", None),
            ("/api/mbti/questions", "get", None)
        ]

        for endpoint, method, payload in test_endpoints:
            if method == "post":
                response = await client.post(endpoint, json=payload, headers=auth_headers)
            else:
                response = await client.get(endpoint, headers=auth_headers)

            assert response.status_code == 403
            error = response.json()
            assert "candidates" in error["detail"].lower()

    @pytest.mark.asyncio
    async def test_mbti_type_information_access(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Test MBTI type information endpoints (accessible to all authenticated users)."""

        # Get all types
        all_types_response = await client.get(
            "/api/mbti/types",
            headers=auth_headers
        )
        assert all_types_response.status_code == 200
        all_types_data = all_types_response.json()
        assert isinstance(all_types_data, list)
        assert len(all_types_data) > 0

        # Verify structure of type info
        first_type = all_types_data[0]
        required_fields = [
            "type_code", "name_en", "name_ja", "description_en",
            "description_ja", "temperament", "strengths_en", "strengths_ja"
        ]
        for field in required_fields:
            assert field in first_type

        # Get specific type
        specific_type_response = await client.get(
            "/api/mbti/types/INTJ",
            headers=auth_headers
        )
        assert specific_type_response.status_code == 200
        specific_type_data = specific_type_response.json()
        assert specific_type_data["type_code"] == "INTJ"
        assert specific_type_data["name_en"] == "The Architect"

        # Test non-existent type
        invalid_type_response = await client.get(
            "/api/mbti/types/XXXX",
            headers=auth_headers
        )
        assert invalid_type_response.status_code == 404

    @pytest.mark.asyncio
    async def test_mbti_validation_scenarios(
        self, client: AsyncClient, candidate_headers: dict
    ):
        """Test various input validation scenarios."""

        # Test invalid language code
        invalid_language_response = await client.post(
            "/api/mbti/start",
            json={"language": "fr"},  # Invalid language
            headers=candidate_headers
        )
        assert invalid_language_response.status_code == 422

        # Start valid test for further testing
        start_response = await client.post(
            "/api/mbti/start",
            json={"language": "ja"},
            headers=candidate_headers
        )
        assert start_response.status_code == 200

        # Test invalid answer format
        invalid_answer_response = await client.post(
            "/api/mbti/answer",
            json={
                "question_id": 1,
                "answer": "C"  # Invalid answer - must be A or B
            },
            headers=candidate_headers
        )
        assert invalid_answer_response.status_code == 422

        # Test invalid question format in questions endpoint
        invalid_lang_questions = await client.get(
            "/api/mbti/questions?language=es",  # Invalid language
            headers=candidate_headers
        )
        assert invalid_lang_questions.status_code == 422

    @pytest.mark.asyncio
    async def test_mbti_error_handling_workflow(
        self, client: AsyncClient, candidate_headers: dict
    ):
        """Test error handling in MBTI workflow."""

        # Try to get questions without starting test
        questions_response = await client.get(
            "/api/mbti/questions",
            headers=candidate_headers
        )
        assert questions_response.status_code == 400
        error = questions_response.json()
        assert "start the test first" in error["detail"]

        # Try to submit answer without starting test
        answer_response = await client.post(
            "/api/mbti/answer",
            json={
                "question_id": 1,
                "answer": "A"
            },
            headers=candidate_headers
        )
        assert answer_response.status_code == 400
        error = answer_response.json()
        assert "No active test found" in error["detail"]

        # Try to get result without test
        result_response = await client.get(
            "/api/mbti/result",
            headers=candidate_headers
        )
        assert result_response.status_code == 404

        # Try to get summary without completed test
        summary_response = await client.get(
            "/api/mbti/summary",
            headers=candidate_headers
        )
        assert summary_response.status_code == 404