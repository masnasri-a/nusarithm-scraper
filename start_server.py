#!/usr/bin/env python3
"""
Startup script for the AI-Assisted News Scraper API
This script ensures proper Python path setup and starts the uvicorn server
"""

import os
import sys
import subprocess
from pathlib import Path

def setup_python_path():
    """Setup Python path to ensure proper module imports"""
    # Get the directory containing this script
    script_dir = Path(__file__).parent.absolute()
    
    # Add the project root to Python path
    project_root = script_dir
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    
    # Set PYTHONPATH environment variable
    current_pythonpath = os.environ.get('PYTHONPATH', '')
    if str(project_root) not in current_pythonpath:
        if current_pythonpath:
            os.environ['PYTHONPATH'] = f"{project_root}:{current_pythonpath}"
        else:
            os.environ['PYTHONPATH'] = str(project_root)
    
    print(f"Python path set to: {sys.path[:3]}...")
    print(f"PYTHONPATH: {os.environ.get('PYTHONPATH', 'Not set')}")

def start_server(host="0.0.0.0", port=6777, reload=False):
    """Start the uvicorn server with proper configuration"""
    setup_python_path()
    
    # Import here to ensure path is set up
    try:
        import uvicorn
    except ImportError:
        print("Error: uvicorn not installed. Install with: pip install uvicorn")
        sys.exit(1)
    
    # Start the server
    print(f"Starting server on {host}:{port}")
    print(f"Reload mode: {reload}")
    print(f"App module: app.main:app")
    
    try:
        uvicorn.run(
            "app.main:app",
            host=host,
            port=port,
            reload=reload,
            log_level="info"
        )
    except Exception as e:
        print(f"Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Start the AI-Assisted News Scraper API")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=6777, help="Port to bind to")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload")
    
    args = parser.parse_args()
    
    start_server(args.host, args.port, args.reload)