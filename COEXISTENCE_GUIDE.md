# FastAPI and OSTicket Coexistence Guide

## Yes, They Can Coexist Perfectly! ✅

The FastAPI server and existing OSTicket installation can run simultaneously without any conflicts. Here's how:

## Architecture Overview

```
                     ┌─────────────────────────────────────┐
                     │         MySQL Database              │
                     │         (osticket DB)               │
                     │  ┌────────────────────────────┐     │
                     │  │ Tables: ost_ticket,        │     │
                     │  │ ost_user, ost_staff, etc.  │     │
                     │  └────────────────────────────┘     │
                     └─────────────┬───────────┬──────────┘
                                   │           │
                        Read/Write │           │ Read/Write
                                   │           │
                    ┌──────────────▼───┐   ┌───▼──────────────┐
                    │  OSTicket PHP    │   │  FastAPI Server  │
                    │  (Port 80/443)   │   │   (Port 8000)    │
                    │                  │   │                  │
                    │ /scp/            │   │ /api/v2/         │
                    │ /tickets.php     │   │ /api/docs        │
                    │ /kb/             │   │ /health          │
                    └──────────────────┘   └──────────────────┘
                              │                     │
                              │                     │
                    ┌─────────▼─────────┐  ┌───────▼─────────┐
                    │  Existing Web UI  │  │  New Frontend   │
                    │  (Staff/Client)   │  │  (React/Vue)    │
                    └───────────────────┘  └─────────────────┘
```

## How They Work Together

### 1. **Shared Database - No Conflicts**

Both systems read and write to the same MySQL database, but they're designed to be compatible:

```python
# FastAPI writes to OSTicket tables maintaining data integrity
async def create_ticket(db: Session, ticket_data):
    # Creates ticket following OSTicket's exact schema
    new_ticket = Ticket(
        number=generate_osticket_format_number(),  # Format: 123456
        status_id=1,  # Uses OSTicket's status IDs
        created=datetime.now(),
        updated=datetime.now(),
        # All required fields that OSTicket expects
    )
    
    # Also creates required related records
    ticket_cdata = TicketCData(...)  # Custom data table
    thread = Thread(...)  # Thread table entry
    
    # Result: OSTicket PHP can read this ticket perfectly
```

### 2. **Different Ports - No Network Conflicts**

```nginx
# Nginx configuration example
server {
    listen 80;
    server_name tickets.example.com;
    
    # OSTicket PHP application
    location / {
        proxy_pass http://localhost:80;
        # OR use PHP-FPM
        # fastcgi_pass unix:/var/run/php/php8.2-fpm.sock;
    }
    
    # FastAPI application on different port
    location /api/v2/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 3. **Session Independence**

- **OSTicket**: Uses PHP sessions (stored in database or files)
- **FastAPI**: Uses JWT tokens (stateless)
- No session conflicts between the two systems

## Deployment Scenarios

### Scenario 1: Same Server Deployment

```bash
# OSTicket running on Apache/Nginx with PHP-FPM
/var/www/osticket/          # Port 80/443
├── index.php
├── scp/
└── api/

# FastAPI running as separate service
/opt/osticket-api/          # Port 8000
├── app/
├── venv/
└── run.sh

# Both connect to same MySQL
MySQL Server                # Port 3306
└── osticket database
```

**Systemd Service Example:**
```ini
# /etc/systemd/system/osticket-api.service
[Unit]
Description=OSTicket FastAPI Server
After=network.target mysql.service

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/osticket-api
Environment="PATH=/opt/osticket-api/venv/bin"
ExecStart=/opt/osticket-api/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

### Scenario 2: Separate Servers

```yaml
# docker-compose.yml for FastAPI
version: '3.8'
services:
  fastapi:
    build: .
    ports:
      - "8000:8000"
    environment:
      DB_HOST: osticket-server.example.com  # Remote OSTicket MySQL
      DB_PORT: 3306
      DB_NAME: osticket
    extra_hosts:
      - "osticket-server.example.com:192.168.1.100"
```

### Scenario 3: Kubernetes Deployment

```yaml
# FastAPI can be in Kubernetes while OSTicket stays traditional
apiVersion: apps/v1
kind: Deployment
metadata:
  name: osticket-api
spec:
  replicas: 3
  template:
    spec:
      containers:
      - name: fastapi
        image: osticket-api:latest
        env:
        - name: DB_HOST
          value: "osticket-mysql.example.com"
```

## Database Compatibility Rules

### 1. **Maintain OSTicket's Data Integrity**

```python
# FastAPI respects all OSTicket's database rules
class TicketService:
    def create_ticket(self, db: Session, data):
        # MUST create entries in these tables for OSTicket compatibility:
        # 1. ost_ticket - Main ticket record
        # 2. ost_ticket__cdata - Custom data
        # 3. ost_thread - Thread record
        # 4. ost_thread_entry - Initial message
        
        # MUST maintain:
        # - Ticket number format (6 digits)
        # - Status IDs matching ost_ticket_status
        # - Department IDs matching ost_department
        # - Timestamps in OSTicket's expected format
```

### 2. **Read Without Breaking**

```python
# FastAPI can safely read all OSTicket data
@app.get("/api/v2/tickets/{ticket_id}")
async def get_ticket(ticket_id: int, db: Session):
    # Direct query to OSTicket tables
    ticket = db.query(Ticket).filter(
        Ticket.ticket_id == ticket_id
    ).first()
    
    # Can join with all related tables
    thread = db.query(Thread).filter(
        Thread.object_id == ticket_id,
        Thread.object_type == 'T'
    ).first()
    
    return format_response(ticket, thread)
```

### 3. **Safe Concurrent Access**

```python
# Use transactions to prevent conflicts
async def update_ticket_status(ticket_id: int, new_status: int):
    with db.begin():  # Transaction
        ticket = db.query(Ticket).with_for_update().filter(
            Ticket.ticket_id == ticket_id
        ).first()  # Row-level lock
        
        ticket.status_id = new_status
        ticket.updated = datetime.now()
        
        # Log the change for OSTicket's audit trail
        create_audit_entry(ticket_id, "status_changed")
```

## Gradual Migration Strategy

### Phase 1: Read-Only API (Week 1-2)
- FastAPI reads from OSTicket database
- No writes, zero risk
- Test API endpoints

### Phase 2: Parallel Operations (Week 3-4)
- FastAPI handles new API requests
- OSTicket continues normal operations
- Both write to same database

### Phase 3: Feature Migration (Week 5-8)
- New features built in FastAPI only
- Existing features remain in OSTicket
- Gradual frontend migration

### Phase 4: Optional Full Migration (Future)
- Move more features to FastAPI
- OSTicket becomes view-only
- Eventually sunset OSTicket

## Common Concerns Addressed

### Q: Will FastAPI break existing tickets?
**A: No!** FastAPI reads and writes using OSTicket's exact schema. Existing tickets remain fully accessible in OSTicket.

### Q: Can staff still use the OSTicket admin panel?
**A: Yes!** The OSTicket admin panel (`/scp/`) continues working normally. Staff can use both interfaces.

### Q: What about email piping and cron jobs?
**A: They continue working!** OSTicket's email piping and cron jobs remain functional:
```bash
# OSTicket cron continues running
*/5 * * * * php /var/www/osticket/api/cron.php

# FastAPI can have its own cron for new features
*/5 * * * * python /opt/osticket-api/cron.py
```

### Q: Database migrations?
**A: Careful coordination needed:**
```python
# FastAPI's Alembic migrations should be read-only for OSTicket tables
def upgrade():
    # DON'T modify existing OSTicket tables
    # DO create new tables if needed
    op.create_table(
        'api_cache',  # New table, won't affect OSTicket
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('key', sa.String(255)),
        sa.Column('value', sa.Text)
    )
    
    # If you MUST modify OSTicket tables, coordinate with OSTicket updates
```

### Q: What about file attachments?
**A: Shared file storage:**
```python
# FastAPI uses same attachment directory
ATTACHMENT_DIR = "/var/www/osticket/attachments"

async def save_attachment(file: UploadFile):
    # Save using OSTicket's file naming convention
    file_hash = generate_osticket_hash(file)
    file_path = f"{ATTACHMENT_DIR}/{file_hash[0]}/{file_hash}"
    
    # Also create database entry in ost_file
    db_file = File(
        name=file.filename,
        type=file.content_type,
        hash=file_hash,
        size=file.size
    )
```

## Testing Coexistence

### 1. **Verification Checklist**
```bash
#!/bin/bash
# verify_coexistence.sh

echo "1. Checking OSTicket is accessible..."
curl -s http://localhost/scp/login.php | grep -q "osTicket" && echo "✓ OSTicket running"

echo "2. Checking FastAPI is accessible..."
curl -s http://localhost:8000/health | grep -q "healthy" && echo "✓ FastAPI running"

echo "3. Creating ticket via FastAPI..."
TICKET_ID=$(curl -s -X POST http://localhost:8000/api/v2/tickets \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"subject":"Test","message":"Test"}' | jq -r '.ticket_id')

echo "4. Verifying ticket in OSTicket..."
mysql -u osticket -p osticket -e "SELECT number FROM ost_ticket WHERE ticket_id=$TICKET_ID"

echo "5. Checking ticket visible in OSTicket UI..."
curl -s "http://localhost/scp/tickets.php?id=$TICKET_ID" | grep -q "Test" && echo "✓ Ticket visible"
```

### 2. **Monitoring Both Systems**
```python
# monitoring.py
import httpx
import asyncio
from datetime import datetime

async def check_health():
    async with httpx.AsyncClient() as client:
        # Check OSTicket
        try:
            r1 = await client.get("http://localhost/api/http.php/tickets.json")
            osticket_status = "UP" if r1.status_code == 401 else "DOWN"  # 401 = needs auth = working
        except:
            osticket_status = "DOWN"
        
        # Check FastAPI
        try:
            r2 = await client.get("http://localhost:8000/health")
            fastapi_status = "UP" if r2.status_code == 200 else "DOWN"
        except:
            fastapi_status = "DOWN"
        
        print(f"{datetime.now()} - OSTicket: {osticket_status}, FastAPI: {fastapi_status}")

# Run every minute
while True:
    asyncio.run(check_health())
    time.sleep(60)
```

## Performance Considerations

### Database Connection Pooling
```python
# FastAPI connection pool configuration
engine = create_engine(
    DATABASE_URL,
    pool_size=20,        # Don't overwhelm MySQL
    max_overflow=40,     # Allow burst traffic
    pool_pre_ping=True,  # Verify connections
    pool_recycle=3600    # Recycle after 1 hour
)

# OSTicket also has its own connection pool
# Monitor total connections:
# MySQL: SHOW VARIABLES LIKE 'max_connections';
# Current: SHOW STATUS WHERE variable_name = 'Threads_connected';
```

### Caching Strategy
```python
# FastAPI can cache to reduce database load
from redis import Redis
redis = Redis(host='localhost', port=6379)

@app.get("/api/v2/tickets/{ticket_id}")
async def get_ticket(ticket_id: int):
    # Check cache first
    cached = redis.get(f"ticket:{ticket_id}")
    if cached:
        return json.loads(cached)
    
    # Fall back to database
    ticket = fetch_from_db(ticket_id)
    
    # Cache for 5 minutes
    redis.setex(f"ticket:{ticket_id}", 300, json.dumps(ticket))
    return ticket
```

## Security Considerations

### 1. **API Key Compatibility**
```python
# FastAPI can validate OSTicket API keys
async def validate_osticket_api_key(api_key: str, request: Request):
    db = get_db()
    key = db.query(ApiKey).filter(
        ApiKey.apikey == api_key,
        ApiKey.isactive == 1
    ).first()
    
    if key and key.ipaddr:
        # Check IP restriction like OSTicket does
        if not check_ip_match(request.client.host, key.ipaddr):
            raise HTTPException(403, "IP not allowed")
    
    return key
```

### 2. **Shared Authentication**
```python
# FastAPI can verify OSTicket sessions
async def verify_osticket_session(session_id: str):
    db = get_db()
    session = db.query(Session).filter(
        Session.session_id == session_id,
        Session.session_expire > datetime.now()
    ).first()
    
    if session:
        return get_user_from_session(session)
    return None
```

## Rollback Plan

If something goes wrong, you can easily rollback:

```bash
#!/bin/bash
# rollback.sh

# 1. Stop FastAPI
systemctl stop osticket-api

# 2. Verify OSTicket still works
curl http://localhost/scp/login.php

# 3. Check database integrity
mysql -u osticket -p osticket -e "
    SELECT COUNT(*) as ticket_count FROM ost_ticket;
    SELECT COUNT(*) as user_count FROM ost_user;
"

# 4. OSTicket continues working independently!
echo "✓ OSTicket is independent and unaffected"
```

## Conclusion

**Yes, FastAPI and OSTicket can coexist perfectly!**

- ✅ Same database, no conflicts
- ✅ Different ports, no network issues  
- ✅ Independent sessions, no auth conflicts
- ✅ Gradual migration possible
- ✅ Easy rollback if needed
- ✅ Both systems remain fully functional

The key is that FastAPI respects OSTicket's database schema and conventions while providing a modern API layer on top.