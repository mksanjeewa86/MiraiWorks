
"""Targeted recruitment workflow integration tests."""

import pytest
from uuid import uuid4

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.job import Job
from app.models.user import User


async def create_job(
    client: AsyncClient,
    headers: dict,
    *,
    title: str,
    company_id: int,
) -> dict:
    payload = {
        "title": title,
        "description": "Job description",
        "requirements": "Requirements",
        "location": "Remote",
        "job_type": "full_time",
        "company_id": company_id,
    }
    response = await client.post("/api/jobs", json=payload, headers=headers)
    assert response.status_code == 201
    return response.json()


@pytest.mark.asyncio
async def test_job_statistics_endpoint(
    client: AsyncClient,
    auth_headers: dict,
    admin_auth_headers: dict,
    test_employer_user: User,
):
    job = await create_job(
        client,
        auth_headers,
        title=f"Platform Engineer {uuid4().hex[:4]}",
        company_id=test_employer_user.company_id,
    )

    await client.patch(
        f"/api/jobs/{job['id']}/status",
        json={"status": "published"},
        headers=auth_headers,
    )

    stats_response = await client.get("/api/jobs/statistics", headers=admin_auth_headers)
    assert stats_response.status_code == 200
    data = stats_response.json()
    assert data["total_jobs"] >= 1


@pytest.mark.asyncio
async def test_job_search_returns_matching_titles(
    client: AsyncClient,
    auth_headers: dict,
    test_employer_user: User,
):
    job = await create_job(
        client,
        auth_headers,
        title="Data Scientist",
        company_id=test_employer_user.company_id,
    )

    await client.patch(
        f"/api/jobs/{job['id']}/status",
        json={"status": "published"},
        headers=auth_headers,
    )

    search_response = await client.get(
        "/api/jobs/search",
        params={"query": "Data"},
    )
    assert search_response.status_code == 200
    jobs = search_response.json()["jobs"]
    assert any("Data Scientist" in job_info["title"] for job_info in jobs)


@pytest.mark.asyncio
async def test_employer_updates_job_details(
    client: AsyncClient,
    auth_headers: dict,
    db_session: AsyncSession,
    test_employer_user: User,
):
    job = await create_job(
        client,
        auth_headers,
        title="QA Specialist",
        company_id=test_employer_user.company_id,
    )

    update_payload = {"summary": "Quality assurance specialist", "status": "published"}
    response = await client.put(
        f"/api/jobs/{job['id']}",
        json=update_payload,
        headers=auth_headers,
    )

    assert response.status_code == 200
    result = await db_session.execute(select(Job).where(Job.id == job["id"]))
    stored = result.scalar_one()
    assert stored.summary == "Quality assurance specialist"
