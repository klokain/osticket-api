"""
Authentication related database models for OSTicket API v2
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from .base import OSTicketBase, TimestampMixin

class ExternalIdentity(OSTicketBase, TimestampMixin):
    """External identity provider mappings - IdP verifies identity, roles stay internal"""
    
    __tablename__ = "ost_external_identity"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    provider = Column(String(50), nullable=False, index=True)  # 'keycloak', 'microsoft', etc.
    external_user_id = Column(String(255), nullable=False, index=True)  # User ID from IdP
    osticket_user_type = Column(String(10), nullable=False, index=True)  # 'staff' or 'user'
    osticket_user_id = Column(Integer, nullable=False, index=True)  # staff_id or user_id
    
    # Additional identity data from IdP
    external_username = Column(String(255), nullable=True)
    external_email = Column(String(255), nullable=True)
    external_name = Column(String(255), nullable=True)
    
    # Flags
    is_active = Column(Boolean, nullable=False, default=True)
    
    def __repr__(self):
        return f"<ExternalIdentity(id={self.id}, provider='{self.provider}', external_user_id='{self.external_user_id}')>"

class AuthToken(OSTicketBase, TimestampMixin):
    """JWT token storage for authentication"""
    
    __tablename__ = "ost_auth_token"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_type = Column(String(10), nullable=False, index=True)  # 'staff' or 'user'
    user_id = Column(Integer, nullable=False, index=True)  # staff_id or user_id
    token_type = Column(String(20), nullable=False, default="access")  # 'access' or 'refresh'
    
    # Token data
    jti = Column(String(36), nullable=False, unique=True, index=True)  # JWT ID (UUID)
    token_hash = Column(String(64), nullable=False, index=True)  # SHA256 of token
    expires_at = Column(DateTime, nullable=False, index=True)
    
    # Session information
    ip_address = Column(String(64), nullable=True)
    user_agent = Column(String(500), nullable=True)
    
    # Flags
    is_revoked = Column(Boolean, nullable=False, default=False, index=True)
    
    def __repr__(self):
        return f"<AuthToken(id={self.id}, user_type='{self.user_type}', user_id={self.user_id}, token_type='{self.token_type}')>"