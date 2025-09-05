from typing import List
from typing import Optional

from fastapi import APIRouter
from fastapi import Depends
from fastapi import Query
from fastapi import Response
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.public import CompanySearchParams
from app.schemas.public import CompanySearchResponse
from app.schemas.public import JobApplicationCreate
from app.schemas.public import JobApplicationResponse
from app.schemas.public import JobResponse
from app.schemas.public import JobSearchParams
from app.schemas.public import JobSearchResponse
from app.schemas.public import JobSummary
from app.schemas.public import PublicCompany
from app.schemas.public import PublicStats
from app.services.auth_service import get_current_user
from app.services.public_service import PublicService

router = APIRouter(prefix="/public", tags=["public"])


@router.get("/stats", response_model=PublicStats)
async def get_public_stats(db: Session = Depends(get_db)):
    """Get public statistics for landing page"""
    service = PublicService(db)
    return service.get_public_stats()


@router.get("/jobs/search", response_model=JobSearchResponse)
async def search_jobs(
    q: Optional[str] = Query(None, description="Search query"),
    location: Optional[str] = Query(None, description="Location filter"),
    country: Optional[str] = Query(None, description="Country filter"),
    city: Optional[str] = Query(None, description="City filter"),
    company_id: Optional[int] = Query(None, description="Company ID filter"),
    job_type: Optional[str] = Query(None, description="Job type filter"),
    experience_level: Optional[str] = Query(None, description="Experience level filter"),
    remote_type: Optional[str] = Query(None, description="Remote type filter"),
    salary_min: Optional[int] = Query(None, description="Minimum salary filter (in currency units)"),
    salary_max: Optional[int] = Query(None, description="Maximum salary filter (in currency units)"),
    skills: Optional[List[str]] = Query(None, description="Skills filter"),
    sort_by: str = Query("published_date", description="Sort by field"),
    sort_order: str = Query("desc", description="Sort order"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    featured_only: bool = Query(False, description="Show only featured jobs"),
    db: Session = Depends(get_db)
):
    """Search jobs with filtering and pagination"""
    
    params = JobSearchParams(
        q=q,
        location=location,
        country=country,
        city=city,
        company_id=company_id,
        job_type=job_type,
        experience_level=experience_level,
        remote_type=remote_type,
        salary_min=salary_min,
        salary_max=salary_max,
        skills=skills or [],
        sort_by=sort_by,
        sort_order=sort_order,
        page=page,
        limit=limit,
        featured_only=featured_only
    )
    
    service = PublicService(db)
    result = service.search_jobs(params)
    
    return JobSearchResponse(**result)


@router.get("/jobs/{slug}", response_model=JobResponse)
async def get_job_by_slug(
    slug: str,
    db: Session = Depends(get_db)
):
    """Get job details by slug"""
    service = PublicService(db)
    job = service.get_job_by_slug(slug)
    return job


@router.post("/jobs/{job_id}/apply", response_model=JobApplicationResponse)
async def apply_to_job(
    job_id: int,
    application_data: JobApplicationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Submit job application (requires authentication)"""
    service = PublicService(db)
    application = service.apply_to_job(job_id, application_data, current_user)
    return application


@router.get("/companies/search", response_model=CompanySearchResponse)
async def search_companies(
    q: Optional[str] = Query(None, description="Search query"),
    industry: Optional[str] = Query(None, description="Industry filter"),
    location: Optional[str] = Query(None, description="Location filter"),
    employee_count: Optional[str] = Query(None, description="Employee count filter"),
    funding_stage: Optional[str] = Query(None, description="Funding stage filter"),
    sort_by: str = Query("name", description="Sort by field"),
    sort_order: str = Query("asc", description="Sort order"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db)
):
    """Search companies with public profiles"""
    
    params = CompanySearchParams(
        q=q,
        industry=industry,
        location=location,
        employee_count=employee_count,
        funding_stage=funding_stage,
        sort_by=sort_by,
        sort_order=sort_order,
        page=page,
        limit=limit
    )
    
    service = PublicService(db)
    result = service.search_companies(params)
    
    return CompanySearchResponse(**result)


@router.get("/companies/{slug}", response_model=PublicCompany)
async def get_company_by_slug(
    slug: str,
    db: Session = Depends(get_db)
):
    """Get company profile by slug"""
    service = PublicService(db)
    company = service.get_company_by_slug(slug)
    return company


@router.get("/companies/{slug}/jobs", response_model=List[JobSummary])
async def get_company_jobs(
    slug: str,
    limit: int = Query(50, ge=1, le=100, description="Number of jobs to return"),
    db: Session = Depends(get_db)
):
    """Get jobs for a specific company"""
    service = PublicService(db)
    company = service.get_company_by_slug(slug)
    jobs = service.get_company_jobs(company.id, limit)
    return jobs


@router.get("/jobs", response_model=List[JobSummary])
async def get_latest_jobs(
    limit: int = Query(10, ge=1, le=50, description="Number of jobs to return"),
    featured_only: bool = Query(False, description="Show only featured jobs"),
    db: Session = Depends(get_db)
):
    """Get latest published jobs"""
    params = JobSearchParams(
        page=1,
        limit=limit,
        featured_only=featured_only,
        sort_by="published_date",
        sort_order="desc"
    )
    
    service = PublicService(db)
    result = service.search_jobs(params)
    return result["jobs"]


@router.get("/companies", response_model=List[PublicCompany])
async def get_featured_companies(
    limit: int = Query(6, ge=1, le=20, description="Number of companies to return"),
    db: Session = Depends(get_db)
):
    """Get featured companies with public profiles"""
    params = CompanySearchParams(
        page=1,
        limit=limit,
        sort_by="name",
        sort_order="asc"
    )
    
    service = PublicService(db)
    result = service.search_companies(params)
    return result["companies"]


# SEO and metadata endpoints
@router.get("/sitemap.xml")
async def get_sitemap(db: Session = Depends(get_db)):
    """Generate XML sitemap for SEO"""
    service = PublicService(db)
    
    # Get all published jobs and public companies
    jobs = service.search_jobs(JobSearchParams(limit=1000))["jobs"]
    companies = service.search_companies(CompanySearchParams(limit=1000))["companies"]
    
    # Generate sitemap XML
    sitemap_entries = []
    
    # Add job URLs
    for job in jobs:
        sitemap_entries.append({
            "url": f"/jobs/{job.slug}",
            "lastmod": job.updated_at.isoformat(),
            "changefreq": "weekly",
            "priority": "0.8" if job.is_featured else "0.6"
        })
    
    # Add company URLs  
    for company in companies:
        sitemap_entries.append({
            "url": f"/companies/{company.profile.public_slug}",
            "lastmod": company.profile.updated_at.isoformat(),
            "changefreq": "monthly",
            "priority": "0.7"
        })
    
    # Generate XML content
    xml_content = '<?xml version="1.0" encoding="UTF-8"?>\n'
    xml_content += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    
    # Add static pages
    static_pages = [
        {"url": "/", "changefreq": "daily", "priority": "1.0"},
        {"url": "/jobs", "changefreq": "hourly", "priority": "0.9"},
        {"url": "/companies", "changefreq": "daily", "priority": "0.8"},
    ]
    
    for page in static_pages:
        xml_content += f'  <url>\n'
        xml_content += f'    <loc>https://your-domain.com{page["url"]}</loc>\n'
        xml_content += f'    <changefreq>{page["changefreq"]}</changefreq>\n'
        xml_content += f'    <priority>{page["priority"]}</priority>\n'
        xml_content += f'  </url>\n'
    
    # Add dynamic pages
    for entry in sitemap_entries:
        xml_content += f'  <url>\n'
        xml_content += f'    <loc>https://your-domain.com{entry["url"]}</loc>\n'
        xml_content += f'    <lastmod>{entry["lastmod"]}</lastmod>\n'
        xml_content += f'    <changefreq>{entry["changefreq"]}</changefreq>\n'
        xml_content += f'    <priority>{entry["priority"]}</priority>\n'
        xml_content += f'  </url>\n'
    
    xml_content += '</urlset>'
    
    return Response(content=xml_content, media_type="application/xml")


@router.get("/robots.txt")
async def get_robots_txt():
    """Generate robots.txt for SEO"""
    robots_content = """User-agent: *
Allow: /
Disallow: /admin/
Disallow: /api/
Disallow: /dashboard/

Sitemap: https://your-domain.com/public/sitemap.xml
"""
    return Response(content=robots_content, media_type="text/plain")


# RSS feeds
@router.get("/rss/jobs.xml")
async def get_jobs_rss(
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """RSS feed for latest jobs"""
    service = PublicService(db)
    
    params = JobSearchParams(
        limit=limit,
        sort_by="published_date",
        sort_order="desc"
    )
    result = service.search_jobs(params)
    jobs = result["jobs"]
    
    # Generate RSS XML
    rss_content = '<?xml version="1.0" encoding="UTF-8"?>\n'
    rss_content += '<rss version="2.0">\n'
    rss_content += '  <channel>\n'
    rss_content += '    <title>Latest Jobs - MiraiWorks</title>\n'
    rss_content += '    <description>Latest job postings from top companies</description>\n'
    rss_content += '    <link>https://your-domain.com/jobs</link>\n'
    rss_content += '    <language>en-us</language>\n'
    
    for job in jobs:
        rss_content += '    <item>\n'
        rss_content += f'      <title><![CDATA[{job.title} at {job.company_name}]]></title>\n'
        rss_content += f'      <description><![CDATA[{job.summary or ""}]]></description>\n'
        rss_content += f'      <link>https://your-domain.com/jobs/{job.slug}</link>\n'
        rss_content += f'      <guid>https://your-domain.com/jobs/{job.slug}</guid>\n'
        if job.published_at:
            rss_content += f'      <pubDate>{job.published_at.strftime("%a, %d %b %Y %H:%M:%S GMT")}</pubDate>\n'
        rss_content += '    </item>\n'
    
    rss_content += '  </channel>\n'
    rss_content += '</rss>'
    
    return Response(content=rss_content, media_type="application/xml")