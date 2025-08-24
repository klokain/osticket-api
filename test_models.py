#!/usr/bin/env python3
"""
Test script to verify SQLAlchemy models work with OSTicket database
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from api.v2.core.database import SessionLocal
from api.v2.models import (
    Staff, Department, User, UserEmail, UserAccount, Organization,
    Ticket, TicketStatus, Config, ApiKey
)

def test_models():
    """Test that models can query the database successfully"""
    db = SessionLocal()
    
    try:
        print("Testing SQLAlchemy models with OSTicket database...\n")
        
        # Test Config model
        print("1. Testing Config model...")
        config_count = db.query(Config).count()
        print(f"   Found {config_count} config entries")
        
        if config_count > 0:
            config = db.query(Config).first()
            print(f"   Sample config: {config.namespace}.{config.key} = {config.value[:50]}...")
        
        # Test Staff model
        print("\n2. Testing Staff model...")
        staff_count = db.query(Staff).count()
        print(f"   Found {staff_count} staff members")
        
        if staff_count > 0:
            staff = db.query(Staff).first()
            print(f"   Sample staff: {staff.username} (ID: {staff.staff_id}, Active: {staff.isactive})")
        
        # Test Department model
        print("\n3. Testing Department model...")
        dept_count = db.query(Department).count()
        print(f"   Found {dept_count} departments")
        
        if dept_count > 0:
            dept = db.query(Department).first()
            print(f"   Sample department: {dept.name} (ID: {dept.id}, Public: {dept.ispublic})")
        
        # Test User model
        print("\n4. Testing User model...")
        user_count = db.query(User).count()
        print(f"   Found {user_count} users")
        
        if user_count > 0:
            user = db.query(User).first()
            print(f"   Sample user: {user.name} (ID: {user.id}, Status: {user.status})")
        
        # Test UserEmail model
        print("\n5. Testing UserEmail model...")
        user_email_count = db.query(UserEmail).count()
        print(f"   Found {user_email_count} user emails")
        
        if user_email_count > 0:
            user_email = db.query(UserEmail).first()
            print(f"   Sample user email: {user_email.address} (User ID: {user_email.user_id})")
        
        # Test Ticket model
        print("\n6. Testing Ticket model...")
        ticket_count = db.query(Ticket).count()
        print(f"   Found {ticket_count} tickets")
        
        if ticket_count > 0:
            ticket = db.query(Ticket).first()
            print(f"   Sample ticket: #{ticket.number} (ID: {ticket.ticket_id}, Status: {ticket.status_id})")
        
        # Test TicketStatus model
        print("\n7. Testing TicketStatus model...")
        status_count = db.query(TicketStatus).count()
        print(f"   Found {status_count} ticket statuses")
        
        if status_count > 0:
            status = db.query(TicketStatus).first()
            print(f"   Sample status: {status.name} (ID: {status.id}, State: {status.state})")
        
        # Test ApiKey model
        print("\n8. Testing ApiKey model...")
        api_key_count = db.query(ApiKey).count()
        print(f"   Found {api_key_count} API keys")
        
        if api_key_count > 0:
            api_key = db.query(ApiKey).first()
            print(f"   Sample API key: {api_key.ipaddr} (Active: {api_key.isactive})")
        
        print("\n✅ All model queries completed successfully!")
        print("✅ SQLAlchemy models are working correctly with the OSTicket database!")
        
    except Exception as e:
        print(f"\n❌ Error testing models: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        db.close()
    
    return True

if __name__ == "__main__":
    success = test_models()
    sys.exit(0 if success else 1)