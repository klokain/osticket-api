# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

# use context7 mcp for up-to-date documentation and snippets
# use linear mcp for project management and issue tracking
# use mem0 mcp for persistent memories and project context

## MCP Configuration

### Linear MCP Settings
- **Team ID**: c3082b74-500a-438e-8867-e70870c32d89 (Resulta)
- **Team Name**: Resulta
- **Project ID**: 41579720-d14b-48f1-9c1f-737f33de6e96 (OSticket API refactor)
- **Project URL**: https://linear.app/resulta/project/osticket-api-refactor-68418ae1ae08/overview
- Use Linear for tracking OSTicket API development tasks and project management

### Context7 MCP Settings
- Use for accessing up-to-date documentation for PHP, REST APIs, and related technologies
- Essential for OSTicket-specific patterns and modern PHP development practices

### Mem0 MCP Settings
- **User ID**: mem0-mcp-user (default)
- Use for storing project insights, decisions, and development patterns
- Maintain context about OSTicket architecture and refactoring decisions

## Project Overview

This is an OSTicket API refactor project aimed at gradually creating a modern REST API for OSTicket that will enable development of alternate frontends. The goal is to create a clean separation between the backend API and frontend implementations.

OSTicket is a PHP-based open source support ticket system that currently has limited API capabilities (only ticket creation via API). This refactor aims to expand the API to cover all resources.

## Project Structure

```
/usr/home/filip/ost-api/
├── osTicket/          # Original OSTicket codebase (v1.18+)
│   ├── api/           # Current limited API implementation
│   ├── include/       # Core PHP classes and business logic
│   ├── scp/           # Staff Control Panel (admin interface)
│   └── setup/         # Installation and documentation
└── [Future API structure to be created]
```

## Key OSTicket Components

### Current API Structure
- **api/api.inc.php**: API bootstrap and session handling
- **api/http.php**: HTTP API entry point
- **include/class.api.php**: API key validation and management
- **include/api.tickets.php**: Ticket creation API controller

### Core Models (in include/)
- **class.ticket.php**: Main ticket model with ORM mappings
- **class.user.php**: User/client management
- **class.staff.php**: Staff member management
- **class.dept.php**: Department management
- **class.topic.php**: Help topics
- **class.thread.php**: Ticket thread and messages
- **class.task.php**: Task management
- **class.organization.php**: Organization/company management

### Database Access
- Uses custom ORM based on VerySimpleModel (class.orm.php)
- Database abstraction through mysqli.php
- Dynamic forms system (class.dynamic_forms.php)

## Development Process

### MCP Tool Integration
- **Context7**: Use for up-to-date PHP documentation and REST API best practices
- **Linear**: Create issues for each API endpoint and track refactoring progress
- **Mem0**: Store architectural decisions and patterns discovered during refactoring

### Development Workflow
1. **Planning**: Create Linear issues for API endpoints to be developed
2. **Research**: Use Context7 to find current best practices for PHP/REST APIs
3. **Implementation**: Follow OSTicket patterns while modernizing architecture
4. **Documentation**: Update Mem0 with decisions and patterns for future reference
5. **Testing**: Validate against existing OSTicket functionality

## Development Commands

```bash
# OSTicket CLI management
php osTicket/manage.php --help

# Deploy code updates
php osTicket/manage.php deploy -v /path/to/deployment

# Run cron tasks
php osTicket/api/cron.php

# Database migrations (from setup directory)
php osTicket/setup/cli/manage.php upgrade
```

## API Development Guidelines

### Current API Authentication
- Uses API keys tied to IP addresses
- Keys managed via admin panel (Manage -> API Keys)
- Required header: `X-API-Key: [API_KEY]`

### Refactoring Strategy

1. **Create New API Layer**: Build alongside existing code without breaking current functionality
2. **RESTful Design**: Follow REST principles for resource endpoints
3. **Maintain Compatibility**: Preserve existing `/api/tickets.json` endpoint
4. **Gradual Migration**: Implement one resource at a time

### Suggested API Structure
```
/api/v2/
├── tickets/      # Full CRUD for tickets
├── users/        # User management
├── staff/        # Staff management
├── departments/  # Department operations
├── tasks/        # Task management
├── organizations/# Organization management
└── auth/         # Authentication endpoints
```

## Testing Approach

Check for existing test framework:
```bash
# Look for test files
find osTicket/setup/test -name "*.php"

# Run tests if available
php osTicket/setup/test/run-tests.php
```

## Important Considerations

1. **Database Schema**: OSTicket uses prefixed tables (ost_*). Check ost-sampleconfig.php for configuration
2. **Session Management**: API calls use stateless sessions (API_SESSION constant)
3. **Forms System**: OSTicket has a dynamic forms system - consider this for API field validation
4. **Permissions**: Existing role-based permission system in class.role.php
5. **File Attachments**: Handled through class.file.php and class.attachment.php

## Code Style

- PHP 8.2+ compatible (recommended 8.4)
- Follow existing OSTicket patterns for consistency
- Use existing ORM patterns from class.orm.php
- Maintain backward compatibility with existing API

## Security Notes

- API keys are stored in API_KEY_TABLE
- IP validation is enforced for API access
- CSRF protection via class.csrf.php for web requests
- Input validation through class.validator.php

## Next Steps for Refactor

1. Analyze existing API usage patterns
2. Design RESTful endpoint structure
3. Create API versioning strategy (v1 legacy, v2 new)
4. Implement authentication/authorization layer
5. Build resource controllers extending ApiController
6. Add comprehensive API documentation
7. Implement rate limiting and throttling
8. Create API testing framework
- never put claude code signature in the commits. put small [cc] at the end of the message. that's all.
- when working on linear issue, always check the subissues