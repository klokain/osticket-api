"""
User and organization related database models for OSTicket API v2
"""

from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from .base import OSTicketBase, TimestampMixin

class User(OSTicketBase, TimestampMixin):
    """User model"""
    
    __tablename__ = "ost_user"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    org_id = Column(Integer, ForeignKey("ost_organization.id"), nullable=False, index=True)
    default_email_id = Column(Integer, ForeignKey("ost_user_email.id"), nullable=False, index=True)
    status = Column(Integer, nullable=False, default=0)
    name = Column(String(128), nullable=False, index=True)
    
    # Relationships
    organization = relationship("Organization", back_populates="users")
    default_email = relationship("UserEmail", foreign_keys=[default_email_id], post_update=True)
    emails = relationship("UserEmail", back_populates="user", foreign_keys="UserEmail.user_id")
    account = relationship("UserAccount", back_populates="user", uselist=False)
    tickets = relationship("Ticket", back_populates="user")
    
    def __repr__(self):
        return f"<User(id={self.id}, name='{self.name}', org_id={self.org_id})>"

class UserEmail(OSTicketBase):
    """User email model"""
    
    __tablename__ = "ost_user_email"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("ost_user.id"), nullable=False, index=True)
    flags = Column(Integer, nullable=False, default=0)
    address = Column(String(255), nullable=False, unique=True, index=True)
    
    # Relationships
    user = relationship("User", back_populates="emails", foreign_keys=[user_id])
    
    def __repr__(self):
        return f"<UserEmail(id={self.id}, user_id={self.user_id}, address='{self.address}')>"

class UserAccount(OSTicketBase):
    """User account model for authentication"""
    
    __tablename__ = "ost_user_account"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("ost_user.id"), nullable=False, unique=True, index=True)
    status = Column(Integer, nullable=False, default=0)
    timezone = Column(String(64), nullable=True)
    lang = Column(String(16), nullable=True)
    username = Column(String(64), nullable=True, unique=True, index=True)
    passwd = Column(String(128), nullable=True)  # ASCII charset, binary collation
    backend = Column(String(32), nullable=True)
    extra = Column(Text, nullable=True)
    registered = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="account")
    
    def __repr__(self):
        return f"<UserAccount(id={self.id}, user_id={self.user_id}, username='{self.username}')>"

class Organization(OSTicketBase, TimestampMixin):
    """Organization model"""
    
    __tablename__ = "ost_organization"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(128), nullable=False, default="", index=True)
    manager = Column(String(16), nullable=False, default="")
    status = Column(Integer, nullable=False, default=0)
    domain = Column(String(128), nullable=False, default="")
    extra = Column(Text, nullable=True)
    
    # Relationships
    users = relationship("User", back_populates="organization")
    
    def __repr__(self):
        return f"<Organization(id={self.id}, name='{self.name}')>"