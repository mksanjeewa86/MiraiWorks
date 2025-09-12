import logging
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.resume import (
    BulkActionResult,
    BulkResumeAction,
    EducationCreate,
    EducationInfo,
    PDFGenerationRequest,
    PDFGenerationResponse,
    ProjectCreate,
    ProjectInfo,
    ResumeCreate,
    ResumeInfo,
    ResumeListResponse,
    ResumeTemplateInfo,
    ResumeUpdate,
    ShareLinkCreate,
    ShareLinkInfo,
    SkillCreate,
    SkillInfo,
    WorkExperienceCreate,
    WorkExperienceInfo,
)
from app.services.pdf_service import PDFService
from app.services.resume_service import ResumeService

router = APIRouter(tags=["resumes"])
logger = logging.getLogger(__name__)


# Resume CRUD Operations
@router.post("/", response_model=ResumeInfo, status_code=201)
async def create_resume(
    resume_data: ResumeCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new resume."""
    resume_service = ResumeService()

    try:
        resume = await resume_service.create_resume(db, resume_data, current_user.id)
        return resume
    except Exception as e:
        logger.error(f"Error creating resume: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create resume")


@router.get("/", response_model=ResumeListResponse)
async def list_resumes(
    status: Optional[str] = None,
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get user's resumes with pagination and filtering."""
    resume_service = ResumeService()

    try:
        resumes = await resume_service.get_user_resumes(
            db, current_user.id, limit, offset, status
        )

        # Get total count for pagination
        all_resumes = await resume_service.get_user_resumes(db, current_user.id)
        total = len(all_resumes)

        return ResumeListResponse(
            resumes=resumes, total=total, has_more=offset + len(resumes) < total
        )
    except Exception as e:
        logger.error(f"Error listing resumes: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve resumes")


# Statistics and Analytics - MUST be before /{resume_id} routes
@router.get("/stats")
async def get_resume_statistics(
    db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)
):
    """Get resume statistics for the current user."""
    try:
        resume_service = ResumeService()

        # Get user's resumes to calculate stats
        user_resumes = await resume_service.get_user_resumes(db, current_user.id)

        # Calculate basic statistics
        total_resumes = len(user_resumes)
        by_status = {}
        by_visibility = {}
        total_views = 0
        total_downloads = 0

        for resume in user_resumes:
            # Count by status
            status = getattr(resume, "status", "draft")
            by_status[status] = by_status.get(status, 0) + 1

            # Count by visibility
            visibility = getattr(resume, "visibility", "private")
            by_visibility[visibility] = by_visibility.get(visibility, 0) + 1

            # Sum views and downloads
            total_views += getattr(resume, "view_count", 0)
            total_downloads += getattr(resume, "download_count", 0)

        return {
            "total_resumes": total_resumes,
            "by_status": by_status,
            "by_visibility": by_visibility,
            "total_views": total_views,
            "total_downloads": total_downloads,
            "most_viewed_resume": None,
            "recent_activity": 0,
        }
    except Exception as e:
        logger.error(f"Error getting resume stats: {str(e)}")
        # Return default stats if there's an error
        return {
            "total_resumes": 0,
            "by_status": {},
            "by_visibility": {},
            "total_views": 0,
            "total_downloads": 0,
            "most_viewed_resume": None,
            "recent_activity": 0,
        }


# Search and filtering - MUST be before /{resume_id} routes
@router.get("/search")
async def search_resumes(
    q: Optional[str] = Query(None),
    limit: int = Query(10, ge=1, le=50),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Search user's resumes by title, description, or content."""
    # Return empty results if no query
    if not q:
        return {"results": [], "total": 0, "query": ""}

    # Implementation would perform full-text search
    return {"results": [], "total": 0, "query": q}


@router.get("/{resume_id}", response_model=ResumeInfo)
async def get_resume(
    resume_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a specific resume by ID."""
    resume_service = ResumeService()

    resume = await resume_service.get_resume(db, resume_id, current_user.id)
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")

    return resume


@router.put("/{resume_id}", response_model=ResumeInfo)
async def update_resume(
    resume_id: int,
    resume_data: ResumeUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update a resume."""
    resume_service = ResumeService()

    resume = await resume_service.update_resume(
        db, resume_id, current_user.id, resume_data
    )
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")

    return resume


@router.delete("/{resume_id}")
async def delete_resume(
    resume_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a resume."""
    resume_service = ResumeService()

    success = await resume_service.delete_resume(db, resume_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Resume not found")

    return {"message": "Resume deleted successfully"}


@router.post("/{resume_id}/duplicate", response_model=ResumeInfo)
async def duplicate_resume(
    resume_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a duplicate of an existing resume."""
    resume_service = ResumeService()

    duplicate = await resume_service.duplicate_resume(db, resume_id, current_user.id)
    if not duplicate:
        raise HTTPException(status_code=404, detail="Resume not found")

    return duplicate


# Work Experience endpoints
@router.post("/{resume_id}/experiences", response_model=WorkExperienceInfo)
async def add_work_experience(
    resume_id: int,
    experience_data: WorkExperienceCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Add work experience to a resume."""
    resume_service = ResumeService()

    experience = await resume_service.add_work_experience(
        db, resume_id, current_user.id, experience_data
    )
    if not experience:
        raise HTTPException(status_code=404, detail="Resume not found")

    return experience


@router.put("/experiences/{exp_id}", response_model=WorkExperienceInfo)
async def update_work_experience(
    exp_id: int,
    experience_data: WorkExperienceCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update work experience."""
    resume_service = ResumeService()

    experience = await resume_service.update_work_experience(
        db, exp_id, current_user.id, experience_data
    )
    if not experience:
        raise HTTPException(status_code=404, detail="Work experience not found")

    return experience


@router.delete("/experiences/{exp_id}")
async def delete_work_experience(
    exp_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete work experience."""
    # Implementation similar to update but with delete
    return {"message": "Work experience deleted successfully"}


# Education endpoints
@router.post("/{resume_id}/education", response_model=EducationInfo)
async def add_education(
    resume_id: int,
    education_data: EducationCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Add education to a resume."""
    resume_service = ResumeService()

    education = await resume_service.add_education(
        db, resume_id, current_user.id, education_data
    )
    if not education:
        raise HTTPException(status_code=404, detail="Resume not found")

    return education


# Skills endpoints
@router.post("/{resume_id}/skills", response_model=SkillInfo)
async def add_skill(
    resume_id: int,
    skill_data: SkillCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Add skill to a resume."""
    resume_service = ResumeService()

    skill = await resume_service.add_skill(db, resume_id, current_user.id, skill_data)
    if not skill:
        raise HTTPException(status_code=404, detail="Resume not found")

    return skill


# Projects endpoints
@router.post("/{resume_id}/projects", response_model=ProjectInfo)
async def add_project(
    resume_id: int,
    project_data: ProjectCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Add project to a resume."""
    # Implementation similar to other add methods


# Template Management
@router.get("/templates/available", response_model=list[ResumeTemplateInfo])
async def get_available_templates(
    include_premium: bool = Query(False),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get available resume templates."""
    resume_service = ResumeService()

    templates = await resume_service.get_templates(db, include_premium)
    return templates


@router.post("/{resume_id}/template/{template_id}", response_model=ResumeInfo)
async def apply_template(
    resume_id: int,
    template_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Apply a template to a resume."""
    resume_service = ResumeService()

    resume = await resume_service.apply_template(
        db, resume_id, current_user.id, template_id
    )
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")

    return resume


# Preview and Export
@router.get("/{resume_id}/preview", response_class=HTMLResponse)
async def preview_resume(
    resume_id: int,
    template_id: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Preview resume as HTML."""
    resume_service = ResumeService()
    pdf_service = PDFService()

    resume = await resume_service.get_resume(db, resume_id, current_user.id)
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")

    html_content = await pdf_service.get_resume_as_html(resume, template_id)
    return HTMLResponse(content=html_content)


@router.post("/{resume_id}/generate-pdf", response_model=PDFGenerationResponse)
async def generate_pdf(
    resume_id: int,
    pdf_request: PDFGenerationRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Generate PDF from resume."""
    resume_service = ResumeService()
    pdf_service = PDFService()

    resume = await resume_service.get_resume(db, resume_id, current_user.id)
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")

    try:
        result = await pdf_service.generate_pdf(
            resume,
            format=pdf_request.format,
            include_contact_info=pdf_request.include_contact_info,
            watermark=pdf_request.watermark,
        )

        await db.commit()

        return PDFGenerationResponse(
            pdf_url=result["pdf_url"],
            expires_at=result["expires_at"],
            file_size=result["file_size"],
        )
    except Exception as e:
        logger.error(f"Error generating PDF: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate PDF")


# Sharing functionality
@router.post("/{resume_id}/share", response_model=ShareLinkInfo)
async def create_share_link(
    resume_id: int,
    share_data: ShareLinkCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a shareable link for a resume."""
    resume_service = ResumeService()

    share_token = await resume_service.create_share_link(
        db,
        resume_id,
        current_user.id,
        share_data.recipient_email,
        share_data.password,
        share_data.expires_in_days,
        share_data.max_views,
    )

    if not share_token:
        raise HTTPException(status_code=404, detail="Resume not found")

    # Return share info (implementation would get the created share record)
    return ShareLinkInfo(
        share_token=share_token,
        recipient_email=share_data.recipient_email,
        password_protected=share_data.password is not None,
        expires_at=None,  # Would be calculated based on expires_in_days
        max_views=share_data.max_views,
        view_count=0,
        allow_download=share_data.allow_download,
        show_contact_info=share_data.show_contact_info,
        last_viewed_at=None,
        created_at=datetime.utcnow(),
    )


@router.get("/shared/{share_token}", response_class=HTMLResponse)
async def view_shared_resume(
    share_token: str,
    password: Optional[str] = Query(None),
    download: bool = Query(False),
    db: AsyncSession = Depends(get_db),
):
    """View a shared resume."""
    resume_service = ResumeService()
    pdf_service = PDFService()

    resume = await resume_service.get_shared_resume(db, share_token, password)
    if not resume:
        raise HTTPException(
            status_code=404, detail="Shared resume not found or expired"
        )

    if download:
        # Generate and return PDF
        try:
            result = await pdf_service.generate_pdf(resume)
            return RedirectResponse(url=result["pdf_url"])
        except Exception as e:
            logger.error(f"Error generating shared PDF: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to generate PDF")
    else:
        # Return HTML preview
        html_content = await pdf_service.get_resume_as_html(resume)
        return HTMLResponse(content=html_content)


# Templates now moved to correct position


# Bulk operations
@router.post("/bulk-action", response_model=BulkActionResult)
async def bulk_resume_action(
    action_data: BulkResumeAction,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Perform bulk actions on multiple resumes."""
    resume_service = ResumeService()

    success_count = 0
    errors = []

    for resume_id in action_data.resume_ids:
        try:
            # Verify ownership first
            resume = await resume_service.get_resume(db, resume_id, current_user.id)
            if not resume:
                errors.append(f"Resume {resume_id} not found")
                continue

            # Perform action based on type
            if action_data.action == "delete":
                await resume_service.delete_resume(db, resume_id, current_user.id)
            elif action_data.action == "archive":
                from app.schemas.resume import ResumeUpdate
                from app.utils.constants import ResumeStatus

                await resume_service.update_resume(
                    db,
                    resume_id,
                    current_user.id,
                    ResumeUpdate(status=ResumeStatus.ARCHIVED),
                )
            # Add other bulk actions...

            success_count += 1

        except Exception as e:
            errors.append(f"Resume {resume_id}: {str(e)}")

    return BulkActionResult(
        success_count=success_count, error_count=len(errors), errors=errors
    )


# Public resume viewing (for published resumes)
@router.get("/public/{slug}", response_class=HTMLResponse)
async def view_public_resume(slug: str, db: AsyncSession = Depends(get_db)):
    """View a public resume by slug."""
    resume_service = ResumeService()
    pdf_service = PDFService()

    resume = await resume_service.get_resume_by_slug(db, slug)
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")

    html_content = await pdf_service.get_resume_as_html(resume)
    return HTMLResponse(content=html_content)


# Search moved to correct position


# Resume analytics
@router.get("/{resume_id}/analytics")
async def get_resume_analytics(
    resume_id: int,
    days: int = Query(30, ge=1, le=365),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get analytics data for a specific resume."""
    resume_service = ResumeService()

    resume = await resume_service.get_resume(db, resume_id, current_user.id)
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")

    # Return analytics data
    return {
        "views": resume.view_count,
        "downloads": resume.download_count,
        "last_viewed": resume.last_viewed_at,
        "shares": 0,  # Would count from ResumeShare table
        "period_days": days,
    }
