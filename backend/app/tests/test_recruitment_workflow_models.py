from datetime import datetime, timedelta

import pytest

from app.models.candidate_process import CandidateProcess
from app.models.node_connection import NodeConnection
from app.models.node_execution import NodeExecution
from app.models.process_node import ProcessNode
from app.models.process_viewer import ProcessViewer
from app.models.recruitment_process import RecruitmentProcess


class TestRecruitmentProcess:
    """Test recruitment process model"""

    def test_create_recruitment_process(self):
        """Test creating a recruitment process"""
        process = RecruitmentProcess(
            name="Software Engineer Process",
            description="Technical interview process",
            employer_company_id=1,
            created_by=1
        )

        assert process.name == "Software Engineer Process"
        assert process.description == "Technical interview process"
        assert process.status == "draft"
        assert process.version == 1
        assert process.is_draft
        assert not process.is_active
        assert process.can_be_edited

    def test_activate_process(self):
        """Test activating a process"""
        process = RecruitmentProcess(
            name="Test Process",
            employer_company_id=1,
            created_by=1
        )

        process.activate(activated_by=1)

        assert process.status == "active"
        assert process.is_active
        assert not process.is_draft
        assert not process.can_be_edited
        assert process.activated_at is not None

    def test_archive_process(self):
        """Test archiving a process"""
        process = RecruitmentProcess(
            name="Test Process",
            employer_company_id=1,
            created_by=1
        )

        process.archive(archived_by=1)

        assert process.status == "archived"
        assert process.archived_at is not None

    def test_activate_non_draft_process_fails(self):
        """Test that only draft processes can be activated"""
        process = RecruitmentProcess(
            name="Test Process",
            employer_company_id=1,
            created_by=1,
            status="active"
        )

        with pytest.raises(ValueError, match="Only draft processes can be activated"):
            process.activate(activated_by=1)


class TestProcessNode:
    """Test process node model"""

    def test_create_process_node(self):
        """Test creating a process node"""
        node = ProcessNode(
            process_id=1,
            node_type="interview",
            title="Technical Interview",
            description="Coding interview with senior engineer",
            sequence_order=1,
            created_by=1
        )

        assert node.node_type == "interview"
        assert node.title == "Technical Interview"
        assert node.sequence_order == 1
        assert node.status == "draft"
        assert node.is_required
        assert not node.can_skip
        assert not node.auto_advance

    def test_activate_node(self):
        """Test activating a node"""
        node = ProcessNode(
            process_id=1,
            node_type="interview",
            title="Interview",
            sequence_order=1,
            created_by=1
        )

        node.activate(updated_by=2)

        assert node.status == "active"
        assert node.is_active
        assert node.updated_by == 2

    def test_node_can_be_deleted_when_no_executions(self):
        """Test node deletion check"""
        node = ProcessNode(
            process_id=1,
            node_type="interview",
            title="Interview",
            sequence_order=1,
            created_by=1
        )

        assert node.can_be_deleted()

    def test_node_properties(self):
        """Test node computed properties"""
        # Start node (sequence_order = 1)
        start_node = ProcessNode(
            process_id=1,
            node_type="interview",
            title="Start Interview",
            sequence_order=1,
            created_by=1
        )

        assert start_node.is_start_node

        # Regular node
        regular_node = ProcessNode(
            process_id=1,
            node_type="todo",
            title="Assignment",
            sequence_order=2,
            created_by=1
        )

        assert not regular_node.is_start_node


class TestCandidateProcess:
    """Test candidate process model"""

    def test_create_candidate_process(self):
        """Test creating a candidate process"""
        candidate_process = CandidateProcess(
            candidate_id=100,
            process_id=1
        )

        assert candidate_process.candidate_id == 100
        assert candidate_process.process_id == 1
        assert candidate_process.status == "not_started"
        assert not candidate_process.is_active
        assert not candidate_process.is_completed

    def test_start_candidate_process(self):
        """Test starting a candidate process"""
        candidate_process = CandidateProcess(
            candidate_id=100,
            process_id=1
        )

        candidate_process.start(first_node_id=10)

        assert candidate_process.status == "in_progress"
        assert candidate_process.current_node_id == 10
        assert candidate_process.is_active
        assert candidate_process.started_at is not None

    def test_complete_candidate_process(self):
        """Test completing a candidate process"""
        candidate_process = CandidateProcess(
            candidate_id=100,
            process_id=1,
            status="in_progress"
        )

        candidate_process.complete(
            final_result="hired",
            overall_score=85.5,
            notes="Excellent candidate"
        )

        assert candidate_process.status == "completed"
        assert candidate_process.is_completed
        assert candidate_process.final_result == "hired"
        assert candidate_process.overall_score == 85.5
        assert candidate_process.notes == "Excellent candidate"
        assert candidate_process.completed_at is not None
        assert candidate_process.current_node_id is None

    def test_fail_candidate_process(self):
        """Test failing a candidate process"""
        candidate_process = CandidateProcess(
            candidate_id=100,
            process_id=1,
            status="in_progress",
            current_node_id=5
        )

        candidate_process.fail(reason="Failed technical interview", failed_at_node_id=5)

        assert candidate_process.status == "failed"
        assert candidate_process.is_failed
        assert candidate_process.final_result == "failed"
        assert candidate_process.notes == "Failed technical interview"
        assert candidate_process.failed_at is not None
        assert candidate_process.current_node_id == 5

    def test_withdraw_candidate_process(self):
        """Test withdrawing from a process"""
        candidate_process = CandidateProcess(
            candidate_id=100,
            process_id=1,
            status="in_progress"
        )

        candidate_process.withdraw(reason="Accepted another offer")

        assert candidate_process.status == "withdrawn"
        assert candidate_process.is_withdrawn
        assert candidate_process.final_result == "withdrawn"
        assert candidate_process.notes == "Accepted another offer"
        assert candidate_process.withdrawn_at is not None
        assert candidate_process.current_node_id is None

    def test_put_on_hold_and_resume(self):
        """Test putting process on hold and resuming"""
        candidate_process = CandidateProcess(
            candidate_id=100,
            process_id=1,
            status="in_progress"
        )

        # Put on hold
        candidate_process.put_on_hold()
        assert candidate_process.status == "on_hold"

        # Resume
        candidate_process.resume()
        assert candidate_process.status == "in_progress"
        assert candidate_process.is_active

    def test_assign_recruiter(self):
        """Test assigning a recruiter"""
        candidate_process = CandidateProcess(
            candidate_id=100,
            process_id=1
        )

        candidate_process.assign_recruiter(recruiter_id=50)

        assert candidate_process.assigned_recruiter_id == 50
        assert candidate_process.assigned_at is not None

    def test_advance_to_node(self):
        """Test advancing to next node"""
        candidate_process = CandidateProcess(
            candidate_id=100,
            process_id=1,
            current_node_id=1
        )

        candidate_process.advance_to_node(next_node_id=2)

        assert candidate_process.current_node_id == 2

    def test_progress_percentage_calculation(self):
        """Test progress percentage calculation"""
        candidate_process = CandidateProcess(
            candidate_id=100,
            process_id=1
        )

        # This would require executions relationship to work properly
        # For now, test that the property exists and returns a number
        progress = candidate_process.progress_percentage
        assert isinstance(progress, float)
        assert 0 <= progress <= 100

    def test_start_already_started_process_fails(self):
        """Test that starting an already started process fails"""
        candidate_process = CandidateProcess(
            candidate_id=100,
            process_id=1,
            status="in_progress"
        )

        with pytest.raises(ValueError, match="Process has already been started"):
            candidate_process.start(first_node_id=1)

    def test_put_on_hold_non_active_process_fails(self):
        """Test that only in-progress processes can be put on hold"""
        candidate_process = CandidateProcess(
            candidate_id=100,
            process_id=1,
            status="completed"
        )

        with pytest.raises(ValueError, match="Only in-progress processes can be put on hold"):
            candidate_process.put_on_hold()

    def test_resume_non_hold_process_fails(self):
        """Test that only processes on hold can be resumed"""
        candidate_process = CandidateProcess(
            candidate_id=100,
            process_id=1,
            status="in_progress"
        )

        with pytest.raises(ValueError, match="Only processes on hold can be resumed"):
            candidate_process.resume()


class TestNodeExecution:
    """Test node execution model"""

    def test_create_node_execution(self):
        """Test creating a node execution"""
        execution = NodeExecution(
            candidate_process_id=1,
            node_id=10
        )

        assert execution.candidate_process_id == 1
        assert execution.node_id == 10
        assert execution.status == "pending"
        assert execution.is_pending
        assert not execution.is_completed
        assert not execution.is_failed

    def test_start_execution(self):
        """Test starting an execution"""
        execution = NodeExecution(
            candidate_process_id=1,
            node_id=10,
            status="pending"
        )

        execution.start(assigned_to=50)

        assert execution.status == "in_progress"
        assert execution.is_in_progress
        assert execution.assigned_to == 50
        assert execution.started_at is not None

    def test_complete_execution(self):
        """Test completing an execution"""
        execution = NodeExecution(
            candidate_process_id=1,
            node_id=10,
            status="in_progress"
        )
        execution.started_at = datetime.utcnow()

        execution.complete(
            result="pass",
            completed_by=25,
            score=90.0,
            feedback="Great performance",
            execution_data={"details": "test"}
        )

        assert execution.status == "completed"
        assert execution.is_completed
        assert execution.result == "pass"
        assert execution.score == 90.0
        assert execution.feedback == "Great performance"
        assert execution.completed_by == 25
        assert execution.execution_data == {"details": "test"}
        assert execution.completed_at is not None

    def test_fail_execution(self):
        """Test failing an execution"""
        execution = NodeExecution(
            candidate_process_id=1,
            node_id=10,
            status="in_progress"
        )

        execution.fail(completed_by=25, reason="Did not meet requirements")

        assert execution.status == "failed"
        assert execution.is_failed
        assert execution.result == "fail"
        assert execution.completed_by == 25
        assert execution.feedback == "Did not meet requirements"
        assert execution.completed_at is not None

    def test_skip_execution(self):
        """Test skipping an execution"""
        execution = NodeExecution(
            candidate_process_id=1,
            node_id=10,
            status="pending"
        )

        execution.skip(completed_by=25, reason="Node no longer required")

        assert execution.status == "skipped"
        assert execution.result == "skipped"
        assert execution.completed_by == 25
        assert execution.feedback == "Node no longer required"
        assert execution.completed_at is not None

    def test_schedule_execution(self):
        """Test scheduling an execution"""
        execution = NodeExecution(
            candidate_process_id=1,
            node_id=10,
            status="pending"
        )

        due_date = datetime.utcnow() + timedelta(days=2)
        execution.schedule(due_date=due_date)

        assert execution.status == "scheduled"
        assert execution.due_date == due_date

    def test_await_input(self):
        """Test marking execution as awaiting input"""
        execution = NodeExecution(
            candidate_process_id=1,
            node_id=10,
            status="in_progress"
        )

        execution.await_input()

        assert execution.status == "awaiting_input"

    def test_link_interview(self):
        """Test linking an interview to execution"""
        execution = NodeExecution(
            candidate_process_id=1,
            node_id=10
        )

        execution.link_interview(interview_id=100)

        assert execution.interview_id == 100

    def test_link_todo(self):
        """Test linking a todo to execution"""
        execution = NodeExecution(
            candidate_process_id=1,
            node_id=10
        )

        execution.link_todo(todo_id=200)

        assert execution.todo_id == 200

    def test_add_review(self):
        """Test adding reviewer notes"""
        execution = NodeExecution(
            candidate_process_id=1,
            node_id=10
        )

        execution.add_review(reviewer_id=30, notes="Good technical skills")

        assert execution.reviewed_by == 30
        assert execution.assessor_notes == "Good technical skills"

    def test_duration_calculation(self):
        """Test execution duration calculation"""
        execution = NodeExecution(
            candidate_process_id=1,
            node_id=10
        )

        start_time = datetime.utcnow()
        end_time = start_time + timedelta(minutes=45)

        execution.started_at = start_time
        execution.completed_at = end_time

        assert execution.duration_minutes == 45

    def test_is_overdue(self):
        """Test overdue check"""
        execution = NodeExecution(
            candidate_process_id=1,
            node_id=10,
            status="in_progress",
            due_date=datetime.utcnow() - timedelta(hours=1)
        )

        assert execution.is_overdue

        # Completed executions should not be overdue
        execution.status = "completed"
        assert not execution.is_overdue

    def test_invalid_state_transitions(self):
        """Test invalid state transitions"""
        # Cannot start completed execution
        execution = NodeExecution(
            candidate_process_id=1,
            node_id=10,
            status="completed"
        )

        with pytest.raises(ValueError):
            execution.start()

        # Cannot complete pending execution
        execution2 = NodeExecution(
            candidate_process_id=1,
            node_id=10,
            status="pending"
        )

        with pytest.raises(ValueError):
            execution2.complete(result="pass", completed_by=1)

        # Cannot await input from non-progress state
        execution3 = NodeExecution(
            candidate_process_id=1,
            node_id=10,
            status="pending"
        )

        with pytest.raises(ValueError):
            execution3.await_input()

        # Cannot schedule non-pending execution
        execution4 = NodeExecution(
            candidate_process_id=1,
            node_id=10,
            status="completed"
        )

        with pytest.raises(ValueError):
            execution4.schedule()


class TestProcessViewer:
    """Test process viewer model"""

    def test_create_process_viewer(self):
        """Test creating a process viewer"""
        viewer = ProcessViewer(
            process_id=1,
            user_id=50,
            role="recruiter",
            added_by=10
        )

        assert viewer.process_id == 1
        assert viewer.user_id == 50
        assert viewer.role == "recruiter"
        assert viewer.is_recruiter
        assert not viewer.is_observer
        assert not viewer.is_admin
        assert viewer.added_by == 10

    def test_viewer_permissions(self):
        """Test viewer permission checks"""
        # Recruiter
        recruiter = ProcessViewer(
            process_id=1,
            user_id=50,
            role="recruiter",
            added_by=10
        )

        assert recruiter.can_execute
        assert recruiter.can_view_all_candidates
        assert recruiter.can_schedule_interviews
        assert recruiter.can_record_results

        # Observer
        observer = ProcessViewer(
            process_id=1,
            user_id=51,
            role="observer",
            added_by=10
        )

        assert not observer.can_execute
        assert observer.can_view_all_candidates
        assert not observer.can_schedule_interviews
        assert not observer.can_record_results

        # Admin
        admin = ProcessViewer(
            process_id=1,
            user_id=52,
            role="admin",
            added_by=10
        )

        assert admin.can_execute
        assert admin.can_view_all_candidates
        assert admin.can_schedule_interviews
        assert admin.can_record_results

    def test_has_permission_with_defaults(self):
        """Test permission checking with role defaults"""
        recruiter = ProcessViewer(
            process_id=1,
            user_id=50,
            role="recruiter",
            added_by=10
        )

        assert recruiter.has_permission("view_process")
        assert recruiter.has_permission("execute_nodes")
        assert recruiter.has_permission("schedule_interviews")
        assert not recruiter.has_permission("override_results")  # Admin only

    def test_has_permission_with_custom_permissions(self):
        """Test permission checking with custom permissions"""
        viewer = ProcessViewer(
            process_id=1,
            user_id=50,
            role="observer",
            added_by=10,
            permissions={
                "view_process": True,
                "execute_nodes": True,  # Custom permission for observer
                "override_results": False
            }
        )

        assert viewer.has_permission("view_process")
        assert viewer.has_permission("execute_nodes")  # Custom granted
        assert not viewer.has_permission("override_results")

    def test_grant_and_revoke_permissions(self):
        """Test granting and revoking permissions"""
        viewer = ProcessViewer(
            process_id=1,
            user_id=50,
            role="observer",
            added_by=10
        )

        # Grant permission
        viewer.grant_permission("execute_nodes")
        assert viewer.has_permission("execute_nodes")
        assert viewer.permissions["execute_nodes"] is True

        # Revoke permission
        viewer.revoke_permission("execute_nodes")
        assert not viewer.has_permission("execute_nodes")
        assert viewer.permissions["execute_nodes"] is False


class TestNodeConnection:
    """Test node connection model"""

    def test_create_node_connection(self):
        """Test creating a node connection"""
        connection = NodeConnection(
            process_id=1,
            source_node_id=10,
            target_node_id=20,
            condition_type="success"
        )

        assert connection.process_id == 1
        assert connection.source_node_id == 10
        assert connection.target_node_id == 20
        assert connection.condition_type == "success"
        assert connection.is_success_path
        assert not connection.is_failure_path
        assert not connection.is_conditional

    def test_evaluate_condition_success(self):
        """Test evaluating success conditions"""
        connection = NodeConnection(
            process_id=1,
            source_node_id=10,
            target_node_id=20,
            condition_type="success"
        )

        assert connection.evaluate_condition("pass")
        assert connection.evaluate_condition("completed")
        assert connection.evaluate_condition("approved")
        assert not connection.evaluate_condition("fail")
        assert not connection.evaluate_condition("rejected")

    def test_evaluate_condition_failure(self):
        """Test evaluating failure conditions"""
        connection = NodeConnection(
            process_id=1,
            source_node_id=10,
            target_node_id=20,
            condition_type="failure"
        )

        assert connection.evaluate_condition("fail")
        assert connection.evaluate_condition("failed")
        assert connection.evaluate_condition("rejected")
        assert not connection.evaluate_condition("pass")
        assert not connection.evaluate_condition("approved")

    def test_evaluate_condition_always(self):
        """Test evaluating always conditions"""
        connection = NodeConnection(
            process_id=1,
            source_node_id=10,
            target_node_id=20,
            condition_type="always"
        )

        assert connection.evaluate_condition("pass")
        assert connection.evaluate_condition("fail")
        assert connection.evaluate_condition("any_result")

    def test_evaluate_condition_conditional_with_result(self):
        """Test evaluating conditional with required result"""
        connection = NodeConnection(
            process_id=1,
            source_node_id=10,
            target_node_id=20,
            condition_type="conditional",
            condition_config={"required_result": "excellent"}
        )

        assert connection.evaluate_condition("excellent")
        assert not connection.evaluate_condition("good")
        assert not connection.evaluate_condition("pass")

    def test_evaluate_condition_conditional_with_score(self):
        """Test evaluating conditional with minimum score"""
        connection = NodeConnection(
            process_id=1,
            source_node_id=10,
            target_node_id=20,
            condition_type="conditional",
            condition_config={"min_score": 80}
        )

        assert connection.evaluate_condition("pass", {"score": 85})
        assert connection.evaluate_condition("pass", {"score": 80})
        assert not connection.evaluate_condition("pass", {"score": 75})
        assert not connection.evaluate_condition("pass", {"score": None})
        assert not connection.evaluate_condition("pass", {})

    def test_evaluate_condition_conditional_no_config(self):
        """Test evaluating conditional with no config returns False"""
        connection = NodeConnection(
            process_id=1,
            source_node_id=10,
            target_node_id=20,
            condition_type="conditional"
        )

        assert not connection.evaluate_condition("pass")
        assert not connection.evaluate_condition("fail")


if __name__ == "__main__":
    pytest.main([__file__])
