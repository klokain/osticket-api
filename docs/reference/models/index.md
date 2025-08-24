# Database Models Index

Complete reference for all 72 SQLAlchemy models in the OSTicket API v2. These models provide 1:1 mapping to the OSTicket database schema.

## Model Organization

Models are organized into logical groups by functionality:

### 🎫 [Ticket System Models](ticket-models.md)
Core ticketing functionality and workflow management.

| Model | Table | Description |
|-------|-------|-------------|
| `Ticket` | `ost_ticket` | Main ticket record |
| `TicketCData` | `ost_ticket__cdata` | Custom ticket data |
| `TicketStatus` | `ost_ticket_status` | Ticket status definitions |
| `TicketPriority` | `ost_ticket_priority` | Ticket priority levels |
| `Thread` | `ost_thread` | Ticket conversation threads |
| `ThreadEntry` | `ost_thread_entry` | Individual thread messages |
| `ThreadEntryEmail` | `ost_thread_entry_email` | Email-specific thread data |
| `ThreadEntryMerge` | `ost_thread_entry_merge` | Ticket merge records |
| `ThreadEvent` | `ost_thread_event` | Thread activity events |
| `ThreadReferral` | `ost_thread_referral` | Thread referral tracking |
| `ThreadCollaborator` | `ost_thread_collaborator` | Thread collaboration |
| `Note` | `ost_note` | Internal staff notes |

### 👥 [User System Models](user-models.md)
End user management and organization structure.

| Model | Table | Description |
|-------|-------|-------------|
| `User` | `ost_user` | End user accounts |
| `UserCData` | `ost_user__cdata` | Custom user data |
| `UserEmail` | `ost_user_email` | User email addresses |
| `UserAccount` | `ost_user_account` | User account credentials |
| `Organization` | `ost_organization` | Company/organization records |
| `OrganizationCData` | `ost_organization__cdata` | Custom organization data |

### 👨‍💼 [Staff System Models](staff-models.md)
Staff management, departments, teams, and roles.

| Model | Table | Description |
|-------|-------|-------------|
| `Staff` | `ost_staff` | Staff member accounts |
| `Department` | `ost_department` | Department structure |
| `Team` | `ost_team` | Team organization |
| `TeamMember` | `ost_team_member` | Team membership |
| `Role` | `ost_role` | Permission roles |

### ⚙️ [System & Core Models](system-models.md)
System configuration, sessions, and core functionality.

| Model | Table | Description |
|-------|-------|-------------|
| `Config` | `ost_config` | System configuration |
| `Session` | `ost_session` | User sessions |
| `Syslog` | `ost_syslog` | System activity logs |
| `Lock` | `ost_lock` | Resource locking |
| `ApiKey` | `ost_api_key` | API key management |
| `Sequence` | `ost_sequence` | Auto-increment sequences |
| `Translation` | `ost_translation` | Multi-language support |
| `Event` | `ost_event` | System events |

### 📧 Email System Models
Email processing, templates, and filtering.

| Model | Table | Description |
|-------|-------|-------------|
| `Email` | `ost_email` | Email accounts/boxes |
| `EmailTemplate` | `ost_email_template` | Email templates |
| `EmailTemplateGroup` | `ost_email_template_group` | Template grouping |
| `Filter` | `ost_filter` | Email filters |
| `FilterAction` | `ost_filter_action` | Filter actions |
| `FilterRule` | `ost_filter_rule` | Filter rules |
| `Banlist` | `ost_banlist` | Email banlist |

### 📋 Form System Models
Dynamic forms and custom fields.

| Model | Table | Description |
|-------|-------|-------------|
| `Form` | `ost_form` | Form definitions |
| `FormField` | `ost_form_field` | Form field definitions |
| `FormEntry` | `ost_form_entry` | Form data entries |
| `FormEntryValue` | `ost_form_entry_values` | Form field values |
| `List` | `ost_list` | Selection lists |
| `ListItem` | `ost_list_items` | List item values |

### 📚 Knowledge Base Models
FAQ, categories, and content management.

| Model | Table | Description |
|-------|-------|-------------|
| `FAQ` | `ost_faq` | FAQ entries |
| `FAQCategory` | `ost_faq_category` | FAQ categories |
| `Category` | `ost_category` | General categories |
| `Page` | `ost_page` | Static pages |
| `Content` | `ost_content` | Content management |
| `Attachment` | `ost_attachment` | File attachments |

### 📁 File System Models
File storage and attachment handling.

| Model | Table | Description |
|-------|-------|-------------|
| `File` | `ost_file` | File metadata |
| `FileChunk` | `ost_file_chunk` | File content chunks |
| `Attachment` | `ost_attachment` | File attachments |
| `SearchIndex` | `ost_search` | Search indexing |
| `Draft` | `ost_draft` | Draft content |

### 🔧 Additional System Models
Specialized system functionality.

| Model | Table | Description |
|-------|-------|-------------|
| `Plugin` | `ost_plugin` | Plugin management |
| `Schedule` | `ost_schedule` | Scheduling system |
| `Queue` | `ost_queue` | Queue management |
| `QueueSort` | `ost_queue_sort` | Queue sorting |
| `QueueColumn` | `ost_queue_columns` | Queue columns |
| `QueueExport` | `ost_queue_export` | Queue exports |
| `SLA` | `ost_sla` | Service level agreements |
| `Topic` | `ost_help_topic` | Help topics |
| `Timezone` | `ost_timezone` | Timezone definitions |
| `Canned` | `ost_canned_response` | Canned responses |

### 🔐 Authentication Models
Authentication and authorization.

| Model | Table | Description |
|-------|-------|-------------|
| `ExternalIdentity` | `ost_external_identity` | OAuth2/OIDC identity mapping |
| `AuthToken` | `ost_auth_token` | JWT token storage |

## Model Features

### Common Patterns

All models inherit from `OSTicketBase` which provides:
- **Automatic table naming** with `ost_` prefix
- **Declarative mapping** using SQLAlchemy
- **Consistent field types** and constraints
- **Relationship definitions** with foreign keys

### Model Relationships

Models include properly defined relationships:
```python
class Ticket(OSTicketBase):
    # Foreign key relationships
    user = relationship("User", back_populates="tickets")
    dept = relationship("Department", back_populates="tickets")
    staff = relationship("Staff", back_populates="assigned_tickets")
    
    # Collection relationships  
    threads = relationship("Thread", back_populates="ticket")
    notes = relationship("Note", back_populates="ticket")
```

### Custom Data Tables

Many core entities have corresponding custom data tables:
- `Ticket` ↔ `TicketCData` - Custom ticket fields
- `User` ↔ `UserCData` - Custom user fields  
- `Organization` ↔ `OrganizationCData` - Custom organization fields

### Timestamps

Models with timestamps inherit from `TimestampMixin`:
```python
class TimestampMixin:
    created = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=True)
```

## Usage Examples

### Basic Model Usage
```python
from api.v2.models.ticket import Ticket
from api.v2.models.user import User
from api.v2.core.database import get_db

# Query tickets
db = next(get_db())
tickets = db.query(Ticket).filter(Ticket.status_id == 1).all()

# Create new ticket
new_ticket = Ticket(
    user_id=123,
    dept_id=1,
    topic_id=1,
    status_id=1,
    subject="New Support Request",
    source="Web"
)
db.add(new_ticket)
db.commit()
```

### Relationship Queries
```python
# Get ticket with related data
ticket = db.query(Ticket).options(
    joinedload(Ticket.user),
    joinedload(Ticket.dept),
    joinedload(Ticket.threads)
).filter(Ticket.ticket_id == 12345).first()

# Access related data
print(f"Ticket #{ticket.number} by {ticket.user.name}")
print(f"Department: {ticket.dept.name}")
print(f"Thread count: {len(ticket.threads)}")
```

### Custom Data Access
```python
from api.v2.models.ticket import Ticket, TicketCData

# Get ticket with custom data
ticket_data = db.query(Ticket).join(TicketCData).filter(
    Ticket.ticket_id == 12345
).first()

# Custom fields are in the cdata relationship
custom_data = ticket_data.cdata
```

## Database Schema Compatibility

### OSTicket Versions
- **Tested with**: OSTicket v1.18+
- **Schema**: MySQL/MariaDB with InnoDB engine
- **Encoding**: UTF-8 (utf8mb4)

### Migration Strategy
Models are designed for:
1. **Zero downtime** - No schema changes required
2. **Read/write compatibility** - Works alongside PHP application
3. **Data integrity** - Proper foreign key constraints
4. **Performance** - Optimized indexes and queries

### Database Prefixes
All table names use the configurable OSTicket prefix:
- Default: `ost_`
- Configurable via `OST_TABLE_PREFIX` environment variable
- Models automatically apply the correct prefix

## Performance Considerations

### Indexes
Models include appropriate indexes for:
- Primary keys and foreign keys
- Frequently queried fields
- Composite indexes for common query patterns

### Query Optimization
- **Lazy loading** - Related data loaded on demand
- **Eager loading** - Use `joinedload()` for related data
- **Query batching** - Batch operations for bulk updates
- **Connection pooling** - Efficient database connections

### Large Tables
For tables with high volume (tickets, threads, logs):
- **Pagination** - Use LIMIT/OFFSET for large result sets
- **Filtering** - Always filter by indexed fields
- **Archiving** - Consider data archiving strategies

## Model Validation

### Field Constraints
Models include appropriate field constraints:
```python
email = Column(String(255), nullable=False, index=True)
status = Column(Enum('active', 'disabled'), nullable=False, default='active')
priority = Column(Integer, CheckConstraint('priority >= 0 AND priority <= 4'))
```

### Business Logic
Keep business logic in service layers, not models:
- Models define data structure
- Services implement business rules
- Controllers handle API logic

## Next Steps

- Review specific model groups: [Ticket](ticket-models.md), [User](user-models.md), [Staff](staff-models.md), [System](system-models.md)
- Learn about [API endpoints](../api/) that use these models
- Check [configuration](../configuration.md) for database setup
- Read [architecture explanation](../../explanation/architecture.md) for system overview