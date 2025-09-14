@echo off
REM MiraiWorks Pytest CI/CD Test Runner
REM Usage: test_run.bat [test-type]
REM test-type: quick, coverage, single, fix, ci

echo ====================================
echo MiraiWorks Pytest Test Runner
echo ====================================

REM Set environment variables
set PYTHONPATH=%CD%
set ENVIRONMENT=test

REM Check if parameter provided
if "%1"=="quick" goto quick_test
if "%1"=="coverage" goto coverage_test
if "%1"=="single" goto single_test
if "%1"=="fix" goto fix_test
if "%1"=="ci" goto ci_test
if "%1"=="collect" goto collect_test

REM Default: Quick test
:quick_test
echo Running quick test validation...
python -m pytest app/tests/ --tb=short --maxfail=3 -q
goto end

:coverage_test
echo Running tests with coverage...
python -m pytest app/tests/ --tb=short --cov=app --cov-report=term-missing --cov-report=html:htmlcov --cov-fail-under=75 -v
goto end

:single_test
echo Running single test validation...
if exist "app/tests/test_fixture_check.py" (
    python -m pytest app/tests/test_fixture_check.py --tb=short -v
) else (
    echo No fixture check test found, running first available test...
    python -m pytest app/tests/ --maxfail=1 --tb=short -v
)
goto end

:fix_test
echo Attempting to fix fixtures and run tests...
echo This would run fixture fixes - not implemented in batch
goto single_test

:ci_test
echo Running CI simulation...
python -m pytest app/tests/ --verbose --tb=long --strict-markers --strict-config --asyncio-mode=auto --maxfail=5 --durations=10 --cov=app --cov-branch --cov-report=term-missing:skip-covered --cov-report=xml:coverage.xml --cov-report=html:htmlcov --cov-fail-under=75 --junit-xml=pytest-results.xml
goto end

:collect_test
echo Testing pytest collection...
python -m pytest app/tests/ --collect-only -q
goto end

:end
echo.
echo Test execution completed!
echo Use 'test_run.bat coverage' for coverage report
echo Use 'test_run.bat ci' for full CI simulation