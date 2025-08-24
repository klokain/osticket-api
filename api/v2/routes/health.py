"""
Health check endpoints for OSTicket API v2
"""

from fastapi import APIRouter, Depends
from datetime import datetime
from sqlalchemy.orm import Session
from ..core.database import get_db, get_db_health
from ..schemas.base import HealthResponse

router = APIRouter()

@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health Check",
    description="Check the health status of the API and its dependencies"
)
async def health_check(db: Session = Depends(get_db)):
    """Health check endpoint"""
    
    # Get database health information
    db_health = get_db_health()
    
    return HealthResponse(
        status="healthy" if db_health["status"] == "healthy" else "unhealthy",
        timestamp=datetime.utcnow(),
        version="2.0.0",
        database=db_health
    )

@router.get(
    "/health/database",
    summary="Database Health Check",
    description="Detailed database health information"
)
async def database_health_check():
    """Database-specific health check"""
    
    return get_db_health()