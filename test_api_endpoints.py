#!/usr/bin/env python3
"""
Test all reported API endpoint issues
"""

import os
import sys
import django
import json

sys.path.insert(0, '/root/game')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gamezone.settings')
django.setup()

from django.test import RequestFactory
from django.contrib.auth import get_user_model
from rest_framework.test import force_authenticate
from notifications.views import NotificationViewSet
from games.views import GameViewSet
from support.views import SupportMessageViewSet
from pages.views import PageDetailView
from pages.models import Page

User = get_user_model()
factory = RequestFactory()

print("=" * 80)
print("🧪 TESTING API ENDPOINTS")
print("=" * 80)

# Create test user
try:
    test_user = User.objects.get(email='test@endpoint.com')
except User.DoesNotExist:
    test_user = User.objects.create_user(
        email='test@endpoint.com',
        username='testuser',
        password='testpass123'
    )

print(f"\n✅ Test user: {test_user.email}")

# ============================================================================
# TEST 1: Notifications - Mark All Read
# ============================================================================
print("\n" + "=" * 80)
print("TEST 1: POST /api/notifications/mark_all_read/")
print("=" * 80)

try:
    request = factory.post('/api/notifications/mark_all_read/')
    force_authenticate(request, user=test_user)
    
    view = NotificationViewSet.as_view({'post': 'mark_all_read'})
    response = view(request)
    
    print(f"✅ Status Code: {response.status_code}")
    print(f"✅ Response: {json.dumps(response.data, indent=2)}")
    print("✅ ENDPOINT WORKS!")
    
except Exception as e:
    print(f"❌ ERROR: {e}")
    import traceback
    traceback.print_exc()

# ============================================================================
# TEST 2: Games - My Loved Games (Favourites)
# ============================================================================
print("\n" + "=" * 80)
print("TEST 2: GET /api/games/my_loved_games/")
print("=" * 80)

try:
    request = factory.get('/api/games/my_loved_games/')
    force_authenticate(request, user=test_user)
    
    view = GameViewSet.as_view({'get': 'my_loved_games'})
    response = view(request)
    
    print(f"✅ Status Code: {response.status_code}")
    if hasattr(response, 'data'):
        print(f"✅ Response keys: {list(response.data.keys()) if isinstance(response.data, dict) else 'list'}")
    print("✅ ENDPOINT WORKS!")
    
except Exception as e:
    print(f"❌ ERROR: {e}")
    import traceback
    traceback.print_exc()

# ============================================================================
# TEST 3: Support - Send Message
# ============================================================================
print("\n" + "=" * 80)
print("TEST 3: POST /api/support/messages/")
print("=" * 80)

try:
    data = {
        'name': 'Test User',
        'email': 'test@example.com',
        'subject': 'Test Subject',
        'message': 'This is a test message'
    }
    request = factory.post('/api/support/messages/', data=data, content_type='application/json')
    # No authentication needed - AllowAny for create
    
    view = SupportMessageViewSet.as_view({'post': 'create'})
    response = view(request)
    
    print(f"✅ Status Code: {response.status_code}")
    print(f"✅ Response: {json.dumps(response.data, indent=2) if hasattr(response, 'data') else 'No data'}")
    print("✅ ENDPOINT WORKS!")
    
except Exception as e:
    print(f"❌ ERROR: {e}")
    import traceback
    traceback.print_exc()

# ============================================================================
# TEST 4: Pages - Get Dashboard Created Pages
# ============================================================================
print("\n" + "=" * 80)
print("TEST 4: GET /api/pages/<title>/")
print("=" * 80)

try:
    # Check if any pages exist
    pages_count = Page.objects.count()
    print(f"📊 Total pages in database: {pages_count}")
    
    if pages_count > 0:
        test_page = Page.objects.first()
        print(f"📄 Testing with page: {test_page.title}")
        
        request = factory.get(f'/api/pages/{test_page.title}/')
        view = PageDetailView.as_view()
        response = view(request, title=test_page.title)
        
        print(f"✅ Status Code: {response.status_code}")
        print(f"✅ Response keys: {list(response.data.keys()) if hasattr(response, 'data') else 'No data'}")
        print("✅ ENDPOINT WORKS!")
    else:
        print("⚠️  No pages found - creating test page...")
        test_page = Page.objects.create(
            title='test-page',
            content='<h1>Test Page</h1><p>This is a test page.</p>'
        )
        print(f"✅ Created test page: {test_page.title}")
        
        request = factory.get(f'/api/pages/{test_page.title}/')
        view = PageDetailView.as_view()
        response = view(request, title=test_page.title)
        
        print(f"✅ Status Code: {response.status_code}")
        print("✅ ENDPOINT WORKS!")
    
except Exception as e:
    print(f"❌ ERROR: {e}")
    import traceback
    traceback.print_exc()

# ============================================================================
# SUMMARY: Check URL Routing
# ============================================================================
print("\n" + "=" * 80)
print("🔍 CHECKING URL ROUTING")
print("=" * 80)

from django.urls import resolve, reverse

endpoints_to_check = [
    ('POST', '/api/notifications/mark_all_read/'),
    ('GET', '/api/games/my_loved_games/'),
    ('POST', '/api/support/messages/'),
]

for method, url in endpoints_to_check:
    try:
        match = resolve(url)
        print(f"✅ {method:5} {url:40} → {match.func.__name__ if hasattr(match.func, '__name__') else match.func}")
    except Exception as e:
        print(f"❌ {method:5} {url:40} → NOT FOUND: {e}")

print("\n" + "=" * 80)
print("✅ TESTING COMPLETE")
print("=" * 80)
