#!/bin/bash

# MiraiWorks Test Runner Script
# Runs comprehensive test suite including backend, frontend, and E2E tests

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test configuration
BACKEND_DIR="backend"
FRONTEND_DIR="frontend-nextjs"
DOCKER_COMPOSE_FILE="docker-compose.test.yml"

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check prerequisites
check_prerequisites() {
    print_status "Checking prerequisites..."
    
    local missing_deps=()
    
    if ! command_exists python3; then
        missing_deps+=("python3")
    fi
    
    if ! command_exists node; then
        missing_deps+=("node")
    fi
    
    if ! command_exists npm; then
        missing_deps+=("npm")
    fi
    
    if ! command_exists docker; then
        missing_deps+=("docker")
    fi
    
    if ! command_exists docker-compose || ! command_exists docker compose; then
        missing_deps+=("docker-compose")
    fi
    
    if [ ${#missing_deps[@]} -ne 0 ]; then
        print_error "Missing dependencies: ${missing_deps[*]}"
        print_error "Please install the missing dependencies and try again."
        exit 1
    fi
    
    print_success "All prerequisites are installed"
}

# Function to setup environment
setup_environment() {
    print_status "Setting up test environment..."
    
    # Create test results directory
    mkdir -p test-results
    
    # Set environment variables
    export CI=true
    export NODE_ENV=test
    export ENVIRONMENT=test
    
    print_success "Test environment setup completed"
}

# Function to run backend tests
run_backend_tests() {
    print_status "Running backend tests..."
    
    cd "$BACKEND_DIR"
    
    # Install dependencies if needed
    if [ ! -d "venv" ]; then
        print_status "Creating Python virtual environment..."
        python3 -m venv venv
    fi
    
    source venv/bin/activate
    
    # Install/upgrade dependencies
    pip install --upgrade pip
    pip install -r requirements.txt
    pip install pytest pytest-asyncio pytest-cov httpx
    
    # Run tests with coverage
    print_status "Executing backend test suite..."
    pytest tests/ -v \
        --cov=app \
        --cov-report=xml \
        --cov-report=html \
        --cov-report=term \
        --cov-fail-under=80
    
    deactivate
    cd ..
    
    print_success "Backend tests completed"
}

# Function to run frontend tests
run_frontend_tests() {
    print_status "Running frontend tests..."
    
    cd "$FRONTEND_DIR"
    
    # Install dependencies if needed
    if [ ! -d "node_modules" ]; then
        print_status "Installing frontend dependencies..."
        npm ci
    fi
    
    # Run unit tests
    print_status "Executing frontend unit tests..."
    npm run test:unit:ci
    
    # Run linting and type checking
    print_status "Running linting and type checking..."
    npm run lint
    npm run type-check
    
    # Build test
    print_status "Testing frontend build..."
    npm run build
    
    cd ..
    
    print_success "Frontend tests completed"
}

# Function to run E2E tests with Docker
run_e2e_tests_docker() {
    print_status "Running E2E tests with Docker..."
    
    # Start services
    docker-compose -f "$DOCKER_COMPOSE_FILE" up --build -d test-db backend-test-server
    
    # Wait for services to be ready
    print_status "Waiting for services to be ready..."
    sleep 30
    
    # Run E2E tests
    docker-compose -f "$DOCKER_COMPOSE_FILE" up --build e2e-test
    
    # Collect test results
    docker-compose -f "$DOCKER_COMPOSE_FILE" up test-results
    
    # Cleanup
    docker-compose -f "$DOCKER_COMPOSE_FILE" down
    
    print_success "E2E tests completed"
}

# Function to run E2E tests locally
run_e2e_tests_local() {
    print_status "Running E2E tests locally..."
    
    # Start backend server in background
    cd "$BACKEND_DIR"
    source venv/bin/activate
    
    # Setup test data
    python scripts/setup_test_data.py
    
    # Start server
    uvicorn app.main:app --host 0.0.0.0 --port 8000 &
    BACKEND_PID=$!
    
    deactivate
    cd ..
    
    # Wait for backend to start
    sleep 10
    
    # Run E2E tests
    cd "$FRONTEND_DIR"
    
    # Install Playwright if needed
    if [ ! -d "node_modules/.bin/playwright" ]; then
        npx playwright install chromium
    fi
    
    # Run tests
    npx playwright test --project=chromium
    
    cd ..
    
    # Stop backend server
    kill $BACKEND_PID 2>/dev/null || true
    
    print_success "E2E tests completed"
}

# Function to run security scans
run_security_scans() {
    print_status "Running security scans..."
    
    # Backend security scan
    cd "$BACKEND_DIR"
    
    if command_exists bandit; then
        print_status "Running Bandit security scan..."
        bandit -r app/ -f json -o ../test-results/bandit-report.json || true
    else
        print_warning "Bandit not installed, skipping Python security scan"
    fi
    
    cd ..
    
    # Frontend security scan
    cd "$FRONTEND_DIR"
    
    print_status "Running npm audit..."
    npm audit --audit-level=high --json > ../test-results/npm-audit.json || true
    
    cd ..
    
    print_success "Security scans completed"
}

# Function to generate test report
generate_test_report() {
    print_status "Generating test report..."
    
    cat > test-results/test-summary.md << EOF
# MiraiWorks Test Summary

Generated on: $(date)

## Test Results

### Backend Tests
- Location: \`$BACKEND_DIR/htmlcov/index.html\`
- Coverage Report: \`$BACKEND_DIR/coverage.xml\`

### Frontend Tests
- Location: \`$FRONTEND_DIR/coverage/\`

### E2E Tests
- Report: \`$FRONTEND_DIR/tests/reports/playwright-report/index.html\`

### Security Scans
- Bandit Report: \`test-results/bandit-report.json\`
- npm audit: \`test-results/npm-audit.json\`

## How to View Reports

### Backend Coverage
\`\`\`bash
open $BACKEND_DIR/htmlcov/index.html
\`\`\`

### Frontend Coverage
\`\`\`bash
open $FRONTEND_DIR/coverage/lcov-report/index.html
\`\`\`

### E2E Test Report
\`\`\`bash
cd $FRONTEND_DIR && npm run test:report
\`\`\`

## Running Individual Test Suites

### Backend Only
\`\`\`bash
./scripts/run-tests.sh --backend-only
\`\`\`

### Frontend Only
\`\`\`bash
./scripts/run-tests.sh --frontend-only
\`\`\`

### E2E Only
\`\`\`bash
./scripts/run-tests.sh --e2e-only
\`\`\`

### With Docker
\`\`\`bash
./scripts/run-tests.sh --docker
\`\`\`
EOF

    print_success "Test report generated: test-results/test-summary.md"
}

# Main function
main() {
    local use_docker=false
    local backend_only=false
    local frontend_only=false
    local e2e_only=false
    local skip_security=false
    
    # Parse command line arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --docker)
                use_docker=true
                shift
                ;;
            --backend-only)
                backend_only=true
                shift
                ;;
            --frontend-only)
                frontend_only=true
                shift
                ;;
            --e2e-only)
                e2e_only=true
                shift
                ;;
            --skip-security)
                skip_security=true
                shift
                ;;
            --help)
                echo "Usage: $0 [OPTIONS]"
                echo ""
                echo "Options:"
                echo "  --docker         Run tests in Docker containers"
                echo "  --backend-only   Run only backend tests"
                echo "  --frontend-only  Run only frontend tests"
                echo "  --e2e-only       Run only E2E tests"
                echo "  --skip-security  Skip security scans"
                echo "  --help           Show this help message"
                exit 0
                ;;
            *)
                print_error "Unknown option: $1"
                exit 1
                ;;
        esac
    done
    
    print_status "Starting MiraiWorks test suite..."
    
    check_prerequisites
    setup_environment
    
    if $use_docker; then
        print_status "Running tests with Docker..."
        
        if ! $backend_only && ! $frontend_only && ! $e2e_only; then
            # Run all tests with Docker
            docker-compose -f "$DOCKER_COMPOSE_FILE" up --build --abort-on-container-exit
            docker-compose -f "$DOCKER_COMPOSE_FILE" up test-results
            docker-compose -f "$DOCKER_COMPOSE_FILE" down
        else
            print_error "Selective test execution not yet supported with Docker"
            exit 1
        fi
    else
        # Run tests locally
        if ! $frontend_only && ! $e2e_only; then
            run_backend_tests
        fi
        
        if ! $backend_only && ! $e2e_only; then
            run_frontend_tests
        fi
        
        if ! $backend_only && ! $frontend_only; then
            run_e2e_tests_local
        fi
        
        if ! $skip_security; then
            run_security_scans
        fi
    fi
    
    generate_test_report
    
    print_success "All tests completed successfully!"
    print_status "View test results in: test-results/"
}

# Run main function with all arguments
main "$@"