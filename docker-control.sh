#!/bin/bash

# MiraiWorks Docker Control Script
# Usage: ./docker-control.sh [command] [environment]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Commands
CMD="${1:-help}"
ENV="${2:-dev}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

show_help() {
    echo "MiraiWorks Docker Control Script"
    echo ""
    echo "Usage: $0 [command] [environment]"
    echo ""
    echo "Commands:"
    echo "  help              Show this help message"
    echo "  build             Build all services"
    echo "  up                Start all services"
    echo "  down              Stop all services"
    echo "  restart           Restart all services"
    echo "  logs              Show logs for all services"
    echo "  logs-backend      Show backend logs"
    echo "  logs-frontend     Show frontend logs"
    echo "  status            Show status of all services"
    echo "  clean             Remove all containers and volumes"
    echo "  reset             Clean and rebuild everything"
    echo "  shell-backend     Open shell in backend container"
    echo "  shell-db          Open MySQL shell"
    echo ""
    echo "Environments:"
    echo "  dev               Development (default)"
    echo "  prod              Production"
    echo ""
    echo "Examples:"
    echo "  $0 up              # Start development environment"
    echo "  $0 up prod         # Start production environment"
    echo "  $0 logs-backend    # Show backend logs"
    echo "  $0 shell-backend   # Open backend shell"
}

get_compose_files() {
    local env="$1"
    if [ "$env" = "prod" ]; then
        echo "-f docker-compose.yml -f docker-compose.prod.yml"
    else
        echo "-f docker-compose.yml -f docker-compose.override.yml"
    fi
}

build_services() {
    local env="$1"
    local compose_files=$(get_compose_files "$env")

    log_info "Building services for $env environment..."
    eval "docker-compose $compose_files build --parallel"
    log_success "Build completed"
}

start_services() {
    local env="$1"
    local compose_files=$(get_compose_files "$env")

    log_info "Starting services for $env environment..."
    eval "docker-compose $compose_files up -d"

    log_info "Waiting for services to be healthy..."
    sleep 10

    eval "docker-compose $compose_files ps"
    log_success "Services started"

    if [ "$env" = "dev" ]; then
        log_info "Development URLs:"
        echo "  - Backend API: http://localhost:8000"
        echo "  - Frontend: http://localhost:3000"
        echo "  - API Docs: http://localhost:8000/docs"
        echo "  - MinIO Console: http://localhost:9001"
        echo "  - MailCatcher: http://localhost:1080"
    fi
}

stop_services() {
    local env="$1"
    local compose_files=$(get_compose_files "$env")

    log_info "Stopping services..."
    eval "docker-compose $compose_files down"
    log_success "Services stopped"
}

restart_services() {
    local env="$1"
    stop_services "$env"
    start_services "$env"
}

show_logs() {
    local env="$1"
    local service="$2"
    local compose_files=$(get_compose_files "$env")

    if [ -n "$service" ]; then
        log_info "Showing logs for $service..."
        eval "docker-compose $compose_files logs -f $service"
    else
        log_info "Showing logs for all services..."
        eval "docker-compose $compose_files logs -f"
    fi
}

show_status() {
    local env="$1"
    local compose_files=$(get_compose_files "$env")

    log_info "Service status:"
    eval "docker-compose $compose_files ps"

    echo ""
    log_info "Container health:"
    docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep miraiworks || echo "No MiraiWorks containers running"
}

clean_all() {
    log_warning "This will remove all containers, volumes, and images for MiraiWorks"
    read -p "Are you sure? (y/N): " -n 1 -r
    echo

    if [[ $REPLY =~ ^[Yy]$ ]]; then
        log_info "Cleaning up..."

        # Stop and remove containers
        docker-compose down -v --remove-orphans 2>/dev/null || true

        # Remove containers
        docker ps -a --filter "name=miraiworks" --format "{{.ID}}" | xargs -r docker rm -f

        # Remove volumes
        docker volume ls --filter "name=miraiworks" --format "{{.Name}}" | xargs -r docker volume rm

        # Remove images
        docker images --filter "reference=miraiworks*" --format "{{.ID}}" | xargs -r docker rmi -f

        log_success "Cleanup completed"
    else
        log_info "Cleanup cancelled"
    fi
}

reset_all() {
    local env="$1"
    clean_all
    build_services "$env"
    start_services "$env"
}

open_shell() {
    local service="$1"
    local env="$2"

    if [ "$service" = "db" ]; then
        log_info "Opening MySQL shell..."
        docker exec -it miraiworks_db mysql -u hrms -phrms miraiworks
    elif [ "$service" = "backend" ]; then
        log_info "Opening backend shell..."
        docker exec -it miraiworks_backend bash
    else
        log_error "Unknown service: $service"
        exit 1
    fi
}

# Main command processing
case "$CMD" in
    "help"|"-h"|"--help")
        show_help
        ;;
    "build")
        build_services "$ENV"
        ;;
    "up")
        start_services "$ENV"
        ;;
    "down")
        stop_services "$ENV"
        ;;
    "restart")
        restart_services "$ENV"
        ;;
    "logs")
        show_logs "$ENV"
        ;;
    "logs-backend")
        show_logs "$ENV" "backend"
        ;;
    "logs-frontend")
        show_logs "$ENV" "frontend"
        ;;
    "status")
        show_status "$ENV"
        ;;
    "clean")
        clean_all
        ;;
    "reset")
        reset_all "$ENV"
        ;;
    "shell-backend")
        open_shell "backend" "$ENV"
        ;;
    "shell-db")
        open_shell "db" "$ENV"
        ;;
    *)
        log_error "Unknown command: $CMD"
        echo ""
        show_help
        exit 1
        ;;
esac