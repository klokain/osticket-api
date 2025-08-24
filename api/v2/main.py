"""
OSTicket API v2 - Main Application

FastAPI application that provides a modern REST API layer for OSTicket,
integrating with the existing PHP codebase and database.
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import structlog
import os
import sys

# Add osTicket include path for potential PHP integration
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../osTicket/include'))

from .core.config import settings
from .core.database import engine, SessionLocal
from .middleware.auth import AuthMiddleware
from .middleware.logging import LoggingMiddleware
from .routes import health, auth, auth_extended
from .core.exceptions import setup_exception_handlers

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.JSONRenderer()
    ],
    wrapper_class=structlog.stdlib.BoundLogger,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

def create_app() -> FastAPI:
    """Create and configure FastAPI application"""
    
    app = FastAPI(
        title="OSTicket API v2",
        description="Modern REST API for OSTicket with comprehensive endpoint coverage",
        version="2.0.0",
        openapi_url="/api/v2/openapi.json",
        docs_url="/api/v2/docs",
        redoc_url="/api/v2/redoc"
    )
    
    # CORS configuration
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_HOSTS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Custom middleware
    app.add_middleware(LoggingMiddleware)
    app.add_middleware(AuthMiddleware)
    
    # Exception handlers
    setup_exception_handlers(app)
    
    # Include routers
    app.include_router(health.router, prefix="/api/v2", tags=["health"])
    app.include_router(auth.router, prefix="/api/v2/auth", tags=["authentication"])
    app.include_router(auth_extended.router, prefix="/api/v2", tags=["extended-authentication"])
    
    @app.on_event("startup")
    async def startup_event():
        """Initialize application on startup"""
        logger.info("Starting OSTicket API v2", version="2.0.0")
        
        # Test database connection
        try:
            from .core.database import test_connection
            await test_connection()
            logger.info("Database connection established successfully")
        except Exception as e:
            logger.error("Database connection failed", error=str(e))
            raise
    
    @app.on_event("shutdown")
    async def shutdown_event():
        """Cleanup on application shutdown"""
        logger.info("Shutting down OSTicket API v2")
    
    return app

app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "api.v2.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_config=None,  # Use our structlog configuration
    )