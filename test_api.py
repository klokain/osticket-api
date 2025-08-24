#!/usr/bin/env python3
"""
Test script for OSTicket API v2

This script tests if the FastAPI application can start and basic functionality works.
"""

import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test if all modules can be imported"""
    print("Testing imports...")
    
    try:
        from api.v2.main import app
        print("✓ Main application imported successfully")
    except Exception as e:
        print(f"✗ Failed to import main application: {e}")
        return False
    
    try:
        from api.v2.core.config import settings
        print(f"✓ Configuration loaded (DEBUG={settings.DEBUG})")
    except Exception as e:
        print(f"✗ Failed to load configuration: {e}")
        return False
    
    try:
        from api.v2.core.database import engine
        print("✓ Database engine created")
    except Exception as e:
        print(f"✗ Failed to create database engine: {e}")
        return False
    
    return True

def test_app_creation():
    """Test if the FastAPI app can be created"""
    print("\nTesting app creation...")
    
    try:
        from api.v2.main import create_app
        app = create_app()
        print("✓ FastAPI app created successfully")
        print(f"✓ App title: {app.title}")
        print(f"✓ App version: {app.version}")
        return True
    except Exception as e:
        print(f"✗ Failed to create app: {e}")
        return False

def test_database_connection():
    """Test database connection (if available)"""
    print("\nTesting database connection...")
    
    try:
        from api.v2.core.database import engine
        with engine.connect() as conn:
            result = conn.execute("SELECT 1 as test")
            row = result.fetchone()
            if row and row[0] == 1:
                print("✓ Database connection successful")
                return True
            else:
                print("✗ Database connection failed: unexpected result")
                return False
    except Exception as e:
        print(f"⚠ Database connection not available: {e}")
        print("  This is normal if OSTicket database is not set up")
        return None  # Not a failure, just not available

def main():
    """Run all tests"""
    print("OSTicket API v2 - Test Suite")
    print("=" * 40)
    
    results = []
    
    # Test imports
    results.append(test_imports())
    
    # Test app creation
    results.append(test_app_creation())
    
    # Test database (optional)
    db_result = test_database_connection()
    if db_result is not None:
        results.append(db_result)
    
    print("\n" + "=" * 40)
    
    # Summary
    passed = sum(1 for r in results if r is True)
    failed = sum(1 for r in results if r is False)
    
    print(f"Tests passed: {passed}")
    print(f"Tests failed: {failed}")
    
    if failed == 0:
        print("✓ All tests passed! The API is ready to run.")
        print("\nTo start the development server, run:")
        print("  python run_api.py")
        print("\nThen visit: http://localhost:8000/api/v2/docs")
        return 0
    else:
        print("✗ Some tests failed. Please fix the issues before running the API.")
        return 1

if __name__ == "__main__":
    sys.exit(main())