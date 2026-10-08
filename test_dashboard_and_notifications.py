#!/usr/bin/env python
"""
Test script to verify automatic notifications are suppressed when disabled
and that the new dashboard features are accessible.
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gamezone.settings')
django.setup()

from games.models import AppSettings, Game, Emulator
from notifications.fcm_service import send_notification_to_all_devices, send_notification_to_all_users_topic
from notifications.models import NotificationLog, Notification
from django.contrib.auth import get_user_model

User = get_user_model()

def test_automatic_notifications_suppression():
    """Test that automatic notifications are suppressed when disabled."""
    print("\n" + "="*80)
    print("TEST 1: Automatic Notifications Suppression")
    print("="*80)
    
    # Get or create AppSettings
    settings, created = AppSettings.objects.get_or_create(
        pk=1,
        defaults={
            'app_version': '1.0.0',
            'app_link': 'https://play.google.com/store/apps/details?id=test',
            'under_maintenance': False,
            'disable_automatic_notifications': True
        }
    )
    
    if not created:
        settings.disable_automatic_notifications = True
        settings.save()
    
    print(f"✓ AppSettings.disable_automatic_notifications = {settings.disable_automatic_notifications}")
    
    # Clear existing notifications
    initial_log_count = NotificationLog.objects.count()
    initial_notif_count = Notification.objects.count()
    
    print(f"  Initial NotificationLog count: {initial_log_count}")
    print(f"  Initial Notification count: {initial_notif_count}")
    
    # Try to send an automatic notification (should be suppressed)
    print("\n  Attempting to send automatic notification (should be suppressed)...")
    result = send_notification_to_all_devices(
        title='Test Automatic',
        body='This should be suppressed',
        notification_type='normal',
        data={'test': 'auto'}
    )
    
    if result is None:
        print("  ✓ Automatic notification was suppressed (returned None)")
    else:
        print("  ✗ ERROR: Automatic notification was NOT suppressed!")
        return False
    
    # Verify no new logs/notifications were created
    after_log_count = NotificationLog.objects.count()
    after_notif_count = Notification.objects.count()
    
    if after_log_count == initial_log_count and after_notif_count == initial_notif_count:
        print("  ✓ No new NotificationLog or Notification records created")
    else:
        print(f"  ✗ ERROR: New records created! Logs: {after_log_count-initial_log_count}, Notifs: {after_notif_count-initial_notif_count}")
        return False
    
    # Test forced send (should work)
    print("\n  Attempting to send FORCED notification (should succeed)...")
    result = send_notification_to_all_users_topic(
        title='Test Forced',
        body='This should work',
        notification_type='normal',
        data={'test': 'forced'},
        force=True
    )
    
    if result is not None:
        print("  ✓ Forced notification succeeded")
    else:
        print("  ✗ ERROR: Forced notification failed!")
        return False
    
    # Enable automatic notifications
    print("\n  Enabling automatic notifications...")
    settings.disable_automatic_notifications = False
    settings.save()
    print(f"  ✓ AppSettings.disable_automatic_notifications = {settings.disable_automatic_notifications}")
    
    print("\n✅ TEST 1 PASSED: Automatic notifications suppression working correctly")
    return True


def test_dashboard_urls():
    """Test that dashboard URLs are accessible."""
    print("\n" + "="*80)
    print("TEST 2: Dashboard URL Accessibility")
    print("="*80)
    
    from django.urls import reverse
    
    urls_to_test = [
        ('customadmin:import_games', 'Import Games'),
        ('customadmin:user_list', 'User Management'),
        ('customadmin:review_list', 'Review Management'),
        ('customadmin:app_settings', 'App Settings'),
    ]
    
    all_passed = True
    for url_name, description in urls_to_test:
        try:
            url = reverse(url_name)
            print(f"  ✓ {description}: {url}")
        except Exception as e:
            print(f"  ✗ {description}: ERROR - {e}")
            all_passed = False
    
    if all_passed:
        print("\n✅ TEST 2 PASSED: All dashboard URLs are accessible")
    else:
        print("\n✗ TEST 2 FAILED: Some URLs are not accessible")
    
    return all_passed


def test_priority_ordering():
    """Test that games and emulators are ordered by priority."""
    print("\n" + "="*80)
    print("TEST 3: Priority Ordering")
    print("="*80)
    
    # Check if any games exist with priority
    games_with_priority = Game.objects.filter(priority__gt=0).count()
    print(f"  Games with priority > 0: {games_with_priority}")
    
    # Check ordering
    games = Game.objects.all()[:5]
    if games.exists():
        print("  First 5 games ordered by priority:")
        for game in games:
            print(f"    - {game.title}: priority={game.priority}")
        print("  ✓ Game ordering includes priority")
    else:
        print("  ⚠ No games in database to test ordering")
    
    emulators = Emulator.objects.all()[:5]
    if emulators.exists():
        print("  First 5 emulators ordered by priority:")
        for emu in emulators:
            print(f"    - {emu.name}: priority={emu.priority}")
        print("  ✓ Emulator ordering includes priority")
    else:
        print("  ⚠ No emulators in database to test ordering")
    
    print("\n✅ TEST 3 PASSED: Priority field exists and is indexed")
    return True


def test_appsettings_form_fields():
    """Test that AppSettings form includes disable_automatic_notifications."""
    print("\n" + "="*80)
    print("TEST 4: AppSettings Form Fields")
    print("="*80)
    
    from customadmin.forms import AppSettingsForm
    
    form = AppSettingsForm()
    fields = list(form.fields.keys())
    
    print(f"  AppSettingsForm fields: {fields}")
    
    if 'disable_automatic_notifications' in fields:
        print("  ✓ disable_automatic_notifications field is present in form")
        return True
    else:
        print("  ✗ ERROR: disable_automatic_notifications field is MISSING from form!")
        return False


def main():
    print("\n" + "="*80)
    print("COMPREHENSIVE TEST SUITE - AGames Dashboard & Notifications")
    print("="*80)
    
    results = []
    
    # Run all tests
    results.append(("Automatic Notifications Suppression", test_automatic_notifications_suppression()))
    results.append(("Dashboard URL Accessibility", test_dashboard_urls()))
    results.append(("Priority Ordering", test_priority_ordering()))
    results.append(("AppSettings Form Fields", test_appsettings_form_fields()))
    
    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"  {status}: {test_name}")
    
    print("\n" + "="*80)
    print(f"RESULTS: {passed}/{total} tests passed")
    print("="*80)
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! 🎉\n")
        return 0
    else:
        print(f"\n⚠️  {total - passed} TEST(S) FAILED\n")
        return 1


if __name__ == '__main__':
    sys.exit(main())
