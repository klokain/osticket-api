# How to Set Up Development Environment

Complete guide for setting up a development environment for the OSTicket API v2.

## Prerequisites

### System Requirements
- **Python**: 3.8+ (recommended: 3.11)
- **Database**: MySQL 5.7+ or MariaDB 10.3+
- **OS**: Linux, macOS, or Windows with WSL
- **Memory**: 4GB RAM minimum, 8GB recommended
- **Disk**: 2GB free space

### Required Tools
- `git` - Version control
- `python3` and `pip` - Python runtime and package manager
- `mysql-client` or equivalent - Database client
- `curl` - API testing (optional but recommended)

### Optional Tools
- **IDE**: VSCode, PyCharm, or similar
- **API Client**: Postman, Insomnia, or Thunder Client
- **Database GUI**: phpMyAdmin, MySQL Workbench, or DBeaver

## Step 1: Clone Repository

```bash
# Clone the repository
git clone https://github.com/your-org/ost-api.git
cd ost-api

# Check current branch
git branch
```

## Step 2: Set Up Python Environment

### Create Virtual Environment
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On Linux/macOS:
source venv/bin/activate

# On Windows:
# venv\Scripts\activate

# Verify activation (should show venv path)
which python
```

### Install Dependencies
```bash
# Upgrade pip
pip install --upgrade pip

# Install project dependencies
pip install -r requirements.txt

# Verify installation
pip list | grep fastapi
pip list | grep sqlalchemy
```

## Step 3: Set Up Database

### Option A: Use Existing OSTicket Installation

If you have an existing OSTicket installation:

```bash
# Note your database connection details
# - Host: usually localhost
# - Database name: usually osticket
# - Username: your MySQL username  
# - Password: your MySQL password
```

### Option B: Set Up New OSTicket Database

#### 1. Install OSTicket
```bash
# Download OSTicket submodule (if not already present)
git submodule update --init --recursive

# Set up web server for OSTicket installation
# For development, use PHP built-in server
cd osTicket
php -S localhost:8080
```

#### 2. Complete OSTicket Web Installation
1. Visit `http://localhost:8080/setup/install.php`
2. Follow installation wizard
3. Create database and admin user
4. Note the database credentials for API configuration

#### 3. Create Database User for API
```bash
# Connect to MySQL as root
sudo mysql

# Create API user with appropriate permissions
CREATE USER 'osticket_api'@'localhost' IDENTIFIED BY 'secure_password';
GRANT SELECT, INSERT, UPDATE, DELETE ON osticket.* TO 'osticket_api'@'localhost';
FLUSH PRIVILEGES;
EXIT;

# Test connection
mysql -u osticket_api -p osticket
```

### Verify Database Schema
```bash
# Count tables (should be around 70+ tables)
mysql -u osticket_api -p osticket -e "SHOW TABLES LIKE 'ost_%';" | wc -l

# Check key tables exist
mysql -u osticket_api -p osticket -e "
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'osticket' 
AND table_name IN ('ost_ticket', 'ost_user', 'ost_staff', 'ost_department');"
```

## Step 4: Configure API

### Create Configuration File
```bash
# Create configuration from template
cp api/v2/core/config.py.example api/v2/core/config.py

# Edit configuration
nano api/v2/core/config.py
```

### Configuration Settings
Update the configuration with your database details:

```python
# Database Configuration
DATABASE_URL = "mysql+pymysql://osticket_api:secure_password@localhost/osticket"

# JWT Configuration  
JWT_SECRET_KEY = "your-super-secret-jwt-key-change-in-production"
JWT_ALGORITHM = "HS256"
JWT_ACCESS_TOKEN_EXPIRE_MINUTES = 30
JWT_REFRESH_TOKEN_EXPIRE_DAYS = 7

# OSTicket Configuration
OST_TABLE_PREFIX = "ost_"  # Match your OSTicket installation
OST_URL = "http://localhost:8080"  # Your OSTicket URL

# API Configuration
ALLOWED_HOSTS = ["localhost", "127.0.0.1", "0.0.0.0"]
API_V2_PREFIX = "/api/v2"

# Development Settings
DEBUG = True
TESTING = False
```

### Environment Variables (Optional)
Alternatively, use environment variables:

```bash
# Create .env file
cat > .env << EOF
DATABASE_URL=mysql+pymysql://osticket_api:secure_password@localhost/osticket
JWT_SECRET_KEY=your-super-secret-jwt-key
DEBUG=True
EOF

# Load environment variables
source .env
```

## Step 5: Test Database Connection

```bash
# Test database connectivity
python3 -c "
from api.v2.core.database import engine
from sqlalchemy import text

try:
    with engine.connect() as conn:
        result = conn.execute(text('SELECT COUNT(*) as table_count FROM information_schema.tables WHERE table_schema = DATABASE() AND table_name LIKE \"ost_%\"'))
        count = result.fetchone()[0]
        print(f'✅ Database connection successful! Found {count} OSTicket tables.')
except Exception as e:
    print(f'❌ Database connection failed: {e}')
"
```

## Step 6: Run the API Server

### Start Development Server
```bash
# Start FastAPI development server
uvicorn api.v2.main:app --host 0.0.0.0 --port 3969 --reload

# Server should start with output similar to:
# INFO:     Uvicorn running on http://0.0.0.0:3969 (Press CTRL+C to quit)
# INFO:     Started reloader process
# INFO:     Started server process
# INFO:     Waiting for application startup.
```

### Verify API is Running
```bash
# Test health endpoint
curl http://localhost:3969/api/v2/health

# Expected response:
# {
#   "status": "healthy",
#   "timestamp": "2024-01-01T12:00:00.000Z",
#   "version": "2.0.0",
#   "database": "connected"
# }
```

## Step 7: Test Authentication

### Create Test User
```bash
# Connect to database
mysql -u osticket_api -p osticket

# Create test user
INSERT INTO ost_user (org_id, default_email_id, status, name, created, updated) 
VALUES (1, 0, 0, 'Test User', NOW(), NOW());

SET @user_id = LAST_INSERT_ID();

INSERT INTO ost_user_email (user_id, flags, address) 
VALUES (@user_id, 0, 'test@example.com');

SET @email_id = LAST_INSERT_ID();

UPDATE ost_user SET default_email_id = @email_id WHERE id = @user_id;

# Create user account with password "testpass123"
INSERT INTO ost_user_account (user_id, status, username, passwd, registered)
VALUES (@user_id, 1, 'testuser', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj0kMJYJp1Ka', NOW());

EXIT;
```

### Test Authentication
```bash
# Test user login
curl -X POST http://localhost:3969/api/v2/auth/user/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "testpass123"
  }'

# Should return JWT tokens
```

### Test Authenticated Endpoint
```bash
# Extract access token from login response and test userinfo
ACCESS_TOKEN="your-access-token-here"

curl -X GET http://localhost:3969/api/v2/auth/userinfo \
  -H "Authorization: Bearer $ACCESS_TOKEN"

# Should return user information
```

## Step 8: Access Documentation

### Interactive API Documentation
Visit the automatically generated API documentation:

- **Swagger UI**: http://localhost:3969/api/v2/docs
- **ReDoc**: http://localhost:3969/api/v2/redoc
- **OpenAPI Schema**: http://localhost:3969/api/v2/openapi.json

### Test Endpoints
Use the Swagger UI to test API endpoints:
1. Visit http://localhost:3969/api/v2/docs
2. Try the authentication endpoints
3. Use "Authorize" button to set Bearer token
4. Test authenticated endpoints

## Step 9: Development Workflow

### Code Changes
The server runs with `--reload` flag, so it automatically restarts when you make changes:

```bash
# Make changes to Python files
# Server will automatically reload
# Check terminal for any error messages
```

### Database Changes
If you modify model definitions:

```bash
# Test model changes
python3 -c "
from api.v2.models.ticket import Ticket
from api.v2.core.database import engine

# Test that models can be imported and used
print('✅ Models imported successfully')

# Test database queries
try:
    from api.v2.core.database import SessionLocal
    db = SessionLocal()
    count = db.query(Ticket).count()
    print(f'✅ Found {count} tickets in database')
    db.close()
except Exception as e:
    print(f'❌ Database query failed: {e}')
"
```

### Running Tests
```bash
# Run API tests
python -m pytest test_api.py -v

# Run model tests  
python -m pytest test_models.py -v

# Run with coverage
pip install pytest-cov
python -m pytest --cov=api/v2 --cov-report=html
```

## Troubleshooting

### Common Issues

#### Database Connection Fails
```
sqlalchemy.exc.OperationalError: (pymysql.err.OperationalError) (2003, "Can't connect to MySQL server...")
```

**Solutions:**
1. Check MySQL is running: `sudo systemctl status mysql`
2. Verify credentials in config.py
3. Test manual connection: `mysql -u osticket_api -p`
4. Check firewall settings
5. Verify database exists: `SHOW DATABASES;`

#### Module Import Errors
```
ModuleNotFoundError: No module named 'fastapi'
```

**Solutions:**
1. Activate virtual environment: `source venv/bin/activate`
2. Install dependencies: `pip install -r requirements.txt`
3. Check Python path: `which python`

#### Port Already in Use
```
OSError: [Errno 98] Address already in use
```

**Solutions:**
1. Find process using port: `lsof -i :3969`
2. Kill process: `kill -9 PID`
3. Use different port: `uvicorn api.v2.main:app --port 8000`

#### OSTicket Table Prefix Issues
```
sqlalchemy.exc.ProgrammingError: (pymysql.err.ProgrammingError) (1146, "Table 'osticket.ost_ticket' doesn't exist")
```

**Solutions:**
1. Check actual table prefix: `SHOW TABLES LIKE '%ticket%';`
2. Update `OST_TABLE_PREFIX` in config.py
3. Verify table names match OSTicket installation

### Development Tips

#### Use Environment-Specific Configuration
```python
# config.py
import os

if os.getenv('ENVIRONMENT') == 'development':
    DEBUG = True
    DATABASE_URL = "mysql+pymysql://dev_user:dev_pass@localhost/osticket_dev"
elif os.getenv('ENVIRONMENT') == 'testing':
    DATABASE_URL = "sqlite:///test.db"
else:
    DEBUG = False
```

#### Enable SQL Query Logging
```python
# Add to config.py for debugging
SQLALCHEMY_ECHO = True  # Logs all SQL queries
```

#### Use Database Transactions
```python
# Example of safe database operations
from api.v2.core.database import SessionLocal

db = SessionLocal()
try:
    # Your database operations
    ticket = Ticket(subject="Test")
    db.add(ticket)
    db.commit()
except Exception as e:
    db.rollback()
    raise e
finally:
    db.close()
```

## Next Steps

1. **Explore the API**: Use the interactive documentation at `/docs`
2. **Read the models**: Check [Database Models](../reference/models/index.md)
3. **Add endpoints**: Follow [How to Add API Endpoints](add-api-endpoints.md)
4. **Set up OAuth2**: Configure [OAuth2 providers](implement-oauth2.md)
5. **Deploy**: Prepare for [Production Deployment](deploy-production.md)

## Getting Help

- **Documentation**: Check other how-to guides and references
- **Logs**: Check server logs for detailed error information
- **Database**: Use MySQL client to inspect data
- **Community**: OSTicket forums and documentation
- **Issues**: Create issues in the project repository

---

*Development environment setup complete! Your API server should now be running and ready for development.*