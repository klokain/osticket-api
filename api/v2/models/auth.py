"""
Authentication related database models for OSTicket API v2
"""

from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean
from sqlalchemy.orm import relationship
from .base import OSTicketBase, TimestampMixin

class ApiKey(OSTicketBase, TimestampMixin):
    """API key model for authentication"""
    
    __tablename__ = "ost_api_key"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    isactive = Column(Boolean, nullable=False, default=True, index=True)
    ipaddr = Column(String(64), nullable=False, index=True)
    apikey = Column(String(255), nullable=False, unique=True, index=True)
    can_create_tickets = Column(Boolean, nullable=False, default=True)
    can_exec_cron = Column(Boolean, nullable=False, default=True)
    notes = Column(Text, nullable=True)
    
    def __repr__(self):
        return f"<ApiKey(id={self.id}, ipaddr='{self.ipaddr}', active={self.isactive})>"

class StaffSession(OSTicketBase):
    """Staff session model"""
    
    __tablename__ = "ost_staff_session"
    
    session_id = Column(String(128), primary_key=True)
    staff_id = Column(Integer, nullable=False, default=0, index=True)
    session_data = Column(Text, nullable=True)
    session_expire = Column(DateTime, nullable=False, index=True)
    session_updated = Column(DateTime, nullable=False)
    user_ip = Column(String(64), nullable=False, default="")
    user_agent = Column(String(255), nullable=False, default="")
    
    def __repr__(self):
        return f"<StaffSession(session_id='{self.session_id}', staff_id={self.staff_id})>"

class UserSession(OSTicketBase):
    """User session model"""
    
    __tablename__ = "ost_user_session"
    
    session_id = Column(String(128), primary_key=True)
    user_id = Column(Integer, nullable=False, default=0, index=True)
    session_data = Column(Text, nullable=True)
    session_expire = Column(DateTime, nullable=False, index=True)
    session_updated = Column(DateTime, nullable=False)
    user_ip = Column(String(64), nullable=False, default="")
    user_agent = Column(String(255), nullable=False, default="")
    
    def __repr__(self):
        return f"<UserSession(session_id='{self.session_id}', user_id={self.user_id})>"