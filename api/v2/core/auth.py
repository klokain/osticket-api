"""
Authentication utilities and token management for OSTicket API v2
"""

import hashlib
import json
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, Union
from jose import jwt, JWTError
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from ..models.auth import AuthToken, ExternalIdentity, ApiKey, StaffSession, UserSession
from ..models.staff import Staff
from ..models.user import User
from ..core.config import settings
import structlog

logger = structlog.get_logger()

# Password context for OSTicket compatibility
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AuthenticationError(Exception):
    """Authentication failed"""
    pass

class AuthorizationError(Exception):
    """Authorization failed"""
    pass

class TokenManager:
    """Manage JWT tokens and authentication"""
    
    def __init__(self):
        self.secret_key = settings.JWT_SECRET_KEY or settings.SECRET_KEY
        self.algorithm = settings.JWT_ALGORITHM
        self.access_token_expire_minutes = settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
        self.refresh_token_expire_days = settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS
    
    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Create JWT access token"""
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        
        to_encode.update({"exp": expire, "type": "access"})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
    
    def create_refresh_token(self, data: dict) -> str:
        """Create JWT refresh token"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=self.refresh_token_expire_days)
        to_encode.update({"exp": expire, "type": "refresh"})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
    
    def verify_token(self, token: str) -> Dict[str, Any]:
        """Verify and decode JWT token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except JWTError as e:
            logger.warning("JWT verification failed", error=str(e))
            raise AuthenticationError("Invalid token")
    
    def hash_token(self, token: str) -> str:
        """Create hash of token for database storage"""
        return hashlib.sha256(token.encode()).hexdigest()

class OSTicketPasswordVerifier:
    """Verify passwords against OSTicket's password hashing"""
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify password against OSTicket's password hash"""
        try:
            # Try bcrypt first (modern OSTicket)
            if hashed_password.startswith('$2'):
                return pwd_context.verify(plain_password, hashed_password)
            
            # Try MD5 (legacy OSTicket) - NOTE: This is insecure
            if len(hashed_password) == 32:
                import hashlib
                md5_hash = hashlib.md5(plain_password.encode()).hexdigest()
                return md5_hash == hashed_password
                
            # Default to bcrypt
            return pwd_context.verify(plain_password, hashed_password)
            
        except Exception as e:
            logger.error("Password verification failed", error=str(e))
            return False

class AuthenticationService:
    """Main authentication service supporting multiple auth methods"""
    
    def __init__(self, db: Session):
        self.db = db
        self.token_manager = TokenManager()
        self.password_verifier = OSTicketPasswordVerifier()
    
    def authenticate_api_key(self, api_key: str, ip_address: str) -> Optional[Dict[str, Any]]:
        """Authenticate using OSTicket API key"""
        try:
            # Query API key from database
            db_api_key = self.db.query(ApiKey).filter(
                ApiKey.apikey == api_key,
                ApiKey.isactive == True
            ).first()
            
            if not db_api_key:
                logger.warning("API key not found", api_key=api_key[:8] + "...")
                return None
            
            # Check IP address restrictions
            if db_api_key.ipaddr and db_api_key.ipaddr != '0.0.0.0':
                allowed_ips = [ip.strip() for ip in db_api_key.ipaddr.split(',')]
                if ip_address not in allowed_ips:
                    logger.warning("API key IP restriction failed", 
                                 allowed_ips=allowed_ips, client_ip=ip_address)
                    return None
            
            logger.info("API key authentication successful", api_key_id=db_api_key.id)
            
            return {
                "user_type": "api_key",
                "user_id": db_api_key.id,
                "api_key_id": db_api_key.id,
                "permissions": {
                    "can_create_tickets": db_api_key.can_create_tickets,
                    "can_exec_cron": db_api_key.can_exec_cron
                }
            }
            
        except Exception as e:
            logger.error("API key authentication error", error=str(e))
            return None
    
    def authenticate_staff(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """Authenticate staff user with username/password"""
        try:
            # Query staff from database
            staff = self.db.query(Staff).filter(
                Staff.username == username,
                Staff.isactive == True
            ).first()
            
            if not staff:
                logger.warning("Staff user not found", username=username)
                return None
            
            # Verify password
            if not self.password_verifier.verify_password(password, staff.passwd):
                logger.warning("Staff password verification failed", username=username)
                return None
            
            logger.info("Staff authentication successful", staff_id=staff.staff_id, username=username)
            
            return {
                "user_type": "staff",
                "user_id": staff.staff_id,
                "username": staff.username,
                "email": staff.email,
                "firstname": staff.firstname,
                "lastname": staff.lastname,
                "dept_id": staff.dept_id,
                "role_id": staff.role_id,
                "isadmin": staff.isadmin
            }
            
        except Exception as e:
            logger.error("Staff authentication error", error=str(e))
            return None
    
    def authenticate_user(self, email: str, password: str) -> Optional[Dict[str, Any]]:
        """Authenticate end user with email/password"""
        try:
            # Query user from database
            user = self.db.query(User).filter(
                User.email == email
            ).first()
            
            if not user:
                logger.warning("User not found", email=email)
                return None
            
            # Check if user account exists and get password
            user_account = user.account
            if not user_account:
                logger.warning("User account not found", user_id=user.id)
                return None
            
            # Verify password
            if not self.password_verifier.verify_password(password, user_account.passwd):
                logger.warning("User password verification failed", email=email)
                return None
            
            logger.info("User authentication successful", user_id=user.id, email=email)
            
            return {
                "user_type": "user",
                "user_id": user.id,
                "email": user.email,
                "name": user.name,
                "organization_id": user.org_id,
                "status": user_account.status
            }
            
        except Exception as e:
            logger.error("User authentication error", error=str(e))
            return None
    
    def authenticate_external_identity(self, provider: str, external_user_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Authenticate using external identity provider (IdP verifies identity, roles internal)"""
        try:
            external_user_id = external_user_data.get("id") or external_user_data.get("sub")
            external_email = external_user_data.get("email")
            
            if not external_user_id:
                logger.error("External user ID not provided", provider=provider)
                return None
            
            # Look for existing external identity mapping
            external_identity = self.db.query(ExternalIdentity).filter(
                ExternalIdentity.provider == provider,
                ExternalIdentity.external_user_id == external_user_id
            ).first()
            
            if external_identity:
                # Update last login and metadata
                external_identity.last_login = datetime.utcnow()
                external_identity.external_email = external_email
                external_identity.external_name = external_user_data.get("name")
                external_identity.provider_metadata = json.dumps(external_user_data)
                self.db.commit()
                
                # Get OSTicket user data based on mapping
                osticket_user = self._get_osticket_user(
                    external_identity.osticket_user_type, 
                    external_identity.osticket_user_id
                )
                
                if osticket_user:
                    logger.info("External identity authentication successful", 
                              provider=provider, external_user_id=external_user_id,
                              osticket_user_type=external_identity.osticket_user_type)
                    
                    # Merge external identity data with OSTicket user data
                    auth_data = dict(osticket_user)
                    auth_data["external_identity"] = {
                        "provider": provider,
                        "external_user_id": external_user_id,
                        "external_email": external_email
                    }
                    return auth_data
            
            # If no mapping exists and auto-creation is disabled, fail
            if not settings.AUTO_CREATE_USERS_FROM_EXTERNAL:
                logger.warning("External identity not mapped and auto-creation disabled",
                             provider=provider, external_user_id=external_user_id)
                return None
            
            # Auto-create logic would go here if enabled
            logger.info("External identity auto-creation not yet implemented",
                       provider=provider, external_user_id=external_user_id)
            return None
            
        except Exception as e:
            logger.error("External identity authentication error", error=str(e))
            return None
    
    def _get_osticket_user(self, user_type: str, user_id: int) -> Optional[Dict[str, Any]]:
        """Get OSTicket user data by type and ID"""
        try:
            if user_type == "staff":
                staff = self.db.query(Staff).filter(Staff.staff_id == user_id).first()
                if staff:
                    return {
                        "user_type": "staff",
                        "user_id": staff.staff_id,
                        "username": staff.username,
                        "email": staff.email,
                        "firstname": staff.firstname,
                        "lastname": staff.lastname,
                        "dept_id": staff.dept_id,
                        "role_id": staff.role_id,
                        "isadmin": staff.isadmin
                    }
            elif user_type == "user":
                user = self.db.query(User).filter(User.id == user_id).first()
                if user:
                    return {
                        "user_type": "user",
                        "user_id": user.id,
                        "email": user.email,
                        "name": user.name,
                        "organization_id": user.org_id
                    }
        except Exception as e:
            logger.error("Error getting OSTicket user", user_type=user_type, user_id=user_id, error=str(e))
        
        return None
    
    def create_auth_tokens(self, user_data: Dict[str, Any], session_id: str = None, 
                          ip_address: str = None, user_agent: str = None) -> Dict[str, str]:
        """Create access and refresh tokens for authenticated user"""
        try:
            # Create token payload
            token_payload = {
                "sub": f"{user_data['user_type']}:{user_data['user_id']}",
                "user_type": user_data["user_type"],
                "user_id": user_data["user_id"],
                "iat": datetime.utcnow()
            }
            
            # Add user-specific data to payload
            if user_data["user_type"] == "staff":
                token_payload.update({
                    "username": user_data.get("username"),
                    "email": user_data.get("email"),
                    "dept_id": user_data.get("dept_id"),
                    "isadmin": user_data.get("isadmin", False)
                })
            elif user_data["user_type"] == "user":
                token_payload.update({
                    "email": user_data.get("email"),
                    "name": user_data.get("name")
                })
            
            # Create tokens
            access_token = self.token_manager.create_access_token(token_payload)
            refresh_token = self.token_manager.create_refresh_token(token_payload)
            
            # Store tokens in database
            self._store_auth_token(
                user_data=user_data,
                token=access_token,
                token_type="access",
                session_id=session_id,
                ip_address=ip_address,
                user_agent=user_agent
            )
            
            self._store_auth_token(
                user_data=user_data,
                token=refresh_token,
                token_type="refresh",
                session_id=session_id,
                ip_address=ip_address,
                user_agent=user_agent
            )
            
            return {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "token_type": "bearer"
            }
            
        except Exception as e:
            logger.error("Error creating auth tokens", error=str(e))
            raise AuthenticationError("Failed to create authentication tokens")
    
    def _store_auth_token(self, user_data: Dict[str, Any], token: str, token_type: str,
                         session_id: str = None, ip_address: str = None, user_agent: str = None):
        """Store authentication token in database"""
        try:
            token_hash = self.token_manager.hash_token(token)
            
            # Calculate expiration
            if token_type == "access":
                expires_at = datetime.utcnow() + timedelta(minutes=self.token_manager.access_token_expire_minutes)
            else:
                expires_at = datetime.utcnow() + timedelta(days=self.token_manager.refresh_token_expire_days)
            
            # Create token record
            auth_token = AuthToken(
                user_type=user_data["user_type"],
                user_id=user_data["user_id"],
                token_type=token_type,
                token_hash=token_hash,
                expires_at=expires_at,
                session_id=session_id,
                ip_address=ip_address,
                user_agent=user_agent
            )
            
            self.db.add(auth_token)
            self.db.commit()
            
        except Exception as e:
            logger.error("Error storing auth token", error=str(e))
            self.db.rollback()
            raise

# Create singleton instance
token_manager = TokenManager()