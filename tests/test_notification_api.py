#!/usr/bin/env python
"""
Test notification API endpoints
"""

import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gamezone.settings')
django.setup()

from django.contrib.auth import get_user_model
from notifications.models import Notification
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token

User = get_user_model()

def test_notification_endpoints():
    """Test all notification API endpoints"""
    print("\n" + "="*60)
    print("🧪 TESTING NOTIFICATION API ENDPOINTS")
    print("="*60)
    
    # Get or create a test user
    user = User.objects.filter(is_active=True).first()
    if not user:
        print("✗ No active users found")
        return
    
    print(f"\n✓ Testing with user: {user.email}")
    
    # Create test notifications
    print("\nCreating test notifications...")
    notifications = []
    for i, notif_type in enumerate(['normal', 'fix', 'update', 'error']):
        notif = Notification.objects.create(
            user=user,
            notification_type=notif_type,
            title=f"Test {notif_type} notification {i+1}",
            body=f"This is test notification {i+1}",
            is_read=(i == 0)  # Make first one read
        )
        notifications.append(notif)
        status = "read" if notif.is_read else "unread"
        print(f"  ✓ Created {notif_type} notification (ID: {notif.id}) - {status}")
    
    # Create API client
    client = APIClient()
    
    # Get or create token for user
    token, created = Token.objects.get_or_create(user=user)
    client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
    print(f"\n✓ Using auth token: {token.key[:20]}...")
    
    # Test 1: List notifications
    print("\n" + "-"*60)
    print("TEST 1: GET /api/notifications/ (List notifications)")
    print("-"*60)
    response = client.get('/api/notifications/')
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"✓ Received {len(data.get('results', []))} notifications")
        if data.get('results'):
            first = data['results'][0]
            print(f"  Sample notification:")
            print(f"    - Type: {first.get('notification_type')}")
            print(f"    - Title: {first.get('title')}")
            print(f"    - Is Read: {first.get('is_read')}")
    else:
        print(f"✗ ERROR: {response.status_code}")
        print(response.content)
    
    # Test 2: Get unread notifications
    print("\n" + "-"*60)
    print("TEST 2: GET /api/notifications/unread/ (Unread count)")
    print("-"*60)
    response = client.get('/api/notifications/unread/')
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"✓ Unread count: {data.get('unread_count', 0)}")
        print(f"  Total unread: {len(data.get('unread_notifications', []))}")
    else:
        print(f"✗ ERROR: {response.status_code}")
        print(response.content)
    
    # Test 3: Mark single notification as read
    print("\n" + "-"*60)
    print("TEST 3: POST /api/notifications/{id}/mark_read/")
    print("-"*60)
    unread_notif = [n for n in notifications if not n.is_read][0]
    response = client.post(f'/api/notifications/{unread_notif.id}/mark_read/')
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"✓ Notification {unread_notif.id} marked as read")
        print(f"  Is Read: {data.get('is_read')}")
    else:
        print(f"✗ ERROR: {response.status_code}")
        print(response.content)
    
    # Test 4: Mark all as read
    print("\n" + "-"*60)
    print("TEST 4: POST /api/notifications/mark_all_read/")
    print("-"*60)
    response = client.post('/api/notifications/mark_all_read/')
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"✓ Marked {data.get('marked_count', 0)} notifications as read")
    else:
        print(f"✗ ERROR: {response.status_code}")
        print(response.content)
    
    # Verify all are read
    unread_count = Notification.objects.filter(user=user, is_read=False).count()
    print(f"  Remaining unread: {unread_count}")
    
    # Clean up
    print("\nCleaning up test data...")
    for notif in notifications:
        notif.delete()
    print("✓ Test notifications deleted")
    
    print("\n" + "="*60)
    print("✅ ALL API ENDPOINT TESTS COMPLETED!")
    print("="*60)

if __name__ == '__main__':
    try:
        test_notification_endpoints()
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
