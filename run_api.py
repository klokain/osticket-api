#!/usr/bin/env python3
"""
OSTicket API v2 Development Server

Run this script to start the development server.
"""

import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    import uvicorn
    
    # Run the FastAPI application
    uvicorn.run(
        "api.v2.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )