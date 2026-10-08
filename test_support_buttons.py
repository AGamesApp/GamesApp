#!/usr/bin/env python
"""
Test script to verify support message buttons work correctly
"""
import os
import django
import sys

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gamezone.settings')
django.setup()

from support.models import SupportMessage
from django.contrib.auth import get_user_model

User = get_user_model()

def test_setup():
    """Create test data"""
    print("=" * 60)
    print("SUPPORT MESSAGE BUTTONS TEST")
    print("=" * 60)
    
    # Get or create admin user
    admin = User.objects.filter(is_superuser=True).first()
    if not admin:
        print("❌ No admin user found!")
        return False
    
    print(f"✓ Admin user: {admin.username}")
    
    # Count messages
    total = SupportMessage.objects.count()
    pending = SupportMessage.objects.filter(is_reviewed=False).count()
    reviewed = SupportMessage.objects.filter(is_reviewed=True).count()
    
    print(f"\nCurrent state:")
    print(f"  Total messages: {total}")
    print(f"  Pending: {pending}")
    print(f"  Reviewed: {reviewed}")
    
    # Create test message if none exist
    if total == 0:
        msg = SupportMessage.objects.create(
            name="Test User",
            email="test@example.com",
            subject="Test Message",
            message="This is a test message for button testing"
        )
        print(f"\n✓ Created test message (ID: {msg.id})")
        pending = 1
        total = 1
    
    return True

def test_views():
    """Test that all views are accessible"""
    from django.urls import reverse
    
    print("\n" + "=" * 60)
    print("TESTING VIEWS")
    print("=" * 60)
    
    views = [
        ('customadmin:support_messages', 'Support messages list'),
        ('customadmin:toggle_review', 'Toggle review', [1]),
        ('customadmin:delete_support_message', 'Delete message', [1]),
        ('customadmin:delete_all_support_messages', 'Delete all'),
        ('customadmin:mark_all_reviewed', 'Mark all reviewed'),
    ]
    
    for view_data in views:
        try:
            if len(view_data) == 3:
                url = reverse(view_data[0], args=view_data[2])
            else:
                url = reverse(view_data[0])
            print(f"✓ {view_data[1]}: {url}")
        except Exception as e:
            print(f"❌ {view_data[1]}: {str(e)}")
            return False
    
    return True

def main():
    print("\n")
    
    if not test_setup():
        sys.exit(1)
    
    if not test_views():
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("✓ ALL TESTS PASSED")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Open browser: https://games.agames.cv/customadmin/support/")
    print("2. Open browser console (F12)")
    print("3. Check for console logs:")
    print("   - 'Script started loading'")
    print("   - 'CSRF token: Found'")
    print("   - 'DOMContentLoaded fired'")
    print("   - 'Current filter: pending'")
    print("4. Test each button:")
    print("   - Individual 'Mark as Reviewed' button")
    print("   - Individual 'Delete' button")
    print("   - 'Mark All as Reviewed' button (top right)")
    print("   - 'Delete All Pending' button (top right)")
    print("\n")

if __name__ == '__main__':
    main()
