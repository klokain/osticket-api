"""
Authentication endpoints for OSTicket API v2
"""

from fastapi import APIRouter, Depends, Request
from ..middleware.auth import get_auth, require_auth, require_staff, require_admin, AuthContext
from ..schemas.base import SuccessResponse

router = APIRouter()

@router.get(
    "/me",
    summary="Get Current User/Staff Info",
    description="Get information about the currently authenticated user or staff member"
)
async def get_current_user(auth: AuthContext = Depends(require_auth)):
    """Get current authenticated user information"""
    
    response_data = {
        "auth_type": auth.auth_type,
        "is_authenticated": auth.is_authenticated,
        "is_staff": auth.is_staff,
        "is_admin": auth.is_admin,
    }
    
    if auth.staff:
        response_data["staff"] = {
            "staff_id": auth.staff.staff_id,
            "username": auth.staff.username,
            "firstname": auth.staff.firstname,
            "lastname": auth.staff.lastname,
            "email": auth.staff.email,
            "dept_id": auth.staff.dept_id,
            "role_id": auth.staff.role_id,
            "isactive": auth.staff.isactive,
            "isadmin": auth.staff.isadmin,
        }
    
    if auth.user:
        response_data["user"] = {
            "id": auth.user.id,
            "name": auth.user.name,
            "org_id": auth.user.org_id,
            "status": auth.user.status,
        }
    
    if auth.api_key:
        response_data["api_key"] = {
            "id": auth.api_key.id,
            "can_create_tickets": auth.api_key.can_create_tickets,
            "can_exec_cron": auth.api_key.can_exec_cron,
        }
    
    return response_data

@router.get(
    "/check",
    summary="Check Authentication Status",
    description="Check if the current request is authenticated"
)
async def check_auth(auth: AuthContext = Depends(get_auth)):
    """Check authentication status"""
    
    return {
        "authenticated": auth.is_authenticated,
        "auth_type": auth.auth_type,
        "is_staff": auth.is_staff,
        "is_admin": auth.is_admin,
    }

@router.get(
    "/staff-only",
    summary="Staff Only Endpoint",
    description="Test endpoint that requires staff authentication"
)
async def staff_only_endpoint(auth: AuthContext = Depends(require_staff)):
    """Staff-only test endpoint"""
    
    return SuccessResponse(
        message="Staff access granted",
        data={
            "staff_id": auth.staff.staff_id,
            "username": auth.staff.username,
            "is_admin": auth.is_admin,
        }
    )

@router.get(
    "/admin-only",
    summary="Admin Only Endpoint", 
    description="Test endpoint that requires admin authentication"
)
async def admin_only_endpoint(auth: AuthContext = Depends(require_admin)):
    """Admin-only test endpoint"""
    
    return SuccessResponse(
        message="Admin access granted",
        data={
            "staff_id": auth.staff.staff_id,
            "username": auth.staff.username,
            "is_admin": auth.is_admin,
        }
    )