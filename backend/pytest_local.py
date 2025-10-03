#!/usr/bin/env python3
"""
Local pytest runner for workflow tests.
Uses your local database configuration.
"""

import os
import sys
from pathlib import Path

# Set up environment for local testing
os.environ["ENVIRONMENT"] = "test"
os.environ["DATABASE_URL"] = "mysql+asyncmy://hrms:hrms@localhost:3306/miraiworks_test"
os.environ["PYTHONPATH"] = str(Path(__file__).parent)

# Add project root to Python path
sys.path.insert(0, str(Path(__file__).parent))

if __name__ == "__main__":
    import pytest
    
    # Basic workflow test
    args = [
        "app/tests/test_workflow_relationships.py::TestWorkflowRelationships::test_workflow_relationships_in_schemas",
        "-v",
        "--tb=short"
    ]
    
    print("🧪 Running pytest with local database configuration...")
    print(f"Database: {os.environ['DATABASE_URL']}")
    print("-" * 60)
    
    exit_code = pytest.main(args)
    sys.exit(exit_code)