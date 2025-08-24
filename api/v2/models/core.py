"""
Core system models for OSTicket API v2
"""

from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, LargeBinary, Enum
from sqlalchemy.orm import relationship
from .base import OSTicketBase
from enum import Enum as PyEnum

class Config(OSTicketBase):
    """Configuration model"""
    
    __tablename__ = "ost_config"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    namespace = Column(String(64), nullable=False)
    key = Column(String(64), nullable=False)
    value = Column(Text, nullable=False)
    updated = Column(DateTime, nullable=False)
    
    def __repr__(self):
        return f"<Config(id={self.id}, namespace='{self.namespace}', key='{self.key}')>"

class Session(OSTicketBase):
    """Session model"""
    
    __tablename__ = "ost_session"
    
    session_id = Column(String(255), primary_key=True)
    session_data = Column(LargeBinary, nullable=True)
    session_expire = Column(DateTime, nullable=True)
    session_updated = Column(DateTime, nullable=True)
    user_id = Column(String(16), nullable=False, default="0")
    user_ip = Column(String(64), nullable=False, default="")
    user_agent = Column(String(255), nullable=False, default="")
    
    def __repr__(self):
        return f"<Session(session_id='{self.session_id}', user_id='{self.user_id}')>"

class Syslog(OSTicketBase):
    """System log model"""
    
    __tablename__ = "ost_syslog"
    
    log_id = Column(Integer, primary_key=True, autoincrement=True)
    log_type = Column(Enum('Debug', 'Warning', 'Error', name='log_type'), nullable=False)
    title = Column(String(255), nullable=False)
    log = Column(Text, nullable=False)
    logger = Column(String(64), nullable=False)
    ip_address = Column(String(64), nullable=False)
    created = Column(DateTime, nullable=False)
    updated = Column(DateTime, nullable=False)
    
    def __repr__(self):
        return f"<Syslog(log_id={self.log_id}, log_type='{self.log_type}', title='{self.title}')>"

class Lock(OSTicketBase):
    """Lock model for preventing concurrent access"""
    
    __tablename__ = "ost_lock"
    
    lock_id = Column(Integer, primary_key=True, autoincrement=True)
    staff_id = Column(Integer, nullable=False, default=0)
    expire = Column(DateTime, nullable=False)
    code = Column(String(20), nullable=True)
    created = Column(DateTime, nullable=False)
    
    def __repr__(self):
        return f"<Lock(lock_id={self.lock_id}, staff_id={self.staff_id})>"

class ApiKey(OSTicketBase):
    """API key model"""
    
    __tablename__ = "ost_api_key"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    isactive = Column(Boolean, nullable=False, default=True)
    ipaddr = Column(String(64), nullable=False)
    apikey = Column(String(255), nullable=False, unique=True)
    can_create_tickets = Column(Boolean, nullable=False, default=True)
    can_exec_cron = Column(Boolean, nullable=False, default=True)
    notes = Column(Text, nullable=True)
    updated = Column(DateTime, nullable=False)
    created = Column(DateTime, nullable=False)
    
    def __repr__(self):
        return f"<ApiKey(id={self.id}, ipaddr='{self.ipaddr}')>"

class Sequence(OSTicketBase):
    """Sequence model for ticket numbering"""
    
    __tablename__ = "ost_sequence"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(64), nullable=True, unique=True)
    flags = Column(Integer, nullable=False, default=0)
    next = Column(Integer, nullable=False, default=1)
    increment = Column(Integer, nullable=False, default=1)
    padding = Column(String(16), nullable=False, default="0")
    updated = Column(DateTime, nullable=False)
    created = Column(DateTime, nullable=False)
    
    def __repr__(self):
        return f"<Sequence(id={self.id}, name='{self.name}', next={self.next})>"

class Translation(OSTicketBase):
    """Translation model"""
    
    __tablename__ = "ost_translation"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    object_hash = Column(String(16), nullable=False)
    type = Column(String(8), nullable=False)
    flags = Column(Integer, nullable=False, default=0)
    revision = Column(Integer, nullable=True)
    agent_id = Column(Integer, nullable=False, default=0)
    lang = Column(String(16), nullable=False)
    text = Column(Text, nullable=False)
    source_text = Column(Text, nullable=True)
    updated = Column(DateTime, nullable=False)
    created = Column(DateTime, nullable=False)
    
    def __repr__(self):
        return f"<Translation(id={self.id}, lang='{self.lang}', type='{self.type}')>"

class Event(OSTicketBase):
    """Event model"""
    
    __tablename__ = "ost_event"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(60), nullable=False)
    description = Column(String(60), nullable=True)
    
    def __repr__(self):
        return f"<Event(id={self.id}, name='{self.name}')>"

class File(OSTicketBase):
    """File model for attachments"""
    
    __tablename__ = "ost_file"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    ft = Column(String(255), nullable=False, default="")  # file type
    bk = Column(String(1), nullable=False, default="D")   # backend
    name = Column(String(255), nullable=False, default="")
    size = Column(Integer, nullable=False, default=0)
    key = Column(String(86), nullable=False)
    signature = Column(String(86), nullable=False)
    created = Column(DateTime, nullable=False)
    
    def __repr__(self):
        return f"<File(id={self.id}, name='{self.name}', size={self.size})>"

class FileChunk(OSTicketBase):
    """File chunk model for large file storage"""
    
    __tablename__ = "ost_file_chunk"
    
    file_id = Column(Integer, primary_key=True)
    chunk_id = Column(Integer, primary_key=True)
    filedata = Column(LargeBinary, nullable=False)
    
    def __repr__(self):
        return f"<FileChunk(file_id={self.file_id}, chunk_id={self.chunk_id})>"

class Attachment(OSTicketBase):
    """Attachment model"""
    
    __tablename__ = "ost_attachment"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    object_id = Column(Integer, nullable=False)
    type = Column(String(1), nullable=False)
    file_id = Column(Integer, nullable=False)
    name = Column(String(255), nullable=True)
    inline = Column(Boolean, nullable=False, default=False)
    lang = Column(String(16), nullable=True)
    
    def __repr__(self):
        return f"<Attachment(id={self.id}, object_id={self.object_id}, file_id={self.file_id})>"

class SearchIndex(OSTicketBase):
    """Search index model"""
    
    __tablename__ = "ost__search"
    
    object_type = Column(String(8), primary_key=True)
    object_id = Column(Integer, primary_key=True)
    title = Column(Text, nullable=True)
    content = Column(Text, nullable=True)
    
    def __repr__(self):
        return f"<SearchIndex(object_type='{self.object_type}', object_id={self.object_id})>"

class Content(OSTicketBase):
    """Content model for pages and templates"""
    
    __tablename__ = "ost_content"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    isactive = Column(Boolean, nullable=False, default=False)
    type = Column(String(32), nullable=False, default="other")
    name = Column(String(255), nullable=False, unique=True)
    body = Column(Text, nullable=False)
    notes = Column(Text, nullable=True)
    created = Column(DateTime, nullable=False)
    updated = Column(DateTime, nullable=False)
    
    def __repr__(self):
        return f"<Content(id={self.id}, name='{self.name}', type='{self.type}')>"

class Draft(OSTicketBase):
    """Draft model for saved drafts"""
    
    __tablename__ = "ost_draft"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    staff_id = Column(Integer, nullable=False)
    namespace = Column(String(32), nullable=False, default="")
    body = Column(Text, nullable=False)
    extra = Column(Text, nullable=True)
    created = Column(DateTime, nullable=False)
    updated = Column(DateTime, nullable=True)
    
    def __repr__(self):
        return f"<Draft(id={self.id}, staff_id={self.staff_id}, namespace='{self.namespace}')>"