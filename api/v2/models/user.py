"""
User-related database models for OSTicket API v2
"""

from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, ForeignKey, LargeBinary
from sqlalchemy.orm import relationship
from .base import OSTicketBase

class User(OSTicketBase):
    """User model"""
    
    __tablename__ = "ost_user"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    org_id = Column(Integer, nullable=False, default=0)
    default_email_id = Column(Integer, nullable=False, default=0)
    status = Column(Integer, nullable=False, default=0)
    name = Column(String(128), nullable=False)
    created = Column(DateTime, nullable=False)
    updated = Column(DateTime, nullable=False)
    
    def __repr__(self):
        return f"<User(id={self.id}, name='{self.name}')>"

class UserCData(OSTicketBase):
    """User custom data model"""
    
    __tablename__ = "ost_user__cdata"
    
    user_id = Column(Integer, primary_key=True)
    email = Column(Text, nullable=True)
    name = Column(Text, nullable=True)
    phone = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    
    def __repr__(self):
        return f"<UserCData(user_id={self.user_id})>"

class UserEmail(OSTicketBase):
    """User email model"""
    
    __tablename__ = "ost_user_email"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False)
    flags = Column(Integer, nullable=False, default=0)
    address = Column(String(255), nullable=False, unique=True)
    
    def __repr__(self):
        return f"<UserEmail(id={self.id}, address='{self.address}')>"

class UserAccount(OSTicketBase):
    """User account model for authentication"""
    
    __tablename__ = "ost_user_account"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False)
    status = Column(Integer, nullable=False, default=0)
    timezone = Column(String(64), nullable=True)
    lang = Column(String(16), nullable=True)
    username = Column(String(64), nullable=True, unique=True)
    passwd = Column(String(128), nullable=True)
    backend = Column(String(32), nullable=True)
    extra = Column(Text, nullable=True)
    registered = Column(DateTime, nullable=True)
    
    def __repr__(self):
        return f"<UserAccount(id={self.id}, username='{self.username}')>"

class Organization(OSTicketBase):
    """Organization model"""
    
    __tablename__ = "ost_organization"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(128), nullable=False, default="")
    manager = Column(String(16), nullable=False, default="")
    status = Column(Integer, nullable=False, default=0)
    domain = Column(String(128), nullable=False, default="")
    extra = Column(Text, nullable=True)
    created = Column(DateTime, nullable=False)
    updated = Column(DateTime, nullable=False)
    
    def __repr__(self):
        return f"<Organization(id={self.id}, name='{self.name}')>"

class OrganizationCData(OSTicketBase):
    """Organization custom data model"""
    
    __tablename__ = "ost_organization__cdata"
    
    org_id = Column(Integer, primary_key=True)
    name = Column(Text, nullable=True)
    address = Column(Text, nullable=True)
    phone = Column(Text, nullable=True)
    website = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    
    def __repr__(self):
        return f"<OrganizationCData(org_id={self.org_id})>"