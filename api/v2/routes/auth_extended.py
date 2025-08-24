"""
Extended authentication endpoints for OSTicket API v2
Multi-provider authentication: OSTicket native, Keycloak, Microsoft Entra
"""

from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from ..core.database import get_db
from ..core.auth import AuthenticationService
from ..core.exceptions import AuthenticationError
from ..core.oauth2 import oauth2_manager, OAuth2Provider
from ..models.auth import ExternalIdentity
from ..middleware.auth import require_auth, get_user_info_dict
import structlog

logger = structlog.get_logger()
router = APIRouter(prefix="/auth", tags=["extended-authentication"])

# Request/Response Models
class StaffLoginRequest(BaseModel):
    username: str
    password: str

class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str

class AuthTokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int

class UserInfoResponse(BaseModel):
    user_type: str
    user_id: int
    email: Optional[str] = None
    username: Optional[str] = None
    name: Optional[str] = None
    isadmin: Optional[bool] = None
    dept_id: Optional[int] = None

# OSTicket Native Authentication Endpoints

@router.post("/staff/login", response_model=AuthTokenResponse)
async def staff_login(
    credentials: StaffLoginRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    """Authenticate staff user with username/password"""
    try:
        auth_service = AuthenticationService(db)
        
        # Authenticate staff
        auth_result = auth_service.authenticate_staff(
            credentials.username, 
            credentials.password
        )
        
        if not auth_result:
            logger.warning("Staff login failed", username=credentials.username)
            raise AuthenticationError("Invalid username or password")
        
        # Create tokens
        tokens = auth_service.create_auth_tokens(
            user_data=auth_result,
            ip_address=_get_client_ip(request),
            user_agent=request.headers.get("User-Agent")
        )
        
        logger.info("Staff login successful", 
                   staff_id=auth_result["user_id"], 
                   username=auth_result["username"])
        
        return AuthTokenResponse(
            access_token=tokens["access_token"],
            refresh_token=tokens["refresh_token"],
            token_type=tokens["token_type"],
            expires_in=30 * 60  # 30 minutes
        )
        
    except AuthenticationError:
        raise
    except Exception as e:
        logger.error("Staff login error", error=str(e))
        raise AuthenticationError("Login failed")

@router.post("/user/login", response_model=AuthTokenResponse) 
async def user_login(
    credentials: UserLoginRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    """Authenticate end user with email/password"""
    try:
        auth_service = AuthenticationService(db)
        
        # Authenticate user
        auth_result = auth_service.authenticate_user(
            credentials.email,
            credentials.password
        )
        
        if not auth_result:
            logger.warning("User login failed", email=credentials.email)
            raise AuthenticationError("Invalid email or password")
        
        # Create tokens
        tokens = auth_service.create_auth_tokens(
            user_data=auth_result,
            ip_address=_get_client_ip(request),
            user_agent=request.headers.get("User-Agent")
        )
        
        logger.info("User login successful", 
                   user_id=auth_result["user_id"],
                   email=auth_result["email"])
        
        return AuthTokenResponse(
            access_token=tokens["access_token"],
            refresh_token=tokens["refresh_token"], 
            token_type=tokens["token_type"],
            expires_in=30 * 60  # 30 minutes
        )
        
    except AuthenticationError:
        raise
    except Exception as e:
        logger.error("User login error", error=str(e))
        raise AuthenticationError("Login failed")

# OAuth2/OIDC Endpoints

@router.get("/oauth2/{provider}/login")
async def oauth2_login(
    provider: str,
    request: Request,
    return_url: Optional[str] = None
):
    """Initiate OAuth2 login with external provider"""
    try:
        oauth_provider = oauth2_manager.get_provider(provider)
        if not oauth_provider:
            from ..core.exceptions import NotFoundError
            raise NotFoundError("OAuth Provider", provider)
        
        # Build redirect URI
        redirect_uri = str(request.url_for("oauth2_callback", provider=provider))
        
        # Generate state parameter (optionally include return URL)
        state = oauth_provider.generate_state()
        if return_url:
            # Store return URL in state (in production, use encrypted state)
            state = f"{state}:{return_url}"
        
        # Get authorization URL
        auth_url = await oauth_provider.get_authorization_url(redirect_uri, state)
        
        logger.info("OAuth2 login initiated", provider=provider, state=state[:16] + "...")
        return RedirectResponse(url=auth_url)
        
    except Exception as e:
        logger.error("OAuth2 login initiation failed", provider=provider, error=str(e))
        from ..core.exceptions import APIException
        raise APIException("OAuth2 login failed")

@router.get("/oauth2/{provider}/callback")
async def oauth2_callback(
    provider: str,
    request: Request,
    code: Optional[str] = None,
    state: Optional[str] = None,
    error: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Handle OAuth2 callback from external provider"""
    try:
        if error:
            logger.warning("OAuth2 callback received error", provider=provider, error=error)
            from ..core.exceptions import ValidationError
            raise ValidationError(f"OAuth2 authentication failed: {error}")
        
        if not code:
            from ..core.exceptions import ValidationError
            raise ValidationError("Authorization code not provided")
        
        oauth_provider = oauth2_manager.get_provider(provider)
        if not oauth_provider:
            from ..core.exceptions import NotFoundError
            raise NotFoundError("OAuth Provider", provider)
        
        # Exchange code for tokens
        redirect_uri = str(request.url_for("oauth2_callback", provider=provider))
        token_data = await oauth_provider.exchange_code_for_token(code, redirect_uri, state)
        
        # Get user information from provider
        user_data = await oauth_provider.get_user_info(token_data["access_token"])
        
        # Authenticate using external identity (IdP verifies identity, roles internal)
        auth_service = AuthenticationService(db)
        auth_result = auth_service.authenticate_external_identity(provider, user_data)
        
        if not auth_result:
            # No mapping exists - return error or redirect to mapping page
            logger.warning("External identity not mapped", 
                          provider=provider, 
                          external_user_id=user_data.get("id"))
            raise AuthenticationError("External identity not linked to OSTicket account")
        
        # Create JWT tokens for the mapped OSTicket user
        tokens = auth_service.create_auth_tokens(
            user_data=auth_result,
            ip_address=_get_client_ip(request),
            user_agent=request.headers.get("User-Agent")
        )
        
        logger.info("OAuth2 authentication successful",
                   provider=provider,
                   external_user_id=user_data.get("id"),
                   osticket_user_type=auth_result["user_type"],
                   osticket_user_id=auth_result["user_id"])
        
        # Extract return URL from state if present
        return_url = None
        if state and ":" in state:
            state_parts = state.split(":", 1)
            if len(state_parts) == 2:
                return_url = state_parts[1]
        
        # For now, return tokens as JSON (in production, might set cookies and redirect)
        response_data = {
            "access_token": tokens["access_token"],
            "refresh_token": tokens["refresh_token"],
            "token_type": tokens["token_type"],
            "user_type": auth_result["user_type"],
            "return_url": return_url
        }
        
        return response_data
        
    except (AuthenticationError, ValidationError, NotFoundError):
        raise
    except Exception as e:
        logger.error("OAuth2 callback error", provider=provider, error=str(e))
        from ..core.exceptions import APIException
        raise APIException("OAuth2 authentication failed")

# Common Authentication Endpoints

@router.get("/userinfo", response_model=UserInfoResponse)
async def get_current_user_info(user_info: dict = Depends(get_user_info_dict)):
    """Get current authenticated user information (JWT token based)"""
    try:
        response = UserInfoResponse(
            user_type=user_info["user_type"],
            user_id=user_info["user_id"],
            email=user_info.get("email"),
            username=user_info.get("username"),
            name=user_info.get("name"),
            isadmin=user_info.get("isadmin"),
            dept_id=user_info.get("dept_id")
        )
        
        return response
        
    except Exception as e:
        logger.error("Get current user error", error=str(e))
        from ..core.exceptions import APIException
        raise APIException("Failed to get user information")

@router.post("/logout")
async def logout(request: Request, user_info: dict = Depends(require_auth)):
    """Logout current user and invalidate tokens"""
    try:
        # TODO: Invalidate current JWT token in database
        # This would involve marking the AuthToken as inactive
        
        logger.info("User logged out", 
                   user_type=user_info["user_type"],
                   user_id=user_info["user_id"])
        
        return {"message": "Logged out successfully"}
        
    except Exception as e:
        logger.error("Logout error", error=str(e))
        from ..core.exceptions import APIException
        raise APIException("Logout failed")

@router.get("/providers")
async def get_enabled_providers():
    """Get list of enabled authentication providers"""
    try:
        providers = oauth2_manager.get_enabled_providers()
        
        provider_info = {}
        for name, provider in providers.items():
            provider_info[name] = {
                "name": name,
                "login_url": f"/api/v2/auth/oauth2/{name}/login"
            }
        
        # Add OSTicket native authentication
        provider_info["osticket"] = {
            "name": "osticket",
            "staff_login_url": "/api/v2/auth/staff/login",
            "user_login_url": "/api/v2/auth/user/login"
        }
        
        return {
            "providers": provider_info,
            "native_auth_enabled": True
        }
        
    except Exception as e:
        logger.error("Get providers error", error=str(e))
        from ..core.exceptions import APIException
        raise APIException("Failed to get provider information")

# Helper Functions

def _get_client_ip(request: Request) -> str:
    """Get client IP address from request"""
    # Check for forwarded headers first (reverse proxy)
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    
    forwarded = request.headers.get("X-Forwarded")
    if forwarded:
        return forwarded.strip()
    
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip.strip()
    
    # Fall back to direct client IP
    if hasattr(request.client, 'host'):
        return request.client.host
    
    return "unknown"