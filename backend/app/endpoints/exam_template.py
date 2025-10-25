"""Exam template endpoints."""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.endpoints import API_ROUTES
from app.crud.exam_template import exam_template as exam_template_crud
from app.database import get_db
from app.dependencies import get_current_active_user
from app.models.user import User
from app.schemas.exam_template import (
    ExamTemplateCreate,
    ExamTemplateInfo,
    ExamTemplateListResponse,
    ExamTemplateUpdate,
)
from app.utils.auth import require_roles
from app.utils.constants import UserRole

router = APIRouter()


@router.post(API_ROUTES.EXAMS.TEMPLATES, response_model=ExamTemplateInfo)
async def create_exam_template(
    template_data: ExamTemplateCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new exam template."""
    require_roles(current_user, [UserRole.ADMIN])

    # Check if system admin
    is_system_admin = any(
        role.role.name == UserRole.SYSTEM_ADMIN for role in current_user.user_roles
    )

    # Company validation
    if not is_system_admin:
        if (
            template_data.company_id
            and template_data.company_id != current_user.company_id
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot create template for different company",
            )
        template_data.company_id = current_user.company_id

    # Create template
    template_dict = template_data.model_dump()
    template_dict["created_by_id"] = current_user.id

    template = await exam_template_crud.create(db=db, obj_in=template_dict)

    return template


@router.get(API_ROUTES.EXAMS.TEMPLATES, response_model=ExamTemplateListResponse)
async def get_exam_templates(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    category: str | None = None,
    is_public: bool | None = None,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Get list of exam templates."""
    # Check if system admin
    is_system_admin = any(
        role.role.name == UserRole.SYSTEM_ADMIN for role in current_user.user_roles
    )

    templates, total = await exam_template_crud.get_templates(
        db=db,
        company_id=current_user.company_id if not is_system_admin else None,
        is_system_admin=is_system_admin,
        category=category,
        is_public=is_public,
        skip=skip,
        limit=limit,
    )

    return ExamTemplateListResponse(
        templates=templates,
        total=total,
        page=skip // limit + 1,
        page_size=limit,
        has_more=(skip + limit) < total,
    )


@router.get(API_ROUTES.EXAMS.TEMPLATE_BY_ID, response_model=ExamTemplateInfo)
async def get_exam_template(
    template_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Get exam template by ID."""
    template = await exam_template_crud.get(db=db, id=template_id)
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Template not found"
        )

    # Check access
    is_system_admin = any(
        role.role.name == UserRole.SYSTEM_ADMIN for role in current_user.user_roles
    )

    if (
        not is_system_admin
        and not template.is_public
        and template.company_id != current_user.company_id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Access denied"
        )

    return template


@router.put(API_ROUTES.EXAMS.TEMPLATE_BY_ID, response_model=ExamTemplateInfo)
async def update_exam_template(
    template_id: int,
    template_data: ExamTemplateUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Update exam template."""
    require_roles(current_user, [UserRole.ADMIN])

    # Get template
    template = await exam_template_crud.get(db=db, id=template_id)
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Template not found"
        )

    # Check permissions
    is_system_admin = any(
        role.role.name == UserRole.SYSTEM_ADMIN for role in current_user.user_roles
    )

    if not is_system_admin and template.company_id != current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Access denied"
        )

    # Update template
    updated_template = await exam_template_crud.update(
        db=db, db_obj=template, obj_in=template_data.model_dump(exclude_unset=True)
    )

    return updated_template


@router.delete(API_ROUTES.EXAMS.TEMPLATE_BY_ID)
async def delete_exam_template(
    template_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete exam template."""
    require_roles(current_user, [UserRole.ADMIN])

    # Get template
    template = await exam_template_crud.get(db=db, id=template_id)
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Template not found"
        )

    # Check permissions
    is_system_admin = any(
        role.role.name == UserRole.SYSTEM_ADMIN for role in current_user.user_roles
    )

    if not is_system_admin and template.company_id != current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Access denied"
        )

    # Delete template
    await exam_template_crud.remove(db=db, id=template_id)

    return {"message": "Template deleted successfully"}


@router.post(API_ROUTES.EXAMS.TEMPLATE_FROM_EXAM, response_model=ExamTemplateInfo)
async def create_template_from_exam(
    exam_id: int,
    name: str = Query(..., min_length=1, max_length=255),
    description: str | None = Query(None),
    is_public: bool = Query(False),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a template from an existing exam."""
    require_roles(current_user, [UserRole.ADMIN])

    # Check if system admin
    is_system_admin = any(
        role.role.name == UserRole.SYSTEM_ADMIN for role in current_user.user_roles
    )

    try:
        template = await exam_template_crud.create_from_exam(
            db=db,
            exam_id=exam_id,
            template_name=name,
            template_description=description,
            created_by_id=current_user.id,
            company_id=current_user.company_id if not is_system_admin else None,
            is_public=is_public,
        )
        return template
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
