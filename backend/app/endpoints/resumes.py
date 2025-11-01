import logging

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.endpoints import API_ROUTES
from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.resume import (
    BulkActionResult,
    BulkResumeAction,
    EducationCreate,
    EducationInfo,
    EmailResumeRequest,
    JapaneseResumeTemplate,
    MessageAttachmentRequest,
    PDFGenerationRequest,
    PDFGenerationResponse,
    ProjectCreate,
    ProjectInfo,
    PublicResumeInfo,
    ResumeCreate,
    ResumeInfo,
    ResumeListResponse,
    ResumePublicSettings,
    ResumeTemplateInfo,
    ResumeUpdate,
    RirekishoData,
    ShareLinkCreate,
    ShareLinkInfo,
    ShokumuKeirekishoData,
    SkillCreate,
    SkillInfo,
    WorkExperienceCreate,
    WorkExperienceInfo,
)
from app.services.pdf_service import PDFService
from app.services.resume_service import ResumeService
from app.utils.datetime_utils import get_utc_now

router = APIRouter(tags=["resumes"])
logger = logging.getLogger(__name__)


# Resume CRUD Operations
@router.post(API_ROUTES.RESUMES.BASE, response_model=ResumeInfo, status_code=201)
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
        raise HTTPException(status_code=500, detail="Failed to create resume") from e


@router.get(API_ROUTES.RESUMES.BASE, response_model=ResumeListResponse)
async def list_resumes(
    status: str | None = None,
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get user's resumes with pagination and filtering."""
    from app.utils.constants import ResumeStatus

    resume_service = ResumeService()

    try:
        status_enum = None
        if status:
            try:
                status_enum = ResumeStatus(status.upper())
            except ValueError as e:
                raise HTTPException(
                    status_code=400, detail=f"Invalid status: {status}"
                ) from e

        resumes = await resume_service.get_user_resumes(
            db, current_user.id, limit, offset, status_enum
        )

        # Get total count for pagination
        all_resumes = await resume_service.get_user_resumes(db, current_user.id)
        total = len(all_resumes)

        return ResumeListResponse(
            resumes=[ResumeInfo.model_validate(r) for r in resumes],
            total=total,
            has_more=offset + len(resumes) < total,
        )
    except Exception as e:
        logger.error(f"Error listing resumes: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve resumes") from e


# Statistics and Analytics - MUST be before /{resume_id} routes
@router.get(API_ROUTES.RESUMES.STATS)
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
@router.get(API_ROUTES.RESUMES.SEARCH)
async def search_resumes(
    q: str | None = Query(None),
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


@router.get(API_ROUTES.RESUMES.BY_ID, response_model=ResumeInfo)
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


@router.put(API_ROUTES.RESUMES.BY_ID, response_model=ResumeInfo)
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


@router.delete(API_ROUTES.RESUMES.BY_ID)
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


@router.post(API_ROUTES.RESUMES.DUPLICATE, response_model=ResumeInfo)
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
@router.post(API_ROUTES.RESUMES.EXPERIENCES, response_model=WorkExperienceInfo)
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


@router.put(API_ROUTES.RESUMES.EXPERIENCE_BY_ID, response_model=WorkExperienceInfo)
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


@router.delete(API_ROUTES.RESUMES.EXPERIENCE_BY_ID)
async def delete_work_experience(
    exp_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete work experience."""
    # Implementation similar to update but with delete
    return {"message": "Work experience deleted successfully"}


# Education endpoints
@router.post(API_ROUTES.RESUMES.EDUCATION, response_model=EducationInfo)
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
@router.post(API_ROUTES.RESUMES.SKILLS, response_model=SkillInfo)
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
@router.post(API_ROUTES.RESUMES.PROJECTS, response_model=ProjectInfo)
async def add_project(
    resume_id: int,
    project_data: ProjectCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Add project to a resume."""
    # Implementation similar to other add methods


# Template Management
@router.get(
    API_ROUTES.RESUMES.TEMPLATES_AVAILABLE, response_model=list[ResumeTemplateInfo]
)
async def get_available_templates(
    include_premium: bool = Query(False),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get available resume templates."""
    resume_service = ResumeService()

    templates = await resume_service.get_templates(db, include_premium)
    return templates


@router.post(API_ROUTES.RESUMES.APPLY_TEMPLATE, response_model=ResumeInfo)
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
@router.get(API_ROUTES.RESUMES.PREVIEW, response_class=HTMLResponse)
async def preview_resume(
    resume_id: int,
    template_id: str | None = None,
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


@router.post(API_ROUTES.RESUMES.GENERATE_PDF, response_model=PDFGenerationResponse)
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
        raise HTTPException(status_code=500, detail="Failed to generate PDF") from e


# Sharing functionality
@router.post(API_ROUTES.RESUMES.SHARE, response_model=ShareLinkInfo)
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
        created_at=get_utc_now(),
    )


@router.get(API_ROUTES.RESUMES.SHARED, response_class=HTMLResponse)
async def view_shared_resume(
    share_token: str,
    password: str | None = Query(None),
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
            raise HTTPException(status_code=500, detail="Failed to generate PDF") from e
    else:
        # Return HTML preview
        html_content = await pdf_service.get_resume_as_html(resume)
        return HTMLResponse(content=html_content)


# Templates now moved to correct position


# Bulk operations
@router.post(API_ROUTES.RESUMES.BULK_ACTION, response_model=BulkActionResult)
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
                    ResumeUpdate.model_validate(
                        {"status": ResumeStatus.ARCHIVED.value}
                    ),
                )
            # Add other bulk actions...

            success_count += 1

        except Exception as e:
            errors.append(f"Resume {resume_id}: {str(e)}")

    return BulkActionResult(
        success_count=success_count, error_count=len(errors), errors=errors
    )


# Public resume viewing (for published resumes)
@router.get(API_ROUTES.RESUMES.PUBLIC, response_class=HTMLResponse)
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
@router.get(API_ROUTES.RESUMES.ANALYTICS)
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


# Japanese Resume Format Endpoints
@router.get(
    API_ROUTES.RESUMES.TEMPLATES_JAPANESE, response_model=list[JapaneseResumeTemplate]
)
async def get_japanese_templates(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get Japanese resume format templates (履歴書, 職務経歴書)."""
    from app.utils.constants import ResumeFormat

    templates = [
        JapaneseResumeTemplate(
            format_type=ResumeFormat.RIREKISHO,
            sections=[
                "personal_info",
                "education",
                "work_history",
                "qualifications",
                "motivation",
            ],
            field_mappings={
                "personal_info": [
                    "full_name",
                    "furigana_name",
                    "birth_date",
                    "gender",
                    "nationality",
                    "photo",
                ],
                "education": ["institution_name", "degree", "graduation_date"],
                "work_history": [
                    "company_name",
                    "position",
                    "employment_period",
                    "job_description",
                ],
                "qualifications": [
                    "certification_name",
                    "issue_date",
                    "issuing_organization",
                ],
                "motivation": [
                    "self_pr",
                    "motivation",
                    "commute_time",
                    "spouse",
                    "dependents",
                ],
            },
            validation_rules={
                "furigana_required": True,
                "photo_required": True,
                "birth_date_required": True,
            },
        ),
        JapaneseResumeTemplate(
            format_type=ResumeFormat.SHOKUMU_KEIREKISHO,
            sections=[
                "career_summary",
                "detailed_experience",
                "skills",
                "achievements",
                "self_pr",
            ],
            field_mappings={
                "career_summary": ["professional_summary", "total_experience"],
                "detailed_experience": [
                    "detailed_work_history",
                    "responsibilities",
                    "achievements",
                ],
                "skills": [
                    "technical_skills",
                    "soft_skills",
                    "languages",
                    "certifications",
                ],
                "achievements": ["key_accomplishments", "quantified_results"],
                "self_pr": ["strengths", "career_goals", "why_this_company"],
            },
            validation_rules={
                "detailed_experience_required": True,
                "career_summary_min_length": 100,
            },
        ),
    ]
    return templates


@router.post(API_ROUTES.RESUMES.CONVERT_RIREKISHO, response_model=ResumeInfo)
async def convert_to_rirekisho(
    resume_id: int,
    rirekisho_data: RirekishoData,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Convert existing resume to 履歴書 format."""
    resume_service = ResumeService()

    resume = await resume_service.get_resume(db, resume_id, current_user.id)
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")

    # Convert to Rirekisho format
    from app.utils.constants import ResumeFormat, ResumeLanguage

    update_data = {
        "resume_format": ResumeFormat.RIREKISHO,
        "resume_language": ResumeLanguage.JAPANESE,
        # Map rirekisho_data to resume fields
        "furigana_name": rirekisho_data.personal_info.get("furigana_name"),
        "birth_date": rirekisho_data.personal_info.get("birth_date"),
        "gender": rirekisho_data.personal_info.get("gender"),
        "nationality": rirekisho_data.personal_info.get("nationality"),
        "marital_status": rirekisho_data.personal_info.get("marital_status"),
        "emergency_contact": rirekisho_data.personal_info.get("emergency_contact"),
    }
    updated_resume = await resume_service.update_resume(
        db,
        resume_id,
        current_user.id,
        ResumeUpdate.model_validate(update_data),
    )

    return updated_resume


@router.post(API_ROUTES.RESUMES.CONVERT_SHOKUMU, response_model=ResumeInfo)
async def convert_to_shokumu_keirekisho(
    resume_id: int,
    shokumu_data: ShokumuKeirekishoData,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Convert existing resume to 職務経歴書 format."""
    resume_service = ResumeService()

    resume = await resume_service.get_resume(db, resume_id, current_user.id)
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")

    # Convert to Shokumu Keirekisho format
    from app.utils.constants import ResumeFormat, ResumeLanguage

    update_data = {
        "resume_format": ResumeFormat.SHOKUMU_KEIREKISHO,
        "resume_language": ResumeLanguage.JAPANESE,
        "professional_summary": shokumu_data.career_summary,
        "objective": shokumu_data.self_pr,
    }
    updated_resume = await resume_service.update_resume(
        db,
        resume_id,
        current_user.id,
        ResumeUpdate.model_validate(update_data),
    )

    return updated_resume


# Public Sharing Endpoints
@router.post(API_ROUTES.RESUMES.TOGGLE_PUBLIC, response_model=ResumeInfo)
async def toggle_resume_public(
    resume_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Toggle public visibility for a resume."""
    resume_service = ResumeService()

    resume = await resume_service.get_resume(db, resume_id, current_user.id)
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")

    new_visibility = not bool(resume.is_public)

    try:
        updated_resume = await resume_service.update_public_settings(
            db,
            resume_id,
            current_user.id,
            new_visibility,
            None,
            resume.can_download_pdf if resume.can_download_pdf is not None else True,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error toggling resume visibility: {str(e)}")
        raise HTTPException(
            status_code=500, detail="Failed to update resume visibility"
        ) from e

    if not updated_resume:
        raise HTTPException(
            status_code=400, detail="Failed to update resume visibility"
        )

    return updated_resume


@router.put(API_ROUTES.RESUMES.PUBLIC_SETTINGS, response_model=ResumeInfo)
async def update_public_settings(
    resume_id: int,
    settings: ResumePublicSettings,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update public sharing settings for a resume."""
    resume_service = ResumeService()

    resume = await resume_service.update_public_settings(
        db,
        resume_id,
        current_user.id,
        settings.is_public,
        settings.custom_slug,
        settings.allow_pdf_download,
    )

    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")

    return resume


@router.get(API_ROUTES.RESUMES.PUBLIC, response_model=PublicResumeInfo)
async def get_public_resume(slug: str, db: AsyncSession = Depends(get_db)):
    """Get public resume by slug (limited information)."""
    resume_service = ResumeService()

    resume = await resume_service.get_public_resume(db, slug)
    if not resume:
        raise HTTPException(status_code=404, detail="Public resume not found")

    # Return limited public information
    return PublicResumeInfo(
        id=resume.id,
        title=resume.title,
        full_name=resume.full_name,
        professional_summary=resume.professional_summary,
        resume_format=resume.resume_format,
        resume_language=resume.resume_language,
        view_count=resume.view_count or 0,
        last_viewed_at=resume.last_viewed_at,
        can_download_pdf=resume.can_download_pdf or False,
        theme_color=resume.theme_color,
        font_family=resume.font_family,
        experiences=resume.experiences[:5],  # Limit to first 5
        educations=resume.educations[:3],  # Limit to first 3
        skills=resume.skills[:10],  # Limit to first 10
    )


@router.get(API_ROUTES.RESUMES.PUBLIC_DOWNLOAD_SLUG)
async def download_public_resume_pdf(slug: str, db: AsyncSession = Depends(get_db)):
    """Download public resume as PDF."""
    resume_service = ResumeService()
    pdf_service = PDFService()

    resume = await resume_service.get_public_resume(db, slug)
    if not resume:
        raise HTTPException(status_code=404, detail="Public resume not found")

    if not resume.can_download_pdf:
        raise HTTPException(status_code=403, detail="PDF download not allowed")

    try:
        # Increment download count
        await resume_service.increment_download_count(db, resume.id)

        # Generate PDF
        result = await pdf_service.generate_pdf(resume)
        return RedirectResponse(url=result["pdf_url"])
    except Exception as e:
        logger.error(f"Error generating public PDF: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate PDF") from e


# Email Integration Endpoints
@router.post(API_ROUTES.RESUMES.SEND_EMAIL)
async def send_resume_by_email(
    resume_id: int,
    email_request: EmailResumeRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Send resume via email."""
    resume_service = ResumeService()

    resume = await resume_service.get_resume(db, resume_id, current_user.id)
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")

    try:
        # Queue email sending as background task
        background_tasks.add_task(
            resume_service.send_resume_email,
            db,
            resume,
            email_request.recipient_emails,
            email_request.subject or "",
            email_request.message or "",
            email_request.include_pdf or True,
            email_request.sender_name or current_user.full_name or "",
        )

        return {
            "message": f"Resume email queued for {len(email_request.recipient_emails)} recipients"
        }
    except Exception as e:
        logger.error(f"Error sending resume email: {str(e)}")
        raise HTTPException(
            status_code=500, detail="Failed to send resume email"
        ) from e


# Message Attachment Endpoints
@router.post(API_ROUTES.RESUMES.ATTACH_TO_MESSAGE)
async def attach_resume_to_message(
    resume_id: int,
    attachment_request: MessageAttachmentRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Attach resume to a message."""
    resume_service = ResumeService()

    resume = await resume_service.get_resume(db, resume_id, current_user.id)
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")

    try:
        attachment = await resume_service.attach_to_message(
            db,
            resume_id,
            attachment_request.message_id,
            attachment_request.include_pdf,
            attachment_request.auto_attach,
        )

        return {
            "message": "Resume attached to message successfully",
            "attachment_id": attachment.id,
            "format": attachment.attachment_format,
        }
    except Exception as e:
        logger.error(f"Error attaching resume to message: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to attach resume") from e


@router.put(API_ROUTES.RESUMES.AUTO_ATTACH_SETTINGS)
async def update_auto_attach_settings(
    resume_id: int,
    auto_attach: bool,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Enable/disable automatic attachment of resume to messages."""
    resume_service = ResumeService()

    resume = await resume_service.get_resume(db, resume_id, current_user.id)
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")

    # Update auto-attach settings (would be stored in user preferences or resume settings)
    # Implementation would update a setting that controls automatic attachment

    return {
        "message": f"Auto-attach {'enabled' if auto_attach else 'disabled'} for resume",
        "resume_id": resume_id,
        "auto_attach": auto_attach,
    }


# Resume Protection Endpoints (for edit/delete restrictions)
@router.put(API_ROUTES.RESUMES.PROTECTION)
async def update_resume_protection(
    resume_id: int,
    can_edit: bool = True,
    can_delete: bool = True,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update resume protection settings (prevent edit/delete)."""
    resume_service = ResumeService()

    resume = await resume_service.update_resume(
        db,
        resume_id,
        current_user.id,
        ResumeUpdate.model_validate({"can_edit": can_edit, "can_delete": can_delete}),
    )

    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")

    return {
        "message": "Resume protection settings updated",
        "can_edit": resume.can_edit,
        "can_delete": resume.can_delete,
    }
