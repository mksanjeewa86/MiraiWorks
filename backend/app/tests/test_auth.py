import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from app.models.company import Company


class TestAuth:
    """Test authentication endpoints."""
    
    async def test_login_success(self, client: AsyncClient, test_user: User):
        """Test successful login."""
        response = await client.post("/api/auth/login", json={
            "email": test_user.email,
            "password": "testpassword123"
        })
        
        assert response.status_code == 200
        data = response.json()
        
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
        assert "expires_in" in data
        assert "user" in data
        assert data["user"]["email"] == test_user.email

    async def test_login_invalid_email(self, client: AsyncClient):
        """Test login with invalid email."""
        response = await client.post("/api/auth/login", json={
            "email": "nonexistent@example.com",
            "password": "testpassword123"
        })
        
        assert response.status_code == 401
        assert "Invalid email or password" in response.json()["detail"]

    async def test_login_invalid_password(self, client: AsyncClient, test_user: User):
        """Test login with invalid password."""
        response = await client.post("/api/auth/login", json={
            "email": test_user.email,
            "password": "wrongpassword"
        })
        
        assert response.status_code == 401
        assert "Invalid email or password" in response.json()["detail"]

    async def test_login_inactive_user(self, client: AsyncClient, test_user: User, db_session: AsyncSession):
        """Test login with inactive user."""
        # Deactivate user
        test_user.is_active = False
        await db_session.commit()
        
        response = await client.post("/api/auth/login", json={
            "email": test_user.email,
            "password": "testpassword123"
        })
        
        assert response.status_code == 401
        assert "Account is deactivated" in response.json()["detail"]

    async def test_refresh_token(self, client: AsyncClient, test_user: User):
        """Test token refresh."""
        # First login to get tokens
        login_response = await client.post("/api/auth/login", json={
            "email": test_user.email,
            "password": "testpassword123"
        })
        
        assert login_response.status_code == 200
        login_data = login_response.json()
        refresh_token = login_data["refresh_token"]
        
        # Use refresh token
        refresh_response = await client.post("/api/auth/refresh", json={
            "refresh_token": refresh_token
        })
        
        assert refresh_response.status_code == 200
        refresh_data = refresh_response.json()
        
        assert "access_token" in refresh_data
        assert refresh_data["token_type"] == "bearer"
        assert "expires_in" in refresh_data

    async def test_refresh_token_invalid(self, client: AsyncClient):
        """Test refresh with invalid token."""
        response = await client.post("/api/auth/refresh", json={
            "refresh_token": "invalid_token"
        })
        
        assert response.status_code == 401
        assert "Invalid or expired refresh token" in response.json()["detail"]

    async def test_logout(self, client: AsyncClient, test_user: User):
        """Test logout."""
        # First login
        login_response = await client.post("/api/auth/login", json={
            "email": test_user.email,
            "password": "testpassword123"
        })
        
        login_data = login_response.json()
        refresh_token = login_data["refresh_token"]
        
        # Logout
        logout_response = await client.post("/api/auth/logout", json={
            "refresh_token": refresh_token
        })
        
        assert logout_response.status_code == 200
        assert "Logged out successfully" in logout_response.json()["message"]
        
        # Try to use refresh token (should fail)
        refresh_response = await client.post("/api/auth/refresh", json={
            "refresh_token": refresh_token
        })
        
        assert refresh_response.status_code == 401

    async def test_get_current_user(self, client: AsyncClient, auth_headers: dict, test_user: User):
        """Test getting current user info."""
        response = await client.get("/api/auth/me", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["id"] == test_user.id
        assert data["email"] == test_user.email
        assert data["first_name"] == test_user.first_name
        assert data["last_name"] == test_user.last_name
        assert data["company_id"] == test_user.company_id

    async def test_change_password(self, client: AsyncClient, auth_headers: dict):
        """Test changing password."""
        response = await client.post("/api/auth/change-password", 
                                   headers=auth_headers,
                                   json={
                                       "current_password": "testpassword123",
                                       "new_password": "newpassword123"
                                   })
        
        assert response.status_code == 200
        assert "Password changed successfully" in response.json()["message"]

    async def test_change_password_wrong_current(self, client: AsyncClient, auth_headers: dict):
        """Test changing password with wrong current password."""
        response = await client.post("/api/auth/change-password",
                                   headers=auth_headers,
                                   json={
                                       "current_password": "wrongpassword",
                                       "new_password": "newpassword123"
                                   })
        
        assert response.status_code == 401
        assert "Current password is incorrect" in response.json()["detail"]

    async def test_password_reset_request(self, client: AsyncClient, test_user: User):
        """Test password reset request."""
        response = await client.post("/api/auth/password-reset/request", json={
            "email": test_user.email
        })
        
        assert response.status_code == 200
        assert "password reset request has been submitted" in response.json()["message"]

    async def test_password_reset_request_nonexistent_email(self, client: AsyncClient):
        """Test password reset request for nonexistent email."""
        response = await client.post("/api/auth/password-reset/request", json={
            "email": "nonexistent@example.com"
        })
        
        # Should still return success to prevent email enumeration
        assert response.status_code == 200
        assert "password reset request has been submitted" in response.json()["message"]

    async def test_unauthorized_access(self, client: AsyncClient):
        """Test accessing protected endpoint without auth."""
        response = await client.get("/api/auth/me")
        
        assert response.status_code == 401

    async def test_invalid_token_access(self, client: AsyncClient):
        """Test accessing protected endpoint with invalid token."""
        headers = {"Authorization": "Bearer invalid_token"}
        response = await client.get("/api/auth/me", headers=headers)
        
        assert response.status_code == 401