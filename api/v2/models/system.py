"""
Additional system models for OSTicket API v2
"""

from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, Enum, LargeBinary
from sqlalchemy.orm import relationship
from .base import OSTicketBase

class Queue(OSTicketBase):
    """Queue model"""
    
    __tablename__ = "ost_queue"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    parent_id = Column(Integer, nullable=False, default=0)
    columns_id = Column(Integer, nullable=False, default=0)
    sort_id = Column(Integer, nullable=False, default=0)
    flags = Column(Integer, nullable=False, default=0)
    staff_id = Column(Integer, nullable=False, default=0)
    title = Column(String(60), nullable=False, default="")
    config = Column(Text, nullable=True)
    filter = Column(String(64), nullable=False, default="")
    root = Column(String(32), nullable=False, default="T")
    path = Column(String(80), nullable=False, default="/")
    created = Column(DateTime, nullable=False)
    updated = Column(DateTime, nullable=False)
    
    def __repr__(self):
        return f"<Queue(id={self.id}, title='{self.title}')>"

class QueueColumn(OSTicketBase):
    """Queue column model"""
    
    __tablename__ = "ost_queue_column"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(64), nullable=False)
    primary = Column(String(64), nullable=False)
    secondary = Column(String(64), nullable=True)
    filter = Column(String(32), nullable=True)
    truncate = Column(String(16), nullable=True)
    annotations = Column(Text, nullable=True)
    conditions = Column(Text, nullable=True)
    extra = Column(Text, nullable=True)
    
    def __repr__(self):
        return f"<QueueColumn(id={self.id}, name='{self.name}')>"

class QueueColumns(OSTicketBase):
    """Queue columns model"""
    
    __tablename__ = "ost_queue_columns"
    
    queue_id = Column(Integer, primary_key=True)
    column_id = Column(Integer, primary_key=True)
    staff_id = Column(Integer, primary_key=True)
    bits = Column(Integer, nullable=False, default=0)
    sort = Column(Integer, nullable=False, default=1)
    heading = Column(String(64), nullable=True)
    width = Column(Integer, nullable=False, default=100)
    
    def __repr__(self):
        return f"<QueueColumns(queue_id={self.queue_id}, column_id={self.column_id}, staff_id={self.staff_id})>"

class QueueConfig(OSTicketBase):
    """Queue configuration model"""
    
    __tablename__ = "ost_queue_config"
    
    queue_id = Column(Integer, primary_key=True)
    staff_id = Column(Integer, primary_key=True)
    setting = Column(Text, nullable=True)
    updated = Column(DateTime, nullable=False)
    
    def __repr__(self):
        return f"<QueueConfig(queue_id={self.queue_id}, staff_id={self.staff_id})>"

class QueueExport(OSTicketBase):
    """Queue export model"""
    
    __tablename__ = "ost_queue_export"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    queue_id = Column(Integer, nullable=False, default=0)
    path = Column(String(64), nullable=False, default="")
    heading = Column(String(64), nullable=True)
    sort = Column(Integer, nullable=False, default=1)
    
    def __repr__(self):
        return f"<QueueExport(id={self.id}, queue_id={self.queue_id}, path='{self.path}')>"

class QueueSort(OSTicketBase):
    """Queue sort model"""
    
    __tablename__ = "ost_queue_sort"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    root = Column(String(32), nullable=False, default="T")
    name = Column(String(64), nullable=False, default="")
    columns = Column(Text, nullable=True)
    updated = Column(DateTime, nullable=False)
    
    def __repr__(self):
        return f"<QueueSort(id={self.id}, name='{self.name}', root='{self.root}')>"

class QueueSorts(OSTicketBase):
    """Queue sorts model"""
    
    __tablename__ = "ost_queue_sorts"
    
    queue_id = Column(Integer, primary_key=True)
    sort_id = Column(Integer, primary_key=True)
    bits = Column(Integer, nullable=False, default=0)
    sort = Column(Integer, nullable=False, default=0)
    
    def __repr__(self):
        return f"<QueueSorts(queue_id={self.queue_id}, sort_id={self.sort_id})>"

class Filter(OSTicketBase):
    """Filter model"""
    
    __tablename__ = "ost_filter"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    execorder = Column(Integer, nullable=False, default=99)
    isactive = Column(Boolean, nullable=False, default=True)
    flags = Column(Integer, nullable=False, default=0)
    status = Column(Integer, nullable=False, default=0)
    match_all_rules = Column(Boolean, nullable=False, default=False)
    stop_onmatch = Column(Boolean, nullable=False, default=False)
    target = Column(String(8), nullable=False, default="")
    email_id = Column(Integer, nullable=False, default=0)
    priority_id = Column(Integer, nullable=False, default=0)
    dept_id = Column(Integer, nullable=False, default=0)
    staff_id = Column(Integer, nullable=False, default=0)
    team_id = Column(Integer, nullable=False, default=0)
    sla_id = Column(Integer, nullable=False, default=0)
    topic_id = Column(Integer, nullable=False, default=0)
    name = Column(String(32), nullable=False, default="", unique=True)
    notes = Column(Text, nullable=True)
    created = Column(DateTime, nullable=False)
    updated = Column(DateTime, nullable=False)
    
    def __repr__(self):
        return f"<Filter(id={self.id}, name='{self.name}')>"

class FilterRule(OSTicketBase):
    """Filter rule model"""
    
    __tablename__ = "ost_filter_rule"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    filter_id = Column(Integer, nullable=False, default=0)
    what = Column(String(32), nullable=False, default="")
    how = Column(Enum('equal', 'not_equal', 'contains', 'dn_contain', 'starts', 'ends', 'match', 'not_match', name='filter_rule_how'), nullable=False, default='equal')
    val = Column(String(255), nullable=False, default="")
    
    def __repr__(self):
        return f"<FilterRule(id={self.id}, filter_id={self.filter_id}, what='{self.what}')>"

class FilterAction(OSTicketBase):
    """Filter action model"""
    
    __tablename__ = "ost_filter_action"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    filter_id = Column(Integer, nullable=False, default=0)
    sort = Column(Integer, nullable=False, default=0)
    type = Column(String(24), nullable=False, default="")
    configuration = Column(Text, nullable=True)
    updated = Column(DateTime, nullable=False)
    created = Column(DateTime, nullable=False)
    
    def __repr__(self):
        return f"<FilterAction(id={self.id}, filter_id={self.filter_id}, type='{self.type}')>"

class Plugin(OSTicketBase):
    """Plugin model"""
    
    __tablename__ = "ost_plugin"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(30), nullable=False)
    install_path = Column(String(60), nullable=False)
    isphar = Column(Boolean, nullable=False, default=False)
    isactive = Column(Boolean, nullable=False, default=False)
    version = Column(String(64), nullable=True)
    installed = Column(DateTime, nullable=False)
    
    def __repr__(self):
        return f"<Plugin(id={self.id}, name='{self.name}', version='{self.version}')>"

class PluginInstance(OSTicketBase):
    """Plugin instance model"""
    
    __tablename__ = "ost_plugin_instance"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    plugin_id = Column(Integer, nullable=False)
    flags = Column(Integer, nullable=False, default=0)
    name = Column(String(255), nullable=False, default="")
    instance = Column(String(128), nullable=True)
    config = Column(Text, nullable=True)
    extra = Column(Text, nullable=True)
    created = Column(DateTime, nullable=False)
    updated = Column(DateTime, nullable=False)
    
    def __repr__(self):
        return f"<PluginInstance(id={self.id}, plugin_id={self.plugin_id}, name='{self.name}')>"

class Task(OSTicketBase):
    """Task model"""
    
    __tablename__ = "ost_task"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    object_id = Column(Integer, nullable=False, default=0)
    object_type = Column(String(1), nullable=False, default="T")
    number = Column(String(20), nullable=True)
    flags = Column(Integer, nullable=False, default=0)
    duedate = Column(DateTime, nullable=True)
    closed = Column(DateTime, nullable=True)
    created = Column(DateTime, nullable=False)
    updated = Column(DateTime, nullable=False)
    
    def __repr__(self):
        return f"<Task(id={self.id}, number='{self.number}', object_id={self.object_id})>"

class TaskCData(OSTicketBase):
    """Task custom data model"""
    
    __tablename__ = "ost_task__cdata"
    
    task_id = Column(Integer, primary_key=True)
    title = Column(Text, nullable=True)
    description = Column(Text, nullable=True)
    
    def __repr__(self):
        return f"<TaskCData(task_id={self.task_id})>"

class List(OSTicketBase):
    """List model"""
    
    __tablename__ = "ost_list"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False, default="")
    name_plural = Column(String(255), nullable=False, default="")
    label = Column(String(255), nullable=False, default="")
    type = Column(String(16), nullable=True, default=None)
    configuration = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    created = Column(DateTime, nullable=False)
    updated = Column(DateTime, nullable=False)
    
    def __repr__(self):
        return f"<List(id={self.id}, name='{self.name}')>"

class ListItems(OSTicketBase):
    """List items model"""
    
    __tablename__ = "ost_list_items"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    list_id = Column(Integer, nullable=False, default=0)
    status = Column(Integer, nullable=False, default=1)
    value = Column(String(255), nullable=False, default="")
    extra = Column(String(255), nullable=True)
    sort = Column(Integer, nullable=False, default=1)
    properties = Column(Text, nullable=True)
    
    def __repr__(self):
        return f"<ListItems(id={self.id}, list_id={self.list_id}, value='{self.value}')>"