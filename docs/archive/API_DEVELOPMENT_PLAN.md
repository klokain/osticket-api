# OSTicket API Development Plan

## Executive Summary

This document outlines a comprehensive plan for building a modern REST API server for OSTicket that will enable development of alternate frontends while maintaining compatibility with the existing system.

## Current State Analysis

### Existing Infrastructure

#### Database Architecture
- **Core Tables**: Prefixed with `ost_` (configurable)
- **Primary Entities**:
  - Tickets (`ost_ticket`, `ost_ticket__cdata`)
  - Users (`ost_user`, `ost_user_email`, `ost_user_account`)
  - Staff (`ost_staff`)
  - Organizations (`ost_organization`)
  - Departments (`ost_department`)
  - Threads (`ost_thread`, `ost_thread_entry`)
  - Tasks (`ost_task`)
  - FAQ/Knowledge Base (`ost_faq`, `ost_faq_category`)

#### Current API Limitations
- Only supports ticket creation (POST `/api/tickets.json`)
- IP-based authentication with API keys
- No RESTful resource endpoints
- No read/update/delete operations
- Limited to JSON/XML formats for tickets only

#### Authentication Mechanisms
- API Keys with IP restrictions
- Staff authentication (username/password + optional 2FA)
- Client authentication (email-based)
- OAuth2 support available
- Database-backed sessions

## Proposed Architecture

### 1. API Server Structure

```
/usr/home/filip/ost-api/
├── api-server/                 # New API server directory
│   ├── src/
│   │   ├── controllers/        # API endpoint controllers
│   │   │   ├── BaseController.php
│   │   │   ├── TicketController.php
│   │   │   ├── UserController.php
│   │   │   ├── StaffController.php
│   │   │   ├── DepartmentController.php
│   │   │   ├── OrganizationController.php
│   │   │   └── AuthController.php
│   │   ├── models/            # Data models wrapping OSTicket classes
│   │   │   ├── TicketModel.php
│   │   │   ├── UserModel.php
│   │   │   └── ...
│   │   ├── middleware/        # Request/response middleware
│   │   │   ├── Authentication.php
│   │   │   ├── RateLimiting.php
│   │   │   ├── CORS.php
│   │   │   └── Validation.php
│   │   ├── routes/            # Route definitions
│   │   │   ├── api_v1.php    # Legacy compatibility
│   │   │   └── api_v2.php    # New REST endpoints
│   │   ├── services/          # Business logic services
│   │   │   ├── TicketService.php
│   │   │   ├── NotificationService.php
│   │   │   └── SearchService.php
│   │   ├── transformers/      # Response formatters
│   │   │   ├── TicketTransformer.php
│   │   │   └── UserTransformer.php
│   │   └── utils/             # Helper utilities
│   │       ├── Database.php
│   │       ├── Paginator.php
│   │       └── ResponseBuilder.php
│   ├── config/
│   │   ├── api.php            # API configuration
│   │   ├── database.php       # Database settings
│   │   └── routes.php         # Route configuration
│   ├── public/
│   │   └── index.php          # Entry point
│   ├── tests/
│   │   ├── unit/
│   │   ├── integration/
│   │   └── fixtures/
│   ├── docs/                  # API documentation
│   │   ├── openapi.yaml       # OpenAPI specification
│   │   └── postman/           # Postman collections
│   ├── composer.json          # PHP dependencies
│   └── .env.example           # Environment configuration
```

### 2. Technology Stack

#### Core Technologies
- **PHP 8.2+** (matching OSTicket requirements)
- **Slim Framework 4** or **Lumen** for lightweight REST API
- **PSR-7/PSR-15** compliant middleware
- **Composer** for dependency management
- **PHPUnit** for testing

#### Key Dependencies
```json
{
  "require": {
    "php": "^8.2",
    "slim/slim": "^4.0",
    "slim/psr7": "^1.0",
    "firebase/php-jwt": "^6.0",
    "respect/validation": "^2.0",
    "monolog/monolog": "^3.0",
    "vlucas/phpdotenv": "^5.0"
  },
  "require-dev": {
    "phpunit/phpunit": "^10.0",
    "mockery/mockery": "^1.0",
    "fakerphp/faker": "^1.0"
  }
}
```

### 3. API Endpoints Design

#### Version 1 (Legacy Compatibility)
- `POST /api/tickets.json` - Maintain existing ticket creation

#### Version 2 (RESTful API)

##### Authentication Endpoints
```
POST   /api/v2/auth/login        # Staff/client login
POST   /api/v2/auth/logout       # Logout
POST   /api/v2/auth/refresh      # Refresh JWT token
GET    /api/v2/auth/me           # Current user info
```

##### Ticket Endpoints
```
GET    /api/v2/tickets           # List tickets (with filters)
GET    /api/v2/tickets/{id}      # Get ticket details
POST   /api/v2/tickets           # Create ticket
PUT    /api/v2/tickets/{id}      # Update ticket
DELETE /api/v2/tickets/{id}      # Delete ticket
POST   /api/v2/tickets/{id}/reply     # Add reply
POST   /api/v2/tickets/{id}/assign    # Assign ticket
POST   /api/v2/tickets/{id}/transfer  # Transfer department
GET    /api/v2/tickets/{id}/thread    # Get conversation thread
```

##### User Endpoints
```
GET    /api/v2/users             # List users
GET    /api/v2/users/{id}        # Get user details
POST   /api/v2/users             # Create user
PUT    /api/v2/users/{id}        # Update user
DELETE /api/v2/users/{id}        # Delete user
GET    /api/v2/users/{id}/tickets # User's tickets
```

##### Organization Endpoints
```
GET    /api/v2/organizations     # List organizations
GET    /api/v2/organizations/{id} # Get organization
POST   /api/v2/organizations     # Create organization
PUT    /api/v2/organizations/{id} # Update organization
DELETE /api/v2/organizations/{id} # Delete organization
GET    /api/v2/organizations/{id}/users   # Organization members
GET    /api/v2/organizations/{id}/tickets # Organization tickets
```

##### Department Endpoints
```
GET    /api/v2/departments       # List departments
GET    /api/v2/departments/{id}  # Get department
POST   /api/v2/departments       # Create department
PUT    /api/v2/departments/{id}  # Update department
DELETE /api/v2/departments/{id}  # Delete department
```

##### Staff Endpoints
```
GET    /api/v2/staff             # List staff members
GET    /api/v2/staff/{id}        # Get staff details
POST   /api/v2/staff             # Create staff
PUT    /api/v2/staff/{id}        # Update staff
DELETE /api/v2/staff/{id}        # Delete staff
GET    /api/v2/staff/{id}/tickets # Assigned tickets
```

### 4. Authentication Strategy

#### Multi-Authentication Support
1. **JWT Tokens** (Primary for new API)
   - Stateless authentication
   - Configurable expiration
   - Refresh token mechanism

2. **API Keys** (Legacy support)
   - Maintain backward compatibility
   - IP restriction support
   - Rate limiting per key

3. **Session-based** (Optional)
   - For web-based frontends
   - CSRF protection

#### Implementation
```php
// Example middleware stack
$app->add(new RateLimitMiddleware());
$app->add(new CORSMiddleware());
$app->add(new AuthenticationMiddleware([
    'jwt' => new JWTAuthProvider(),
    'apikey' => new APIKeyAuthProvider(),
    'session' => new SessionAuthProvider()
]));
```

### 5. Database Integration Strategy

#### Approach: Wrapper Pattern
- Create model wrappers around existing OSTicket classes
- Reuse existing ORM and business logic
- Gradual migration path

```php
// Example wrapper
class TicketModel {
    private $osticket_ticket;
    
    public function __construct() {
        require_once OSTICKET_INCLUDE_DIR . 'class.ticket.php';
    }
    
    public function find($id) {
        $ticket = Ticket::lookup($id);
        return $this->transform($ticket);
    }
    
    public function create(array $data) {
        // Use existing OSTicket validation and creation
        return Ticket::create($data);
    }
}
```

## Implementation Phases

### Phase 1: Foundation (Week 1-2)
- [ ] Set up project structure
- [ ] Configure Slim/Lumen framework
- [ ] Implement basic routing
- [ ] Create database connection wrapper
- [ ] Set up configuration management
- [ ] Implement logging system

### Phase 2: Authentication (Week 2-3)
- [ ] Implement JWT authentication
- [ ] Create API key compatibility layer
- [ ] Build authentication middleware
- [ ] Implement rate limiting
- [ ] Add CORS support
- [ ] Create auth endpoints

### Phase 3: Core Resources (Week 3-5)
- [ ] Implement Ticket endpoints
  - [ ] List with pagination/filtering
  - [ ] CRUD operations
  - [ ] Thread management
  - [ ] Status updates
- [ ] Implement User endpoints
  - [ ] CRUD operations
  - [ ] Profile management
  - [ ] Ticket associations

### Phase 4: Extended Resources (Week 5-6)
- [ ] Organization management
- [ ] Department operations
- [ ] Staff management
- [ ] Team operations
- [ ] Priority/SLA/Topic endpoints

### Phase 5: Advanced Features (Week 6-7)
- [ ] Search functionality
- [ ] File upload/attachment handling
- [ ] Email integration endpoints
- [ ] Webhook support
- [ ] Real-time notifications (WebSocket/SSE)

### Phase 6: Testing & Documentation (Week 7-8)
- [ ] Unit tests for all components
- [ ] Integration tests
- [ ] API documentation (OpenAPI)
- [ ] Postman collection
- [ ] Performance testing
- [ ] Security audit

### Phase 7: Deployment & Migration (Week 8-9)
- [ ] Docker containerization
- [ ] CI/CD pipeline setup
- [ ] Migration scripts
- [ ] Monitoring setup
- [ ] Production deployment guide

## Technical Requirements

### System Requirements
- PHP 8.2+ with extensions:
  - mysqli
  - json
  - mbstring
  - openssl
  - fileinfo
- MySQL 5.5+ (matching OSTicket)
- Redis/Memcached (optional, for caching)
- Nginx/Apache web server

### Development Environment
```dockerfile
# Example Docker setup
FROM php:8.2-fpm
RUN docker-php-ext-install mysqli pdo pdo_mysql
RUN pecl install redis && docker-php-ext-enable redis
COPY . /var/www/api
WORKDIR /var/www/api
RUN composer install
```

### Configuration Management
```php
// .env example
APP_ENV=development
APP_DEBUG=true
APP_URL=http://localhost:8080

DB_CONNECTION=mysql
DB_HOST=127.0.0.1
DB_PORT=3306
DB_DATABASE=osticket
DB_USERNAME=root
DB_PASSWORD=

JWT_SECRET=your-secret-key
JWT_TTL=3600
JWT_REFRESH_TTL=604800

RATE_LIMIT_ENABLED=true
RATE_LIMIT_REQUESTS=60
RATE_LIMIT_WINDOW=60
```

## Security Considerations

### API Security
1. **Input Validation**: Use Respect\Validation for all inputs
2. **SQL Injection**: Leverage OSTicket's existing prepared statements
3. **XSS Prevention**: Sanitize all outputs
4. **CSRF Protection**: For session-based auth
5. **Rate Limiting**: Per IP and per API key
6. **HTTPS Only**: Enforce SSL in production
7. **API Versioning**: Maintain backward compatibility

### Data Protection
- Implement field-level permissions
- Audit logging for sensitive operations
- Data encryption for sensitive fields
- GDPR compliance considerations

## Testing Strategy

### Unit Tests
```php
class TicketControllerTest extends TestCase {
    public function testCreateTicket() {
        $data = [
            'subject' => 'Test Ticket',
            'message' => 'Test message',
            'email' => 'test@example.com'
        ];
        
        $response = $this->post('/api/v2/tickets', $data);
        $response->assertStatus(201);
        $response->assertJsonStructure(['id', 'number', 'status']);
    }
}
```

### Integration Tests
- Test full request/response cycle
- Database transaction testing
- Authentication flow testing
- Error handling verification

### Performance Testing
- Load testing with Apache JMeter
- Response time benchmarks
- Database query optimization
- Caching effectiveness

## Monitoring & Maintenance

### Logging Strategy
- Application logs (Monolog)
- Access logs
- Error tracking (Sentry integration)
- Performance metrics

### Monitoring
- API endpoint health checks
- Response time tracking
- Error rate monitoring
- Database performance metrics

## Success Metrics

### Technical Metrics
- API response time < 200ms for simple queries
- 99.9% uptime
- Support for 1000+ concurrent users
- Test coverage > 80%

### Business Metrics
- Successful migration of existing integrations
- Adoption by frontend developers
- Reduction in support tickets about API
- Time to implement new features

## Risks & Mitigation

### Technical Risks
1. **Database Schema Changes**: Monitor OSTicket updates
2. **Performance Issues**: Implement caching layer
3. **Breaking Changes**: Maintain version compatibility
4. **Security Vulnerabilities**: Regular security audits

### Mitigation Strategies
- Comprehensive testing suite
- Gradual rollout with feature flags
- Rollback procedures
- Regular backups
- Documentation and training

## Next Steps

1. **Approval**: Review and approve this plan
2. **Environment Setup**: Prepare development environment
3. **Team Assignment**: Allocate resources
4. **Kickoff**: Begin Phase 1 implementation
5. **Regular Reviews**: Weekly progress meetings

## Appendix

### A. Database Schema Reference
Key tables and relationships documented in CLAUDE.md

### B. OSTicket Class Reference
- Ticket: `/include/class.ticket.php`
- User: `/include/class.user.php`
- Staff: `/include/class.staff.php`
- Organization: `/include/class.organization.php`

### C. API Response Format
```json
{
  "success": true,
  "data": {
    // Resource data
  },
  "meta": {
    "page": 1,
    "per_page": 20,
    "total": 100
  },
  "errors": []
}
```

### D. Error Codes
- 400: Bad Request
- 401: Unauthorized
- 403: Forbidden
- 404: Not Found
- 422: Validation Error
- 429: Rate Limited
- 500: Server Error

---

*This plan is a living document and will be updated as the project progresses.*