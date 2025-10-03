#!/usr/bin/env python3
"""
Test runner for comprehensive workflow relationship tests.
Runs all workflow-related tests and provides detailed coverage report.
"""

import subprocess
import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def run_command(command: str, description: str = "") -> bool:
    """Run a command and return success status."""
    print(f"\n{'='*60}")
    if description:
        print(f"🧪 {description}")
    print(f"{'='*60}")
    print(f"Running: {command}")
    print("-" * 60)
    
    try:
        result = subprocess.run(
            command,
            shell=True,
            cwd=project_root,
            capture_output=False,
            text=True
        )
        
        if result.returncode == 0:
            print(f"✅ {description or 'Command'} completed successfully")
            return True
        else:
            print(f"❌ {description or 'Command'} failed with exit code {result.returncode}")
            return False
            
    except Exception as e:
        print(f"❌ Error running command: {e}")
        return False


def main():
    """Run comprehensive workflow tests."""
    print("🚀 Workflow Relationship Tests")
    print("=" * 60)
    print("Running comprehensive test suite for workflow relationships")
    print("Including permissions, API endpoints, and edge cases")
    
    # Set environment variables for testing
    os.environ["ENVIRONMENT"] = "test"
    os.environ["PYTHONPATH"] = str(project_root)
    
    test_commands = [
        {
            "command": "python3 scripts/verify_workflow_schema.py",
            "description": "Database Schema Verification"
        },
        {
            "command": "python3 scripts/test_schemas_only.py",
            "description": "Schema Validation Tests"
        },
        {
            "command": "python3 -m pytest app/tests/test_workflow_permissions_comprehensive.py -v --tb=short",
            "description": "Comprehensive Permission Tests"
        },
        {
            "command": "python3 -m pytest app/tests/test_workflow_api_permissions.py -v --tb=short",
            "description": "API Permission Tests"
        },
        {
            "command": "python3 -m pytest app/tests/test_workflow_relationships.py -v --tb=short",
            "description": "Basic Relationship Tests"
        },
        {
            "command": "python3 -m pytest app/tests/ -k 'workflow' -v --tb=short --maxfail=5",
            "description": "All Workflow-Related Tests"
        }
    ]
    
    # Optional: Run with coverage if pytest-cov is available
    coverage_commands = [
        {
            "command": "python3 -m pytest app/tests/test_workflow_permissions_comprehensive.py app/tests/test_workflow_api_permissions.py app/tests/test_workflow_relationships.py --cov=app.models --cov=app.schemas --cov=app.crud --cov-report=term-missing --cov-report=html",
            "description": "Coverage Report for Workflow Tests"
        }
    ]
    
    results = []
    
    # Run basic tests first
    for test in test_commands:
        success = run_command(test["command"], test["description"])
        results.append((test["description"], success))
        
        # If basic tests fail, don't continue with advanced tests
        if not success and "Schema" in test["description"]:
            print("\n❌ Basic schema tests failed. Stopping test execution.")
            break
    
    # Try to run coverage if all basic tests pass
    if all(result[1] for result in results if "Schema" in result[0]):
        print("\n🔍 Attempting to run coverage analysis...")
        for test in coverage_commands:
            success = run_command(test["command"], test["description"])
            results.append((test["description"], success))
    
    # Summary
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)
    
    passed = 0
    failed = 0
    
    for description, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{status:<10} {description}")
        if success:
            passed += 1
        else:
            failed += 1
    
    print("-" * 60)
    print(f"Total: {len(results)} | Passed: {passed} | Failed: {failed}")
    
    if failed == 0:
        print("\n🎉 All workflow tests completed successfully!")
        print("\n📋 Test Coverage Includes:")
        print("  ✅ Database schema verification")
        print("  ✅ Model relationship testing")
        print("  ✅ Schema validation")
        print("  ✅ Permission-based access control")
        print("  ✅ API endpoint testing")
        print("  ✅ Cascading soft delete")
        print("  ✅ Cross-company restrictions")
        print("  ✅ Edge cases and error handling")
        print("  ✅ Bulk operations")
        print("  ✅ Concurrent operations")
        
        print("\n🎯 Test Scenarios Covered:")
        print("  • Admin creating workflows with interviews/todos")
        print("  • Employer creating company workflows") 
        print("  • Recruiter creating interviews/todos for existing workflows")
        print("  • Candidate permission restrictions")
        print("  • Workflow soft delete cascading to related items")
        print("  • Invalid workflow_id handling")
        print("  • Cross-company access restrictions")
        print("  • API authentication and authorization")
        print("  • Filtering by workflow_id")
        print("  • Bulk operations with permissions")
        
        return True
    else:
        print(f"\n❌ {failed} test(s) failed. Please review the output above.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)