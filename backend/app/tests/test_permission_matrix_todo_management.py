"""
Comprehensive permission matrix tests for todo management.

Tests the permission boundaries:
- Super Admin: Can assign todos to anyone
- Company Admin: Can assign todos to company users only
- Recruiter/Employer: Can assign todos to company users only
- Candidate: Cannot assign todos to others
- All users: Can create, update, delete own todos
- Cross-company todo assignment restrictions
- Todo visibility restrictions
"""

from datetime import datetime, timedelta

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.company import Company
from app.models.role import UserRole
from app.models.todo import Todo
from app.models.user import User
from app.services.auth_service import auth_service
from app.utils.constants import CompanyType
from app.utils.constants import UserRole as UserRoleEnum


class TestTodoManagementPermissionMatrix:
    """Comprehensive tests for todo management permission boundaries."""

    # ===== BASIC TODO CREATION PERMISSIONS =====

    @pytest.mark.asyncio
    async def test_all_authenticated_users_can_create_todos(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_company: Company,
        test_roles: dict,
    ):
        """Test that all authenticated users can create todos."""
        roles_to_test = [
            UserRoleEnum.CANDIDATE,
            UserRoleEnum.RECRUITER,
            UserRoleEnum.EMPLOYER,
            UserRoleEnum.COMPANY_ADMIN,
        ]

        for role in roles_to_test:
            user = await self._create_user_with_role(
                db_session, test_company, test_roles, role, f"{role.value}@test.com"
            )
            headers = await self._get_auth_headers(client, user)

            todo_data = {
                "title": f"Todo by {role.value}",
                "description": f"Todo created by {role.value}",
                "due_date": (datetime.utcnow() + timedelta(days=7)).isoformat(),
                "priority": "medium",
            }

            response = await client.post("/api/todos", json=todo_data, headers=headers)

            assert response.status_code == 201, f"Failed for role {role.value}"
            data = response.json()
            assert data["title"] == todo_data["title"]
            assert data["creator_id"] == user.id

    @pytest.mark.asyncio
    async def test_super_admin_can_create_todos(
        self, client: AsyncClient, super_admin_auth_headers: dict
    ):
        """Test that Super Admin can create todos."""
        todo_data = {
            "title": "Super Admin Todo",
            "description": "Todo created by super admin",
            "due_date": (datetime.utcnow() + timedelta(days=7)).isoformat(),
            "priority": "high",
        }

        response = await client.post(
            "/api/todos", json=todo_data, headers=super_admin_auth_headers
        )

        assert response.status_code == 201
        data = response.json()
        assert data["title"] == todo_data["title"]

    # ===== TODO ASSIGNMENT PERMISSIONS =====

    @pytest.mark.asyncio
    async def test_super_admin_can_assign_todos_to_anyone(
        self,
        client: AsyncClient,
        super_admin_auth_headers: dict,
        db_session: AsyncSession,
        test_company: Company,
        test_roles: dict,
    ):
        """Test that Super Admin can assign todos to any user."""
        # Create users in different companies
        user1 = await self._create_user_with_role(
            db_session, test_company, test_roles, UserRoleEnum.RECRUITER, "recruiter1@test.com"
        )
        other_company = await self._create_other_company(db_session)
        user2 = await self._create_user_with_role(
            db_session, other_company, test_roles, UserRoleEnum.RECRUITER, "recruiter2@test.com"
        )

        # Create todo
        todo = await self._create_todo(db_session, None, "Super Admin Todo")

        # Super admin should be able to assign to any user
        assign_data = {"assignee_id": user1.id}
        response = await client.post(
            f"/api/todos/{todo.id}/assign", json=assign_data, headers=super_admin_auth_headers
        )
        assert response.status_code == 200

        # Should also be able to assign to user from different company
        assign_data = {"assignee_id": user2.id}
        response = await client.post(
            f"/api/todos/{todo.id}/assign", json=assign_data, headers=super_admin_auth_headers
        )
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_company_admin_can_assign_todos_to_company_users_only(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_company: Company,
        test_roles: dict,
    ):
        """Test that Company Admin can only assign todos to their company users."""
        company_admin = await self._create_user_with_role(
            db_session, test_company, test_roles, UserRoleEnum.COMPANY_ADMIN, "companyadmin@test.com"
        )
        company_user = await self._create_user_with_role(
            db_session, test_company, test_roles, UserRoleEnum.RECRUITER, "recruiter@test.com"
        )

        other_company = await self._create_other_company(db_session)
        other_user = await self._create_user_with_role(
            db_session, other_company, test_roles, UserRoleEnum.RECRUITER, "otherrecruiter@test.com"
        )

        headers = await self._get_auth_headers(client, company_admin)
        todo = await self._create_todo(db_session, company_admin.id, "Company Admin Todo")

        # Should be able to assign to same company user
        assign_data = {"assignee_id": company_user.id}
        response = await client.post(
            f"/api/todos/{todo.id}/assign", json=assign_data, headers=headers
        )
        assert response.status_code == 200

        # Should NOT be able to assign to other company user
        assign_data = {"assignee_id": other_user.id}
        response = await client.post(
            f"/api/todos/{todo.id}/assign", json=assign_data, headers=headers
        )
        assert response.status_code == 403
        assert "other company" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_recruiter_can_assign_todos_to_company_users_only(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_company: Company,
        test_roles: dict,
    ):
        """Test that Recruiter can only assign todos to their company users."""
        recruiter = await self._create_user_with_role(
            db_session, test_company, test_roles, UserRoleEnum.RECRUITER, "recruiter@test.com"
        )
        company_user = await self._create_user_with_role(
            db_session, test_company, test_roles, UserRoleEnum.EMPLOYER, "employer@test.com"
        )

        other_company = await self._create_other_company(db_session)
        other_user = await self._create_user_with_role(
            db_session, other_company, test_roles, UserRoleEnum.RECRUITER, "otherrecruiter@test.com"
        )

        headers = await self._get_auth_headers(client, recruiter)
        todo = await self._create_todo(db_session, recruiter.id, "Recruiter Todo")

        # Should be able to assign to same company user
        assign_data = {"assignee_id": company_user.id}
        response = await client.post(
            f"/api/todos/{todo.id}/assign", json=assign_data, headers=headers
        )
        assert response.status_code == 200

        # Should NOT be able to assign to other company user
        assign_data = {"assignee_id": other_user.id}
        response = await client.post(
            f"/api/todos/{todo.id}/assign", json=assign_data, headers=headers
        )
        assert response.status_code == 403
        assert "other company" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_employer_can_assign_todos_to_company_users_only(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_company: Company,
        test_roles: dict,
    ):
        """Test that Employer can only assign todos to their company users."""
        employer = await self._create_user_with_role(
            db_session, test_company, test_roles, UserRoleEnum.EMPLOYER, "employer@test.com"
        )
        company_user = await self._create_user_with_role(
            db_session, test_company, test_roles, UserRoleEnum.RECRUITER, "recruiter@test.com"
        )

        other_company = await self._create_other_company(db_session)
        other_user = await self._create_user_with_role(
            db_session, other_company, test_roles, UserRoleEnum.EMPLOYER, "otheremployer@test.com"
        )

        headers = await self._get_auth_headers(client, employer)
        todo = await self._create_todo(db_session, employer.id, "Employer Todo")

        # Should be able to assign to same company user
        assign_data = {"assignee_id": company_user.id}
        response = await client.post(
            f"/api/todos/{todo.id}/assign", json=assign_data, headers=headers
        )
        assert response.status_code == 200

        # Should NOT be able to assign to other company user
        assign_data = {"assignee_id": other_user.id}
        response = await client.post(
            f"/api/todos/{todo.id}/assign", json=assign_data, headers=headers
        )
        assert response.status_code == 403
        assert "other company" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_candidate_cannot_assign_todos_to_others(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_company: Company,
        test_roles: dict,
    ):
        """Test that Candidate cannot assign todos to others."""
        candidate = await self._create_user_with_role(
            db_session, test_company, test_roles, UserRoleEnum.CANDIDATE, "candidate@test.com"
        )
        other_user = await self._create_user_with_role(
            db_session, test_company, test_roles, UserRoleEnum.RECRUITER, "recruiter@test.com"
        )

        headers = await self._get_auth_headers(client, candidate)
        todo = await self._create_todo(db_session, candidate.id, "Candidate Todo")

        # Should NOT be able to assign to others
        assign_data = {"assignee_id": other_user.id}
        response = await client.post(
            f"/api/todos/{todo.id}/assign", json=assign_data, headers=headers
        )

        assert response.status_code == 403
        assert "cannot assign" in response.json()["detail"].lower()

    # ===== TODO VIEWING PERMISSIONS =====

    @pytest.mark.asyncio
    async def test_users_can_view_own_and_assigned_todos(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_company: Company,
        test_roles: dict,
    ):
        """Test that users can view their own and assigned todos."""
        user = await self._create_user_with_role(
            db_session, test_company, test_roles, UserRoleEnum.RECRUITER, "recruiter@test.com"
        )
        other_user = await self._create_user_with_role(
            db_session, test_company, test_roles, UserRoleEnum.EMPLOYER, "employer@test.com"
        )

        headers = await self._get_auth_headers(client, user)

        # Create own todo
        own_todo = await self._create_todo(db_session, user.id, "Own Todo")

        # Create todo assigned to user
        assigned_todo = await self._create_todo(db_session, other_user.id, "Assigned Todo", assignee_id=user.id)

        # Should be able to view own todo
        response = await client.get(f"/api/todos/{own_todo.id}", headers=headers)
        assert response.status_code == 200

        # Should be able to view assigned todo
        response = await client.get(f"/api/todos/{assigned_todo.id}", headers=headers)
        assert response.status_code == 200

        # List should include both
        response = await client.get("/api/todos", headers=headers)
        assert response.status_code == 200
        data = response.json()
        todo_ids = [todo["id"] for todo in data["todos"]]
        assert own_todo.id in todo_ids
        assert assigned_todo.id in todo_ids

    @pytest.mark.asyncio
    async def test_users_cannot_view_unrelated_todos(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_company: Company,
        test_roles: dict,
    ):
        """Test that users cannot view todos they didn't create or aren't assigned to."""
        user1 = await self._create_user_with_role(
            db_session, test_company, test_roles, UserRoleEnum.RECRUITER, "recruiter1@test.com"
        )
        user2 = await self._create_user_with_role(
            db_session, test_company, test_roles, UserRoleEnum.RECRUITER, "recruiter2@test.com"
        )

        user1_headers = await self._get_auth_headers(client, user1)

        # User2 creates a todo not assigned to user1
        unrelated_todo = await self._create_todo(db_session, user2.id, "Unrelated Todo")

        # User1 should NOT be able to view user2's unrelated todo
        response = await client.get(f"/api/todos/{unrelated_todo.id}", headers=user1_headers)
        assert response.status_code == 403
        assert "not authorized" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_super_admin_can_view_any_todo(
        self,
        client: AsyncClient,
        super_admin_auth_headers: dict,
        db_session: AsyncSession,
        test_company: Company,
        test_roles: dict,
    ):
        """Test that Super Admin can view any todo."""
        user = await self._create_user_with_role(
            db_session, test_company, test_roles, UserRoleEnum.RECRUITER, "recruiter@test.com"
        )

        # Create todo
        todo = await self._create_todo(db_session, user.id, "User Todo")

        # Super admin should be able to view it
        response = await client.get(
            f"/api/todos/{todo.id}", headers=super_admin_auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == todo.id

    # ===== TODO UPDATE PERMISSIONS =====

    @pytest.mark.asyncio
    async def test_owner_and_assignee_can_update_todos(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_company: Company,
        test_roles: dict,
    ):
        """Test that todo owner and assignee can update todos."""
        owner = await self._create_user_with_role(
            db_session, test_company, test_roles, UserRoleEnum.RECRUITER, "owner@test.com"
        )
        assignee = await self._create_user_with_role(
            db_session, test_company, test_roles, UserRoleEnum.EMPLOYER, "assignee@test.com"
        )

        todo = await self._create_todo(db_session, owner.id, "Todo to Update", assignee_id=assignee.id)

        owner_headers = await self._get_auth_headers(client, owner)
        assignee_headers = await self._get_auth_headers(client, assignee)

        update_data = {"title": "Updated Todo"}

        # Owner should be able to update
        response = await client.put(
            f"/api/todos/{todo.id}", json=update_data, headers=owner_headers
        )
        assert response.status_code == 200

        # Assignee should be able to update
        response = await client.put(
            f"/api/todos/{todo.id}", json=update_data, headers=assignee_headers
        )
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_non_related_users_cannot_update_todos(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_company: Company,
        test_roles: dict,
    ):
        """Test that non-related users cannot update todos."""
        owner = await self._create_user_with_role(
            db_session, test_company, test_roles, UserRoleEnum.RECRUITER, "owner@test.com"
        )
        other_user = await self._create_user_with_role(
            db_session, test_company, test_roles, UserRoleEnum.EMPLOYER, "other@test.com"
        )

        todo = await self._create_todo(db_session, owner.id, "Protected Todo")
        other_user_headers = await self._get_auth_headers(client, other_user)

        update_data = {"title": "Unauthorized Update"}

        response = await client.put(
            f"/api/todos/{todo.id}", json=update_data, headers=other_user_headers
        )

        assert response.status_code == 403
        assert "not authorized" in response.json()["detail"].lower()

    # ===== TODO DELETION PERMISSIONS =====

    @pytest.mark.asyncio
    async def test_only_owner_can_delete_todos(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_company: Company,
        test_roles: dict,
    ):
        """Test that only todo owner can delete todos."""
        owner = await self._create_user_with_role(
            db_session, test_company, test_roles, UserRoleEnum.RECRUITER, "owner@test.com"
        )
        assignee = await self._create_user_with_role(
            db_session, test_company, test_roles, UserRoleEnum.EMPLOYER, "assignee@test.com"
        )

        todo = await self._create_todo(db_session, owner.id, "Todo to Delete", assignee_id=assignee.id)

        owner_headers = await self._get_auth_headers(client, owner)
        assignee_headers = await self._get_auth_headers(client, assignee)

        # Assignee should NOT be able to delete
        response = await client.delete(f"/api/todos/{todo.id}", headers=assignee_headers)
        assert response.status_code == 403
        assert "owner only" in response.json()["detail"].lower()

        # Owner should be able to delete
        response = await client.delete(f"/api/todos/{todo.id}", headers=owner_headers)
        assert response.status_code == 200
        data = response.json()
        assert "deleted" in data["message"].lower()

    @pytest.mark.asyncio
    async def test_super_admin_can_delete_any_todo(
        self,
        client: AsyncClient,
        super_admin_auth_headers: dict,
        db_session: AsyncSession,
        test_company: Company,
        test_roles: dict,
    ):
        """Test that Super Admin can delete any todo."""
        user = await self._create_user_with_role(
            db_session, test_company, test_roles, UserRoleEnum.RECRUITER, "recruiter@test.com"
        )
        todo = await self._create_todo(db_session, user.id, "Todo to Delete by Admin")

        response = await client.delete(
            f"/api/todos/{todo.id}", headers=super_admin_auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert "deleted" in data["message"].lower()

    # ===== TODO COMPLETION PERMISSIONS =====

    @pytest.mark.asyncio
    async def test_assigned_user_can_complete_todos(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_company: Company,
        test_roles: dict,
    ):
        """Test that assigned user can mark todos as complete."""
        owner = await self._create_user_with_role(
            db_session, test_company, test_roles, UserRoleEnum.RECRUITER, "owner@test.com"
        )
        assignee = await self._create_user_with_role(
            db_session, test_company, test_roles, UserRoleEnum.EMPLOYER, "assignee@test.com"
        )

        todo = await self._create_todo(db_session, owner.id, "Todo to Complete", assignee_id=assignee.id)
        assignee_headers = await self._get_auth_headers(client, assignee)

        response = await client.post(f"/api/todos/{todo.id}/complete", headers=assignee_headers)

        assert response.status_code == 200
        data = response.json()
        assert "completed" in data["message"].lower()

    @pytest.mark.asyncio
    async def test_non_assigned_user_cannot_complete_todos(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_company: Company,
        test_roles: dict,
    ):
        """Test that non-assigned users cannot mark todos as complete."""
        owner = await self._create_user_with_role(
            db_session, test_company, test_roles, UserRoleEnum.RECRUITER, "owner@test.com"
        )
        other_user = await self._create_user_with_role(
            db_session, test_company, test_roles, UserRoleEnum.EMPLOYER, "other@test.com"
        )

        todo = await self._create_todo(db_session, owner.id, "Protected Todo")
        other_user_headers = await self._get_auth_headers(client, other_user)

        response = await client.post(f"/api/todos/{todo.id}/complete", headers=other_user_headers)

        assert response.status_code == 403
        assert "not assigned" in response.json()["detail"].lower()

    # ===== TODO ATTACHMENTS PERMISSIONS =====

    @pytest.mark.asyncio
    async def test_related_users_can_manage_attachments(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_company: Company,
        test_roles: dict,
    ):
        """Test that related users can manage todo attachments."""
        owner = await self._create_user_with_role(
            db_session, test_company, test_roles, UserRoleEnum.RECRUITER, "owner@test.com"
        )
        assignee = await self._create_user_with_role(
            db_session, test_company, test_roles, UserRoleEnum.EMPLOYER, "assignee@test.com"
        )

        todo = await self._create_todo(db_session, owner.id, "Todo with Attachments", assignee_id=assignee.id)

        owner_headers = await self._get_auth_headers(client, owner)
        assignee_headers = await self._get_auth_headers(client, assignee)

        # Both should be able to view attachments
        response = await client.get(f"/api/todos/{todo.id}/attachments", headers=owner_headers)
        assert response.status_code == 200

        response = await client.get(f"/api/todos/{todo.id}/attachments", headers=assignee_headers)
        assert response.status_code == 200

        # Both should be able to add attachments
        attachment_data = {"file_path": "/test/attachment.pdf", "description": "Test attachment"}

        response = await client.post(
            f"/api/todos/{todo.id}/attachments", json=attachment_data, headers=owner_headers
        )
        assert response.status_code == 201

        response = await client.post(
            f"/api/todos/{todo.id}/attachments", json=attachment_data, headers=assignee_headers
        )
        assert response.status_code == 201

    # ===== TODO EXTENSIONS PERMISSIONS =====

    @pytest.mark.asyncio
    async def test_assigned_user_can_request_extensions(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_company: Company,
        test_roles: dict,
    ):
        """Test that assigned user can request deadline extensions."""
        owner = await self._create_user_with_role(
            db_session, test_company, test_roles, UserRoleEnum.RECRUITER, "owner@test.com"
        )
        assignee = await self._create_user_with_role(
            db_session, test_company, test_roles, UserRoleEnum.EMPLOYER, "assignee@test.com"
        )

        todo = await self._create_todo(db_session, owner.id, "Todo with Extension", assignee_id=assignee.id)
        assignee_headers = await self._get_auth_headers(client, assignee)

        extension_data = {
            "new_due_date": (datetime.utcnow() + timedelta(days=14)).isoformat(),
            "reason": "Need more time to complete",
        }

        response = await client.post(
            f"/api/todos/{todo.id}/extensions", json=extension_data, headers=assignee_headers
        )

        assert response.status_code == 201
        data = response.json()
        assert "extension" in data

    @pytest.mark.asyncio
    async def test_non_assigned_user_cannot_request_extensions(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_company: Company,
        test_roles: dict,
    ):
        """Test that non-assigned users cannot request extensions."""
        owner = await self._create_user_with_role(
            db_session, test_company, test_roles, UserRoleEnum.RECRUITER, "owner@test.com"
        )
        other_user = await self._create_user_with_role(
            db_session, test_company, test_roles, UserRoleEnum.EMPLOYER, "other@test.com"
        )

        todo = await self._create_todo(db_session, owner.id, "Protected Todo")
        other_user_headers = await self._get_auth_headers(client, other_user)

        extension_data = {
            "new_due_date": (datetime.utcnow() + timedelta(days=14)).isoformat(),
            "reason": "Unauthorized extension request",
        }

        response = await client.post(
            f"/api/todos/{todo.id}/extensions", json=extension_data, headers=other_user_headers
        )

        assert response.status_code == 403
        assert "not assigned" in response.json()["detail"].lower()

    # ===== AUTHENTICATION BOUNDARY TESTS =====

    @pytest.mark.asyncio
    async def test_unauthenticated_todo_access(
        self,
        client: AsyncClient,
        db_session: AsyncSession,
        test_company: Company,
        test_roles: dict,
    ):
        """Test unauthenticated access to todo endpoints."""
        user = await self._create_user_with_role(
            db_session, test_company, test_roles, UserRoleEnum.RECRUITER, "recruiter@test.com"
        )
        todo = await self._create_todo(db_session, user.id, "Test Todo")

        endpoints = [
            ("GET", "/api/todos"),
            ("POST", "/api/todos"),
            ("GET", f"/api/todos/{todo.id}"),
            ("PUT", f"/api/todos/{todo.id}"),
            ("DELETE", f"/api/todos/{todo.id}"),
            ("POST", f"/api/todos/{todo.id}/assign"),
            ("POST", f"/api/todos/{todo.id}/complete"),
            ("GET", f"/api/todos/{todo.id}/attachments"),
            ("POST", f"/api/todos/{todo.id}/attachments"),
            ("GET", f"/api/todos/{todo.id}/extensions"),
            ("POST", f"/api/todos/{todo.id}/extensions"),
        ]

        for method, endpoint in endpoints:
            if method == "GET":
                response = await client.get(endpoint)
            elif method == "POST":
                response = await client.post(endpoint, json={"test": "data"})
            elif method == "PUT":
                response = await client.put(endpoint, json={"test": "data"})
            elif method == "DELETE":
                response = await client.delete(endpoint)

            assert response.status_code == 401, f"Failed for {method} {endpoint}"

    # ===== HELPER METHODS =====

    async def _create_user_with_role(
        self,
        db_session: AsyncSession,
        company: Company,
        test_roles: dict,
        role: UserRoleEnum,
        email: str,
    ) -> User:
        """Create a user with specified role."""
        user = User(
            email=email,
            first_name="Test",
            last_name="User",
            company_id=company.id if company else None,
            hashed_password=auth_service.get_password_hash("testpass123"),
            is_active=True,
            is_admin=(role in [UserRoleEnum.SUPER_ADMIN, UserRoleEnum.COMPANY_ADMIN]),
            require_2fa=False,
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

        # Assign role
        user_role = UserRole(
            user_id=user.id,
            role_id=test_roles[role.value].id,
        )
        db_session.add(user_role)
        await db_session.commit()

        return user

    async def _create_todo(
        self,
        db_session: AsyncSession,
        creator_id: int | None,
        title: str,
        assignee_id: int | None = None,
    ) -> Todo:
        """Create a todo."""
        todo = Todo(
            title=title,
            description=f"Description for {title}",
            creator_id=creator_id,
            assignee_id=assignee_id,
            due_date=datetime.utcnow() + timedelta(days=7),
            priority="medium",
            status="pending",
        )
        db_session.add(todo)
        await db_session.commit()
        await db_session.refresh(todo)
        return todo

    async def _create_other_company(self, db_session: AsyncSession) -> Company:
        """Create another company for cross-company testing."""
        other_company = Company(
            name="Other Test Company",
            email="other@test.com",
            phone="090-9876-5432",
            type=CompanyType.EMPLOYER,
        )
        db_session.add(other_company)
        await db_session.commit()
        await db_session.refresh(other_company)
        return other_company

    async def _get_auth_headers(self, client: AsyncClient, user: User) -> dict:
        """Get authentication headers for a user."""
        login_response = await client.post(
            "/api/auth/login",
            json={"email": user.email, "password": "testpass123"},
        )
        assert login_response.status_code == 200
        token_data = login_response.json()

        # Handle 2FA if required
        if token_data.get("require_2fa"):
            verify_response = await client.post(
                "/api/auth/2fa/verify",
                json={"user_id": user.id, "code": "123456"},
            )
            assert verify_response.status_code == 200
            token_data = verify_response.json()

        return {"Authorization": f"Bearer {token_data['access_token']}"}
