# FastAPI Implementation Plan for OSTicket API

## Project Structure

```
/usr/home/filip/ost-api/
├── osTicket/                    # Existing OSTicket installation (unchanged)
├── api-server/                  # New FastAPI server
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py             # FastAPI application entry point
│   │   ├── config.py           # Configuration management
│   │   ├── database.py         # Database connection setup
│   │   │
│   │   ├── models/             # SQLAlchemy models mapping OSTicket tables
│   │   │   ├── __init__.py
│   │   │   ├── ticket.py       # ost_ticket table mapping
│   │   │   ├── user.py         # ost_user table mapping
│   │   │   ├── staff.py        # ost_staff table mapping
│   │   │   ├── thread.py       # ost_thread, ost_thread_entry
│   │   │   ├── organization.py # ost_organization
│   │   │   ├── department.py   # ost_department
│   │   │   └── base.py         # Base model configuration
│   │   │
│   │   ├── schemas/            # Pydantic models for validation
│   │   │   ├── __init__.py
│   │   │   ├── ticket.py       # Request/response schemas
│   │   │   ├── user.py
│   │   │   ├── auth.py
│   │   │   └── common.py       # Shared schemas
│   │   │
│   │   ├── api/                # API endpoints
│   │   │   ├── __init__.py
│   │   │   ├── v1/             # Legacy compatibility
│   │   │   │   └── tickets.py  # /api/tickets.json compatibility
│   │   │   └── v2/             # New RESTful API
│   │   │       ├── auth.py     # Authentication endpoints
│   │   │       ├── tickets.py   # Ticket CRUD operations
│   │   │       ├── users.py     # User management
│   │   │       ├── organizations.py
│   │   │       ├── departments.py
│   │   │       ├── staff.py
│   │   │       └── search.py   # Advanced search
│   │   │
│   │   ├── core/               # Core functionality
│   │   │   ├── __init__.py
│   │   │   ├── security.py     # JWT, authentication
│   │   │   ├── dependencies.py # FastAPI dependencies
│   │   │   ├── middleware.py   # Custom middleware
│   │   │   └── exceptions.py   # Exception handlers
│   │   │
│   │   ├── services/           # Business logic
│   │   │   ├── __init__.py
│   │   │   ├── ticket_service.py
│   │   │   ├── user_service.py
│   │   │   ├── email_service.py
│   │   │   └── notification_service.py
│   │   │
│   │   └── utils/              # Utility functions
│   │       ├── __init__.py
│   │       ├── osticket_compat.py  # OSTicket compatibility helpers
│   │       ├── pagination.py
│   │       └── validators.py
│   │
│   ├── migrations/             # Alembic migrations (if needed)
│   ├── tests/
│   │   ├── conftest.py
│   │   ├── test_tickets.py
│   │   ├── test_users.py
│   │   └── test_auth.py
│   │
│   ├── requirements.txt        # Python dependencies
│   ├── .env.example           # Environment variables template
│   ├── Dockerfile             # Container definition
│   ├── docker-compose.yml     # Development environment
│   └── pytest.ini             # Test configuration
```

## Phase 1: Database Connection & Models

### 1.1 Database Configuration (`app/database.py`)
```python
from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import settings

# Connect to existing OSTicket database
SQLALCHEMY_DATABASE_URL = (
    f"mysql+pymysql://{settings.DB_USER}:{settings.DB_PASSWORD}@"
    f"{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
)

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Use OSTicket's existing schema
metadata = MetaData(bind=engine)
Base = declarative_base(metadata=metadata)

# Dependency for FastAPI
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

### 1.2 Ticket Model (`app/models/ticket.py`)
```python
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import Base

class Ticket(Base):
    __tablename__ = 'ost_ticket'
    __table_args__ = {'extend_existing': True}
    
    ticket_id = Column(Integer, primary_key=True)
    ticket_pid = Column(Integer)  # Parent ticket
    number = Column(String(20), unique=True, nullable=False)
    user_id = Column(Integer, ForeignKey('ost_user.id'))
    user_email_id = Column(Integer)
    status_id = Column(Integer, ForeignKey('ost_ticket_status.id'))
    dept_id = Column(Integer, ForeignKey('ost_department.id'))
    sla_id = Column(Integer, ForeignKey('ost_sla.id'))
    topic_id = Column(Integer, ForeignKey('ost_help_topic.topic_id'))
    staff_id = Column(Integer, ForeignKey('ost_staff.staff_id'))
    team_id = Column(Integer, ForeignKey('ost_team.team_id'))
    email_id = Column(Integer)
    lock_id = Column(Integer)
    flags = Column(Integer, default=0)
    sort = Column(Integer, default=0)
    ip_address = Column(String(64))
    source = Column(String(16))
    source_extra = Column(String(255))
    isoverdue = Column(Integer, default=0)
    isanswered = Column(Integer, default=0)
    duedate = Column(DateTime)
    est_duedate = Column(DateTime)
    reopened = Column(DateTime)
    closed = Column(DateTime)
    lastupdate = Column(DateTime)
    created = Column(DateTime)
    updated = Column(DateTime)
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id])
    status = relationship("TicketStatus", foreign_keys=[status_id])
    department = relationship("Department", foreign_keys=[dept_id])
    staff = relationship("Staff", foreign_keys=[staff_id])
    team = relationship("Team", foreign_keys=[team_id])
    thread = relationship("Thread", back_populates="ticket", uselist=False)
    cdata = relationship("TicketCData", back_populates="ticket", uselist=False)

class TicketCData(Base):
    """Custom data fields for tickets"""
    __tablename__ = 'ost_ticket__cdata'
    __table_args__ = {'extend_existing': True}
    
    ticket_id = Column(Integer, ForeignKey('ost_ticket.ticket_id'), primary_key=True)
    subject = Column(String(255))
    priority = Column(String(10))
    priority_id = Column(Integer, ForeignKey('ost_ticket_priority.priority_id'))
    
    ticket = relationship("Ticket", back_populates="cdata")

class TicketStatus(Base):
    __tablename__ = 'ost_ticket_status'
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True)
    name = Column(String(60), unique=True)
    state = Column(String(16))
    mode = Column(Integer)
    flags = Column(Integer)
    sort = Column(Integer)
    properties = Column(Text)
    created = Column(DateTime)
    updated = Column(DateTime)
```

### 1.3 User Model (`app/models/user.py`)
```python
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from app.models.base import Base

class User(Base):
    __tablename__ = 'ost_user'
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True)
    org_id = Column(Integer, ForeignKey('ost_organization.id'))
    default_email_id = Column(Integer)
    status = Column(Integer, default=0)
    name = Column(String(128))
    created = Column(DateTime)
    updated = Column(DateTime)
    
    # Relationships
    organization = relationship("Organization", back_populates="users")
    emails = relationship("UserEmail", back_populates="user")
    tickets = relationship("Ticket", back_populates="user")
    cdata = relationship("UserCData", back_populates="user", uselist=False)

class UserEmail(Base):
    __tablename__ = 'ost_user_email'
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('ost_user.id'))
    flags = Column(Integer)
    address = Column(String(255), unique=True)
    
    user = relationship("User", back_populates="emails")

class UserCData(Base):
    """Custom fields for users"""
    __tablename__ = 'ost_user__cdata'
    __table_args__ = {'extend_existing': True}
    
    user_id = Column(Integer, ForeignKey('ost_user.id'), primary_key=True)
    email = Column(String(255))
    name = Column(String(255))
    phone = Column(String(64))
    notes = Column(Text)
    
    user = relationship("User", back_populates="cdata")
```

## Phase 2: Core API Implementation

### 2.1 Main Application (`app/main.py`)
```python
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.api.v2 import auth, tickets, users, organizations, departments, staff
from app.api.v1 import legacy
from app.core.config import settings
from app.core.exceptions import setup_exception_handlers

# Create FastAPI instance
app = FastAPI(
    title="OSTicket API",
    description="Modern REST API for OSTicket",
    version="2.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup exception handlers
setup_exception_handlers(app)

# Health check
@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "2.0.0"}

# Include routers
app.include_router(auth.router, prefix="/api/v2/auth", tags=["Authentication"])
app.include_router(tickets.router, prefix="/api/v2/tickets", tags=["Tickets"])
app.include_router(users.router, prefix="/api/v2/users", tags=["Users"])
app.include_router(organizations.router, prefix="/api/v2/organizations", tags=["Organizations"])
app.include_router(departments.router, prefix="/api/v2/departments", tags=["Departments"])
app.include_router(staff.router, prefix="/api/v2/staff", tags=["Staff"])

# Legacy compatibility
app.include_router(legacy.router, prefix="/api", tags=["Legacy"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=settings.DEBUG)
```

### 2.2 Ticket Endpoints (`app/api/v2/tickets.py`)
```python
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models import ticket as ticket_models
from app.schemas import ticket as ticket_schemas
from app.services import ticket_service
from app.core.security import get_current_user
from app.utils.pagination import paginate

router = APIRouter()

@router.get("/", response_model=ticket_schemas.TicketList)
async def list_tickets(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[str] = None,
    department_id: Optional[int] = None,
    user_id: Optional[int] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    List tickets with filtering and pagination.
    
    - **skip**: Number of tickets to skip
    - **limit**: Maximum number of tickets to return
    - **status**: Filter by status (open, closed, etc.)
    - **department_id**: Filter by department
    - **user_id**: Filter by user
    - **search**: Search in ticket subject and content
    """
    query = ticket_service.build_ticket_query(
        db, status=status, department_id=department_id, 
        user_id=user_id, search=search
    )
    
    return paginate(query, skip=skip, limit=limit, schema=ticket_schemas.Ticket)

@router.get("/{ticket_id}", response_model=ticket_schemas.TicketDetail)
async def get_ticket(
    ticket_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get detailed information about a specific ticket."""
    ticket = ticket_service.get_ticket_by_id(db, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    # Check permissions
    if not ticket_service.can_view_ticket(current_user, ticket):
        raise HTTPException(status_code=403, detail="Access denied")
    
    return ticket_schemas.TicketDetail.from_orm(ticket)

@router.post("/", response_model=ticket_schemas.Ticket, status_code=201)
async def create_ticket(
    ticket: ticket_schemas.TicketCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create a new support ticket."""
    return ticket_service.create_ticket(db, ticket, current_user)

@router.put("/{ticket_id}", response_model=ticket_schemas.Ticket)
async def update_ticket(
    ticket_id: int,
    ticket_update: ticket_schemas.TicketUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Update ticket information."""
    ticket = ticket_service.get_ticket_by_id(db, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    if not ticket_service.can_edit_ticket(current_user, ticket):
        raise HTTPException(status_code=403, detail="Access denied")
    
    return ticket_service.update_ticket(db, ticket, ticket_update)

@router.post("/{ticket_id}/reply", response_model=ticket_schemas.ThreadEntry)
async def add_reply(
    ticket_id: int,
    reply: ticket_schemas.ThreadEntryCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Add a reply to the ticket thread."""
    ticket = ticket_service.get_ticket_by_id(db, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    return ticket_service.add_reply(db, ticket, reply, current_user)

@router.post("/{ticket_id}/assign", response_model=ticket_schemas.Ticket)
async def assign_ticket(
    ticket_id: int,
    assignment: ticket_schemas.TicketAssignment,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Assign ticket to staff or team."""
    ticket = ticket_service.get_ticket_by_id(db, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    if not ticket_service.can_assign_ticket(current_user):
        raise HTTPException(status_code=403, detail="Access denied")
    
    return ticket_service.assign_ticket(db, ticket, assignment)

@router.get("/{ticket_id}/thread", response_model=List[ticket_schemas.ThreadEntry])
async def get_ticket_thread(
    ticket_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get the complete conversation thread for a ticket."""
    ticket = ticket_service.get_ticket_by_id(db, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    if not ticket_service.can_view_ticket(current_user, ticket):
        raise HTTPException(status_code=403, detail="Access denied")
    
    return ticket_service.get_thread_entries(db, ticket_id)
```

### 2.3 Authentication (`app/core/security.py`)
```python
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.database import get_db
from app.config import settings
from app.models.user import User
from app.models.staff import Staff

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

async def get_current_user(
    token_data: dict = Depends(verify_token),
    db: Session = Depends(get_db)
):
    user_id = token_data.get("sub")
    user_type = token_data.get("type")
    
    if user_type == "staff":
        user = db.query(Staff).filter(Staff.staff_id == user_id).first()
    else:
        user = db.query(User).filter(User.id == user_id).first()
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    return user

# API Key compatibility for legacy support
async def get_api_key(api_key: str = Depends(security)):
    # Validate against OSTicket API keys table
    pass
```

## Phase 3: Services & Business Logic

### 3.1 Ticket Service (`app/services/ticket_service.py`)
```python
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from datetime import datetime
from typing import Optional, List
from app.models.ticket import Ticket, TicketCData, TicketStatus
from app.models.thread import Thread, ThreadEntry
from app.schemas.ticket import TicketCreate, TicketUpdate
from app.utils.osticket_compat import generate_ticket_number, get_default_sla

def build_ticket_query(
    db: Session,
    status: Optional[str] = None,
    department_id: Optional[int] = None,
    user_id: Optional[int] = None,
    search: Optional[str] = None
):
    query = db.query(Ticket).join(TicketCData)
    
    if status:
        query = query.join(TicketStatus).filter(TicketStatus.name == status)
    
    if department_id:
        query = query.filter(Ticket.dept_id == department_id)
    
    if user_id:
        query = query.filter(Ticket.user_id == user_id)
    
    if search:
        query = query.filter(
            or_(
                TicketCData.subject.contains(search),
                Ticket.number.contains(search)
            )
        )
    
    return query.order_by(Ticket.created.desc())

def create_ticket(db: Session, ticket_data: TicketCreate, current_user):
    # Generate ticket number in OSTicket format
    ticket_number = generate_ticket_number(db)
    
    # Create main ticket record
    db_ticket = Ticket(
        number=ticket_number,
        user_id=current_user.id if hasattr(current_user, 'id') else None,
        status_id=1,  # Default to open status
        dept_id=ticket_data.department_id or get_default_department(db),
        topic_id=ticket_data.topic_id,
        source=ticket_data.source or 'API',
        ip_address=ticket_data.ip_address,
        created=datetime.utcnow(),
        updated=datetime.utcnow(),
        lastupdate=datetime.utcnow()
    )
    db.add(db_ticket)
    db.flush()  # Get ticket_id
    
    # Create custom data record
    db_cdata = TicketCData(
        ticket_id=db_ticket.ticket_id,
        subject=ticket_data.subject,
        priority_id=ticket_data.priority_id or get_default_priority(db)
    )
    db.add(db_cdata)
    
    # Create thread
    db_thread = Thread(
        object_id=db_ticket.ticket_id,
        object_type='T',  # T for Ticket
        extra=None,
        lastresponse=None,
        created=datetime.utcnow()
    )
    db.add(db_thread)
    db.flush()
    
    # Create initial message
    db_entry = ThreadEntry(
        thread_id=db_thread.id,
        staff_id=None,
        user_id=current_user.id if hasattr(current_user, 'id') else None,
        type='M',  # M for Message
        flags=0,
        poster='API User',
        editor=None,
        source='API',
        title=ticket_data.subject,
        body=ticket_data.message,
        format='html' if ticket_data.html else 'text',
        ip_address=ticket_data.ip_address,
        created=datetime.utcnow(),
        updated=datetime.utcnow()
    )
    db.add(db_entry)
    
    db.commit()
    db.refresh(db_ticket)
    
    return db_ticket

def can_view_ticket(user, ticket: Ticket) -> bool:
    """Check if user can view the ticket"""
    # Staff can view all tickets in their department
    if hasattr(user, 'dept_id'):  # Is staff
        return True  # Simplified - add proper permission checks
    
    # Users can view their own tickets
    if hasattr(user, 'id') and ticket.user_id == user.id:
        return True
    
    # Check organization access
    # Add more permission logic as needed
    
    return False

def can_edit_ticket(user, ticket: Ticket) -> bool:
    """Check if user can edit the ticket"""
    # Only staff can edit tickets
    if not hasattr(user, 'dept_id'):
        return False
    
    # Check department access
    # Check role permissions
    # Add proper permission logic
    
    return True

def can_assign_ticket(user) -> bool:
    """Check if user can assign tickets"""
    # Only staff with proper permissions
    return hasattr(user, 'dept_id')  # Simplified
```

## Phase 4: Docker Setup

### 4.1 Dockerfile
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY ./app /app/app

# Create non-root user
RUN useradd -m -u 1000 apiuser && chown -R apiuser:apiuser /app
USER apiuser

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 4.2 docker-compose.yml
```yaml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DB_HOST=host.docker.internal  # Connect to host MySQL
      - DB_PORT=3306
      - DB_NAME=osticket
      - DB_USER=osticket
      - DB_PASSWORD=${DB_PASSWORD}
      - SECRET_KEY=${SECRET_KEY}
      - DEBUG=true
    volumes:
      - ./app:/app/app
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
    depends_on:
      - redis

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

volumes:
  redis_data:
```

### 4.3 Requirements.txt
```txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlalchemy==2.0.23
pymysql==1.1.0
cryptography==41.0.7
pydantic==2.5.0
pydantic[email]==2.5.0
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6
redis==5.0.1
celery==5.3.4
httpx==0.25.2
pytest==7.4.3
pytest-asyncio==0.21.1
alembic==1.12.1
python-dotenv==1.0.0
```

## Phase 5: Testing

### 5.1 Test Configuration (`tests/conftest.py`)
```python
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import Base, get_db
from app.core.security import create_access_token

# Test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture
def client():
    Base.metadata.create_all(bind=engine)
    
    def override_get_db():
        try:
            db = TestingSessionLocal()
            yield db
        finally:
            db.close()
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def auth_headers():
    token = create_access_token(data={"sub": "1", "type": "staff"})
    return {"Authorization": f"Bearer {token}"}
```

### 5.2 Ticket Tests (`tests/test_tickets.py`)
```python
import pytest
from fastapi.testclient import TestClient

def test_create_ticket(client: TestClient, auth_headers):
    response = client.post(
        "/api/v2/tickets",
        json={
            "subject": "Test Ticket",
            "message": "This is a test ticket",
            "department_id": 1,
            "priority_id": 2
        },
        headers=auth_headers
    )
    assert response.status_code == 201
    data = response.json()
    assert data["subject"] == "Test Ticket"
    assert "number" in data

def test_list_tickets(client: TestClient, auth_headers):
    response = client.get("/api/v2/tickets", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data

def test_get_ticket(client: TestClient, auth_headers):
    # Create a ticket first
    create_response = client.post(
        "/api/v2/tickets",
        json={
            "subject": "Test Ticket",
            "message": "Test message"
        },
        headers=auth_headers
    )
    ticket_id = create_response.json()["ticket_id"]
    
    # Get the ticket
    response = client.get(f"/api/v2/tickets/{ticket_id}", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["ticket_id"] == ticket_id
```

## Environment Configuration

### .env.example
```env
# Database
DB_HOST=localhost
DB_PORT=3306
DB_NAME=osticket
DB_USER=osticket
DB_PASSWORD=your_password_here

# Security
SECRET_KEY=your-secret-key-here-change-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# API Configuration
API_V2_PREFIX=/api/v2
ALLOWED_ORIGINS=["http://localhost:3000", "http://localhost:8080"]
DEBUG=false

# Redis (for caching)
REDIS_URL=redis://localhost:6379/0

# OSTicket Compatibility
OSTICKET_TABLE_PREFIX=ost_
OSTICKET_TIMEZONE=America/New_York

# Rate Limiting
RATE_LIMIT_ENABLED=true
RATE_LIMIT_PER_MINUTE=60
```

## Deployment Instructions

### Development Setup
```bash
# Clone repository
cd /usr/home/filip/ost-api

# Create API server directory
mkdir api-server
cd api-server

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy .env.example to .env and configure
cp .env.example .env
# Edit .env with your database credentials

# Run development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Docker Deployment
```bash
# Build and run with Docker Compose
docker-compose up --build

# Or build manually
docker build -t osticket-api .
docker run -p 8000:8000 --env-file .env osticket-api
```

### Production Deployment
```bash
# Use Gunicorn with Uvicorn workers
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000

# Or use systemd service
sudo cp osticket-api.service /etc/systemd/system/
sudo systemctl enable osticket-api
sudo systemctl start osticket-api
```

## API Documentation

Once running, the API documentation will be available at:
- Swagger UI: http://localhost:8000/api/docs
- ReDoc: http://localhost:8000/api/redoc
- OpenAPI JSON: http://localhost:8000/api/openapi.json

## Next Steps

1. **Week 1**: Set up project structure and database models
2. **Week 2**: Implement authentication and core ticket endpoints
3. **Week 3**: Add user, organization, and department endpoints
4. **Week 4**: Implement search, filtering, and pagination
5. **Week 5**: Add file attachments and email integration
6. **Week 6**: Testing and optimization
7. **Week 7**: Documentation and deployment preparation
8. **Week 8**: Production deployment and monitoring setup

This implementation provides:
- Direct database access to OSTicket tables
- Full REST API with automatic documentation
- JWT authentication with legacy API key support
- Comprehensive testing framework
- Docker deployment ready
- Production-ready configuration