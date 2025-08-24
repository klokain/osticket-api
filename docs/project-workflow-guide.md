# OSTicket API Refactor - Project Workflow Guide

## Project Overview
This document outlines the development workflow, conventions, and best practices for the OSTicket API refactor project. The goal is to create a modern REST API layer for OSTicket while maintaining the existing functionality.

## Project Management

### Linear Project Structure
- **Project**: OSTicket API Refactor
- **Team**: Resulta (c3082b74-500a-438e-8867-e70870c32d89)
- **Project ID**: 41579720-d14b-48f1-9c1f-737f33de6e96

### Issue Organization
- Parent issues represent major components (e.g., RES-15: Infrastructure Foundation)
- Sub-tasks break down implementation details
- Phase labels indicate development timeline (Phase 1-4)
- Priority levels: P0 (Critical), P1 (High), P2 (Medium), P3 (Low)

## GitHub Workflow

### Branch Naming Conventions
**Format**: `<type>/<issue-number>-<brief-description>`

#### Branch Types
- `feature/` - New functionality
- `fix/` - Bug fixes
- `refactor/` - Code improvements without changing functionality
- `docs/` - Documentation updates
- `test/` - Test additions or modifications

#### Examples
- ❌ `feature/res-15` (Old format - unclear)
- ✅ `feature/res-15-api-authentication` (New format - descriptive)
- ✅ `feature/res-16-ticket-crud-endpoints`
- ✅ `fix/res-24-permission-validation`
- ✅ `docs/res-20-api-documentation`

### Commit Message Standards
- Keep messages concise and descriptive
- Include issue reference when applicable
- Add `[cc]` at the end to indicate Claude Code assistance
- Format: `<verb> <what changed> [cc]`

#### Examples
```
Add JWT authentication for API endpoints [cc]
Fix ticket status validation logic [cc]
Update API documentation for ticket endpoints [cc]
Refactor database connection pooling [cc]
```

## Documentation

### Documentation Structure
```
/usr/home/filip/ost-api/
├── docs/                        # All project documentation
│   ├── project-workflow-guide.md    # This file
│   ├── analysis-phase-plan.md       # Analysis planning
│   ├── analysis-phase-report.md     # Analysis results
│   ├── api/                         # API documentation
│   │   ├── endpoints/               # Endpoint specifications
│   │   ├── authentication.md       # Auth documentation
│   │   └── schemas/                 # Request/response schemas
│   ├── architecture/                # Architecture decisions
│   │   ├── decisions/              # ADRs (Architecture Decision Records)
│   │   └── diagrams/                # System diagrams
│   └── development/                 # Development guides
│       ├── setup.md                 # Local setup instructions
│       └── testing.md               # Testing guidelines
```

### Documentation Updates
1. **When to Update**:
   - After implementing new features
   - When API endpoints change
   - After architectural decisions
   - When discovering important OSTicket behaviors

2. **How to Update**:
   - Create feature branch with descriptive name
   - Update relevant markdown files
   - Include code examples where helpful
   - Update the table of contents if adding new files
   - Commit with clear message and `[cc]` tag

3. **Documentation Standards**:
   - Use Markdown format
   - Include code examples with syntax highlighting
   - Add diagrams for complex flows (Mermaid preferred)
   - Keep language clear and concise
   - Update timestamps where relevant

## Development Process

### 1. Starting Work on an Issue
```bash
# 1. Update main branch
git checkout main
git pull origin main

# 2. Create descriptive feature branch
git checkout -b feature/res-XX-brief-description

# 3. Update Linear issue status to "In Progress"
```

### 2. During Development
- Follow existing OSTicket code patterns
- Use Context7 MCP for up-to-date PHP/API documentation
- Update Mem0 with important discoveries
- Write tests for new functionality
- Document API changes immediately

### 3. Code Review Preparation
```bash
# Run linting and tests
php osTicket/manage.php lint
php osTicket/setup/test/run-tests.php

# Ensure documentation is updated
# Create clear commit history
git log --oneline
```

### 4. Pull Request
- Reference Linear issue in PR description
- Include summary of changes
- List any breaking changes
- Update API documentation if needed
- Request review from team members

## API Development Guidelines

### Endpoint Naming
- Use RESTful conventions
- Plural resource names (e.g., `/tickets`, `/users`)
- Nested resources where logical (e.g., `/tickets/{id}/threads`)
- Version prefix: `/api/v2/`

### Response Formats
- Consistent JSON structure
- Include metadata for collections
- Use HTTP status codes correctly
- Provide meaningful error messages

### Example Response Structure
```json
{
  "data": {...},
  "meta": {
    "total": 100,
    "page": 1,
    "per_page": 20
  },
  "links": {
    "self": "/api/v2/tickets?page=1",
    "next": "/api/v2/tickets?page=2"
  }
}
```

## Testing Strategy

### Test Organization
```
tests/
├── unit/           # Unit tests for individual components
├── integration/    # Integration tests for API endpoints
├── fixtures/       # Test data and mocks
└── performance/    # Performance benchmarks
```

### Running Tests
```bash
# Run all tests
php osTicket/setup/test/run-tests.php

# Run specific test suite
php osTicket/setup/test/run-tests.php --suite=api

# Run with coverage
php osTicket/setup/test/run-tests.php --coverage
```

## MCP Tool Usage

### Context7 (Documentation)
- Use for PHP best practices
- Research REST API patterns
- Find modern authentication methods

### Linear (Project Management)
- Update issue status promptly
- Add comments for important decisions
- Link PRs to issues

### Mem0 (Knowledge Base)
- Store architectural decisions
- Document OSTicket quirks
- Save performance optimization findings

## Common Tasks

### Adding a New API Endpoint
1. Create Linear sub-task under appropriate parent issue
2. Create feature branch with descriptive name
3. Implement endpoint following REST conventions
4. Add tests for the endpoint
5. Document in `/docs/api/endpoints/`
6. Update Postman collection
7. Create PR with Linear reference

### Updating Existing OSTicket Functionality
1. Analyze impact on existing code
2. Create refactor branch
3. Maintain backward compatibility
4. Update tests
5. Document changes in ADR
6. Gradual migration approach

## Environment Setup

### Local Development
```bash
# Clone repository
git clone git@github.com:klokain/osticket-api.git
cd osticket-api

# Install dependencies
composer install

# Configure database
cp osTicket/include/ost-sampleconfig.php osTicket/include/ost-config.php
# Edit ost-config.php with your database credentials

# Run migrations
php osTicket/setup/cli/manage.php upgrade

# Start development server
php -S localhost:8000 -t osTicket/
```

### Required Tools
- PHP 8.2+ (8.4 recommended)
- MySQL 5.7+ or MariaDB 10.3+
- Composer 2.0+
- Git
- Linear CLI (optional)

## Troubleshooting

### Common Issues
1. **Permission Errors**: Ensure web server has write access to `osTicket/include/` and `osTicket/assets/`
2. **API Key Issues**: Check IP restrictions in admin panel
3. **Database Errors**: Verify table prefixes match configuration

### Debug Mode
```php
// Enable in ost-config.php
define('OSTSCPDEBUG', true);
define('DISPLAY_ERRORS', true);
```

## Contact & Support

- **Linear Project**: [OSTicket API Refactor](https://linear.app/resulta/project/osticket-api-refactor-68418ae1ae08)
- **GitHub Repository**: [klokain/osticket-api](https://github.com/klokain/osticket-api)
- **Team**: Resulta Development Team

## Version History
- v1.0 - Initial workflow guide (2025-01-24)

---

*This document is maintained as part of the OSTicket API refactor project. Updates should be committed with the `[cc]` tag when using Claude Code assistance.*