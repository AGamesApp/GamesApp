# 📱 Testing Notifications on Your Phone - Quick Guide

## Your Authentication Token
```
Token: 4cd5dd9b29a6299c4b37e1073827c5e993116c0e
User: saged@gmail.com
```

## 🚀 Quick Steps

### Method 1: Using Mobile App (Production Way)

**1. Get FCM Token from Your App**

For **Android** (Kotlin/Java):
```kotlin
FirebaseMessaging.getInstance().token.addOnCompleteListener { task ->
    if (task.isSuccessful) {
        val token = task.result
        Log.d("FCM Token", token)
        // Send this to your server
    }
}
```

For **iOS** (Swift):
```swift
Messaging.messaging().token { token, error in
    if let token = token {
        print("FCM Token: \(token)")
        // Send this to your server
    }
}
```

**2. Register Device via API**

Using cURL:
```bash
curl -X POST http://YOUR_SERVER_IP:8000/api/notifications/register/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Token 4cd5dd9b29a6299c4b37e1073827c5e993116c0e" \
  -d '{
    "fcm_token": "YOUR_ACTUAL_FCM_TOKEN_HERE",
    "platform": "android"
  }'
```

Or using the HTML test page:
```bash
# Open in your phone's browser:
http://YOUR_SERVER_IP:8000/phone_notification_test.html
```

**3. Send Test Notification**

From dashboard:
1. Start server: `python manage.py runserver 0.0.0.0:8000`
2. Open: `http://YOUR_IP:8000/customadmin/`
3. Click: **📱 Notifications** tab
4. Fill the form:
   - Title: "🎮 Test Notification"
   - Content: "Hello from AGames!"
   - Image URL: (optional)
5. Click "Send Notification"
6. **Check your phone!** 📱

### Method 2: Quick Test (No Mobile App Needed)

**Use Postman or HTTP client:**

**Register Device:**
```
POST http://localhost:8000/api/notifications/register/
Headers:
  Content-Type: application/json
  Authorization: Token 4cd5dd9b29a6299c4b37e1073827c5e993116c0e
  
Body:
{
  "fcm_token": "YOUR_FCM_TOKEN",
  "platform": "android"
}
```

**Send Notification:**
```
Go to: http://localhost:8000/customadmin/
Click: Notifications tab
Send test notification
```

## 🔧 Find Your Server IP

**Windows (PowerShell):**
```powershell
ipconfig
# Look for IPv4 Address (e.g., 192.168.1.100)
```

**Start Server on All Interfaces:**
```bash
python manage.py runserver 0.0.0.0:8000
```

Then access from phone:
```
http://192.168.1.100:8000/customadmin/
```

## 📋 Complete Test Checklist

- [ ] Firebase configured in mobile app
- [ ] serviceAccountKey.json in project root
- [ ] Server running: `python manage.py runserver 0.0.0.0:8000`
- [ ] Got FCM token from device
- [ ] Registered device via API
- [ ] Sent test notification from dashboard
- [ ] Received notification on phone! 🎉

## 🐛 Troubleshooting

**Notification not received?**
- ✓ Check phone has internet connection
- ✓ Verify notification permissions enabled
- ✓ Check FCM token is valid (not expired)
- ✓ Verify serviceAccountKey.json is correct
- ✓ Check server logs for errors

**Can't connect to server?**
- ✓ Phone and server on same WiFi network
- ✓ Firewall allows port 8000
- ✓ Using correct IP address
- ✓ Server running on 0.0.0.0:8000

**FCM token registration fails?**
- ✓ Check authentication token is correct
- ✓ Verify API endpoint is accessible
- ✓ Check request headers and body format

## 🎯 Example: Full Workflow

```python
# 1. Start server
python manage.py runserver 0.0.0.0:8000

# 2. From another terminal/script
python register_phone_for_notifications.py
# Copy the token: 4cd5dd9b29a6299c4b37e1073827c5e993116c0e

# 3. Get FCM token from your mobile app
# (Use the code snippets above)

# 4. Register device
curl -X POST http://192.168.1.100:8000/api/notifications/register/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Token 4cd5dd9b29a6299c4b37e1073827c5e993116c0e" \
  -d '{
    "fcm_token": "eXaMpLe_FCM_ToKeN_fRoM_yOuR_pHoNe_123456...",
    "platform": "android"
  }'

# 5. Send test notification from dashboard
# http://192.168.1.100:8000/customadmin/ → Notifications tab

# 6. Check your phone! 📱✓
```

## 🌐 Using the Test HTML Page

1. Open `phone_notification_test.html` in your phone's browser
2. Enter your server IP
3. Paste FCM token
4. Select platform
5. Click "Register Device"
6. Go to dashboard and send notification!

## ✅ Success!

Once you see the notification on your phone, you're all set! 🎉

The system is now fully functional:
- ✓ Support messages working
- ✓ Push notifications working
- ✓ Dashboard integration complete
- ✓ Real device testing ready

Happy testing! 📱🚀
