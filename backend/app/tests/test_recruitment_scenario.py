#!/usr/bin/env python3
"""
Simplified Recruitment Workflow Scenario Tests

This test suite validates core recruitment scenarios without Unicode characters:
1. Complete job posting to hiring workflow
2. Interview scheduling and management
3. Multiple position handling
"""

import pytest
from datetime import datetime, timedelta
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models import *  # Import all models
from app.services.auth_service import auth_service
from app.utils.constants import UserRole as UserRoleEnum


@pytest.mark.asyncio
async def test_basic_recruitment_flow(client: AsyncClient, db_session: AsyncSession):
    """Test basic recruitment workflow from job creation to completion."""

    print("\n[TEST] Starting Basic Recruitment Flow Test")
    print("=" * 60)

    # Setup test data
    print("[SETUP] Creating test environment...")

    # Create roles
    roles = {}
    for role_name in UserRoleEnum:
        role = Role(name=role_name.value, description=f"Test {role_name.value} role")
        db_session.add(role)
        roles[role_name.value] = role
    await db_session.commit()

    for role in roles.values():
        await db_session.refresh(role)

    # Create company
    company = Company(
        name="Test Recruitment Company",
        email="hr@testrecruit.com",
        phone="03-1234-5678",
        type="employer"
    )
    db_session.add(company)
    await db_session.commit()
    await db_session.refresh(company)

    # Create HR manager
    hr_manager = User(
        email='hr@testrecruit.com',
        first_name='HR',
        last_name='Manager',
        company_id=company.id,
        hashed_password=auth_service.get_password_hash('hrtest123'),
        is_active=True,
        is_admin=True,
        require_2fa=False,
    )
    db_session.add(hr_manager)
    await db_session.commit()
    await db_session.refresh(hr_manager)

    # Assign HR role
    hr_role = UserRole(user_id=hr_manager.id, role_id=roles[UserRoleEnum.COMPANY_ADMIN.value].id)
    db_session.add(hr_role)

    # Create candidate
    candidate = User(
        email='candidate@test.com',
        first_name='Test',
        last_name='Candidate',
        hashed_password=auth_service.get_password_hash('candidate123'),
        is_active=True,
        is_admin=False,
        require_2fa=False,
    )
    db_session.add(candidate)
    await db_session.commit()
    await db_session.refresh(candidate)

    # Assign candidate role
    candidate_role = UserRole(user_id=candidate.id, role_id=roles[UserRoleEnum.CANDIDATE.value].id)
    db_session.add(candidate_role)
    await db_session.commit()

    print(f"[SETUP] Created company: {company.name}")
    print(f"[SETUP] Created HR manager: {hr_manager.email}")
    print(f"[SETUP] Created candidate: {candidate.email}")

    # Authenticate HR manager
    print("\n[AUTH] Authenticating HR manager...")
    login_response = await client.post(
        "/api/auth/login",
        json={"email": "hr@testrecruit.com", "password": "hrtest123"},
    )
    assert login_response.status_code == 200
    login_data = login_response.json()

    # Handle 2FA if required
    if login_data.get("require_2fa"):
        print("[AUTH] 2FA required, verifying...")
        verify_response = await client.post(
            "/api/auth/2fa/verify",
            json={"user_id": hr_manager.id, "code": "123456"}
        )
        assert verify_response.status_code == 200
        login_data = verify_response.json()

    hr_token = login_data['access_token']
    hr_headers = {"Authorization": f"Bearer {hr_token}"}
    print("[AUTH] HR manager authenticated successfully")

    # SCENARIO 1: Job Creation and Publication
    print("\n[JOB] Creating and publishing job posting...")

    job_data = {
        "title": "Software Developer",
        "description": "Exciting software development opportunity with modern technologies",
        "requirements": "Programming experience required",
        "location": "Tokyo, Japan",
        "job_type": "full_time",
        "salary_min": 5000000,
        "salary_max": 8000000,
        "company_id": company.id,
        "application_deadline": (datetime.now() + timedelta(days=30)).isoformat()
    }

    create_job_response = await client.post(
        "/api/jobs/",
        json=job_data,
        headers=hr_headers
    )

    if create_job_response.status_code != 201:
        print(f"[ERROR] Job creation failed with status {create_job_response.status_code}")
        print(f"[ERROR] Response: {create_job_response.json()}")

    assert create_job_response.status_code == 201
    job = create_job_response.json()
    job_id = job['id']
    print(f"[JOB] Created job posting: {job['title']} (ID: {job_id})")

    # Publish the job
    update_response = await client.put(
        f"/api/jobs/{job_id}",
        json={"status": "published"},
        headers=hr_headers
    )
    assert update_response.status_code == 200
    updated_job = update_response.json()
    assert updated_job['status'] == 'published'
    print(f"[JOB] Published job posting successfully")

    # Verify job appears in listings
    jobs_response = await client.get("/api/jobs/")
    assert jobs_response.status_code == 200
    jobs_list = jobs_response.json()
    job_ids = [j['id'] for j in jobs_list['jobs']]
    assert job_id in job_ids
    print(f"[JOB] Job appears in public listings")

    # SCENARIO 2: Interview Scheduling
    print("\n[INTERVIEW] Scheduling candidate interview...")

    interview_data = {
        "title": f"Interview - {candidate.first_name} {candidate.last_name}",
        "description": "Technical interview for software developer position",
        "interview_type": "video",  # Changed from "technical" to valid type
        "recruiter_id": hr_manager.id,  # Changed from interviewer_id
        "candidate_id": candidate.id,
        "employer_company_id": company.id  # Added required field
    }

    interview_response = await client.post(
        "/api/interviews/",
        json=interview_data,
        headers=hr_headers
    )
    assert interview_response.status_code == 201
    interview = interview_response.json()
    interview_id = interview['id']
    print(f"[INTERVIEW] Scheduled interview (ID: {interview_id})")

    # Complete the interview
    complete_response = await client.put(
        f"/api/interviews/{interview_id}",
        json={
            "status": "completed",
            "notes": "Good technical skills, proceed with hiring"
        },
        headers=hr_headers
    )
    assert complete_response.status_code == 200
    completed_interview = complete_response.json()
    assert completed_interview['status'] == 'completed'
    print(f"[INTERVIEW] Completed interview with positive outcome")

    # SCENARIO 3: Hiring Decision
    print("\n[HIRING] Making hiring decision...")

    # Fill the job position
    fill_job_response = await client.put(
        f"/api/jobs/{job_id}",
        json={"status": "filled"},
        headers=hr_headers
    )
    assert fill_job_response.status_code == 200
    filled_job = fill_job_response.json()
    assert filled_job['status'] == 'filled'
    print(f"[HIRING] Job marked as filled")

    # VERIFICATION
    print("\n[VERIFY] Verifying workflow completion...")

    # Check final job status
    final_job_response = await client.get(f"/api/jobs/{job_id}")
    assert final_job_response.status_code == 200
    final_job = final_job_response.json()
    assert final_job['status'] == 'filled'

    # Check interview status
    final_interview_response = await client.get("/api/interviews/", headers=hr_headers)
    assert final_interview_response.status_code == 200
    interviews = final_interview_response.json()
    completed_interviews = [i for i in interviews if i['status'] == 'completed']
    assert len(completed_interviews) >= 1

    print("[VERIFY] All workflow steps completed successfully")
    print("[SUCCESS] Basic recruitment workflow test passed!")

    # Print summary
    print("\n[SUMMARY] Workflow Results:")
    print(f"  - Job Created: {final_job['title']}")
    print(f"  - Job Status: {final_job['status']}")
    print(f"  - Interviews Completed: {len(completed_interviews)}")
    print(f"  - Candidate Hired: {candidate.first_name} {candidate.last_name}")


@pytest.mark.asyncio
async def test_multi_job_workflow(client: AsyncClient, db_session: AsyncSession):
    """Test workflow with multiple job positions."""

    print("\n[TEST] Starting Multi-Job Workflow Test")
    print("=" * 60)

    # Quick setup
    roles = {}
    for role_name in UserRoleEnum:
        role = Role(name=role_name.value, description=f"Test {role_name.value} role")
        db_session.add(role)
        roles[role_name.value] = role
    await db_session.commit()

    for role in roles.values():
        await db_session.refresh(role)

    company = Company(
        name="Multi Job Company",
        email="multijob@test.com",
        phone="03-9999-8888",
        type="employer"
    )
    db_session.add(company)
    await db_session.commit()
    await db_session.refresh(company)

    admin = User(
        email='admin@multijob.com',
        first_name='Multi',
        last_name='Admin',
        company_id=company.id,
        hashed_password=auth_service.get_password_hash('multiadmin123'),
        is_active=True,
        is_admin=True,
        require_2fa=False,
    )
    db_session.add(admin)
    await db_session.commit()
    await db_session.refresh(admin)

    admin_role = UserRole(user_id=admin.id, role_id=roles[UserRoleEnum.COMPANY_ADMIN.value].id)
    db_session.add(admin_role)
    await db_session.commit()

    # Authenticate
    login_response = await client.post(
        "/api/auth/login",
        json={"email": "admin@multijob.com", "password": "multiadmin123"},
    )
    assert login_response.status_code == 200
    login_data = login_response.json()

    # Handle 2FA if required
    if login_data.get("require_2fa"):
        verify_response = await client.post(
            "/api/auth/2fa/verify",
            json={"user_id": admin.id, "code": "123456"}
        )
        assert verify_response.status_code == 200
        login_data = verify_response.json()

    token = login_data['access_token']
    headers = {"Authorization": f"Bearer {token}"}

    print("[SETUP] Multi-job test environment ready")

    # Create multiple job positions
    print("\n[JOBS] Creating multiple job positions...")

    job_titles = [
        "Frontend Developer",
        "Backend Engineer",
        "DevOps Specialist"
    ]

    created_jobs = []
    for i, title in enumerate(job_titles):
        job_data = {
            "title": title,
            "description": f"Opportunity for {title.lower()} role",
            "requirements": f"Skills needed for {title.lower()}",
            "location": "Tokyo, Japan",
            "job_type": "full_time",
            "salary_min": 5000000 + (i * 1000000),
            "salary_max": 8000000 + (i * 1000000),
            "company_id": company.id,
            "application_deadline": (datetime.now() + timedelta(days=30 - i*5)).isoformat()
        }

        response = await client.post("/api/jobs/", json=job_data, headers=headers)
        assert response.status_code == 201
        job = response.json()

        # Publish the job so it appears in search results
        publish_response = await client.put(
            f"/api/jobs/{job['id']}",
            json={"status": "published"},
            headers=headers
        )
        assert publish_response.status_code == 200

        created_jobs.append(job)
        print(f"[JOBS] Created and published: {job['title']} (ID: {job['id']})")

    # Test company jobs endpoint
    company_jobs_response = await client.get(
        f"/api/jobs/company/{company.id}",
        headers=headers
    )
    assert company_jobs_response.status_code == 200
    company_jobs = company_jobs_response.json()
    assert len(company_jobs) == len(created_jobs)
    print(f"[JOBS] Company has {len(company_jobs)} active positions")

    # Test job search
    search_response = await client.get(
        "/api/jobs/search",
        params={"query": "Developer"}
    )
    assert search_response.status_code == 200
    search_results = search_response.json()

    # Search endpoint returns List[JobInfo] directly
    developer_jobs = [job for job in search_results if "Developer" in job['title']]
    assert len(developer_jobs) >= 1
    print(f"[SEARCH] Found {len(developer_jobs)} developer positions")

    # Test job statistics
    stats_response = await client.get("/api/jobs/statistics", headers=headers)
    assert stats_response.status_code == 200
    stats = stats_response.json()
    print(f"[STATS] Job statistics retrieved: {stats}")

    print("[SUCCESS] Multi-job workflow test passed!")


@pytest.mark.asyncio
async def test_interview_management_workflow(client: AsyncClient, db_session: AsyncSession):
    """Test interview management and scheduling workflow."""

    print("\n[TEST] Starting Interview Management Workflow Test")
    print("=" * 60)

    # Setup
    roles = {}
    for role_name in UserRoleEnum:
        role = Role(name=role_name.value, description=f"Test {role_name.value} role")
        db_session.add(role)
        roles[role_name.value] = role
    await db_session.commit()

    for role in roles.values():
        await db_session.refresh(role)

    company = Company(
        name="Interview Test Company",
        email="interview@test.com",
        phone="03-7777-8888",
        type="employer"
    )
    db_session.add(company)
    await db_session.commit()
    await db_session.refresh(company)

    interviewer = User(
        email='interviewer@test.com',
        first_name='Interview',
        last_name='Manager',
        company_id=company.id,
        hashed_password=auth_service.get_password_hash('interview123'),
        is_active=True,
        is_admin=True,
        require_2fa=False,
    )
    db_session.add(interviewer)
    await db_session.commit()
    await db_session.refresh(interviewer)

    interviewer_role = UserRole(user_id=interviewer.id, role_id=roles[UserRoleEnum.COMPANY_ADMIN.value].id)
    db_session.add(interviewer_role)

    candidate = User(
        email='interviewee@test.com',
        first_name='Interview',
        last_name='Candidate',
        hashed_password=auth_service.get_password_hash('candidate123'),
        is_active=True,
        is_admin=False,
        require_2fa=False,
    )
    db_session.add(candidate)
    await db_session.commit()
    await db_session.refresh(candidate)

    candidate_role = UserRole(user_id=candidate.id, role_id=roles[UserRoleEnum.CANDIDATE.value].id)
    db_session.add(candidate_role)
    await db_session.commit()

    # Authenticate
    login_response = await client.post(
        "/api/auth/login",
        json={"email": "interviewer@test.com", "password": "interview123"},
    )
    assert login_response.status_code == 200
    login_data = login_response.json()

    # Handle 2FA if required
    if login_data.get("require_2fa"):
        verify_response = await client.post(
            "/api/auth/2fa/verify",
            json={"user_id": interviewer.id, "code": "123456"}
        )
        assert verify_response.status_code == 200
        login_data = verify_response.json()

    token = login_data['access_token']
    headers = {"Authorization": f"Bearer {token}"}

    print("[SETUP] Interview management test environment ready")

    # Test interview lifecycle
    print("\n[INTERVIEW] Testing interview lifecycle...")

    # Create interview
    interview_data = {
        "title": "Technical Assessment",
        "description": "Technical interview for software position",
        "interview_type": "technical",
        "recruiter_id": interviewer.id,
        "candidate_id": candidate.id,
        "employer_company_id": company.id
    }

    create_response = await client.post("/api/interviews/", json=interview_data, headers=headers)
    if create_response.status_code != 201:
        print(f"[ERROR] Interview creation failed: {create_response.status_code}")
        print(f"[ERROR] Response: {create_response.json()}")
    assert create_response.status_code == 201
    interview = create_response.json()
    interview_id = interview['id']
    print(f"[INTERVIEW] Created interview (ID: {interview_id})")

    # Reschedule interview
    reschedule_data = {
        "scheduled_start": (datetime.now() + timedelta(days=2)).isoformat(),
        "scheduled_end": (datetime.now() + timedelta(days=2, hours=1)).isoformat(),
        "notes": "Rescheduled due to availability"
    }

    reschedule_response = await client.put(
        f"/api/interviews/{interview_id}",
        json=reschedule_data,
        headers=headers
    )
    assert reschedule_response.status_code == 200
    print("[INTERVIEW] Successfully rescheduled interview")

    # Progress through interview stages
    status_updates = [
        {"status": "in_progress", "notes": "Interview started"},
        {"status": "completed", "notes": "Interview completed successfully"}
    ]

    for update in status_updates:
        update_response = await client.put(
            f"/api/interviews/{interview_id}",
            json=update,
            headers=headers
        )
        assert update_response.status_code == 200
        print(f"[INTERVIEW] Updated status to: {update['status']}")

    # Verify final state
    final_response = await client.get("/api/interviews", headers=headers)
    assert final_response.status_code == 200
    interviews = final_response.json()

    completed_interviews = [i for i in interviews if i['status'] == 'completed']
    assert len(completed_interviews) >= 1
    print(f"[INTERVIEW] Found {len(completed_interviews)} completed interviews")

    print("[SUCCESS] Interview management workflow test passed!")


if __name__ == "__main__":
    print("Run these tests with:")
    print("pytest test_recruitment_scenario.py -v -s")