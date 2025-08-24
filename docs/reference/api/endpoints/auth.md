# Authentication Endpoints

Complete reference for all authentication-related API endpoints.

## Base URL
```
https://your-domain.com/api/v2/auth
```

## Endpoints Overview

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/staff/login` | Staff authentication | No |
| POST | `/user/login` | User authentication | No |
| GET | `/oauth2/{provider}/login` | OAuth2 login initiation | No |
| GET | `/oauth2/{provider}/callback` | OAuth2 callback handler | No |
| GET | `/userinfo` | Current user information | Yes |
| POST | `/logout` | User logout | Yes |
| GET | `/providers` | Available auth providers | No |

---

## POST /staff/login

Authenticate staff member with username and password.

### Request

**Method:** `POST`  
**URL:** `/api/v2/auth/staff/login`  
**Content-Type:** `application/json`

#### Request Body Schema
```json
{
  "username": "string (required) - Staff username",
  "password": "string (required) - Staff password"
}
```

#### Example Request
```bash
curl -X POST "http://localhost:3969/api/v2/auth/staff/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "admin123"
  }'
```

### Response

#### Success (200 OK)
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJzdGFmZjoxIiwidXNlcl90eXBlIjoic3RhZmYiLCJ1c2VyX2lkIjoxLCJpYXQiOjE2NDA5OTUyMDAsInVzZXJuYW1lIjoiYWRtaW4iLCJlbWFpbCI6ImFkbWluQGV4YW1wbGUuY29tIiwiZGVwdF9pZCI6MSwiaXNhZG1pbiI6dHJ1ZSwiZXhwIjoxNjQwOTk3MDAwLCJ0eXBlIjoiYWNjZXNzIn0.signature",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJzdGFmZjoxIiwidXNlcl90eXBlIjoic3RhZmYiLCJ1c2VyX2lkIjoxLCJpYXQiOjE2NDA5OTUyMDAsInVzZXJuYW1lIjoiYWRtaW4iLCJlbWFpbCI6ImFkbWluQGV4YW1wbGUuY29tIiwiZGVwdF9pZCI6MSwiaXNhZG1pbiI6dHJ1ZSwiZXhwIjoxNjQwOTk1MjAwLCJ0eXBlIjoicmVmcmVzaCJ9.signature",
  "token_type": "bearer",
  "expires_in": 1800
}
```

#### Error (401 Unauthorized)
```json
{
  "error": {
    "code": "AUTHENTICATION_ERROR",
    "message": "Invalid username or password",
    "timestamp": "2024-01-01T12:00:00.000Z",
    "request_id": "550e8400-e29b-41d4-a716-446655440000",
    "path": "/api/v2/auth/staff/login"
  }
}
```

---

## POST /user/login

Authenticate end user with email and password.

### Request

**Method:** `POST`  
**URL:** `/api/v2/auth/user/login`  
**Content-Type:** `application/json`

#### Request Body Schema
```json
{
  "email": "string (required) - User email address",
  "password": "string (required) - User password"
}
```

#### Example Request
```bash
curl -X POST "http://localhost:3969/api/v2/auth/user/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "userpass123"
  }'
```

### Response

#### Success (200 OK)
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c2VyOjIiLCJ1c2VyX3R5cGUiOiJ1c2VyIiwidXNlcl9pZCI6MiwiaWF0IjoxNjQwOTk1MjAwLCJlbWFpbCI6InVzZXJAZXhhbXBsZS5jb20iLCJuYW1lIjoiSm9obiBEb2UiLCJleHAiOjE2NDA5OTcwMDAsInR5cGUiOiJhY2Nlc3MifQ.signature",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c2VyOjIiLCJ1c2VyX3R5cGUiOiJ1c2VyIiwidXNlcl9pZCI6MiwiaWF0IjoxNjQwOTk1MjAwLCJlbWFpbCI6InVzZXJAZXhhbXBsZS5jb20iLCJuYW1lIjoiSm9obiBEb2UiLCJleHAiOjE2NDEwODM2MDAsInR5cGUiOiJyZWZyZXNoIn0.signature",
  "token_type": "bearer",
  "expires_in": 1800
}
```

#### Error (401 Unauthorized)
```json
{
  "error": {
    "code": "AUTHENTICATION_ERROR",
    "message": "Invalid email or password",
    "timestamp": "2024-01-01T12:00:00.000Z",
    "request_id": "550e8400-e29b-41d4-a716-446655440000",
    "path": "/api/v2/auth/user/login"
  }
}
```

---

## GET /oauth2/{provider}/login

Initiate OAuth2 authentication flow with external provider.

### Request

**Method:** `GET`  
**URL:** `/api/v2/auth/oauth2/{provider}/login`

#### Path Parameters
- `provider` (string, required): Provider identifier (`keycloak`, `microsoft`)

#### Query Parameters
- `return_url` (string, optional): URL to redirect after successful authentication

#### Example Request
```bash
curl "http://localhost:3969/api/v2/auth/oauth2/keycloak/login?return_url=https://example.com/dashboard"
```

### Response

#### Success (302 Found)
Redirects to the OAuth2 provider's login page.

**Headers:**
```
Location: https://keycloak.example.com/auth/realms/osticket/protocol/openid-connect/auth?client_id=osticket&response_type=code&redirect_uri=http://localhost:3969/api/v2/auth/oauth2/keycloak/callback&state=random-state-string
```

#### Error (404 Not Found)
```json
{
  "error": {
    "code": "NOT_FOUND",
    "message": "OAuth Provider not found: invalid_provider",
    "timestamp": "2024-01-01T12:00:00.000Z",
    "request_id": "550e8400-e29b-41d4-a716-446655440000",
    "path": "/api/v2/auth/oauth2/invalid_provider/login",
    "details": {
      "resource": "OAuth Provider",
      "identifier": "invalid_provider"
    }
  }
}
```

---

## GET /oauth2/{provider}/callback

Handle OAuth2 callback from external provider.

### Request

**Method:** `GET`  
**URL:** `/api/v2/auth/oauth2/{provider}/callback`

#### Path Parameters
- `provider` (string, required): Provider identifier

#### Query Parameters
- `code` (string, required): Authorization code from provider
- `state` (string, required): State parameter for CSRF protection
- `error` (string, optional): Error code if authentication failed

### Response

#### Success (200 OK)
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.payload.signature",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.payload.signature",
  "token_type": "bearer",
  "user_type": "staff",
  "return_url": "https://example.com/dashboard"
}
```

#### Error (401 Unauthorized)
```json
{
  "error": {
    "code": "AUTHENTICATION_ERROR",
    "message": "External identity not linked to OSTicket account",
    "timestamp": "2024-01-01T12:00:00.000Z",
    "request_id": "550e8400-e29b-41d4-a716-446655440000",
    "path": "/api/v2/auth/oauth2/keycloak/callback"
  }
}
```

---

## GET /userinfo

Get current authenticated user information.

### Request

**Method:** `GET`  
**URL:** `/api/v2/auth/userinfo`  
**Authentication:** Required (Bearer token)

#### Headers
```
Authorization: Bearer <access_token>
```

#### Example Request
```bash
curl -X GET "http://localhost:3969/api/v2/auth/userinfo" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

### Response

#### Success (200 OK) - Staff User
```json
{
  "user_type": "staff",
  "user_id": 1,
  "email": "admin@example.com",
  "username": "admin",
  "name": "Administrator",
  "isadmin": true,
  "dept_id": 1
}
```

#### Success (200 OK) - End User
```json
{
  "user_type": "user",
  "user_id": 2,
  "email": "user@example.com",
  "username": null,
  "name": "John Doe",
  "isadmin": null,
  "dept_id": null
}
```

#### Error (401 Unauthorized)
```json
{
  "error": {
    "code": "AUTHENTICATION_ERROR",
    "message": "Authentication required",
    "timestamp": "2024-01-01T12:00:00.000Z",
    "request_id": "550e8400-e29b-41d4-a716-446655440000",
    "path": "/api/v2/auth/userinfo"
  }
}
```

---

## POST /logout

Logout current user and invalidate tokens.

### Request

**Method:** `POST`  
**URL:** `/api/v2/auth/logout`  
**Authentication:** Required (Bearer token)

#### Headers
```
Authorization: Bearer <access_token>
```

#### Example Request
```bash
curl -X POST "http://localhost:3969/api/v2/auth/logout" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

### Response

#### Success (200 OK)
```json
{
  "message": "Logged out successfully"
}
```

---

## GET /providers

Get list of enabled authentication providers.

### Request

**Method:** `GET`  
**URL:** `/api/v2/auth/providers`

#### Example Request
```bash
curl -X GET "http://localhost:3969/api/v2/auth/providers"
```

### Response

#### Success (200 OK)
```json
{
  "providers": {
    "keycloak": {
      "name": "keycloak",
      "login_url": "/api/v2/auth/oauth2/keycloak/login"
    },
    "microsoft": {
      "name": "microsoft",
      "login_url": "/api/v2/auth/oauth2/microsoft/login"
    },
    "osticket": {
      "name": "osticket",
      "staff_login_url": "/api/v2/auth/staff/login",
      "user_login_url": "/api/v2/auth/user/login"
    }
  },
  "native_auth_enabled": true
}
```

## Common Response Headers

All endpoints include standard response headers:

```
Content-Type: application/json
X-Request-ID: 550e8400-e29b-41d4-a716-446655440000
X-Response-Time: 0.123s
```

## Authentication Flow Examples

### 1. Staff Login Flow
```bash
# 1. Login
curl -X POST "http://localhost:3969/api/v2/auth/staff/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'

# 2. Use token for authenticated requests
curl -X GET "http://localhost:3969/api/v2/auth/userinfo" \
  -H "Authorization: Bearer <access_token>"

# 3. Logout
curl -X POST "http://localhost:3969/api/v2/auth/logout" \
  -H "Authorization: Bearer <access_token>"
```

### 2. OAuth2 Flow
```bash
# 1. Get providers
curl -X GET "http://localhost:3969/api/v2/auth/providers"

# 2. Initiate OAuth2 flow (in browser)
# GET /api/v2/auth/oauth2/keycloak/login

# 3. Provider redirects to callback (automatic)
# GET /api/v2/auth/oauth2/keycloak/callback?code=...&state=...

# 4. Use returned tokens
curl -X GET "http://localhost:3969/api/v2/auth/userinfo" \
  -H "Authorization: Bearer <access_token>"
```