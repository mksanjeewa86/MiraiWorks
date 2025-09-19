from typing import Any, List, Optional
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_active_user
from app.models.job import Job
from app.crud.job import job as job_crud
from app.models.user import User
from app.schemas.job import (
    JobCreate,
    JobInfo,
    JobUpdate,
    JobListResponse,
    JobStatsResponse
)

router = APIRouter()


@router.post("/", response_model=JobInfo, status_code=status.HTTP_201_CREATED)
async def create_job(
    *,
    db: AsyncSession = Depends(get_db),
    job_in: JobCreate,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Create new job posting.
    """
    # Check if user can create jobs
    if not current_user.is_admin and not current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to create job postings"
        )

    # If user is not admin, ensure they can only create jobs for their company
    if not current_user.is_admin and current_user.company_id:
        if job_in.company_id != current_user.company_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Can only create jobs for your own company"
            )

    # Add posted_by field from current user
    job_data = job_in.model_dump()
    job_data['posted_by'] = current_user.id

    job = await job_crud.create_with_slug(db=db, obj_in=JobCreate(**job_data))
    return job


@router.get("/", response_model=JobListResponse)
async def list_jobs(
    db: AsyncSession = Depends(get_db),
    skip: int = Query(0, ge=0, description="Number of jobs to skip"),
    limit: int = Query(100, ge=1, le=500, description="Number of jobs to return"),
    location: Optional[str] = Query(None, description="Filter by location"),
    job_type: Optional[str] = Query(None, description="Filter by job type"),
    salary_min: Optional[int] = Query(None, ge=0, description="Minimum salary filter"),
    salary_max: Optional[int] = Query(None, ge=0, description="Maximum salary filter"),
    company_id: Optional[int] = Query(None, description="Filter by company"),
    search: Optional[str] = Query(None, description="Search in title, description, requirements"),
    status: Optional[str] = Query("published", description="Job status filter")
) -> Any:
    """
    Retrieve jobs with optional filtering.
    """
    if status == "published":
        jobs = await job_crud.get_published_jobs(
            db=db,
            skip=skip,
            limit=limit,
            location=location,
            job_type=job_type,
            salary_min=salary_min,
            salary_max=salary_max,
            company_id=company_id,
            search=search
        )
    else:
        jobs = await job_crud.get_jobs_by_status(
            db=db,
            status=status,
            skip=skip,
            limit=limit
        )

    return JobListResponse(
        jobs=jobs,
        total=len(jobs),
        skip=skip,
        limit=limit
    )


@router.get("/search", response_model=List[JobInfo])
async def search_jobs(
    *,
    db: AsyncSession = Depends(get_db),
    query: Optional[str] = Query(None, description="Search query"),
    location: Optional[str] = Query(None, description="Location filter"),
    job_type: Optional[str] = Query(None, description="Job type filter"),
    salary_min: Optional[int] = Query(None, description="Minimum salary"),
    salary_max: Optional[int] = Query(None, description="Maximum salary"),
    company_id: Optional[int] = Query(None, description="Company ID filter"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500)
) -> Any:
    """
    Advanced job search with multiple criteria.
    """
    jobs = await job_crud.get_published_jobs(
        db=db,
        skip=skip,
        limit=limit,
        location=location,
        job_type=job_type,
        salary_min=salary_min,
        salary_max=salary_max,
        company_id=company_id,
        search=query
    )

    return jobs


@router.get("/popular", response_model=List[JobInfo])
async def get_popular_jobs(
    db: AsyncSession = Depends(get_db),
    limit: int = Query(10, ge=1, le=50, description="Number of popular jobs to return")
) -> Any:
    """
    Get most popular jobs by view count.
    """
    jobs = await job_crud.get_popular_jobs(db=db, limit=limit)
    return jobs


@router.get("/recent", response_model=List[JobInfo])
async def get_recent_jobs(
    db: AsyncSession = Depends(get_db),
    days: int = Query(7, ge=1, le=30, description="Jobs posted in the last N days"),
    limit: int = Query(100, ge=1, le=500)
) -> Any:
    """
    Get recently posted jobs.
    """
    jobs = await job_crud.get_recent_jobs(db=db, days=days, limit=limit)
    return jobs


@router.get("/expiring", response_model=List[JobInfo])
async def get_expiring_jobs(
    db: AsyncSession = Depends(get_db),
    days: int = Query(7, ge=1, le=30, description="Jobs expiring in the next N days"),
    limit: int = Query(100, ge=1, le=500),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Get jobs expiring soon (admin/employer only).
    """
    if not current_user.is_admin and not current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to view expiring jobs"
        )

    jobs = await job_crud.get_jobs_expiring_soon(db=db, days=days, limit=limit)
    return jobs


@router.get("/statistics", response_model=JobStatsResponse)
async def get_job_statistics(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Get job posting statistics (admin only).
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )

    stats = await job_crud.get_job_statistics(db=db)
    return JobStatsResponse(**stats)


@router.get("/company/{company_id}", response_model=List[JobInfo])
async def get_company_jobs(
    *,
    db: AsyncSession = Depends(get_db),
    company_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Get jobs for a specific company.
    """
    # Employers can only see their own company's jobs
    if not current_user.is_admin and current_user.company_id != company_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Can only view jobs for your own company"
        )

    jobs = await job_crud.get_by_company(
        db=db,
        company_id=company_id,
        skip=skip,
        limit=limit
    )
    return jobs


@router.get("/{job_id}", response_model=JobInfo)
async def get_job(
    *,
    db: AsyncSession = Depends(get_db),
    job_id: int
) -> Any:
    """
    Get job by ID and increment view count.
    """
    job = await job_crud.get(db=db, id=job_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )

    # Increment view count for published jobs
    if job.status == "published":
        job = await job_crud.increment_view_count(db=db, job_id=job_id)

    return job


@router.get("/slug/{slug}", response_model=JobInfo)
async def get_job_by_slug(
    *,
    db: AsyncSession = Depends(get_db),
    slug: str
) -> Any:
    """
    Get job by slug and increment view count.
    """
    job = await job_crud.get_by_slug(db=db, slug=slug)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )

    # Increment view count for published jobs
    if job.status == "published":
        job = await job_crud.increment_view_count(db=db, job_id=job.id)

    return job


@router.put("/{job_id}", response_model=JobInfo)
async def update_job(
    *,
    db: AsyncSession = Depends(get_db),
    job_id: int,
    job_in: JobUpdate,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Update job posting.
    """
    job = await job_crud.get(db=db, id=job_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )

    # Check permissions
    if not current_user.is_admin:
        if current_user.company_id != job.company_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Can only update jobs for your own company"
            )

    job = await job_crud.update(db=db, db_obj=job, obj_in=job_in)
    return job




@router.delete("/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_job(
    *,
    db: AsyncSession = Depends(get_db),
    job_id: int,
    current_user: User = Depends(get_current_active_user)
):
    """
    Delete job posting (admin only).
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can delete job postings"
        )

    job = await job_crud.get(db=db, id=job_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )

    await job_crud.remove(db=db, id=job_id)