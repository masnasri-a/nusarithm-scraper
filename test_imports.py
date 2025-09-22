#!/usr/bin/env python3
"""
Test script to check if all imports work correctly
"""

import os
import sys
from pathlib import Path

# Setup Python path
script_dir = Path(__file__).parent.absolute()
sys.path.insert(0, str(script_dir))

print(f"Testing imports from: {script_dir}")
print(f"Python path: {sys.path[:3]}...")

try:
    print("Testing app package import...")
    import app
    print("✓ app package imported successfully")
    
    print("Testing app.models import...")
    from app.models import schema, auth
    print("✓ app.models imported successfully")
    
    print("Testing app.routers import...")
    from app.routers import training, scraping, auth as auth_router, users
    print("✓ app.routers imported successfully")
    
    print("Testing app.services import...")
    from app.services import template, scraper, llm_agent
    print("✓ app.services imported successfully")
    
    print("Testing app.main import...")
    from app.main import app as fastapi_app
    print("✓ app.main imported successfully")
    
    print("\n🎉 All imports successful!")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
except Exception as e:
    print(f"❌ Unexpected error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)