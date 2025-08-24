# OSTicket API - FastAPI Implementation

A modern REST API server for OSTicket built with FastAPI that can coexist with existing OSTicket installations.

## Overview

This project creates a comprehensive REST API for OSTicket while maintaining full compatibility with existing OSTicket installations. The FastAPI server reads and writes to the same MySQL database as OSTicket, enabling gradual migration to modern frontends.

## Development Setup

### Prerequisites

- Python 3.11+
- MySQL 5.5+ (same as OSTicket requirements)
- Local OSTicket installation (for development and testing)
- Git

### Quick Start

1. **Clone this repository:**
   ```bash
   git clone git@github.com:klokain/osticket-api.git
   cd osticket-api
   ```

2. **Set up OSTicket for development:**
   ```bash
   # Clone OSTicket v1.18.x for development reference
   git clone -b 1.18.x https://github.com/osTicket/osTicket.git osTicket
   ```
   
   **Note:** The `osTicket/` directory is intentionally excluded from version control (.gitignore) as it serves as a development dependency.

3. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your database credentials
   ```

4. **Install Python dependencies:**
   ```bash
   cd api-server
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

5. **Run the development server:**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

6. **Access the API documentation:**
   - Swagger UI: http://localhost:8000/api/docs
   - ReDoc: http://localhost:8000/api/redoc

### Why OSTicket is needed locally

The FastAPI server requires access to OSTicket for development because:

- **Direct database access**: Maps to existing OSTicket tables (`ost_ticket`, `ost_user`, etc.)
- **Schema compatibility**: Ensures API writes data in OSTicket-compatible format
- **Business logic reference**: Uses OSTicket's validation rules and workflows
- **Testing integration**: Verifies API works alongside existing OSTicket installation

### Project Structure

```
osticket-api/
├── osTicket/                    # OSTicket v1.18.x (development reference)
├── api-server/                  # FastAPI application (to be created)
├── docs/                        # Planning and implementation docs
│   ├── API_DEVELOPMENT_PLAN.md
│   ├── FASTAPI_IMPLEMENTATION_PLAN.md
│   ├── FASTAPI_VS_PHP_ANALYSIS.md
│   └── COEXISTENCE_GUIDE.md
├── CLAUDE.md                    # Project context for AI assistance
├── setup-dev.sh               # Development environment setup script
├── .env.example               # Environment configuration template
└── README.md
```

## Key Features (Planned)

- **Full REST API** for all OSTicket resources
- **Coexistence** with existing OSTicket installations
- **JWT Authentication** with API key compatibility
- **Real-time updates** via WebSocket
- **Automatic API documentation** (OpenAPI/Swagger)
- **High performance** (3-5x faster than PHP)
- **Modern architecture** with async/await support

## API Endpoints (Planned)

### v2 REST API
- `GET/POST /api/v2/tickets` - Ticket management
- `GET/POST /api/v2/users` - User management  
- `GET/POST /api/v2/organizations` - Organization management
- `GET/POST /api/v2/departments` - Department operations
- `GET/POST /api/v2/staff` - Staff management
- `POST /api/v2/auth/login` - Authentication

### v1 Legacy Compatibility
- `POST /api/tickets.json` - Maintains existing OSTicket API compatibility

## Development Workflow

1. **Database Development**: Work against live OSTicket MySQL database
2. **API Development**: Build FastAPI endpoints that read/write OSTicket tables
3. **Testing**: Verify both systems can operate simultaneously
4. **Frontend Integration**: Build modern frontends using the new API

## Documentation

- **[API Development Plan](docs/API_DEVELOPMENT_PLAN.md)** - Comprehensive development strategy
- **[FastAPI Implementation Guide](docs/FASTAPI_IMPLEMENTATION_PLAN.md)** - Detailed implementation with code examples
- **[FastAPI vs PHP Analysis](docs/FASTAPI_VS_PHP_ANALYSIS.md)** - Technology comparison and rationale
- **[Coexistence Guide](docs/COEXISTENCE_GUIDE.md)** - How to run alongside OSTicket

## Contributing

This is a development project for creating a modern API layer for OSTicket. See the planning documents in the `docs/` directory for implementation details.

## License

This project is licensed under the GPL-2.0 License - same as OSTicket.
