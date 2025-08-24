# OSTicket API v2 Documentation

A modern REST API for OSTicket that enables development of alternate frontends while maintaining compatibility with the existing system.

## 🚀 Project Status

**Current Version:** 2.0.0 (Development)  
**Implementation Status:** ✅ Authentication Infrastructure Complete

### ✅ Implemented Features
- **Complete Database Models**: 72 SQLAlchemy models covering all OSTicket tables
- **Authentication System**: JWT, OAuth2, and native OSTicket authentication
- **Core Infrastructure**: Middleware, exception handling, database connectivity
- **API Endpoints**: Authentication, health checks, and user management

### 🚧 In Development
- Ticket management endpoints
- Staff and department management
- Knowledge base API
- File attachment handling

## 📚 Documentation Structure

This documentation follows the [Diátaxis](https://diataxis.fr/) framework, organizing content by user needs:

### 📖 Tutorials (Learning-oriented)
*Step-by-step guides for beginners*

- [Getting Started](tutorials/01-getting-started.md) - Set up your development environment
- [Your First API Request](tutorials/02-first-api-request.md) - Make your first API call
- [Authentication Basics](tutorials/03-authentication-basics.md) - Understand authentication methods
- [Creating Tickets](tutorials/04-creating-tickets.md) - Create tickets via API

### 🔧 How-to Guides (Task-oriented)
*Practical guides for specific tasks*

- [Setup Development Environment](how-to/setup-development.md) - Complete dev setup with database
- [Configure Authentication](how-to/configure-authentication.md) - Set up auth methods
- [Implement OAuth2](how-to/implement-oauth2.md) - Add OAuth2 providers (Keycloak, Microsoft Entra)
- [Add API Endpoints](how-to/add-api-endpoints.md) - Guide for adding new endpoints
- [Test API Endpoints](how-to/test-api-endpoints.md) - Testing with curl, Postman, pytest
- [Deploy to Production](how-to/deploy-production.md) - Production deployment

### 📋 Reference (Information-oriented)
*Technical specifications and API documentation*

#### API Reference
- [Authentication API](reference/api/authentication.md) - Auth endpoints and flows
- [Authentication Endpoints](reference/api/endpoints/auth.md) - `/api/v2/auth/*` endpoints
- [Ticket Endpoints](reference/api/endpoints/tickets.md) - Ticket management API
- [User Endpoints](reference/api/endpoints/users.md) - User management API
- [Staff Endpoints](reference/api/endpoints/staff.md) - Staff management API
- [Error Responses](reference/api/errors.md) - Error codes and formats

#### Database Models
- [Model Index](reference/models/index.md) - Complete list of 72 models
- [Ticket Models](reference/models/ticket-models.md) - Ticket, Thread, Status models
- [User Models](reference/models/user-models.md) - User, Organization models
- [Staff Models](reference/models/staff-models.md) - Staff, Department, Team models
- [System Models](reference/models/system-models.md) - Config, Session, API keys

#### Configuration
- [Configuration Reference](reference/configuration.md) - Environment variables and settings
- [Database Schema](reference/database-schema.md) - Complete schema documentation

### 💡 Explanation (Understanding-oriented)
*Background information and concepts*

- [System Architecture](explanation/architecture.md) - Overall design and components
- [Authentication Flow](explanation/authentication-flow.md) - How auth works (JWT, OAuth2, sessions)
- [Coexistence Strategy](explanation/coexistence-strategy.md) - How API v2 works with OSTicket
- [Migration Path](explanation/migration-path.md) - Migrating from API v1 to v2

## 🏃‍♂️ Quick Start

### Prerequisites
- Python 3.8+
- MySQL/MariaDB
- OSTicket installation (for database schema)

### Installation
```bash
git clone <repository>
cd ost-api
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Configuration
```bash
cp api/v2/core/config.py.example api/v2/core/config.py
# Edit config.py with your database settings
```

### Run the API
```bash
uvicorn api.v2.main:app --host 0.0.0.0 --port 3969 --reload
```

Visit `http://localhost:3969/api/v2/docs` for interactive API documentation.

## 🔐 Authentication

The API supports multiple authentication methods:

1. **JWT Bearer Tokens** (Recommended for web applications)
   ```bash
   curl -H "Authorization: Bearer <token>" http://localhost:3969/api/v2/auth/userinfo
   ```

2. **API Keys** (For server-to-server integration)
   ```bash
   curl -H "X-API-Key: <api-key>" http://localhost:3969/api/v2/tickets
   ```

3. **OAuth2/OIDC** (Keycloak, Microsoft Entra)
   ```
   GET /api/v2/auth/oauth2/{provider}/login
   ```

4. **Session-based** (Compatible with OSTicket sessions)

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   FastAPI       │    │   OSTicket      │
│   Applications  │◄──►│   API v2        │◄──►│   Database      │
│                 │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                       ┌─────────────────┐
                       │   OSTicket      │
                       │   PHP App       │
                       │   (Existing)    │
                       └─────────────────┘
```

- **FastAPI**: Modern Python web framework for the API layer
- **SQLAlchemy**: Database ORM with 1:1 mapping to OSTicket tables
- **JWT**: Stateless authentication tokens
- **OAuth2**: Integration with identity providers
- **Coexistence**: API runs alongside existing OSTicket installation

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Follow the existing code style
4. Add tests for new functionality
5. Update documentation
6. Submit a pull request

## 📄 License

This project is licensed under the same terms as OSTicket.

## 🆘 Support

- **Documentation Issues**: Create an issue in this repository
- **API Questions**: Check the [API Reference](reference/api/) section
- **OSTicket Issues**: Refer to the [OSTicket community](https://forum.osticket.com/)

---

*Last updated: $(date +"%Y-%m-%d")*