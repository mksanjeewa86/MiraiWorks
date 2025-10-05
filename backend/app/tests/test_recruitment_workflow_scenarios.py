import pytest


class TestRecruitmentWorkflowScenarios:
    """End-to-end scenario tests for recruitment workflows"""

    @pytest.mark.asyncio
    async def test_complete_recruitment_workflow_success_path(
        self, client, auth_headers
    ):
        """Test complete successful recruitment workflow from start to finish"""
        # Step 1: Employer creates a recruitment process
        process_data = {
            "name": "Senior Software Engineer - Technical Track",
            "description": "Complete technical assessment process for senior engineers",
            "settings": {"category": "engineering", "seniority": "senior"},
        }

        response = await client.post(
            "/api/workflows/", json=process_data, headers=auth_headers
        )
        assert response.status_code == 201
        process = response.json()
        workflow_id = process["id"]

        # Step 2: Add nodes to the process
        nodes = [
            {
                "node_type": "interview",
                "title": "HR Screening",
                "description": "Initial screening with HR",
                "sequence_order": 1,
                "position": {"x": 100, "y": 100},
                "config": {
                    "interview_type": "video",
                    "duration_minutes": 30,
                    "interviewers": [10],
                },
                "is_required": True,
            },
            {
                "node_type": "todo",
                "title": "Technical Assignment",
                "description": "Complete the coding assignment",
                "sequence_order": 2,
                "position": {"x": 200, "y": 200},
                "config": {
                    "todo_type": "assignment",
                    "submission_type": "file",
                    "due_in_days": 7,
                    "file_size_limit_mb": 10,
                },
                "is_required": True,
            },
            {
                "node_type": "interview",
                "title": "Technical Interview",
                "description": "Deep dive technical interview",
                "sequence_order": 3,
                "position": {"x": 300, "y": 300},
                "config": {
                    "interview_type": "video",
                    "duration_minutes": 60,
                    "interviewers": [11, 12],
                },
                "is_required": True,
            },
        ]

        # Create each node
        created_nodes = []
        for node_data in nodes:
            response = await client.post(
                f"/api/workflows/{process_id}/nodes",
                json=node_data,
                headers=auth_headers,
            )
            assert response.status_code == 201
            created_nodes.append(response.json())

        # Step 3: Activate the process
        activation_data = {"force_activate": False}
        response = await client.post(
            f"/api/workflows/{process_id}/activate",
            json=activation_data,
            headers=auth_headers,
        )
        assert response.status_code == 200

        # Step 4: Add a candidate to the process
        candidate_data = {
            "candidate_id": 100,
            "workflow_id": workflow_id,
            "position_id": 1,
            "initial_stage": "hr_screening",
        }

        response = await client.post(
            "/api/recruitment-workflows/candidate-processes",
            json=candidate_data,
            headers=auth_headers,
        )
        assert response.status_code == 201
        candidate_workflow = response.json()

        # Step 5: Progress candidate through workflow
        candidate_workflow_id = candidate_workflow["id"]

        # Complete HR screening
        completion_data = {
            "status": "completed",
            "score": 85,
            "feedback": "Candidate shows strong communication skills",
            "execution_data": {
                "interview_duration_minutes": 25,
                "interviewer_notes": "Positive impression",
            },
        }

        response = await client.put(
            f"/api/recruitment-workflows/candidate-processes/{candidate_workflow_id}/advance",
            json=completion_data,
            headers=auth_headers,
        )
        assert response.status_code == 200

        # Verify candidate advanced to next stage
        response = await client.get(
            f"/api/recruitment-workflows/candidate-processes/{candidate_workflow_id}",
            headers=auth_headers,
        )
        assert response.status_code == 200
        updated_process = response.json()
        assert updated_process["current_stage"] == "technical_assignment"

        # Complete technical assignment
        assignment_completion = {
            "status": "completed",
            "score": 92,
            "feedback": "Excellent code quality and problem-solving approach",
            "execution_data": {
                "submission_url": "https://github.com/candidate/assignment",
                "completion_time_hours": 48,
            },
        }

        response = await client.put(
            f"/api/recruitment-workflows/candidate-processes/{candidate_workflow_id}/advance",
            json=assignment_completion,
            headers=auth_headers,
        )
        assert response.status_code == 200

        # Complete technical interview
        tech_interview_completion = {
            "status": "completed",
            "score": 88,
            "feedback": "Strong technical knowledge, good cultural fit",
            "execution_data": {
                "interview_duration_minutes": 65,
                "technical_score": 90,
                "cultural_fit_score": 85,
            },
        }

        response = await client.put(
            f"/api/recruitment-workflows/candidate-processes/{candidate_workflow_id}/advance",
            json=tech_interview_completion,
            headers=auth_headers,
        )
        assert response.status_code == 200

        # Step 6: Verify final process state
        response = await client.get(
            f"/api/recruitment-workflows/candidate-processes/{candidate_workflow_id}",
            headers=auth_headers,
        )
        assert response.status_code == 200
        final_process = response.json()

        assert final_process["status"] == "completed"
        assert final_process["progress_percentage"] == 100
        assert final_process["final_result"] is not None

        # Step 7: Verify process analytics
        response = await client.get(
            f"/api/workflows/{process_id}/analytics", headers=auth_headers
        )
        assert response.status_code == 200
        analytics = response.json()

        assert analytics["total_candidates"] >= 1
        assert analytics["completed_candidates"] >= 1
        assert "average_duration_days" in analytics
        assert "completion_rate" in analytics
