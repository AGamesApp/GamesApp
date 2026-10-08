#!/usr/bin/env python3
"""
Exact simulation of dashboard notification send flow
"""

import os
import sys
import django

sys.path.insert(0, '/root/game')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gamezone.settings')
django.setup()

from notifications.fcm_service import send_notification_to_all_users_topic
from notifications.models import NotificationLog

print("=" * 70)
print("🎯 SIMULATING EXACT DASHBOARD FLOW")
print("=" * 70)

# Simulate form data from dashboard
title = "🎯 Dashboard Simulation Test"
body = "This simulates exactly what the dashboard does when you click Send"
notification_type = "normal"
image_url = None
data = {
    'sent_from': 'dashboard',
    'sent_by': 'test@example.com'
}

print(f"\nInput data:")
print(f"  Title: {title}")
print(f"  Body: {body}")
print(f"  Type: {notification_type}")
print(f"  Image: {image_url}")
print(f"  Data: {data}")

print("\n" + "-" * 70)
print("Calling send_notification_to_all_users_topic...")
print("-" * 70)

try:
    log = send_notification_to_all_users_topic(
        title=title,
        body=body,
        notification_type=notification_type,
        data=data,
        image_url=image_url if image_url else None
    )
    
    print(f"\n✅ Function returned successfully!")
    print(f"\nNotificationLog details:")
    print(f"  ID: {log.id}")
    print(f"  Title: {log.title}")
    print(f"  Body: {log.body}")
    print(f"  Type: {log.notification_type}")
    print(f"  Successful sends: {log.successful_sends}")
    print(f"  Failed sends: {log.failed_sends}")
    print(f"  Created at: {log.created_at}")
    
    # Verify in database
    print("\n" + "-" * 70)
    print("Verifying in database...")
    print("-" * 70)
    
    db_log = NotificationLog.objects.get(id=log.id)
    print(f"\n  Database record confirmed:")
    print(f"  ID: {db_log.id}")
    print(f"  Successful sends: {db_log.successful_sends}")
    print(f"  Failed sends: {db_log.failed_sends}")
    
    if db_log.successful_sends > 0:
        print(f"\n✅ ✅ ✅ DASHBOARD SEND WORKED! ✅ ✅ ✅")
        print(f"\nThe notification was sent to Firebase successfully!")
        print(f"Message is now in FCM and will be delivered to subscribed devices.")
    else:
        print(f"\n❌ ❌ ❌ DASHBOARD SEND FAILED! ❌ ❌ ❌")
        print(f"\nThe function ran but FCM send returned False.")
        print(f"This means there was an issue with the FCMService.send_to_topic call.")
    
except Exception as e:
    print(f"\n❌ Exception occurred: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70)

EOF
