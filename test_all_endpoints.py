#!/usr/bin/env python3
"""
Comprehensive API Endpoint Testing Script for MiraiWorks Backend

This script tests all API endpoints to ensure they are working correctly.
It covers both authenticated and unauthenticated endpoints.
"""

import requests
import json
import sys
from typing import Dict, List, Any
import time

class APITester:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.access_token = None
        self.results = []
        
    def log_test(self, method: str, endpoint: str, status_code: int, expected: int, details: str = ""):
        """Log test result"""
        success = status_code == expected
        result = {
            "method": method,
            "endpoint": endpoint,
            "status_code": status_code,
            "expected": expected,
            "success": success,
            "details": details
        }
        self.results.append(result)
        
        status = "PASS" if success else "FAIL"
        print(f"{status} {method} {endpoint} - {status_code} (expected {expected}) {details}")
        
    def test_request(self, method: str, endpoint: str, expected_status: int = 200, 
                    data: Dict = None, headers: Dict = None, auth_required: bool = False):
        """Make a test request and log results"""
        url = f"{self.base_url}{endpoint}"
        
        # Set default headers
        if headers is None:
            headers = {"Content-Type": "application/json"}
            
        # Add auth token if required and available
        if auth_required and self.access_token:
            headers["Authorization"] = f"Bearer {self.access_token}"
        
        try:
            if method.upper() == "GET":
                response = requests.get(url, headers=headers, timeout=10)
            elif method.upper() == "POST":
                response = requests.post(url, json=data, headers=headers, timeout=10)
            elif method.upper() == "PUT":
                response = requests.put(url, json=data, headers=headers, timeout=10)
            elif method.upper() == "PATCH":
                response = requests.patch(url, json=data, headers=headers, timeout=10)
            elif method.upper() == "DELETE":
                response = requests.delete(url, headers=headers, timeout=10)
            else:
                self.log_test(method, endpoint, 0, expected_status, "Unsupported method")
                return None
                
            self.log_test(method, endpoint, response.status_code, expected_status)
            return response
            
        except requests.exceptions.RequestException as e:
            self.log_test(method, endpoint, 0, expected_status, f"Request error: {str(e)}")
            return None

    def test_health_endpoints(self):
        """Test basic health endpoints"""
        print("\n[HEALTH] Testing Health Endpoints")
        self.test_request("GET", "/health", 200)
        self.test_request("GET", "/", 200)
        self.test_request("GET", "/webhooks/health", 200)

    def test_auth_endpoints(self):
        """Test authentication endpoints"""
        print("\n[AUTH] Testing Authentication Endpoints")
        
        # Test login with admin user (2FA disabled for testing)
        login_data = {
            "email": "admin@miraiworks.com", 
            "password": "admin123"
        }
        response = self.test_request("POST", "/api/auth/login", 200, login_data)
        
        if response and response.status_code == 200:
            try:
                data = response.json()
                print(f"[DEBUG] Login response data: {data}")
                
                # Check if 2FA is required
                if data.get("require_2fa"):
                    print("[INFO] 2FA required for admin user, attempting with 2FA verification")
                    # For testing purposes, try to complete 2FA flow
                    verify_data = {"code": "123456"}  # Invalid code for testing
                    verify_response = self.test_request("POST", "/api/auth/2fa/verify", 422, verify_data)
                    # This will fail as expected, so we'll test with alternative user
                
                if "access_token" in data and data["access_token"]:
                    self.access_token = data["access_token"]
                    print(f"[SUCCESS] Got access token: {self.access_token[:20]}...")
                elif "data" in data and "access_token" in data["data"]:
                    self.access_token = data["data"]["access_token"]
                    print(f"[SUCCESS] Got access token from data: {self.access_token[:20]}...")
                else:
                    print("[WARNING] Login successful but no access token received")
                    print(f"[DEBUG] Available keys: {list(data.keys())}")
            except Exception as e:
                print(f"[WARNING] Could not parse login response: {str(e)}")
        
        # Test /me endpoint (requires auth)
        self.test_request("GET", "/api/auth/me", 200 if self.access_token else 401, auth_required=True)
        
        # Test refresh (would need refresh token)
        self.test_request("POST", "/api/auth/refresh", 422, {"refresh_token": "invalid"})
        
        # Test password reset request
        self.test_request("POST", "/api/auth/password-reset/request", 422, {"email": "test@example.com"})
        
        # Test 2FA verify
        self.test_request("POST", "/api/auth/2fa/verify", 422, {"code": "123456"})

    def test_dashboard_endpoints(self):
        """Test dashboard endpoints"""
        print("\n[DASHBOARD] Testing Dashboard Endpoints") 
        self.test_request("GET", "/api/dashboard/stats", 200 if self.access_token else 401, auth_required=True)
        self.test_request("GET", "/api/dashboard/activity", 200 if self.access_token else 401, auth_required=True)

    def test_messaging_endpoints(self):
        """Test messaging endpoints"""
        print("\n[MESSAGING] Testing Messaging Endpoints")
        self.test_request("GET", "/api/messaging/conversations", 200 if self.access_token else 401, auth_required=True)
        self.test_request("GET", "/api/messaging/participants/search", 200 if self.access_token else 401, auth_required=True)
        
        # Test conversation read endpoint
        self.test_request("PUT", "/api/messaging/conversations/1/read", 200 if self.access_token else 401, auth_required=True)
        
        # Test messages for a conversation
        self.test_request("GET", "/api/messaging/conversations/1/messages", 200 if self.access_token else 401, auth_required=True)

    def test_resume_endpoints(self):
        """Test resume endpoints"""  
        print("\n[RESUME] Testing Resume Endpoints")
        self.test_request("GET", "/api/resumes", 200 if self.access_token else 401, auth_required=True)
        self.test_request("GET", "/api/resumes/stats", 200 if self.access_token else 401, auth_required=True)
        self.test_request("GET", "/api/resumes/templates/available", 200 if self.access_token else 401, auth_required=True)
        self.test_request("GET", "/api/resumes/search", 200 if self.access_token else 401, auth_required=True)

    def test_interview_endpoints(self):
        """Test interview endpoints"""
        print("\n[INTERVIEW] Testing Interview Endpoints")
        self.test_request("GET", "/api/interviews", 200 if self.access_token else 401, auth_required=True)
        self.test_request("GET", "/api/interviews/stats/summary", 200 if self.access_token else 401, auth_required=True)
        self.test_request("GET", "/api/interviews/calendar/events", 200 if self.access_token else 401, auth_required=True)
        self.test_request("GET", "/api/interviews/calendar/integration-status", 200 if self.access_token else 401, auth_required=True)

    def test_calendar_endpoints(self):
        """Test calendar endpoints"""
        print("\n[CALENDAR] Testing Calendar Endpoints")
        self.test_request("GET", "/api/calendar/accounts", 200 if self.access_token else 401, auth_required=True)
        self.test_request("GET", "/api/calendar/calendars", 200 if self.access_token else 401, auth_required=True)
        self.test_request("GET", "/api/calendar/events", 200 if self.access_token else 401, auth_required=True)

    def test_public_endpoints(self):
        """Test public endpoints (no auth required)"""
        print("\n[PUBLIC] Testing Public Endpoints")
        self.test_request("GET", "/api/public/stats", 200)
        self.test_request("GET", "/api/public/jobs", 200)
        self.test_request("GET", "/api/public/jobs/search", 200)
        self.test_request("GET", "/api/public/companies/search", 200)
        self.test_request("GET", "/api/public/companies", 200)
        self.test_request("GET", "/api/public/sitemap.xml", 200)
        self.test_request("GET", "/api/public/robots.txt", 200)
        self.test_request("GET", "/api/public/rss/jobs.xml", 200)

    def test_stub_endpoints(self):
        """Test temporary stub endpoints"""
        print("\n[STUB] Testing Stub Endpoints")
        self.test_request("GET", "/api/public/jobs", 200)

    def run_all_tests(self):
        """Run all endpoint tests"""
        print("Starting Comprehensive API Endpoint Tests")
        print("=" * 60)
        
        start_time = time.time()
        
        # Run test suites
        self.test_health_endpoints()
        self.test_auth_endpoints()
        self.test_dashboard_endpoints()
        self.test_messaging_endpoints()
        self.test_resume_endpoints()
        self.test_interview_endpoints()
        self.test_calendar_endpoints()
        self.test_public_endpoints()
        self.test_stub_endpoints()
        
        end_time = time.time()
        
        # Print summary
        print("\n" + "=" * 60)
        print("TEST SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.results)
        passed_tests = sum(1 for result in self.results if result["success"])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} [PASS]")
        print(f"Failed: {failed_tests} [FAIL]")
        print(f"Success Rate: {(passed_tests/total_tests*100):.1f}%")
        print(f"Test Duration: {(end_time - start_time):.2f}s")
        
        # Show failed tests
        if failed_tests > 0:
            print(f"\n[FAIL] FAILED TESTS:")
            for result in self.results:
                if not result["success"]:
                    print(f"   {result['method']} {result['endpoint']} - {result['status_code']} {result['details']}")
        
        return passed_tests == total_tests

if __name__ == "__main__":
    tester = APITester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)