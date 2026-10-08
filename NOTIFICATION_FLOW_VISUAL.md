# Notification System - Visual Guide

## 📱 Complete Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    USER DOWNLOADS APP                           │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    APP OPENS FIRST TIME                          │
│                                                                  │
│  [Firebase SDK automatically generates device token]             │
│  Token: "abc123xyz..."                                          │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│              APP SENDS TOKEN TO YOUR BACKEND                     │
│                                                                  │
│  POST https://games.agames.cv/api/device-tokens/                      │
│  {                                                              │
│    "token": "abc123xyz...",                                     │
│    "platform": "android",                                       │
│    "device_id": "device-unique-id"                              │
│  }                                                              │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                BACKEND STORES TOKEN                             │
│                                                                  │
│  DeviceToken Table:                                             │
│  ┌────┬──────────────┬─────────┬──────────┬───────────┐        │
│  │ ID │ Token        │ User    │ Platform │ Active    │        │
│  ├────┼──────────────┼─────────┼──────────┼───────────┤        │
│  │ 1  │ abc123xyz... │ NULL    │ android  │ true      │ ←─┐    │
│  └────┴──────────────┴─────────┴──────────┴───────────┘   │    │
│                                                             │    │
│  ✓ Token stored! User can now receive notifications  ──────┘    │
│  ✗ No account needed at this point                             │
└─────────────────────────────────────────────────────────────────┘
                              ↓
                    ┌─────────┴─────────┐
                    │                   │
                    ↓                   ↓
    ┌───────────────────────┐  ┌──────────────────────┐
    │  User stays anonymous │  │  User creates account│
    │  (just uses app)      │  │  (registers/logs in) │
    └───────────────────────┘  └──────────────────────┘
                    │                   │
                    │                   ↓
                    │          ┌─────────────────────┐
                    │          │ Update token record │
                    │          │ user_id = 5         │
                    │          └─────────────────────┘
                    │                   │
                    └─────────┬─────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                 ADMIN SENDS NOTIFICATION                         │
│                                                                  │
│  Admin Dashboard: https://games.agames.cv/custom-admin/notifications/  │
│  ┌──────────────────────────────────────────────┐              │
│  │ Title: "New Games Added!"                    │              │
│  │ Message: "Check out 50 new games"            │              │
│  │ Type: [Update ▼]                             │              │
│  │ [Send Notification]                          │              │
│  └──────────────────────────────────────────────┘              │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│              BACKEND PROCESSES NOTIFICATION                      │
│                                                                  │
│  Step 1: Get ALL active device tokens                          │
│  tokens = DeviceToken.objects.filter(is_active=True)           │
│                                                                  │
│  Step 2: Get registered users                                  │
│  users = User.objects.filter(is_active=True)                   │
│                                                                  │
│  Step 3: Send push to ALL devices via Firebase                 │
│  Step 4: Save to database for registered users only            │
└─────────────────────────────────────────────────────────────────┘
                              ↓
                    ┌─────────┴─────────┐
                    │                   │
                    ↓                   ↓
    ┌───────────────────────────────────────────────────┐
    │           ANONYMOUS USER DEVICE                   │
    │  ┌─────────────────────────────────────────┐     │
    │  │  📱 Push Notification                    │     │
    │  │  ────────────────────────────────        │     │
    │  │  🎮 Game Zone                            │     │
    │  │  New Games Added!                        │     │
    │  │  Check out 50 new games                  │     │
    │  └─────────────────────────────────────────┘     │
    │                                                   │
    │  ✓ Received push notification                    │
    │  ✗ Not saved to database (no account)            │
    └───────────────────────────────────────────────────┘

    ┌───────────────────────────────────────────────────┐
    │        REGISTERED USER DEVICE                     │
    │  ┌─────────────────────────────────────────┐     │
    │  │  📱 Push Notification                    │     │
    │  │  ────────────────────────────────────    │     │
    │  │  🎮 Game Zone                            │     │
    │  │  New Games Added!                        │     │
    │  │  Check out 50 new games                  │     │
    │  └─────────────────────────────────────────┘     │
    │                                                   │
    │  ✓ Received push notification                    │
    │  ✓ Also saved to database                        │
    │  ✓ Can view in app notification center           │
    │  ✓ Can mark as read/unread                       │
    └───────────────────────────────────────────────────┘
```

---

## 📊 Database Example

### Before Sending Notification

**DeviceToken Table (100 devices):**
```
ID  | Token        | User    | Platform | Active
----|--------------|---------|----------|--------
1   | abc123...    | NULL    | android  | true    ← Anonymous user
2   | def456...    | NULL    | ios      | true    ← Anonymous user
3   | ghi789...    | 5       | android  | true    ← User John
4   | jkl012...    | 7       | ios      | true    ← User Mary
...
100 | xyz999...    | NULL    | android  | true    ← Anonymous user
```

**User Table (30 users):**
```
ID | Email              | Name
---|--------------------|---------
5  | john@email.com     | John
7  | mary@email.com     | Mary
...
```

### After Sending Notification

**Push Notifications Sent:**
- ✅ Sent to ALL 100 devices
- ✅ Anonymous users (70 devices) received push
- ✅ Registered users (30 devices) received push

**Database Notifications Created:**
```sql
Notification Table:
ID  | User | Type   | Title            | Read
----|------|--------|------------------|------
1   | 5    | update | New Games Added! | false
2   | 7    | update | New Games Added! | false
...
30  | 45   | update | New Games Added! | false
```

**Result:**
- 100 push notifications sent ✅
- 30 database records created (only for registered users) ✅

---

## 🎯 Key Points

### 1. Device Token ≠ User Account
```
Device Token → Created automatically when app opens
User Account → Created when user registers

You can have a device token WITHOUT a user account!
```

### 2. Firebase Does the Magic
```
Firebase Cloud Messaging (FCM):
- Generates unique token for each device
- Manages token lifecycle
- Delivers notifications
- Works on iOS, Android, Web

Your backend just needs to:
1. Store the token
2. Tell Firebase which tokens to notify
```

### 3. Two-Tier System
```
Tier 1: Push Notifications (Everyone)
  └─ Sent to ALL devices via Firebase
  └─ Shows on lock screen / notification bar
  └─ No login required

Tier 2: Database Storage (Registered only)
  └─ Saved in PostgreSQL database
  └─ Viewable in app notification center
  └─ Requires user account
```

---

## 💡 Simple Explanation

**Imagine your app is a radio station:**

1. **Device Token** = Radio receiver
   - Everyone who downloads the app gets a "receiver"
   - No subscription needed
   - Just download and you're ready to receive

2. **Push Notification** = Radio broadcast
   - You broadcast a message
   - Everyone with a "receiver" hears it
   - Doesn't matter if they have an account

3. **Database Notification** = Personal message
   - Only subscribers (registered users) get a personal copy
   - Saved in their account
   - Can review it later

**When you send a notification:**
- Radio broadcast → Everyone hears it (push notification)
- Personal copy → Only subscribers get it (database record)

---

## 📱 Mobile App Developer Guide

### What You Need to Do:

1. **Add Firebase to your app** (iOS/Android)
2. **Request notification permission**
3. **Get device token from Firebase**
4. **Send token to backend**

### Example Code:

```javascript
// When app starts
async function setupPushNotifications() {
  // 1. Request permission
  const permission = await requestNotificationPermission();
  
  if (permission === 'granted') {
    // 2. Get token from Firebase
    const fcmToken = await getFirebaseToken();
    
    // 3. Send to backend
    await axios.post('https://games.agames.cv/api/device-tokens/', {
      token: fcmToken,
      platform: Platform.OS,
      device_id: getDeviceId()
    });
    
    console.log('✓ Device ready for notifications');
  }
}
```

**That's it!** No user login required at this point.

---

## ❓ FAQ

**Q: Why store tokens for users without accounts?**
A: So we can send them notifications! They downloaded our app, they should get our updates.

**Q: What if they create an account later?**
A: Their existing token gets updated with their user_id. Now they get both push + database notifications.

**Q: What if they uninstall the app?**
A: Firebase marks the token as invalid. We track failures and deactivate the token automatically.

**Q: Can we send to specific groups?**
A: Yes! Filter by platform, user type, etc.
```python
# Only Android
android_tokens = DeviceToken.objects.filter(platform='android')

# Only registered users
registered_tokens = DeviceToken.objects.filter(user__isnull=False)

# Everyone (current default)
all_tokens = DeviceToken.objects.filter(is_active=True)
```

---

## ✅ Summary

**The system works because:**
1. Every device gets a Firebase token automatically
2. We store ALL tokens (not just registered users)
3. We send notifications to ALL stored tokens
4. Firebase handles the delivery
5. Bonus: Save to database for registered users

**No accounts needed for push notifications!**
**Accounts only needed for notification history!**

---

**Last Updated**: December 8, 2025
**Status**: ✅ Working
**Devices**: {{ active_devices }} ready to receive notifications
