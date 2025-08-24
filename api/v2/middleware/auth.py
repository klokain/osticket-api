"""
Authentication middleware for OSTicket API v2
Multi-provider authentication: API keys, OAuth2/OIDC, staff/user passwords, JWT tokens
"""

import re
from datetime import datetime
from typing import Callable, Optional, Tuple
from fastapi import Request, Response, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text
import structlog
import ipaddress

from ..core.database import SessionLocal, get_db
from ..core.auth import AuthenticationService, AuthenticationError, token_manager
from ..models.auth import ApiKey, StaffSession, UserSession, AuthToken
from ..models.staff import Staff
from ..models.user import User
from ..core.exceptions import AuthorizationError

logger = structlog.get_logger()

class AuthContext:
    """Authentication context for the current request"""
    
    def __init__(
        self,
        auth_type: str,
        api_key: Optional[ApiKey] = None,
        staff: Optional[Staff] = None,
        user: Optional[User] = None,
        session_id: Optional[str] = None
    ):
        self.auth_type = auth_type  # "api_key", "staff_session", "user_session", "anonymous"
        self.api_key = api_key
        self.staff = staff
        self.user = user
        self.session_id = session_id
        self.is_authenticated = auth_type != "anonymous"
        self.is_staff = staff is not None
        self.is_admin = staff and staff.isadmin if staff else False

class AuthMiddleware(BaseHTTPMiddleware):
    """Authentication middleware"""
    
    # Public endpoints that don't require authentication
    PUBLIC_ENDPOINTS = {
        "/api/v2/health",
        "/api/v2/docs",
        "/api/v2/redoc",
        "/api/v2/openapi.json",
    }
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Check if endpoint is public
        if request.url.path in self.PUBLIC_ENDPOINTS:
            request.state.auth = AuthContext("anonymous")
            return await call_next(request)
        
        # Attempt authentication
        auth_context = await self.authenticate_request(request)
        request.state.auth = auth_context
        
        # Continue to endpoint
        return await call_next(request)
    
    async def authenticate_request(self, request: Request) -> AuthContext:
        """Authenticate the request using various methods"""
        
        db = SessionLocal()
        try:
            # Try API key authentication first
            api_key_header = request.headers.get("X-API-Key")
            if api_key_header:
                return await self.authenticate_api_key(db, request, api_key_header)
            
            # Try session authentication
            session_cookie = request.cookies.get("OSTSESSID")
            if session_cookie:
                return await self.authenticate_session(db, request, session_cookie)
            
            # No authentication provided
            logger.info(
                "Unauthenticated request",
                path=request.url.path,
                request_id=getattr(request.state, 'request_id', 'unknown')
            )
            
            return AuthContext("anonymous")
            
        except Exception as e:
            logger.error(
                "Authentication error",
                error=str(e),
                path=request.url.path,
                request_id=getattr(request.state, 'request_id', 'unknown')
            )
            raise AuthenticationError("Authentication failed")
        finally:
            db.close()
    
    async def authenticate_api_key(
        self, db: Session, request: Request, api_key: str
    ) -> AuthContext:
        """Authenticate using API key"""
        
        # Look up API key in database
        db_api_key = db.query(ApiKey).filter(
            ApiKey.apikey == api_key,
            ApiKey.isactive == True
        ).first()
        
        if not db_api_key:
            logger.warning(
                "Invalid API key",
                api_key_prefix=api_key[:8] + "..." if len(api_key) > 8 else api_key,
                request_id=getattr(request.state, 'request_id', 'unknown')
            )
            raise AuthenticationError("Invalid API key")
        
        # Check IP address restriction
        client_ip = self.get_client_ip(request)
        if not self.is_ip_allowed(client_ip, db_api_key.ipaddr):
            logger.warning(
                "API key IP restriction violation",
                client_ip=client_ip,
                allowed_ip=db_api_key.ipaddr,
                api_key_id=db_api_key.id,
                request_id=getattr(request.state, 'request_id', 'unknown')
            )
            raise AuthorizationError("IP address not allowed for this API key")
        
        logger.info(
            "API key authentication successful",
            api_key_id=db_api_key.id,
            client_ip=client_ip,
            request_id=getattr(request.state, 'request_id', 'unknown')
        )
        
        return AuthContext("api_key", api_key=db_api_key)
    
    async def authenticate_session(
        self, db: Session, request: Request, session_id: str
    ) -> AuthContext:
        """Authenticate using session cookie"""
        
        # Try staff session first
        staff_session = db.query(StaffSession).filter(
            StaffSession.session_id == session_id,
            StaffSession.session_expire > datetime.utcnow()
        ).first()
        
        if staff_session:
            # Get staff member
            staff = db.query(Staff).filter(
                Staff.staff_id == staff_session.staff_id,
                Staff.isactive == True
            ).first()
            
            if staff:
                logger.info(
                    "Staff session authentication successful",
                    staff_id=staff.staff_id,
                    username=staff.username,
                    session_id=session_id[:8] + "...",
                    request_id=getattr(request.state, 'request_id', 'unknown')
                )
                return AuthContext("staff_session", staff=staff, session_id=session_id)
        
        # Try user session
        user_session = db.query(UserSession).filter(
            UserSession.session_id == session_id,
            UserSession.session_expire > datetime.utcnow()
        ).first()
        
        if user_session:
            # Get user
            user = db.query(User).filter(
                User.id == user_session.user_id
            ).first()
            
            if user:
                logger.info(
                    "User session authentication successful",
                    user_id=user.id,
                    username=user.name,
                    session_id=session_id[:8] + "...",
                    request_id=getattr(request.state, 'request_id', 'unknown')
                )
                return AuthContext("user_session", user=user, session_id=session_id)
        
        logger.warning(
            "Invalid or expired session",
            session_id=session_id[:8] + "...",
            request_id=getattr(request.state, 'request_id', 'unknown')
        )
        
        raise AuthenticationError("Invalid or expired session")
    
    def get_client_ip(self, request: Request) -> str:
        """Get client IP address, considering proxy headers"""
        
        # Check for forwarded headers (for load balancers/proxies)
        x_forwarded_for = request.headers.get("X-Forwarded-For")
        if x_forwarded_for:
            # Take the first IP in the chain
            return x_forwarded_for.split(",")[0].strip()
        
        x_real_ip = request.headers.get("X-Real-IP")
        if x_real_ip:
            return x_real_ip
        
        # Fallback to direct client IP
        return request.client.host if request.client else "unknown"
    
    def is_ip_allowed(self, client_ip: str, allowed_ips: str) -> bool:
        """Check if client IP is allowed based on API key restrictions"""
        
        if not allowed_ips or allowed_ips == "*":
            return True
        
        # Handle multiple IPs/ranges separated by commas
        allowed_list = [ip.strip() for ip in allowed_ips.split(",") if ip.strip()]
        
        try:
            client_addr = ipaddress.ip_address(client_ip)
            
            for allowed in allowed_list:
                if "/" in allowed:
                    # CIDR notation
                    if client_addr in ipaddress.ip_network(allowed, strict=False):
                        return True
                else:
                    # Single IP
                    if client_addr == ipaddress.ip_address(allowed):
                        return True
            
            return False
            
        except ValueError as e:
            logger.error(
                "IP address validation error",
                client_ip=client_ip,
                allowed_ips=allowed_ips,
                error=str(e)
            )
            return False

# Dependency for getting authentication context in endpoints
def get_auth(request: Request) -> AuthContext:
    """Get authentication context from request state"""
    return request.state.auth

def require_auth(request: Request) -> AuthContext:
    """Require authentication - raises exception if not authenticated"""
    auth = get_auth(request)
    if not auth.is_authenticated:
        raise AuthenticationError("Authentication required")
    return auth

def require_staff(request: Request) -> AuthContext:
    """Require staff authentication"""
    auth = require_auth(request)
    if not auth.is_staff:
        raise AuthorizationError("Staff access required")
    return auth

def require_admin(request: Request) -> AuthContext:
    """Require admin authentication"""
    auth = require_staff(request)
    if not auth.is_admin:
        raise AuthorizationError("Admin access required")
    return auth

def require_api_key(request: Request) -> AuthContext:
    """Require API key authentication"""
    auth = require_auth(request)
    if auth.auth_type != "api_key":
        raise AuthorizationError("API key authentication required")
    return auth