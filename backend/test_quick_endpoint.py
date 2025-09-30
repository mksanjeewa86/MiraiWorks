import asyncio
import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_recruitment_process_endpoint():
    """Quick test to verify recruitment process endpoint works"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Try to create a recruitment process without auth (should fail with 401)
        process_data = {
            "name": "Test Process",
            "description": "Test description"
        }

        response = await client.post("/api/recruitment-processes/", json=process_data)
        print(f"Without auth: {response.status_code}")
        assert response.status_code == 401  # Should require authentication

        # Test that the endpoint exists and routing works
        assert "Unauthorized" in response.text or response.status_code == 401

if __name__ == "__main__":
    asyncio.run(test_recruitment_process_endpoint())