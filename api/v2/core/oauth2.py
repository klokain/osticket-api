"""
OAuth2/OIDC providers integration for OSTicket API v2
IdP provides identity verification only - roles managed internally
"""

import json
import secrets
import base64
from typing import Dict, Any, Optional
from urllib.parse import urlencode
import httpx
from fastapi import HTTPException
from jose import jwt
from ..core.config import settings
import structlog

logger = structlog.get_logger()

class OAuth2Provider:
    """Base OAuth2/OIDC provider"""
    
    def __init__(self, provider_name: str):
        self.provider_name = provider_name
        self.client = httpx.AsyncClient()
    
    async def get_authorization_url(self, redirect_uri: str, state: str = None) -> str:
        """Get authorization URL for OAuth2 flow"""
        raise NotImplementedError
    
    async def exchange_code_for_token(self, code: str, redirect_uri: str, state: str = None) -> Dict[str, Any]:
        """Exchange authorization code for access token"""
        raise NotImplementedError
    
    async def get_user_info(self, access_token: str) -> Dict[str, Any]:
        """Get user information from provider"""
        raise NotImplementedError
    
    def generate_state(self) -> str:
        """Generate secure state parameter"""
        return base64.urlsafe_b64encode(secrets.token_bytes(32)).decode('utf-8')

class KeycloakProvider(OAuth2Provider):
    """Keycloak OAuth2/OIDC provider"""
    
    def __init__(self):
        super().__init__("keycloak")
        self.server_url = settings.KEYCLOAK_SERVER_URL
        self.realm = settings.KEYCLOAK_REALM
        self.client_id = settings.KEYCLOAK_CLIENT_ID
        self.client_secret = settings.KEYCLOAK_CLIENT_SECRET
        
        if not all([self.server_url, self.client_id, self.client_secret]):
            logger.warning("Keycloak configuration incomplete")
            return
        
        # Build URLs
        self.realm_url = f"{self.server_url}/realms/{self.realm}"
        self.auth_url = f"{self.realm_url}/protocol/openid-connect/auth"
        self.token_url = f"{self.realm_url}/protocol/openid-connect/token"
        self.userinfo_url = f"{self.realm_url}/protocol/openid-connect/userinfo"
        self.discovery_url = f"{self.realm_url}/.well-known/openid_configuration"
    
    async def get_authorization_url(self, redirect_uri: str, state: str = None) -> str:
        """Get Keycloak authorization URL"""
        if not state:
            state = self.generate_state()
        
        params = {
            'client_id': self.client_id,
            'response_type': 'code',
            'scope': 'openid email profile',
            'redirect_uri': redirect_uri,
            'state': state,
        }
        
        auth_url = f"{self.auth_url}?{urlencode(params)}"
        logger.debug("Generated Keycloak auth URL", url=auth_url, state=state)
        return auth_url
    
    async def exchange_code_for_token(self, code: str, redirect_uri: str, state: str = None) -> Dict[str, Any]:
        """Exchange code for Keycloak tokens"""
        try:
            data = {
                'grant_type': 'authorization_code',
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'code': code,
                'redirect_uri': redirect_uri,
            }
            
            headers = {'Content-Type': 'application/x-www-form-urlencoded'}
            
            async with self.client as client:
                response = await client.post(self.token_url, data=data, headers=headers)
                response.raise_for_status()
                
                token_data = response.json()
                logger.debug("Keycloak token exchange successful")
                return token_data
                
        except httpx.HTTPError as e:
            logger.error("Keycloak token exchange failed", error=str(e))
            raise HTTPException(status_code=400, detail="Token exchange failed")
    
    async def get_user_info(self, access_token: str) -> Dict[str, Any]:
        """Get user info from Keycloak"""
        try:
            headers = {'Authorization': f'Bearer {access_token}'}
            
            async with self.client as client:
                response = await client.get(self.userinfo_url, headers=headers)
                response.raise_for_status()
                
                user_data = response.json()
                logger.debug("Keycloak user info retrieved", email=user_data.get("email"))
                return user_data
                
        except httpx.HTTPError as e:
            logger.error("Keycloak user info retrieval failed", error=str(e))
            raise HTTPException(status_code=400, detail="User info retrieval failed")
    
    def verify_id_token(self, id_token: str) -> Dict[str, Any]:
        """Verify Keycloak ID token (simplified - production should verify signature)"""
        try:
            # NOTE: In production, you should verify the signature against Keycloak's public keys
            # For development, we'll decode without verification (INSECURE)
            payload = jwt.get_unverified_claims(id_token)
            
            # Basic validation
            if payload.get('iss') != self.realm_url:
                raise ValueError("Invalid issuer")
            
            if payload.get('aud') != self.client_id:
                raise ValueError("Invalid audience")
            
            logger.debug("Keycloak ID token verified", sub=payload.get("sub"))
            return payload
            
        except Exception as e:
            logger.error("Keycloak ID token verification failed", error=str(e))
            raise HTTPException(status_code=400, detail="Invalid ID token")

class MicrosoftProvider(OAuth2Provider):
    """Microsoft Entra (Azure AD) OAuth2/OIDC provider"""
    
    def __init__(self):
        super().__init__("microsoft")
        self.tenant_id = settings.MICROSOFT_TENANT_ID
        self.client_id = settings.MICROSOFT_CLIENT_ID
        self.client_secret = settings.MICROSOFT_CLIENT_SECRET
        
        if not all([self.tenant_id, self.client_id, self.client_secret]):
            logger.warning("Microsoft Entra configuration incomplete")
            return
        
        # Build URLs
        self.auth_url = f"https://login.microsoftonline.com/{self.tenant_id}/oauth2/v2.0/authorize"
        self.token_url = f"https://login.microsoftonline.com/{self.tenant_id}/oauth2/v2.0/token"
        self.userinfo_url = "https://graph.microsoft.com/v1.0/me"
        self.discovery_url = f"https://login.microsoftonline.com/{self.tenant_id}/v2.0/.well-known/openid_configuration"
    
    async def get_authorization_url(self, redirect_uri: str, state: str = None) -> str:
        """Get Microsoft authorization URL"""
        if not state:
            state = self.generate_state()
        
        params = {
            'client_id': self.client_id,
            'response_type': 'code',
            'scope': 'openid email profile User.Read',
            'redirect_uri': redirect_uri,
            'state': state,
            'response_mode': 'query'
        }
        
        auth_url = f"{self.auth_url}?{urlencode(params)}"
        logger.debug("Generated Microsoft auth URL", url=auth_url, state=state)
        return auth_url
    
    async def exchange_code_for_token(self, code: str, redirect_uri: str, state: str = None) -> Dict[str, Any]:
        """Exchange code for Microsoft tokens"""
        try:
            data = {
                'grant_type': 'authorization_code',
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'code': code,
                'redirect_uri': redirect_uri,
                'scope': 'openid email profile User.Read'
            }
            
            headers = {'Content-Type': 'application/x-www-form-urlencoded'}
            
            async with self.client as client:
                response = await client.post(self.token_url, data=data, headers=headers)
                response.raise_for_status()
                
                token_data = response.json()
                logger.debug("Microsoft token exchange successful")
                return token_data
                
        except httpx.HTTPError as e:
            logger.error("Microsoft token exchange failed", error=str(e))
            raise HTTPException(status_code=400, detail="Token exchange failed")
    
    async def get_user_info(self, access_token: str) -> Dict[str, Any]:
        """Get user info from Microsoft Graph"""
        try:
            headers = {'Authorization': f'Bearer {access_token}'}
            
            async with self.client as client:
                response = await client.get(self.userinfo_url, headers=headers)
                response.raise_for_status()
                
                user_data = response.json()
                
                # Normalize Microsoft Graph response to standard format
                normalized_data = {
                    'id': user_data.get('id'),
                    'email': user_data.get('mail') or user_data.get('userPrincipalName'),
                    'name': user_data.get('displayName'),
                    'given_name': user_data.get('givenName'),
                    'family_name': user_data.get('surname'),
                    'username': user_data.get('userPrincipalName'),
                    'microsoft_user_data': user_data  # Store full response
                }
                
                logger.debug("Microsoft user info retrieved", email=normalized_data.get("email"))
                return normalized_data
                
        except httpx.HTTPError as e:
            logger.error("Microsoft user info retrieval failed", error=str(e))
            raise HTTPException(status_code=400, detail="User info retrieval failed")

class OAuth2Manager:
    """Manage OAuth2/OIDC providers"""
    
    def __init__(self):
        self.providers = {}
        self._init_providers()
    
    def _init_providers(self):
        """Initialize available OAuth2 providers"""
        if settings.KEYCLOAK_ENABLED and settings.KEYCLOAK_SERVER_URL:
            self.providers['keycloak'] = KeycloakProvider()
            logger.info("Keycloak provider initialized")
        
        if settings.MICROSOFT_ENABLED and settings.MICROSOFT_TENANT_ID:
            self.providers['microsoft'] = MicrosoftProvider()
            logger.info("Microsoft Entra provider initialized")
        
        logger.info("OAuth2 manager initialized", providers=list(self.providers.keys()))
    
    def get_provider(self, provider_name: str) -> Optional[OAuth2Provider]:
        """Get OAuth2 provider by name"""
        provider = self.providers.get(provider_name)
        if not provider:
            logger.warning("OAuth2 provider not found", provider=provider_name)
        return provider
    
    def is_provider_enabled(self, provider_name: str) -> bool:
        """Check if provider is enabled"""
        return provider_name in self.providers
    
    def get_enabled_providers(self) -> Dict[str, OAuth2Provider]:
        """Get all enabled providers"""
        return self.providers.copy()

# Create singleton instance
oauth2_manager = OAuth2Manager()