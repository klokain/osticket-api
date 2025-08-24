"""
Email system models for OSTicket API v2
"""

from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, Enum
from sqlalchemy.orm import relationship
from .base import OSTicketBase

class Email(OSTicketBase):
    """Email model"""
    
    __tablename__ = "ost_email"
    
    email_id = Column(Integer, primary_key=True, autoincrement=True)
    noautoresp = Column(Boolean, nullable=False, default=False)
    priority_id = Column(Integer, nullable=False, default=2)
    dept_id = Column(Integer, nullable=False, default=0)
    topic_id = Column(Integer, nullable=False, default=0)
    email = Column(String(255), nullable=False, default="", unique=True)
    name = Column(String(255), nullable=False, default="")
    notes = Column(Text, nullable=True)
    created = Column(DateTime, nullable=False)
    updated = Column(DateTime, nullable=False)
    
    def __repr__(self):
        return f"<Email(email_id={self.email_id}, email='{self.email}', name='{self.name}')>"

class EmailAccount(OSTicketBase):
    """Email account model"""
    
    __tablename__ = "ost_email_account"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    email_id = Column(Integer, nullable=False)
    type = Column(Enum('mailbox', 'smtp', name='email_account_type'), nullable=False, default='mailbox')
    auth_bk = Column(String(128), nullable=False)
    auth_id = Column(String(16), nullable=True)
    active = Column(Boolean, nullable=False, default=False)
    host = Column(String(128), nullable=False, default="")
    port = Column(Integer, nullable=False)
    folder = Column(String(255), nullable=True)
    protocol = Column(Enum('IMAP', 'POP', 'SMTP', 'OTHER', name='email_protocol'), nullable=False, default='OTHER')
    encryption = Column(Enum('NONE', 'AUTO', 'SSL', name='email_encryption'), nullable=False, default='AUTO')
    fetchfreq = Column(Integer, nullable=False, default=5)
    fetchmax = Column(Integer, nullable=True, default=30)
    postfetch = Column(Enum('archive', 'delete', 'nothing', name='email_postfetch'), nullable=False, default='nothing')
    archivefolder = Column(String(255), nullable=True)
    allow_spoofing = Column(Boolean, nullable=True, default=False)
    num_errors = Column(Integer, nullable=False, default=0)
    last_error_msg = Column(Text, nullable=True)
    last_error = Column(DateTime, nullable=True)
    last_activity = Column(DateTime, nullable=True)
    created = Column(DateTime, nullable=False)
    updated = Column(DateTime, nullable=False, default='0000-00-00 00:00:00')
    
    def __repr__(self):
        return f"<EmailAccount(id={self.id}, email_id={self.email_id}, type='{self.type}')>"

class EmailTemplate(OSTicketBase):
    """Email template model"""
    
    __tablename__ = "ost_email_template"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    tpl_id = Column(Integer, nullable=False, default=0)
    code_name = Column(String(32), nullable=False)
    subject = Column(String(255), nullable=False)
    body = Column(Text, nullable=False)
    notes = Column(Text, nullable=True)
    created = Column(DateTime, nullable=False)
    updated = Column(DateTime, nullable=False)
    
    def __repr__(self):
        return f"<EmailTemplate(id={self.id}, code_name='{self.code_name}', subject='{self.subject}')>"

class EmailTemplateGroup(OSTicketBase):
    """Email template group model"""
    
    __tablename__ = "ost_email_template_group"
    
    tpl_id = Column(Integer, primary_key=True, autoincrement=True)
    isactive = Column(Boolean, nullable=False, default=False)
    name = Column(String(32), nullable=False, default="")
    lang = Column(String(16), nullable=False, default="en_US")
    notes = Column(Text, nullable=True)
    created = Column(DateTime, nullable=False)
    updated = Column(DateTime, nullable=False)
    
    def __repr__(self):
        return f"<EmailTemplateGroup(tpl_id={self.tpl_id}, name='{self.name}', lang='{self.lang}')>"

class CannedResponse(OSTicketBase):
    """Canned response model"""
    
    __tablename__ = "ost_canned_response"
    
    canned_id = Column(Integer, primary_key=True, autoincrement=True)
    dept_id = Column(Integer, nullable=False, default=0)
    isenabled = Column(Boolean, nullable=False, default=True)
    title = Column(String(255), nullable=False, default="", unique=True)
    response = Column(Text, nullable=False)
    lang = Column(String(16), nullable=False, default="en_US")
    notes = Column(Text, nullable=True)
    created = Column(DateTime, nullable=False)
    updated = Column(DateTime, nullable=False)
    
    def __repr__(self):
        return f"<CannedResponse(canned_id={self.canned_id}, title='{self.title}')>"