import logging

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import PlainTextResponse, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.resume import PublicResumeInfo
from app.services.pdf_service import PDFService
from app.services.resume_service import ResumeService

router = APIRouter()
logger = logging.getLogger(__name__)

resume_service = ResumeService()
pdf_service = PDFService()


@router.get("/resume/{slug}")
async def get_public_resume_detail(
    slug: str,
    db: AsyncSession = Depends(get_db),
):
    """Fetch public resume details and HTML preview."""
    resume = await resume_service.get_public_resume(db, slug)
    if not resume:
        raise HTTPException(status_code=404, detail="Public resume not found")

    try:
        html_content = await pdf_service.get_resume_as_html(resume, resume.template_id)
    except Exception as exc:
        logger.error("Failed to render public resume preview: %s", exc)
        raise HTTPException(status_code=500, detail="Failed to render resume preview") from exc

    resume_info = PublicResumeInfo.model_validate(resume, from_attributes=True)
    return {"resume": resume_info.model_dump(), "html": html_content}


@router.post("/resume/{slug}/view")
async def track_public_resume_view(
    slug: str,
    db: AsyncSession = Depends(get_db),
):
    """Record a view for a public resume."""
    tracked = await resume_service.track_public_view(db, slug)
    if not tracked:
        raise HTTPException(status_code=404, detail="Public resume not found")
    return {"message": "View tracked"}


@router.post("/resume/{slug}/download-pdf")
async def generate_public_resume_pdf(
    slug: str,
    db: AsyncSession = Depends(get_db),
):
    """Generate and return a public resume PDF link."""
    resume = await resume_service.get_public_resume(db, slug)
    if not resume:
        raise HTTPException(status_code=404, detail="Public resume not found")

    try:
        pdf_result = await pdf_service.generate_pdf(resume)
        await resume_service.increment_download_count(db, resume.id)
    except HTTPException:
        raise
    except Exception as exc:
        logger.error("Failed to generate public resume PDF: %s", exc)
        raise HTTPException(status_code=500, detail="Failed to generate PDF") from exc

    return {"pdf_url": pdf_result.get("pdf_url")}


@router.get("/stats")
async def get_public_stats():
    """Get public platform statistics."""
    return {
        "total_positions": 0,
        "active_positions": 0,
        "total_companies": 0,
        "total_candidates": 0,
        "successful_placements": 0,
        "platform_metrics": {
            "interviews_conducted": 0,
            "applications_submitted": 0,
            "avg_time_to_hire": 0,
        },
    }


@router.get("/positions")
async def get_public_positions(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    search: str | None = Query(None),
    location: str | None = Query(None),
    category: str | None = Query(None),
):
    """Get public position listings."""
    return {
        "positions": [],
        "total": 0,
        "page": offset // limit + 1,
        "total_pages": 0,
        "has_next": False,
        "has_prev": offset > 0,
        "filters": {"search": search, "location": location, "category": category},
    }


@router.get("/positions/search")
async def search_public_positions(
    q: str = Query(..., min_length=1),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    location: str | None = Query(None),
    salary_min: int | None = Query(None),
    salary_max: int | None = Query(None),
    position_type: str | None = Query(None),
):
    """Search public position listings."""
    return {
        "results": [],
        "total": 0,
        "query": q,
        "page": offset // limit + 1,
        "total_pages": 0,
        "filters": {
            "location": location,
            "salary_range": [salary_min, salary_max]
            if salary_min or salary_max
            else None,
            "position_type": position_type,
        },
        "suggestions": [],
    }


@router.get("/companies")
async def get_public_companies(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    industry: str | None = Query(None),
    size: str | None = Query(None),
):
    """Get public company listings."""
    return {
        "companies": [],
        "total": 0,
        "page": offset // limit + 1,
        "total_pages": 0,
        "has_next": False,
        "has_prev": offset > 0,
        "filters": {"industry": industry, "size": size},
    }


@router.get("/companies/search")
async def search_public_companies(
    q: str = Query(..., min_length=1),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    industry: str | None = Query(None),
    location: str | None = Query(None),
):
    """Search public companies."""
    return {
        "results": [],
        "total": 0,
        "query": q,
        "page": offset // limit + 1,
        "total_pages": 0,
        "filters": {"industry": industry, "location": location},
        "suggestions": [],
    }


@router.get("/sitemap.xml", response_class=Response)
async def get_sitemap():
    """Generate sitemap.xml for SEO."""
    sitemap_content = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
    <url>
        <loc>http://localhost:3000/</loc>
        <changefreq>daily</changefreq>
        <priority>1.0</priority>
    </url>
    <url>
        <loc>http://localhost:3000/positions</loc>
        <changefreq>daily</changefreq>
        <priority>0.9</priority>
    </url>
    <url>
        <loc>http://localhost:3000/companies</loc>
        <changefreq>weekly</changefreq>
        <priority>0.8</priority>
    </url>
    <url>
        <loc>http://localhost:3000/about</loc>
        <changefreq>monthly</changefreq>
        <priority>0.7</priority>
    </url>
</urlset>"""

    return Response(
        content=sitemap_content,
        media_type="application/xml",
        headers={"Content-Type": "application/xml"},
    )


@router.get("/robots.txt", response_class=PlainTextResponse)
async def get_robots_txt():
    """Generate robots.txt for search engine crawlers."""
    robots_content = """User-agent: *
Allow: /
Allow: /positions
Allow: /companies
Allow: /public/*

Disallow: /admin/
Disallow: /api/
Disallow: /auth/
Disallow: /dashboard/
Disallow: /profile/
Disallow: /messages/

Sitemap: http://localhost:3000/api/public/sitemap.xml
"""

    return PlainTextResponse(
        content=robots_content, headers={"Content-Type": "text/plain"}
    )


@router.get("/rss/positions.xml", response_class=Response)
async def get_positions_rss():
    """Generate RSS feed for position listings."""
    rss_content = """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
    <channel>
        <title>MiraiWorks - Latest Positions</title>
        <link>http://localhost:3000/positions</link>
        <description>Latest position opportunities on MiraiWorks platform</description>
        <language>en-us</language>
        <lastBuildDate>Fri, 06 Sep 2025 00:00:00 GMT</lastBuildDate>
        <generator>MiraiWorks RSS Generator</generator>

        <!-- Position items would be dynamically generated here -->
        <item>
            <title>Sample Position - Software Engineer</title>
            <link>http://localhost:3000/positions/sample-position-1</link>
            <description>Sample position description for RSS feed</description>
            <pubDate>Fri, 06 Sep 2025 00:00:00 GMT</pubDate>
            <guid>http://localhost:3000/positions/sample-position-1</guid>
        </item>
    </channel>
</rss>"""

    return Response(
        content=rss_content,
        media_type="application/rss+xml",
        headers={"Content-Type": "application/rss+xml"},
    )

