"""
Authentication related database models for OSTicket API v2
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, ForeignKey
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


class ExternalIdentity(OSTicketBase, TimestampMixin):
    """External identity provider mappings - IdP verifies identity, roles stay internal"""
    
    __tablename__ = "ost_external_identity"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # External provider information (identity verification only)
    provider = Column(String(50), nullable=False, index=True)  # 'keycloak', 'microsoft', etc.
    external_user_id = Column(String(255), nullable=False, index=True)
    external_email = Column(String(255), nullable=True, index=True)
    external_username = Column(String(255), nullable=True)
    external_name = Column(String(255), nullable=True)
    
    # OSTicket user mapping (roles managed internally)
    osticket_user_type = Column(String(10), nullable=False)  # 'staff' or 'user'
    osticket_user_id = Column(Integer, nullable=False, index=True)
    
    # Identity verification metadata
    identity_verified = Column(Boolean, default=False)
    last_login = Column(DateTime, nullable=True)
    provider_metadata = Column(Text, nullable=True)  # JSON data from provider (non-role data)
    
    def __repr__(self):
        return f"<ExternalIdentity {self.provider}:{self.external_user_id} -> {self.osticket_user_type}:{self.osticket_user_id}>"


class AuthToken(OSTicketBase, TimestampMixin):
    """JWT and OAuth2 token storage for authentication"""
    
    __tablename__ = "ost_auth_token"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # User identification
    user_type = Column(String(10), nullable=False, index=True)  # 'staff', 'user', 'external'
    user_id = Column(Integer, nullable=False, index=True)
    external_identity_id = Column(Integer, ForeignKey("ost_external_identity.id"), nullable=True)
    
    # Token information
    token_type = Column(String(20), nullable=False)  # 'access', 'refresh', 'oauth2'
    token_hash = Column(String(255), nullable=False, index=True)  # Hashed token for security
    expires_at = Column(DateTime, nullable=False, index=True)
    
    # OAuth2 specific fields (encrypted storage)
    access_token_encrypted = Column(Text, nullable=True)
    refresh_token_encrypted = Column(Text, nullable=True)
    scope = Column(String(500), nullable=True)
    
    # Session tracking
    session_id = Column(String(255), nullable=True, index=True)
    ip_address = Column(String(64), nullable=True)
    user_agent = Column(String(500), nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True, index=True)
    revoked_at = Column(DateTime, nullable=True)
    
    # Relationships
    external_identity = relationship("ExternalIdentity", backref="auth_tokens")
    
    def __repr__(self):
        return f"<AuthToken {self.token_type} for {self.user_type}:{self.user_id}>"