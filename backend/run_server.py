#!/usr/bin/env python
"""
Startup script for the Recipe Management API server.

This script ensures proper module import paths and environment configuration
when running the FastAPI application from different contexts (terminal, PyCharm, etc.).
"""

import sys
import os
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

# Set environment variables if not already set
os.environ.setdefault("PYTHONPATH", str(project_root))

# Now import and run the application
if __name__ == "__main__":
    import uvicorn
    from app.config.settings import get_settings

    # Load settings to validate environment configuration
    settings = get_settings()

    # Run the application
    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug,
        log_level=settings.log_level.lower(),
    )