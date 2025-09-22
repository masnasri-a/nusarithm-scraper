#!/bin/bash

# Development run script for AI-Assisted News Scraper API

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

# Check if we're in the right directory
if [ ! -f "start_server.py" ]; then
    error "start_server.py not found. Please run this script from the project root directory."
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    warn "Virtual environment not found. Creating..."
    python3 -m venv venv
    log "Virtual environment created"
fi

# Activate virtual environment
log "Activating virtual environment..."
source venv/bin/activate

# Install/update dependencies
log "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Test imports
log "Testing imports..."
python test_imports.py

if [ $? -eq 0 ]; then
    log "All imports successful! Starting server..."
    
    # Load environment variables
    if [ -f ".env" ]; then
        log "Loading environment variables from .env"
        export $(cat .env | grep -v '^#' | xargs)
    else
        warn ".env file not found. Using default settings."
    fi
    
    # Start the server
    info "Starting API server on http://localhost:6777"
    info "API Documentation: http://localhost:6777/docs"
    
    python start_server.py --host 0.0.0.0 --port 6777 --reload
else
    error "Import test failed. Please check the error messages above."
    exit 1
fi