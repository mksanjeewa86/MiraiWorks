#!/usr/bin/env python3
"""
Script to create test data for video call testing
"""

import requests

BASE_URL = "http://localhost:8000"


def create_test_interview():
    """Create a test video interview"""

    # First login to get access token
    login_data = {"email": "admin@miraiworks.com", "password": "admin123"}

    try:
        # Login
        print("Logging in...")
        response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
        if response.status_code == 200:
            token = response.json()["access_token"]
            print("Login successful!")
        else:
            print(f"Login failed: {response.status_code}")
            print("Trying alternative credentials...")

            # Try with test account
            login_data["email"] = "test@test.com"
            login_data["password"] = "test123"
            response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)

            if response.status_code == 200:
                token = response.json()["access_token"]
                print("Login successful with test account!")
            else:
                print("All login attempts failed. Please check your credentials.")
                return

        headers = {"Authorization": f"Bearer {token}"}

        # Create a test interview
        interview_data = {
            "title": "Video Call Test Interview",
            "description": "Test interview for video call functionality",
            "interview_type": "video",
            "status": "scheduled",
            "position_id": 1,  # Assuming position exists
            "interviewer_id": 1,
            "candidate_id": 2,
            "scheduled_start": "2024-12-20T14:00:00Z",
            "scheduled_end": "2024-12-20T15:00:00Z",
            "duration_minutes": 60,
            "location": "Video Call",
            "notes": "This is a test video interview for testing video call functionality",
        }

        print("Creating test interview...")
        response = requests.post(
            f"{BASE_URL}/api/interviews", json=interview_data, headers=headers
        )

        if response.status_code in [200, 201]:
            interview = response.json()
            print("Interview created successfully!")
            print(f"Interview ID: {interview.get('id')}")
            print(f"Title: {interview.get('title')}")
            print(f"Type: {interview.get('interview_type')}")
            print(f"Status: {interview.get('status')}")
            print()
            print(
                f"Access the interview at: http://localhost:3000/interviews/{interview.get('id')}"
            )
            print("Click 'Start Video Call' button to test video functionality")
            return interview.get("id")
        else:
            print(f"Failed to create interview: {response.status_code}")
            print(f"Response: {response.text}")

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    print("=== Creating Test Video Interview ===")
    print()
    interview_id = create_test_interview()

    if interview_id:
        print()
        print("=== Test Instructions ===")
        print("1. Open two browser windows")
        print("2. Login with different accounts in each:")
        print("   - Window 1: admin@miraiworks.com / admin123 (Interviewer)")
        print("   - Window 2: candidate@test.com / password123 (Candidate)")
        print(f"3. Navigate to: http://localhost:3000/interviews/{interview_id}")
        print("4. Click 'Start Video Call' button in both windows")
        print("5. Test the video call functionality")
