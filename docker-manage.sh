#!/bin/bash

# Docker management script for AI-Assisted News Scraper API

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}"
}

info() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')] INFO: $1${NC}"
}

# Help function
show_help() {
    echo "Docker management script for AI-Assisted News Scraper API"
    echo ""
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  dev           Start development environment"
    echo "  prod          Start production environment"
    echo "  stop          Stop all containers"
    echo "  restart       Restart all containers"
    echo "  logs          Show logs from all containers"
    echo "  logs-api      Show logs from API container"
    echo "  logs-frontend Show logs from frontend container"
    echo "  build         Build all images"
    echo "  clean         Clean up containers, images, and volumes"
    echo "  reset         Reset everything (clean + rebuild)"
    echo "  status        Show container status"
    echo "  shell-api     Open shell in API container"
    echo "  shell-frontend Open shell in frontend container"
    echo "  backup        Backup database and volumes"
    echo "  restore       Restore from backup"
    echo "  help          Show this help message"
    echo ""
}

# Check if .env file exists
check_env() {
    if [ ! -f .env ]; then
        warn ".env file not found. Creating from .env.example..."
        if [ -f .env.example ]; then
            cp .env.example .env
            info "Please edit .env file with your actual configuration values"
        else
            error ".env.example file not found. Please create .env file manually."
            exit 1
        fi
    fi
}

# Development environment
start_dev() {
    log "Starting development environment..."
    check_env
    docker-compose -f docker-compose.yml up -d
    log "Development environment started successfully!"
    info "API: http://localhost:6777"
    info "Frontend: http://localhost:3677"
    info "API Docs: http://localhost:6777/docs"
}

# Production environment
start_prod() {
    log "Starting production environment..."
    check_env
    docker-compose -f docker-compose.prod.yml up -d
    log "Production environment started successfully!"
    info "Application: http://localhost"
    info "API: http://localhost/api"
}

# Stop containers
stop_containers() {
    log "Stopping all containers..."
    docker-compose -f docker-compose.yml down 2>/dev/null || true
    docker-compose -f docker-compose.prod.yml down 2>/dev/null || true
    log "All containers stopped"
}

# Restart containers
restart_containers() {
    log "Restarting containers..."
    stop_containers
    start_dev
}

# Show logs
show_logs() {
    if [ -n "$1" ]; then
        docker-compose -f docker-compose.yml logs -f "$1"
    else
        docker-compose -f docker-compose.yml logs -f
    fi
}

# Build images
build_images() {
    log "Building all images..."
    docker-compose -f docker-compose.yml build --no-cache
    docker-compose -f docker-compose.prod.yml build --no-cache
    log "All images built successfully!"
}

# Clean up
clean_up() {
    warn "This will remove all containers, images, and volumes. Are you sure? (y/N)"
    read -r response
    if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
        log "Cleaning up..."
        stop_containers
        docker system prune -af --volumes
        log "Cleanup completed"
    else
        info "Cleanup cancelled"
    fi
}

# Reset everything
reset_all() {
    warn "This will reset everything (containers, images, volumes). Are you sure? (y/N)"
    read -r response
    if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
        clean_up
        build_images
        start_dev
    else
        info "Reset cancelled"
    fi
}

# Show container status
show_status() {
    log "Container status:"
    docker-compose -f docker-compose.yml ps
    echo ""
    log "Production containers:"
    docker-compose -f docker-compose.prod.yml ps 2>/dev/null || info "Production environment not running"
}

# Open shell in container
open_shell() {
    container="$1"
    if [ -z "$container" ]; then
        error "Container name required"
        exit 1
    fi
    
    log "Opening shell in $container container..."
    docker-compose -f docker-compose.yml exec "$container" /bin/sh
}

# Backup
backup_data() {
    log "Creating backup..."
    timestamp=$(date +%Y%m%d_%H%M%S)
    backup_dir="backups/$timestamp"
    mkdir -p "$backup_dir"
    
    # Backup database
    if docker-compose -f docker-compose.yml ps | grep -q scraper-api; then
        docker-compose -f docker-compose.yml exec scraper-api cp /app/data/scraper.db /tmp/backup.db
        docker cp "$(docker-compose -f docker-compose.yml ps -q scraper-api)":/tmp/backup.db "$backup_dir/scraper.db"
        log "Database backed up to $backup_dir/scraper.db"
    fi
    
    # Backup volumes
    docker run --rm -v scraper_data:/data -v "$(pwd)/$backup_dir":/backup alpine tar czf /backup/volumes.tar.gz -C /data .
    log "Volumes backed up to $backup_dir/volumes.tar.gz"
    
    log "Backup completed: $backup_dir"
}

# Restore
restore_data() {
    if [ -z "$1" ]; then
        error "Backup directory required"
        echo "Usage: $0 restore [backup_directory]"
        exit 1
    fi
    
    backup_dir="$1"
    if [ ! -d "$backup_dir" ]; then
        error "Backup directory not found: $backup_dir"
        exit 1
    fi
    
    warn "This will restore data from $backup_dir. Current data will be lost. Continue? (y/N)"
    read -r response
    if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
        log "Restoring from backup..."
        
        # Stop containers
        stop_containers
        
        # Restore database
        if [ -f "$backup_dir/scraper.db" ]; then
            docker run --rm -v scraper_data:/data -v "$(pwd)/$backup_dir":/backup alpine cp /backup/scraper.db /data/
            log "Database restored"
        fi
        
        # Restore volumes
        if [ -f "$backup_dir/volumes.tar.gz" ]; then
            docker run --rm -v scraper_data:/data -v "$(pwd)/$backup_dir":/backup alpine tar xzf /backup/volumes.tar.gz -C /data
            log "Volumes restored"
        fi
        
        # Start containers
        start_dev
        log "Restore completed"
    else
        info "Restore cancelled"
    fi
}

# Main script logic
case "${1:-help}" in
    dev)
        start_dev
        ;;
    prod)
        start_prod
        ;;
    stop)
        stop_containers
        ;;
    restart)
        restart_containers
        ;;
    logs)
        show_logs
        ;;
    logs-api)
        show_logs scraper-api
        ;;
    logs-frontend)
        show_logs scraper-frontend
        ;;
    build)
        build_images
        ;;
    clean)
        clean_up
        ;;
    reset)
        reset_all
        ;;
    status)
        show_status
        ;;
    shell-api)
        open_shell scraper-api
        ;;
    shell-frontend)
        open_shell scraper-frontend
        ;;
    backup)
        backup_data
        ;;
    restore)
        restore_data "$2"
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        error "Unknown command: $1"
        echo ""
        show_help
        exit 1
        ;;
esac