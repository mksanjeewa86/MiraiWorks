#!/usr/bin/env python3
"""
Test script to verify MBTI endpoints are working
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_endpoint_exists(endpoint):
    """Test if an endpoint exists (even without auth)"""
    url = f"{BASE_URL}{endpoint}"
    try:
        response = requests.get(url, timeout=5)
        print(f"OK {endpoint}: Status {response.status_code}")
        if response.status_code == 401:
            print(f"   Auth required (good - endpoint exists)")
            return True
        elif response.status_code == 404:
            print(f"   FAIL Endpoint not found")
            return False
        else:
            print(f"   Unexpected status: {response.status_code}")
            return True
    except requests.exceptions.ConnectionError:
        print(f"FAIL {endpoint}: Connection refused - server not running?")
        return False
    except requests.exceptions.Timeout:
        print(f"FAIL {endpoint}: Timeout")
        return False
    except Exception as e:
        print(f"FAIL {endpoint}: Error - {e}")
        return False

def main():
    print("Testing MBTI endpoints...")
    print("=" * 50)

    endpoints = [
        "/api/mbti/progress",
        "/api/mbti/summary",
        "/api/mbti/start",
        "/api/mbti/questions",
        "/api/mbti/result",
        "/api/mbti/types"
    ]

    results = []
    for endpoint in endpoints:
        result = test_endpoint_exists(endpoint)
        results.append((endpoint, result))
        print()

    print("=" * 50)
    print("SUMMARY:")
    working = sum(1 for _, result in results if result)
    total = len(results)
    print(f"Working endpoints: {working}/{total}")

    for endpoint, result in results:
        status = "OK" if result else "FAIL"
        print(f"{status} {endpoint}")

if __name__ == "__main__":
    main()