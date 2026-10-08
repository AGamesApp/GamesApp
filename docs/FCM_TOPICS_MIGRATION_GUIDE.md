# FCM Topics Migration Guide

## Overview

This guide covers the complete migration from **token-based** push notifications to **FCM Topics** for broadcasting messages to all users. This optimization reduces API calls from O(n/500) to O(1), significantly improving performance and reducing latency.

---

## Table of Contents

1. [Why FCM Topics?](#why-fcm-topics)
2. [Architecture Changes](#architecture-changes)
3. [Implementation Steps](#implementation-steps)
4. [Backend Changes](#backend-changes)
5. [Client-Side Integration](#client-side-integration)
6. [Migration Process](#migration-process)
7. [Testing](#testing)
8. [Rollback Plan](#rollback-plan)

---

## Why FCM Topics?

### Current Approach (Token-based)
- Fetches all active device tokens from database
- Sends notifications in batches of 500 tokens
- **Example:** 2,000 devices = 4 API calls
- Higher latency for all users
- More complex error handling

### New Approach (Topic-based)
- All devices subscribe to 'all_users' topic
- Single API call to send to topic
- **Example:** 2,000 devices = 1 API call
- Lower latency across all devices
- Simpler code and error handling

### Performance Comparison

| Metric | Token-based | Topic-based | Improvement |
|--------|-------------|-------------|-------------|
| API Calls (2K devices) | 4 | 1 | 75% reduction |
| API Calls (10K devices) | 20 | 1 | 95% reduction |
| Average Latency | High | Low | Significant |
| Code Complexity | High | Low | Much simpler |
| Scalability | Limited | Excellent | Unlimited |

---

## Architecture Changes

### Before (Token-based)
```
Admin Dashboard
    ↓
send_notification_to_all_devices()
    ↓
Fetch ALL tokens from DB
    ↓
Batch into groups of 500
    ↓
Send to FCM (multiple calls)
    ↓
Handle responses per batch
```

### After (Topic-based)
```
Admin Dashboard
    ↓
send_notification_to_all_users_topic()
    ↓
Send to 'all_users' topic
    ↓
Single FCM API call
    ↓
FCM delivers to all subscribers
```

---

## Implementation Steps

### Phase 1: Backend Updates ✅

1. **Enhanced FCM Service** (`notifications/fcm_service.py`)
   - Added `TOPIC_ALL_USERS = 'all_users'` constant
   - Enhanced `send_to_topic()` method with full notification payload
   - Created `send_notification_to_all_users_topic()` function

2. **Migration Command** (`notifications/management/commands/migrate_tokens_to_topic.py`)
   - Subscribes existing device tokens to 'all_users' topic
   - Handles batches of up to 1,000 tokens (FCM limit)
   - Provides dry-run mode for testing
   - Automatic error handling and reporting

### Phase 2: Client-Side Updates

1. **React Native** (`docs/client-side-fcm-topics-react-native.js`)
   - Auto-subscribe on app initialization
   - Register device token with backend
   - Handle topic subscription status

2. **Flutter** (`docs/client-side-fcm-topics-flutter.dart`)
   - NotificationService class
   - Auto-subscribe on app start
   - Cross-platform support (iOS/Android)

### Phase 3: Migration Execution

1. Run migration script for existing tokens
2. Update mobile apps with new topic subscription code
3. Switch notification sending to use topic-based function
4. Monitor and validate delivery

---

## Backend Changes

### New Functions

#### 1. Enhanced `send_to_topic()` Method
```python
fcm_service = FCMService()
fcm_service.send_to_topic(
    topic='all_users',
    title='Game Update',
    body='New features available!',
    notification_type='update',
    image_url='https://example.com/image.jpg',
    data={'game_id': '123'}
)
```

**Features:**
- Full notification payload (title, body, image)
- Platform-specific configurations (Android/iOS)
- Custom data payload
- Notification type support
- Image support

#### 2. New `send_notification_to_all_users_topic()` Function
```python
from notifications.fcm_service import send_notification_to_all_users_topic

log = send_notification_to_all_users_topic(
    title='New Game Added',
    body='Check out Amazing Game now!',
    notification_type='normal',
    image_url='https://example.com/game.jpg',
    data={'game_id': '456', 'action': 'view_game'}
)
```

**Benefits:**
- Single API call for all users
- Automatic database notification creation
- Notification logging
- Backward compatible with existing code

### Migration Command

```bash
# Dry run (see what would happen)
python manage.py migrate_tokens_to_topic --dry-run

# Actual migration (default batch size: 1000)
python manage.py migrate_tokens_to_topic

# Custom batch size
python manage.py migrate_tokens_to_topic --batch-size 500
```

**Output Example:**
```
======================================================================
FCM Topic Migration Script
======================================================================

📊 Found 2004 active device tokens
📦 Batch size: 1000 tokens per batch
🎯 Target topic: all_users

⚠️  This will subscribe all tokens to the FCM topic.
Do you want to continue? (yes/no): yes

🚀 Starting migration...

Processing batch 1 (1000 tokens)... ✅ 1000 succeeded
Processing batch 2 (1000 tokens)... ✅ 1000 succeeded
Processing batch 3 (4 tokens)... ✅ 4 succeeded

======================================================================
📊 Migration Summary
======================================================================
Total tokens processed: 2004
✅ Successfully subscribed: 2004
🎉 All tokens successfully subscribed!
Success rate: 100.00%

======================================================================
✅ Migration completed!
======================================================================
```

---

## Client-Side Integration

### React Native Implementation

See: `docs/client-side-fcm-topics-react-native.js`

**Key Points:**
1. Install: `@react-native-firebase/messaging`
2. Call `setupPushNotifications()` on app start
3. Auto-subscribes to 'all_users' topic
4. Registers token with backend (includes `subscribed_to_all_users: true`)

**Integration:**
```javascript
import { setupPushNotifications } from './services/notifications';

// In App.js or similar
useEffect(() => {
  setupPushNotifications();
}, []);
```

### Flutter Implementation

See: `docs/client-side-fcm-topics-flutter.dart`

**Key Points:**
1. Add `firebase_messaging` dependency
2. Initialize `NotificationService` on app start
3. Auto-subscribes to topic
4. Handles both iOS and Android

**Integration:**
```dart
import 'services/notification_service.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await Firebase.initializeApp();
  
  final notificationService = NotificationService();
  await notificationService.setupPushNotifications();
  
  runApp(MyApp());
}
```

---

## Migration Process

### Step-by-Step Migration

#### Step 1: Backup Current System
```bash
# Backup database
pg_dump gamezone_db > backup_before_fcm_migration.sql

# Backup current code (commit to git)
git add .
git commit -m "Backup before FCM Topics migration"
git tag before-fcm-topics
```

#### Step 2: Deploy Backend Changes
Backend changes are already implemented in:
- `notifications/fcm_service.py` ✅
- `notifications/management/commands/migrate_tokens_to_topic.py` ✅

No deployment needed - code is ready!

#### Step 3: Run Migration Script (Dry Run)
```bash
# Test migration without making changes
python manage.py migrate_tokens_to_topic --dry-run
```

Review output to verify token count and expected batches.

#### Step 4: Run Actual Migration
```bash
# Subscribe all existing tokens to 'all_users' topic
python manage.py migrate_tokens_to_topic
```

**Expected Duration:** ~5-10 seconds for 2,000 tokens

#### Step 5: Update Mobile Apps

**React Native:**
1. Update notification service with code from `docs/client-side-fcm-topics-react-native.js`
2. Test on development build
3. Deploy to production

**Flutter:**
1. Update notification service with code from `docs/client-side-fcm-topics-flutter.dart`
2. Test on development build
3. Deploy to production

#### Step 6: Update Admin Dashboard

Modify `customadmin/views.py` to use the new topic-based function:

```python
# OLD (token-based)
from notifications.fcm_service import send_notification_to_all_devices
log = send_notification_to_all_devices(...)

# NEW (topic-based)
from notifications.fcm_service import send_notification_to_all_users_topic
log = send_notification_to_all_users_topic(...)
```

#### Step 7: Verification

1. Send test notification from admin dashboard
2. Verify receipt on multiple devices (iOS + Android)
3. Check Firebase Console for topic statistics
4. Review notification logs in database

---

## Testing

### Pre-Migration Testing

1. **Count Active Tokens**
```python
from notifications.models import DeviceToken
active_count = DeviceToken.objects.filter(is_active=True).count()
print(f"Active tokens: {active_count}")
```

2. **Dry Run Migration**
```bash
python manage.py migrate_tokens_to_topic --dry-run
```

### Post-Migration Testing

1. **Verify Topic Subscriptions**
   - Check Firebase Console → Cloud Messaging → Topics
   - Topic 'all_users' should show subscriber count

2. **Send Test Notification**
```python
from notifications.fcm_service import send_notification_to_all_users_topic

log = send_notification_to_all_users_topic(
    title='Test Topic Notification',
    body='If you receive this, topics are working!',
    notification_type='normal'
)
print(f"Success: {log.successful_sends}, Failed: {log.failed_sends}")
```

3. **Test on Multiple Devices**
   - iOS device (physical or simulator)
   - Android device (physical or emulator)
   - Verify both receive notification within 1-2 seconds

4. **Monitor Logs**
```bash
tail -f logs/django.log | grep -i "topic"
```

### Load Testing

Send multiple notifications to verify scalability:
```python
for i in range(10):
    send_notification_to_all_users_topic(
        title=f'Load Test {i+1}',
        body=f'Testing notification {i+1}',
        notification_type='normal'
    )
```

---

## Rollback Plan

If issues arise, you can rollback:

### Option 1: Use Old Function
Simply continue using `send_notification_to_all_devices()` - it still works!

### Option 2: Restore from Backup
```bash
# Restore database
psql gamezone_db < backup_before_fcm_migration.sql

# Restore code
git reset --hard before-fcm-topics
```

### Option 3: Hybrid Approach
Use both methods during transition:
```python
# Send to both topics AND individual tokens (belt and suspenders)
from notifications.fcm_service import (
    send_notification_to_all_users_topic,
    send_notification_to_all_devices
)

# Topic-based (new users with app update)
send_notification_to_all_users_topic(...)

# Token-based (old users without app update)
send_notification_to_all_devices(...)
```

---

## Monitoring & Maintenance

### Firebase Console
- Navigate to: Firebase Console → Cloud Messaging → Topics
- View subscriber count for 'all_users' topic
- Monitor delivery rates and errors

### Django Admin
- Check NotificationLog entries
- Monitor successful_sends vs failed_sends
- Review notification delivery patterns

### Logs
```bash
# View topic-related logs
grep -i "topic" logs/django.log

# View notification success/failure
grep -i "notification sent" logs/django.log
```

---

## FAQ

**Q: What happens to users who don't update their app?**  
A: They remain subscribed to the topic from the migration script. New notifications will still reach them.

**Q: Can I use both methods during transition?**  
A: Yes! Both functions work independently. You can use topic-based for new notifications while maintaining token-based as backup.

**Q: How do I know if a device is subscribed to the topic?**  
A: Check the backend registration - the client sends `subscribed_to_all_users: true` when registering. You can also check Firebase Console.

**Q: What if the migration script fails?**  
A: It processes in batches and continues on errors. Failed tokens are logged. You can re-run the script - it won't duplicate subscriptions.

**Q: Can I subscribe users to multiple topics?**  
A: Yes! Topics are independent. You could have 'all_users', 'premium_users', 'beta_testers', etc.

**Q: Is there a cost difference?**  
A: No - FCM is free for both methods. Topics just use fewer API calls.

**Q: How long does migration take?**  
A: Very fast - about 5-10 seconds for 2,000 tokens.

---

## Next Steps

1. ✅ Backend code implemented
2. ✅ Migration script created
3. ⏳ Run migration on production database
4. ⏳ Update mobile apps with topic subscription
5. ⏳ Update admin dashboard to use new function
6. ⏳ Monitor and verify delivery

---

## Support

For issues or questions:
1. Check logs: `logs/django.log`
2. Review Firebase Console for delivery stats
3. Test with `send_notification_to_all_users_topic()` in Django shell

---

**Last Updated:** 2024  
**Version:** 1.0  
**Status:** Ready for Production
