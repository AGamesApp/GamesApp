# 🚀 Quick Start Guide - Support & Notifications

## What's New?

### Support Messages System ✅
- Users can submit support requests via API
- Admins can view and manage messages in custom dashboard
- One-click review functionality
- Automatic message ordering (pending → reviewed)
- Beautiful dark-themed interface

### Enhanced Notifications ✅
- Custom admin dashboard integration
- Live preview when sending notifications
- Support for title, message, and optional images
- Active device count tracking

## 🎯 Quick Test (5 Minutes)

### 1. Start the Server
```bash
python manage.py runserver
```

### 2. Login to Custom Admin
- URL: http://localhost:8000/customadmin/
- Use your superuser credentials

### 3. Check Support Messages
- Click **💬 Support** tab in navigation
- You'll see 5 test messages (created by test script)
- All are in "Pending" status (yellow indicator)

### 4. Test Review Workflow
1. Click "✓ Mark as Reviewed" on any message
2. Watch it move to the bottom with green indicator
3. See review footer: "Reviewed by [your username] on [timestamp]"
4. Go back to Dashboard - pending count decreased by 1

### 5. Test Notifications
1. Click **📱 Notifications** tab
2. Fill in the form:
   - **Title**: "Test Notification"
   - **Content**: "This is a test message"
   - **Image URL** (optional): https://images.unsplash.com/photo-1511512578047-dfb367046420?w=500
3. Watch live preview update as you type
4. Click "Send Notification"
5. See success message with delivery stats

## 📊 Dashboard Overview

The main dashboard now shows 6 cards:

1. **🎯 Games** - Total games count
2. **💻 Emulators** - Total emulators count
3. **🏷️ Genres** - Total genres count
4. **📄 Pages** - Total pages count
5. **📱 Push Notifications** - Active devices count → Send Notification
6. **💬 Support Messages** - Pending messages count → View Messages ✨ NEW!

## 🔌 API Quick Reference

### Submit Support Message
```bash
POST /api/support/api/messages/
Content-Type: application/json

{
  "name": "John Doe",
  "email": "john@example.com",
  "subject": "Need Help",
  "message": "I have a question..."
}
```

### Send Push Notification (Python)
```python
from notifications.fcm_service import send_notification_to_all_devices

log = send_notification_to_all_devices(
    title="📬 New Message",
    body="Thank you for your message!",
    image_url="https://example.com/image.jpg"  # optional
)

print(f"Sent: {log.successful_sends}, Failed: {log.failed_sends}")
```

## 📱 Testing Notifications

### Current Status
- 3 test devices registered (from demo)
- Test tokens will fail with 404 (expected)
- For real testing, use actual FCM tokens

### Register Real Device
```bash
POST /api/notifications/register/
Authorization: Token <user_token>
Content-Type: application/json

{
  "fcm_token": "<your_real_fcm_token>",
  "platform": "android"  # or "ios", "web"
}
```

## 🎨 UI Features

### Support Messages List
- **Filter Tabs**: All, Pending (yellow badge), Reviewed (green badge)
- **Message Cards**: 
  - Yellow left border = Pending
  - Green left border = Reviewed
  - Hover effect: lift & shadow
- **Automatic Ordering**: Pending at top, reviewed at bottom
- **One-Click Review**: Toggle button switches status

### Notification Form
- **Title** (required, max 200 chars)
- **Content** (required, max 500 chars)
- **Image URL** (optional, validated)
- **Live Preview**: Updates as you type
- **Success Feedback**: Shows delivery statistics

## 📁 Key Files

### Support System
```
support/
├── models.py              # SupportMessage model
├── views.py               # API & custom admin views
├── serializers.py         # API serializers
├── urls.py                # API routes
└── admin.py               # Django admin

customadmin/
├── templates/customadmin/
│   ├── base.html          # Added Support tab
│   ├── dashboard.html     # Added support card
│   └── support_messages_list.html  # Support interface
├── views.py               # Added support context
└── urls.py                # Added support routes
```

### Notifications
```
notifications/
├── models.py              # DeviceToken, NotificationLog
├── fcm_service.py         # FCM integration
├── views.py               # API views
└── urls.py                # API routes

customadmin/templates/customadmin/
└── notification_send.html # Notification form
```

## ✅ Test Checklist

Run this checklist to verify everything works:

- [ ] Server starts without errors
- [ ] Can login to `/customadmin/`
- [ ] Dashboard shows 6 cards including Support
- [ ] Support Messages tab accessible
- [ ] 5 test messages visible
- [ ] Can filter by All/Pending/Reviewed
- [ ] Can mark message as reviewed
- [ ] Reviewed message moves to bottom
- [ ] Pending count updates in dashboard
- [ ] Notifications tab accessible
- [ ] Can fill notification form
- [ ] Live preview updates
- [ ] Can send notification
- [ ] Success message shows delivery stats

## 🐛 Troubleshooting

### Support messages not showing?
```bash
# Check database
python manage.py dbshell
SELECT COUNT(*) FROM support_supportmessage;

# Run test script again
python test_support_and_notifications.py
```

### Notification sending fails?
- Check `serviceAccountKey.json` exists in project root
- Verify `FIREBASE_CREDENTIALS_PATH` in settings.py
- Test tokens from demo will fail (expected)
- Register real devices for actual testing

### Dashboard not updating?
- Hard refresh browser (Ctrl+F5)
- Check browser console for errors
- Verify migrations ran: `python manage.py migrate`

## 📊 Database Schema

### SupportMessage Table
```sql
- id (PK)
- user_id (FK, nullable)
- name (varchar 200)
- email (email)
- subject (varchar 300)
- message (text)
- status (varchar 20: 'pending'|'reviewed')
- is_reviewed (boolean, indexed)
- reviewed_at (datetime, nullable)
- reviewed_by_id (FK, nullable)
- admin_notes (text)
- created_at (datetime, indexed)
- updated_at (datetime)

Indexes:
- (is_reviewed, -created_at)
- (status, -created_at)

Ordering: is_reviewed ASC, created_at DESC
```

## 🎓 Usage Examples

### Example 1: User Submits Issue
```python
# Mobile app calls API
POST /api/support/api/messages/
{
  "name": "Alice",
  "email": "alice@example.com",
  "subject": "Can't login",
  "message": "App crashes when I click login"
}

# Admin sees in dashboard: "1" pending message
# Admin clicks Support → sees message
# Admin clicks "✓ Mark as Reviewed"
# Message marked, moves to bottom
```

### Example 2: Auto-notify on Submit
```python
# In your view after creating support message
from notifications.fcm_service import send_notification_to_all_devices

# Create message
message = SupportMessage.objects.create(...)

# Auto-notify admins (if you have admin devices)
send_notification_to_all_devices(
    title="📬 New Support Message",
    body=f"{message.name}: {message.subject}",
    notification_type='support_new'
)
```

### Example 3: Notify User When Reviewed
```python
# When admin marks as reviewed
message.mark_as_reviewed(admin_user=request.user)

# Send confirmation to user (if registered)
if message.user and message.user.device_tokens.filter(is_active=True).exists():
    send_notification_to_all_devices(
        title="✅ Support Update",
        body=f"Your message '{message.subject}' has been reviewed!",
        user=message.user,  # Send only to this user
        notification_type='support_reviewed'
    )
```

## 🚀 Production Checklist

Before deploying to production:

- [ ] Replace test FCM tokens with real ones
- [ ] Set up proper Firebase project
- [ ] Configure `serviceAccountKey.json` securely
- [ ] Set up email notifications for support messages
- [ ] Add rate limiting to API endpoints
- [ ] Configure CORS properly
- [ ] Set up monitoring for notification failures
- [ ] Add admin email alerts for new support messages
- [ ] Configure backup for support messages
- [ ] Add export functionality for support data

## 📚 Documentation Files

- **SUPPORT_SYSTEM_GUIDE.md** - Complete system documentation
- **DASHBOARD_NOTIFICATION_IMPLEMENTATION.md** - Notification dashboard guide
- **NOTIFICATION_SYSTEM_SETUP.md** - Firebase setup guide
- **QUICK_START.md** - This file

## 🎉 Success!

You now have a complete support and notification system:

✅ **Support Messages**
- API for user submissions
- Custom admin dashboard
- Review workflow
- Status tracking

✅ **Push Notifications**
- Firebase integration
- Custom admin form
- Live preview
- Image support

✅ **Testing**
- 5 sample support messages
- Notification test suite
- Comprehensive guides

**Ready to use!** 🚀

---

**Need Help?**
- Check the guides in the project root
- Review API documentation
- Test with the provided scripts
- Check Django admin at `/admin/` for raw data access
