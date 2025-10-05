from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.endpoints import API_ROUTES
from app.crud.workflow.candidate_workflow import candidate_workflow
from app.crud.workflow.workflow import workflow
from app.crud.workflow.workflow_viewer import workflow_viewer
from app.database import get_db
from app.dependencies import get_current_active_user
from app.models.user import User
from app.schemas.workflow.candidate_workflow import (
    BulkCandidateAssignment,
    CandidateTimeline,
    CandidateWorkflowCreate,
    CandidateWorkflowDetails,
    CandidateWorkflowInfo,
    CandidateWorkflowStart,
    CandidateWorkflowStatusChange,
    RecruiterWorkload,
)
from app.services.workflow.workflow_engine import workflow_engine

router = APIRouter()


@router.post(
    API_ROUTES.WORKFLOWS.CANDIDATES,
    response_model=CandidateWorkflowInfo,
    status_code=status.HTTP_201_CREATED,
)
async def assign_candidate_to_workflow(
    workflow_id: int,
    assignment: CandidateWorkflowCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Assign a candidate to a recruitment workflow.

    Requires: workflow owner or viewer with assignment permissions
    """
    wf = await workflow.get(db, id=workflow_id)
    if not wf:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow not found",
        )

    # Check permissions
    if current_user.role == "employer":
        if wf.employer_company_id != current_user.company_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Access denied"
            )
    elif current_user.role == "recruiter":
        has_access = await workflow_viewer.check_user_access(
            db,
            process_id=workflow_id,
            user_id=current_user.id,
            required_permission="manage_assignments",
        )
        if not has_access:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions"
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Access denied"
        )

    try:
        candidate_wf = await workflow_engine.assign_candidate(
            db,
            process_id=workflow_id,
            candidate_id=assignment.candidate_id,
            recruiter_id=assignment.assigned_recruiter_id,
            start_immediately=assignment.start_immediately,
        )
        return candidate_wf
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@router.post(
    API_ROUTES.WORKFLOWS.CANDIDATES_BULK, response_model=list[CandidateWorkflowInfo]
)
async def bulk_assign_candidates(
    workflow_id: int,
    bulk_assignment: BulkCandidateAssignment,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Bulk assign multiple candidates to a recruitment workflow.
    """
    wf = await workflow.get(db, id=workflow_id)
    if not wf:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow not found",
        )

    # Check permissions
    if current_user.role == "employer":
        if wf.employer_company_id != current_user.company_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Access denied"
            )
    elif current_user.role == "recruiter":
        has_access = await workflow_viewer.check_user_access(
            db,
            process_id=workflow_id,
            user_id=current_user.id,
            required_permission="manage_assignments",
        )
        if not has_access:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions"
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Access denied"
        )

    candidate_workflows = await workflow_engine.bulk_assign_candidates(
        db,
        process_id=workflow_id,
        candidate_ids=bulk_assignment.candidate_ids,
        assigned_recruiter_id=bulk_assignment.assigned_recruiter_id,
        start_immediately=bulk_assignment.start_immediately,
    )

    return candidate_workflows


@router.get(API_ROUTES.WORKFLOWS.CANDIDATES, response_model=list[CandidateWorkflowInfo])
async def list_workflow_candidates(
    workflow_id: int,
    status: str | None = Query(None, description="Filter by status"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    List candidates in a recruitment workflow.
    """
    wf = await workflow.get(db, id=workflow_id)
    if not wf:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow not found",
        )

    # Check permissions
    if current_user.role == "employer":
        if wf.employer_company_id != current_user.company_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Access denied"
            )
    elif current_user.role == "recruiter":
        has_access = await workflow_viewer.check_user_access(
            db,
            process_id=workflow_id,
            user_id=current_user.id,
            required_permission="view_candidates",
        )
        if not has_access:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions"
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Access denied"
        )

    candidates = await candidate_workflow.get_by_process_id(
        db, process_id=workflow_id, status=status, skip=skip, limit=limit
    )

    return candidates


@router.get(
    API_ROUTES.WORKFLOWS.CANDIDATE_PROCESS_BY_ID, response_model=CandidateWorkflowDetails
)
async def get_candidate_workflow(
    candidate_workflow_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Get detailed information about a candidate workflow.
    """
    candidate_wf = await candidate_workflow.get_with_details(
        db, id=candidate_workflow_id
    )
    if not candidate_wf:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Candidate workflow not found"
        )

    # Check permissions
    if current_user.role == "candidate":
        if candidate_wf.candidate_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Access denied"
            )
    elif current_user.role == "employer":
        if candidate_wf.process.employer_company_id != current_user.company_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Access denied"
            )
    elif current_user.role == "recruiter":
        # Check if assigned to this candidate or has viewer access
        if candidate_wf.assigned_recruiter_id != current_user.id:
            has_access = await workflow_viewer.check_user_access(
                db,
                process_id=candidate_wf.workflow_id,
                user_id=current_user.id,
                required_permission="view_candidates",
            )
            if not has_access:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN, detail="Access denied"
                )
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Access denied"
        )

    return candidate_wf


@router.post(API_ROUTES.WORKFLOWS.CANDIDATE_START, response_model=CandidateWorkflowInfo)
async def start_candidate_workflow(
    candidate_workflow_id: int,
    start_data: CandidateWorkflowStart,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Start a candidate workflow.
    """
    candidate_wf = await candidate_workflow.get(db, id=candidate_workflow_id)
    if not candidate_wf:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Candidate workflow not found"
        )

    # Check permissions - only recruiters or employers can start workflows
    if current_user.role == "employer":
        wf = await workflow.get(db, id=candidate_wf.process_id)
        if not wf or wf.employer_company_id != current_user.company_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Access denied"
            )
    elif current_user.role == "recruiter":
        if candidate_wf.assigned_recruiter_id != current_user.id:
            has_access = await workflow_viewer.check_user_access(
                db,
                process_id=candidate_wf.workflow_id,
                user_id=current_user.id,
                required_permission="execute_nodes",
            )
            if not has_access:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN, detail="Access denied"
                )
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only recruiters and employers can start candidate workflows",
        )

    try:
        started_wf = await workflow_engine.start_candidate_workflow(
            db, candidate_workflow_id
        )
        return started_wf
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@router.put(API_ROUTES.WORKFLOWS.CANDIDATE_STATUS, response_model=CandidateWorkflowInfo)
async def update_candidate_workflow_status(
    candidate_workflow_id: int,
    status_change: CandidateWorkflowStatusChange,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Update candidate workflow status.
    """
    candidate_wf = await candidate_workflow.get(db, id=candidate_workflow_id)
    if not candidate_wf:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Candidate workflow not found"
        )

    # Check permissions
    if current_user.role == "employer":
        wf = await workflow.get(db, id=candidate_wf.process_id)
        if not wf or wf.employer_company_id != current_user.company_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Access denied"
            )
    elif current_user.role == "recruiter":
        if candidate_wf.assigned_recruiter_id != current_user.id:
            has_access = await workflow_viewer.check_user_access(
                db,
                process_id=candidate_wf.workflow_id,
                user_id=current_user.id,
                required_permission="override_results",
            )
            if not has_access:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN, detail="Access denied"
                )
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Access denied"
        )

    # Handle different status changes
    if status_change.status == "completed":
        if not status_change.final_result:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Final result is required when completing a workflow",
            )
        updated_wf = await candidate_workflow.complete_process(
            db,
            candidate_workflow=candidate_wf,
            final_result=status_change.final_result,
            overall_score=status_change.overall_score,
            notes=status_change.reason,
        )
    elif status_change.status == "failed":
        updated_wf = await candidate_workflow.fail_process(
            db, candidate_workflow=candidate_wf, reason=status_change.reason
        )
    elif status_change.status == "withdrawn":
        updated_wf = await candidate_workflow.withdraw_process(
            db, candidate_workflow=candidate_wf, reason=status_change.reason
        )
    elif status_change.status == "on_hold":
        updated_wf = await candidate_workflow.put_on_hold(
            db, candidate_workflow=candidate_wf
        )
    elif status_change.status == "in_progress":
        updated_wf = await candidate_workflow.resume_process(
            db, candidate_workflow=candidate_wf
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid status transition",
        )

    return updated_wf


@router.get(API_ROUTES.WORKFLOWS.CANDIDATE_TIMELINE, response_model=CandidateTimeline)
async def get_candidate_timeline(
    candidate_workflow_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Get timeline for a candidate workflow.
    """
    candidate_wf = await candidate_workflow.get_with_details(
        db, id=candidate_workflow_id
    )
    if not candidate_wf:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Candidate workflow not found"
        )

    # Check permissions
    if current_user.role == "candidate":
        if candidate_wf.candidate_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Access denied"
            )
    elif current_user.role == "employer":
        if candidate_wf.process.employer_company_id != current_user.company_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Access denied"
            )
    elif current_user.role == "recruiter":
        if candidate_wf.assigned_recruiter_id != current_user.id:
            has_access = await workflow_viewer.check_user_access(
                db,
                process_id=candidate_wf.workflow_id,
                user_id=current_user.id,
                required_permission="view_candidates",
            )
            if not has_access:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN, detail="Access denied"
                )
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Access denied"
        )

    timeline_items = await workflow_engine.get_candidate_timeline(
        db, candidate_workflow_id
    )

    return CandidateTimeline(
        candidate_workflow_id=candidate_workflow_id,
        candidate_name=candidate_wf.candidate.name
        if candidate_wf.candidate
        else "Unknown",
        process_name=candidate_wf.process.name,
        current_status=candidate_wf.status,
        timeline_items=timeline_items,
    )


@router.get(
    API_ROUTES.WORKFLOWS.MY_PROCESSES, response_model=list[CandidateWorkflowInfo]
)
async def get_my_candidate_workflows(
    status: str | None = Query(None, description="Filter by status"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Get candidate workflows for the current user.

    For candidates: returns their own workflows
    For recruiters: returns workflows assigned to them
    """
    if current_user.role == "candidate":
        workflows = await candidate_workflow.get_by_candidate_id(
            db, candidate_id=current_user.id, status=status, skip=skip, limit=limit
        )
    elif current_user.role == "recruiter":
        workflows = await candidate_workflow.get_by_recruiter_id(
            db, recruiter_id=current_user.id, status=status, skip=skip, limit=limit
        )
    else:
        workflows = []

    return workflows


@router.get(API_ROUTES.WORKFLOWS.RECRUITER_WORKLOAD, response_model=RecruiterWorkload)
async def get_recruiter_workload(
    recruiter_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Get workload information for a recruiter.
    """
    # Check permissions - only employers, admins, or the recruiter themselves
    if current_user.role == "recruiter" and current_user.id != recruiter_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Access denied"
        )
    elif current_user.role not in ["employer", "admin", "recruiter"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Access denied"
        )

    workload = await candidate_workflow.get_recruiter_workload(
        db, recruiter_id=recruiter_id
    )

    # Get recruiter name (would typically be from user table)
    recruiter_name = f"Recruiter {recruiter_id}"  # Placeholder

    return RecruiterWorkload(
        recruiter_id=recruiter_id,
        recruiter_name=recruiter_name,
        active_processes=workload["active_processes"],
        pending_tasks=workload["pending_tasks"],
        overdue_tasks=workload["overdue_tasks"],
        completion_rate=workload["completion_rate"],
        average_response_time_hours=0.0,  # Would be calculated from response times
    )
