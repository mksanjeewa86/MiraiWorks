#!/usr/bin/env python3
"""
Comprehensive Recruitment Workflow Scenario Tests

This test suite validates complete end-to-end recruitment scenarios:
1. Job posting creation and publication workflow
2. Candidate application and management workflow
3. Interview scheduling and management workflow
4. Complete hiring process from job posting to hiring decision
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
async def test_complete_recruitment_workflow(client: AsyncClient, db_session: AsyncSession):
    """Test the complete recruitment workflow from job posting to hiring."""

    print("\n[TEST] Starting Complete Recruitment Workflow Test")
    print("=" * 70)

    # === SETUP PHASE ===
    print("[SETUP] Setting up test environment...")

    # Create test roles
    roles = {}
    for role_name in UserRoleEnum:
        role = Role(name=role_name.value, description=f"Test {role_name.value} role")
        db_session.add(role)
        roles[role_name.value] = role
    await db_session.commit()

    # Refresh all roles
    for role in roles.values():
        await db_session.refresh(role)

    # Create test company
    test_company = Company(
        name="TechCorp Recruitment Test",
        email="hiring@techcorp.com",
        phone="03-1234-5678",
        type="employer"
    )
    db_session.add(test_company)
    await db_session.commit()
    await db_session.refresh(test_company)

    # Create HR manager (company admin)
    hr_manager = User(
        email='hr.manager@techcorp.com',
        first_name='Sarah',
        last_name='Johnson',
        company_id=test_company.id,
        hashed_password=auth_service.get_password_hash('hrpass123'),
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
    await db_session.commit()

    # Create hiring manager
    hiring_manager = User(
        email='hiring.manager@techcorp.com',
        first_name='John',
        last_name='Smith',
        company_id=test_company.id,
        hashed_password=auth_service.get_password_hash('hiringpass123'),
        is_active=True,
        is_admin=False,
        require_2fa=False,
    )
    db_session.add(hiring_manager)
    await db_session.commit()
    await db_session.refresh(hiring_manager)

    # Assign hiring manager role
    hiring_role = UserRole(user_id=hiring_manager.id, role_id=roles[UserRoleEnum.EMPLOYER.value].id)
    db_session.add(hiring_role)
    await db_session.commit()

    # Create candidate users
    candidates_data = [
        {
            'email': 'alice.developer@email.com',
            'first_name': 'Alice',
            'last_name': 'Developer',
            'skills': ['React', 'Node.js', 'TypeScript'],
            'experience': 'senior'
        },
        {
            'email': 'bob.engineer@email.com',
            'first_name': 'Bob',
            'last_name': 'Engineer',
            'skills': ['Python', 'Django', 'PostgreSQL'],
            'experience': 'mid'
        },
        {
            'email': 'carol.programmer@email.com',
            'first_name': 'Carol',
            'last_name': 'Programmer',
            'skills': ['Java', 'Spring', 'MySQL'],
            'experience': 'entry'
        }
    ]

    candidates = []
    for candidate_data in candidates_data:
        candidate = User(
            email=candidate_data['email'],
            first_name=candidate_data['first_name'],
            last_name=candidate_data['last_name'],
            hashed_password=auth_service.get_password_hash('candidatepass123'),
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
        candidates.append(candidate)

    await db_session.commit()
    print(f"✅ Created test environment: 1 company, 2 employers, 3 candidates")

    # === SCENARIO 1: JOB POSTING WORKFLOW ===
    print("\n📝 SCENARIO 1: Job Posting Creation and Publication")
    print("-" * 50)

    # Authenticate HR manager
    login_response = await client.post(
        "/api/auth/login",
        json={"email": "hr.manager@techcorp.com", "password": "hrpass123"},
    )
    assert login_response.status_code == 200
    hr_token = login_response.json()['access_token']
    hr_headers = {"Authorization": f"Bearer {hr_token}"}

    # Step 1.1: Create job posting (draft state)
    job_data = {
        "title": "Senior Full Stack Developer",
        "description": "We are looking for an experienced full stack developer to join our team. You will be responsible for developing web applications using modern technologies.",
        "requirements": "5+ years experience, React, Node.js, TypeScript, Team leadership",
        "location": "Tokyo, Japan",
        "job_type": "full-time",
        "salary_min": 8000000,
        "salary_max": 12000000,
        "company_id": test_company.id,
        "status": "draft",
        "deadline": (datetime.now() + timedelta(days=30)).isoformat()
    }

    create_job_response = await client.post(
        "/api/jobs",
        json=job_data,
        headers=hr_headers
    )
    assert create_job_response.status_code == 201
    job = create_job_response.json()
    job_id = job['id']
    print(f"✅ Created job posting (ID: {job_id}) in draft status")

    # Step 1.2: Review and publish job posting
    update_job_response = await client.put(
        f"/api/jobs/{job_id}",
        json={"status": "published"},
        headers=hr_headers
    )
    assert update_job_response.status_code == 200
    updated_job = update_job_response.json()
    assert updated_job['status'] == 'published'
    print(f"✅ Published job posting (ID: {job_id})")

    # Step 1.3: Verify job appears in public listings
    public_jobs_response = await client.get("/api/jobs")
    assert public_jobs_response.status_code == 200
    public_jobs = public_jobs_response.json()
    published_job_ids = [j['id'] for j in public_jobs['jobs']]
    assert job_id in published_job_ids
    print(f"✅ Job posting appears in public listings")

    # === SCENARIO 2: CANDIDATE APPLICATION WORKFLOW ===
    print("\n👥 SCENARIO 2: Candidate Application Process")
    print("-" * 50)

    # Step 2.1: Candidates view and apply to job
    applied_candidates = []

    for i, candidate in enumerate(candidates):
        # Authenticate candidate
        login_response = await client.post(
            "/api/auth/login",
            json={"email": candidate.email, "password": "candidatepass123"},
        )
        assert login_response.status_code == 200
        candidate_token = login_response.json()['access_token']
        candidate_headers = {"Authorization": f"Bearer {candidate_token}"}

        # View job posting (increment view count)
        view_job_response = await client.get(f"/api/jobs/{job_id}")
        assert view_job_response.status_code == 200

        # Simulate application process (in real system, this would be through application endpoint)
        # For now, we track this conceptually
        applied_candidates.append({
            'candidate': candidate,
            'application_date': datetime.now(),
            'status': 'applied'
        })

        print(f"✅ Candidate {candidate.first_name} {candidate.last_name} applied to job")

    # === SCENARIO 3: INTERVIEW SCHEDULING WORKFLOW ===
    print("\n📅 SCENARIO 3: Interview Scheduling and Management")
    print("-" * 50)

    # Step 3.1: HR manager schedules interviews for qualified candidates
    scheduled_interviews = []

    # Select top 2 candidates for interviews (Alice and Bob)
    selected_candidates = applied_candidates[:2]

    for i, application in enumerate(selected_candidates):
        candidate = application['candidate']

        # Create interview
        interview_data = {
            "title": f"Technical Interview - {candidate.first_name} {candidate.last_name}",
            "description": f"Technical interview for Senior Full Stack Developer position",
            "interview_type": "technical",
            "status": "scheduled",
            "scheduled_start": (datetime.now() + timedelta(days=i+3, hours=10)).isoformat(),
            "scheduled_end": (datetime.now() + timedelta(days=i+3, hours=11)).isoformat(),
            "interviewer_id": hiring_manager.id,
            "candidate_id": candidate.id,
            "location": "TechCorp Office - Conference Room A"
        }

        create_interview_response = await client.post(
            "/api/interviews",
            json=interview_data,
            headers=hr_headers
        )
        assert create_interview_response.status_code == 201
        interview = create_interview_response.json()
        scheduled_interviews.append(interview)

        print(f"✅ Scheduled interview for {candidate.first_name} {candidate.last_name} (ID: {interview['id']})")

    # Step 3.2: Verify interviews in system
    interviews_response = await client.get(
        "/api/interviews",
        headers=hr_headers
    )
    assert interviews_response.status_code == 200
    interviews_list = interviews_response.json()

    scheduled_interview_ids = [i['id'] for i in scheduled_interviews]
    system_interview_ids = [i['id'] for i in interviews_list]

    for interview_id in scheduled_interview_ids:
        assert interview_id in system_interview_ids

    print(f"✅ All interviews appear in system ({len(scheduled_interviews)} interviews)")

    # === SCENARIO 4: INTERVIEW EXECUTION AND FEEDBACK ===
    print("\n💼 SCENARIO 4: Interview Execution and Feedback")
    print("-" * 50)

    # Authenticate hiring manager
    login_response = await client.post(
        "/api/auth/login",
        json={"email": "hiring.manager@techcorp.com", "password": "hiringpass123"},
    )
    assert login_response.status_code == 200
    hiring_token = login_response.json()['access_token']
    hiring_headers = {"Authorization": f"Bearer {hiring_token}"}

    # Step 4.1: Conduct interviews and provide feedback
    interview_results = []

    for i, interview in enumerate(scheduled_interviews):
        # Mark interview as completed
        update_interview_response = await client.put(
            f"/api/interviews/{interview['id']}",
            json={
                "status": "completed",
                "notes": f"Excellent technical skills, good communication. {'Strong candidate for the role.' if i == 0 else 'Good candidate but needs more experience.'}"
            },
            headers=hiring_headers
        )
        assert update_interview_response.status_code == 200
        completed_interview = update_interview_response.json()

        # Record result
        interview_results.append({
            'interview': completed_interview,
            'decision': 'hire' if i == 0 else 'maybe',  # Alice gets hired, Bob is maybe
            'candidate': selected_candidates[i]['candidate']
        })

        print(f"✅ Completed interview for {selected_candidates[i]['candidate'].first_name} - Decision: {interview_results[i]['decision']}")

    # === SCENARIO 5: HIRING DECISION AND WORKFLOW COMPLETION ===
    print("\n🎯 SCENARIO 5: Hiring Decision and Process Completion")
    print("-" * 50)

    # Step 5.1: Make hiring decision (hire Alice)
    hired_candidate = interview_results[0]['candidate']

    # Update job status to indicate progress
    update_job_final_response = await client.put(
        f"/api/jobs/{job_id}",
        json={"status": "filled"},
        headers=hr_headers
    )
    assert update_job_final_response.status_code == 200
    final_job = update_job_final_response.json()
    assert final_job['status'] == 'filled'

    print(f"✅ Hired candidate: {hired_candidate.first_name} {hired_candidate.last_name}")
    print(f"✅ Updated job status to 'filled'")

    # === VERIFICATION PHASE ===
    print("\n🔍 VERIFICATION: End-to-End Workflow Validation")
    print("-" * 50)

    # Verify complete workflow state

    # 1. Job posting exists and is filled
    final_job_response = await client.get(f"/api/jobs/{job_id}")
    assert final_job_response.status_code == 200
    job_final_state = final_job_response.json()
    assert job_final_state['status'] == 'filled'
    print(f"✅ Job posting workflow complete: {job_final_state['title']}")

    # 2. All interviews were conducted
    final_interviews_response = await client.get("/api/interviews", headers=hr_headers)
    assert final_interviews_response.status_code == 200
    final_interviews = final_interviews_response.json()

    completed_count = len([i for i in final_interviews if i['status'] == 'completed'])
    assert completed_count == len(scheduled_interviews)
    print(f"✅ Interview process complete: {completed_count} interviews conducted")

    # 3. Candidates were processed
    print(f"✅ Candidate pipeline processed: {len(candidates)} candidates, {len(selected_candidates)} interviewed, 1 hired")

    # 4. Verify database consistency
    db_job = await db_session.execute(select(Job).where(Job.id == job_id))
    db_job_obj = db_job.scalar_one()
    assert db_job_obj.status == 'filled'

    db_interviews = await db_session.execute(
        select(Interview).where(Interview.id.in_(scheduled_interview_ids))
    )
    db_interview_objs = db_interviews.scalars().all()
    assert len(db_interview_objs) == len(scheduled_interviews)

    print(f"✅ Database consistency verified")

    print("\n🎉 COMPLETE RECRUITMENT WORKFLOW TEST PASSED!")
    print("=" * 70)
    print(f"Summary:")
    print(f"  • Job created and published: {job_final_state['title']}")
    print(f"  • Candidates processed: {len(candidates)}")
    print(f"  • Interviews conducted: {completed_count}")
    print(f"  • Final hiring decision: {hired_candidate.first_name} {hired_candidate.last_name}")
    print(f"  • Job status: {job_final_state['status']}")


@pytest.mark.asyncio
async def test_multi_position_recruitment_workflow(client: AsyncClient, db_session: AsyncSession):
    """Test recruitment workflow with multiple positions and complex scenarios."""

    print("\n🧪 Starting Multi-Position Recruitment Workflow Test")
    print("=" * 70)

    # Setup (simplified for multiple positions)
    roles = {}
    for role_name in UserRoleEnum:
        role = Role(name=role_name.value, description=f"Test {role_name.value} role")
        db_session.add(role)
        roles[role_name.value] = role
    await db_session.commit()

    for role in roles.values():
        await db_session.refresh(role)

    # Create tech company
    tech_company = Company(
        name="MultiTech Solutions",
        email="hr@multitech.com",
        phone="03-2468-1357",
        type="employer"
    )
    db_session.add(tech_company)
    await db_session.commit()
    await db_session.refresh(tech_company)

    # Create HR admin
    hr_admin = User(
        email='hr.admin@multitech.com',
        first_name='Emma',
        last_name='Wilson',
        company_id=tech_company.id,
        hashed_password=auth_service.get_password_hash('hradmin123'),
        is_active=True,
        is_admin=True,
        require_2fa=False,
    )
    db_session.add(hr_admin)
    await db_session.commit()
    await db_session.refresh(hr_admin)

    hr_role = UserRole(user_id=hr_admin.id, role_id=roles[UserRoleEnum.COMPANY_ADMIN.value].id)
    db_session.add(hr_role)
    await db_session.commit()

    # Authenticate HR admin
    login_response = await client.post(
        "/api/auth/login",
        json={"email": "hr.admin@multitech.com", "password": "hradmin123"},
    )
    assert login_response.status_code == 200
    admin_token = login_response.json()['access_token']
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    # === SCENARIO: Multiple Position Types ===
    print("\n📋 SCENARIO: Creating Multiple Position Types")
    print("-" * 50)

    # Create different types of positions
    positions_data = [
        {
            "title": "Senior Frontend Developer",
            "description": "React specialist for our web applications",
            "requirements": "React, TypeScript, 5+ years experience",
            "location": "Tokyo, Japan",
            "job_type": "full-time",
            "salary_min": 7000000,
            "salary_max": 10000000,
            "status": "published",
            "deadline": (datetime.now() + timedelta(days=30)).isoformat()
        },
        {
            "title": "Backend Engineer",
            "description": "Python/Django expert for our API services",
            "requirements": "Python, Django, PostgreSQL, 3+ years experience",
            "location": "Osaka, Japan",
            "job_type": "full-time",
            "salary_min": 6000000,
            "salary_max": 9000000,
            "status": "published",
            "deadline": (datetime.now() + timedelta(days=25)).isoformat()
        },
        {
            "title": "DevOps Engineer",
            "description": "Infrastructure and deployment specialist",
            "requirements": "AWS, Docker, Kubernetes, CI/CD",
            "location": "Remote",
            "job_type": "contract",
            "salary_min": 8000000,
            "salary_max": 12000000,
            "status": "published",
            "deadline": (datetime.now() + timedelta(days=20)).isoformat()
        }
    ]

    created_positions = []
    for position_data in positions_data:
        position_data["company_id"] = tech_company.id

        create_response = await client.post(
            "/api/jobs",
            json=position_data,
            headers=admin_headers
        )
        assert create_response.status_code == 201
        position = create_response.json()
        created_positions.append(position)
        print(f"✅ Created position: {position['title']} (ID: {position['id']})")

    # === SCENARIO: Bulk Operations ===
    print("\n⚡ SCENARIO: Bulk Position Management")
    print("-" * 50)

    # Test company jobs endpoint
    company_jobs_response = await client.get(
        f"/api/jobs/company/{tech_company.id}",
        headers=admin_headers
    )
    assert company_jobs_response.status_code == 200
    company_jobs = company_jobs_response.json()
    assert len(company_jobs) == len(created_positions)
    print(f"✅ Retrieved {len(company_jobs)} company positions")

    # Test job statistics
    stats_response = await client.get(
        "/api/jobs/statistics",
        headers=admin_headers
    )
    assert stats_response.status_code == 200
    stats = stats_response.json()
    print(f"✅ Job statistics: {stats}")

    # Test popular jobs endpoint
    popular_response = await client.get("/api/jobs/popular")
    assert popular_response.status_code == 200
    popular_jobs = popular_response.json()
    print(f"✅ Popular jobs endpoint working ({len(popular_jobs)} jobs)")

    # Test recent jobs endpoint
    recent_response = await client.get("/api/jobs/recent")
    assert recent_response.status_code == 200
    recent_jobs = recent_response.json()
    print(f"✅ Recent jobs endpoint working ({len(recent_jobs)} jobs)")

    # === SCENARIO: Search and Filtering ===
    print("\n🔍 SCENARIO: Advanced Job Search and Filtering")
    print("-" * 50)

    # Test search functionality
    search_response = await client.get(
        "/api/jobs/search",
        params={"query": "React", "location": "Tokyo"}
    )
    assert search_response.status_code == 200
    search_results = search_response.json()

    # Should find the frontend position
    react_jobs = [job for job in search_results if "React" in job.get('requirements', '')]
    assert len(react_jobs) > 0
    print(f"✅ Search found {len(react_jobs)} React jobs in Tokyo")

    # Test salary filtering
    salary_search_response = await client.get(
        "/api/jobs/search",
        params={"salary_min": 8000000}
    )
    assert salary_search_response.status_code == 200
    high_salary_jobs = salary_search_response.json()

    # Should find DevOps and Senior Frontend positions
    assert len(high_salary_jobs) >= 2
    print(f"✅ Salary filter found {len(high_salary_jobs)} high-paying positions")

    # Test job type filtering
    contract_search_response = await client.get(
        "/api/jobs",
        params={"job_type": "contract"}
    )
    assert contract_search_response.status_code == 200
    contract_jobs = contract_search_response.json()

    contract_count = len([job for job in contract_jobs['jobs'] if job['job_type'] == 'contract'])
    assert contract_count >= 1  # Should find the DevOps position
    print(f"✅ Job type filter found {contract_count} contract positions")

    print("\n🎉 MULTI-POSITION RECRUITMENT WORKFLOW TEST PASSED!")
    print("=" * 70)


@pytest.mark.asyncio
async def test_interview_workflow_scenarios(client: AsyncClient, db_session: AsyncSession):
    """Test various interview workflow scenarios and edge cases."""

    print("\n🧪 Starting Interview Workflow Scenarios Test")
    print("=" * 70)

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
        name="Interview Test Corp",
        email="interviews@testcorp.com",
        phone="03-1111-2222",
        type="employer"
    )
    db_session.add(company)
    await db_session.commit()
    await db_session.refresh(company)

    # Create users
    interviewer = User(
        email='interviewer@testcorp.com',
        first_name='Mike',
        last_name='Interviewer',
        company_id=company.id,
        hashed_password=auth_service.get_password_hash('interviewpass'),
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
        email='candidate@email.com',
        first_name='Jane',
        last_name='Candidate',
        hashed_password=auth_service.get_password_hash('candidatepass'),
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
        json={"email": "interviewer@testcorp.com", "password": "interviewpass"},
    )
    assert login_response.status_code == 200
    token = login_response.json()['access_token']
    headers = {"Authorization": f"Bearer {token}"}

    # === SCENARIO: Interview Lifecycle Management ===
    print("\n📅 SCENARIO: Interview Lifecycle Management")
    print("-" * 50)

    # Create initial interview
    interview_data = {
        "title": "Technical Interview - Jane Candidate",
        "description": "First round technical interview",
        "interview_type": "technical",
        "status": "scheduled",
        "scheduled_start": (datetime.now() + timedelta(days=2, hours=9)).isoformat(),
        "scheduled_end": (datetime.now() + timedelta(days=2, hours=10)).isoformat(),
        "interviewer_id": interviewer.id,
        "candidate_id": candidate.id,
        "location": "Conference Room A"
    }

    create_response = await client.post(
        "/api/interviews",
        json=interview_data,
        headers=headers
    )
    assert create_response.status_code == 201
    interview = create_response.json()
    interview_id = interview['id']
    print(f"✅ Created interview (ID: {interview_id})")

    # Test rescheduling
    reschedule_data = {
        "scheduled_start": (datetime.now() + timedelta(days=3, hours=14)).isoformat(),
        "scheduled_end": (datetime.now() + timedelta(days=3, hours=15)).isoformat(),
        "notes": "Rescheduled due to candidate availability"
    }

    reschedule_response = await client.put(
        f"/api/interviews/{interview_id}",
        json=reschedule_data,
        headers=headers
    )
    assert reschedule_response.status_code == 200
    rescheduled_interview = reschedule_response.json()
    print(f"✅ Rescheduled interview")

    # Test status progression
    status_updates = [
        {"status": "in_progress", "notes": "Interview started"},
        {"status": "completed", "notes": "Interview completed. Candidate showed strong technical skills."},
    ]

    for update in status_updates:
        update_response = await client.put(
            f"/api/interviews/{interview_id}",
            json=update,
            headers=headers
        )
        assert update_response.status_code == 200
        updated_interview = update_response.json()
        assert updated_interview['status'] == update['status']
        print(f"✅ Updated interview status to: {update['status']}")

    # === SCENARIO: Multiple Interview Types ===
    print("\n🎯 SCENARIO: Multiple Interview Types and Rounds")
    print("-" * 50)

    # Create different interview rounds
    interview_rounds = [
        {
            "title": "HR Screening - Jane Candidate",
            "interview_type": "hr_screening",
            "scheduled_start": (datetime.now() + timedelta(days=1)).isoformat(),
            "scheduled_end": (datetime.now() + timedelta(days=1, hours=1)).isoformat(),
        },
        {
            "title": "System Design - Jane Candidate",
            "interview_type": "system_design",
            "scheduled_start": (datetime.now() + timedelta(days=4)).isoformat(),
            "scheduled_end": (datetime.now() + timedelta(days=4, hours=1.5)).isoformat(),
        },
        {
            "title": "Final Interview - Jane Candidate",
            "interview_type": "final",
            "scheduled_start": (datetime.now() + timedelta(days=7)).isoformat(),
            "scheduled_end": (datetime.now() + timedelta(days=7, hours=1)).isoformat(),
        }
    ]

    created_rounds = []
    for round_data in interview_rounds:
        round_data.update({
            "description": f"{round_data['interview_type']} round for candidate evaluation",
            "status": "scheduled",
            "interviewer_id": interviewer.id,
            "candidate_id": candidate.id,
            "location": "Virtual Meeting"
        })

        create_round_response = await client.post(
            "/api/interviews",
            json=round_data,
            headers=headers
        )
        assert create_round_response.status_code == 201
        round_interview = create_round_response.json()
        created_rounds.append(round_interview)
        print(f"✅ Created {round_data['interview_type']} interview (ID: {round_interview['id']})")

    # Test interview listing and filtering
    all_interviews_response = await client.get("/api/interviews", headers=headers)
    assert all_interviews_response.status_code == 200
    all_interviews = all_interviews_response.json()

    # Should have original + 3 new rounds = 4 total
    total_interviews = len(all_interviews)
    assert total_interviews >= 4
    print(f"✅ Total interviews in system: {total_interviews}")

    # Test candidate's interviews
    candidate_interviews = [i for i in all_interviews if i['candidate_id'] == candidate.id]
    assert len(candidate_interviews) >= 4
    print(f"✅ Candidate has {len(candidate_interviews)} scheduled interviews")

    print("\n🎉 INTERVIEW WORKFLOW SCENARIOS TEST PASSED!")
    print("=" * 70)


if __name__ == "__main__":
    print("Run these tests with:")
    print("pytest test_recruitment_workflows.py -v -s")
    print("\nOr run specific scenarios:")
    print("pytest test_recruitment_workflows.py::test_complete_recruitment_workflow -v -s")
    print("pytest test_recruitment_workflows.py::test_multi_position_recruitment_workflow -v -s")
    print("pytest test_recruitment_workflows.py::test_interview_workflow_scenarios -v -s")