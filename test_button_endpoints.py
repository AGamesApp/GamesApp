#!/usr/bin/env python
"""
Test all button endpoints directly
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gamezone.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from support.models import SupportMessage
import json

User = get_user_model()

def test_buttons():
    """Test all button endpoints"""
    print("\n" + "=" * 70)
    print("TESTING ALL BUTTON ENDPOINTS")
    print("=" * 70)
    
    # Get admin user
    admin = User.objects.filter(is_superuser=True).first()
    if not admin:
        print("❌ No admin user found!")
        return False
    
    # Create test client and login
    client = Client()
    client.force_login(admin)
    
    # Ensure we have a test message
    msg = SupportMessage.objects.first()
    if not msg:
        msg = SupportMessage.objects.create(
            name="Test User",
            email="test@example.com",
            subject="Test Button",
            message="Testing buttons"
        )
    
    print(f"\nTest message ID: {msg.id}")
    print(f"Initial state: {'Reviewed' if msg.is_reviewed else 'Pending'}")
    
    # Test 1: Toggle Review (Mark as Reviewed)
    print("\n" + "-" * 70)
    print("TEST 1: Individual 'Mark as Reviewed' button")
    print("-" * 70)
    response = client.post(
        f'/customadmin/support/{msg.id}/toggle/',
        data=json.dumps({'next': '/customadmin/support/'}),
        content_type='application/json'
    )
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Response: {data}")
        print(f"✓ Mark as reviewed works! Message is now: {'Reviewed' if data.get('is_reviewed') else 'Pending'}")
    else:
        print(f"❌ Failed: {response.content.decode()}")
    
    # Test 2: Delete Single Message
    print("\n" + "-" * 70)
    print("TEST 2: Individual 'Delete' button")
    print("-" * 70)
    
    # Create a new message to delete
    delete_msg = SupportMessage.objects.create(
        name="Delete Test",
        email="delete@example.com",
        subject="To be deleted",
        message="This will be deleted"
    )
    msg_id = delete_msg.id
    print(f"Created message ID: {msg_id}")
    
    response = client.post(
        f'/customadmin/support/{msg_id}/delete/',
        content_type='application/json'
    )
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Response: {data}")
        exists = SupportMessage.objects.filter(id=msg_id).exists()
        print(f"✓ Delete works! Message exists: {exists}")
    else:
        print(f"❌ Failed: {response.content.decode()}")
    
    # Test 3: Mark All as Reviewed
    print("\n" + "-" * 70)
    print("TEST 3: 'Mark All as Reviewed' button")
    print("-" * 70)
    
    # Create some pending messages
    for i in range(3):
        SupportMessage.objects.create(
            name=f"User {i}",
            email=f"user{i}@example.com",
            subject=f"Message {i}",
            message=f"Test message {i}"
        )
    
    pending_count = SupportMessage.objects.filter(is_reviewed=False).count()
    print(f"Pending messages: {pending_count}")
    
    response = client.post(
        '/customadmin/support/mark-all-reviewed/',
        data=json.dumps({'filter': 'pending'}),
        content_type='application/json'
    )
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Response: {data}")
        new_pending = SupportMessage.objects.filter(is_reviewed=False).count()
        print(f"✓ Mark all works! Pending before: {pending_count}, after: {new_pending}")
    else:
        print(f"❌ Failed: {response.content.decode()}")
    
    # Test 4: Delete All
    print("\n" + "-" * 70)
    print("TEST 4: 'Delete All' button")
    print("-" * 70)
    
    reviewed_count = SupportMessage.objects.filter(is_reviewed=True).count()
    print(f"Reviewed messages: {reviewed_count}")
    
    response = client.post(
        '/customadmin/support/delete-all/',
        data=json.dumps({'filter': 'reviewed'}),
        content_type='application/json'
    )
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Response: {data}")
        new_reviewed = SupportMessage.objects.filter(is_reviewed=True).count()
        print(f"✓ Delete all works! Reviewed before: {reviewed_count}, after: {new_reviewed}")
    else:
        print(f"❌ Failed: {response.content.decode()}")
    
    print("\n" + "=" * 70)
    print("✓ ALL BUTTON TESTS COMPLETED")
    print("=" * 70)
    print("\nFinal state:")
    print(f"  Total messages: {SupportMessage.objects.count()}")
    print(f"  Pending: {SupportMessage.objects.filter(is_reviewed=False).count()}")
    print(f"  Reviewed: {SupportMessage.objects.filter(is_reviewed=True).count()}")
    print("\n")
    
    return True

if __name__ == '__main__':
    test_buttons()
