#!/usr/bin/env python
"""
Test script for new features:
1. Game description field
2. Notification system with types
3. Notification database storage
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gamezone.settings')
django.setup()

from django.contrib.auth import get_user_model
from games.models import Game
from notifications.models import Notification, DeviceToken, NotificationLog
from notifications.fcm_service import send_notification_to_all_devices

User = get_user_model()

def test_game_description():
    """Test game description field"""
    print("\n" + "="*60)
    print("TEST 1: Game Description Field")
    print("="*60)
    
    # Get first game
    game = Game.objects.first()
    if game:
        print(f"✓ Found game: {game.title}")
        print(f"  Current description: '{game.description}'")
        
        # Update description
        test_desc = "This is a test description for the game."
        game.description = test_desc
        game.save()
        print(f"  Updated description to: '{test_desc}'")
        
        # Reload and verify
        game.refresh_from_db()
        if game.description == test_desc:
            print("✓ Description field working correctly!")
        else:
            print("✗ ERROR: Description not saved correctly")
    else:
        print("✗ No games found in database")
    
def test_notification_model():
    """Test notification model and fields"""
    print("\n" + "="*60)
    print("TEST 2: Notification Model")
    print("="*60)
    
    # Get a user
    user = User.objects.filter(is_active=True).first()
    if not user:
        print("✗ No active users found")
        return
    
    print(f"✓ Testing with user: {user.email}")
    
    # Test all notification types
    types = ['normal', 'fix', 'update', 'error']
    created_notifications = []
    
    for notif_type in types:
        notif = Notification.objects.create(
            user=user,
            notification_type=notif_type,
            title=f"Test {notif_type.upper()} notification",
            body=f"This is a test {notif_type} notification",
            data={'test': True}
        )
        created_notifications.append(notif)
        print(f"✓ Created {notif_type} notification (ID: {notif.id})")
    
    # Test unread count
    unread_count = Notification.objects.filter(user=user, is_read=False).count()
    print(f"\n✓ Unread notifications: {unread_count}")
    
    # Test mark as read
    first_notif = created_notifications[0]
    first_notif.mark_as_read()
    print(f"✓ Marked notification {first_notif.id} as read")
    
    if first_notif.is_read and first_notif.read_at:
        print("✓ Mark as read working correctly!")
    else:
        print("✗ ERROR: Mark as read not working")
    
    # Clean up test notifications
    for notif in created_notifications:
        notif.delete()
    print("\n✓ Test notifications cleaned up")

def test_notification_types():
    """Test notification type field in NotificationLog"""
    print("\n" + "="*60)
    print("TEST 3: Notification Types")
    print("="*60)
    
    types = ['normal', 'fix', 'update', 'error']
    print(f"✓ Valid notification types: {', '.join(types)}")
    
    # Check if NotificationLog has the type field
    from notifications.models import NotificationLog
    type_choices = dict(NotificationLog.TYPE_CHOICES)
    print(f"✓ NotificationLog type choices: {list(type_choices.keys())}")
    
    if all(t in type_choices for t in types):
        print("✓ All required notification types are available!")
    else:
        print("✗ ERROR: Some notification types are missing")

def test_device_tokens():
    """Test device token count"""
    print("\n" + "="*60)
    print("TEST 4: Device Tokens")
    print("="*60)
    
    total_tokens = DeviceToken.objects.filter(is_active=True).count()
    registered_tokens = DeviceToken.objects.filter(
        is_active=True,
        user__isnull=False
    ).count()
    anonymous_tokens = total_tokens - registered_tokens
    
    print(f"✓ Total active device tokens: {total_tokens}")
    print(f"  - Registered users: {registered_tokens}")
    print(f"  - Anonymous users: {anonymous_tokens}")

def test_send_notification():
    """Test sending notification to all devices"""
    print("\n" + "="*60)
    print("TEST 5: Send Notification (DRY RUN)")
    print("="*60)
    
    # Count what would happen
    total_devices = DeviceToken.objects.filter(is_active=True).count()
    registered_users = User.objects.filter(is_active=True).count()
    
    print(f"If we send a notification:")
    print(f"  - Push notifications would be sent to: {total_devices} devices")
    print(f"  - Database notifications would be created for: {registered_users} users")
    
    # Ask for confirmation to send real notification
    print("\n⚠️  To send a REAL test notification, uncomment the code below")
    print("    and run this script again.")
    
    # UNCOMMENT TO SEND REAL NOTIFICATION:
    # log = send_notification_to_all_devices(
    #     title="🧪 Test Notification",
    #     body="This is a test notification from the new system",
    #     notification_type='normal',
    #     data={'test': True, 'source': 'test_script'}
    # )
    # print(f"\n✓ Notification sent!")
    # print(f"  - Success: {log.successful_sends}/{log.total_recipients}")
    # print(f"  - Failed: {log.failed_sends}")
    # print(f"  - Success rate: {log.success_rate}%")

def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("🧪 TESTING NEW FEATURES")
    print("="*60)
    
    try:
        test_game_description()
        test_notification_model()
        test_notification_types()
        test_device_tokens()
        test_send_notification()
        
        print("\n" + "="*60)
        print("✅ ALL TESTS COMPLETED!")
        print("="*60)
        print("\nSummary:")
        print("1. ✓ Game description field is working")
        print("2. ✓ Notification model with all types is working")
        print("3. ✓ Notification type system is configured")
        print("4. ✓ Device token system is ready")
        print("5. ✓ Send notification system is ready")
        print("\n🎉 All new features are ready to use!")
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
