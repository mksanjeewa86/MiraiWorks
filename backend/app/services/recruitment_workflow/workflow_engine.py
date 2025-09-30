from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.recruitment_workflow.recruitment_process import recruitment_process
from app.crud.recruitment_workflow.process_node import process_node
from app.crud.recruitment_workflow.candidate_process import candidate_process
from app.crud.recruitment_workflow.node_execution import node_execution
from app.crud.recruitment_workflow.node_connection import node_connection
from app.crud.recruitment_workflow.process_viewer import process_viewer
from app.crud.interview import interview as interview_crud
from app.crud.todo import todo as todo_crud
from app.models.recruitment_process import RecruitmentProcess
from app.models.process_node import ProcessNode
from app.models.candidate_process import CandidateProcess
from app.models.node_execution import NodeExecution
from app.schemas.recruitment_workflow.enums import NodeType, InterviewNodeType, TodoNodeType


class WorkflowEngineService:
    """Core service for managing recruitment workflow execution"""

    async def create_process_from_template(
        self,
        db: AsyncSession,
        template_id: int,
        employer_id: int,
        process_data: Dict[str, Any]
    ) -> RecruitmentProcess:
        """Create a new process from a template"""
        template = await recruitment_process.get(db, id=template_id)
        if not template or not template.is_template:
            raise ValueError("Template not found or not a valid template")

        # Clone the template
        cloned_process = await recruitment_process.clone(
            db,
            source_process=template,
            new_name=process_data["name"],
            created_by=employer_id,
            clone_nodes=True,
            clone_viewers=process_data.get("clone_viewers", True)
        )

        return cloned_process

    async def activate_process(
        self,
        db: AsyncSession,
        process_id: int,
        user_id: int
    ) -> RecruitmentProcess:
        """Activate a draft process after validation"""
        process = await recruitment_process.get(db, id=process_id)
        if not process:
            raise ValueError("Process not found")

        # Validate process before activation
        validation_result = await self.validate_process(db, process_id)
        if not validation_result["is_valid"]:
            raise ValueError(f"Process validation failed: {validation_result['issues']}")

        # Activate all nodes
        nodes = await process_node.get_by_process_id(db, process_id=process_id)
        for node in nodes:
            if node.status == "draft":
                await process_node.activate_node(db, db_obj=node, updated_by=user_id)

        # Activate the process
        activated_process = await recruitment_process.activate(
            db, db_obj=process, activated_by=user_id
        )

        return activated_process

    async def assign_candidate(
        self,
        db: AsyncSession,
        process_id: int,
        candidate_id: int,
        recruiter_id: Optional[int] = None,
        start_immediately: bool = False
    ) -> CandidateProcess:
        """Assign a candidate to a process"""
        process = await recruitment_process.get(db, id=process_id)
        if not process:
            raise ValueError("Process not found")

        if process.status != "active":
            raise ValueError("Cannot assign candidates to inactive processes")

        # Check if candidate is already assigned
        existing = await candidate_process.get_by_candidate_and_process(
            db, candidate_id=candidate_id, process_id=process_id
        )
        if existing:
            raise ValueError("Candidate is already assigned to this process")

        # Create candidate process
        candidate_process_data = {
            "candidate_id": candidate_id,
            "process_id": process_id,
            "assigned_recruiter_id": recruiter_id,
            "assigned_at": datetime.utcnow() if recruiter_id else None
        }

        candidate_proc = await candidate_process.create(db, obj_in=candidate_process_data)

        # Start immediately if requested
        if start_immediately:
            candidate_proc = await self.start_candidate_process(db, candidate_proc.id)

        return candidate_proc

    async def start_candidate_process(
        self,
        db: AsyncSession,
        candidate_process_id: int
    ) -> CandidateProcess:
        """Start the first node for a candidate"""
        candidate_proc = await candidate_process.get(db, id=candidate_process_id)
        if not candidate_proc:
            raise ValueError("Candidate process not found")

        if candidate_proc.status != "not_started":
            raise ValueError("Process has already been started")

        # Find the first node
        start_nodes = await process_node.get_start_nodes(db, process_id=candidate_proc.process_id)
        if not start_nodes:
            raise ValueError("No start node found for this process")

        first_node = start_nodes[0]  # Use the first start node

        # Start the process
        candidate_proc = await candidate_process.start_process(
            db, candidate_process=candidate_proc, first_node_id=first_node.id
        )

        # Create the first node execution
        await self.create_node_execution(
            db, candidate_process_id=candidate_proc.id, node_id=first_node.id
        )

        return candidate_proc

    async def create_node_execution(
        self,
        db: AsyncSession,
        candidate_process_id: int,
        node_id: int,
        assigned_to: Optional[int] = None
    ) -> NodeExecution:
        """Create a new node execution"""
        # Get the node to determine configuration
        node = await process_node.get(db, id=node_id)
        if not node:
            raise ValueError("Node not found")

        # Calculate due date based on node configuration
        due_date = None
        if node.estimated_duration_minutes:
            due_date = datetime.utcnow() + timedelta(minutes=node.estimated_duration_minutes)

        execution_data = {
            "candidate_process_id": candidate_process_id,
            "node_id": node_id,
            "assigned_to": assigned_to,
            "due_date": due_date
        }

        execution = await node_execution.create(db, obj_in=execution_data)

        # Create linked resources based on node type
        if node.node_type == NodeType.INTERVIEW:
            await self._create_interview_for_execution(db, execution, node)
        elif node.node_type == NodeType.TODO:
            await self._create_todo_for_execution(db, execution, node)

        return execution

    async def complete_node_execution(
        self,
        db: AsyncSession,
        execution_id: int,
        result: str,
        completed_by: int,
        score: Optional[float] = None,
        feedback: Optional[str] = None,
        execution_data: Optional[Dict[str, Any]] = None
    ) -> Optional[NodeExecution]:
        """Complete a node and advance to next"""
        execution = await node_execution.get(db, id=execution_id)
        if not execution:
            raise ValueError("Execution not found")

        # Complete the execution
        completed_execution = await node_execution.complete_execution(
            db,
            execution=execution,
            result=result,
            completed_by=completed_by,
            score=score,
            feedback=feedback,
            execution_data=execution_data
        )

        # Advance to next node(s)
        await self.advance_to_next_node(
            db, completed_execution.candidate_process_id, completed_execution.node_id, result, execution_data
        )

        return completed_execution

    async def advance_to_next_node(
        self,
        db: AsyncSession,
        candidate_process_id: int,
        current_node_id: int,
        execution_result: str,
        execution_data: Optional[Dict[str, Any]] = None
    ) -> List[NodeExecution]:
        """Advance candidate to the next node(s)"""
        # Get next nodes based on execution result
        next_nodes = await process_node.get_next_nodes(
            db, node_id=current_node_id, execution_result=execution_result, execution_data=execution_data
        )

        new_executions = []

        if not next_nodes:
            # No next nodes - complete the process
            await self._complete_candidate_process(db, candidate_process_id, execution_result)
        else:
            # Update current node in candidate process
            candidate_proc = await candidate_process.get(db, id=candidate_process_id)
            if candidate_proc:
                # If multiple next nodes, use the first one as current
                await candidate_process.advance_to_node(
                    db, candidate_process=candidate_proc, next_node_id=next_nodes[0].id
                )

                # Create executions for all next nodes
                for next_node in next_nodes:
                    execution = await self.create_node_execution(
                        db, candidate_process_id=candidate_process_id, node_id=next_node.id
                    )
                    new_executions.append(execution)

        return new_executions

    async def _complete_candidate_process(
        self,
        db: AsyncSession,
        candidate_process_id: int,
        final_result: str
    ) -> CandidateProcess:
        """Complete a candidate process"""
        candidate_proc = await candidate_process.get_with_details(db, id=candidate_process_id)
        if not candidate_proc:
            raise ValueError("Candidate process not found")

        # Calculate overall score from executions
        total_score = 0
        scored_executions = 0

        for execution in candidate_proc.executions:
            if execution.score is not None:
                total_score += execution.score
                scored_executions += 1

        overall_score = total_score / scored_executions if scored_executions > 0 else None

        # Determine final result based on execution results
        if final_result in ["pass", "approved"]:
            final_result = "hired"
        elif final_result in ["fail", "rejected"]:
            final_result = "rejected"

        completed_process = await candidate_process.complete_process(
            db,
            candidate_process=candidate_proc,
            final_result=final_result,
            overall_score=overall_score
        )

        return completed_process

    async def _create_interview_for_execution(
        self,
        db: AsyncSession,
        execution: NodeExecution,
        node: ProcessNode
    ) -> None:
        """Create an interview for an interview node execution"""
        # Get candidate process details
        candidate_proc = await candidate_process.get_with_details(db, id=execution.candidate_process_id)
        if not candidate_proc:
            return

        config = node.config or {}

        interview_data = {
            "candidate_id": candidate_proc.candidate_id,
            "recruiter_id": candidate_proc.assigned_recruiter_id or execution.assigned_to,
            "employer_company_id": candidate_proc.process.employer_company_id,
            "recruiter_company_id": candidate_proc.process.employer_company_id,  # Same as employer for now
            "title": f"{node.title} - {candidate_proc.candidate.name if candidate_proc.candidate else 'Candidate'}",
            "description": node.description,
            "interview_type": config.get("interview_type", InterviewNodeType.VIDEO),
            "duration_minutes": config.get("duration_minutes", 60),
            "preparation_notes": node.instructions,
            "created_by": execution.assigned_to or candidate_proc.assigned_recruiter_id
        }

        # Create the interview
        interview = await interview_crud.create(db, obj_in=interview_data)

        # Link to execution
        await node_execution.link_interview(db, execution=execution, interview_id=interview.id)

    async def _create_todo_for_execution(
        self,
        db: AsyncSession,
        execution: NodeExecution,
        node: ProcessNode
    ) -> None:
        """Create a todo for a todo node execution"""
        # Get candidate process details
        candidate_proc = await candidate_process.get_with_details(db, id=execution.candidate_process_id)
        if not candidate_proc:
            return

        config = node.config or {}

        # Calculate due date
        due_days = config.get("due_in_days", 3)
        due_date = datetime.utcnow() + timedelta(days=due_days)

        todo_data = {
            "owner_id": candidate_proc.assigned_recruiter_id or execution.assigned_to,
            "assigned_user_id": candidate_proc.candidate_id,
            "created_by": execution.assigned_to or candidate_proc.assigned_recruiter_id,
            "title": node.title,
            "description": node.description,
            "notes": node.instructions,
            "todo_type": "assignment" if config.get("todo_type") == TodoNodeType.ASSIGNMENT else "regular",
            "due_date": due_date,
            "visibility": "shared"  # Visible to both recruiter and candidate
        }

        # Create the todo
        todo = await todo_crud.create(db, obj_in=todo_data)

        # Link to execution
        await node_execution.link_todo(db, execution=execution, todo_id=todo.id)

    async def validate_process(
        self,
        db: AsyncSession,
        process_id: int
    ) -> Dict[str, Any]:
        """Validate a process before activation"""
        # Get process nodes
        nodes = await process_node.get_by_process_id(db, process_id=process_id, include_inactive=False)

        issues = []
        warnings = []

        # Check minimum requirements
        if len(nodes) == 0:
            issues.append("Process must have at least one node")

        # Check for required node types
        node_types = {node.node_type for node in nodes}

        # Every process should have at least one decision point (interview or assessment)
        if not any(nt in node_types for nt in [NodeType.INTERVIEW, NodeType.ASSESSMENT]):
            warnings.append("Process should have at least one interview or assessment")

        # Validate node connections
        flow_validation = await node_connection.validate_process_flow(db, process_id=process_id)
        issues.extend([issue["message"] for issue in flow_validation.get("issues", [])])
        warnings.extend([warning["message"] for warning in flow_validation.get("warnings", [])])

        # Check node configurations
        for node in nodes:
            node_issues = self._validate_node_config(node)
            issues.extend(node_issues)

        return {
            "is_valid": len(issues) == 0,
            "issues": issues,
            "warnings": warnings,
            "total_nodes": len(nodes),
            "node_types": list(node_types)
        }

    def _validate_node_config(self, node: ProcessNode) -> List[str]:
        """Validate individual node configuration"""
        issues = []

        if not node.title or not node.title.strip():
            issues.append(f"Node {node.id} must have a title")

        if node.node_type == NodeType.INTERVIEW:
            config = node.config or {}
            if not config.get("interview_type"):
                issues.append(f"Interview node {node.id} must specify interview type")

            duration = config.get("duration_minutes")
            if not duration or duration < 15 or duration > 480:
                issues.append(f"Interview node {node.id} duration must be between 15-480 minutes")

        elif node.node_type == NodeType.TODO:
            config = node.config or {}
            due_days = config.get("due_in_days")
            if not due_days or due_days < 1 or due_days > 30:
                issues.append(f"Todo node {node.id} due_in_days must be between 1-30 days")

        elif node.node_type == NodeType.DECISION:
            config = node.config or {}
            decision_makers = config.get("decision_makers", [])
            if not decision_makers:
                issues.append(f"Decision node {node.id} must have at least one decision maker")

        return issues

    async def get_candidate_timeline(
        self,
        db: AsyncSession,
        candidate_process_id: int
    ) -> List[Dict[str, Any]]:
        """Get detailed timeline for a candidate process"""
        return await candidate_process.get_timeline(db, candidate_process_id=candidate_process_id)

    async def get_process_analytics(
        self,
        db: AsyncSession,
        process_id: int
    ) -> Dict[str, Any]:
        """Get comprehensive analytics for a process"""
        # Basic statistics
        stats = await candidate_process.get_statistics_by_process(db, process_id=process_id)

        # Node statistics
        nodes = await process_node.get_by_process_id(db, process_id=process_id)
        node_stats = []

        for node in nodes:
            node_stat = await process_node.get_node_statistics(db, node_id=node.id)
            node_stat["node_title"] = node.title
            node_stat["node_type"] = node.node_type
            node_stats.append(node_stat)

        # Bottleneck analysis
        bottlenecks = await process_node.get_bottleneck_nodes(db, process_id=process_id)

        # Execution workload
        workload = await node_execution.get_workload_by_assignee(db, process_id=process_id)

        return {
            **stats,
            "node_statistics": node_stats,
            "bottleneck_nodes": bottlenecks,
            "recruiter_workload": workload
        }

    async def bulk_assign_candidates(
        self,
        db: AsyncSession,
        process_id: int,
        candidate_ids: List[int],
        assigned_recruiter_id: Optional[int] = None,
        start_immediately: bool = False
    ) -> List[CandidateProcess]:
        """Bulk assign multiple candidates to a process"""
        assigned_processes = await candidate_process.bulk_assign_candidates(
            db,
            process_id=process_id,
            candidate_ids=candidate_ids,
            assigned_recruiter_id=assigned_recruiter_id
        )

        if start_immediately:
            for candidate_proc in assigned_processes:
                await self.start_candidate_process(db, candidate_proc.id)

        return assigned_processes

    async def clone_process(
        self,
        db: AsyncSession,
        source_process_id: int,
        new_name: str,
        created_by: int,
        clone_candidates: bool = False,
        clone_viewers: bool = True
    ) -> RecruitmentProcess:
        """Clone an existing process"""
        source_process = await recruitment_process.get_with_nodes(db, id=source_process_id)
        if not source_process:
            raise ValueError("Source process not found")

        cloned_process = await recruitment_process.clone(
            db,
            source_process=source_process,
            new_name=new_name,
            created_by=created_by,
            clone_nodes=True,
            clone_viewers=clone_viewers
        )

        # Clone candidate assignments if requested
        if clone_candidates:
            source_candidates = await candidate_process.get_by_process_id(
                db, process_id=source_process_id
            )

            candidate_ids = [cp.candidate_id for cp in source_candidates]
            if candidate_ids:
                await self.bulk_assign_candidates(
                    db, cloned_process.id, candidate_ids
                )

        return cloned_process


workflow_engine = WorkflowEngineService()