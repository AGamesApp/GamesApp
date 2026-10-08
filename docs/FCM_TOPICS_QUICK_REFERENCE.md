# Quick Reference: Switching to FCM Topics

## For Developers: How to Use the New Topic-Based Notifications

---

## 🚀 Quick Start

### Before (Token-based - OLD)
```python
from notifications.fcm_service import send_notification_to_all_devices

log = send_notification_to_all_devices(
    title='New Game Available',
    body='Check out our latest game!',
    notification_type='normal',
    image_url='https://example.com/game.jpg',
    data={'game_id': '123'}
)
```

### After (Topic-based - NEW)
```python
from notifications.fcm_service import send_notification_to_all_users_topic

log = send_notification_to_all_users_topic(
    title='New Game Available',
    body='Check out our latest game!',
    notification_type='normal',
    image_url='https://example.com/game.jpg',
    data={'game_id': '123'}
)
```

**That's it! Just change the function name.** ✨

---

## 📋 Complete Comparison

| Feature | Token-based | Topic-based |
|---------|-------------|-------------|
| Function | `send_notification_to_all_devices()` | `send_notification_to_all_users_topic()` |
| API Calls | Multiple (n/500) | Single (1) |
| Performance | Slower | Faster |
| Scalability | Limited | Unlimited |
| Parameters | Same | Same |
| Return Value | NotificationLog | NotificationLog |
| Database Notifications | ✅ Yes | ✅ Yes |
| Push Notifications | ✅ Yes | ✅ Yes |

---

## 🔧 Migration Steps

### Step 1: Run Migration Script
```bash
# Dry run first (recommended)
python manage.py migrate_tokens_to_topic --dry-run

# Actual migration
python manage.py migrate_tokens_to_topic
```

**Output:**
```
📊 Found 2004 active device tokens
✅ Successfully subscribed: 2004
🎉 All tokens successfully subscribed!
```

### Step 2: Update Your Code

**Example: Admin Dashboard Notification View**

File: `customadmin/views.py`

```python
# BEFORE
from notifications.fcm_service import send_notification_to_all_devices

class NotificationSendView(LoginRequiredMixin, View):
    def post(self, request):
        # ... form validation ...
        
        log = send_notification_to_all_devices(
            title=title,
            body=body,
            notification_type=notification_type,
            image_url=image_url,
            data=data
        )
        
        messages.success(request, f'✅ Sent to {log.successful_sends} devices')
        return redirect('customadmin:notification_send')


# AFTER
from notifications.fcm_service import send_notification_to_all_users_topic

class NotificationSendView(LoginRequiredMixin, View):
    def post(self, request):
        # ... form validation ...
        
        log = send_notification_to_all_users_topic(
            title=title,
            body=body,
            notification_type=notification_type,
            image_url=image_url,
            data=data
        )
        
        messages.success(request, '✅ Notification sent to all users!')
        return redirect('customadmin:notification_send')
```

---

## 📱 Client-Side Setup

### React Native

```javascript
import messaging from '@react-native-firebase/messaging';

async function setupPushNotifications() {
  // Request permission
  const authStatus = await messaging().requestPermission();
  
  // Subscribe to topic
  await messaging().subscribeToTopic('all_users');
  
  // Get token
  const token = await messaging().getToken();
  
  // Register with backend
  await fetch('https://yourapi.com/api/device-tokens/', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
      token: token,
      platform: Platform.OS,
      subscribed_to_all_users: true
    })
  });
}

// Call on app start
useEffect(() => {
  setupPushNotifications();
}, []);
```

### Flutter

```dart
import 'package:firebase_messaging/firebase_messaging.dart';

class NotificationService {
  final FirebaseMessaging _messaging = FirebaseMessaging.instance;
  
  Future<void> setupPushNotifications() async {
    // Request permission
    await _messaging.requestPermission();
    
    // Subscribe to topic
    await _messaging.subscribeToTopic('all_users');
    
    // Get token
    String? token = await _messaging.getToken();
    
    // Register with backend
    await http.post(
      Uri.parse('https://yourapi.com/api/device-tokens/'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'token': token,
        'platform': Platform.isAndroid ? 'android' : 'ios',
        'subscribed_to_all_users': true,
      }),
    );
  }
}

// Call in main.dart
void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await Firebase.initializeApp();
  
  final notificationService = NotificationService();
  await notificationService.setupPushNotifications();
  
  runApp(MyApp());
}
```

---

## 🧪 Testing

### Test 1: Send Notification via Django Shell
```python
python manage.py shell

from notifications.fcm_service import send_notification_to_all_users_topic

log = send_notification_to_all_users_topic(
    title='🧪 Test Notification',
    body='Testing FCM Topics!',
    notification_type='normal'
)

print(f"Success: {log.successful_sends}, Failed: {log.failed_sends}")
```

### Test 2: Send via Admin Dashboard
1. Go to: `/admin/notifications/send/`
2. Fill in notification details
3. Click "Send Notification"
4. Verify on your mobile device

### Test 3: Check Firebase Console
1. Go to Firebase Console
2. Navigate to: Cloud Messaging → Topics
3. Verify 'all_users' topic shows subscriber count

---

## 📊 Monitoring

### View Notification Logs
```python
from notifications.models import NotificationLog

# Recent notifications
recent = NotificationLog.objects.order_by('-created_at')[:10]

for log in recent:
    print(f"{log.title}: {log.successful_sends} sent, {log.failed_sends} failed")
```

### Check Django Logs
```bash
# View topic notifications
tail -f logs/django.log | grep "Topic notification sent"

# Output example:
# Topic notification sent: New Game | Topic: all_users | Status: SUCCESS
```

---

## 🔄 Both Methods Available

You can use both methods during transition!

```python
# For ALL users (recommended - use topics)
from notifications.fcm_service import send_notification_to_all_users_topic

send_notification_to_all_users_topic(
    title='Game Update',
    body='New features available!',
    notification_type='update'
)

# For SPECIFIC user (use tokens)
from notifications.fcm_service import send_notification_to_all_devices

send_notification_to_all_devices(
    title='Personal Message',
    body='Your request is ready!',
    notification_type='normal',
    user=specific_user  # Send to one user only
)
```

---

## ⚡ Performance Gains

### Scenario: 2,000 Active Users

**Token-based (OLD):**
- API Calls: 4 (batches of 500)
- Average Latency: ~2-3 seconds
- Code Complexity: High (batch management)

**Topic-based (NEW):**
- API Calls: 1
- Average Latency: ~0.5-1 second
- Code Complexity: Low (single call)

### Scenario: 10,000 Active Users

**Token-based (OLD):**
- API Calls: 20
- Average Latency: ~10-15 seconds
- Risk of timeout

**Topic-based (NEW):**
- API Calls: 1
- Average Latency: ~0.5-1 second
- No timeout risk

---

## ❓ Common Questions

**Q: Do I need to update all mobile apps immediately?**  
A: No! The migration script subscribes existing tokens. Users with old app versions will still receive notifications.

**Q: What if I want to keep the old method?**  
A: It still works! Use `send_notification_to_all_devices()` anytime.

**Q: Can I send to specific users with topics?**  
A: For specific users, use the token-based method. Topics are for broadcasting to ALL users.

**Q: How do I know it's working?**  
A: Send a test notification and check multiple devices. Also check Firebase Console → Topics.

---

## 🎯 Summary

### What Changed
- ✅ New function: `send_notification_to_all_users_topic()`
- ✅ Migration script: `migrate_tokens_to_topic`
- ✅ Same parameters, better performance

### What Didn't Change
- ✅ Database notifications still created
- ✅ NotificationLog still saved
- ✅ Images, data, notification types all work the same
- ✅ Admin dashboard interface unchanged

### Next Steps
1. Run migration: `python manage.py migrate_tokens_to_topic`
2. Update code: Change function name
3. Test: Send notification and verify
4. Monitor: Check logs and Firebase Console

---

**That's it! Your notification system is now optimized! 🎉**
