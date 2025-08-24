"""
Base schema classes for OSTicket API v2
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Any, Dict, List, Optional
from datetime import datetime

class OSTicketBase(BaseModel):
    """Base schema for OSTicket models"""
    
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        use_enum_values=True,
        validate_assignment=True,
        str_strip_whitespace=True
    )

class TimestampSchema(BaseModel):
    """Schema for timestamp fields"""
    created: datetime
    updated: datetime

class PaginationParams(BaseModel):
    """Pagination parameters"""
    page: int = Field(default=1, ge=1, description="Page number")
    limit: int = Field(default=20, ge=1, le=100, description="Items per page")
    
    @property
    def offset(self) -> int:
        return (self.page - 1) * self.limit

class PaginationMeta(BaseModel):
    """Pagination metadata"""
    page: int
    limit: int
    total: int
    pages: int
    has_next: bool
    has_prev: bool

class PaginatedResponse(BaseModel):
    """Generic paginated response"""
    data: List[Any]
    meta: PaginationMeta
    
class ErrorDetail(BaseModel):
    """Error detail schema"""
    field: Optional[str] = None
    message: str
    type: Optional[str] = None
    input: Optional[Any] = None

class ErrorResponse(BaseModel):
    """Error response schema"""
    error: Dict[str, Any] = Field(
        description="Error information",
        example={
            "code": "VALIDATION_ERROR",
            "message": "Request validation failed",
            "timestamp": "2025-01-24T12:00:00Z",
            "request_id": "req_123456789",
            "path": "/api/v2/tickets",
            "details": {
                "validation_errors": [
                    {
                        "field": "subject",
                        "message": "Field required",
                        "type": "missing"
                    }
                ]
            }
        }
    )

class HealthResponse(BaseModel):
    """Health check response schema"""
    status: str = Field(description="Service health status")
    timestamp: datetime = Field(description="Response timestamp")
    version: str = Field(description="API version")
    database: Optional[Dict[str, Any]] = Field(description="Database health info")

class SuccessResponse(BaseModel):
    """Generic success response"""
    success: bool = True
    message: str
    data: Optional[Dict[str, Any]] = None