"""
Forms system models for OSTicket API v2
"""

from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, Enum
from sqlalchemy.orm import relationship
from .base import OSTicketBase

class Form(OSTicketBase):
    """Form model"""
    
    __tablename__ = "ost_form"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    pid = Column(Integer, nullable=True)
    type = Column(String(8), nullable=False, default="G")
    flags = Column(Integer, nullable=False, default=1)
    title = Column(String(255), nullable=False, default="")
    instructions = Column(String(512), nullable=False, default="")
    notes = Column(Text, nullable=True)
    created = Column(DateTime, nullable=False)
    updated = Column(DateTime, nullable=False)
    
    def __repr__(self):
        return f"<Form(id={self.id}, title='{self.title}', type='{self.type}')>"

class FormField(OSTicketBase):
    """Form field model"""
    
    __tablename__ = "ost_form_field"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    form_id = Column(Integer, nullable=False, default=0)
    flags = Column(Integer, nullable=False, default=1)
    type = Column(String(255), nullable=False, default="text")
    label = Column(String(255), nullable=False, default="")
    name = Column(String(64), nullable=False, default="")
    configuration = Column(Text, nullable=True)
    sort = Column(Integer, nullable=False, default=1)
    hint = Column(String(512), nullable=False, default="")
    created = Column(DateTime, nullable=False)
    updated = Column(DateTime, nullable=False)
    
    def __repr__(self):
        return f"<FormField(id={self.id}, form_id={self.form_id}, label='{self.label}', type='{self.type}')>"

class FormEntry(OSTicketBase):
    """Form entry model"""
    
    __tablename__ = "ost_form_entry"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    form_id = Column(Integer, nullable=False, default=0)
    object_id = Column(Integer, nullable=False, default=0)
    object_type = Column(String(1), nullable=False, default="T")
    sort = Column(Integer, nullable=False, default=1)
    extra = Column(Text, nullable=True)
    created = Column(DateTime, nullable=False)
    updated = Column(DateTime, nullable=False)
    
    def __repr__(self):
        return f"<FormEntry(id={self.id}, form_id={self.form_id}, object_id={self.object_id})>"

class FormEntryValues(OSTicketBase):
    """Form entry values model"""
    
    __tablename__ = "ost_form_entry_values"
    
    entry_id = Column(Integer, primary_key=True)
    field_id = Column(Integer, primary_key=True)
    value = Column(Text, nullable=True)
    value_id = Column(Integer, nullable=True)
    
    def __repr__(self):
        return f"<FormEntryValues(entry_id={self.entry_id}, field_id={self.field_id})>"