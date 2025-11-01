from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.endpoints import API_ROUTES
from app.crud.workflow.workflow import workflow
from app.crud.workflow.workflow_viewer import workflow_viewer
from app.database import get_db
from app.dependencies import get_current_active_user
from app.models.user import User
from app.schemas.workflow.workflow import (
    ProcessActivation,
    ProcessAnalytics,
    ProcessArchive,
    ProcessClone,
    ProcessStatistics,
    WorkflowCreate,
    WorkflowDetails,
    WorkflowInfo,
    WorkflowUpdate,
)
from app.services.workflow.workflow_engine import workflow_engine
from app.utils.constants import UserRole

router = APIRouter()


def get_user_roles(user: User) -> list[str]:
    """Helper function to get user roles."""
    return [user_role.role.name for user_role in user.user_roles]


@router.post(
    API_ROUTES.WORKFLOWS.BASE,
    response_model=WorkflowInfo,
    status_code=status.HTTP_201_CREATED,
)
async def create_workflow(
    workflow_data: WorkflowCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Create a new recruitment workflow.

    Requires: employer or company_admin role
    """
    # Verify user is employer/company_admin and has company access
    user_roles = get_user_roles(current_user)
    if (
        not any(
            role in user_roles for role in [UserRole.MEMBER.value, UserRole.ADMIN.value]
        )
        or not current_user.company_id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only employers can create recruitment workflows",
        )

    # Add employer company ID
    workflow_dict = workflow_data.dict()
    workflow_dict["employer_company_id"] = current_user.company_id

    wf = await workflow.create(db, obj_in=workflow_dict, created_by=current_user.id)

    return wf


@router.get(API_ROUTES.WORKFLOWS.BASE, response_model=list[WorkflowInfo])
async def list_workflows(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: str | None = Query(None, description="Filter by status"),
    company_id: int | None = Query(None, description="Filter by company (admin only)"),
    search: str | None = Query(None, description="Search by name or description"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    List recruitment workflows.

    Returns workflows based on user role and permissions.
    """
    # Get current user's roles
    current_user_roles = [user_role.role.name for user_role in current_user.user_roles]

    if (
        UserRole.SYSTEM_ADMIN.value in current_user_roles
        or UserRole.ADMIN.value in current_user_roles
    ) and company_id:
        # Admin can view workflows for any company
        if search:
            workflows = await workflow.search(
                db,
                company_id=company_id,
                query=search,
                status=status,
                skip=skip,
                limit=limit,
            )
        else:
            workflows = await workflow.get_by_company_id(
                db, company_id=company_id, skip=skip, limit=limit
            )
    elif (
        any(
            role in current_user_roles
            for role in [UserRole.MEMBER.value, UserRole.ADMIN.value]
        )
        and current_user.company_id
    ):
        # Employer sees their company's workflows
        if search:
            workflows = await workflow.search(
                db,
                company_id=current_user.company_id,
                query=search,
                status=status,
                skip=skip,
                limit=limit,
            )
        else:
            workflows = await workflow.get_by_company_id(
                db, company_id=current_user.company_id, skip=skip, limit=limit
            )
    else:
        # Recruiter/viewer sees workflows they have access to
        workflows = await workflow.get_for_user(
            db,
            user_id=current_user.id,
            role=current_user_roles[0] if current_user_roles else "user",
            skip=skip,
            limit=limit,
        )

    return workflows


@router.get(API_ROUTES.WORKFLOWS.BY_ID, response_model=WorkflowDetails)
async def get_workflow(
    workflow_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Get detailed information about a recruitment workflow.
    """
    wf = await workflow.get_with_nodes(db, id=workflow_id)
    if not wf:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow not found",
        )

    # Check access permissions
    user_roles = get_user_roles(current_user)
    if any(
        role in user_roles for role in [UserRole.MEMBER.value, UserRole.ADMIN.value]
    ):
        if wf.employer_company_id != current_user.company_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Access denied"
            )
    elif any(role in user_roles for role in [UserRole.MEMBER.value, "candidate"]):
        # Check if user has viewer access
        has_access = await workflow_viewer.check_user_access(
            db,
            workflow_id=workflow_id,
            user_id=current_user.id,
            required_permission="view_process",
        )
        if not has_access:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Access denied"
            )

    return wf


@router.put(API_ROUTES.WORKFLOWS.BY_ID, response_model=WorkflowInfo)
async def update_workflow(
    workflow_id: int,
    workflow_update: WorkflowUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Update a recruitment workflow.

    Requires: workflow owner or admin
    """
    wf = await workflow.get(db, id=workflow_id)
    if not wf:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow not found",
        )

    # Check permissions
    user_roles = get_user_roles(current_user)
    if any(
        role in user_roles for role in [UserRole.MEMBER.value, UserRole.ADMIN.value]
    ):
        if wf.employer_company_id != current_user.company_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Access denied"
            )
    elif not any(
        role in user_roles
        for role in [UserRole.SYSTEM_ADMIN.value, UserRole.ADMIN.value]
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions"
        )

    # Cannot update active workflows without special handling
    if wf.status == "active" and not workflow_update.dict(exclude_unset=True).get(
        "force_update"
    ):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cannot update active workflows without force_update=true",
        )

    updated_wf = await workflow.update(
        db,
        db_obj=wf,
        obj_in=workflow_update.dict(exclude_unset=True),
        updated_by=current_user.id,
    )

    return updated_wf


@router.post(API_ROUTES.WORKFLOWS.ACTIVATE, response_model=WorkflowInfo)
async def activate_workflow(
    workflow_id: int,
    activation: ProcessActivation,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Activate a recruitment workflow.

    Requires: workflow owner
    """
    wf = await workflow.get(db, id=workflow_id)
    if not wf:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow not found",
        )

    # Check permissions
    user_roles = get_user_roles(current_user)
    if any(
        role in user_roles for role in [UserRole.MEMBER.value, UserRole.ADMIN.value]
    ):
        if wf.employer_company_id != current_user.company_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Access denied"
            )
    elif not any(
        role in user_roles
        for role in [UserRole.SYSTEM_ADMIN.value, UserRole.ADMIN.value]
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions"
        )

    try:
        activated_wf = await workflow_engine.activate_process(
            db, workflow_id=workflow_id, user_id=current_user.id
        )
        return activated_wf
    except ValueError as e:
        if activation.force_activate:
            # Force activation even with validation issues
            activated_wf = await workflow.activate(
                db, db_obj=wf, activated_by=current_user.id
            )
            return activated_wf
        else:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e)
            ) from e


@router.post(API_ROUTES.WORKFLOWS.ARCHIVE, response_model=WorkflowInfo)
async def archive_workflow(
    workflow_id: int,
    archive_data: ProcessArchive,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Archive a recruitment workflow.

    Requires: workflow owner
    """
    wf = await workflow.get(db, id=workflow_id)
    if not wf:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow not found",
        )

    # Check permissions
    user_roles = get_user_roles(current_user)
    if any(
        role in user_roles for role in [UserRole.MEMBER.value, UserRole.ADMIN.value]
    ):
        if wf.employer_company_id != current_user.company_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Access denied"
            )
    elif not any(
        role in user_roles
        for role in [UserRole.SYSTEM_ADMIN.value, UserRole.ADMIN.value]
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions"
        )

    archived_wf = await workflow.archive(db, db_obj=wf, archived_by=current_user.id)

    return archived_wf


@router.post(API_ROUTES.WORKFLOWS.CLONE, response_model=WorkflowInfo)
async def clone_workflow(
    workflow_id: int,
    clone_data: ProcessClone,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Clone a recruitment workflow.

    Requires: workflow access
    """
    # Check if user can access the source workflow
    source_wf = await workflow.get(db, id=workflow_id)
    if not source_wf:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Source workflow not found"
        )

    # Check access permissions
    user_roles = get_user_roles(current_user)
    if any(
        role in user_roles for role in [UserRole.MEMBER.value, UserRole.ADMIN.value]
    ):
        if source_wf.employer_company_id != current_user.company_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Access denied"
            )
    elif any(role in user_roles for role in [UserRole.MEMBER.value, "candidate"]):
        has_access = await workflow_viewer.check_user_access(
            db,
            workflow_id=workflow_id,
            user_id=current_user.id,
            required_permission="view_process",
        )
        if not has_access:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Access denied"
            )

    # Only employers can create new workflows
    user_roles = get_user_roles(current_user)
    if not any(
        role in user_roles for role in [UserRole.MEMBER.value, UserRole.ADMIN.value]
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only employers can create new workflows",
        )

    cloned_wf = await workflow_engine.clone_process(
        db,
        source_workflow_id=workflow_id,
        new_name=clone_data.new_name,
        created_by=current_user.id,
        clone_candidates=clone_data.clone_candidates,
        clone_viewers=clone_data.clone_viewers,
    )

    return cloned_wf


@router.delete(API_ROUTES.WORKFLOWS.BY_ID, status_code=status.HTTP_204_NO_CONTENT)
async def delete_workflow(
    workflow_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Soft delete a recruitment workflow (論理削除).

    Requires: workflow owner or admin
    Only draft workflows can be deleted.
    """
    wf = await workflow.get(db, id=workflow_id)
    if not wf:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow not found",
        )

    # Check permissions
    user_roles = get_user_roles(current_user)
    if any(
        role in user_roles for role in [UserRole.MEMBER.value, UserRole.ADMIN.value]
    ):
        if wf.employer_company_id != current_user.company_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Access denied"
            )
    elif not any(
        role in user_roles
        for role in [UserRole.SYSTEM_ADMIN.value, UserRole.ADMIN.value]
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions"
        )

    # Only allow deletion of draft workflows
    if wf.status != "draft":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Only draft workflows can be deleted",
        )

    # Use soft delete instead of hard delete
    await workflow.soft_delete(db, id=workflow_id)


@router.get(API_ROUTES.WORKFLOWS.VALIDATE)
async def validate_workflow(
    workflow_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Validate a recruitment workflow before activation.
    """
    wf = await workflow.get(db, id=workflow_id)
    if not wf:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow not found",
        )

    # Check access permissions
    user_roles = get_user_roles(current_user)
    if any(
        role in user_roles for role in [UserRole.MEMBER.value, UserRole.ADMIN.value]
    ):
        if wf.employer_company_id != current_user.company_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Access denied"
            )
    elif UserRole.MEMBER.value in user_roles:
        has_access = await workflow_viewer.check_user_access(
            db,
            workflow_id=workflow_id,
            user_id=current_user.id,
            required_permission="view_process",
        )
        if not has_access:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Access denied"
            )

    validation_result = await workflow_engine.validate_process(db, workflow_id)
    return validation_result


@router.get(API_ROUTES.WORKFLOWS.ANALYTICS, response_model=ProcessAnalytics)
async def get_workflow_analytics(
    workflow_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Get comprehensive analytics for a recruitment workflow.
    """
    wf = await workflow.get(db, id=workflow_id)
    if not wf:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow not found",
        )

    # Check permissions
    user_roles = get_user_roles(current_user)
    if any(
        role in user_roles for role in [UserRole.MEMBER.value, UserRole.ADMIN.value]
    ):
        if wf.employer_company_id != current_user.company_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Access denied"
            )
    elif UserRole.MEMBER.value in user_roles:
        has_access = await workflow_viewer.check_user_access(
            db,
            workflow_id=workflow_id,
            user_id=current_user.id,
            required_permission="view_analytics",
        )
        if not has_access:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Access denied"
            )

    analytics = await workflow_engine.get_process_analytics(db, workflow_id)

    return ProcessAnalytics(
        workflow_id=workflow_id,
        process_name=wf.name,
        total_candidates=analytics["total_candidates"],
        completed_candidates=analytics["by_status"].get("completed", 0),
        failed_candidates=analytics["by_status"].get("failed", 0),
        withdrawn_candidates=analytics["by_status"].get("withdrawn", 0),
        completion_rate=analytics["completion_rate"],
        average_duration_days=analytics["average_duration_days"],
        node_statistics=analytics["node_statistics"],
        bottleneck_nodes=analytics["bottleneck_nodes"],
        recruiter_workload=analytics["recruiter_workload"],
    )


@router.get(API_ROUTES.WORKFLOWS.COMPANY_STATS, response_model=ProcessStatistics)
async def get_company_workflow_statistics(
    company_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Get recruitment workflow statistics for a company.

    Requires: company access or admin
    """
    # Check permissions
    user_roles = get_user_roles(current_user)
    if any(
        role in user_roles for role in [UserRole.MEMBER.value, UserRole.ADMIN.value]
    ):
        if current_user.company_id != company_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Access denied"
            )
    elif not any(
        role in user_roles
        for role in [UserRole.SYSTEM_ADMIN.value, UserRole.ADMIN.value]
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions"
        )

    stats = await workflow.get_statistics(db, company_id=company_id)

    return ProcessStatistics(**stats)


@router.get(API_ROUTES.WORKFLOWS.TEMPLATES, response_model=list[WorkflowInfo])
async def list_workflow_templates(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    category: str | None = Query(None, description="Filter by category"),
    industry: str | None = Query(None, description="Filter by industry"),
    public_only: bool = Query(False, description="Show only public templates"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    List available workflow templates.
    """
    company_id = (
        current_user.company_id
        if any(
            role in get_user_roles(current_user)
            for role in [UserRole.MEMBER.value, UserRole.ADMIN.value]
        )
        else None
    )

    templates = await workflow.get_templates(
        db, company_id=company_id, is_public=public_only, skip=skip, limit=limit
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


@router.post(API_ROUTES.WORKFLOWS.APPLY_TEMPLATE, response_model=WorkflowInfo)
async def apply_workflow_template(
    template_id: int,
    workflow_data: WorkflowCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Create a new workflow from a template.

    Requires: employer or company_admin role
    """
    # Verify user is employer
    user_roles = get_user_roles(current_user)
    if (
        not any(
            role in user_roles for role in [UserRole.MEMBER.value, UserRole.ADMIN.value]
        )
        or not current_user.company_id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only employers can create workflows from templates",
        )

    try:
        wf = await workflow_engine.create_process_from_template(
            db,
            template_id=template_id,
            employer_id=current_user.id,
            process_data=workflow_data.dict(),
        )
        return wf
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
