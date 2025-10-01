#!/usr/bin/env python3
"""
Local test runner script to validate pytest setup before CI/CD
Run this script to test your pytest configuration locally.

Usage:
    python scripts/test_local.py [--fix-fixtures] [--verbose] [--coverage]
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path


def run_command(cmd, cwd=None, env=None):
    """Run command and return success status."""
    try:
        print(f"🔧 Running: {' '.join(cmd)}")
        result = subprocess.run(
            cmd, cwd=cwd, env=env, check=True, capture_output=True, text=True
        )
        print(f"✅ Success: {' '.join(cmd)}")
        if result.stdout:
            print(f"📄 Output:\n{result.stdout}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed: {' '.join(cmd)}")
        print(f"💥 Error: {e.stderr}")
        if e.stdout:
            print(f"📄 Output:\n{e.stdout}")
        return False


def setup_test_environment():
    """Set up test environment variables and files."""
    backend_dir = Path(__file__).parent.parent
    env_test_file = backend_dir / ".env.test"

    print("🔧 Setting up test environment...")

    # Create .env.test file
    env_content = """# Local Test Environment
ENVIRONMENT=test
SECRET_KEY=test-secret-key-for-local-testing
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Database
DATABASE_URL=sqlite+aiosqlite:///:memory:

# Redis (optional for local testing)
REDIS_URL=redis://localhost:6379/1

# Email (Mock for tests)
SMTP_HOST=localhost
SMTP_PORT=587
SMTP_USER=test@example.com
SMTP_PASSWORD=testpassword

# File Storage
STORAGE_TYPE=local
STORAGE_PATH=/tmp/test_storage

# Security
CORS_ORIGINS=["http://localhost:3000"]
ALLOWED_HOSTS=["localhost", "127.0.0.1"]

# Testing flags
DISABLE_AUTH_FOR_TESTS=false
MOCK_EXTERNAL_SERVICES=true
"""

    with open(env_test_file, "w") as f:
        f.write(env_content)

    print(f"✅ Created {env_test_file}")

    # Set up environment variables
    env = os.environ.copy()
    env["PYTHONPATH"] = str(backend_dir)
    env["ENVIRONMENT"] = "test"

    return env, backend_dir


def check_dependencies():
    """Check if required dependencies are installed."""
    print("🔧 Checking dependencies...")

    required_packages = [
        "pytest",
        "pytest-asyncio",
        "pytest-cov",
        "httpx",
        "fastapi",
        "sqlalchemy",
    ]

    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
            print(f"✅ {package} is installed")
        except ImportError:
            print(f"❌ {package} is NOT installed")
            print(f"💡 Install with: pip install {package}")
            return False

    return True


def check_fixture_imports(backend_dir, env):
    """Test if fixtures can be imported correctly."""
    print("🔧 Testing fixture imports...")

    test_script = """
import sys
sys.path.append('.')

try:
    # Test basic imports
    print("Testing basic imports...")
    import pytest
    import pytest_asyncio
    print("✅ pytest imports successful")

    # Test conftest import
    print("Testing conftest import...")
    from app.tests.conftest import *
    print("✅ conftest import successful")

    # Test model imports
    print("Testing model imports...")
    from app.models.user import User
    from app.models.company import Company
    print("✅ model imports successful")

    print("🎉 All fixture imports successful!")

except Exception as e:
    print(f"❌ Fixture import error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
"""

    return run_command([sys.executable, "-c", test_script], cwd=backend_dir, env=env)


def run_pytest_collection(backend_dir, env):
    """Test pytest collection without running tests."""
    print("🔧 Testing pytest collection...")

    return run_command(
        [sys.executable, "-m", "pytest", "app/tests/", "--collect-only", "-v"],
        cwd=backend_dir,
        env=env,
    )


def run_single_test(backend_dir, env):
    """Run a single simple test to validate setup."""
    print("🔧 Running single test validation...")

    # First check if we have working tests
    test_files = list(Path(backend_dir / "app/tests").glob("test_*.py"))
    if not test_files:
        print("❌ No test files found!")
        return False

    # Try to run the fixture check test if it exists
    fixture_test = backend_dir / "app/tests/test_fixture_check.py"
    if fixture_test.exists():
        print("🎯 Running fixture validation test...")
        return run_command(
            [
                sys.executable,
                "-m",
                "pytest",
                "app/tests/test_fixture_check.py",
                "-v",
                "--tb=short",
            ],
            cwd=backend_dir,
            env=env,
        )

    # Otherwise run any available test
    return run_command(
        [
            sys.executable,
            "-m",
            "pytest",
            str(test_files[0]),
            "-v",
            "--tb=short",
            "--maxfail=1",
        ],
        cwd=backend_dir,
        env=env,
    )


def run_full_tests(backend_dir, env, verbose=False, coverage=False):
    """Run full test suite."""
    print("🔧 Running full test suite...")

    cmd = [sys.executable, "-m", "pytest", "app/tests/", "--tb=short", "--maxfail=5"]

    if verbose:
        cmd.extend(["-v", "--durations=10"])

    if coverage:
        cmd.extend(
            [
                "--cov=app",
                "--cov-report=term-missing",
                "--cov-report=html:htmlcov",
                "--cov-fail-under=70",
            ]
        )

    return run_command(cmd, cwd=backend_dir, env=env)


def fix_fixtures():
    """Attempt to fix common fixture issues."""
    print("🔧 Attempting to fix fixture issues...")

    backend_dir = Path(__file__).parent.parent
    conftest_file = backend_dir / "app/tests/conftest.py"

    if not conftest_file.exists():
        print("❌ conftest.py not found!")
        return False

    # Read current conftest
    with open(conftest_file) as f:
        content = f.read()

    fixes_applied = []

    # Fix 1: Remove pytest_asyncio imports if causing issues
    if "import pytest_asyncio" in content:
        content = content.replace("import pytest_asyncio\n", "")
        fixes_applied.append("Removed pytest_asyncio import")

    # Fix 2: Ensure proper pytest.fixture decorators
    content = content.replace("@pytest_asyncio.fixture", "@pytest.fixture")
    if "@pytest_asyncio.fixture" in content:
        fixes_applied.append("Fixed pytest fixture decorators")

    # Fix 3: Add async fixture support
    if (
        '@pytest.fixture(scope="session")' in content
        and "def event_loop" not in content
    ):
        event_loop_fixture = '''

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    import asyncio
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()
'''
        content = content + event_loop_fixture
        fixes_applied.append("Added event_loop fixture")

    if fixes_applied:
        # Backup original
        backup_file = conftest_file.with_suffix(".py.bak")
        with open(backup_file, "w") as f, open(conftest_file) as original:
            f.write(original.read())

        # Write fixed version
        with open(conftest_file, "w") as f:
            f.write(content)

        print(f"✅ Applied fixes: {', '.join(fixes_applied)}")
        print(f"💾 Backup saved to: {backup_file}")
        return True

    print("ℹ️ No fixture issues detected to fix")
    return True


def main():
    parser = argparse.ArgumentParser(description="Local pytest validation script")
    parser.add_argument(
        "--fix-fixtures",
        action="store_true",
        help="Attempt to fix common fixture issues",
    )
    parser.add_argument(
        "--verbose", action="store_true", help="Run tests with verbose output"
    )
    parser.add_argument(
        "--coverage", action="store_true", help="Run tests with coverage reporting"
    )
    parser.add_argument(
        "--single-test",
        action="store_true",
        help="Run only a single test for validation",
    )

    args = parser.parse_args()

    print("MiraiWorks Pytest Local Validation")
    print("=" * 50)

    # Step 1: Check dependencies
    if not check_dependencies():
        print("❌ Missing dependencies. Please install them first.")
        return 1

    # Step 2: Fix fixtures if requested
    if args.fix_fixtures and not fix_fixtures():
        print("❌ Failed to fix fixtures")
        return 1

    # Step 3: Set up environment
    env, backend_dir = setup_test_environment()

    # Step 4: Test fixture imports
    if not check_fixture_imports(backend_dir, env):
        print("❌ Fixture import test failed")
        if not args.fix_fixtures:
            print("💡 Try running with --fix-fixtures")
        return 1

    # Step 5: Test pytest collection
    if not run_pytest_collection(backend_dir, env):
        print("❌ Pytest collection failed")
        return 1

    # Step 6: Run tests
    if args.single_test:
        success = run_single_test(backend_dir, env)
    else:
        success = run_full_tests(backend_dir, env, args.verbose, args.coverage)

    if success:
        print("🎉 All tests passed! Ready for CI/CD")
        return 0
    else:
        print("❌ Some tests failed. Check the output above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
