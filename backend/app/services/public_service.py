from typing import Any

from fastapi import HTTPException, status
from sqlalchemy import asc, desc, func, or_
from sqlalchemy.orm import Session

from app.models.company import Company
from app.models.position import CompanyProfile, Position, PositionApplication
from app.models.user import User
from app.schemas.position import PositionStatus
from app.schemas.public import (
    CompanyProfileUpdate,
    CompanySearchParams,
    PositionApplicationCreate,
    PositionSearchParams,
)
from app.services.audit_service import log_action


class PublicService:
    def __init__(self, db: Session):
        self.db = db

    def get_public_stats(self) -> dict[str, Any]:
        """Get public statistics for landing page"""

        # Basic counts
        total_companies = (
            self.db.query(Company).filter(Company.is_active == "1").count()
        )
        total_positions = (
            self.db.query(Position)
            .filter(Position.status == PositionStatus.PUBLISHED)
            .count()
        )
        total_applications = self.db.query(PositionApplication).count()

        # Featured companies (those with profiles and position postings)
        featured_companies = (
            self.db.query(Company)
            .join(CompanyProfile)
            .filter(Company.is_active == "1", CompanyProfile.is_public)
            .limit(6)
            .all()
        )

        # Latest positions
        latest_positions = (
            self.db.query(Position)
            .filter(Position.status == PositionStatus.PUBLISHED)
            .order_by(desc(Position.published_at))
            .limit(8)
            .all()
        )

        # Position categories (position types)
        position_categories = dict(
            self.db.query(Position.position_type, func.count(Position.id))  # type: ignore
            .filter(Position.status == PositionStatus.PUBLISHED)
            .group_by(Position.position_type)  # type: ignore
            .all()
        )

        # Location stats
        location_stats = dict(  # type: ignore
            self.db.query(Position.country, func.count(Position.id))  # type: ignore
            .filter(
                Position.status == PositionStatus.PUBLISHED,
                Position.country.isnot(None),
            )
            .group_by(Position.country)
            .order_by(desc(func.count(Position.id)))
            .limit(10)
            .all()
        )

        return {
            "total_companies": total_companies,
            "total_positions": total_positions,
            "total_applications": total_applications,
            "featured_companies": featured_companies,
            "latest_positions": latest_positions,
            "position_categories": position_categories,
            "location_stats": location_stats,
        }

    def search_positions(self, params: PositionSearchParams) -> dict[str, Any]:
        """Search positions with filtering and pagination"""

        query = self.db.query(Position).filter(
            Position.status == PositionStatus.PUBLISHED
        )

        # Text search
        if params.q:
            query = query.filter(
                or_(
                    Position.title.contains(params.q),
                    Position.description.contains(params.q),
                    Position.summary.contains(params.q),
                )
            )

        # Location filters
        if params.location:
            query = query.filter(
                or_(
                    Position.location.contains(params.location),
                    Position.city.contains(params.location),
                    Position.country.contains(params.location),
                )
            )

        if params.country:
            query = query.filter(Position.country == params.country)

        if params.city:
            query = query.filter(Position.city == params.city)

        if params.company_id:
            query = query.filter(Position.company_id == params.company_id)

        # Position type filters
        if params.position_type:  # type: ignore
            query = query.filter(Position.position_type == params.position_type)  # type: ignore

        if params.experience_level:
            query = query.filter(Position.experience_level == params.experience_level)

        if params.remote_type:
            query = query.filter(Position.remote_type == params.remote_type)

        # Salary filters
        if params.salary_min:
            query = query.filter(
                Position.salary_min >= params.salary_min * 100
            )  # Convert to cents

        if params.salary_max:
            query = query.filter(
                Position.salary_max <= params.salary_max * 100
            )  # Convert to cents

        # Skills filter (if skills are stored as JSON)
        if params.skills:
            for skill in params.skills:
                query = query.filter(
                    or_(
                        Position.required_skills.contains(skill),
                        Position.preferred_skills.contains(skill),
                    )
                )

        # Featured only
        if params.featured_only:
            query = query.filter(Position.is_featured)

        # Sorting
        if params.sort_by == "published_date":
            order_col = Position.published_at
        elif params.sort_by == "salary":
            order_col = Position.salary_max
        elif params.sort_by == "company":
            query = query.join(Company)
            order_col = Company.name
        else:  # relevance - default to published date
            order_col = Position.published_at

        if params.sort_order == "asc":
            query = query.order_by(asc(order_col))
        else:
            query = query.order_by(desc(order_col))

        # Get total count
        total = query.count()

        # Apply pagination
        offset = (params.page - 1) * params.limit
        positions = query.offset(offset).limit(params.limit).all()

        # Get available filter values
        filters = self._get_position_filters()

        return {
            "positions": positions,
            "total": total,
            "page": params.page,
            "limit": params.limit,
            "total_pages": (total + params.limit - 1) // params.limit,
            "filters": filters,
        }

    def get_position_by_slug(self, slug: str) -> Position:
        """Get position by slug and increment view count"""
        position = (
            self.db.query(Position)
            .filter(Position.slug == slug, Position.status == PositionStatus.PUBLISHED)
            .first()
        )

        if not position:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Position not found"
            )

        # Increment view count
        position.increment_view_count()
        self.db.commit()

        return position

    def search_companies(self, params: CompanySearchParams) -> dict[str, Any]:
        """Search companies with public profiles"""

        query = (
            self.db.query(Company)
            .join(CompanyProfile)
            .filter(Company.is_active == "1", CompanyProfile.is_public)
        )

        # Text search
        if params.q:
            query = query.filter(
                or_(
                    Company.name.contains(params.q),
                    Company.description.contains(params.q),
                    CompanyProfile.tagline.contains(params.q),
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
            "total_pages": (total + params.limit - 1) // params.limit,
        }

    def get_company_by_slug(self, slug: str) -> Company:
        """Get company by slug and increment profile view count"""
        company = (
            self.db.query(Company)
            .join(CompanyProfile)
            .filter(
                or_(
                    CompanyProfile.custom_slug == slug,
                    Company.domain.like(f"{slug}.%"),  # Match domain prefix  # type: ignore
                ),
                Company.is_active == "1",
                CompanyProfile.is_public,
            )
            .first()
        )

        if not company:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Company not found"
            )

        # Increment profile view count
        if company.profile:
            company.profile.increment_view_count()
            self.db.commit()

        return company

    def get_company_positions(self, company_id: int, limit: int = 50) -> list[Position]:
        """Get active positions for a company"""
        return (
            self.db.query(Position)
            .filter(
                Position.company_id == company_id,
                Position.status == PositionStatus.PUBLISHED,
            )
            .order_by(desc(Position.published_at))
            .limit(limit)
            .all()
        )

    def apply_to_position(
        self,
        position_id: int,
        application_data: PositionApplicationCreate,
        candidate: User,
    ) -> PositionApplication:
        """Submit position application"""

        # Get position and validate
        position = self.db.query(Position).filter(Position.id == position_id).first()
        if not position:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Position not found"
            )

        if not position.can_apply():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Position applications are not being accepted",
            )

        # Check for duplicate application
        existing = (
            self.db.query(PositionApplication)
            .filter(
                PositionApplication.position_id == position_id,
                PositionApplication.candidate_id == candidate.id,
            )
            .first()
        )

        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You have already applied to this position",
            )

        # Create application
        application = PositionApplication(
            position_id=position_id,
            candidate_id=candidate.id,
            resume_id=application_data.resume_id,
            cover_letter=application_data.cover_letter,
            application_answers=application_data.application_answers,
            source=application_data.source,
        )

        self.db.add(application)

        # Update position application count
        position.application_count += 1

        self.db.commit()

        # Log action
        log_action(
            self.db,  # type: ignore
            candidate,  # type: ignore
            "position.apply",
            f"Applied to position '{position.title}' (ID: {position.id})",  # type: ignore
            {"position_id": position.id, "application_id": application.id},
        )

        return application

    def _get_position_filters(self) -> dict[str, Any]:
        """Get available filter values for position search"""

        # Get unique values for filters
        countries = [
            row[0]
            for row in self.db.query(Position.country)
            .filter(
                Position.status == PositionStatus.PUBLISHED,
                Position.country.isnot(None),
            )
            .distinct()
            .all()
        ]

        cities = [
            row[0]
            for row in self.db.query(Position.city)
            .filter(
                Position.status == PositionStatus.PUBLISHED, Position.city.isnot(None)
            )
            .distinct()
            .all()
        ]

        companies = (
            self.db.query(Company.id, Company.name)
            .join(Position)
            .filter(Position.status == PositionStatus.PUBLISHED)
            .distinct()
            .all()
        )

        return {
            "countries": sorted(countries),
            "cities": sorted(cities),
            "companies": [{"id": c.id, "name": c.name} for c in companies],
            "position_types": [t.value for t in Position.position_type.type.enums],  # type: ignore
            "experience_levels": [
                e.value for e in Position.experience_level.type.enums
            ],
            "remote_types": [r.value for r in Position.remote_type.type.enums],
        }


class CompanyProfileService:
    def __init__(self, db: Session):
        self.db = db

    def get_or_create_profile(
        self, company_id: int, current_user: User
    ) -> CompanyProfile:
        """Get existing profile or create new one"""

        profile = self.db.query(CompanyProfile).filter_by(company_id=company_id).first()

        if not profile:
            # Create default profile
            profile = CompanyProfile(
                company_id=company_id, last_updated_by=current_user.id
            )
            self.db.add(profile)
            self.db.commit()

        return profile

    def update_profile(
        self, company_id: int, update_data: CompanyProfileUpdate, current_user: User
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
            self.db,  # type: ignore
            current_user,  # type: ignore
            "company_profile.update",
            f"Updated company profile for company ID {company_id}",  # type: ignore
            {
                "company_id": company_id,
                "updated_fields": list(update_data.dict(exclude_unset=True).keys()),
            },
        )

        return profile
