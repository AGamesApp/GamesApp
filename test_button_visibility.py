#!/usr/bin/env python
"""
Test script to check if buttons are visible in the rendered HTML
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gamezone.settings')
django.setup()

from django.test import RequestFactory, Client
from django.contrib.auth import get_user_model

User = get_user_model()

# Create a test client
client = Client()

# Get or create admin user
admin, _ = User.objects.get_or_create(
    username='agames',
    defaults={'is_staff': True, 'is_superuser': True}
)

# Login
client.force_login(admin)

# Test pending tab
print("=" * 60)
print("TESTING PENDING TAB")
print("=" * 60)
response = client.get('/customadmin/support/?status=pending')
print(f"Status Code: {response.status_code}")

html = response.content.decode('utf-8')

# Check for button IDs
if 'id="btn-mark-all-reviewed"' in html:
    print("✓ Mark All Reviewed button ID found in HTML")
else:
    print("✗ Mark All Reviewed button ID NOT found in HTML")

if 'id="btn-delete-all"' in html:
    print("✓ Delete All button ID found in HTML")
else:
    print("✗ Delete All button ID NOT found in HTML")

# Check for JavaScript
if 'addEventListener' in html:
    print("✓ JavaScript addEventListener found")
else:
    print("✗ JavaScript addEventListener NOT found")

if "getElementById('btn-mark-all-reviewed')" in html:
    print("✓ getElementById for Mark All button found")
else:
    print("✗ getElementById for Mark All button NOT found")

if "getElementById('btn-delete-all')" in html:
    print("✓ getElementById for Delete All button found")
else:
    print("✗ getElementById for Delete All button NOT found")

# Check for console.log statements
import re
console_logs = re.findall(r"console\.log\('([^']+)'\)", html)
if console_logs:
    print(f"\n✓ Found {len(console_logs)} console.log statements")
    print("  First 5 logs:")
    for log in console_logs[:5]:
        print(f"    - {log}")
else:
    print("\n✗ No console.log statements found")

# Test reviewed tab
print("\n" + "=" * 60)
print("TESTING REVIEWED TAB")
print("=" * 60)
response = client.get('/customadmin/support/?status=reviewed')
print(f"Status Code: {response.status_code}")

print("\n" + "=" * 60)
print("RECOMMENDATION")
print("=" * 60)
print("Open browser console (F12) and check for these messages:")
print("  1. 'Script started loading'")
print("  2. 'DOMContentLoaded fired'")
print("  3. 'Current filter: pending' (or 'reviewed')")
print("  4. 'Mark All button: [object HTMLButtonElement]'")
print("  5. 'Delete All button: [object HTMLButtonElement]'")
print("  6. 'Buttons configured, adding event listeners'")
print("  7. 'Event listeners added'")
print("\nIf you don't see these messages, there's a JavaScript error.")
print("If you see 'Buttons not found!', the HTML structure is wrong.")
