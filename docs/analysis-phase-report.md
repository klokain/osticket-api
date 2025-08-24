# OSTicket Process Model Analysis Report

This document captures the results of the Phase 1 analysis for the osTicket system. It summarizes core business workflows, technical architecture, and integration points to guide FastAPI implementation.

## 1. Ticket Lifecycle Processes

### 1.1 State and Workflow
- Tickets move through states stored in the `TicketStatus` table (e.g., *open*, *closed*, *archived*).
- Transitions are triggered by user actions, automated rules, or system events.
- Overdue processing and lock cleanup run on scheduled cron tasks.

### 1.2 Permissions and Validation
The ticket model exposes granular permission constants that gate lifecycle actions:

```php
const PERM_CREATE   = 'ticket.create';
const PERM_EDIT     = 'ticket.edit';
const PERM_ASSIGN   = 'ticket.assign';
const PERM_RELEASE  = 'ticket.release';
const PERM_TRANSFER = 'ticket.transfer';
const PERM_CLOSE    = 'ticket.close';
const PERM_DELETE   = 'ticket.delete';
```

- Role and team permissions determine which agents can perform each transition.
- Validation checks confirm required fields and enforce SLA policies before state changes are persisted.

### 1.3 Triggers
- **Manual actions**: agent interface operations such as reply, assign, transfer, or close.
- **Email events**: inbound email processed by `osTicket\Mail\Fetcher` which routes messages to the API controller for ticket creation or thread updates.
- **Automation**: filters, canned responses, and SLA timers initiate follow-up actions.

## 2. Communication & Thread Management
- Each ticket owns a `Thread` containing ordered `ThreadEntry` records for messages, notes, and system events.
- Threads maintain collaborator lists and referral history for auditability.
- Attachments are stored via `Attachment` models linked to `AttachmentFile` entries to support reusable file references.
- Auto-response and notification templates send outbound email based on thread events.

## 3. Assignment & Routing Logic
- Departments provide initial routing; help topics map incoming requests to departments.
- Tickets may be assigned to individual `Staff` members or `Team`s. Assignment methods record events and update ticket fields atomically.
- Escalation rules leverage SLAs to escalate overdue tickets or reassign based on schedules.
- Ticket filters can auto-assign, set priority, or trigger custom actions during creation.

## 4. Event & Signal Architecture
The system uses a lightweight publish/subscribe mechanism:

```php
Signal::connect($signal, $callable, $object=null, $check=null);
Signal::send($signal, $object, &$data=null);
```

- Signals broadcast context and data to registered handlers without requiring tight coupling.
- Many core operations emit signals (e.g., ticket creation, assignment, status change) enabling plugins and observers to react.
- Signal handlers may modify data in-flight, enabling extensibility and customization.

## 5. Database Transaction Patterns
- Models extend `VerySimpleModel`, declaring table names, primary keys, and join relationships via static metadata arrays.
- Complex operations often involve multi-table updates wrapped in application-level transactions to maintain consistency between tickets, threads, and attachments.
- The ORM caches related objects (e.g., staff, team, user) to reduce redundant queries.
- Explicit cleanup tasks (e.g., lock and draft purges) run in cron to maintain data hygiene.

## 6. Permission & Security Model
- Authentication covers staff login, client access, and API key validation.
- `API` class validates keys against IP addresses and tracks capabilities like ticket creation or cron execution.
- `Role` configurations define permission sets consumed by `Staff` records; permissions are stored as JSON for flexibility.
- Sessions are periodically purged and password reset tokens cleaned via cron.

## 7. Integration Points
- **Email Servers**: IMAP/POP3 fetching and SMTP sending via `Mail\Fetcher` and `Mail` classes.
- **Plugin System**: Plugins extend functionality through `PluginConfig` and signal handlers.
- **Cron Jobs**: Central `Cron` class orchestrates mail fetching, overdue checks, log purges, and table maintenance.
- **File Storage**: Attachments use database-backed file storage with orphan cleanup tasks.

## 8. API Impact and Recommendations
- Map ticket, thread, user, department, and SLA entities to REST resources.
- Expose endpoints for assignment, status transitions, and collaborator management while enforcing permission checks.
- Surface event hooks or webhooks mirroring the Signal system to enable external integrations.
- Ensure API endpoints support idempotent operations and transactional integrity across related models.

## 9. Next Steps
- Create Linear issues for each major process area (ticket workflow, thread handling, assignment, events, security, integrations).
- Produce state transition and data flow diagrams based on this analysis.
- Establish documentation templates and standards for the upcoming FastAPI implementation.
- Prioritize endpoints that unlock core ticket management features for external consumers.

This report should serve as the primary reference for planning and implementing the FastAPI layer on top of the existing osTicket business logic.
