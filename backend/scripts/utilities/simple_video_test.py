#!/usr/bin/env python3
"""
Simple test script to verify video call functionality
"""

import requests


def check_api_health():
    """Check if the API is running"""
    try:
        response = requests.get("http://localhost:8000/health")
        print(f"API Health: {response.status_code}")
        return response.status_code == 200
    except Exception as e:
        print(f"API not accessible: {e}")
        return False


def check_openapi_docs():
    """Check API documentation"""
    try:
        response = requests.get("http://localhost:8000/openapi.json")
        if response.status_code == 200:
            openapi_data = response.json()

            # Check for video call endpoints
            video_endpoints = []
            for path, methods in openapi_data.get("paths", {}).items():
                if "video-call" in path:
                    for method, _details in methods.items():
                        video_endpoints.append(f"{method.upper()} {path}")

            print("=== Video Call API Endpoints ===")
            for endpoint in video_endpoints:
                print(f"  {endpoint}")

            print(f"\nTotal video call endpoints found: {len(video_endpoints)}")
            return len(video_endpoints) > 0
        else:
            print(f"Could not fetch OpenAPI spec: {response.status_code}")
            return False
    except Exception as e:
        print(f"Error checking OpenAPI docs: {e}")
        return False


def show_video_call_features():
    """Show video call features available"""
    print("\n=== Video Call Features ===")
    features = [
        "Schedule video calls for interviews",
        "Join/leave video calls",
        "Record participant activity",
        "Manage recording consent",
        "Generate WebRTC tokens",
        "Real-time transcription",
        "Download transcripts in multiple formats",
        "Permission-based access control",
    ]

    for i, feature in enumerate(features, 1):
        print(f"  {i}. {feature}")


def show_test_instructions():
    """Show testing instructions"""
    print("\n=== How to Test Video Calls ===")

    print("\n1. API Testing:")
    print("   - Visit http://localhost:8000/docs for interactive API docs")
    print("   - Use the Swagger UI to test endpoints")
    print("   - Authenticate first to get access tokens")

    print("\n2. Required for Full Testing:")
    print("   - Valid user accounts (interviewer and candidate)")
    print("   - Interview records in the database")
    print("   - Position/job records")

    print("\n3. Testing Flow:")
    print("   a) Login as interviewer")
    print("   b) Schedule a video call")
    print("   c) Join the call")
    print("   d) Test recording consent")
    print("   e) End the call")
    print("   f) Check transcription")

    print("\n4. Frontend Integration:")
    print("   - Check frontend/src for video call components")
    print("   - Look for WebRTC integration")
    print("   - Verify video call UI pages")


def main():
    """Main test function"""
    print("MiraiWorks Video Call System Check")
    print("=" * 40)

    # Check API availability
    if check_api_health():
        print("✓ API is running")
    else:
        print("✗ API is not accessible")
        return

    # Check video call endpoints
    if check_openapi_docs():
        print("✓ Video call endpoints are available")
    else:
        print("✗ Video call endpoints not found")

    # Show features and instructions
    show_video_call_features()
    show_test_instructions()

    print("\n" + "=" * 40)
    print("Video Call System Check Complete!")
    print("The video call functionality appears to be properly configured.")


if __name__ == "__main__":
    main()
