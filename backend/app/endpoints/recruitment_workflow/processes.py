
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.recruitment_workflow.process_viewer import process_viewer
from app.crud.recruitment_workflow.recruitment_process import recruitment_process
from app.database import get_db
from app.dependencies import get_current_active_user
from app.models.user import User
from app.schemas.recruitment_workflow.recruitment_process import (
    ProcessActivation,
    ProcessAnalytics,
    ProcessArchive,
    ProcessClone,
    ProcessStatistics,
    RecruitmentProcessCreate,
    RecruitmentProcessDetails,
    RecruitmentProcessInfo,
    RecruitmentProcessUpdate,
)
from app.services.recruitment_workflow.workflow_engine import workflow_engine

router = APIRouter()


def get_user_roles(user: User) -> list[str]:
    """Helper function to get user roles."""
    return [user_role.role.name for user_role in user.user_roles]


@router.post("/", response_model=RecruitmentProcessInfo, status_code=status.HTTP_201_CREATED)
async def create_recruitment_process(
    process_data: RecruitmentProcessCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Create a new recruitment process.

    Requires: employer or company_admin role
    """
    # Verify user is employer/company_admin and has company access
    user_roles = get_user_roles(current_user)
    if not any(role in user_roles for role in ["employer", "company_admin"]) or not current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only employers can create recruitment processes"
        )

    # Add employer company ID
    process_dict = process_data.dict()
    process_dict["employer_company_id"] = current_user.company_id

    process = await recruitment_process.create(
        db, obj_in=process_dict, created_by=current_user.id
    )

    return process


@router.get("/", response_model=list[RecruitmentProcessInfo])
async def list_recruitment_processes(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: str | None = Query(None, description="Filter by status"),
    company_id: int | None = Query(None, description="Filter by company (admin only)"),
    search: str | None = Query(None, description="Search by name or description"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    List recruitment processes.

    Returns processes based on user role and permissions.
    """
    # Get current user's roles
    current_user_roles = [user_role.role.name for user_role in current_user.user_roles]

    if ("super_admin" in current_user_roles or "company_admin" in current_user_roles) and company_id:
        # Admin can view processes for any company
        if search:
            processes = await recruitment_process.search(
                db, company_id=company_id, query=search, status=status, skip=skip, limit=limit
            )
        else:
            processes = await recruitment_process.get_by_company_id(
                db, company_id=company_id, skip=skip, limit=limit
            )
    elif any(role in current_user_roles for role in ["employer", "company_admin"]) and current_user.company_id:
        # Employer sees their company's processes
        if search:
            processes = await recruitment_process.search(
                db, company_id=current_user.company_id, query=search, status=status, skip=skip, limit=limit
            )
        else:
            processes = await recruitment_process.get_by_company_id(
                db, company_id=current_user.company_id, skip=skip, limit=limit
            )
    else:
        # Recruiter/viewer sees processes they have access to
        processes = await recruitment_process.get_for_user(
            db, user_id=current_user.id, role=current_user_roles[0] if current_user_roles else "user", skip=skip, limit=limit
        )

    return processes


@router.get("/{process_id}", response_model=RecruitmentProcessDetails)
async def get_recruitment_process(
    process_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get detailed information about a recruitment process.
    """
    process = await recruitment_process.get_with_nodes(db, id=process_id)
    if not process:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recruitment process not found"
        )

    # Check access permissions
    user_roles = get_user_roles(current_user)
    if any(role in user_roles for role in ["employer", "company_admin"]):
        if process.employer_company_id != current_user.company_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
    elif any(role in user_roles for role in ["recruiter", "candidate"]):
        # Check if user has viewer access
        has_access = await process_viewer.check_user_access(
            db, process_id=process_id, user_id=current_user.id, required_permission="view_process"
        )
        if not has_access:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )

    return process


@router.put("/{process_id}", response_model=RecruitmentProcessInfo)
async def update_recruitment_process(
    process_id: int,
    process_update: RecruitmentProcessUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Update a recruitment process.

    Requires: process owner or admin
    """
    process = await recruitment_process.get(db, id=process_id)
    if not process:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recruitment process not found"
        )

    # Check permissions
    user_roles = get_user_roles(current_user)
    if any(role in user_roles for role in ["employer", "company_admin"]):
        if process.employer_company_id != current_user.company_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
    elif not any(role in user_roles for role in ["super_admin", "company_admin"]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions"
        )

    # Cannot update active processes without special handling
    if process.status == "active" and not process_update.dict(exclude_unset=True).get("force_update"):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cannot update active processes without force_update=true"
        )

    updated_process = await recruitment_process.update(
        db, db_obj=process, obj_in=process_update.dict(exclude_unset=True), updated_by=current_user.id
    )

    return updated_process


@router.post("/{process_id}/activate", response_model=RecruitmentProcessInfo)
async def activate_recruitment_process(
    process_id: int,
    activation: ProcessActivation,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Activate a recruitment process.

    Requires: process owner
    """
    process = await recruitment_process.get(db, id=process_id)
    if not process:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recruitment process not found"
        )

    # Check permissions
    user_roles = get_user_roles(current_user)
    if any(role in user_roles for role in ["employer", "company_admin"]):
        if process.employer_company_id != current_user.company_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
    elif not any(role in user_roles for role in ["super_admin", "company_admin"]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions"
        )

    try:
        activated_process = await workflow_engine.activate_process(
            db, process_id=process_id, user_id=current_user.id
        )
        return activated_process
    except ValueError as e:
        if activation.force_activate:
            # Force activation even with validation issues
            activated_process = await recruitment_process.activate(
                db, db_obj=process, activated_by=current_user.id
            )
            return activated_process
        else:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=str(e)
            )


@router.post("/{process_id}/archive", response_model=RecruitmentProcessInfo)
async def archive_recruitment_process(
    process_id: int,
    archive_data: ProcessArchive,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Archive a recruitment process.

    Requires: process owner
    """
    process = await recruitment_process.get(db, id=process_id)
    if not process:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recruitment process not found"
        )

    # Check permissions
    user_roles = get_user_roles(current_user)
    if any(role in user_roles for role in ["employer", "company_admin"]):
        if process.employer_company_id != current_user.company_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
    elif not any(role in user_roles for role in ["super_admin", "company_admin"]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions"
        )

    archived_process = await recruitment_process.archive(
        db, db_obj=process, archived_by=current_user.id
    )

    return archived_process


@router.post("/{process_id}/clone", response_model=RecruitmentProcessInfo)
async def clone_recruitment_process(
    process_id: int,
    clone_data: ProcessClone,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Clone a recruitment process.

    Requires: process access
    """
    # Check if user can access the source process
    source_process = await recruitment_process.get(db, id=process_id)
    if not source_process:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Source process not found"
        )

    # Check access permissions
    user_roles = get_user_roles(current_user)
    if any(role in user_roles for role in ["employer", "company_admin"]):
        if source_process.employer_company_id != current_user.company_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
    elif any(role in user_roles for role in ["recruiter", "candidate"]):
        has_access = await process_viewer.check_user_access(
            db, process_id=process_id, user_id=current_user.id, required_permission="view_process"
        )
        if not has_access:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )

    # Only employers can create new processes
    user_roles = get_user_roles(current_user)
    if not any(role in user_roles for role in ["employer", "company_admin"]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only employers can create new processes"
        )

    cloned_process = await workflow_engine.clone_process(
        db,
        source_process_id=process_id,
        new_name=clone_data.new_name,
        created_by=current_user.id,
        clone_candidates=clone_data.clone_candidates,
        clone_viewers=clone_data.clone_viewers
    )

    return cloned_process


@router.delete("/{process_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_recruitment_process(
    process_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Soft delete a recruitment process (論理削除).

    Requires: process owner or admin
    Only draft processes can be deleted.
    """
    process = await recruitment_process.get(db, id=process_id)
    if not process:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recruitment process not found"
        )

    # Check permissions
    user_roles = get_user_roles(current_user)
    if any(role in user_roles for role in ["employer", "company_admin"]):
        if process.employer_company_id != current_user.company_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
    elif not any(role in user_roles for role in ["super_admin", "company_admin"]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions"
        )

    # Only allow deletion of draft processes
    if process.status != "draft":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Only draft processes can be deleted"
        )

    # Use soft delete instead of hard delete
    await recruitment_process.soft_delete(db, id=process_id)


@router.get("/{process_id}/validate")
async def validate_recruitment_process(
    process_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Validate a recruitment process before activation.
    """
    process = await recruitment_process.get(db, id=process_id)
    if not process:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recruitment process not found"
        )

    # Check access permissions
    user_roles = get_user_roles(current_user)
    if any(role in user_roles for role in ["employer", "company_admin"]):
        if process.employer_company_id != current_user.company_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
    elif "recruiter" in user_roles:
        has_access = await process_viewer.check_user_access(
            db, process_id=process_id, user_id=current_user.id, required_permission="view_process"
        )
        if not has_access:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )

    validation_result = await workflow_engine.validate_process(db, process_id)
    return validation_result


@router.get("/{process_id}/analytics", response_model=ProcessAnalytics)
async def get_process_analytics(
    process_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get comprehensive analytics for a recruitment process.
    """
    process = await recruitment_process.get(db, id=process_id)
    if not process:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recruitment process not found"
        )

    # Check permissions
    user_roles = get_user_roles(current_user)
    if any(role in user_roles for role in ["employer", "company_admin"]):
        if process.employer_company_id != current_user.company_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
    elif "recruiter" in user_roles:
        has_access = await process_viewer.check_user_access(
            db, process_id=process_id, user_id=current_user.id, required_permission="view_analytics"
        )
        if not has_access:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )

    analytics = await workflow_engine.get_process_analytics(db, process_id)

    return ProcessAnalytics(
        process_id=process_id,
        process_name=process.name,
        total_candidates=analytics["total_candidates"],
        completed_candidates=analytics["by_status"].get("completed", 0),
        failed_candidates=analytics["by_status"].get("failed", 0),
        withdrawn_candidates=analytics["by_status"].get("withdrawn", 0),
        completion_rate=analytics["completion_rate"],
        average_duration_days=analytics["average_duration_days"],
        node_statistics=analytics["node_statistics"],
        bottleneck_nodes=analytics["bottleneck_nodes"],
        recruiter_workload=analytics["recruiter_workload"]
    )


@router.get("/company/{company_id}/statistics", response_model=ProcessStatistics)
async def get_company_process_statistics(
    company_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get recruitment process statistics for a company.

    Requires: company access or admin
    """
    # Check permissions
    user_roles = get_user_roles(current_user)
    if any(role in user_roles for role in ["employer", "company_admin"]):
        if current_user.company_id != company_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
    elif not any(role in user_roles for role in ["super_admin", "company_admin"]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions"
        )

    stats = await recruitment_process.get_statistics(db, company_id=company_id)

    return ProcessStatistics(**stats)


@router.get("/templates/", response_model=list[RecruitmentProcessInfo])
async def list_process_templates(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    category: str | None = Query(None, description="Filter by category"),
    industry: str | None = Query(None, description="Filter by industry"),
    public_only: bool = Query(False, description="Show only public templates"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    List available process templates.
    """
    company_id = current_user.company_id if any(role in get_user_roles(current_user) for role in ["employer", "company_admin"]) else None

    templates = await recruitment_process.get_templates(
        db,
        company_id=company_id,
        is_public=public_only,
        skip=skip,
        limit=limit
    )

    # Filter by category/industry if specified
    if category or industry:
        filtered_templates = []
        for template in templates:
            settings = template.settings or {}
            if category and settings.get("category") != category:
                continue
            if industry and settings.get("industry") != industry:
                continue
            filtered_templates.append(template)
        templates = filtered_templates

    return templates


@router.post("/templates/{template_id}/apply", response_model=RecruitmentProcessInfo)
async def apply_process_template(
    template_id: int,
    process_data: RecruitmentProcessCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Create a new process from a template.

    Requires: employer or company_admin role
    """
    # Verify user is employer
    user_roles = get_user_roles(current_user)
    if not any(role in user_roles for role in ["employer", "company_admin"]) or not current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only employers can create processes from templates"
        )

    try:
        process = await workflow_engine.create_process_from_template(
            db,
            template_id=template_id,
            employer_id=current_user.id,
            process_data=process_data.dict()
        )
        return process
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
