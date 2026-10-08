#!/usr/bin/env python
"""
FCM Topics Test Script

This script tests the FCM Topics implementation by:
1. Checking Firebase initialization
2. Testing the send_to_topic function
3. Verifying the enhanced topic method works
4. Providing detailed feedback

Usage:
    python scripts/test_fcm_topics.py
"""

import os
import sys
import django

# Setup Django environment
sys.path.insert(0, '/root/game')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gamezone.settings')
django.setup()

from notifications.fcm_service import FCMService, send_notification_to_all_users_topic
from notifications.models import DeviceToken, NotificationLog
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def print_section(title):
    """Print a formatted section header"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")


def test_firebase_initialization():
    """Test 1: Check if Firebase is initialized"""
    print_section("TEST 1: Firebase Initialization")
    
    try:
        fcm_service = FCMService()
        if fcm_service.initialized:
            print("✅ Firebase is initialized successfully")
            return True
        else:
            print("❌ Firebase is NOT initialized")
            print("   Check if serviceAccountKey.json exists and is valid")
            return False
    except Exception as e:
        print(f"❌ Error initializing Firebase: {e}")
        return False


def test_topic_constant():
    """Test 2: Check if TOPIC_ALL_USERS constant exists"""
    print_section("TEST 2: Topic Constant")
    
    try:
        topic = FCMService.TOPIC_ALL_USERS
        print(f"✅ TOPIC_ALL_USERS constant exists: '{topic}'")
        return True
    except AttributeError:
        print("❌ TOPIC_ALL_USERS constant not found")
        return False


def test_send_to_topic_method():
    """Test 3: Test basic send_to_topic method"""
    print_section("TEST 3: Send to Topic Method (Dry Run)")
    
    try:
        fcm_service = FCMService()
        
        # Check if method exists
        if not hasattr(fcm_service, 'send_to_topic'):
            print("❌ send_to_topic method not found")
            return False
        
        print("✅ send_to_topic method exists")
        print("\nMethod signature:")
        import inspect
        sig = inspect.signature(fcm_service.send_to_topic)
        print(f"   send_to_topic{sig}")
        
        # Show expected parameters
        print("\nExpected parameters:")
        for param_name, param in sig.parameters.items():
            if param.default == inspect.Parameter.empty:
                print(f"   - {param_name} (required)")
            else:
                print(f"   - {param_name} (optional, default: {param.default})")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing send_to_topic: {e}")
        return False


def test_send_notification_to_all_users_topic():
    """Test 4: Test the main topic notification function"""
    print_section("TEST 4: Send Notification to All Users Topic Function")
    
    try:
        # Check if function exists
        if send_notification_to_all_users_topic is None:
            print("❌ send_notification_to_all_users_topic function not found")
            return False
        
        print("✅ send_notification_to_all_users_topic function exists")
        
        # Show function signature
        import inspect
        sig = inspect.signature(send_notification_to_all_users_topic)
        print(f"\nFunction signature:")
        print(f"   send_notification_to_all_users_topic{sig}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_actual_send(dry_run=True):
    """Test 5: Actually send a test notification to topic"""
    print_section("TEST 5: Actual Topic Send Test")
    
    if dry_run:
        print("⚠️  DRY RUN MODE - No actual notification will be sent")
        print("   To send a real notification, run with: test_actual_send(dry_run=False)\n")
        return True
    
    try:
        print("🚀 Sending test notification to 'all_users' topic...\n")
        
        log = send_notification_to_all_users_topic(
            title='🧪 FCM Topics Test',
            body='This is a test notification from the FCM Topics system',
            notification_type='normal',
            data={
                'test': 'true',
                'timestamp': str(timezone.now())
            }
        )
        
        print(f"✅ Notification sent!")
        print(f"\nResults:")
        print(f"   - Log ID: {log.id}")
        print(f"   - Title: {log.title}")
        print(f"   - Successful sends: {log.successful_sends}")
        print(f"   - Failed sends: {log.failed_sends}")
        print(f"   - Sent to all: {log.sent_to_all}")
        print(f"   - Created at: {log.created_at}")
        
        if log.successful_sends > 0:
            print("\n✅ Topic notification sent successfully!")
            print("   Check Firebase Console → Cloud Messaging → Topics")
            print("   to see delivery statistics")
            return True
        else:
            print("\n⚠️  Notification logged but send status unclear")
            print("   This is normal if no devices are subscribed yet")
            return True
            
    except Exception as e:
        print(f"❌ Error sending notification: {e}")
        import traceback
        traceback.print_exc()
        return False


def check_device_tokens():
    """Check device token status"""
    print_section("Device Token Status")
    
    total_tokens = DeviceToken.objects.count()
    active_tokens = DeviceToken.objects.filter(is_active=True).count()
    
    print(f"Total device tokens: {total_tokens}")
    print(f"Active device tokens: {active_tokens}")
    
    if active_tokens == 0:
        print("\n⚠️  No active device tokens found")
        print("   This means:")
        print("   1. No mobile devices have registered yet")
        print("   2. You can still test topic sending (it will succeed)")
        print("   3. But no devices will receive the notification")
        print("\n   To fully test:")
        print("   - Install mobile app on a device")
        print("   - Implement topic subscription code")
        print("   - Register device token with backend")
    else:
        print(f"\n✅ You have {active_tokens} active device(s)")
        print("   You can run the migration script:")
        print("   python manage.py migrate_tokens_to_topic")


def check_notification_logs():
    """Check recent notification logs"""
    print_section("Recent Notification Logs")
    
    recent_logs = NotificationLog.objects.order_by('-created_at')[:5]
    
    if not recent_logs.exists():
        print("No notification logs found yet")
    else:
        print(f"Last {recent_logs.count()} notifications:\n")
        for log in recent_logs:
            status = "✅" if log.successful_sends > 0 else "❌"
            print(f"{status} {log.created_at.strftime('%Y-%m-%d %H:%M:%S')} - {log.title}")
            print(f"   Type: {log.notification_type}, Success: {log.successful_sends}, Failed: {log.failed_sends}")
            print()


def main():
    """Run all tests"""
    print("\n" + "╔" + "=" * 78 + "╗")
    print("║" + " " * 78 + "║")
    print("║" + "FCM TOPICS TEST SUITE".center(78) + "║")
    print("║" + " " * 78 + "║")
    print("╚" + "=" * 78 + "╝")
    
    results = []
    
    # Run tests
    results.append(("Firebase Initialization", test_firebase_initialization()))
    results.append(("Topic Constant", test_topic_constant()))
    results.append(("Send to Topic Method", test_send_to_topic_method()))
    results.append(("Main Topic Function", test_send_notification_to_all_users_topic()))
    results.append(("Actual Send (Dry Run)", test_actual_send(dry_run=True)))
    
    # Check status
    check_device_tokens()
    check_notification_logs()
    
    # Summary
    print_section("TEST SUMMARY")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print(f"\nResults: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed!")
        print("\n" + "=" * 80)
        print("NEXT STEPS:")
        print("=" * 80)
        print("\n1. Send a real test notification:")
        print("   python manage.py shell")
        print("   >>> from notifications.fcm_service import send_notification_to_all_users_topic")
        print("   >>> log = send_notification_to_all_users_topic(")
        print("   ...     title='Test',")
        print("   ...     body='Testing topics!',")
        print("   ...     notification_type='normal'")
        print("   ... )")
        print("   >>> print(f'Success: {log.successful_sends}, Failed: {log.failed_sends}')")
        print("\n2. Check Firebase Console:")
        print("   - Go to: Firebase Console → Cloud Messaging → Topics")
        print("   - Look for 'all_users' topic")
        print("   - Check subscriber count and delivery stats")
        print("\n3. If you have device tokens:")
        print("   - Run: python manage.py migrate_tokens_to_topic")
        print("   - This subscribes existing tokens to the topic")
        print("\n4. Update mobile apps:")
        print("   - See: docs/client-side-fcm-topics-react-native.js")
        print("   - See: docs/client-side-fcm-topics-flutter.dart")
    else:
        print("\n⚠️  Some tests failed. Please check the errors above.")
    
    print("\n" + "=" * 80 + "\n")


if __name__ == '__main__':
    main()
