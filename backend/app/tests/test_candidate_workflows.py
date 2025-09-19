#!/usr/bin/env python3
"""
Comprehensive Candidate Management Workflow Tests

This test suite validates candidate-related workflows:
1. Candidate registration and profile management
2. Application tracking and status management
3. Candidate-interviewer communication flows
4. Hiring decision and onboarding workflows
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
async def test_candidate_application_workflow(client: AsyncClient, db_session: AsyncSession):
    """Test complete candidate application and tracking workflow."""

    print("\nStarting Candidate Application Workflow Test")
    print("=" * 70)

    # Setup
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
        name="Candidate Test Corp",
        email="hr@candidatetest.com",
        phone="03-9999-8888",
        type="employer"
    )
    db_session.add(company)
    await db_session.commit()
    await db_session.refresh(company)

    # Create HR manager
    hr_manager = User(
        email='hr@candidatetest.com',
        first_name='Lisa',
        last_name='HR',
        company_id=company.id,
        hashed_password=auth_service.get_password_hash('hrpass123'),
        is_active=True,
        is_admin=True,
        require_2fa=False,
    )
    db_session.add(hr_manager)
    await db_session.commit()
    await db_session.refresh(hr_manager)

    hr_role = UserRole(user_id=hr_manager.id, role_id=roles[UserRoleEnum.COMPANY_ADMIN.value].id)
    db_session.add(hr_role)
    await db_session.commit()

    # Authenticate HR manager
    login_response = await client.post(
        "/api/auth/login",
        json={"email": "hr@candidatetest.com", "password": "hrpass123"},
    )
    assert login_response.status_code == 200
    login_data = login_response.json()

    # Handle 2FA if required
    if login_data.get("require_2fa"):
        verify_response = await client.post(
            "/api/auth/2fa/verify",
            json={"user_id": hr_manager.id, "code": "123456"}
        )
        assert verify_response.status_code == 200
        login_data = verify_response.json()

    hr_token = login_data['access_token']
    hr_headers = {"Authorization": f"Bearer {hr_token}"}

    # Create job posting
    job_data = {
        "title": "Software Engineer Position",
        "description": "Exciting opportunity for software engineers",
        "requirements": "Python, React, 2+ years experience",
        "location": "Tokyo, Japan",
        "job_type": "full_time",
        "salary_min": 5000000,
        "salary_max": 8000000,
        "company_id": company.id,
        "application_deadline": (datetime.now() + timedelta(days=30)).isoformat()
    }

    job_response = await client.post("/api/jobs/", json=job_data, headers=hr_headers)
    assert job_response.status_code == 201
    job = job_response.json()
    job_id = job['id']

    print(f"Created job posting: {job['title']} (ID: {job_id})")

    # === SCENARIO 1: Candidate Registration and Profile ===
    print("\n👤 SCENARIO 1: Candidate Registration and Profile Creation")
    print("-" * 50)

    # Create candidates with different profiles
    candidates_data = [
        {
            'email': 'senior.dev@email.com',
            'first_name': 'Alex',
            'last_name': 'Senior',
            'experience_level': 'senior',
            'skills': ['Python', 'React', 'Docker', 'AWS'],
            'years_experience': 7
        },
        {
            'email': 'mid.dev@email.com',
            'first_name': 'Morgan',
            'last_name': 'Mid',
            'experience_level': 'mid',
            'skills': ['Python', 'Django', 'PostgreSQL'],
            'years_experience': 3
        },
        {
            'email': 'junior.dev@email.com',
            'first_name': 'Sam',
            'last_name': 'Junior',
            'experience_level': 'entry',
            'skills': ['Python', 'HTML', 'CSS'],
            'years_experience': 1
        }
    ]

    candidates = []
    for candidate_data in candidates_data:
        # Create candidate user
        candidate = User(
            email=candidate_data['email'],
            first_name=candidate_data['first_name'],
            last_name=candidate_data['last_name'],
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

        # Store additional data for simulation
        candidate_data['user_obj'] = candidate
        candidates.append(candidate_data)

        print(f"Registered candidate: {candidate.first_name} {candidate.last_name} ({candidate_data['experience_level']})")

    # === SCENARIO 2: Application Process ===
    print("\n📄 SCENARIO 2: Application Submission and Tracking")
    print("-" * 50)

    # Simulate candidates applying to the job
    applications = []

    for i, candidate_data in enumerate(candidates):
        candidate = candidate_data['user_obj']

        # Authenticate candidate
        login_response = await client.post(
            "/api/auth/login",
            json={"email": candidate.email, "password": "candidate123"},
        )
        assert login_response.status_code == 200
        candidate_token = login_response.json()['access_token']
        candidate_headers = {"Authorization": f"Bearer {candidate_token}"}

        # View job posting (simulate browsing)
        view_response = await client.get(f"/api/jobs/{job_id}")
        assert view_response.status_code == 200

        # Simulate application submission (conceptual - tracking application status)
        application = {
            'candidate': candidate,
            'candidate_data': candidate_data,
            'job_id': job_id,
            'application_date': datetime.now() - timedelta(days=i),  # Stagger application dates
            'status': 'submitted',
            'cover_letter': f"I am excited to apply for the {job['title']} position. With {candidate_data['years_experience']} years of experience in {', '.join(candidate_data['skills'][:3])}, I believe I would be a great fit for your team.",
            'candidate_headers': candidate_headers
        }
        applications.append(application)

        print(f"{candidate.first_name} applied for position (application {i+1}/3)")

    # === SCENARIO 3: HR Review and Candidate Screening ===
    print("\nSCENARIO 3: HR Review and Candidate Screening")
    print("-" * 50)

    # HR reviews applications and makes initial screening decisions
    screened_applications = []

    for i, application in enumerate(applications):
        candidate = application['candidate']
        candidate_data = application['candidate_data']

        # HR decision based on experience level and skills match
        if candidate_data['experience_level'] in ['senior', 'mid'] and 'Python' in candidate_data['skills']:
            decision = 'phone_screen'
            status = 'phone_screen_scheduled'
        elif candidate_data['experience_level'] == 'entry' and candidate_data['years_experience'] >= 1:
            decision = 'phone_screen'
            status = 'phone_screen_scheduled'
        else:
            decision = 'rejected'
            status = 'rejected'

        application['screening_decision'] = decision
        application['status'] = status
        application['screening_notes'] = f"Experience: {candidate_data['years_experience']} years, Skills match: {'Good' if 'Python' in candidate_data['skills'] else 'Partial'}"

        if decision == 'phone_screen':
            screened_applications.append(application)

        print(f"{candidate.first_name}: {decision} - {application['screening_notes']}")

    print(f"Screening complete: {len(screened_applications)}/{len(applications)} candidates advance to phone screen")

    # === SCENARIO 4: Interview Scheduling ===
    print("\n📞 SCENARIO 4: Interview Scheduling and Management")
    print("-" * 50)

    scheduled_interviews = []

    for i, application in enumerate(screened_applications):
        candidate = application['candidate']

        # Schedule phone screen interview
        interview_data = {
            "title": f"Phone Screen - {candidate.first_name} {candidate.last_name}",
            "description": f"Initial phone screening for Software Engineer position",
            "interview_type": "phone",
            "recruiter_id": hr_manager.id,
            "candidate_id": candidate.id,
            "employer_company_id": company.id
        }

        create_interview_response = await client.post(
            "/api/interviews/",
            json=interview_data,
            headers=hr_headers
        )
        assert create_interview_response.status_code == 201
        interview = create_interview_response.json()

        application['phone_screen_interview'] = interview
        scheduled_interviews.append(interview)

        print(f"Scheduled phone screen for {candidate.first_name} (Interview ID: {interview['id']})")

    # === SCENARIO 5: Interview Execution and Progression ===
    print("\n💼 SCENARIO 5: Interview Execution and Candidate Progression")
    print("-" * 50)

    # Conduct phone screens and make progression decisions
    technical_candidates = []

    for i, application in enumerate(screened_applications):
        candidate = application['candidate']
        interview = application['phone_screen_interview']

        # Simulate phone screen completion
        phone_screen_notes = f"Phone screen with {candidate.first_name}: "

        if application['candidate_data']['experience_level'] == 'senior':
            phone_screen_notes += "Excellent communication, strong technical background, advance to technical interview"
            progression_decision = 'technical_interview'
        elif application['candidate_data']['experience_level'] == 'mid':
            phone_screen_notes += "Good communication, solid experience, advance to technical interview"
            progression_decision = 'technical_interview'
        else:
            phone_screen_notes += "Good potential but needs more experience, feedback provided"
            progression_decision = 'feedback_only'

        # Update interview status
        update_response = await client.put(
            f"/api/interviews/{interview['id']}",
            json={
                "status": "completed",
                "notes": phone_screen_notes
            },
            headers=hr_headers
        )
        assert update_response.status_code == 200

        application['phone_screen_result'] = progression_decision
        application['phone_screen_notes'] = phone_screen_notes

        if progression_decision == 'technical_interview':
            technical_candidates.append(application)

        print(f"{candidate.first_name} phone screen completed: {progression_decision}")

    # Schedule technical interviews for advancing candidates
    print(f"\n🔧 Scheduling technical interviews for {len(technical_candidates)} candidates")

    for i, application in enumerate(technical_candidates):
        candidate = application['candidate']

        # Schedule technical interview
        tech_interview_data = {
            "title": f"Technical Interview - {candidate.first_name} {candidate.last_name}",
            "description": f"Technical assessment for Software Engineer position",
            "interview_type": "technical",
            "status": "scheduled",
            "scheduled_start": (datetime.now() + timedelta(days=i+5, hours=14)).isoformat(),
            "scheduled_end": (datetime.now() + timedelta(days=i+5, hours=15, minutes=30)).isoformat(),
            "interviewer_id": hr_manager.id,
            "candidate_id": candidate.id,
            "location": "Technical Assessment Room"
        }

        tech_response = await client.post(
            "/api/interviews/",
            json=tech_interview_data,
            headers=hr_headers
        )
        assert tech_response.status_code == 201
        tech_interview = tech_response.json()

        application['technical_interview'] = tech_interview
        print(f"Scheduled technical interview for {candidate.first_name} (Interview ID: {tech_interview['id']})")

    # === SCENARIO 6: Final Hiring Decision ===
    print("\nSCENARIO 6: Final Hiring Decision and Communication")
    print("-" * 50)

    # Conduct technical interviews and make final decisions
    hired_candidate = None

    for i, application in enumerate(technical_candidates):
        candidate = application['candidate']
        tech_interview = application['technical_interview']
        candidate_data = application['candidate_data']

        # Simulate technical interview results
        if candidate_data['experience_level'] == 'senior' and i == 0:  # First senior candidate gets offer
            tech_result = 'hire'
            tech_notes = "Excellent technical performance, strong problem-solving skills, team fit confirmed"
            hired_candidate = application
        else:
            tech_result = 'strong_candidate'
            tech_notes = "Good technical performance, keep in pipeline for future opportunities"

        # Update technical interview
        tech_update_response = await client.put(
            f"/api/interviews/{tech_interview['id']}",
            json={
                "status": "completed",
                "notes": tech_notes
            },
            headers=hr_headers
        )
        assert tech_update_response.status_code == 200

        application['final_decision'] = tech_result
        application['final_notes'] = tech_notes

        print(f"{candidate.first_name} technical interview: {tech_result}")

    # Update job status if candidate hired
    if hired_candidate:
        hired_name = f"{hired_candidate['candidate'].first_name} {hired_candidate['candidate'].last_name}"

        # Mark job as filled
        job_update_response = await client.put(
            f"/api/jobs/{job_id}",
            json={"status": "filled"},
            headers=hr_headers
        )
        assert job_update_response.status_code == 200

        print(f"HIRED: {hired_name}")
        print(f"Job status updated to 'filled'")

    # === VERIFICATION ===
    print("\nVERIFICATION: Workflow Validation")
    print("-" * 50)

    # Verify all interviews were created and completed
    all_interviews_response = await client.get("/api/interviews/", headers=hr_headers)
    assert all_interviews_response.status_code == 200
    all_interviews = all_interviews_response.json()

    phone_screens = [i for i in all_interviews if i['interview_type'] == 'phone_screen']
    technical_interviews = [i for i in all_interviews if i['interview_type'] == 'technical']

    assert len(phone_screens) == len(screened_applications)
    assert len(technical_interviews) == len(technical_candidates)

    print(f"Interview verification:")
    print(f"  • Phone screens conducted: {len(phone_screens)}")
    print(f"  • Technical interviews conducted: {len(technical_interviews)}")
    print(f"  • Final hiring decision: {'Yes' if hired_candidate else 'No'}")

    # Verify job status
    final_job_response = await client.get(f"/api/jobs/{job_id}")
    assert final_job_response.status_code == 200
    final_job = final_job_response.json()

    print(f"Job final status: {final_job['status']}")

    print("\n🎉 CANDIDATE APPLICATION WORKFLOW TEST PASSED!")
    print("=" * 70)
    print("Workflow Summary:")
    print(f"  • Candidates registered: {len(candidates)}")
    print(f"  • Applications submitted: {len(applications)}")
    print(f"  • Phone screens conducted: {len(screened_applications)}")
    print(f"  • Technical interviews: {len(technical_candidates)}")
    print(f"  • Final hire: {hired_candidate['candidate'].first_name if hired_candidate else 'None'}")


@pytest.mark.asyncio
async def test_candidate_pipeline_management(client: AsyncClient, db_session: AsyncSession):
    """Test candidate pipeline and bulk management operations."""

    print("\n🧪 Starting Candidate Pipeline Management Test")
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
        name="Pipeline Test Company",
        email="pipeline@test.com",
        phone="03-5555-6666",
        type="employer"
    )
    db_session.add(company)
    await db_session.commit()
    await db_session.refresh(company)

    hr_user = User(
        email='pipeline.hr@test.com',
        first_name='Pipeline',
        last_name='Manager',
        company_id=company.id,
        hashed_password=auth_service.get_password_hash('pipelinepass'),
        is_active=True,
        is_admin=True,
        require_2fa=False,
    )
    db_session.add(hr_user)
    await db_session.commit()
    await db_session.refresh(hr_user)

    hr_role = UserRole(user_id=hr_user.id, role_id=roles[UserRoleEnum.COMPANY_ADMIN.value].id)
    db_session.add(hr_role)
    await db_session.commit()

    # Authenticate
    login_response = await client.post(
        "/api/auth/login",
        json={"email": "pipeline.hr@test.com", "password": "pipelinepass"},
    )
    assert login_response.status_code == 200
    login_data = login_response.json()

    # Handle 2FA if required
    if login_data.get("require_2fa"):
        verify_response = await client.post(
            "/api/auth/2fa/verify",
            json={"user_id": hr_user.id, "code": "123456"}
        )
        assert verify_response.status_code == 200
        login_data = verify_response.json()

    token = login_data['access_token']
    headers = {"Authorization": f"Bearer {token}"}

    # === SCENARIO: Bulk Candidate Management ===
    print("\nSCENARIO: Bulk Candidate Operations")
    print("-" * 50)

    # Create multiple candidates with different statuses
    bulk_candidates = []
    candidate_profiles = [
        ('active_senior', 'senior', ['Python', 'React', 'AWS']),
        ('active_mid', 'mid', ['Java', 'Spring', 'MySQL']),
        ('active_junior', 'entry', ['JavaScript', 'HTML', 'CSS']),
        ('interviewing_senior', 'senior', ['C++', 'Docker', 'Kubernetes']),
        ('interviewing_mid', 'mid', ['PHP', 'Laravel', 'Redis']),
    ]

    for i, (status_type, level, skills) in enumerate(candidate_profiles):
        candidate = User(
            email=f'bulk.candidate{i+1}@email.com',
            first_name=f'Bulk{i+1}',
            last_name=f'Candidate',
            hashed_password=auth_service.get_password_hash('bulkpass'),
            is_active=True,
            is_admin=False,
            require_2fa=False,
        )
        db_session.add(candidate)
        await db_session.commit()
        await db_session.refresh(candidate)

        candidate_role = UserRole(user_id=candidate.id, role_id=roles[UserRoleEnum.CANDIDATE.value].id)
        db_session.add(candidate_role)

        bulk_candidates.append({
            'user': candidate,
            'status_type': status_type,
            'level': level,
            'skills': skills
        })

    await db_session.commit()
    print(f"Created {len(bulk_candidates)} candidates for pipeline testing")

    # Test user management endpoints for candidate filtering
    print("\nTesting candidate filtering and management...")

    # Get all users (should include our candidates)
    all_users_response = await client.get("/api/admin/users", headers=headers)
    assert all_users_response.status_code == 200
    all_users = all_users_response.json()

    # Filter candidates by role
    candidate_users = []
    for user in all_users:
        if any(role['name'] == 'candidate' for role in user.get('roles', [])):
            candidate_users.append(user)

    print(f"Found {len(candidate_users)} candidates in user management system")

    # Test individual candidate management
    print("\n👤 Testing individual candidate operations...")

    # Get specific candidate details
    first_candidate = bulk_candidates[0]['user']
    candidate_detail_response = await client.get(f"/api/admin/users/{first_candidate.id}", headers=headers)
    assert candidate_detail_response.status_code == 200
    candidate_detail = candidate_detail_response.json()

    assert candidate_detail['email'] == first_candidate.email
    assert candidate_detail['first_name'] == first_candidate.first_name
    print(f"Retrieved candidate details: {candidate_detail['first_name']} {candidate_detail['last_name']}")

    # Test candidate profile updates
    update_data = {
        "first_name": "Updated",
        "last_name": "Name"
    }

    update_response = await client.put(
        f"/api/admin/users/{first_candidate.id}",
        json=update_data,
        headers=headers
    )
    assert update_response.status_code == 200
    updated_candidate = update_response.json()

    assert updated_candidate['first_name'] == "Updated"
    print(f"Updated candidate profile successfully")

    print("\n🎉 CANDIDATE PIPELINE MANAGEMENT TEST PASSED!")
    print("=" * 70)


if __name__ == "__main__":
    print("Run these tests with:")
    print("pytest test_candidate_workflows.py -v -s")
    print("\nOr run specific scenarios:")
    print("pytest test_candidate_workflows.py::test_candidate_application_workflow -v -s")
    print("pytest test_candidate_workflows.py::test_candidate_pipeline_management -v -s")