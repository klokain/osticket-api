"""
Ticket-related database models for OSTicket API v2
"""

from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, Enum as SQLEnum, ForeignKey
from sqlalchemy.orm import relationship
from .base import OSTicketBase, TimestampMixin
from enum import Enum

class TicketSource(str, Enum):
    """Ticket source enumeration"""
    WEB = "Web"
    EMAIL = "Email"
    PHONE = "Phone"
    API = "API"
    OTHER = "Other"

class TicketState(str, Enum):
    """Ticket state enumeration"""
    OPEN = "open"
    CLOSED = "closed"
    ARCHIVED = "archived"

class Ticket(OSTicketBase, TimestampMixin):
    """Ticket model"""
    
    __tablename__ = "ost_ticket"
    
    ticket_id = Column(Integer, primary_key=True, autoincrement=True)
    ticket_pid = Column(Integer, nullable=True)  # Parent ticket ID
    number = Column(String(20), nullable=True, index=True)  # Human-readable ticket number
    
    # Foreign keys
    user_id = Column(Integer, ForeignKey("ost_user.id"), nullable=False, default=0)
    user_email_id = Column(Integer, nullable=False, default=0)
    status_id = Column(Integer, ForeignKey("ost_ticket_status.id"), nullable=False, default=0)
    dept_id = Column(Integer, ForeignKey("ost_department.dept_id"), nullable=False, default=0)
    sla_id = Column(Integer, ForeignKey("ost_sla.id"), nullable=False, default=0)
    topic_id = Column(Integer, nullable=False, default=0)
    staff_id = Column(Integer, ForeignKey("ost_staff.staff_id"), nullable=False, default=0)
    team_id = Column(Integer, ForeignKey("ost_team.team_id"), nullable=False, default=0)
    email_id = Column(Integer, nullable=False, default=0)
    lock_id = Column(Integer, nullable=False, default=0)
    
    # Ticket attributes
    flags = Column(Integer, nullable=False, default=0)
    sort = Column(Integer, nullable=False, default=0)
    ip_address = Column(String(64), nullable=False, default="")
    source = Column(SQLEnum(TicketSource), nullable=False, default=TicketSource.OTHER)
    source_extra = Column(String(40), nullable=True)
    
    # Status flags
    isoverdue = Column(Boolean, nullable=False, default=False)
    isanswered = Column(Boolean, nullable=False, default=False)
    isclosed = Column(Boolean, nullable=False, default=False)
    isdeleted = Column(Boolean, nullable=False, default=False)
    
    # Relationships
    user = relationship("User", back_populates="tickets", foreign_keys=[user_id])
    status = relationship("TicketStatus", back_populates="tickets")
    department = relationship("Department", back_populates="tickets") 
    staff = relationship("Staff", back_populates="assigned_tickets", foreign_keys=[staff_id])
    team = relationship("Team", back_populates="tickets", foreign_keys=[team_id])
    thread = relationship("Thread", back_populates="ticket", uselist=False)
    
    def __repr__(self):
        return f"<Ticket(id={self.ticket_id}, number='{self.number}', status_id={self.status_id})>"

class TicketStatus(OSTicketBase, TimestampMixin):
    """Ticket status model"""
    
    __tablename__ = "ost_ticket_status"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(60), nullable=False, default="", unique=True)
    state = Column(String(16), nullable=True, index=True)
    mode = Column(Integer, nullable=False, default=0)
    flags = Column(Integer, nullable=False, default=0)
    sort = Column(Integer, nullable=False, default=0)
    properties = Column(Text, nullable=False)
    
    # Relationships
    tickets = relationship("Ticket", back_populates="status")
    
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
    ispublic = Column(Boolean, nullable=False, default=True, index=True)
    
    def __repr__(self):
        return f"<TicketPriority(id={self.priority_id}, priority='{self.priority}')>"

class Thread(OSTicketBase, TimestampMixin):
    """Thread model for ticket conversations"""
    
    __tablename__ = "ost_thread"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    object_id = Column(Integer, nullable=False, default=0, index=True)
    object_type = Column(String(1), nullable=False, default="T", index=True)  # T = Ticket
    extra = Column(Text, nullable=True)
    
    # Relationships
    ticket_id = Column(Integer, ForeignKey("ost_ticket.ticket_id"), nullable=True)
    ticket = relationship("Ticket", back_populates="thread", foreign_keys=[ticket_id])
    entries = relationship("ThreadEntry", back_populates="thread")
    collaborators = relationship("ThreadCollaborator", back_populates="thread")
    
    def __repr__(self):
        return f"<Thread(id={self.id}, object_id={self.object_id}, object_type='{self.object_type}')>"

class ThreadEntry(OSTicketBase, TimestampMixin):
    """Thread entry model for messages, notes, etc."""
    
    __tablename__ = "ost_thread_entry"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    thread_id = Column(Integer, ForeignKey("ost_thread.id"), nullable=False, index=True)
    staff_id = Column(Integer, ForeignKey("ost_staff.staff_id"), nullable=False, default=0)
    user_id = Column(Integer, ForeignKey("ost_user.id"), nullable=False, default=0)
    
    type = Column(String(1), nullable=False, default="M", index=True)  # M=Message, R=Response, N=Note
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
    
    # Relationships
    thread = relationship("Thread", back_populates="entries")
    staff = relationship("Staff", foreign_keys=[staff_id])
    user = relationship("User", foreign_keys=[user_id])
    
    def __repr__(self):
        return f"<ThreadEntry(id={self.id}, thread_id={self.thread_id}, type='{self.type}')>"

class ThreadCollaborator(OSTicketBase, TimestampMixin):
    """Thread collaborator model"""
    
    __tablename__ = "ost_thread_collaborator"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    flags = Column(Integer, nullable=False, default=1)
    thread_id = Column(Integer, ForeignKey("ost_thread.id"), nullable=False, default=0)
    user_id = Column(Integer, ForeignKey("ost_user.id"), nullable=False, default=0)
    role = Column(String(1), nullable=False, default="M")  # M=message, N=note, R=reply
    
    # Relationships
    thread = relationship("Thread", back_populates="collaborators")
    user = relationship("User")
    
    def __repr__(self):
        return f"<ThreadCollaborator(id={self.id}, thread_id={self.thread_id}, user_id={self.user_id})>"