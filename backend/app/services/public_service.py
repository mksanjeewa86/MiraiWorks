from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc, asc
from fastapi import HTTPException, status

from app.models.job import Job, JobApplication, CompanyProfile, JobStatus
from app.models.company import Company
from app.models.user import User
from app.schemas.public import (
    JobCreate, JobUpdate, JobSearchParams, CompanySearchParams,
    JobApplicationCreate, JobApplicationUpdate, CompanyProfileCreate, CompanyProfileUpdate
)
from app.utils.text_search import create_search_vector, search_jobs, search_companies
from app.services.audit_service import log_action


class PublicService:
    def __init__(self, db: Session):
        self.db = db

    def get_public_stats(self) -> Dict[str, Any]:
        """Get public statistics for landing page"""
        
        # Basic counts
        total_companies = self.db.query(Company).filter(Company.is_active == "1").count()
        total_jobs = self.db.query(Job).filter(Job.status == JobStatus.PUBLISHED).count()
        total_applications = self.db.query(JobApplication).count()

        # Featured companies (those with profiles and job postings)
        featured_companies = (
            self.db.query(Company)
            .join(CompanyProfile)
            .filter(
                Company.is_active == "1",
                CompanyProfile.is_public == True
            )
            .limit(6)
            .all()
        )

        # Latest jobs
        latest_jobs = (
            self.db.query(Job)
            .filter(Job.status == JobStatus.PUBLISHED)
            .order_by(desc(Job.published_at))
            .limit(8)
            .all()
        )

        # Job categories (job types)
        job_categories = dict(
            self.db.query(Job.job_type, func.count(Job.id))
            .filter(Job.status == JobStatus.PUBLISHED)
            .group_by(Job.job_type)
            .all()
        )

        # Location stats
        location_stats = dict(
            self.db.query(Job.country, func.count(Job.id))
            .filter(Job.status == JobStatus.PUBLISHED, Job.country.isnot(None))
            .group_by(Job.country)
            .order_by(desc(func.count(Job.id)))
            .limit(10)
            .all()
        )

        return {
            "total_companies": total_companies,
            "total_jobs": total_jobs,
            "total_applications": total_applications,
            "featured_companies": featured_companies,
            "latest_jobs": latest_jobs,
            "job_categories": job_categories,
            "location_stats": location_stats
        }

    def search_jobs(self, params: JobSearchParams) -> Dict[str, Any]:
        """Search jobs with filtering and pagination"""
        
        query = self.db.query(Job).filter(Job.status == JobStatus.PUBLISHED)
        
        # Text search
        if params.q:
            query = query.filter(
                or_(
                    Job.title.contains(params.q),
                    Job.description.contains(params.q),
                    Job.summary.contains(params.q)
                )
            )
        
        # Location filters
        if params.location:
            query = query.filter(
                or_(
                    Job.location.contains(params.location),
                    Job.city.contains(params.location),
                    Job.country.contains(params.location)
                )
            )
        
        if params.country:
            query = query.filter(Job.country == params.country)
        
        if params.city:
            query = query.filter(Job.city == params.city)
        
        if params.company_id:
            query = query.filter(Job.company_id == params.company_id)
        
        # Job type filters
        if params.job_type:
            query = query.filter(Job.job_type == params.job_type)
        
        if params.experience_level:
            query = query.filter(Job.experience_level == params.experience_level)
        
        if params.remote_type:
            query = query.filter(Job.remote_type == params.remote_type)
        
        # Salary filters
        if params.salary_min:
            query = query.filter(Job.salary_min >= params.salary_min * 100)  # Convert to cents
        
        if params.salary_max:
            query = query.filter(Job.salary_max <= params.salary_max * 100)  # Convert to cents
        
        # Skills filter (if skills are stored as JSON)
        if params.skills:
            for skill in params.skills:
                query = query.filter(
                    or_(
                        Job.required_skills.contains(skill),
                        Job.preferred_skills.contains(skill)
                    )
                )
        
        # Featured only
        if params.featured_only:
            query = query.filter(Job.is_featured == True)
        
        # Sorting
        if params.sort_by == "published_date":
            order_col = Job.published_at
        elif params.sort_by == "salary":
            order_col = Job.salary_max
        elif params.sort_by == "company":
            query = query.join(Company)
            order_col = Company.name
        else:  # relevance - default to published date
            order_col = Job.published_at
        
        if params.sort_order == "asc":
            query = query.order_by(asc(order_col))
        else:
            query = query.order_by(desc(order_col))
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        offset = (params.page - 1) * params.limit
        jobs = query.offset(offset).limit(params.limit).all()
        
        # Get available filter values
        filters = self._get_job_filters()
        
        return {
            "jobs": jobs,
            "total": total,
            "page": params.page,
            "limit": params.limit,
            "total_pages": (total + params.limit - 1) // params.limit,
            "filters": filters
        }

    def get_job_by_slug(self, slug: str) -> Job:
        """Get job by slug and increment view count"""
        job = self.db.query(Job).filter(
            Job.slug == slug,
            Job.status == JobStatus.PUBLISHED
        ).first()
        
        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job not found"
            )
        
        # Increment view count
        job.increment_view_count()
        self.db.commit()
        
        return job

    def search_companies(self, params: CompanySearchParams) -> Dict[str, Any]:
        """Search companies with public profiles"""
        
        query = (
            self.db.query(Company)
            .join(CompanyProfile)
            .filter(
                Company.is_active == "1",
                CompanyProfile.is_public == True
            )
        )
        
        # Text search
        if params.q:
            query = query.filter(
                or_(
                    Company.name.contains(params.q),
                    Company.description.contains(params.q),
                    CompanyProfile.tagline.contains(params.q)
                )
            )
        
        # Filters
        if params.location:
            query = query.filter(CompanyProfile.headquarters.contains(params.location))
        
        if params.employee_count:
            query = query.filter(CompanyProfile.employee_count == params.employee_count)
        
        if params.funding_stage:
            query = query.filter(CompanyProfile.funding_stage == params.funding_stage)
        
        # Sorting
        if params.sort_by == "name":
            order_col = Company.name
        elif params.sort_by == "founded_year":
            order_col = CompanyProfile.founded_year
        elif params.sort_by == "employee_count":
            order_col = CompanyProfile.employee_count
        else:
            order_col = Company.name
        
        if params.sort_order == "asc":
            query = query.order_by(asc(order_col))
        else:
            query = query.order_by(desc(order_col))
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        offset = (params.page - 1) * params.limit
        companies = query.offset(offset).limit(params.limit).all()
        
        return {
            "companies": companies,
            "total": total,
            "page": params.page,
            "limit": params.limit,
            "total_pages": (total + params.limit - 1) // params.limit
        }

    def get_company_by_slug(self, slug: str) -> Company:
        """Get company by slug and increment profile view count"""
        company = (
            self.db.query(Company)
            .join(CompanyProfile)
            .filter(
                or_(
                    CompanyProfile.custom_slug == slug,
                    Company.domain.like(f"{slug}.%")  # Match domain prefix
                ),
                Company.is_active == "1",
                CompanyProfile.is_public == True
            )
            .first()
        )
        
        if not company:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Company not found"
            )
        
        # Increment profile view count
        if company.profile:
            company.profile.increment_view_count()
            self.db.commit()
        
        return company

    def get_company_jobs(self, company_id: int, limit: int = 50) -> List[Job]:
        """Get active jobs for a company"""
        return (
            self.db.query(Job)
            .filter(
                Job.company_id == company_id,
                Job.status == JobStatus.PUBLISHED
            )
            .order_by(desc(Job.published_at))
            .limit(limit)
            .all()
        )

    def apply_to_job(
        self, 
        job_id: int, 
        application_data: JobApplicationCreate, 
        candidate: User
    ) -> JobApplication:
        """Submit job application"""
        
        # Get job and validate
        job = self.db.query(Job).filter(Job.id == job_id).first()
        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job not found"
            )
        
        if not job.can_apply():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Job applications are not being accepted"
            )
        
        # Check for duplicate application
        existing = self.db.query(JobApplication).filter(
            JobApplication.job_id == job_id,
            JobApplication.candidate_id == candidate.id
        ).first()
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You have already applied to this job"
            )
        
        # Create application
        application = JobApplication(
            job_id=job_id,
            candidate_id=candidate.id,
            resume_id=application_data.resume_id,
            cover_letter=application_data.cover_letter,
            application_answers=application_data.application_answers,
            source=application_data.source
        )
        
        self.db.add(application)
        
        # Update job application count
        job.application_count += 1
        
        self.db.commit()
        
        # Log action
        log_action(
            self.db,
            candidate,
            "job.apply",
            f"Applied to job '{job.title}' (ID: {job.id})",
            {"job_id": job.id, "application_id": application.id}
        )
        
        return application

    def _get_job_filters(self) -> Dict[str, Any]:
        """Get available filter values for job search"""
        
        # Get unique values for filters
        countries = [
            row[0] for row in 
            self.db.query(Job.country).filter(
                Job.status == JobStatus.PUBLISHED,
                Job.country.isnot(None)
            ).distinct().all()
        ]
        
        cities = [
            row[0] for row in 
            self.db.query(Job.city).filter(
                Job.status == JobStatus.PUBLISHED,
                Job.city.isnot(None)
            ).distinct().all()
        ]
        
        companies = (
            self.db.query(Company.id, Company.name)
            .join(Job)
            .filter(Job.status == JobStatus.PUBLISHED)
            .distinct()
            .all()
        )
        
        return {
            "countries": sorted(countries),
            "cities": sorted(cities),
            "companies": [{"id": c.id, "name": c.name} for c in companies],
            "job_types": [t.value for t in Job.job_type.type.enums],
            "experience_levels": [e.value for e in Job.experience_level.type.enums],
            "remote_types": [r.value for r in Job.remote_type.type.enums]
        }


class CompanyProfileService:
    def __init__(self, db: Session):
        self.db = db

    def get_or_create_profile(self, company_id: int, current_user: User) -> CompanyProfile:
        """Get existing profile or create new one"""
        
        profile = self.db.query(CompanyProfile).filter_by(company_id=company_id).first()
        
        if not profile:
            # Create default profile
            profile = CompanyProfile(
                company_id=company_id,
                last_updated_by=current_user.id
            )
            self.db.add(profile)
            self.db.commit()
        
        return profile

    def update_profile(
        self, 
        company_id: int, 
        update_data: CompanyProfileUpdate, 
        current_user: User
    ) -> CompanyProfile:
        """Update company profile"""
        
        profile = self.get_or_create_profile(company_id, current_user)
        
        # Apply updates
        for field, value in update_data.dict(exclude_unset=True).items():
            if hasattr(profile, field):
                setattr(profile, field, value)
        
        profile.last_updated_by = current_user.id
        self.db.commit()
        
        # Log action
        log_action(
            self.db,
            current_user,
            "company_profile.update",
            f"Updated company profile for company ID {company_id}",
            {"company_id": company_id, "updated_fields": list(update_data.dict(exclude_unset=True).keys())}
        )
        
        return profile