"""
Database connection and session management for OSTicket API v2

Integrates with OSTicket's existing database using SQLAlchemy ORM.
"""

from sqlalchemy import create_engine, MetaData, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
import structlog
from typing import AsyncGenerator
from .config import settings

logger = structlog.get_logger()

# Create database engine
engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    pool_pre_ping=True,
    pool_recycle=300,  # Recycle connections after 5 minutes
    connect_args={
        "charset": "utf8mb4",
        "connect_timeout": 10,
        "read_timeout": 30,
        "write_timeout": 30,
    }
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for ORM models
Base = declarative_base()

# Metadata with OSTicket table prefix
metadata = MetaData(naming_convention={
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
})

def get_table_name(name: str) -> str:
    """Add OSTicket table prefix to table name"""
    return f"{settings.TABLE_PREFIX}{name}"

async def test_connection() -> bool:
    """Test database connection"""
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1 as test"))
            row = result.fetchone()
            if row and row[0] == 1:
                logger.info("Database connection test successful")
                return True
            else:
                logger.error("Database connection test failed: unexpected result")
                return False
    except Exception as e:
        logger.error("Database connection test failed", error=str(e))
        raise

def get_db() -> Session:
    """Get database session - for FastAPI dependency injection"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def get_db_async() -> AsyncGenerator[Session, None]:
    """Get database session asynchronously"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def check_osticket_tables() -> dict:
    """Check if OSTicket tables exist in the database"""
    required_tables = [
        'ticket', 'thread', 'user', 'staff', 'organization', 
        'department', 'team', 'role', 'api_key', 'config'
    ]
    
    results = {}
    
    try:
        with engine.connect() as conn:
            for table in required_tables:
                table_name = get_table_name(table)
                query = text("""
                    SELECT COUNT(*) as count 
                    FROM information_schema.tables 
                    WHERE table_schema = :database_name 
                    AND table_name = :table_name
                """)
                
                result = conn.execute(
                    query, 
                    {"database_name": settings.DATABASE_NAME, "table_name": table_name}
                )
                row = result.fetchone()
                results[table] = row[0] > 0 if row else False
                
        logger.info("OSTicket table check completed", results=results)
        
    except Exception as e:
        logger.error("Failed to check OSTicket tables", error=str(e))
        
    return results

# Database health check
def get_db_health() -> dict:
    """Get database health information"""
    try:
        with engine.connect() as conn:
            # Test basic connectivity
            conn.execute(text("SELECT 1"))
            
            # Get database version
            version_result = conn.execute(text("SELECT VERSION()"))
            version = version_result.fetchone()[0]
            
            # Get connection info
            status_result = conn.execute(text("SHOW STATUS LIKE 'Threads_connected'"))
            connections = status_result.fetchone()[1]
            
            # Check OSTicket tables
            table_status = check_osticket_tables()
            
            return {
                "status": "healthy",
                "database_version": version,
                "active_connections": int(connections),
                "osticket_tables": table_status,
                "table_prefix": settings.TABLE_PREFIX
            }
            
    except Exception as e:
        logger.error("Database health check failed", error=str(e))
        return {
            "status": "unhealthy",
            "error": str(e),
            "table_prefix": settings.TABLE_PREFIX
        }

# Initialize database connection on module import
try:
    # Test initial connection
    import asyncio
    if hasattr(asyncio, '_get_running_loop') and asyncio._get_running_loop():
        # We're in an async context, schedule the test
        asyncio.create_task(test_connection())
    else:
        # We're not in an async context, create one
        asyncio.run(test_connection())
except Exception as e:
    logger.warning("Initial database connection test failed", error=str(e))