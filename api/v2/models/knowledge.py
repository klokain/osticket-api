"""
Knowledge base models for OSTicket API v2
"""

from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, Enum
from sqlalchemy.orm import relationship
from .base import OSTicketBase

class FAQ(OSTicketBase):
    """FAQ model"""
    
    __tablename__ = "ost_faq"
    
    faq_id = Column(Integer, primary_key=True, autoincrement=True)
    category_id = Column(Integer, nullable=False, default=0)
    ispublished = Column(Boolean, nullable=False, default=False)
    question = Column(String(255), nullable=False)
    answer = Column(Text, nullable=False)
    keywords = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    created = Column(DateTime, nullable=False)
    updated = Column(DateTime, nullable=False)
    
    def __repr__(self):
        return f"<FAQ(faq_id={self.faq_id}, question='{self.question}')>"

class FAQCategory(OSTicketBase):
    """FAQ category model"""
    
    __tablename__ = "ost_faq_category"
    
    category_id = Column(Integer, primary_key=True, autoincrement=True)
    ispublic = Column(Boolean, nullable=False, default=False)
    name = Column(String(125), nullable=False, default="", unique=True)
    description = Column(Text, nullable=False)
    notes = Column(Text, nullable=True)
    created = Column(DateTime, nullable=False)
    updated = Column(DateTime, nullable=False)
    
    def __repr__(self):
        return f"<FAQCategory(category_id={self.category_id}, name='{self.name}')>"

class FAQTopic(OSTicketBase):
    """FAQ topic model"""
    
    __tablename__ = "ost_faq_topic"
    
    faq_id = Column(Integer, primary_key=True)
    topic_id = Column(Integer, primary_key=True)
    
    def __repr__(self):
        return f"<FAQTopic(faq_id={self.faq_id}, topic_id={self.topic_id})>"

class HelpTopic(OSTicketBase):
    """Help topic model"""
    
    __tablename__ = "ost_help_topic"
    
    topic_id = Column(Integer, primary_key=True, autoincrement=True)
    topic_pid = Column(Integer, nullable=False, default=0)
    isactive = Column(Boolean, nullable=False, default=True)
    ispublic = Column(Boolean, nullable=False, default=True)
    noautoresp = Column(Boolean, nullable=False, default=False)
    flags = Column(Integer, nullable=False, default=0)
    status_id = Column(Integer, nullable=False, default=0)
    priority_id = Column(Integer, nullable=False, default=0)
    dept_id = Column(Integer, nullable=False, default=0)
    staff_id = Column(Integer, nullable=False, default=0)
    team_id = Column(Integer, nullable=False, default=0)
    sla_id = Column(Integer, nullable=False, default=0)
    page_id = Column(Integer, nullable=False, default=0)
    sequence_id = Column(Integer, nullable=False, default=0)
    sort = Column(Integer, nullable=False, default=0)
    topic = Column(String(32), nullable=False, default="", unique=True)
    number_format = Column(String(32), nullable=False, default="")
    notes = Column(Text, nullable=True)
    created = Column(DateTime, nullable=False)
    updated = Column(DateTime, nullable=False)
    
    def __repr__(self):
        return f"<HelpTopic(topic_id={self.topic_id}, topic='{self.topic}')>"

class HelpTopicForm(OSTicketBase):
    """Help topic form model"""
    
    __tablename__ = "ost_help_topic_form"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    topic_id = Column(Integer, nullable=False, default=0)
    form_id = Column(Integer, nullable=False, default=0)
    sort = Column(Integer, nullable=False, default=1)
    extra = Column(Text, nullable=True)
    
    def __repr__(self):
        return f"<HelpTopicForm(id={self.id}, topic_id={self.topic_id}, form_id={self.form_id})>"