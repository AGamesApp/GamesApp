#!/usr/bin/env python
"""
Simulate what happens when you press the buttons in the browser
This will help identify if the issue is frontend or backend
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gamezone.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from support.models import SupportMessage

User = get_user_model()

# Create test client
client = Client()

# Get or create admin user
admin, _ = User.objects.get_or_create(
    username='agames',
    defaults={'is_staff': True, 'is_superuser': True}
)

# Login
client.force_login(admin)

print("=" * 70)
print("SIMULATING BUTTON CLICKS - Support Messages Dashboard")
print("=" * 70)

# Get current counts
total_messages = SupportMessage.objects.count()
pending_count = SupportMessage.objects.filter(is_reviewed=False).count()
reviewed_count = SupportMessage.objects.filter(is_reviewed=True).count()

print(f"\n📊 CURRENT STATE:")
print(f"   Total messages: {total_messages}")
print(f"   Pending: {pending_count}")
print(f"   Reviewed: {reviewed_count}")

if total_messages == 0:
    print("\n⚠️  No messages exist. Creating test messages...")
    
    # Create test messages
    for i in range(3):
        SupportMessage.objects.create(
            name=f"Test User {i+1}",
            email=f"test{i+1}@example.com",
            subject=f"Test Message {i+1}",
            message=f"This is test message number {i+1}",
            is_reviewed=False
        )
    
    pending_count = 3
    print(f"   ✅ Created 3 test messages")

print("\n" + "=" * 70)
print("TEST 1: Loading Support Messages Page (Pending Tab)")
print("=" * 70)

response = client.get('/customadmin/support/?status=pending')
print(f"Status Code: {response.status_code}")

if response.status_code == 200:
    html = response.content.decode('utf-8')
    
    # Check if buttons are in HTML
    has_mark_all = 'btn-mark-all-reviewed' in html
    has_delete_all = 'btn-delete-all' in html
    has_event_listeners = 'addEventListener' in html
    
    print(f"✓ Page loaded successfully")
    print(f"   - Mark All button present: {'YES' if has_mark_all else 'NO'}")
    print(f"   - Delete All button present: {'YES' if has_delete_all else 'NO'}")
    print(f"   - Event listeners added: {'YES' if has_event_listeners else 'NO'}")
    
    # Check for script errors
    if 'Uncaught' in html or 'SyntaxError' in html:
        print("   ⚠️  WARNING: Possible JavaScript error detected in HTML")
else:
    print(f"✗ Failed to load page: {response.status_code}")

print("\n" + "=" * 70)
print("TEST 2: Simulating 'Mark All as Reviewed' Button Click")
print("=" * 70)

print("This simulates what happens when JavaScript calls:")
print("  fetch('/customadmin/support/mark-all-reviewed/', {...})")

response = client.post(
    '/customadmin/support/mark-all-reviewed/',
    data='{"filter": "pending"}',
    content_type='application/json',
    HTTP_X_CSRFTOKEN='test-token'
)

print(f"\nResponse Status: {response.status_code}")

if response.status_code == 200:
    import json
    data = json.loads(response.content)
    print(f"✅ SUCCESS!")
    print(f"   Response: {data}")
    print(f"   Messages marked: {data.get('count', 0)}")
else:
    print(f"❌ FAILED! Status: {response.status_code}")
    print(f"   Response: {response.content.decode('utf-8')[:200]}")

# Check new state
new_pending = SupportMessage.objects.filter(is_reviewed=False).count()
new_reviewed = SupportMessage.objects.filter(is_reviewed=True).count()

print(f"\n📊 STATE AFTER MARK ALL:")
print(f"   Pending: {pending_count} → {new_pending}")
print(f"   Reviewed: {reviewed_count} → {new_reviewed}")

print("\n" + "=" * 70)
print("TEST 3: Simulating 'Delete All' Button Click")
print("=" * 70)

print("This simulates what happens when JavaScript calls:")
print("  fetch('/customadmin/support/delete-all/', {...})")

response = client.post(
    '/customadmin/support/delete-all/',
    data='{"filter": "reviewed"}',
    content_type='application/json',
    HTTP_X_CSRFTOKEN='test-token'
)

print(f"\nResponse Status: {response.status_code}")

if response.status_code == 200:
    import json
    data = json.loads(response.content)
    print(f"✅ SUCCESS!")
    print(f"   Response: {data}")
    print(f"   Messages deleted: {data.get('count', 0)}")
else:
    print(f"❌ FAILED! Status: {response.status_code}")
    print(f"   Response: {response.content.decode('utf-8')[:200]}")

# Final state
final_total = SupportMessage.objects.count()
final_pending = SupportMessage.objects.filter(is_reviewed=False).count()
final_reviewed = SupportMessage.objects.filter(is_reviewed=True).count()

print(f"\n📊 FINAL STATE:")
print(f"   Total: {total_messages} → {final_total}")
print(f"   Pending: {pending_count} → {final_pending}")
print(f"   Reviewed: {reviewed_count} → {final_reviewed}")

print("\n" + "=" * 70)
print("CONCLUSION")
print("=" * 70)

if response.status_code == 200:
    print("✅ Backend is working perfectly!")
    print("\nIf buttons don't work in browser, the issue is FRONTEND:")
    print("  1. Open browser console (F12)")
    print("  2. Look for JavaScript errors (red text)")
    print("  3. Check if you see the green border around buttons")
    print("  4. Verify console logs appear:")
    print("     - 'Script started loading'")
    print("     - 'DOMContentLoaded fired'")
    print("     - 'Event listeners added'")
    print("\n  5. Try hard refresh: Ctrl+Shift+R (Cmd+Shift+R on Mac)")
    print("  6. Try different browser (Chrome, Firefox, Safari)")
    print("\nRead BUTTON_DEBUG_GUIDE.md for detailed troubleshooting")
else:
    print("❌ Backend has issues - need to fix server-side code")
