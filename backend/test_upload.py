#!/usr/bin/env python3

import requests
import json

# Test the upload endpoint
def test_upload():
    # Try registration first if login fails
    register_data = {
        "email": "testuser@example.com",
        "password": "testpassword123",
        "full_name": "Test User"
    }
    
    register_response = requests.post(
        "http://localhost:8000/api/auth/register",
        json=register_data
    )
    
    print(f"Register status: {register_response.status_code}")
    
    # Then login
    login_data = {
        "email": "testuser@example.com",
        "password": "testpassword123"
    }
    
    login_response = requests.post(
        "http://localhost:8000/api/auth/login",
        json=login_data
    )
    
    if login_response.status_code != 200:
        print(f"Login failed: {login_response.status_code}")
        print(f"Response: {login_response.text}")
        return
    
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    print(f"Login successful, token: {token[:50]}...")
    
    # Create a small test file
    test_data = b"test image data for avatar upload"
    files = {"file": ("test_avatar.png", test_data, "image/png")}
    
    print("Testing upload endpoint...")
    upload_response = requests.post(
        "http://localhost:8000/api/files/upload",
        headers=headers,
        files=files
    )
    
    print(f"Upload status: {upload_response.status_code}")
    print(f"Upload response: {upload_response.text}")
    
    if upload_response.status_code == 200:
        result = upload_response.json()
        print(f"Upload successful!")
        print(f"S3 key: {result.get('s3_key')}")
        print(f"File size: {result.get('file_size')}")
        print(f"File URL: {result.get('file_url')}")
    else:
        print("Upload failed!")

if __name__ == "__main__":
    test_upload()