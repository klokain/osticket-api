# Error Response Reference

The OSTicket API v2 uses structured error responses to provide consistent, machine-readable error information.

## Error Response Format

All API errors return a JSON response with the following structure:

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error description",
    "timestamp": "2024-01-01T12:00:00.000Z",
    "request_id": "550e8400-e29b-41d4-a716-446655440000",
    "path": "/api/v2/endpoint/path",
    "details": {
      "additional": "context-specific information"
    }
  }
}
```

### Fields

- **`code`** (string): Machine-readable error code
- **`message`** (string): Human-readable error description
- **`timestamp`** (string): ISO 8601 timestamp when error occurred
- **`request_id`** (string): Unique identifier for tracing the request
- **`path`** (string): API endpoint path where error occurred
- **`details`** (object, optional): Additional context-specific information

## HTTP Status Codes

The API uses standard HTTP status codes:

| Status Code | Meaning | Usage |
|-------------|---------|-------|
| 200 | OK | Request successful |
| 201 | Created | Resource created successfully |
| 400 | Bad Request | Invalid request format or parameters |
| 401 | Unauthorized | Authentication required or failed |
| 403 | Forbidden | Insufficient permissions |
| 404 | Not Found | Resource not found |
| 409 | Conflict | Resource conflict (e.g., duplicate) |
| 422 | Unprocessable Entity | Validation failed |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Server error |

## Error Codes

### Authentication Errors (401)

#### AUTHENTICATION_ERROR
Authentication failed or required.

**Example:**
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

**Common Causes:**
- Invalid credentials
- Expired JWT token
- Invalid JWT signature
- Missing Authorization header
- Invalid API key

### Authorization Errors (403)

#### AUTHORIZATION_ERROR
Insufficient permissions for the requested operation.

**Example:**
```json
{
  "error": {
    "code": "AUTHORIZATION_ERROR",
    "message": "Admin access required",
    "timestamp": "2024-01-01T12:00:00.000Z",
    "request_id": "550e8400-e29b-41d4-a716-446655440000",
    "path": "/api/v2/admin/users"
  }
}
```

**Common Causes:**
- Non-admin user accessing admin endpoint
- User accessing staff-only resource
- API key lacking required permissions
- IP address not allowed for API key

### Validation Errors (400/422)

#### VALIDATION_ERROR
Request validation failed.

**Example:**
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Request validation failed",
    "timestamp": "2024-01-01T12:00:00.000Z",
    "request_id": "550e8400-e29b-41d4-a716-446655440000",
    "path": "/api/v2/auth/staff/login",
    "details": {
      "validation_errors": [
        {
          "field": "username",
          "message": "field required",
          "type": "missing",
          "input": null
        },
        {
          "field": "password",
          "message": "ensure this value has at least 8 characters",
          "type": "value_error.any_str.min_length",
          "input": "short"
        }
      ]
    }
  }
}
```

**Common Causes:**
- Missing required fields
- Invalid field formats
- Field length violations
- Invalid email addresses
- Malformed JSON

### Not Found Errors (404)

#### NOT_FOUND
Requested resource not found.

**Example:**
```json
{
  "error": {
    "code": "NOT_FOUND",
    "message": "Ticket not found: 12345",
    "timestamp": "2024-01-01T12:00:00.000Z",
    "request_id": "550e8400-e29b-41d4-a716-446655440000",
    "path": "/api/v2/tickets/12345",
    "details": {
      "resource": "Ticket",
      "identifier": "12345"
    }
  }
}
```

**Common Causes:**
- Non-existent resource ID
- Resource deleted or archived
- Incorrect endpoint path
- Missing URL parameters

### Conflict Errors (409)

#### CONFLICT_ERROR
Resource conflict detected.

**Example:**
```json
{
  "error": {
    "code": "CONFLICT_ERROR",
    "message": "Email address already exists",
    "timestamp": "2024-01-01T12:00:00.000Z",
    "request_id": "550e8400-e29b-41d4-a716-446655440000",
    "path": "/api/v2/users",
    "details": {
      "field": "email",
      "value": "user@example.com"
    }
  }
}
```

**Common Causes:**
- Duplicate unique fields
- Resource in invalid state for operation
- Concurrent modification conflicts

### Rate Limiting Errors (429)

#### RATE_LIMIT_EXCEEDED
API rate limit exceeded.

**Example:**
```json
{
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Rate limit exceeded",
    "timestamp": "2024-01-01T12:00:00.000Z",
    "request_id": "550e8400-e29b-41d4-a716-446655440000",
    "path": "/api/v2/auth/staff/login",
    "details": {
      "limit": 5,
      "window": 60,
      "retry_after": 45
    }
  }
}
```

**Headers:**
```
X-RateLimit-Limit: 5
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 1640995260
Retry-After: 45
```

### Server Errors (500)

#### INTERNAL_SERVER_ERROR
Unexpected server error.

**Example:**
```json
{
  "error": {
    "code": "INTERNAL_SERVER_ERROR",
    "message": "Internal server error",
    "timestamp": "2024-01-01T12:00:00.000Z",
    "request_id": "550e8400-e29b-41d4-a716-446655440000",
    "path": "/api/v2/tickets"
  }
}
```

#### DATABASE_ERROR
Database operation failed.

**Example:**
```json
{
  "error": {
    "code": "DATABASE_ERROR",
    "message": "Database operation failed",
    "timestamp": "2024-01-01T12:00:00.000Z",
    "request_id": "550e8400-e29b-41d4-a716-446655440000",
    "path": "/api/v2/tickets"
  }
}
```

## OAuth2-Specific Errors

### OAuth2 Login Errors

#### Provider Not Found
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

#### OAuth2 Callback Errors
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "OAuth2 authentication failed: access_denied",
    "timestamp": "2024-01-01T12:00:00.000Z",
    "request_id": "550e8400-e29b-41d4-a716-446655440000",
    "path": "/api/v2/auth/oauth2/keycloak/callback"
  }
}
```

#### External Identity Not Mapped
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

## Error Handling Best Practices

### For Client Applications

1. **Always check HTTP status codes** before parsing response body
2. **Use error codes for programmatic handling** rather than error messages
3. **Log request_id for debugging** and support requests
4. **Implement exponential backoff** for rate limiting errors
5. **Handle network errors gracefully** (timeouts, connection failures)

### Example Error Handling

```javascript
async function apiRequest(url, options) {
  try {
    const response = await fetch(url, options);
    
    if (!response.ok) {
      const errorData = await response.json();
      const error = errorData.error;
      
      switch (error.code) {
        case 'AUTHENTICATION_ERROR':
          // Redirect to login
          window.location.href = '/login';
          break;
        case 'RATE_LIMIT_EXCEEDED':
          // Implement backoff
          const retryAfter = error.details.retry_after;
          await new Promise(resolve => setTimeout(resolve, retryAfter * 1000));
          return apiRequest(url, options); // Retry
        case 'VALIDATION_ERROR':
          // Show validation errors to user
          showValidationErrors(error.details.validation_errors);
          break;
        default:
          // Generic error handling
          console.error(`API Error ${error.code}: ${error.message}`);
          console.error(`Request ID: ${error.request_id}`);
      }
      
      throw new Error(error.message);
    }
    
    return await response.json();
  } catch (networkError) {
    // Handle network errors
    console.error('Network error:', networkError);
    throw new Error('Network error occurred');
  }
}
```

## Debugging Errors

### Request ID Tracing

Every error response includes a unique `request_id` that can be used for tracing:

1. **Log the request_id** in your application
2. **Include request_id in bug reports** or support requests
3. **Search server logs** using the request_id for detailed debugging information

### Common Debugging Steps

1. **Check HTTP status code** - determines error category
2. **Examine error code** - identifies specific error type  
3. **Review error message** - provides human-readable description
4. **Inspect details object** - contains context-specific information
5. **Trace request_id** - find detailed logs on server side

### Development vs Production

**Development:**
- Error messages include detailed information
- Stack traces may be included for 500 errors
- Additional debugging headers present

**Production:**
- Generic error messages for security
- No stack traces or sensitive information
- Request IDs for tracing without exposing internals

## Error Response Headers

Standard headers included with error responses:

```
HTTP/1.1 401 Unauthorized
Content-Type: application/json
X-Request-ID: 550e8400-e29b-41d4-a716-446655440000
X-Response-Time: 0.045s
X-RateLimit-Limit: 5
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 1640995260
```

Rate limiting headers (when applicable):
- `X-RateLimit-Limit`: Request limit per window
- `X-RateLimit-Remaining`: Remaining requests in current window
- `X-RateLimit-Reset`: Unix timestamp when window resets
- `Retry-After`: Seconds to wait before retrying