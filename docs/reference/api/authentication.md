# Authentication API Reference

The OSTicket API v2 supports multiple authentication methods to accommodate different use cases and integration patterns.

## Authentication Methods

### 1. JWT Bearer Tokens (Recommended)

JWT tokens provide stateless authentication ideal for web applications and SPAs.

**Workflow:**
1. Login with credentials to receive access and refresh tokens
2. Include access token in `Authorization` header for API requests
3. Refresh token when access token expires

**Headers:**
```
Authorization: Bearer <access_token>
```

**Token Types:**
- **Access Token**: Short-lived (30 minutes), used for API requests
- **Refresh Token**: Long-lived (7 days), used to obtain new access tokens

### 2. API Keys

Server-to-server authentication using OSTicket's existing API key system.

**Headers:**
```
X-API-Key: <api_key>
```

**Features:**
- IP address restrictions
- Per-key permissions
- Compatible with OSTicket v1 API keys

### 3. OAuth2/OIDC

Third-party identity provider integration for enterprise environments.

**Supported Providers:**
- Keycloak
- Microsoft Entra (Azure AD)
- Generic OAuth2/OIDC

**Flow:**
1. Redirect user to provider login
2. Provider redirects back with authorization code
3. Exchange code for tokens
4. Map external identity to OSTicket user

### 4. Session-based Authentication

Compatible with existing OSTicket web sessions.

**Headers:**
```
Cookie: OSTSESSID=<session_id>
```

## Authentication Endpoints

### Staff Login
```http
POST /api/v2/auth/staff/login
```

Authenticate staff member with username and password.

**Request Body:**
```json
{
  "username": "admin",
  "password": "password123"
}
```

**Success Response (200):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

**Error Response (401):**
```json
{
  "error": {
    "code": "AUTHENTICATION_ERROR",
    "message": "Invalid username or password",
    "timestamp": "2024-01-01T12:00:00.000Z",
    "request_id": "uuid-here",
    "path": "/api/v2/auth/staff/login"
  }
}
```

### User Login
```http
POST /api/v2/auth/user/login
```

Authenticate end user with email and password.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**Success Response (200):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

### OAuth2 Login Initiation
```http
GET /api/v2/auth/oauth2/{provider}/login?return_url={optional_url}
```

Initiate OAuth2 login flow with external provider.

**Parameters:**
- `provider`: Provider identifier (`keycloak`, `microsoft`, etc.)
- `return_url`: Optional URL to redirect after successful authentication

**Response:**
- **302 Redirect** to provider login page

### OAuth2 Callback
```http
GET /api/v2/auth/oauth2/{provider}/callback?code={auth_code}&state={state}
```

Handle OAuth2 callback from external provider.

**Parameters:**
- `provider`: Provider identifier
- `code`: Authorization code from provider
- `state`: State parameter for CSRF protection

**Success Response (200):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user_type": "staff",
  "return_url": "https://example.com/dashboard"
}
```

### Get User Info
```http
GET /api/v2/auth/userinfo
```

Get current authenticated user information.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Success Response (200):**
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

### Logout
```http
POST /api/v2/auth/logout
```

Logout current user and invalidate tokens.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Success Response (200):**
```json
{
  "message": "Logged out successfully"
}
```

### Get Authentication Providers
```http
GET /api/v2/auth/providers
```

Get list of enabled authentication providers.

**Success Response (200):**
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

## JWT Token Structure

### Access Token Payload
```json
{
  "sub": "staff:1",
  "user_type": "staff",
  "user_id": 1,
  "username": "admin",
  "email": "admin@example.com",
  "dept_id": 1,
  "isadmin": true,
  "iat": 1640995200,
  "exp": 1640997000,
  "type": "access"
}
```

### Token Validation

Tokens are validated using:
- **Signature**: HMAC-SHA256 with secret key
- **Expiration**: `exp` claim checked on each request
- **User Existence**: User/staff record verified in database
- **Token Type**: `type` claim must be "access" for API requests

## Security Considerations

### Password Hashing
- **bcrypt**: Used for new passwords (recommended)
- **MD5**: Legacy support for existing OSTicket installations
- **Automatic Detection**: System detects hash type and validates accordingly

### Token Security
- **Secret Key**: Configure strong JWT secret key in production
- **HTTPS**: Always use HTTPS in production
- **Token Storage**: Store refresh tokens securely (httpOnly cookies recommended)

### API Key Security
- **IP Restrictions**: Limit API key usage to specific IP addresses
- **Least Privilege**: Grant minimal required permissions
- **Rotation**: Regular API key rotation recommended

### OAuth2 Security
- **State Parameter**: CSRF protection for OAuth2 flows
- **Redirect URI Validation**: Strict redirect URI validation
- **Scope Limitation**: Request minimal required scopes

## Error Handling

All authentication errors return structured responses:

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "timestamp": "2024-01-01T12:00:00.000Z",
    "request_id": "unique-request-id",
    "path": "/api/v2/auth/endpoint"
  }
}
```

### Common Error Codes
- `AUTHENTICATION_ERROR` (401): Invalid credentials or token
- `AUTHORIZATION_ERROR` (403): Insufficient permissions
- `VALIDATION_ERROR` (400): Invalid request format
- `NOT_FOUND` (404): Resource not found
- `RATE_LIMIT_EXCEEDED` (429): Too many requests

## Rate Limiting

Authentication endpoints are rate-limited to prevent abuse:

- **Login endpoints**: 5 attempts per minute per IP
- **Token refresh**: 10 requests per minute per user
- **OAuth2 flows**: 3 attempts per minute per IP

Rate limit headers are included in responses:
```
X-RateLimit-Limit: 5
X-RateLimit-Remaining: 4
X-RateLimit-Reset: 1640995260
```