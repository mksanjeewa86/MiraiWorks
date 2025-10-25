"""Profile endpoints for managing user profile information."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.endpoints import API_ROUTES
from app.crud import profile as profile_crud
from app.database import get_db
from app.dependencies import get_current_active_user
from app.models.user import User
from app.schemas.certification import (
    CertificationCreate,
    CertificationInfo,
    CertificationUpdate,
)
from app.schemas.education import EducationCreate, EducationInfo, EducationUpdate
from app.schemas.job_preference import (
    JobPreferenceCreate,
    JobPreferenceInfo,
    JobPreferenceUpdate,
)
from app.schemas.project import ProjectCreate, ProjectInfo, ProjectUpdate
from app.schemas.skill import SkillCreate, SkillInfo, SkillUpdate
from app.schemas.work_experience import (
    WorkExperienceCreate,
    WorkExperienceInfo,
    WorkExperienceUpdate,
)
from app.services.profile_service import profile_completeness_calculator

router = APIRouter()


# ================== WORK EXPERIENCE ENDPOINTS ==================


@router.get(API_ROUTES.PROFILE.WORK_EXPERIENCE, response_model=list[WorkExperienceInfo])
async def get_work_experiences(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Get all work experience entries for the current user."""
    return await profile_crud.work_experience.get_by_user(db, user_id=current_user.id)


@router.post(
    API_ROUTES.PROFILE.WORK_EXPERIENCE,
    response_model=WorkExperienceInfo,
    status_code=status.HTTP_201_CREATED,
)
async def create_work_experience(
    data: WorkExperienceCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new work experience entry."""
    return await profile_crud.work_experience.create_for_user(
        db, obj_in=data, user_id=current_user.id
    )


@router.get(API_ROUTES.PROFILE.WORK_EXPERIENCE_BY_ID, response_model=WorkExperienceInfo)
async def get_work_experience(
    experience_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Get a specific work experience entry."""
    experience = await profile_crud.work_experience.get_user_experience(
        db, id=experience_id, user_id=current_user.id
    )
    if not experience:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Work experience not found",
        )
    return experience


@router.put(API_ROUTES.PROFILE.WORK_EXPERIENCE_BY_ID, response_model=WorkExperienceInfo)
async def update_work_experience(
    experience_id: int,
    data: WorkExperienceUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Update a work experience entry."""
    experience = await profile_crud.work_experience.get_user_experience(
        db, id=experience_id, user_id=current_user.id
    )
    if not experience:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Work experience not found",
        )
    return await profile_crud.work_experience.update(db, db_obj=experience, obj_in=data)


@router.delete(
    API_ROUTES.PROFILE.WORK_EXPERIENCE_BY_ID, status_code=status.HTTP_204_NO_CONTENT
)
async def delete_work_experience(
    experience_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a work experience entry."""
    experience = await profile_crud.work_experience.get_user_experience(
        db, id=experience_id, user_id=current_user.id
    )
    if not experience:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Work experience not found",
        )
    await profile_crud.work_experience.remove(db, id=experience_id)
    return None


# ================== EDUCATION ENDPOINTS ==================


@router.get(API_ROUTES.PROFILE.EDUCATION, response_model=list[EducationInfo])
async def get_educations(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Get all education entries for the current user."""
    return await profile_crud.education.get_by_user(db, user_id=current_user.id)


@router.post(
    API_ROUTES.PROFILE.EDUCATION,
    response_model=EducationInfo,
    status_code=status.HTTP_201_CREATED,
)
async def create_education(
    data: EducationCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new education entry."""
    return await profile_crud.education.create_for_user(
        db, obj_in=data, user_id=current_user.id
    )


@router.get(API_ROUTES.PROFILE.EDUCATION_BY_ID, response_model=EducationInfo)
async def get_education(
    education_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Get a specific education entry."""
    education = await profile_crud.education.get_user_education(
        db, id=education_id, user_id=current_user.id
    )
    if not education:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Education not found",
        )
    return education


@router.put(API_ROUTES.PROFILE.EDUCATION_BY_ID, response_model=EducationInfo)
async def update_education(
    education_id: int,
    data: EducationUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Update an education entry."""
    education = await profile_crud.education.get_user_education(
        db, id=education_id, user_id=current_user.id
    )
    if not education:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Education not found",
        )
    return await profile_crud.education.update(db, db_obj=education, obj_in=data)


@router.delete(
    API_ROUTES.PROFILE.EDUCATION_BY_ID, status_code=status.HTTP_204_NO_CONTENT
)
async def delete_education(
    education_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete an education entry."""
    education = await profile_crud.education.get_user_education(
        db, id=education_id, user_id=current_user.id
    )
    if not education:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Education not found",
        )
    await profile_crud.education.remove(db, id=education_id)
    return None


# ================== SKILLS ENDPOINTS ==================


@router.get(API_ROUTES.PROFILE.SKILLS, response_model=list[SkillInfo])
async def get_skills(
    category: str | None = None,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Get all skills for the current user, optionally filtered by category."""
    if category:
        return await profile_crud.skill.get_by_category(
            db, user_id=current_user.id, category=category
        )
    return await profile_crud.skill.get_by_user(db, user_id=current_user.id)


@router.post(
    API_ROUTES.PROFILE.SKILLS,
    response_model=SkillInfo,
    status_code=status.HTTP_201_CREATED,
)
async def create_skill(
    data: SkillCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new skill entry."""
    return await profile_crud.skill.create_for_user(
        db, obj_in=data, user_id=current_user.id
    )


@router.get(API_ROUTES.PROFILE.SKILLS_BY_ID, response_model=SkillInfo)
async def get_skill(
    skill_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Get a specific skill entry."""
    skill = await profile_crud.skill.get_user_skill(
        db, id=skill_id, user_id=current_user.id
    )
    if not skill:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Skill not found",
        )
    return skill


@router.put(API_ROUTES.PROFILE.SKILLS_BY_ID, response_model=SkillInfo)
async def update_skill(
    skill_id: int,
    data: SkillUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Update a skill entry."""
    skill = await profile_crud.skill.get_user_skill(
        db, id=skill_id, user_id=current_user.id
    )
    if not skill:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Skill not found",
        )
    return await profile_crud.skill.update(db, db_obj=skill, obj_in=data)


@router.delete(API_ROUTES.PROFILE.SKILLS_BY_ID, status_code=status.HTTP_204_NO_CONTENT)
async def delete_skill(
    skill_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a skill entry."""
    skill = await profile_crud.skill.get_user_skill(
        db, id=skill_id, user_id=current_user.id
    )
    if not skill:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Skill not found",
        )
    await profile_crud.skill.remove(db, id=skill_id)
    return None


# ================== CERTIFICATIONS ENDPOINTS ==================


@router.get(API_ROUTES.PROFILE.CERTIFICATIONS, response_model=list[CertificationInfo])
async def get_certifications(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Get all certifications for the current user."""
    return await profile_crud.certification.get_by_user(db, user_id=current_user.id)


@router.post(
    API_ROUTES.PROFILE.CERTIFICATIONS,
    response_model=CertificationInfo,
    status_code=status.HTTP_201_CREATED,
)
async def create_certification(
    data: CertificationCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new certification entry."""
    return await profile_crud.certification.create_for_user(
        db, obj_in=data, user_id=current_user.id
    )


@router.get(API_ROUTES.PROFILE.CERTIFICATIONS_BY_ID, response_model=CertificationInfo)
async def get_certification(
    certification_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Get a specific certification entry."""
    certification = await profile_crud.certification.get_user_certification(
        db, id=certification_id, user_id=current_user.id
    )
    if not certification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Certification not found",
        )
    return certification


@router.put(API_ROUTES.PROFILE.CERTIFICATIONS_BY_ID, response_model=CertificationInfo)
async def update_certification(
    certification_id: int,
    data: CertificationUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Update a certification entry."""
    certification = await profile_crud.certification.get_user_certification(
        db, id=certification_id, user_id=current_user.id
    )
    if not certification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Certification not found",
        )
    return await profile_crud.certification.update(
        db, db_obj=certification, obj_in=data
    )


@router.delete(
    API_ROUTES.PROFILE.CERTIFICATIONS_BY_ID, status_code=status.HTTP_204_NO_CONTENT
)
async def delete_certification(
    certification_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a certification entry."""
    certification = await profile_crud.certification.get_user_certification(
        db, id=certification_id, user_id=current_user.id
    )
    if not certification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Certification not found",
        )
    await profile_crud.certification.remove(db, id=certification_id)
    return None


# ================== PROJECTS ENDPOINTS ==================


@router.get(API_ROUTES.PROFILE.PROJECTS, response_model=list[ProjectInfo])
async def get_projects(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Get all projects for the current user."""
    return await profile_crud.project.get_by_user(db, user_id=current_user.id)


@router.post(
    API_ROUTES.PROFILE.PROJECTS,
    response_model=ProjectInfo,
    status_code=status.HTTP_201_CREATED,
)
async def create_project(
    data: ProjectCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new project entry."""
    return await profile_crud.project.create_for_user(
        db, obj_in=data, user_id=current_user.id
    )


@router.get(API_ROUTES.PROFILE.PROJECTS_BY_ID, response_model=ProjectInfo)
async def get_project(
    project_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Get a specific project entry."""
    project = await profile_crud.project.get_user_project(
        db, id=project_id, user_id=current_user.id
    )
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )
    return project


@router.put(API_ROUTES.PROFILE.PROJECTS_BY_ID, response_model=ProjectInfo)
async def update_project(
    project_id: int,
    data: ProjectUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Update a project entry."""
    project = await profile_crud.project.get_user_project(
        db, id=project_id, user_id=current_user.id
    )
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )
    return await profile_crud.project.update(db, db_obj=project, obj_in=data)


@router.delete(
    API_ROUTES.PROFILE.PROJECTS_BY_ID, status_code=status.HTTP_204_NO_CONTENT
)
async def delete_project(
    project_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a project entry."""
    project = await profile_crud.project.get_user_project(
        db, id=project_id, user_id=current_user.id
    )
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )
    await profile_crud.project.remove(db, id=project_id)
    return None


# ================== JOB PREFERENCES ENDPOINTS ==================


@router.get(API_ROUTES.PROFILE.JOB_PREFERENCES, response_model=JobPreferenceInfo)
async def get_job_preferences(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Get job preferences for the current user."""
    return await profile_crud.job_preference.get_or_create(db, user_id=current_user.id)


@router.post(
    API_ROUTES.PROFILE.JOB_PREFERENCES,
    response_model=JobPreferenceInfo,
    status_code=status.HTTP_201_CREATED,
)
async def create_job_preferences(
    data: JobPreferenceCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Create job preferences for the current user."""
    # Check if already exists
    existing = await profile_crud.job_preference.get_by_user(
        db, user_id=current_user.id
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Job preferences already exist. Use PUT to update.",
        )
    return await profile_crud.job_preference.create_for_user(
        db, obj_in=data, user_id=current_user.id
    )


@router.put(API_ROUTES.PROFILE.JOB_PREFERENCES, response_model=JobPreferenceInfo)
async def update_job_preferences(
    data: JobPreferenceUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Update job preferences for the current user."""
    return await profile_crud.job_preference.update_for_user(
        db, user_id=current_user.id, obj_in=data
    )


# ================== PROFILE COMPLETENESS ENDPOINTS ==================


@router.get(API_ROUTES.PROFILE.COMPLETENESS)
async def get_profile_completeness(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Get profile completeness percentage and missing sections."""
    completeness = await profile_completeness_calculator.calculate_completeness(
        db, current_user
    )
    return completeness
