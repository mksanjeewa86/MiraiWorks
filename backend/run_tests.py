#!/usr/bin/env python3
"""
Quick test runner script for MiraiWorks backend
Optimized for fast database testing with persistent connection
"""
import os
import subprocess
import sys
import time


def run_command(cmd, description=""):
    """Run a command and return success status."""
    if description:
        print(f"\n[RUNNING] {description}")

    start_time = time.time()

    try:
        subprocess.run(cmd, shell=True, check=True, capture_output=False)
        duration = time.time() - start_time
        print(f"[SUCCESS] Completed in {duration:.2f}s")
        return True
    except subprocess.CalledProcessError:
        duration = time.time() - start_time
        print(f"[FAILED] Failed in {duration:.2f}s")
        return False


def check_database():
    """Check if test database is running."""
    try:
        result = subprocess.run(
            [
                "docker",
                "inspect",
                "--format={{.State.Health.Status}}",
                "miraiworks-mysql-test",
            ],
            capture_output=True,
            text=True,
            timeout=5,
        )
        return result.returncode == 0 and "healthy" in result.stdout
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
        return False


def start_database():
    """Start test database if not running."""
    if check_database():
        print("[OK] MySQL test database is already running")
        return True

    print("[STARTING] Starting MySQL test database...")
    success = run_command(
        "docker-compose -f docker-compose.test.yml up -d", "Starting Docker MySQL"
    )

    if not success:
        return False

    # Wait for health check
    print("[WAITING] Waiting for MySQL to be healthy...")
    for attempt in range(30):
        if check_database():
            print(f"[READY] MySQL is ready! (attempt {attempt + 1})")
            return True
        time.sleep(2)
        if attempt % 5 == 0:
            print(f"[WAITING] Still waiting... (attempt {attempt + 1}/30)")

    print("[ERROR] MySQL failed to start within timeout")
    return False


def main():
    """Main test runner."""
    print("MiraiWorks Test Runner")
    print("=" * 40)

    # Change to backend directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    # Parse command line arguments
    test_args = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else None

    # Start database if needed
    if not start_database():
        print("[ERROR] Cannot start database - aborting tests")
        sys.exit(1)

    # Run tests based on arguments
    if test_args is None:
        # Default: run fast tests
        print("\n[TESTING] Running default test suite...")
        tests = [
            ("app/tests/test_simple.py", "Simple tests"),
            ("app/tests/test_auth.py", "Authentication tests"),
        ]

        failed_tests = []
        for test_file, description in tests:
            if os.name == "nt":  # Windows
                cmd = f"set PYTHONPATH=. && python -m pytest {test_file} -v"
            else:  # Unix/Linux/Mac
                cmd = f"PYTHONPATH=. python -m pytest {test_file} -v"
            success = run_command(cmd, f"Running {description}")
            if not success:
                failed_tests.append(description)

        if failed_tests:
            print(f"\n[ERROR] Failed tests: {', '.join(failed_tests)}")
            sys.exit(1)
        else:
            print("\n[SUCCESS] All default tests passed!")

    elif test_args == "all":
        # Run all tests
        if os.name == "nt":  # Windows
            cmd = "set PYTHONPATH=. && python -m pytest app/tests/ -v --maxfail=5"
        else:  # Unix/Linux/Mac
            cmd = "PYTHONPATH=. python -m pytest app/tests/ -v --maxfail=5"
        success = run_command(cmd, "Running ALL tests")
        if not success:
            sys.exit(1)

    elif test_args == "fast":
        # Run only fast tests
        if os.name == "nt":  # Windows
            cmd = "set PYTHONPATH=. && python -m pytest app/tests/test_simple.py app/tests/test_auth.py -v"
        else:  # Unix/Linux/Mac
            cmd = "PYTHONPATH=. python -m pytest app/tests/test_simple.py app/tests/test_auth.py -v"
        success = run_command(cmd, "Running fast tests")
        if not success:
            sys.exit(1)

    elif test_args.startswith("file:"):
        # Run specific test file
        test_file = test_args[5:]
        if os.name == "nt":  # Windows
            cmd = f"set PYTHONPATH=. && python -m pytest {test_file} -v"
        else:  # Unix/Linux/Mac
            cmd = f"PYTHONPATH=. python -m pytest {test_file} -v"
        success = run_command(cmd, f"Running {test_file}")
        if not success:
            sys.exit(1)

    else:
        # Pass through custom arguments
        if os.name == "nt":  # Windows
            cmd = f"set PYTHONPATH=. && python -m pytest {test_args}"
        else:  # Unix/Linux/Mac
            cmd = f"PYTHONPATH=. python -m pytest {test_args}"
        success = run_command(cmd, f"Running custom test: {test_args}")
        if not success:
            sys.exit(1)

    print("\n[SUCCESS] All tests completed successfully!")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[INTERRUPTED] Tests interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n[ERROR] Unexpected error: {e}")
        sys.exit(1)
