"""
Staff, department, and team related database models for OSTicket API v2
"""

from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from .base import OSTicketBase, TimestampMixin

class Staff(OSTicketBase, TimestampMixin):
    """Staff model"""
    
    __tablename__ = "ost_staff"
    
    staff_id = Column(Integer, primary_key=True, autoincrement=True)
    dept_id = Column(Integer, ForeignKey("ost_department.dept_id"), nullable=False, default=0)
    role_id = Column(Integer, ForeignKey("ost_role.id"), nullable=False, default=0)
    username = Column(String(32), nullable=False, default="", unique=True, index=True)
    firstname = Column(String(32), nullable=True)
    lastname = Column(String(32), nullable=True)
    passwd = Column(String(128), nullable=True)
    backend = Column(String(32), nullable=True)
    email = Column(String(255), nullable=True, unique=True, index=True)
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
    assigned = Column(Integer, nullable=False, default=0)
    show_assigned_tickets = Column(Boolean, nullable=False, default=True)
    change_passwd = Column(Boolean, nullable=False, default=False)
    max_page_size = Column(Integer, nullable=False, default=0)
    auto_refresh_rate = Column(Integer, nullable=False, default=0)
    default_signature_type = Column(String(8), nullable=False, default="none")
    default_paper_size = Column(String(8), nullable=False, default="Letter")
    extra = Column(Text, nullable=True)
    
    # Foreign key relationships
    department = relationship("Department", back_populates="staff", foreign_keys=[dept_id])
    role = relationship("Role", back_populates="staff")
    assigned_tickets = relationship("Ticket", back_populates="staff", foreign_keys="Ticket.staff_id")
    team_members = relationship("TeamMember", back_populates="staff")
    department_access = relationship("StaffDeptAccess", back_populates="staff")
    
    def __repr__(self):
        return f"<Staff(staff_id={self.staff_id}, username='{self.username}', email='{self.email}')>"

class Department(OSTicketBase, TimestampMixin):
    """Department model"""
    
    __tablename__ = "ost_department"
    
    dept_id = Column(Integer, primary_key=True, autoincrement=True)
    pid = Column(Integer, nullable=True, default=None)  # Parent department
    ispublic = Column(Boolean, nullable=False, default=True, index=True)
    flags = Column(Integer, nullable=False, default=0)
    name = Column(String(128), nullable=False, default="", unique=True)
    signature = Column(Text, nullable=False)
    manager_id = Column(Integer, ForeignKey("ost_staff.staff_id"), nullable=False, default=0)
    email_id = Column(Integer, nullable=False, default=0)
    tpl_id = Column(Integer, nullable=False, default=0)
    sla_id = Column(Integer, ForeignKey("ost_sla.id"), nullable=False, default=0)
    schedule_id = Column(Integer, nullable=False, default=0)
    autoresp_email_id = Column(Integer, nullable=False, default=0)
    group_membership = Column(String(8), nullable=False, default="")
    path = Column(String(128), nullable=False, default="/", index=True)
    extra = Column(Text, nullable=True)
    
    # Relationships
    manager = relationship("Staff", foreign_keys=[manager_id])
    staff = relationship("Staff", back_populates="department", foreign_keys="Staff.dept_id")
    tickets = relationship("Ticket", back_populates="department")
    sla = relationship("SLA", foreign_keys=[sla_id])
    
    def __repr__(self):
        return f"<Department(dept_id={self.dept_id}, name='{self.name}')>"

class Team(OSTicketBase, TimestampMixin):
    """Team model"""
    
    __tablename__ = "ost_team"
    
    team_id = Column(Integer, primary_key=True, autoincrement=True)
    lead_id = Column(Integer, ForeignKey("ost_staff.staff_id"), nullable=False, default=0)
    flags = Column(Integer, nullable=False, default=1)
    name = Column(String(125), nullable=False, default="", unique=True)
    notes = Column(Text, nullable=True)
    
    # Relationships
    lead = relationship("Staff", foreign_keys=[lead_id])
    members = relationship("TeamMember", back_populates="team")
    tickets = relationship("Ticket", back_populates="team", foreign_keys="Ticket.team_id")
    
    def __repr__(self):
        return f"<Team(team_id={self.team_id}, name='{self.name}')>"

class TeamMember(OSTicketBase):
    """Team member association model"""
    
    __tablename__ = "ost_team_member"
    
    team_id = Column(Integer, ForeignKey("ost_team.team_id"), primary_key=True)
    staff_id = Column(Integer, ForeignKey("ost_staff.staff_id"), primary_key=True)
    flags = Column(Integer, nullable=False, default=0)
    
    # Relationships
    team = relationship("Team", back_populates="members")
    staff = relationship("Staff", back_populates="team_members")
    
    def __repr__(self):
        return f"<TeamMember(team_id={self.team_id}, staff_id={self.staff_id})>"

class Role(OSTicketBase, TimestampMixin):
    """Role model for permissions"""
    
    __tablename__ = "ost_role"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    flags = Column(Integer, nullable=False, default=1)
    name = Column(String(64), nullable=False, default="", unique=True)
    permissions = Column(Text, nullable=True)  # JSON encoded permissions
    notes = Column(Text, nullable=True)
    
    # Relationships
    staff = relationship("Staff", back_populates="role")
    
    def __repr__(self):
        return f"<Role(id={self.id}, name='{self.name}')>"

class StaffDeptAccess(OSTicketBase):
    """Staff department access model"""
    
    __tablename__ = "ost_staff_dept_access"
    
    staff_id = Column(Integer, ForeignKey("ost_staff.staff_id"), primary_key=True)
    dept_id = Column(Integer, ForeignKey("ost_department.dept_id"), primary_key=True, index=True)
    role_id = Column(Integer, ForeignKey("ost_role.id"), nullable=False, default=0)
    flags = Column(Integer, nullable=False, default=1)
    
    # Relationships
    staff = relationship("Staff", back_populates="department_access")
    department = relationship("Department")
    role = relationship("Role")
    
    def __repr__(self):
        return f"<StaffDeptAccess(staff_id={self.staff_id}, dept_id={self.dept_id})>"

class SLA(OSTicketBase, TimestampMixin):
    """SLA (Service Level Agreement) model"""
    
    __tablename__ = "ost_sla"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    schedule_id = Column(Integer, nullable=False, default=0)
    flags = Column(Integer, nullable=False, default=3)
    grace_period = Column(Integer, nullable=False, default=0)
    name = Column(String(64), nullable=False, default="", unique=True)
    notes = Column(Text, nullable=True)
    
    def __repr__(self):
        return f"<SLA(id={self.id}, name='{self.name}')>"