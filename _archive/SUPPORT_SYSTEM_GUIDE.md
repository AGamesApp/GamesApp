# Support Messages System - Complete Guide

## 📋 Overview

The Support Messages system allows users to submit support requests through the API, and administrators can view, manage, and mark messages as reviewed through the custom admin dashboard.

## ✨ Features

### User Features
- ✅ Submit support messages via API
- ✅ Optional authentication (can submit anonymously)
- ✅ Auto-fill name and email from user profile (if authenticated)
- ✅ Track message status (pending/reviewed)

### Admin Features
- ✅ View all support messages in custom admin dashboard
- ✅ Filter by status (All, Pending, Reviewed)
- ✅ Mark messages as reviewed with one click
- ✅ Reviewed messages move to the bottom automatically
- ✅ View submitter details (name, email, user account)
- ✅ Track review information (who reviewed, when)
- ✅ Beautiful dark-themed UI with status badges
- ✅ Dashboard card showing pending message count

## 🗂️ File Structure

```
support/
├── __init__.py
├── admin.py                 # Django admin configuration
├── apps.py
├── models.py                # SupportMessage model
├── serializers.py           # API serializers
├── urls.py                  # API routes
├── views.py                 # API and custom admin views
└── migrations/
    └── 0001_initial.py

customadmin/
├── templates/
│   └── customadmin/
│       ├── base.html        # Updated with Support tab
│       ├── dashboard.html   # Updated with support messages card
│       └── support_messages_list.html  # Support messages interface
├── urls.py                  # Updated with support routes
└── views.py                 # Updated with support context

gamezone/
├── settings.py              # Updated with 'support' app
└── urls.py                  # Updated with support API routes
```

## 📊 Database Model

### SupportMessage

| Field | Type | Description |
|-------|------|-------------|
| id | AutoField | Primary key |
| user | ForeignKey | User who sent (optional) |
| name | CharField(200) | Name of sender |
| email | EmailField | Email for response |
| subject | CharField(300) | Message subject |
| message | TextField | Message content |
| status | CharField | 'pending' or 'reviewed' |
| is_reviewed | BooleanField | Review status flag |
| reviewed_at | DateTimeField | When reviewed |
| reviewed_by | ForeignKey | Admin who reviewed |
| admin_notes | TextField | Internal admin notes |
| created_at | DateTimeField | Creation timestamp |
| updated_at | DateTimeField | Last update timestamp |

**Ordering**: Unreviewed messages first, then by newest

**Indexes**:
- `(is_reviewed, -created_at)` - Fast filtering and sorting
- `(status, -created_at)` - Status-based queries

## 🔌 API Endpoints

### 1. Create Support Message

**Endpoint**: `POST /api/support/api/messages/`

**Authentication**: Optional (AllowAny)

**Request Body**:
```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "subject": "Game Download Issue",
  "message": "I'm having trouble downloading..."
}
```

**Response** (201 Created):
```json
{
  "id": 1,
  "user": null,
  "user_email": null,
  "name": "John Doe",
  "email": "john@example.com",
  "subject": "Game Download Issue",
  "message": "I'm having trouble downloading...",
  "status": "pending",
  "is_reviewed": false,
  "reviewed_at": null,
  "reviewed_by": null,
  "reviewed_by_username": null,
  "created_at": "2025-11-27T10:30:00Z",
  "updated_at": "2025-11-27T10:30:00Z"
}
```

**Auto-fill for Authenticated Users**:
If the request includes an authentication token:
- `user` field is automatically set
- `name` is auto-filled from user profile (if not provided)
- `email` is auto-filled from user account (if not provided)

### 2. List Support Messages (Admin Only)

**Endpoint**: `GET /api/support/api/messages/`

**Authentication**: Required (IsAdminUser)

**Query Parameters**:
- `is_reviewed=true|false` - Filter by review status
- `status=pending|reviewed` - Filter by status

**Response** (200 OK):
```json
[
  {
    "id": 1,
    "user_details": {
      "id": 5,
      "username": "testuser",
      "email": "test@example.com",
      "full_name": "Test User"
    },
    "name": "Test User",
    "email": "test@example.com",
    "subject": "Payment Issue",
    "message": "My payment failed...",
    "status": "pending",
    "is_reviewed": false,
    "reviewed_at": null,
    "reviewed_by": null,
    "reviewed_by_details": null,
    "created_at": "2025-11-27T10:30:00Z",
    "updated_at": "2025-11-27T10:30:00Z"
  }
]
```

### 3. Mark as Reviewed (Admin Only)

**Endpoint**: `POST /api/support/api/messages/{id}/mark_reviewed/`

**Authentication**: Required (IsAdminUser)

**Response** (200 OK):
```json
{
  "status": "success",
  "message": "Message marked as reviewed by admin_username"
}
```

### 4. Mark as Pending (Admin Only)

**Endpoint**: `POST /api/support/api/messages/{id}/mark_pending/`

**Authentication**: Required (IsAdminUser)

**Response** (200 OK):
```json
{
  "status": "success",
  "message": "Message marked as pending"
}
```

## 🎨 Custom Admin Dashboard

### Access

1. Navigate to: `http://localhost:8000/customadmin/`
2. Login with superuser credentials
3. Click **💬 Support** tab in navigation

### Dashboard Card

The main dashboard displays a "Support Messages" card showing:
- **Icon**: 💬
- **Label**: "Support Messages"
- **Value**: Number of pending (unreviewed) messages
- **Link**: "View Messages →" (goes to support messages list)
- **Style**: Pink gradient border

### Support Messages List

**URL**: `/customadmin/support/`

**Features**:

1. **Filter Tabs**:
   - **All Messages** - Shows total count
   - **Pending** - Shows unreviewed messages (yellow badge)
   - **Reviewed** - Shows reviewed messages (green badge)

2. **Message Cards**:
   - **Status Icon**: ● (pending) or ✓ (reviewed)
   - **Subject**: Bold title with status icon
   - **Metadata**: From, Email, Date
   - **Message Body**: Full message content
   - **Review Button**: 
     - "✓ Mark as Reviewed" (green) for pending messages
     - "Mark as Pending" (gray) for reviewed messages
   - **Review Footer**: Shows who reviewed and when (for reviewed messages)

3. **Automatic Ordering**:
   - Pending messages appear at the top
   - Reviewed messages move to the bottom
   - Within each group, newest messages first

4. **Visual Indicators**:
   - Pending: Yellow left border, full opacity
   - Reviewed: Green left border, 80% opacity

### Review Workflow

1. Admin opens Support Messages page
2. Pending messages are shown at the top with yellow indicator
3. Admin reads the message
4. Admin clicks "✓ Mark as Reviewed" button
5. Message is marked as reviewed with timestamp and admin username
6. Message moves to the bottom of the list with green indicator
7. Dashboard count updates automatically

## 🧪 Testing

### Run Test Script

```bash
python test_support_and_notifications.py
```

**What it does**:
1. ✅ Creates 5 test support messages
2. ✅ Tests push notification system with 3 scenarios
3. ✅ Shows statistics and results

**Test Messages Created**:
1. Game Download Issue (John Doe) - Anonymous
2. Payment Not Processing (Jane Smith) - Authenticated
3. Feature Request - Dark Mode (Bob Wilson) - Anonymous
4. Bug Report - Login Issue (Alice Johnson) - Authenticated
5. Great Service! (Mike Brown) - Anonymous

### Manual Testing

1. **Submit via API**:
```bash
curl -X POST http://localhost:8000/api/support/api/messages/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test User",
    "email": "test@example.com",
    "subject": "Test Subject",
    "message": "Test message content"
  }'
```

2. **View in Admin**:
   - Login to `/customadmin/`
   - Click Support tab
   - Verify message appears in Pending

3. **Mark as Reviewed**:
   - Click "✓ Mark as Reviewed"
   - Verify message moves to bottom
   - Verify green indicator
   - Verify review footer shows your username

## 📱 Push Notifications Integration

### Notification System Test Results

The test script also tests the push notification system:

1. **Test 1**: Simple welcome notification
2. **Test 2**: Notification with image (game alert)
3. **Test 3**: Support confirmation notification

**Note**: Test tokens from demo will fail with 404 errors. This is expected. For real testing:
- Use real FCM tokens from actual devices
- Register devices via `/api/notifications/register/`

### Sending Notifications

**Via Custom Admin**:
1. Go to `/customadmin/`
2. Click **📱 Notifications** tab
3. Fill in:
   - Title (required)
   - Message/Content (required)
   - Image URL (optional)
4. Preview updates in real-time
5. Click "Send Notification"

**Via API**:
```python
from notifications.fcm_service import send_notification_to_all_devices

log = send_notification_to_all_devices(
    title="📬 Support Confirmation",
    body="We received your message and will respond soon!",
    notification_type='support'
)

print(f"Sent to {log.successful_sends} devices")
```

## 🎯 Use Cases

### 1. User Submits Anonymous Support Request

```python
# User calls API without authentication
POST /api/support/api/messages/
{
  "name": "Jane Doe",
  "email": "jane@example.com",
  "subject": "Download Issue",
  "message": "Can't download game X"
}
```

### 2. Authenticated User Submits Request

```python
# User calls API with token
# name and email auto-filled
POST /api/support/api/messages/
Headers: {"Authorization": "Token abc123..."}
{
  "subject": "Subscription Problem",
  "message": "My subscription didn't renew"
}
# name/email automatically filled from user account
```

### 3. Admin Reviews Messages

```
1. Admin logs into custom admin dashboard
2. Sees "5" pending messages on Support card
3. Clicks "View Messages →"
4. Reviews pending messages at top
5. Clicks "✓ Mark as Reviewed" for each
6. Messages move to bottom with green indicator
7. Dashboard now shows "0" pending messages
```

### 4. Admin Sends Notification Response

```
1. Admin reviews support message
2. Admin goes to Notifications tab
3. Sends notification:
   Title: "Support Update"
   Message: "Your issue has been resolved!"
4. User receives push notification
```

## 🔧 Configuration

### Settings.py

Ensure `'support'` is in `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    # ...
    'support',
]
```

### URLs

Main project URLs include:
```python
path('api/support/', include('support.urls')),
```

Custom admin URLs include:
```python
path('support/', SupportMessagesListView.as_view(), name='support_messages'),
path('support/<int:message_id>/toggle/', ToggleReviewView.as_view(), name='toggle_review'),
```

## 📊 Admin Statistics

The dashboard shows:
- **Total Messages**: All support messages ever submitted
- **Pending Count**: Unreviewed messages (shown in dashboard card)
- **Reviewed Count**: Messages marked as reviewed

## 🎨 UI Features

### Color Scheme
- **Pending**: Yellow (#ffc107) - Attention needed
- **Reviewed**: Green (#28a745) - Completed
- **Background**: Dark theme (#1a1a1a, #2a2a2a)

### Animations
- Hover effects on cards (lift and shadow)
- Button hover scaling
- Smooth transitions (0.3s ease)

### Responsive Design
- Flexible card layouts
- Wrapping metadata items
- Mobile-friendly spacing

## ✅ Testing Checklist

- [x] Support app created and configured
- [x] Models migrated to database
- [x] API endpoints working
- [x] Custom admin views functional
- [x] Navigation tab added
- [x] Dashboard card showing pending count
- [x] Filter tabs working (All, Pending, Reviewed)
- [x] Mark as reviewed functionality
- [x] Messages reorder after review
- [x] Status indicators correct
- [x] Test messages created
- [x] Push notifications integrated

## 🚀 Next Steps

1. **Start the server**:
   ```bash
   python manage.py runserver
   ```

2. **Login to custom admin**:
   - URL: `http://localhost:8000/customadmin/`
   - Login with your superuser account

3. **View support messages**:
   - Click **💬 Support** tab
   - See 5 test messages in Pending status

4. **Test review functionality**:
   - Click "✓ Mark as Reviewed" on a message
   - Watch it move to the bottom
   - Verify green indicator and review footer

5. **Test notifications**:
   - Click **📱 Notifications** tab
   - Send a test notification
   - Check devices receive it

## 📝 Summary

**Created**:
- ✅ Support app with SupportMessage model
- ✅ API endpoints for creating and managing messages
- ✅ Custom admin interface with filtering
- ✅ Review workflow with toggle functionality
- ✅ Dashboard integration with pending count
- ✅ Navigation tab for easy access
- ✅ Test script with 5 sample messages
- ✅ Push notification system testing

**Features**:
- ✅ Users can submit support messages (authenticated or anonymous)
- ✅ Admins see pending messages in dashboard
- ✅ One-click review with automatic reordering
- ✅ Beautiful dark-themed UI
- ✅ Complete API with filtering
- ✅ Push notification integration ready

The support system is **fully functional** and ready for production use! 🎉
