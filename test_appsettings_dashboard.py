#!/usr/bin/env python
"""
Test the app settings dashboard page
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gamezone.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model

User = get_user_model()

def test_dashboard_access():
    """Test that dashboard page loads correctly for admin"""
    print("\n" + "="*70)
    print("TEST: App Settings Dashboard Access")
    print("="*70)
    
    # Get or create admin user
    admin, created = User.objects.get_or_create(
        username='admin',
        defaults={
            'email': 'admin@example.com',
            'is_superuser': True,
            'is_staff': True
        }
    )
    
    if created:
        admin.set_password('admin123')
        admin.save()
        print("✓ Created admin user")
    else:
        print("✓ Admin user exists")
    
    # Create test client and login
    client = Client()
    client.force_login(admin)
    
    # Test GET request
    print("\nTesting GET request...")
    response = client.get('/customadmin/settings/')
    
    print(f"Response status code: {response.status_code}")
    
    if response.status_code == 200:
        # Check if form fields are present
        content = response.content.decode('utf-8')
        
        fields_to_check = [
            'id_app_version',
            'id_app_link',
            'id_under_maintenance',
            'id_show_popup',
            'id_popup_title',
            'id_popup_description',
            'id_popup_link'
        ]
        
        print("\nChecking form fields in HTML:")
        for field in fields_to_check:
            if field in content:
                print(f"  ✓ {field}")
            else:
                print(f"  ✗ {field} MISSING")
                return False
        
        print("\n✅ Dashboard page loads successfully!")
        return True
    else:
        print(f"✗ Dashboard returned status {response.status_code}")
        if response.status_code == 500:
            print("\nError details:")
            print(response.content.decode('utf-8')[:500])
        return False

def test_post_update():
    """Test updating settings via POST"""
    print("\n" + "="*70)
    print("TEST: Update Settings via Dashboard")
    print("="*70)
    
    admin = User.objects.filter(is_superuser=True).first()
    if not admin:
        print("✗ No admin user found")
        return False
    
    client = Client()
    client.force_login(admin)
    
    # Test POST request
    data = {
        'app_version': '2.0.0',
        'app_link': 'https://newlink.com',
        'under_maintenance': False,
        'show_popup': True,
        'popup_title': 'New Update Available',
        'popup_description': 'Download the latest version now!',
        'popup_link': 'https://download.com/app'
    }
    
    print("Submitting form with data...")
    response = client.post('/customadmin/settings/', data)
    
    print(f"Response status code: {response.status_code}")
    
    if response.status_code in [200, 302]:
        # Verify data was saved
        from games.models import AppSettings
        settings = AppSettings.objects.get(pk=1)
        
        print("\nVerifying saved data:")
        checks = [
            ('app_version', settings.app_version, '2.0.0'),
            ('popup_title', settings.popup_title, 'New Update Available'),
            ('show_popup', settings.show_popup, True)
        ]
        
        for field_name, actual, expected in checks:
            if actual == expected:
                print(f"  ✓ {field_name}: {actual}")
            else:
                print(f"  ✗ {field_name}: expected {expected}, got {actual}")
                return False
        
        print("\n✅ Settings updated successfully!")
        return True
    else:
        print(f"✗ POST request failed with status {response.status_code}")
        return False

if __name__ == '__main__':
    results = []
    
    try:
        results.append(("Dashboard Access", test_dashboard_access()))
    except Exception as e:
        print(f"✗ Dashboard access test failed: {e}")
        import traceback
        traceback.print_exc()
        results.append(("Dashboard Access", False))
    
    try:
        results.append(("Update Settings", test_post_update()))
    except Exception as e:
        print(f"✗ Update test failed: {e}")
        import traceback
        traceback.print_exc()
        results.append(("Update Settings", False))
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    for test_name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name:30} {status}")
    
    all_passed = all(result[1] for result in results)
    print("\n" + ("="*70))
    if all_passed:
        print("🎉 ALL TESTS PASSED!")
    else:
        print("⚠️  SOME TESTS FAILED")
    print("="*70)
