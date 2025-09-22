#!/bin/bash

# MiraiWorks Video Call Feature Deployment Script
# This script deploys the video call functionality with proper optimizations

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
ENVIRONMENT=${1:-development}
BACKUP_ENABLED=${BACKUP_ENABLED:-true}
MIGRATION_CHECK=${MIGRATION_CHECK:-true}

echo -e "${BLUE}🚀 Starting MiraiWorks Video Call Feature Deployment${NC}"
echo -e "${BLUE}Environment: ${ENVIRONMENT}${NC}"

# Function to print colored output
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Check if Docker is installed
    if ! command -v docker &> /dev/null; then
        log_error "Docker is required but not installed"
        exit 1
    fi
    
    # Check if Docker Compose is installed
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose is required but not installed"
        exit 1
    fi
    
    # Check if required environment variables are set
    if [[ "$ENVIRONMENT" == "production" ]]; then
        required_vars=("JWT_SECRET_KEY" "COTURN_SECRET" "EXTERNAL_IP")
        for var in "${required_vars[@]}"; do
            if [[ -z "${!var}" ]]; then
                log_error "Required environment variable $var is not set"
                exit 1
            fi
        done
    fi
    
    log_success "Prerequisites check passed"
}

# Backup database
backup_database() {
    if [[ "$BACKUP_ENABLED" == "true" ]]; then
        log_info "Creating database backup..."
        
        # Create backup directory
        mkdir -p backups
        
        # Generate backup filename with timestamp
        backup_file="backups/miraiworks_backup_$(date +%Y%m%d_%H%M%S).sql"
        
        # Create database backup
        docker-compose -f docker/docker-compose.video.yml exec -T postgres \
            pg_dump -U postgres miraiworks > "$backup_file"
        
        log_success "Database backup created: $backup_file"
    else
        log_warning "Database backup skipped"
    fi
}

# Run database migrations
run_migrations() {
    if [[ "$MIGRATION_CHECK" == "true" ]]; then
        log_info "Running database migrations..."
        
        # Start database service if not running
        docker-compose -f docker/docker-compose.video.yml up -d postgres
        
        # Wait for database to be ready
        log_info "Waiting for database to be ready..."
        sleep 10
        
        # Run Alembic migrations
        docker-compose -f docker/docker-compose.video.yml run --rm miraiworks-video \
            alembic upgrade head
        
        log_success "Database migrations completed"
    else
        log_warning "Database migrations skipped"
    fi
}

# Build and deploy services
deploy_services() {
    log_info "Building and deploying services..."
    
    # Build images
    log_info "Building Docker images..."
    docker-compose -f docker/docker-compose.video.yml build --no-cache
    
    # Start services
    log_info "Starting services..."
    docker-compose -f docker/docker-compose.video.yml up -d
    
    # Wait for services to be healthy
    log_info "Waiting for services to be healthy..."
    sleep 30
    
    # Check service health
    if docker-compose -f docker/docker-compose.video.yml ps | grep -q "unhealthy\|Exit"; then
        log_error "Some services are not healthy"
        docker-compose -f docker/docker-compose.video.yml ps
        exit 1
    fi
    
    log_success "Services deployed successfully"
}

# Run post-deployment tests
run_post_deployment_tests() {
    log_info "Running post-deployment tests..."
    
    # Health check
    if curl -f http://localhost:8000/health > /dev/null 2>&1; then
        log_success "Health check passed"
    else
        log_error "Health check failed"
        exit 1
    fi
    
    # Run basic API tests
    log_info "Running API tests..."
    docker-compose -f docker/docker-compose.video.yml run --rm miraiworks-video \
        python -m pytest app/tests/test_video_call_endpoints.py::TestVideoCallEndpoints::test_schedule_video_call_success -v
    
    log_success "Post-deployment tests passed"
}

# Optimize performance
optimize_performance() {
    log_info "Running performance optimizations..."
    
    # Run optimization script
    docker-compose -f docker/docker-compose.video.yml exec miraiworks-video \
        python -c "
import asyncio
from app.database import get_session
from app.utils.video_optimization import run_optimization_cycle

async def main():
    async with get_session() as db:
        results = await run_optimization_cycle(db)
        print('Optimization results:', results)

asyncio.run(main())
"
    
    log_success "Performance optimization completed"
}

# Setup monitoring
setup_monitoring() {
    log_info "Setting up monitoring..."
    
    # Ensure Prometheus and Grafana are running
    docker-compose -f docker/docker-compose.video.yml up -d prometheus grafana
    
    # Wait for services to start
    sleep 10
    
    log_success "Monitoring setup completed"
    log_info "Grafana dashboard: http://localhost:3000 (admin/admin)"
    log_info "Prometheus: http://localhost:9090"
}

# Print deployment summary
print_summary() {
    log_success "🎉 Deployment completed successfully!"
    echo
    echo -e "${BLUE}=== Deployment Summary ===${NC}"
    echo -e "${GREEN}✅ Environment: ${ENVIRONMENT}${NC}"
    echo -e "${GREEN}✅ Services: Running${NC}"
    echo -e "${GREEN}✅ Database: Migrated${NC}"
    echo -e "${GREEN}✅ Performance: Optimized${NC}"
    echo -e "${GREEN}✅ Monitoring: Enabled${NC}"
    echo
    echo -e "${BLUE}=== Service URLs ===${NC}"
    echo -e "${GREEN}🌐 Application: http://localhost${NC}"
    echo -e "${GREEN}📊 Grafana: http://localhost:3000${NC}"
    echo -e "${GREEN}📈 Prometheus: http://localhost:9090${NC}"
    echo
    echo -e "${BLUE}=== Next Steps ===${NC}"
    echo -e "${YELLOW}1. Configure your STUN/TURN server settings${NC}"
    echo -e "${YELLOW}2. Set up SSL certificates for production${NC}"
    echo -e "${YELLOW}3. Configure transcription service API keys${NC}"
    echo -e "${YELLOW}4. Test video call functionality${NC}"
    echo
}

# Error handling
handle_error() {
    local exit_code=$?
    log_error "Deployment failed with exit code $exit_code"
    
    # Show logs for debugging
    log_info "Showing service logs for debugging..."
    docker-compose -f docker/docker-compose.video.yml logs --tail=50
    
    exit $exit_code
}

# Set up error handling
trap handle_error ERR

# Main deployment flow
main() {
    log_info "Starting deployment process..."
    
    check_prerequisites
    backup_database
    run_migrations
    deploy_services
    run_post_deployment_tests
    optimize_performance
    setup_monitoring
    print_summary
}

# Environment-specific configurations
case $ENVIRONMENT in
    development)
        log_info "Development environment configuration"
        export DEBUG=true
        export LOG_LEVEL=debug
        ;;
    staging)
        log_info "Staging environment configuration"
        export DEBUG=false
        export LOG_LEVEL=info
        ;;
    production)
        log_info "Production environment configuration"
        export DEBUG=false
        export LOG_LEVEL=warning
        
        # Additional production checks
        if [[ -z "$SSL_CERT_PATH" ]]; then
            log_warning "SSL certificates not configured for production"
        fi
        ;;
    *)
        log_error "Unknown environment: $ENVIRONMENT"
        echo "Usage: $0 [development|staging|production]"
        exit 1
        ;;
esac

# Run main deployment
main

log_success "🚀 MiraiWorks Video Call Feature deployment completed!"