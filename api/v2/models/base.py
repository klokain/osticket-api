"""
Base model classes for OSTicket API v2

Provides common functionality and patterns for all database models.
"""

from sqlalchemy import Column, Integer, DateTime, func
from sqlalchemy.ext.declarative import as_declarative, declared_attr
from ..core.database import get_table_name

@as_declarative()
class Base:
    """Base class for all database models"""
    
    # Generate __tablename__ automatically
    @declared_attr
    def __tablename__(cls):
        return get_table_name(cls.__name__.lower())
    
    # Common columns
    id = Column(Integer, primary_key=True, index=True)

class TimestampMixin:
    """Mixin to add created/updated timestamps"""
    
    created = Column(DateTime, nullable=False, server_default=func.now())
    updated = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

class OSTicketBase(Base):
    """Base class for OSTicket models with proper table naming"""
    
    __abstract__ = True
    
    @declared_attr
    def __tablename__(cls):
        # Handle special table name mappings
        table_mappings = {
            'apikey': 'api_key',
            'ticketstatus': 'ticket_status', 
            'ticketpriority': 'ticket_priority',
            'useremail': 'user_email',
            'useraccount': 'user_account',
            'staffdeptaccess': 'staff_dept_access',
            'threadcollaborator': 'thread_collaborator',
            'faqcategory': 'faq_category',
            'faqtopic': 'faq_topic',
        }
        
        class_name = cls.__name__.lower()
        table_name = table_mappings.get(class_name, class_name)
        return get_table_name(table_name)