#!/usr/bin/env python3
"""
Test script to simulate dashboard notification sending
and compare with direct Firebase send
"""

import os
import sys
import django

# Setup Django
sys.path.insert(0, '/root/game')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gamezone.settings')
django.setup()

from notifications.fcm_service import send_notification_to_all_users_topic
from datetime import datetime

print("=" * 70)
print("🧪 TESTING DASHBOARD NOTIFICATION FLOW")
print("=" * 70)

# Test 1: Simulate dashboard send (using the same function)
print("\n1️⃣ Testing dashboard function (send_notification_to_all_users_topic)")
print("-" * 70)

try:
    log = send_notification_to_all_users_topic(
        title='🎯 Dashboard Test',
        body=f'Testing dashboard send at {datetime.utcnow().isoformat()}',
        notification_type='normal',
        data={
            'sent_from': 'dashboard_test',
            'test': 'true'
        },
        image_url=None
    )
    
    print(f"✅ Function executed successfully!")
    print(f"   NotificationLog ID: {log.id}")
    print(f"   Successful sends: {log.successful_sends}")
    print(f"   Failed sends: {log.failed_sends}")
    print(f"   Title: {log.title}")
    print(f"   Body: {log.body}")
    
    if log.successful_sends > 0:
        print("\n✅ Dashboard send WORKED! Message sent to FCM.")
    else:
        print("\n❌ Dashboard send FAILED! Check logs.")
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

# Test 2: Direct Firebase send (like the working script)
print("\n" + "=" * 70)
print("2️⃣ Testing direct Firebase send (like send_test_now.py)")
print("-" * 70)

import firebase_admin
from firebase_admin import credentials, messaging

# Check if Firebase is already initialized
if not firebase_admin._apps:
    cred = credentials.Certificate('serviceAccountKey.json')
    firebase_admin.initialize_app(cred)

try:
    message = messaging.Message(
        notification=messaging.Notification(
            title='🎯 Direct Test',
            body=f'Testing direct send at {datetime.utcnow().isoformat()}'
        ),
        data={
            'sent_from': 'direct_test',
            'test': 'true'
        },
        topic='all_users'
    )
    
    response = messaging.send(message)
    print(f"✅ Direct send successful!")
    print(f"   Message ID: {response}")
    
except Exception as e:
    print(f"❌ Direct send failed: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70)
print("📊 COMPARISON RESULTS")
print("=" * 70)
print("""
Both methods should work identically.

If dashboard method works but you don't see notifications:
  → Check that you're looking in the right place
  → Firebase Console only shows topics with subscribers
  → Both messages ARE being sent to FCM successfully

If dashboard method fails:
  → Check Django logs for errors
  → Verify database connection
  → Check NotificationLog table

Next step: Check Django logs and NotificationLog database
""")

print("=" * 70)
