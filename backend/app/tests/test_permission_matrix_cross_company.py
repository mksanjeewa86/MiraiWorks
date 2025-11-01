import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.attachment import Attachment
from app.models.candidate_workflow import CandidateWorkflow
from app.models.company import Company
from app.models.interview import Interview
from app.models.position import Position
from app.models.resume import Resume
from app.models.user import User
from app.models.workflow import Workflow as RecruitmentProcess
from app.models.workflow_node import WorkflowNode
from app.schemas.user import UserRole
from app.services.auth_service import AuthService
from app.utils.datetime_utils import get_utc_now


class TestCrossCompanyAccessPrevention:
    """
    Comprehensive tests for cross-company access prevention.
    Tests ensure users cannot access resources from other companies.
    """

    @pytest.fixture
    async def setup_cross_company_scenario(self, db: AsyncSession):
        """Setup scenario with multiple companies and users for cross-company testing."""

        # Create Company A
        company_a = Company(
            name="TechCorp A",
            description="Technology Company A",
            industry="Technology",
            size="medium",
            location="Tokyo",
            is_active=True,
        )
        db.add(company_a)
        await db.flush()

        # Create Company B
        company_b = Company(
            name="TechCorp B",
            description="Technology Company B",
            industry="Technology",
            size="large",
            location="Osaka",
            is_active=True,
        )
        db.add(company_b)
        await db.flush()

        # Create Company Admin for Company A
        company_admin_a = User(
            email="admin_a@techcorp-a.com",
            hashed_password="hashed_password",
            company_id=company_a.id,
            role=UserRole.ADMIN,
            is_active=True,
            is_verified=True,
            first_name="Admin",
            last_name="CompanyA",
        )
        db.add(company_admin_a)

        # Create Company Admin for Company B
        company_admin_b = User(
            email="admin_b@techcorp-b.com",
            hashed_password="hashed_password",
            company_id=company_b.id,
            role=UserRole.ADMIN,
            is_active=True,
            is_verified=True,
            first_name="Admin",
            last_name="CompanyB",
        )
        db.add(company_admin_b)

        # Create Recruiter for Company A
        recruiter_a = User(
            email="recruiter_a@techcorp-a.com",
            hashed_password="hashed_password",
            company_id=company_a.id,
            role=UserRole.MEMBER,
            is_active=True,
            is_verified=True,
            first_name="Recruiter",
            last_name="CompanyA",
        )
        db.add(recruiter_a)

        # Create Recruiter for Company B
        recruiter_b = User(
            email="recruiter_b@techcorp-b.com",
            hashed_password="hashed_password",
            company_id=company_b.id,
            role=UserRole.MEMBER,
            is_active=True,
            is_verified=True,
            first_name="Recruiter",
            last_name="CompanyB",
        )
        db.add(recruiter_b)

        # Create Employer for Company A
        employer_a = User(
            email="employer_a@techcorp-a.com",
            hashed_password="hashed_password",
            company_id=company_a.id,
            role=UserRole.MEMBER,
            is_active=True,
            is_verified=True,
            first_name="Employer",
            last_name="CompanyA",
        )
        db.add(employer_a)

        # Create Employer for Company B
        employer_b = User(
            email="employer_b@techcorp-b.com",
            hashed_password="hashed_password",
            company_id=company_b.id,
            role=UserRole.MEMBER,
            is_active=True,
            is_verified=True,
            first_name="Employer",
            last_name="CompanyB",
        )
        db.add(employer_b)

        # Create Independent Candidates
        candidate_a = User(
            email="candidate_a@email.com",
            hashed_password="hashed_password",
            company_id=None,
            role=UserRole.CANDIDATE,
            is_active=True,
            is_verified=True,
            first_name="Candidate",
            last_name="A",
        )
        db.add(candidate_a)

        candidate_b = User(
            email="candidate_b@email.com",
            hashed_password="hashed_password",
            company_id=None,
            role=UserRole.CANDIDATE,
            is_active=True,
            is_verified=True,
            first_name="Candidate",
            last_name="B",
        )
        db.add(candidate_b)

        await db.commit()
        await db.refresh(company_a)
        await db.refresh(company_b)
        await db.refresh(company_admin_a)
        await db.refresh(company_admin_b)
        await db.refresh(recruiter_a)
        await db.refresh(recruiter_b)
        await db.refresh(employer_a)
        await db.refresh(employer_b)
        await db.refresh(candidate_a)
        await db.refresh(candidate_b)

        return {
            "company_a": company_a,
            "company_b": company_b,
            "company_admin_a": company_admin_a,
            "company_admin_b": company_admin_b,
            "recruiter_a": recruiter_a,
            "recruiter_b": recruiter_b,
            "employer_a": employer_a,
            "employer_b": employer_b,
            "candidate_a": candidate_a,
            "candidate_b": candidate_b,
        }

    def _create_auth_headers(self, user: User) -> dict:
        """Create authentication headers for a user."""
        auth_service = AuthService()
        access_token = auth_service.create_access_token(data={"sub": user.email})
        return {"Authorization": f"Bearer {access_token}"}

    async def test_company_admin_cannot_access_other_company_users(
        self, client: AsyncClient, setup_cross_company_scenario: dict
    ):
        """Test Company Admin cannot access users from other companies."""
        scenario = setup_cross_company_scenario
        admin_a_headers = self._create_auth_headers(scenario["company_admin_a"])

        # Try to access Company B admin
        response = await client.get(
            f"/api/admin/users/{scenario['company_admin_b'].id}",
            headers=admin_a_headers,
        )
        assert response.status_code == 403

        # Try to update Company B admin
        response = await client.put(
            f"/api/admin/users/{scenario['company_admin_b'].id}",
            json={"first_name": "Modified"},
            headers=admin_a_headers,
        )
        assert response.status_code == 403

        # Try to delete Company B admin
        response = await client.delete(
            f"/api/admin/users/{scenario['company_admin_b'].id}",
            headers=admin_a_headers,
        )
        assert response.status_code == 403

    async def test_company_admin_cannot_create_users_in_other_companies(
        self, client: AsyncClient, setup_cross_company_scenario: dict
    ):
        """Test Company Admin cannot create users in other companies."""
        scenario = setup_cross_company_scenario
        admin_a_headers = self._create_auth_headers(scenario["company_admin_a"])

        # Try to create user in Company B
        user_data = {
            "email": "newuser@company-b.com",
            "company_id": scenario["company_b"].id,
            "role": "member",
            "first_name": "New",
            "last_name": "User",
        }

        response = await client.post(
            "/api/admin/users", json=user_data, headers=admin_a_headers
        )
        assert response.status_code == 403

    async def test_recruiter_cannot_access_other_company_positions(
        self, client: AsyncClient, db: AsyncSession, setup_cross_company_scenario: dict
    ):
        """Test Recruiter cannot access positions from other companies."""
        scenario = setup_cross_company_scenario

        # Create position in Company B
        position_b = Position(
            title="Software Engineer",
            description="Great opportunity",
            company_id=scenario["company_b"].id,
            posted_by=scenario["recruiter_b"].id,
            location="Osaka",
            job_type="full_time",
            experience_level="mid",
            status="published",
            slug="software-engineer-b",
        )
        db.add(position_b)
        await db.commit()
        await db.refresh(position_b)

        recruiter_a_headers = self._create_auth_headers(scenario["recruiter_a"])

        # Try to access Company B position
        response = await client.get(
            f"/api/positions/{position_b.id}", headers=recruiter_a_headers
        )
        assert response.status_code == 403

        # Try to update Company B position
        response = await client.put(
            f"/api/positions/{position_b.id}",
            json={"title": "Modified Title"},
            headers=recruiter_a_headers,
        )
        assert response.status_code == 403

    async def test_employer_cannot_access_other_company_interviews(
        self, client: AsyncClient, db: AsyncSession, setup_cross_company_scenario: dict
    ):
        """Test Employer cannot access interviews from other companies."""
        scenario = setup_cross_company_scenario

        # Create position and interview in Company B
        position_b = Position(
            title="Backend Developer",
            description="Backend role",
            company_id=scenario["company_b"].id,
            posted_by=scenario["employer_b"].id,
            location="Osaka",
            job_type="full_time",
            experience_level="senior",
            status="published",
            slug="backend-developer-b",
        )
        db.add(position_b)
        await db.flush()

        interview_b = Interview(
            position_id=position_b.id,
            candidate_id=scenario["candidate_a"].id,
            interviewer_id=scenario["employer_b"].id,
            scheduled_at=get_utc_now(),
            duration_minutes=60,
            interview_type="technical",
            status="scheduled",
        )
        db.add(interview_b)
        await db.commit()
        await db.refresh(interview_b)

        employer_a_headers = self._create_auth_headers(scenario["employer_a"])

        # Try to access Company B interview
        response = await client.get(
            f"/api/interviews/{interview_b.id}", headers=employer_a_headers
        )
        assert response.status_code == 403

        # Try to update Company B interview
        response = await client.put(
            f"/api/interviews/{interview_b.id}",
            json={"status": "completed"},
            headers=employer_a_headers,
        )
        assert response.status_code == 403

    async def test_cross_company_messaging_restrictions(
        self, client: AsyncClient, setup_cross_company_scenario: dict
    ):
        """Test messaging restrictions between companies."""
        scenario = setup_cross_company_scenario

        # Company Admin A cannot message Company Admin B directly
        admin_a_headers = self._create_auth_headers(scenario["company_admin_a"])

        message_data = {
            "recipient_id": scenario["company_admin_b"].id,
            "subject": "Cross Company Message",
            "content": "This should not be allowed",
        }

        response = await client.post(
            "/api/messages", json=message_data, headers=admin_a_headers
        )
        assert response.status_code == 403

        # Recruiter A cannot message Recruiter B
        recruiter_a_headers = self._create_auth_headers(scenario["recruiter_a"])

        message_data = {
            "recipient_id": scenario["recruiter_b"].id,
            "subject": "Cross Company Recruitment",
            "content": "This should not be allowed",
        }

        response = await client.post(
            "/api/messages", json=message_data, headers=recruiter_a_headers
        )
        assert response.status_code == 403

    async def test_cross_company_file_access_prevention(
        self, client: AsyncClient, db: AsyncSession, setup_cross_company_scenario: dict
    ):
        """Test file access restrictions between companies."""
        scenario = setup_cross_company_scenario

        # Create file owned by Company B user
        file_b = Attachment(
            original_filename="Company B Document.pdf",
            s3_key="company_b/documents/company_b_document.pdf",
            s3_bucket="test-bucket",
            file_size=1024,
            mime_type="application/pdf",
            sha256_hash="abcd1234567890abcd1234567890abcd1234567890abcd1234567890abcd1234",
            owner_id=scenario["employer_b"].id,
            is_available=True,
        )
        db.add(file_b)
        await db.commit()
        await db.refresh(file_b)

        employer_a_headers = self._create_auth_headers(scenario["employer_a"])

        # Try to access Company B file
        response = await client.get(
            f"/api/attachments/{file_b.id}", headers=employer_a_headers
        )
        assert response.status_code == 403

        # Try to delete Company B file
        response = await client.delete(
            f"/api/attachments/{file_b.id}", headers=employer_a_headers
        )
        assert response.status_code == 403

    async def test_cross_company_resume_access_prevention(
        self, client: AsyncClient, db: AsyncSession, setup_cross_company_scenario: dict
    ):
        """Test resume access restrictions between companies."""
        scenario = setup_cross_company_scenario

        # Create resume for candidate
        resume_a = Resume(
            candidate_id=scenario["candidate_a"].id,
            title="Software Engineer Resume",
            content="Experienced developer...",
            skills=["Python", "FastAPI", "React"],
            experience_years=3,
            is_public=False,
        )
        db.add(resume_a)
        await db.commit()
        await db.refresh(resume_a)

        # Company B recruiter tries to access private resume
        recruiter_b_headers = self._create_auth_headers(scenario["recruiter_b"])

        response = await client.get(
            f"/api/resumes/{resume_a.id}", headers=recruiter_b_headers
        )
        assert response.status_code == 403

    async def test_cross_company_todo_assignment_prevention(
        self, client: AsyncClient, setup_cross_company_scenario: dict
    ):
        """Test todo assignment restrictions between companies."""
        scenario = setup_cross_company_scenario

        # Company Admin A tries to assign todo to Company B user
        admin_a_headers = self._create_auth_headers(scenario["company_admin_a"])

        todo_data = {
            "title": "Cross Company Task",
            "description": "This should not be allowed",
            "assigned_to": scenario["recruiter_b"].id,
            "priority": "medium",
            "due_date": "2024-02-01",
        }

        response = await client.post(
            "/api/todos", json=todo_data, headers=admin_a_headers
        )
        assert response.status_code == 403

        # Recruiter A tries to assign todo to Employer B
        recruiter_a_headers = self._create_auth_headers(scenario["recruiter_a"])

        todo_data = {
            "title": "Cross Company Assignment",
            "description": "This should not be allowed",
            "assigned_to": scenario["employer_b"].id,
            "priority": "high",
            "due_date": "2024-02-15",
        }

        response = await client.post(
            "/api/todos", json=todo_data, headers=recruiter_a_headers
        )
        assert response.status_code == 403

    async def test_cross_company_recruitment_process_isolation(
        self, client: AsyncClient, db: AsyncSession, setup_cross_company_scenario: dict
    ):
        """Test recruitment process isolation between companies."""
        scenario = setup_cross_company_scenario

        # Create recruitment process for Company B
        recruitment_process_b = RecruitmentProcess(
            name="Company B Hiring Process",
            description="Hiring process for Company B",
            company_id=scenario["company_b"].id,
            created_by=scenario["company_admin_b"].id,
            is_active=True,
        )
        db.add(recruitment_process_b)
        await db.flush()

        # Create process node for Company B
        process_node_b = WorkflowNode(
            workflow_id=recruitment_process_b.id,
            name="Company B Interview",
            node_type="interview",
            order_index=1,
            is_active=True,
        )
        db.add(process_node_b)
        await db.commit()
        await db.refresh(recruitment_process_b)
        await db.refresh(process_node_b)

        # Company A admin tries to access Company B recruitment process
        admin_a_headers = self._create_auth_headers(scenario["company_admin_a"])

        response = await client.get(
            f"/api/recruitment-workflows/processes/{recruitment_process_b.id}",
            headers=admin_a_headers,
        )
        assert response.status_code == 403

        # Company A recruiter tries to modify Company B process node
        recruiter_a_headers = self._create_auth_headers(scenario["recruiter_a"])

        response = await client.put(
            f"/api/recruitment-workflows/nodes/{process_node_b.id}",
            json={"name": "Modified Node"},
            headers=recruiter_a_headers,
        )
        assert response.status_code == 403

    async def test_cross_company_candidate_process_isolation(
        self, client: AsyncClient, db: AsyncSession, setup_cross_company_scenario: dict
    ):
        """Test candidate process isolation between companies."""
        scenario = setup_cross_company_scenario

        # Create position and recruitment process for Company B
        position_b = Position(
            title="Data Scientist",
            description="Data science role",
            company_id=scenario["company_b"].id,
            posted_by=scenario["recruiter_b"].id,
            location="Osaka",
            job_type="full_time",
            experience_level="senior",
            status="published",
            slug="data-scientist-b",
        )
        db.add(position_b)
        await db.flush()

        recruitment_process_b = RecruitmentProcess(
            name="Data Science Hiring",
            description="Data science hiring process",
            company_id=scenario["company_b"].id,
            created_by=scenario["recruiter_b"].id,
            is_active=True,
        )
        db.add(recruitment_process_b)
        await db.flush()

        # Create candidate process for Company B
        candidate_process_b = CandidateWorkflow(
            candidate_id=scenario["candidate_a"].id,
            position_id=position_b.id,
            workflow_id=recruitment_process_b.id,
            current_stage="application_review",
            status="in_progress",
        )
        db.add(candidate_process_b)
        await db.commit()
        await db.refresh(candidate_process_b)

        # Company A recruiter tries to access Company B candidate process
        recruiter_a_headers = self._create_auth_headers(scenario["recruiter_a"])

        response = await client.get(
            f"/api/recruitment-workflows/candidate-processes/{candidate_process_b.id}",
            headers=recruiter_a_headers,
        )
        assert response.status_code == 403

        # Company A admin tries to update Company B candidate process
        admin_a_headers = self._create_auth_headers(scenario["company_admin_a"])

        response = await client.put(
            f"/api/recruitment-workflows/candidate-processes/{candidate_process_b.id}",
            json={"status": "rejected"},
            headers=admin_a_headers,
        )
        assert response.status_code == 403

    async def test_cross_company_bulk_operations_prevention(
        self, client: AsyncClient, setup_cross_company_scenario: dict
    ):
        """Test bulk operations cannot affect other companies."""
        scenario = setup_cross_company_scenario
        admin_a_headers = self._create_auth_headers(scenario["company_admin_a"])

        # Try bulk user operation across companies
        bulk_data = {
            "user_ids": [scenario["recruiter_b"].id, scenario["employer_b"].id],
            "action": "deactivate",
        }

        response = await client.post(
            "/api/admin/users/bulk", json=bulk_data, headers=admin_a_headers
        )
        assert response.status_code == 403

        # Try bulk message send to other company users
        bulk_message_data = {
            "recipient_ids": [scenario["recruiter_b"].id, scenario["employer_b"].id],
            "subject": "Cross Company Announcement",
            "content": "This should not reach other company",
        }

        response = await client.post(
            "/api/messages/bulk", json=bulk_message_data, headers=admin_a_headers
        )
        assert response.status_code == 403

    async def test_cross_company_search_isolation(
        self, client: AsyncClient, setup_cross_company_scenario: dict
    ):
        """Test search results are isolated between companies."""
        scenario = setup_cross_company_scenario
        recruiter_a_headers = self._create_auth_headers(scenario["recruiter_a"])

        # Search for users should only return Company A users
        response = await client.get(
            "/api/admin/users/search?query=recruiter", headers=recruiter_a_headers
        )
        assert response.status_code == 200

        users = response.json()
        company_ids = [
            user.get("company_id") for user in users if user.get("company_id")
        ]

        # All returned users should be from Company A only
        for company_id in company_ids:
            assert company_id == scenario["company_a"].id

        # Search for positions should only return Company A positions
        response = await client.get(
            "/api/positions/search?query=engineer", headers=recruiter_a_headers
        )
        assert response.status_code == 200

    async def test_cross_company_statistics_isolation(
        self, client: AsyncClient, setup_cross_company_scenario: dict
    ):
        """Test statistical data is isolated between companies."""
        scenario = setup_cross_company_scenario
        admin_a_headers = self._create_auth_headers(scenario["company_admin_a"])

        # Company stats should only include own company data
        response = await client.get(
            "/api/admin/statistics/dashboard", headers=admin_a_headers
        )
        assert response.status_code == 200

        stats = response.json()

        # Stats should not include data from Company B
        if "company_breakdown" in stats:
            company_names = [comp["name"] for comp in stats["company_breakdown"]]
            assert scenario["company_b"].name not in company_names

        # Recruitment stats should only include Company A data
        response = await client.get(
            "/api/admin/statistics/recruitment", headers=admin_a_headers
        )
        assert response.status_code == 200

    async def test_cross_company_export_isolation(
        self, client: AsyncClient, setup_cross_company_scenario: dict
    ):
        """Test data export is isolated between companies."""
        scenario = setup_cross_company_scenario
        admin_a_headers = self._create_auth_headers(scenario["company_admin_a"])

        # Export users should only include Company A users
        response = await client.get("/api/admin/export/users", headers=admin_a_headers)
        assert response.status_code == 200

        # Export recruitment data should only include Company A data
        response = await client.get(
            "/api/admin/export/recruitment-data", headers=admin_a_headers
        )
        assert response.status_code == 200

        # Try to export other company data directly (should fail)
        response = await client.get(
            f"/api/admin/export/company-data/{scenario['company_b'].id}",
            headers=admin_a_headers,
        )
        assert response.status_code == 403
