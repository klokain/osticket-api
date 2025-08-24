# System Architecture

Understanding the design and structure of the OSTicket API v2 system.

## Overview

The OSTicket API v2 is designed as a modern REST API layer that sits alongside the existing OSTicket PHP application, providing comprehensive API access while maintaining full compatibility with the existing system.

## Architecture Principles

### 1. Coexistence Strategy
The API is designed to coexist with the existing OSTicket installation without requiring any changes to the PHP codebase or database schema.

- **Zero database changes** - Uses existing OSTicket tables
- **Read/write compatibility** - Both systems can operate simultaneously
- **Shared authentication** - Supports OSTicket sessions and native auth
- **Gradual migration** - Allows incremental adoption

### 2. API-First Design
Built with modern API standards and practices:

- **RESTful design** - Standard HTTP methods and status codes
- **JSON-first** - All requests/responses use JSON
- **OpenAPI specification** - Auto-generated documentation
- **Versioned endpoints** - Future-proof versioning strategy

### 3. Security by Design
Multiple layers of security and authentication:

- **Multi-auth support** - JWT, OAuth2, API keys, sessions
- **Role-based access** - Respect OSTicket permissions
- **Input validation** - Comprehensive request validation
- **Structured errors** - Secure error messages

## System Components

```
┌─────────────────────────────────────────────────────────────────┐
│                        Client Applications                        │
├─────────────────────────────────────────────────────────────────┤
│  Web App  │  Mobile App  │  Integrations  │  Admin Dashboard    │
└─────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────┐
│                       Load Balancer / Proxy                      │
│                        (nginx, Apache)                          │
└─────────────────────────────────────────────────────────────────┘
                                    │
                    ┌───────────────┼───────────────┐
                    ▼               │               ▼
┌─────────────────────────┐         │    ┌─────────────────────────┐
│     FastAPI Server      │         │    │    OSTicket PHP App     │
│      (API v2)           │         │    │     (Existing)          │
│                         │         │    │                         │
│ ┌─────────────────────┐ │         │    │ ┌─────────────────────┐ │
│ │     Routes          │ │         │    │ │   Web Interface     │ │
│ │  /api/v2/tickets    │ │         │    │ │   Staff Panel       │ │
│ │  /api/v2/users      │ │         │    │ │   Client Portal     │ │
│ │  /api/v2/auth       │ │         │    │ │   Admin Panel       │ │
│ └─────────────────────┘ │         │    │ └─────────────────────┘ │
│                         │         │    │                         │
│ ┌─────────────────────┐ │         │    │ ┌─────────────────────┐ │
│ │    Middleware       │ │         │    │ │   PHP Classes       │ │
│ │  Authentication     │ │         │    │ │   Business Logic    │ │
│ │  Authorization      │ │         │    │ │   Session Mgmt      │ │
│ │  Logging            │ │         │    │ │   Email Processing  │ │
│ └─────────────────────┘ │         │    │ └─────────────────────┘ │
│                         │         │    │                         │
│ ┌─────────────────────┐ │         │    │                         │
│ │  SQLAlchemy ORM     │ │         │    │                         │
│ │   72 Models         │ │         │    │                         │
│ │   Relationships     │ │         │    │                         │
│ └─────────────────────┘ │         │    │                         │
└─────────────────────────┘         │    └─────────────────────────┘
                    │               │               │
                    └───────────────┼───────────────┘
                                    ▼
┌─────────────────────────────────────────────────────────────────┐
│                    MySQL/MariaDB Database                       │
│                                                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────┐ │
│  │   Tickets   │  │    Users    │  │    Staff    │  │  Config │ │
│  │ ost_ticket  │  │  ost_user   │  │ ost_staff   │  │ ost_*   │ │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────┘ │
│                                                                 │
│              72 Tables (ost_ prefix)                            │
└─────────────────────────────────────────────────────────────────┘
                                    │
                    ┌───────────────┼───────────────┐
                    ▼               │               ▼
┌─────────────────────────┐         │    ┌─────────────────────────┐
│   Identity Providers    │         │    │   External Services     │
│                         │         │    │                         │
│ ┌─────────────────────┐ │         │    │ ┌─────────────────────┐ │
│ │     Keycloak        │ │         │    │ │   Email Servers     │ │
│ │  Microsoft Entra    │ │         │    │ │   SMTP/IMAP         │ │
│ │   Generic OAuth2    │ │         │    │ │   File Storage      │ │
│ └─────────────────────┘ │         │    │ │   Search Engine     │ │
└─────────────────────────┘         │    │ └─────────────────────┘ │
                                    │    └─────────────────────────┘
                                    ▼
┌─────────────────────────────────────────────────────────────────┐
│                         Monitoring                              │
│                                                                 │
│    Logs    │   Metrics   │  Health Checks  │   Performance     │
└─────────────────────────────────────────────────────────────────┘
```

## Core Architecture Layers

### 1. API Layer (FastAPI)

**Purpose**: Handle HTTP requests and responses  
**Technology**: FastAPI with Pydantic  
**Responsibilities**:
- HTTP request/response handling
- Route definition and URL mapping
- Request validation and serialization
- OpenAPI documentation generation
- CORS handling

**Key Components**:
```python
# Route definition
@router.post("/tickets", response_model=TicketResponse)
async def create_ticket(ticket: TicketCreate, auth: AuthContext = Depends(require_auth)):
    # Handler logic
```

### 2. Middleware Layer

**Purpose**: Cross-cutting concerns applied to all requests  
**Technology**: FastAPI middleware, Starlette  
**Responsibilities**:
- Authentication and authorization
- Request/response logging
- Error handling and formatting
- Request ID generation
- Performance monitoring

**Middleware Stack** (applied in order):
1. **Logging Middleware** - Request/response logging
2. **Authentication Middleware** - Multi-provider auth
3. **Exception Middleware** - Error handling (built-in)

### 3. Service Layer

**Purpose**: Business logic and orchestration  
**Technology**: Python classes and functions  
**Responsibilities**:
- Business rule enforcement
- Cross-model operations
- External service integration
- Complex query logic
- Transaction management

**Example**:
```python
class TicketService:
    def __init__(self, db: Session):
        self.db = db
    
    def create_ticket(self, ticket_data: TicketCreate, user: AuthContext) -> Ticket:
        # Business logic
        # Validation
        # Database operations
        # Return result
```

### 4. Model Layer (SQLAlchemy ORM)

**Purpose**: Database abstraction and data modeling  
**Technology**: SQLAlchemy with declarative mapping  
**Responsibilities**:
- Database schema definition
- Relationship mapping
- Query generation
- Transaction support
- Connection pooling

**Model Structure**:
```python
class Ticket(OSTicketBase):
    __tablename__ = "ost_ticket"
    
    ticket_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("ost_user.id"))
    
    # Relationships
    user = relationship("User", back_populates="tickets")
    threads = relationship("Thread", back_populates="ticket")
```

### 5. Database Layer

**Purpose**: Data persistence and storage  
**Technology**: MySQL/MariaDB with InnoDB  
**Responsibilities**:
- Data storage and retrieval
- Transaction support
- Constraint enforcement
- Performance optimization
- Backup and recovery

## Authentication Architecture

The system supports multiple authentication methods through a unified authentication middleware:

### Authentication Flow
```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Client App    │    │   API Gateway    │    │  Auth Service   │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                        │                        │
         │ 1. Login Request       │                        │
         ├──────────────────────► │                        │
         │                        │ 2. Validate Creds     │
         │                        ├──────────────────────► │
         │                        │                        │
         │                        │ 3. Return JWT Token   │
         │                        │◄────────────────────── │
         │ 4. JWT Token           │                        │
         │◄────────────────────── │                        │
         │                        │                        │
         │ 5. API Request         │                        │
         │    + Bearer Token      │                        │
         ├──────────────────────► │                        │
         │                        │ 6. Validate Token     │
         │                        ├──────────────────────► │
         │                        │ 7. User Context       │
         │                        │◄────────────────────── │
         │                        │ 8. Process Request    │
         │                        │                        │
         │ 9. API Response        │                        │
         │◄────────────────────── │                        │
```

### Authentication Methods

1. **JWT Bearer Tokens** (Primary)
   - Stateless authentication
   - Short-lived access tokens (30 minutes)
   - Long-lived refresh tokens (7 days)
   - Includes user context and permissions

2. **OAuth2/OIDC** (External Identity)
   - Keycloak integration
   - Microsoft Entra (Azure AD)
   - Generic OAuth2 providers
   - Identity mapping to OSTicket users

3. **API Keys** (System Integration)
   - Compatible with OSTicket v1 API
   - IP address restrictions
   - Permission-based access control

4. **Session-based** (Legacy Compatibility)
   - OSTicket web session cookies
   - Seamless integration with PHP app
   - Maintains existing user experience

## Database Design

### Model Organization

The 72 SQLAlchemy models are organized into logical groups:

```
Models/
├── Core System (8 models)
│   ├── Config, Session, Syslog
│   ├── ApiKey, Lock, Sequence
│   └── Translation, Event
│
├── Tickets (12 models)
│   ├── Ticket, TicketCData, TicketStatus
│   ├── Thread, ThreadEntry, ThreadEvent
│   └── Note, Priority, Collaborator
│
├── Users (6 models)
│   ├── User, UserCData, UserEmail
│   ├── UserAccount, Organization
│   └── OrganizationCData
│
├── Staff (5 models)
│   ├── Staff, Department, Team
│   └── TeamMember, Role
│
├── Forms (8 models)
│   ├── Form, FormField, FormEntry
│   ├── FormEntryValue, List
│   └── ListItem, Queue, QueueSort
│
├── Knowledge Base (6 models)
│   ├── FAQ, FAQCategory, Category
│   ├── Page, Content, Attachment
│
├── Email (10 models)
│   ├── Email, EmailTemplate
│   ├── Filter, FilterRule, FilterAction
│   └── Banlist, Draft, Plugin
│
└── Files (7 models)
    ├── File, FileChunk, Attachment
    ├── SearchIndex, Schedule
    └── SLA, Topic, Timezone
```

### Relationship Patterns

**One-to-Many**: User → Tickets
```python
class User(OSTicketBase):
    tickets = relationship("Ticket", back_populates="user")

class Ticket(OSTicketBase):
    user = relationship("User", back_populates="tickets")
```

**Many-to-Many**: Staff ↔ Teams
```python
class Staff(OSTicketBase):
    teams = relationship("Team", secondary="ost_team_member", back_populates="members")

class Team(OSTicketBase):
    members = relationship("Staff", secondary="ost_team_member", back_populates="teams")
```

**Custom Data Pattern**: Ticket → TicketCData
```python
class Ticket(OSTicketBase):
    cdata = relationship("TicketCData", back_populates="ticket", uselist=False)
```

## Security Architecture

### Multi-layered Security

1. **Transport Security**
   - HTTPS/TLS encryption
   - Secure headers (HSTS, CSP)
   - CORS configuration

2. **Authentication Security**
   - Password hashing (bcrypt)
   - JWT token signing and verification
   - OAuth2 state parameter validation
   - Token expiration and refresh

3. **Authorization Security**
   - Role-based access control
   - Resource-level permissions
   - IP-based restrictions (API keys)
   - Department-based access control

4. **Input Security**
   - Pydantic model validation
   - SQL injection prevention (ORM)
   - XSS prevention (JSON API)
   - Request size limits

5. **Data Security**
   - Structured error messages (no sensitive data leakage)
   - Request ID tracking
   - Audit logging
   - Database connection pooling

### Permission Model

The API inherits OSTicket's permission model:

```
Admin Staff ────► Full Access
   │
   ▼
Department Staff ────► Department Resources
   │
   ▼
Team Members ────► Team-assigned Tickets
   │
   ▼
End Users ────► Own Tickets + Organization Tickets
```

## Performance Architecture

### Optimization Strategies

1. **Database Optimization**
   - Connection pooling (SQLAlchemy)
   - Query optimization with indexes
   - Lazy loading for relationships
   - Batch operations for bulk updates

2. **Caching Strategy**
   - Application-level caching (planned)
   - Database query caching
   - Static content caching
   - CDN for assets (production)

3. **Asynchronous Processing**
   - FastAPI async support
   - Background tasks for heavy operations
   - Email processing queues
   - File upload streaming

4. **Monitoring and Metrics**
   - Request/response timing
   - Database query performance
   - Memory usage tracking
   - Error rate monitoring

## Deployment Architecture

### Development Environment
```
Developer Machine
├── Python Virtual Environment
├── Local MySQL Database
├── FastAPI Dev Server (auto-reload)
└── OSTicket PHP (optional)
```

### Production Environment
```
Load Balancer (nginx/Apache)
├── FastAPI Server 1 (Gunicorn + Uvicorn)
├── FastAPI Server 2 (Gunicorn + Uvicorn)
└── FastAPI Server N (Gunicorn + Uvicorn)
         │
         ▼
Database Cluster (MySQL/MariaDB)
├── Master (Read/Write)
└── Replicas (Read Only)
         │
         ▼
External Services
├── Redis (Caching)
├── Elasticsearch (Search)
└── File Storage (S3/MinIO)
```

### Containerization
```yaml
# docker-compose.yml structure
services:
  api:
    build: .
    environment:
      - DATABASE_URL=mysql://...
      - JWT_SECRET_KEY=...
    depends_on:
      - db
      - redis
  
  db:
    image: mysql:8.0
    volumes:
      - mysql_data:/var/lib/mysql
  
  redis:
    image: redis:alpine
    
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
```

## Integration Patterns

### External System Integration

1. **Identity Providers** (OAuth2/OIDC)
   - Keycloak for enterprise SSO
   - Microsoft Entra for Office 365 integration
   - Generic OAuth2 for other providers

2. **Email Systems** (SMTP/IMAP)
   - Outbound email via SMTP
   - Inbound email processing via IMAP
   - Email template rendering

3. **File Storage**
   - Local filesystem (development)
   - AWS S3 (production)
   - MinIO (self-hosted S3-compatible)

4. **Search Engines**
   - MySQL full-text search (basic)
   - Elasticsearch (advanced)
   - Ticket and knowledge base indexing

### API Integration Patterns

1. **Webhook Support** (Planned)
   - Event-driven notifications
   - Third-party system integration
   - Real-time updates

2. **Bulk Operations**
   - Batch ticket creation
   - Bulk user imports
   - Mass updates

3. **Real-time Features** (Future)
   - WebSocket support
   - Live ticket updates
   - Real-time notifications

## Scalability Considerations

### Horizontal Scaling

1. **Stateless Design**
   - JWT tokens (no server sessions)
   - Database-backed state
   - Load balancer friendly

2. **Database Scaling**
   - Read replicas for queries
   - Connection pooling
   - Query optimization

3. **Caching Layers**
   - Application caching
   - Database query caching
   - CDN for static content

### Vertical Scaling

1. **Resource Optimization**
   - Memory efficient models
   - Async I/O for database operations
   - Efficient JSON serialization

2. **Performance Monitoring**
   - Request latency tracking
   - Database performance metrics
   - Resource utilization monitoring

## Future Architecture Evolution

### Planned Enhancements

1. **Microservices Transition** (Long-term)
   - Service decomposition
   - API gateway
   - Independent scaling

2. **Event-Driven Architecture**
   - Event sourcing
   - CQRS patterns
   - Message queues

3. **Real-time Features**
   - WebSocket connections
   - Server-sent events
   - Live updates

4. **Advanced Security**
   - Rate limiting
   - Advanced threat detection
   - Zero-trust architecture

The architecture is designed to evolve gradually while maintaining compatibility with existing OSTicket installations and providing a smooth migration path for organizations adopting the new API.