# MiraiWorks Project Makefile
# Quick commands for development and CI/CD

.PHONY: help install-hooks check-imports fix-imports validate-imports clean-imports sort-imports lint format test ci

# Default target
help:
	@echo "MiraiWorks Development Commands"
	@echo "================================"
	@echo ""
	@echo "🔧 Setup:"
	@echo "  install-hooks     Install pre-commit hooks"
	@echo ""
	@echo "📦 Import Management:"
	@echo "  check-imports     Check for unused imports and errors (no fixes)"
	@echo "  fix-imports       Auto-fix unused imports and sorting"
	@echo "  validate-imports  Comprehensive import validation"
	@echo "  clean-imports     Remove unused imports only"
	@echo "  sort-imports      Sort imports only"
	@echo ""
	@echo "🧹 Code Quality:"
	@echo "  lint             Run all linting checks"
	@echo "  format           Format code with ruff"
	@echo "  test             Run tests"
	@echo "  ci               Run full CI checks locally"
	@echo ""
	@echo "📊 Usage Examples:"
	@echo "  make check-imports    # Check what needs fixing"
	@echo "  make fix-imports      # Fix everything automatically"
	@echo "  make ci               # Full pre-deployment check"

# Setup commands
install-hooks:
	@echo "🔧 Installing pre-commit hooks..."
	pip install pre-commit
	pre-commit install
	@echo "✅ Pre-commit hooks installed"

# Import management commands
check-imports:
	@echo "🔍 Checking for import issues..."
	@cd backend && python -m ruff check app/ --select F401,I001
	@echo "💡 To fix issues, run: make fix-imports"

fix-imports:
	@echo "🔧 Fixing import issues..."
	@cd backend && python -m ruff check app/ --select F401,I001 --fix
	@echo "✅ Import issues fixed"

validate-imports:
	@echo "🔍 Running comprehensive import validation..."
	@cd backend && python scripts/validate_imports.py --verbose

clean-imports:
	@echo "🗑️ Removing unused imports..."
	@cd backend && python -m ruff check app/ --select F401 --fix
	@echo "✅ Unused imports removed"

sort-imports:
	@echo "📝 Sorting imports..."
	@cd backend && python -m ruff check app/ --select I001 --fix
	@echo "✅ Imports sorted"

# Code quality commands
lint:
	@echo "🔍 Running linting checks..."
	@cd backend && python -m ruff check app/
	@echo "✅ Linting complete"

format:
	@echo "🎨 Formatting code..."
	@cd backend && python -m ruff format app/
	@echo "✅ Code formatted"

# Test commands
test:
	@echo "🧪 Running tests with Docker MySQL..."
	@cd backend && PYTHONPATH=. python -m pytest app/tests/ -v
	@echo "✅ Tests complete"

test-db-start:
	@echo "🐳 Starting MySQL test database..."
	@docker-compose -f docker-compose.test.yml up -d
	@echo "✅ MySQL test database started"

test-db-stop:
	@echo "🛑 Stopping MySQL test database..."
	@docker-compose -f docker-compose.test.yml down -v
	@echo "✅ MySQL test database stopped"

test-db-restart:
	@echo "🔄 Restarting MySQL test database..."
	@docker-compose -f docker-compose.test.yml down -v
	@docker-compose -f docker-compose.test.yml up -d
	@echo "✅ MySQL test database restarted"

test-imports:
	@echo "🧪 Testing import functionality..."
	@cd backend && python -c "from app.main import app; print('✅ Main app imports successfully')"
	@cd backend && python -c "import app.endpoints; print('✅ Endpoints import successfully')"
	@cd backend && python -c "import app.services; print('✅ Services import successfully')"
	@echo "✅ Import tests passed"

# CI/CD simulation
ci:
	@echo "🚀 Running full CI checks locally..."
	@echo ""
	@echo "1/6 🔍 Checking imports..."
	@make check-imports || { echo "❌ Import check failed"; exit 1; }
	@echo ""
	@echo "2/6 🧹 Validating import functionality..."
	@make test-imports || { echo "❌ Import test failed"; exit 1; }
	@echo ""
	@echo "3/6 🔍 Running linting..."
	@make lint || { echo "❌ Linting failed"; exit 1; }
	@echo ""
	@echo "4/6 🎨 Checking formatting..."
	@cd backend && python -m ruff format app/ --check || { echo "❌ Formatting check failed"; exit 1; }
	@echo ""
	@echo "5/6 🧪 Running tests..."
	@make test || { echo "❌ Tests failed"; exit 1; }
	@echo ""
	@echo "6/6 📊 Comprehensive import validation..."
	@make validate-imports || { echo "❌ Import validation failed"; exit 1; }
	@echo ""
	@echo "✅ All CI checks passed! Ready for deployment 🚀"

# Quick fix commands
quick-fix:
	@echo "⚡ Running quick fixes..."
	@make fix-imports
	@make format
	@echo "✅ Quick fixes applied"

# Development workflow
dev-check:
	@echo "👨‍💻 Running development checks..."
	@make check-imports
	@make lint
	@echo "✅ Development checks complete"

# Clean up commands
clean:
	@echo "🧹 Cleaning up..."
	@find backend -name "*.pyc" -delete
	@find backend -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
	@echo "✅ Cleanup complete"

# Help for import issues
import-help:
	@echo "🆘 Import Issues Help"
	@echo "===================="
	@echo ""
	@echo "Common import problems and solutions:"
	@echo ""
	@echo "❌ Unused imports:"
	@echo "   Solution: make clean-imports"
	@echo ""
	@echo "❌ Unsorted imports:"
	@echo "   Solution: make sort-imports"
	@echo ""
	@echo "❌ Missing imports:"
	@echo "   Solution: Check if module exists and fix manually"
	@echo ""
	@echo "❌ Wrong imports:"
	@echo "   Solution: Update import path (e.g., app.dependencies instead of app.services.auth_service)"
	@echo ""
	@echo "🔧 Quick fix all: make fix-imports"
	@echo "🔍 Diagnose issues: make validate-imports"