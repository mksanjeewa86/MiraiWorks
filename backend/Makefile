# MiraiWorks Backend Testing Makefile
.PHONY: help test test-verbose test-coverage test-single test-fix install-deps clean-test lint format check-all seed-exam-data

# Default target
help:
	@echo "🧪 MiraiWorks Backend Testing Commands"
	@echo "======================================"
	@echo ""
	@echo "Testing:"
	@echo "  test           - Run all tests"
	@echo "  test-fast      - ⚡ Run tests in parallel (FASTEST)"
	@echo "  test-parallel  - Run tests with N workers (WORKERS=8)"
	@echo "  test-failed    - Re-run only failed tests"
	@echo "  test-verbose   - Run tests with verbose output"
	@echo "  test-coverage  - Run tests with coverage report"
	@echo "  test-single    - Run single test for quick validation"
	@echo "  test-fix       - Attempt to fix fixture issues and run tests"
	@echo "  test-collect   - Test collection without running tests"
	@echo "  test-quick     - Quick test (stops on first failure)"
	@echo ""
	@echo "Development:"
	@echo "  install-deps   - Install all dependencies"
	@echo "  lint           - Run code linting"
	@echo "  format         - Format code"
	@echo "  seed-exam-data - Create sample exam data for testing"
	@echo "  seed-resume-data - Create sample resume data for testing"
	@echo "  check-all      - Run all checks (lint + format + test)"
	@echo ""
	@echo "Cleanup:"
	@echo "  clean-test     - Clean test artifacts"
	@echo ""

# Install dependencies
install-deps:
	@echo "📦 Installing dependencies..."
	pip install -r requirements.txt

# Basic test run
test:
	@echo "🧪 Running pytest..."
	@export PYTHONPATH=$$(pwd) && \
	python -m pytest app/tests/ \
		--tb=short \
		--maxfail=3 \
		-q

# Fastest: Parallel execution with all CPU cores
test-fast:
	@echo "⚡ Running tests in parallel (auto-detect CPU cores)..."
	@export PYTHONPATH=$$(pwd) && \
	python -m pytest app/tests/ \
		-n auto \
		--dist loadfile \
		--tb=short \
		--maxfail=1 \
		-q

# Parallel with specific number of workers
WORKERS ?= 4
test-parallel:
	@echo "⚡ Running tests with $(WORKERS) workers..."
	@export PYTHONPATH=$$(pwd) && \
	python -m pytest app/tests/ \
		-n $(WORKERS) \
		--dist loadfile \
		--tb=short \
		-v

# Re-run only failed tests
test-failed:
	@echo "🔄 Re-running failed tests..."
	@export PYTHONPATH=$$(pwd) && \
	python -m pytest app/tests/ \
		--lf \
		-x \
		-v

# Quick test (stops on first failure)
test-quick:
	@echo "⚡ Running quick test (stops on first failure)..."
	@export PYTHONPATH=$$(pwd) && \
	python -m pytest app/tests/ \
		-x \
		-n auto \
		--dist loadfile \
		-q

# Verbose test run
test-verbose:
	@echo "🧪 Running pytest with verbose output..."
	@export PYTHONPATH=$$(pwd) && \
	python -m pytest app/tests/ \
		--tb=long \
		--maxfail=5 \
		-v \
		--durations=10

# Test with coverage
test-coverage:
	@echo "🧪 Running pytest with coverage..."
	@export PYTHONPATH=$$(pwd) && \
	python -m pytest app/tests/ \
		--tb=short \
		--cov=app \
		--cov-report=term-missing \
		--cov-report=html:htmlcov \
		--cov-fail-under=75 \
		-v

# Single test validation
test-single:
	@echo "🧪 Running single test validation..."
	@export PYTHONPATH=$$(pwd) && \
	python -m pytest app/tests/test_fixture_check.py \
		--tb=short \
		-v

# Collection test
test-collect:
	@echo "🧪 Testing pytest collection..."
	@export PYTHONPATH=$$(pwd) && \
	python -m pytest app/tests/ \
		--collect-only \
		-q

# Fix fixtures and run tests
test-fix:
	@echo "🔧 Attempting to fix fixtures and run tests..."
	python scripts/test_local.py --fix-fixtures --single-test

# Run full local validation
test-local:
	@echo "🧪 Running full local validation..."
	python scripts/test_local.py --verbose --coverage

# Linting
lint:
	@echo "🔍 Running linting..."
	ruff check . || echo "Linting completed with issues"

# Code formatting
format:
	@echo "🎨 Formatting code..."
	ruff format .

# Seed exam data
seed-exam-data:
	@echo "🌱 Creating sample exam data..."
	@export PYTHONPATH=$$(pwd) && python scripts/run_seed.py

# Seed resume data
seed-resume-data:
	@echo "🌱 Creating sample resume data..."
	@export PYTHONPATH=$$(pwd) && python scripts/run_resume_seed.py

# Run all checks
check-all: lint format test
	@echo "✅ All checks completed!"

# Clean test artifacts
clean-test:
	@echo "🧹 Cleaning test artifacts..."
	rm -rf htmlcov/
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -f coverage.xml
	rm -f pytest-results.xml
	find . -type d -name "__pycache__" -delete
	find . -name "*.pyc" -delete

# CI simulation (what CI will run)
test-ci:
	@echo "🔄 Simulating CI test run..."
	@export PYTHONPATH=$$(pwd) && \
	export ENVIRONMENT=test && \
	python -m pytest app/tests/ \
		--verbose \
		--tb=long \
		--strict-markers \
		--strict-config \
		--asyncio-mode=auto \
		--maxfail=5 \
		--durations=10 \
		--cov=app \
		--cov-branch \
		--cov-report=term-missing:skip-covered \
		--cov-report=xml:coverage.xml \
		--cov-report=html:htmlcov \
		--cov-fail-under=75 \
		--junit-xml=pytest-results.xml

# Open coverage report
coverage-report:
	@echo "📊 Opening coverage report..."
	@if [ -f htmlcov/index.html ]; then \
		echo "Opening htmlcov/index.html..."; \
		python -m webbrowser htmlcov/index.html || echo "Open htmlcov/index.html manually"; \
	else \
		echo "Coverage report not found. Run 'make test-coverage' first."; \
	fi