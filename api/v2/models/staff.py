"""
Staff, department, and team related database models for OSTicket API v2
"""

from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, ForeignKey, Enum
from sqlalchemy.orm import relationship
from .base import OSTicketBase

class Staff(OSTicketBase):
    """Staff model"""
    
    __tablename__ = "ost_staff"
    
    staff_id = Column(Integer, primary_key=True, autoincrement=True)
    dept_id = Column(Integer, nullable=False, default=0)
    role_id = Column(Integer, nullable=False, default=0)
    username = Column(String(32), nullable=False, default="", unique=True)
    firstname = Column(String(32), nullable=True)
    lastname = Column(String(32), nullable=True)
    passwd = Column(String(128), nullable=True)
    backend = Column(String(32), nullable=True)
    email = Column(String(255), nullable=True)
    phone = Column(String(24), nullable=False, default="")
    phone_ext = Column(String(6), nullable=True)
    mobile = Column(String(24), nullable=False, default="")
    signature = Column(Text, nullable=False)
    lang = Column(String(16), nullable=True)
    timezone = Column(String(64), nullable=True)
    locale = Column(String(16), nullable=True)
    notes = Column(Text, nullable=True)
    isactive = Column(Boolean, nullable=False, default=True)
    isadmin = Column(Boolean, nullable=False, default=False)
    isvisible = Column(Boolean, nullable=False, default=True)
    onvacation = Column(Boolean, nullable=False, default=False)
    assigned_only = Column(Boolean, nullable=False, default=False)
    show_assigned_tickets = Column(Boolean, nullable=False, default=False)
    change_passwd = Column(Boolean, nullable=False, default=False)
    max_page_size = Column(Integer, nullable=False, default=0)
    auto_refresh_rate = Column(Integer, nullable=False, default=0)
    default_signature_type = Column(Enum('none', 'mine', 'dept', name='staff_signature_type'), nullable=False, default='none')
    default_paper_size = Column(Enum('Letter', 'Legal', 'Ledger', 'A4', 'A3', name='staff_paper_size'), nullable=False, default='Letter')
    extra = Column(Text, nullable=True)
    permissions = Column(Text, nullable=True)
    created = Column(DateTime, nullable=False)
    lastlogin = Column(DateTime, nullable=True)
    passwdreset = Column(DateTime, nullable=True)
    updated = Column(DateTime, nullable=False)
    
    def __repr__(self):
        return f"<Staff(staff_id={self.staff_id}, username='{self.username}', email='{self.email}')>"

class Department(OSTicketBase):
    """Department model"""
    
    __tablename__ = "ost_department"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    pid = Column(Integer, nullable=True, default=None)  # Parent department
    tpl_id = Column(Integer, nullable=False, default=0)
    sla_id = Column(Integer, nullable=False, default=0)
    schedule_id = Column(Integer, nullable=False, default=0)
    email_id = Column(Integer, nullable=False, default=0)
    autoresp_email_id = Column(Integer, nullable=False, default=0)
    manager_id = Column(Integer, nullable=False, default=0)
    flags = Column(Integer, nullable=False, default=0)
    name = Column(String(128), nullable=False, default="")
    signature = Column(Text, nullable=False)
    ispublic = Column(Boolean, nullable=False, default=True)
    group_membership = Column(Boolean, nullable=False, default=False)
    ticket_auto_response = Column(Boolean, nullable=False, default=True)
    message_auto_response = Column(Boolean, nullable=False, default=False)
    path = Column(String(128), nullable=False, default="/")
    updated = Column(DateTime, nullable=False)
    created = Column(DateTime, nullable=False)
    
    def __repr__(self):
        return f"<Department(id={self.id}, name='{self.name}')>"

class Team(OSTicketBase):
    """Team model"""
    
    __tablename__ = "ost_team"
    
    team_id = Column(Integer, primary_key=True, autoincrement=True)
    lead_id = Column(Integer, nullable=False, default=0)
    flags = Column(Integer, nullable=False, default=1)
    name = Column(String(125), nullable=False, default="", unique=True)
    notes = Column(Text, nullable=True)
    created = Column(DateTime, nullable=False)
    updated = Column(DateTime, nullable=False)
    
    def __repr__(self):
        return f"<Team(team_id={self.team_id}, name='{self.name}')>"

class TeamMember(OSTicketBase):
    """Team member association model"""
    
    __tablename__ = "ost_team_member"
    
    team_id = Column(Integer, primary_key=True)
    staff_id = Column(Integer, primary_key=True)
    flags = Column(Integer, nullable=False, default=0)
    
    def __repr__(self):
        return f"<TeamMember(team_id={self.team_id}, staff_id={self.staff_id})>"

class Role(OSTicketBase):
    """Role model for permissions"""
    
    __tablename__ = "ost_role"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    flags = Column(Integer, nullable=False, default=1)
    name = Column(String(64), nullable=True, unique=True)
    permissions = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    created = Column(DateTime, nullable=False)
    updated = Column(DateTime, nullable=False)
    
    def __repr__(self):
        return f"<Role(id={self.id}, name='{self.name}')>"

class StaffDeptAccess(OSTicketBase):
    """Staff department access model"""
    
    __tablename__ = "ost_staff_dept_access"
    
    staff_id = Column(Integer, primary_key=True)
    dept_id = Column(Integer, primary_key=True)
    role_id = Column(Integer, nullable=False, default=0)
    flags = Column(Integer, nullable=False, default=1)
    
    def __repr__(self):
        return f"<StaffDeptAccess(staff_id={self.staff_id}, dept_id={self.dept_id})>"

class SLA(OSTicketBase):
    """SLA (Service Level Agreement) model"""
    
    __tablename__ = "ost_sla"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    schedule_id = Column(Integer, nullable=False, default=0)
    flags = Column(Integer, nullable=False, default=3)
    grace_period = Column(Integer, nullable=False, default=0)
    name = Column(String(64), nullable=False, default="", unique=True)
    notes = Column(Text, nullable=True)
    created = Column(DateTime, nullable=False)
    updated = Column(DateTime, nullable=False)
    
    def __repr__(self):
        return f"<SLA(id={self.id}, name='{self.name}')>"

class Schedule(OSTicketBase):
    """Schedule model"""
    
    __tablename__ = "ost_schedule"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    flags = Column(Integer, nullable=False, default=0)
    name = Column(String(255), nullable=False)
    timezone = Column(String(64), nullable=True)
    description = Column(String(255), nullable=False)
    created = Column(DateTime, nullable=False)
    updated = Column(DateTime, nullable=False)
    
    def __repr__(self):
        return f"<Schedule(id={self.id}, name='{self.name}')>"

class ScheduleEntry(OSTicketBase):
    """Schedule entry model"""
    
    __tablename__ = "ost_schedule_entry"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    schedule_id = Column(Integer, nullable=False, default=0)
    flags = Column(Integer, nullable=False, default=0)
    sort = Column(Integer, nullable=False, default=0)
    name = Column(String(255), nullable=False)
    repeats = Column(Enum('never', 'daily', 'weekly', 'monthly', name='schedule_repeat'), nullable=False, default='never')
    starts_on = Column(DateTime, nullable=True)
    starts_at = Column(String(10), nullable=True)
    ends_on = Column(DateTime, nullable=True)
    ends_at = Column(String(10), nullable=True)
    day_of_week = Column(Integer, nullable=True)
    week_of_month = Column(Integer, nullable=True)
    day_of_month = Column(Integer, nullable=True)
    month_of_year = Column(Integer, nullable=True)
    created = Column(DateTime, nullable=False)
    updated = Column(DateTime, nullable=False)
    
    def __repr__(self):
        return f"<ScheduleEntry(id={self.id}, schedule_id={self.schedule_id}, name='{self.name}')>"

class Group(OSTicketBase):
    """Group model"""
    
    __tablename__ = "ost_group"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    role_id = Column(Integer, nullable=False, default=0)
    flags = Column(Integer, nullable=False, default=1)
    name = Column(String(120), nullable=False, default="")
    notes = Column(Text, nullable=True)
    created = Column(DateTime, nullable=False)
    updated = Column(DateTime, nullable=False)
    
    def __repr__(self):
        return f"<Group(id={self.id}, name='{self.name}')>"