# Database models - Complete OSTicket Schema
from .base import OSTicketBase, TimestampMixin
from .auth import ExternalIdentity, AuthToken

# Core system models
from .core import (
    Config, Session, Syslog, Lock, ApiKey, Sequence, Translation,
    Event, File, FileChunk, Attachment, SearchIndex, Content, Draft
)

# Staff and department models
from .staff import (
    Staff, Department, Team, TeamMember, Role, StaffDeptAccess, SLA,
    Schedule, ScheduleEntry, Group
)

# User and organization models  
from .user import (
    User, UserCData, UserEmail, UserAccount, Organization, OrganizationCData
)

# Ticket system models
from .ticket import (
    Ticket, TicketCData, TicketStatus, TicketPriority, Thread, ThreadEntry,
    ThreadEntryEmail, ThreadEntryMerge, ThreadEvent, ThreadReferral,
    ThreadCollaborator, Note
)

# Email system models
from .email import (
    Email, EmailAccount, EmailTemplate, EmailTemplateGroup, CannedResponse
)

# Forms system models
from .form import (
    Form, FormField, FormEntry, FormEntryValues
)

# Knowledge base models
from .knowledge import (
    FAQ, FAQCategory, FAQTopic, HelpTopic, HelpTopicForm
)

# Additional system models
from .system import (
    Queue, QueueColumn, QueueColumns, QueueConfig, QueueExport, QueueSort,
    QueueSorts, Filter, FilterRule, FilterAction, Plugin, PluginInstance,
    Task, TaskCData, List, ListItems
)

__all__ = [
    # Base classes
    "OSTicketBase",
    "TimestampMixin",
    
    # Auth models
    "ExternalIdentity",
    "AuthToken",
    
    # Core system models
    "Config", "Session", "Syslog", "Lock", "ApiKey", "Sequence", "Translation",
    "Event", "File", "FileChunk", "Attachment", "SearchIndex", "Content", "Draft",
    
    # Staff and department models
    "Staff", "Department", "Team", "TeamMember", "Role", "StaffDeptAccess", "SLA",
    "Schedule", "ScheduleEntry", "Group",
    
    # User and organization models
    "User", "UserCData", "UserEmail", "UserAccount", "Organization", "OrganizationCData",
    
    # Ticket system models
    "Ticket", "TicketCData", "TicketStatus", "TicketPriority", "Thread", "ThreadEntry",
    "ThreadEntryEmail", "ThreadEntryMerge", "ThreadEvent", "ThreadReferral",
    "ThreadCollaborator", "Note",
    
    # Email system models
    "Email", "EmailAccount", "EmailTemplate", "EmailTemplateGroup", "CannedResponse",
    
    # Forms system models
    "Form", "FormField", "FormEntry", "FormEntryValues",
    
    # Knowledge base models
    "FAQ", "FAQCategory", "FAQTopic", "HelpTopic", "HelpTopicForm",
    
    # Additional system models
    "Queue", "QueueColumn", "QueueColumns", "QueueConfig", "QueueExport", "QueueSort",
    "QueueSorts", "Filter", "FilterRule", "FilterAction", "Plugin", "PluginInstance",
    "Task", "TaskCData", "List", "ListItems",
]