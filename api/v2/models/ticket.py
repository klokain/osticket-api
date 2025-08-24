"""
Ticket-related database models for OSTicket API v2
"""

from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, Enum, ForeignKey
from sqlalchemy.orm import relationship
from .base import OSTicketBase

class Ticket(OSTicketBase):
    """Ticket model"""
    
    __tablename__ = "ost_ticket"
    
    ticket_id = Column(Integer, primary_key=True, autoincrement=True)
    ticket_pid = Column(Integer, nullable=True)  # Parent ticket ID
    number = Column(String(20), nullable=True)  # Human-readable ticket number
    
    # Foreign keys
    user_id = Column(Integer, nullable=False, default=0)
    user_email_id = Column(Integer, nullable=False, default=0)
    status_id = Column(Integer, nullable=False, default=0)
    dept_id = Column(Integer, nullable=False, default=0)
    sla_id = Column(Integer, nullable=False, default=0)
    topic_id = Column(Integer, nullable=False, default=0)
    staff_id = Column(Integer, nullable=False, default=0)
    team_id = Column(Integer, nullable=False, default=0)
    email_id = Column(Integer, nullable=False, default=0)
    lock_id = Column(Integer, nullable=False, default=0)
    
    # Ticket attributes
    flags = Column(Integer, nullable=False, default=0)
    sort = Column(Integer, nullable=False, default=0)
    ip_address = Column(String(64), nullable=False, default="")
    source = Column(Enum('Web', 'Email', 'Phone', 'API', 'Other', name='ticket_source'), nullable=False, default='Other')
    source_extra = Column(String(40), nullable=True)
    
    # Status flags
    isoverdue = Column(Boolean, nullable=False, default=False)
    isanswered = Column(Boolean, nullable=False, default=False)
    
    # Timestamps
    duedate = Column(DateTime, nullable=True)
    est_duedate = Column(DateTime, nullable=True)
    reopened = Column(DateTime, nullable=True)
    closed = Column(DateTime, nullable=True)
    lastupdate = Column(DateTime, nullable=True)
    created = Column(DateTime, nullable=False)
    updated = Column(DateTime, nullable=False)
    
    def __repr__(self):
        return f"<Ticket(ticket_id={self.ticket_id}, number='{self.number}', status_id={self.status_id})>"

class TicketCData(OSTicketBase):
    """Ticket custom data model"""
    
    __tablename__ = "ost_ticket__cdata"
    
    ticket_id = Column(Integer, primary_key=True)
    subject = Column(Text, nullable=True)
    priority = Column(Text, nullable=True)
    
    def __repr__(self):
        return f"<TicketCData(ticket_id={self.ticket_id})>"

class TicketStatus(OSTicketBase):
    """Ticket status model"""
    
    __tablename__ = "ost_ticket_status"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(60), nullable=False, default="", unique=True)
    state = Column(String(16), nullable=True)
    mode = Column(Integer, nullable=False, default=0)
    flags = Column(Integer, nullable=False, default=0)
    sort = Column(Integer, nullable=False, default=0)
    properties = Column(Text, nullable=False)
    created = Column(DateTime, nullable=False)
    updated = Column(DateTime, nullable=False)
    
    def __repr__(self):
        return f"<TicketStatus(id={self.id}, name='{self.name}', state='{self.state}')>"

class TicketPriority(OSTicketBase):
    """Ticket priority model"""
    
    __tablename__ = "ost_ticket_priority"
    
    priority_id = Column(Integer, primary_key=True, autoincrement=True)
    priority = Column(String(60), nullable=False, default="", unique=True)
    priority_desc = Column(String(30), nullable=False, default="")
    priority_color = Column(String(7), nullable=False, default="")
    priority_urgency = Column(Boolean, nullable=False, default=False)
    ispublic = Column(Boolean, nullable=False, default=True)
    
    def __repr__(self):
        return f"<TicketPriority(priority_id={self.priority_id}, priority='{self.priority}')>"

class Thread(OSTicketBase):
    """Thread model for ticket conversations"""
    
    __tablename__ = "ost_thread"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    object_id = Column(Integer, nullable=False, default=0)
    object_type = Column(String(1), nullable=False, default="T")  # T = Ticket
    extra = Column(Text, nullable=True)
    created = Column(DateTime, nullable=False)
    updated = Column(DateTime, nullable=False)
    
    def __repr__(self):
        return f"<Thread(id={self.id}, object_id={self.object_id}, object_type='{self.object_type}')>"

class ThreadEntry(OSTicketBase):
    """Thread entry model for messages, notes, etc."""
    
    __tablename__ = "ost_thread_entry"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    thread_id = Column(Integer, nullable=False)
    staff_id = Column(Integer, nullable=False, default=0)
    user_id = Column(Integer, nullable=False, default=0)
    
    type = Column(String(1), nullable=False, default="M")  # M=Message, R=Response, N=Note
    flags = Column(Integer, nullable=False, default=0)
    poster = Column(String(128), nullable=False, default="")
    editor = Column(Integer, nullable=False, default=0)
    editor_type = Column(String(1), nullable=False, default="")
    source = Column(String(8), nullable=False, default="")
    title = Column(String(255), nullable=True, default=None)
    body = Column(Text, nullable=False)
    format = Column(String(16), nullable=False, default="html")
    ip_address = Column(String(64), nullable=False, default="")
    extra = Column(Text, nullable=True)
    created = Column(DateTime, nullable=False)
    updated = Column(DateTime, nullable=False)
    
    def __repr__(self):
        return f"<ThreadEntry(id={self.id}, thread_id={self.thread_id}, type='{self.type}')>"

class ThreadEntryEmail(OSTicketBase):
    """Thread entry email model"""
    
    __tablename__ = "ost_thread_entry_email"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    thread_entry_id = Column(Integer, nullable=False)
    email_id = Column(Integer, nullable=False, default=0)
    mid = Column(String(255), nullable=False, default="")
    headers = Column(Text, nullable=True)
    
    def __repr__(self):
        return f"<ThreadEntryEmail(id={self.id}, thread_entry_id={self.thread_entry_id})>"

class ThreadEntryMerge(OSTicketBase):
    """Thread entry merge model"""
    
    __tablename__ = "ost_thread_entry_merge"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    thread_entry_id = Column(Integer, nullable=False)
    data = Column(Text, nullable=True)
    
    def __repr__(self):
        return f"<ThreadEntryMerge(id={self.id}, thread_entry_id={self.thread_entry_id})>"

class ThreadEvent(OSTicketBase):
    """Thread event model"""
    
    __tablename__ = "ost_thread_event"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    thread_id = Column(Integer, nullable=False, default=0)
    staff_id = Column(Integer, nullable=False, default=0)
    team_id = Column(Integer, nullable=False, default=0)
    dept_id = Column(Integer, nullable=False, default=0)
    topic_id = Column(Integer, nullable=False, default=0)
    event_id = Column(Integer, nullable=True)
    username = Column(String(128), nullable=False, default="")
    event = Column(String(255), nullable=False, default="")
    data = Column(String(1024), nullable=True)
    timestamp = Column(DateTime, nullable=False)
    
    def __repr__(self):
        return f"<ThreadEvent(id={self.id}, thread_id={self.thread_id}, event='{self.event}')>"

class ThreadReferral(OSTicketBase):
    """Thread referral model"""
    
    __tablename__ = "ost_thread_referral"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    thread_id = Column(Integer, nullable=False, default=0)
    object_id = Column(Integer, nullable=False, default=0)
    object_type = Column(String(1), nullable=False, default="T")
    created = Column(DateTime, nullable=False)
    
    def __repr__(self):
        return f"<ThreadReferral(id={self.id}, thread_id={self.thread_id}, object_id={self.object_id})>"

class ThreadCollaborator(OSTicketBase):
    """Thread collaborator model"""
    
    __tablename__ = "ost_thread_collaborator"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    flags = Column(Integer, nullable=False, default=1)
    thread_id = Column(Integer, nullable=False, default=0)
    user_id = Column(Integer, nullable=False, default=0)
    role = Column(String(1), nullable=False, default="M")  # M=message, N=note, R=reply
    created = Column(DateTime, nullable=False)
    updated = Column(DateTime, nullable=False)
    
    def __repr__(self):
        return f"<ThreadCollaborator(id={self.id}, thread_id={self.thread_id}, user_id={self.user_id})>"

class Note(OSTicketBase):
    """Note model"""
    
    __tablename__ = "ost_note"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    pid = Column(Integer, nullable=True)
    staff_id = Column(Integer, nullable=False, default=0)
    ext_id = Column(String(10), nullable=True)
    sort = Column(Integer, nullable=False, default=0)
    types = Column(String(25), nullable=False, default="")
    flags = Column(Integer, nullable=False, default=0)
    status = Column(Integer, nullable=False, default=0)
    title = Column(String(255), nullable=False, default="")
    body = Column(Text, nullable=False)
    extra = Column(Text, nullable=True)
    created = Column(DateTime, nullable=False)
    updated = Column(DateTime, nullable=False)
    
    def __repr__(self):
        return f"<Note(id={self.id}, title='{self.title}')>"