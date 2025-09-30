import pytest
from httpx import AsyncClient
from datetime import datetime, timedelta

from app.main import app


class TestRecruitmentWorkflowScenarios:
    """End-to-end scenario tests for recruitment workflows"""

    @pytest.mark.asyncio
    async def test_complete_recruitment_workflow_success_path(self, client, auth_headers):
        """Test complete successful recruitment workflow from start to finish"""
            # Step 1: Employer creates a recruitment process
            process_data = {
                "name": "Senior Software Engineer - Technical Track",
                "description": "Complete technical assessment process for senior engineers",
                "settings": {
                    "category": "engineering",
                    "seniority": "senior"
                }
            }

            response = await client.post(
                "/api/recruitment-processes/",
                json=process_data,
                headers=auth_headers
            )
            assert response.status_code == 201
            process = response.json()
            process_id = process["id"]

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
                        "interviewers": [10]
                    },
                    "is_required": True
                },
                {
                    "node_type": "todo",
                    "title": "Coding Assignment",
                    "description": "Take-home coding challenge",
                    "sequence_order": 2,
                    "position": {"x": 200, "y": 100},
                    "config": {
                        "todo_type": "assignment",
                        "due_in_days": 3,
                        "submission_type": "file",
                        "file_size_limit_mb": 10
                    },
                    "requirements": ["Complete within 3 days", "Upload to platform"]
                },
                {
                    "node_type": "interview",
                    "title": "Technical Interview",
                    "description": "Deep technical discussion",
                    "sequence_order": 3,
                    "position": {"x": 300, "y": 100},
                    "config": {
                        "interview_type": "video",
                        "duration_minutes": 60,
                        "interviewers": [11, 12]
                    }
                },
                {
                    "node_type": "interview",
                    "title": "Final Interview",
                    "description": "Cultural fit and role expectations",
                    "sequence_order": 4,
                    "position": {"x": 400, "y": 100},
                    "config": {
                        "interview_type": "video",
                        "duration_minutes": 45,
                        "interviewers": [13]
                    }
                }
            ]

            created_nodes = []
            for node_data in nodes:
                response = await client.post(
                    f"/api/recruitment-processes/{process_id}/nodes",
                    json=node_data,
                    headers=auth_headers
                )
                assert response.status_code == 201
                created_nodes.append(response.json())

            # Step 3: Create connections between nodes
            connections = [
                {
                    "source_node_id": created_nodes[0]["id"],
                    "target_node_id": created_nodes[1]["id"],
                    "condition_type": "success"
                },
                {
                    "source_node_id": created_nodes[1]["id"],
                    "target_node_id": created_nodes[2]["id"],
                    "condition_type": "success"
                },
                {
                    "source_node_id": created_nodes[2]["id"],
                    "target_node_id": created_nodes[3]["id"],
                    "condition_type": "success"
                }
            ]

            for connection_data in connections:
                response = await client.post(
                    f"/api/recruitment-processes/{process_id}/connections",
                    json=connection_data,
                    headers=auth_headers
                )
                assert response.status_code == 201

            # Step 4: Add recruiter as viewer
            viewer_data = {
                "user_id": 50,
                "role": "recruiter"
            }

            response = await client.post(
                f"/api/recruitment-processes/{process_id}/viewers",
                json=viewer_data,
                headers=auth_headers
            )
            assert response.status_code == 201

            # Step 5: Validate and activate the process
            response = await client.get(
                f"/api/recruitment-processes/{process_id}/validate",
                headers=auth_headers
            )
            assert response.status_code == 200
            validation = response.json()
            assert validation["is_valid"] is True

            response = await client.post(
                f"/api/recruitment-processes/{process_id}/activate",
                json={"force_activate": False},
                headers=auth_headers
            )
            assert response.status_code == 200

            # Step 6: Assign a candidate to the process
            assignment_data = {
                "candidate_id": 100,
                "assigned_recruiter_id": 50,
                "start_immediately": True
            }

            response = await client.post(
                f"/api/recruitment-processes/{process_id}/candidates",
                json=assignment_data,
                headers=auth_headers
            )
            assert response.status_code == 201
            candidate_process = response.json()
            candidate_process_id = candidate_process["id"]

            assert candidate_process["status"] == "in_progress"
            assert candidate_process["assigned_recruiter_id"] == 50

            # Step 7: Complete HR Screening (first node)
            # Get current executions
            response = await client.get(
                f"/api/recruitment-processes/candidate-processes/{candidate_process_id}",
                headers={"Authorization": "Bearer recruiter_token"}
            )
            assert response.status_code == 200
            candidate_details = response.json()

            # Find first execution
            hr_execution = next(
                (exec for exec in candidate_details["executions"]
                 if exec["node"]["title"] == "HR Screening"), None
            )
            assert hr_execution is not None
            hr_execution_id = hr_execution["id"]

            # Complete HR screening
            completion_data = {
                "result": "pass",
                "score": 85.0,
                "feedback": "Good communication skills and relevant experience",
                "execution_data": {"notes": "Candidate shows strong potential"}
            }

            response = await client.post(
                f"/api/recruitment-processes/executions/{hr_execution_id}/complete",
                json=completion_data,
                headers={"Authorization": "Bearer recruiter_token"}
            )
            assert response.status_code == 200

            # Step 8: Complete Coding Assignment (second node)
            # Get updated process state
            response = await client.get(
                f"/api/recruitment-processes/candidate-processes/{candidate_process_id}",
                headers={"Authorization": "Bearer recruiter_token"}
            )
            candidate_details = response.json()

            coding_execution = next(
                (exec for exec in candidate_details["executions"]
                 if exec["node"]["title"] == "Coding Assignment" and exec["status"] != "completed"), None
            )
            assert coding_execution is not None

            # Simulate candidate submission first
            submission_data = {
                "submission_type": "file",
                "content": "# My coding solution\nprint('Hello World')",
                "notes": "Completed the assignment as requested"
            }

            response = await client.post(
                f"/api/recruitment-processes/executions/{coding_execution['id']}/submit",
                json=submission_data,
                headers={"Authorization": "Bearer candidate_token"}
            )
            assert response.status_code == 200

            # Recruiter reviews and completes
            review_data = {
                "result": "pass",
                "score": 90.0,
                "feedback": "Excellent code quality and problem-solving approach",
                "execution_data": {"code_quality": "excellent", "test_coverage": "good"}
            }

            response = await client.post(
                f"/api/recruitment-processes/executions/{coding_execution['id']}/complete",
                json=review_data,
                headers={"Authorization": "Bearer recruiter_token"}
            )
            assert response.status_code == 200

            # Step 9: Complete Technical Interview
            response = await client.get(
                f"/api/recruitment-processes/candidate-processes/{candidate_process_id}",
                headers={"Authorization": "Bearer recruiter_token"}
            )
            candidate_details = response.json()

            tech_execution = next(
                (exec for exec in candidate_details["executions"]
                 if exec["node"]["title"] == "Technical Interview" and exec["status"] != "completed"), None
            )
            assert tech_execution is not None

            # Complete technical interview
            tech_completion = {
                "result": "pass",
                "score": 88.0,
                "feedback": "Strong technical knowledge, good system design thinking",
                "execution_data": {"technical_depth": "high", "communication": "clear"}
            }

            response = await client.post(
                f"/api/recruitment-processes/executions/{tech_execution['id']}/complete",
                json=tech_completion,
                headers={"Authorization": "Bearer recruiter_token"}
            )
            assert response.status_code == 200

            # Step 10: Complete Final Interview
            response = await client.get(
                f"/api/recruitment-processes/candidate-processes/{candidate_process_id}",
                headers={"Authorization": "Bearer recruiter_token"}
            )
            candidate_details = response.json()

            final_execution = next(
                (exec for exec in candidate_details["executions"]
                 if exec["node"]["title"] == "Final Interview" and exec["status"] != "completed"), None
            )
            assert final_execution is not None

            # Complete final interview
            final_completion = {
                "result": "pass",
                "score": 92.0,
                "feedback": "Great cultural fit, aligns well with team values",
                "execution_data": {"culture_fit": "excellent", "leadership_potential": "high"}
            }

            response = await client.post(
                f"/api/recruitment-processes/executions/{final_execution['id']}/complete",
                json=final_completion,
                headers={"Authorization": "Bearer recruiter_token"}
            )
            assert response.status_code == 200

            # Step 11: Process should auto-complete or employer makes final decision
            response = await client.get(
                f"/api/recruitment-processes/candidate-processes/{candidate_process_id}",
                headers=auth_headers
            )
            candidate_details = response.json()

            if candidate_details["status"] != "completed":
                # Employer makes final decision
                final_decision = {
                    "status": "completed",
                    "final_result": "hired",
                    "overall_score": 88.75,  # Average of all scores
                    "reason": "Excellent performance across all evaluation criteria"
                }

                response = await client.put(
                    f"/api/recruitment-processes/candidate-processes/{candidate_process_id}/status",
                    json=final_decision,
                    headers=auth_headers
                )
                assert response.status_code == 200
                final_candidate_process = response.json()
            else:
                final_candidate_process = candidate_details

            # Step 12: Verify final state
            assert final_candidate_process["status"] == "completed"
            assert final_candidate_process["final_result"] == "hired"
            assert final_candidate_process["overall_score"] is not None
            assert final_candidate_process["completed_at"] is not None

            # Step 13: Get timeline to verify complete journey
            response = await client.get(
                f"/api/recruitment-processes/candidate-processes/{candidate_process_id}/timeline",
                headers=auth_headers
            )
            assert response.status_code == 200
            timeline = response.json()

            # Verify timeline has all major events
            event_types = {item["event_type"] for item in timeline["timeline_items"]}
            expected_events = {
                "process_started",
                "node_completed",  # Multiple instances
                "process_completed"
            }

            assert expected_events.issubset(event_types)
            assert len(timeline["timeline_items"]) >= 6  # Start + 4 node completions + end

            # Step 14: Get process analytics
            response = await client.get(
                f"/api/recruitment-processes/{process_id}/analytics",
                headers=auth_headers
            )
            assert response.status_code == 200
            analytics = response.json()

            assert analytics["total_candidates"] >= 1
            assert analytics["completed_candidates"] >= 1
            assert analytics["completion_rate"] > 0
            assert len(analytics["node_statistics"]) == 4  # 4 nodes

    @pytest.mark.asyncio
    async def test_recruitment_workflow_candidate_failure_path(self, client, auth_headers):
        """Test recruitment workflow where candidate fails at technical interview"""
            # Setup similar to success path but with failure at technical interview

            # Create process and nodes (abbreviated setup)
            process_data = {
                "name": "Failure Path Test Process",
                "description": "Test process for failure scenario"
            }

            response = await client.post(
                "/api/recruitment-processes/",
                json=process_data,
                headers=auth_headers
            )
            process_id = response.json()["id"]

            # Add basic nodes
            nodes = [
                {
                    "node_type": "interview",
                    "title": "HR Screening",
                    "sequence_order": 1,
                    "position": {"x": 100, "y": 100},
                    "config": {"interview_type": "video", "duration_minutes": 30}
                },
                {
                    "node_type": "interview",
                    "title": "Technical Interview",
                    "sequence_order": 2,
                    "position": {"x": 200, "y": 100},
                    "config": {"interview_type": "video", "duration_minutes": 60}
                }
            ]

            created_nodes = []
            for node_data in nodes:
                response = await client.post(
                    f"/api/recruitment-processes/{process_id}/nodes",
                    json=node_data,
                    headers=auth_headers
                )
                created_nodes.append(response.json())

            # Create success and failure connections
            connections = [
                {
                    "source_node_id": created_nodes[0]["id"],
                    "target_node_id": created_nodes[1]["id"],
                    "condition_type": "success"
                }
            ]

            for connection_data in connections:
                await client.post(
                    f"/api/recruitment-processes/{process_id}/connections",
                    json=connection_data,
                    headers=auth_headers
                )

            # Activate process
            await client.post(
                f"/api/recruitment-processes/{process_id}/activate",
                json={"force_activate": True},
                headers=auth_headers
            )

            # Assign candidate
            assignment_data = {
                "candidate_id": 200,
                "assigned_recruiter_id": 50,
                "start_immediately": True
            }

            response = await client.post(
                f"/api/recruitment-processes/{process_id}/candidates",
                json=assignment_data,
                headers=auth_headers
            )
            candidate_process_id = response.json()["id"]

            # Complete HR screening successfully
            response = await client.get(
                f"/api/recruitment-processes/candidate-processes/{candidate_process_id}",
                headers={"Authorization": "Bearer recruiter_token"}
            )
            candidate_details = response.json()

            hr_execution = next(
                (exec for exec in candidate_details["executions"]
                 if exec["node"]["title"] == "HR Screening"), None
            )

            await client.post(
                f"/api/recruitment-processes/executions/{hr_execution['id']}/complete",
                json={
                    "result": "pass",
                    "score": 75.0,
                    "feedback": "Meets basic requirements"
                },
                headers={"Authorization": "Bearer recruiter_token"}
            )

            # Fail technical interview
            response = await client.get(
                f"/api/recruitment-processes/candidate-processes/{candidate_process_id}",
                headers={"Authorization": "Bearer recruiter_token"}
            )
            candidate_details = response.json()

            tech_execution = next(
                (exec for exec in candidate_details["executions"]
                 if exec["node"]["title"] == "Technical Interview" and exec["status"] != "completed"), None
            )

            # Fail the technical interview
            await client.post(
                f"/api/recruitment-processes/executions/{tech_execution['id']}/complete",
                json={
                    "result": "fail",
                    "score": 40.0,
                    "feedback": "Insufficient technical depth for senior role"
                },
                headers={"Authorization": "Bearer recruiter_token"}
            )

            # Process should be failed or employer makes rejection decision
            response = await client.get(
                f"/api/recruitment-processes/candidate-processes/{candidate_process_id}",
                headers=auth_headers
            )
            candidate_details = response.json()

            if candidate_details["status"] != "failed":
                # Employer makes rejection decision
                rejection_decision = {
                    "status": "failed",
                    "reason": "Did not meet technical requirements for senior role"
                }

                response = await client.put(
                    f"/api/recruitment-processes/candidate-processes/{candidate_process_id}/status",
                    json=rejection_decision,
                    headers=auth_headers
                )
                assert response.status_code == 200
                final_state = response.json()
            else:
                final_state = candidate_details

            # Verify failure state
            assert final_state["status"] == "failed"
            assert final_state["final_result"] == "failed"
            assert final_state["failed_at"] is not None

            # Verify timeline shows failure
            response = await client.get(
                f"/api/recruitment-processes/candidate-processes/{candidate_process_id}/timeline",
                headers=auth_headers
            )
            timeline = response.json()

            failure_events = [
                item for item in timeline["timeline_items"]
                if item.get("result") == "fail" or item.get("event_type") == "process_failed"
            ]
            assert len(failure_events) >= 1

    @pytest.mark.asyncio
    async def test_recruitment_workflow_candidate_withdrawal(self, client, auth_headers):
        """Test scenario where candidate withdraws from process"""            # Setup basic process (abbreviated)
            process_data = {
                "name": "Withdrawal Test Process",
                "description": "Test candidate withdrawal"
            }

            response = await client.post(
                "/api/recruitment-processes/",
                json=process_data,
                headers=auth_headers
            )
            process_id = response.json()["id"]

            # Add node and activate (abbreviated setup)
            node_data = {
                "node_type": "interview",
                "title": "Initial Interview",
                "sequence_order": 1,
                "position": {"x": 100, "y": 100},
                "config": {"interview_type": "video", "duration_minutes": 30}
            }

            await client.post(
                f"/api/recruitment-processes/{process_id}/nodes",
                json=node_data,
                headers=auth_headers
            )

            await client.post(
                f"/api/recruitment-processes/{process_id}/activate",
                json={"force_activate": True},
                headers=auth_headers
            )

            # Assign and start candidate process
            assignment_data = {
                "candidate_id": 300,
                "assigned_recruiter_id": 50,
                "start_immediately": True
            }

            response = await client.post(
                f"/api/recruitment-processes/{process_id}/candidates",
                json=assignment_data,
                headers=auth_headers
            )
            candidate_process_id = response.json()["id"]

            # Candidate withdraws
            withdrawal_data = {
                "status": "withdrawn",
                "reason": "Accepted offer from another company"
            }

            response = await client.put(
                f"/api/recruitment-processes/candidate-processes/{candidate_process_id}/status",
                json=withdrawal_data,
                headers={"Authorization": "Bearer candidate_token"}  # Candidate can withdraw
            )
            assert response.status_code == 200

            final_state = response.json()
            assert final_state["status"] == "withdrawn"
            assert final_state["final_result"] == "withdrawn"
            assert final_state["withdrawn_at"] is not None

    @pytest.mark.asyncio
    async def test_bulk_candidate_assignment_and_processing(self, client, auth_headers):
        """Test bulk candidate assignment and parallel processing"""            # Setup process
            process_data = {
                "name": "Bulk Processing Test",
                "description": "Test bulk candidate handling"
            }

            response = await client.post(
                "/api/recruitment-processes/",
                json=process_data,
                headers=auth_headers
            )
            process_id = response.json()["id"]

            # Add simple node structure
            node_data = {
                "node_type": "interview",
                "title": "Screening Interview",
                "sequence_order": 1,
                "position": {"x": 100, "y": 100},
                "config": {"interview_type": "phone", "duration_minutes": 15}
            }

            await client.post(
                f"/api/recruitment-processes/{process_id}/nodes",
                json=node_data,
                headers=auth_headers
            )

            await client.post(
                f"/api/recruitment-processes/{process_id}/activate",
                json={"force_activate": True},
                headers=auth_headers
            )

            # Bulk assign multiple candidates
            bulk_assignment = {
                "candidate_ids": [400, 401, 402, 403, 404],
                "assigned_recruiter_id": 50,
                "start_immediately": True,
                "send_notifications": True
            }

            response = await client.post(
                f"/api/recruitment-processes/{process_id}/candidates/bulk",
                json=bulk_assignment,
                headers=auth_headers
            )
            assert response.status_code == 200

            candidate_processes = response.json()
            assert len(candidate_processes) == 5

            # Verify all were started
            for cp in candidate_processes:
                assert cp["status"] == "in_progress"
                assert cp["assigned_recruiter_id"] == 50
                assert cp["started_at"] is not None

            # Get recruiter workload
            response = await client.get(
                "/api/recruitment-processes/recruiters/50/workload",
                headers=auth_headers
            )
            assert response.status_code == 200

            workload = response.json()
            assert workload["active_processes"] >= 5
            assert workload["pending_tasks"] >= 5

    @pytest.mark.asyncio
    async def test_process_modification_with_active_candidates(self, client, auth_headers):
        """Test modifying process structure while candidates are active"""            # Create and activate process
            process_data = {
                "name": "Modification Test Process",
                "description": "Test process modification scenarios"
            }

            response = await client.post(
                "/api/recruitment-processes/",
                json=process_data,
                headers=auth_headers
            )
            process_id = response.json()["id"]

            # Add initial node
            initial_node = {
                "node_type": "interview",
                "title": "Initial Node",
                "sequence_order": 1,
                "position": {"x": 100, "y": 100},
                "config": {"interview_type": "video", "duration_minutes": 30}
            }

            response = await client.post(
                f"/api/recruitment-processes/{process_id}/nodes",
                json=initial_node,
                headers=auth_headers
            )
            initial_node_id = response.json()["id"]

            await client.post(
                f"/api/recruitment-processes/{process_id}/activate",
                json={"force_activate": True},
                headers=auth_headers
            )

            # Assign candidate
            assignment_data = {
                "candidate_id": 500,
                "assigned_recruiter_id": 50,
                "start_immediately": True
            }

            response = await client.post(
                f"/api/recruitment-processes/{process_id}/candidates",
                json=assignment_data,
                headers=auth_headers
            )
            candidate_process_id = response.json()["id"]

            # Try to modify active process (should require special handling)
            modification_data = {
                "name": "Modified Process Name"
            }

            response = await client.put(
                f"/api/recruitment-processes/{process_id}",
                json=modification_data,
                headers=auth_headers
            )
            # Should fail without force_update
            assert response.status_code == 409

            # Try to add new node to active process
            new_node = {
                "node_type": "todo",
                "title": "Additional Assignment",
                "sequence_order": 2,
                "position": {"x": 200, "y": 100},
                "config": {"todo_type": "assignment", "due_in_days": 2}
            }

            response = await client.post(
                f"/api/recruitment-processes/{process_id}/nodes",
                json=new_node,
                headers=auth_headers
            )
            # Should succeed - adding nodes to active process is allowed
            assert response.status_code == 201

            # Try to delete node with active executions
            response = await client.delete(
                f"/api/recruitment-processes/{process_id}/nodes/{initial_node_id}",
                headers=auth_headers
            )
            # Should fail - cannot delete node with executions
            assert response.status_code == 409

    @pytest.mark.asyncio
    async def test_complex_conditional_workflow(self, client, auth_headers):
        """Test workflow with conditional paths based on scores"""            # Create process with conditional paths
            process_data = {
                "name": "Conditional Workflow Test",
                "description": "Test conditional routing based on performance"
            }

            response = await client.post(
                "/api/recruitment-processes/",
                json=process_data,
                headers=auth_headers
            )
            process_id = response.json()["id"]

            # Create nodes
            nodes = [
                {
                    "node_type": "interview",
                    "title": "Initial Assessment",
                    "sequence_order": 1,
                    "position": {"x": 100, "y": 100},
                    "config": {"interview_type": "video", "duration_minutes": 45}
                },
                {
                    "node_type": "interview",
                    "title": "Advanced Technical Interview",
                    "sequence_order": 2,
                    "position": {"x": 200, "y": 50},
                    "config": {"interview_type": "video", "duration_minutes": 90}
                },
                {
                    "node_type": "interview",
                    "title": "Basic Technical Interview",
                    "sequence_order": 3,
                    "position": {"x": 200, "y": 150},
                    "config": {"interview_type": "video", "duration_minutes": 60}
                },
                {
                    "node_type": "decision",
                    "title": "Final Decision",
                    "sequence_order": 4,
                    "position": {"x": 300, "y": 100},
                    "config": {"decision_makers": [10], "require_unanimous": False}
                }
            ]

            created_nodes = []
            for node_data in nodes:
                response = await client.post(
                    f"/api/recruitment-processes/{process_id}/nodes",
                    json=node_data,
                    headers=auth_headers
                )
                created_nodes.append(response.json())

            # Create conditional connections
            connections = [
                {
                    "source_node_id": created_nodes[0]["id"],
                    "target_node_id": created_nodes[1]["id"],  # Advanced path
                    "condition_type": "conditional",
                    "condition_config": {"min_score": 80},
                    "label": "High Score Path"
                },
                {
                    "source_node_id": created_nodes[0]["id"],
                    "target_node_id": created_nodes[2]["id"],  # Basic path
                    "condition_type": "conditional",
                    "condition_config": {"min_score": 60},
                    "label": "Standard Score Path"
                },
                {
                    "source_node_id": created_nodes[1]["id"],
                    "target_node_id": created_nodes[3]["id"],  # To decision
                    "condition_type": "success"
                },
                {
                    "source_node_id": created_nodes[2]["id"],
                    "target_node_id": created_nodes[3]["id"],  # To decision
                    "condition_type": "success"
                }
            ]

            for connection_data in connections:
                response = await client.post(
                    f"/api/recruitment-processes/{process_id}/connections",
                    json=connection_data,
                    headers=auth_headers
                )
                assert response.status_code == 201

            await client.post(
                f"/api/recruitment-processes/{process_id}/activate",
                json={"force_activate": True},
                headers=auth_headers
            )

            # Test high-score candidate (should go to advanced path)
            high_score_assignment = {
                "candidate_id": 600,
                "assigned_recruiter_id": 50,
                "start_immediately": True
            }

            response = await client.post(
                f"/api/recruitment-processes/{process_id}/candidates",
                json=high_score_assignment,
                headers=auth_headers
            )
            high_score_process_id = response.json()["id"]

            # Complete initial assessment with high score
            response = await client.get(
                f"/api/recruitment-processes/candidate-processes/{high_score_process_id}",
                headers={"Authorization": "Bearer recruiter_token"}
            )
            candidate_details = response.json()

            initial_execution = next(
                (exec for exec in candidate_details["executions"]
                 if exec["node"]["title"] == "Initial Assessment"), None
            )

            await client.post(
                f"/api/recruitment-processes/executions/{initial_execution['id']}/complete",
                json={
                    "result": "pass",
                    "score": 85.0,  # High score
                    "feedback": "Excellent performance"
                },
                headers={"Authorization": "Bearer recruiter_token"}
            )

            # Verify candidate advanced to advanced technical interview
            response = await client.get(
                f"/api/recruitment-processes/candidate-processes/{high_score_process_id}",
                headers={"Authorization": "Bearer recruiter_token"}
            )
            updated_details = response.json()

            advanced_execution = next(
                (exec for exec in updated_details["executions"]
                 if exec["node"]["title"] == "Advanced Technical Interview"), None
            )
            basic_execution = next(
                (exec for exec in updated_details["executions"]
                 if exec["node"]["title"] == "Basic Technical Interview"), None
            )

            # Should have advanced execution, not basic
            assert advanced_execution is not None
            assert basic_execution is None or basic_execution["status"] == "pending"

            print("✅ All recruitment workflow scenario tests completed successfully!")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])