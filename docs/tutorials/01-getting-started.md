# Tutorial 1: Getting Started with OSTicket API v2

Welcome to the OSTicket API v2! This tutorial will guide you through your first steps with the API, from setup to making your first authenticated request.

## What You'll Learn

By the end of this tutorial, you'll be able to:
- ✅ Set up the OSTicket API v2 development environment
- ✅ Understand the API authentication flow
- ✅ Make your first API request
- ✅ Authenticate as both a staff member and end user
- ✅ Access user information through the API

## What You'll Need

- 30 minutes of your time
- Basic command line knowledge
- Python 3.8+ installed
- MySQL/MariaDB database access

## Overview of OSTicket API v2

The OSTicket API v2 is a modern REST API built with FastAPI that provides comprehensive access to OSTicket functionality. Unlike the original OSTicket API which only supported ticket creation, API v2 offers:

- **Full CRUD operations** for tickets, users, and staff
- **Modern authentication** with JWT tokens and OAuth2
- **Interactive documentation** with Swagger UI
- **Structured error responses** for better debugging
- **Real-time compatibility** with existing OSTicket installations

## Step 1: Quick Setup

### Install Prerequisites

First, make sure you have the required software:

```bash
# Check Python version (should be 3.8+)
python3 --version

# Check if MySQL is available
mysql --version

# Install git if not already installed
git --version
```

### Clone and Setup

```bash
# Clone the repository
git clone https://github.com/your-org/ost-api.git
cd ost-api

# Create and activate Python virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Quick Database Setup

For this tutorial, we'll assume you have an existing OSTicket installation. If not, see the [full setup guide](../how-to/setup-development.md).

```bash
# Test your database connection
mysql -u your_username -p your_osticket_database -e "SHOW TABLES LIKE 'ost_ticket';"

# Should show: ost_ticket table
```

## Step 2: Configure the API

Create your configuration file:

```bash
# Copy configuration template
cp api/v2/core/config.py.example api/v2/core/config.py

# Edit with your database details
nano api/v2/core/config.py
```

Update these key settings:

```python
# Replace with your actual database details
DATABASE_URL = "mysql+pymysql://username:password@localhost/osticket_db"

# Generate a secure secret key for JWT tokens
JWT_SECRET_KEY = "your-secret-key-here-make-it-long-and-random"

# OSTicket table prefix (usually 'ost_')
OST_TABLE_PREFIX = "ost_"
```

💡 **Tip**: You can generate a secure secret key with:
```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

## Step 3: Start the API Server

```bash
# Start the development server
uvicorn api.v2.main:app --host 0.0.0.0 --port 3969 --reload

# You should see output like:
# INFO:     Uvicorn running on http://0.0.0.0:3969 (Press CTRL+C to quit)
# INFO:     Started reloader process [28720]
# INFO:     Started server process [28722]
# INFO:     Waiting for application startup.
```

🎉 **Success!** Your API server is now running.

## Step 4: Explore the Interactive Documentation

Open your web browser and visit: **http://localhost:3969/api/v2/docs**

You'll see the Swagger UI with all available API endpoints. This is an interactive documentation where you can:
- See all available endpoints
- Understand request/response formats
- Test endpoints directly in the browser
- View authentication requirements

### Try the Health Check

1. Find the **Health** section in the documentation
2. Click on **GET /health**
3. Click **"Try it out"**
4. Click **"Execute"**

You should see a successful response:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T12:00:00.000Z",
  "version": "2.0.0",
  "database": "connected"
}
```

## Step 5: Your First API Request

Let's make our first API request using the command line:

```bash
# Test the health endpoint
curl http://localhost:3969/api/v2/health

# You should get:
# {"status":"healthy","timestamp":"2024-01-01T12:00:00.000Z","version":"2.0.0","database":"connected"}
```

### Check Available Authentication Methods

```bash
# See what authentication providers are available
curl http://localhost:3969/api/v2/auth/providers | jq

# Response will show available authentication methods:
# {
#   "providers": {
#     "osticket": {
#       "name": "osticket",
#       "staff_login_url": "/api/v2/auth/staff/login",
#       "user_login_url": "/api/v2/auth/user/login"
#     }
#   },
#   "native_auth_enabled": true
# }
```

💡 **Note**: If you don't have `jq` installed, remove `| jq` from the commands - the output will just be less formatted.

## Step 6: Authenticate as Staff

Let's authenticate using an existing staff account from your OSTicket installation.

### Find Your Staff Credentials

You can use any existing staff account from your OSTicket installation, or check what accounts exist:

```bash
# List existing staff accounts
mysql -u your_username -p your_osticket_database -e "
SELECT staff_id, username, email, firstname, lastname, isadmin 
FROM ost_staff 
WHERE isactive = 1 
LIMIT 5;"
```

### Staff Login

Replace `admin` and `your_password` with actual credentials:

```bash
# Login as staff member
curl -X POST http://localhost:3969/api/v2/auth/staff/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "your_password"
  }' | jq

# Successful response includes JWT tokens:
# {
#   "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
#   "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
#   "token_type": "bearer",
#   "expires_in": 1800
# }
```

### Save the Access Token

Copy the `access_token` value from the response and save it:

```bash
# Save token to environment variable for easier use
ACCESS_TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

### Make Authenticated Request

Now use the token to access protected endpoints:

```bash
# Get current user information
curl -X GET http://localhost:3969/api/v2/auth/userinfo \
  -H "Authorization: Bearer $ACCESS_TOKEN" | jq

# Response shows your staff information:
# {
#   "user_type": "staff",
#   "user_id": 1,
#   "email": "admin@example.com",
#   "username": "admin",
#   "name": "Administrator",
#   "isadmin": true,
#   "dept_id": 1
# }
```

## Step 7: Understanding JWT Tokens

The access token you received is a JWT (JSON Web Token). You can decode it to see what information it contains:

```bash
# Decode JWT token (without verification) to see contents
python3 -c "
import base64
import json
token = '$ACCESS_TOKEN'
# Extract payload (middle part between dots)
payload = token.split('.')[1]
# Add padding if needed
payload += '=' * (4 - len(payload) % 4)
# Decode
decoded = base64.urlsafe_b64decode(payload)
print(json.dumps(json.loads(decoded), indent=2))
"
```

You'll see the token contains information like:
- User ID and type (staff)
- Username and email
- Department and admin status
- Token expiration time

## Step 8: Create and Authenticate End User

Let's create a test end user and authenticate with them too.

### Create Test User

```bash
# Create a test user in the database
mysql -u your_username -p your_osticket_database << 'EOF'
-- Create user record
INSERT INTO ost_user (org_id, default_email_id, status, name, created, updated) 
VALUES (1, 0, 0, 'Tutorial User', NOW(), NOW());

SET @user_id = LAST_INSERT_ID();

-- Create email address
INSERT INTO ost_user_email (user_id, flags, address) 
VALUES (@user_id, 0, 'tutorial@example.com');

SET @email_id = LAST_INSERT_ID();

-- Update user with email ID
UPDATE ost_user SET default_email_id = @email_id WHERE id = @user_id;

-- Create user account with password "tutorial123"
INSERT INTO ost_user_account (user_id, status, username, passwd, registered)
VALUES (@user_id, 1, 'tutorial', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj0kMJYJp1Ka', NOW());

SELECT 'Tutorial user created successfully!' as result;
EOF
```

### User Login

```bash
# Login as end user
curl -X POST http://localhost:3969/api/v2/auth/user/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "tutorial@example.com",
    "password": "tutorial123"
  }' | jq

# Save the user access token
USER_TOKEN="paste-user-access-token-here"
```

### Test User Authentication

```bash
# Get user information
curl -X GET http://localhost:3969/api/v2/auth/userinfo \
  -H "Authorization: Bearer $USER_TOKEN" | jq

# Response shows user information (different from staff):
# {
#   "user_type": "user",
#   "user_id": 2,
#   "email": null,
#   "username": null,
#   "name": "Tutorial User",
#   "isadmin": null,
#   "dept_id": null
# }
```

## Step 9: Test Error Handling

Let's see what happens when authentication fails:

```bash
# Try login with wrong password
curl -X POST http://localhost:3969/api/v2/auth/user/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "tutorial@example.com",
    "password": "wrong_password"
  }' | jq

# You'll get a structured error response:
# {
#   "error": {
#     "code": "AUTHENTICATION_ERROR",
#     "message": "Invalid email or password",
#     "timestamp": "2024-01-01T12:00:00.000Z",
#     "request_id": "550e8400-e29b-41d4-a716-446655440000",
#     "path": "/api/v2/auth/user/login"
#   }
# }
```

### Test Missing Authorization

```bash
# Try accessing protected endpoint without token
curl -X GET http://localhost:3969/api/v2/auth/userinfo | jq

# You'll get an authentication error:
# {
#   "error": {
#     "code": "AUTHENTICATION_ERROR",
#     "message": "Authentication required",
#     "timestamp": "2024-01-01T12:00:00.000Z",
#     "request_id": "550e8400-e29b-41d4-a716-446655440000",
#     "path": "/api/v2/auth/userinfo"
#   }
# }
```

## Step 10: Logout

When you're done, you can logout to invalidate your tokens:

```bash
# Logout (invalidates token)
curl -X POST http://localhost:3969/api/v2/auth/logout \
  -H "Authorization: Bearer $ACCESS_TOKEN" | jq

# Response confirms logout:
# {
#   "message": "Logged out successfully"
# }
```

## What You've Accomplished! 🎉

Congratulations! You've successfully:

✅ **Set up** the OSTicket API v2 development environment  
✅ **Started** the API server and accessed interactive documentation  
✅ **Made** your first API requests using curl  
✅ **Authenticated** as both staff and end user  
✅ **Received** JWT tokens and used them for authenticated requests  
✅ **Explored** error handling and structured error responses  
✅ **Tested** logout functionality

## Key Concepts You've Learned

### 🔐 Authentication Flow
1. **Login** with credentials (username/password or email/password)
2. **Receive** JWT access and refresh tokens
3. **Include** access token in Authorization header
4. **Access** protected endpoints
5. **Logout** to invalidate tokens

### 🎯 API Patterns
- **RESTful endpoints** with standard HTTP methods
- **Structured JSON** requests and responses
- **Bearer token authentication** for protected endpoints
- **Consistent error format** with error codes and request IDs

### 🛠️ Development Tools
- **Interactive docs** at `/api/v2/docs` for testing
- **Command line tools** (curl) for API testing
- **JWT tokens** for stateless authentication
- **Structured errors** for debugging

## Next Steps

Now that you've got the basics down, here's what to explore next:

### 🚀 [Tutorial 2: Your First API Request](02-first-api-request.md)
Learn about different types of API requests and response formats.

### 🔑 [Tutorial 3: Authentication Basics](03-authentication-basics.md)
Dive deeper into authentication methods, token refresh, and security.

### 🎫 [Tutorial 4: Creating Tickets](04-creating-tickets.md)
Learn how to create and manage tickets through the API.

### 📚 Additional Resources
- **[How-to Guides](../how-to/)** - Task-oriented guides for specific scenarios
- **[API Reference](../reference/api/)** - Complete endpoint documentation
- **[Model Reference](../reference/models/)** - Database model documentation

## Troubleshooting

### Server Won't Start
- Check Python version: `python3 --version`
- Verify virtual environment: `which python`
- Check database connection in config.py

### Authentication Fails
- Verify credentials exist in OSTicket database
- Check table prefix in config.py matches database
- Ensure user account is active

### Can't Connect to Database
- Test manual connection: `mysql -u username -p database`
- Verify DATABASE_URL in config.py
- Check MySQL service is running

### Need Help?
- Check the [setup guide](../how-to/setup-development.md) for detailed instructions
- Review [error responses](../reference/api/errors.md) for debugging
- Look at server logs for detailed error information

---

**Great job completing your first tutorial!** You now have a solid foundation for working with the OSTicket API v2. The next tutorials will build on these concepts to show you more advanced features and real-world usage patterns.