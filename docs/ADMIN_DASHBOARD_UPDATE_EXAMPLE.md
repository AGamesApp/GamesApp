# Example: Updating Admin Dashboard to Use FCM Topics

This file shows how to update the admin dashboard's notification sending view to use the new topic-based method.

## Option 1: Simple Update (Recommended)

Just change the import and function name. Everything else stays the same!

### Before (Token-based)
```python
# File: customadmin/views.py

from notifications.fcm_service import send_notification_to_all_devices

class NotificationSendView(SuperUserRequiredMixin, View):
    def post(self, request):
        # ... validation code ...
        
        try:
            log = send_notification_to_all_devices(
                title=title,
                body=body,
                notification_type=notification_type,
                data={
                    'sent_from': 'dashboard',
                    'sent_by': request.user.email
                },
                image_url=image_url if image_url else None
            )
            
            messages.success(
                request,
                f'✅ Notification sent successfully! '
                f'Delivered to {log.successful_sends} devices, '
                f'{log.failed_sends} failed. '
                f'Success rate: {log.success_rate}%'
            )
        except Exception as e:
            messages.error(request, f'Error sending notification: {str(e)}')
        
        return redirect('customadmin:notification_send')
```

### After (Topic-based)
```python
# File: customadmin/views.py

from notifications.fcm_service import send_notification_to_all_users_topic

class NotificationSendView(SuperUserRequiredMixin, View):
    def post(self, request):
        # ... validation code ...
        
        try:
            log = send_notification_to_all_users_topic(
                title=title,
                body=body,
                notification_type=notification_type,
                data={
                    'sent_from': 'dashboard',
                    'sent_by': request.user.email
                },
                image_url=image_url if image_url else None
            )
            
            messages.success(
                request,
                f'✅ Notification sent to all users! '
                f'Status: {"Success" if log.successful_sends > 0 else "Failed"}'
            )
        except Exception as e:
            messages.error(request, f'Error sending notification: {str(e)}')
        
        return redirect('customadmin:notification_send')
```

**Changes Made:**
1. Import: `send_notification_to_all_devices` → `send_notification_to_all_users_topic`
2. Function call: Same name change
3. Success message: Simplified (topics don't report individual device counts)

---

## Option 2: Both Methods (During Transition)

Keep both methods available and let admin choose:

```python
# File: customadmin/views.py

from notifications.fcm_service import (
    send_notification_to_all_devices,
    send_notification_to_all_users_topic
)

class NotificationSendView(SuperUserRequiredMixin, View):
    def post(self, request):
        title = request.POST.get('title', '').strip()
        body = request.POST.get('body', '').strip()
        image_url = request.POST.get('image_url', '').strip()
        notification_type = request.POST.get('notification_type', 'normal').strip()
        use_topics = request.POST.get('use_topics', 'true') == 'true'  # Default to topics
        
        # ... validation code ...
        
        try:
            if use_topics:
                # New method - faster, single API call
                log = send_notification_to_all_users_topic(
                    title=title,
                    body=body,
                    notification_type=notification_type,
                    data={'sent_from': 'dashboard', 'sent_by': request.user.email},
                    image_url=image_url if image_url else None
                )
                messages.success(
                    request,
                    f'✅ Notification sent via Topics! Status: {"Success" if log.successful_sends > 0 else "Failed"}'
                )
            else:
                # Old method - individual tokens
                log = send_notification_to_all_devices(
                    title=title,
                    body=body,
                    notification_type=notification_type,
                    data={'sent_from': 'dashboard', 'sent_by': request.user.email},
                    image_url=image_url if image_url else None
                )
                messages.success(
                    request,
                    f'✅ Notification sent! Delivered to {log.successful_sends} devices, '
                    f'{log.failed_sends} failed. Success rate: {log.success_rate}%'
                )
        except Exception as e:
            messages.error(request, f'Error sending notification: {str(e)}')
        
        return redirect('customadmin:notification_send')
```

**Template Addition** (customadmin/templates/customadmin/notification_send.html):
```html
<!-- Add this checkbox in the form -->
<div class="form-check mb-3">
    <input class="form-check-input" type="checkbox" id="use_topics" name="use_topics" value="true" checked>
    <label class="form-check-label" for="use_topics">
        Use Topics (faster, recommended)
    </label>
    <small class="form-text text-muted d-block">
        Topics send to all users with a single API call. Uncheck to use individual tokens (slower).
    </small>
</div>
```

---

## Option 3: Keep Original (No Changes)

**You don't have to change anything!** The old method still works perfectly.

The migration script subscribes existing tokens to the topic, so when you eventually update your mobile apps, those users will be ready. You can switch to topics whenever you're ready.

```python
# This still works - no changes needed
from notifications.fcm_service import send_notification_to_all_devices

log = send_notification_to_all_devices(
    title=title,
    body=body,
    notification_type=notification_type,
    image_url=image_url
)
```

---

## Complete Example: Full View Code

Here's the complete updated view using topics:

```python
# File: customadmin/views.py

from django.shortcuts import render, redirect
from django.contrib import messages
from django.views import View
from notifications.models import DeviceToken
from notifications.fcm_service import send_notification_to_all_users_topic

class NotificationSendView(SuperUserRequiredMixin, View):
    """Send push notification to all users via FCM Topics"""
    template_name = 'customadmin/notification_send.html'
    
    def get(self, request):
        # Get active device count for display
        active_devices = DeviceToken.objects.filter(is_active=True).count()
        
        context = {
            'active_devices': active_devices,
        }
        return render(request, self.template_name, context)
    
    def post(self, request):
        title = request.POST.get('title', '').strip()
        body = request.POST.get('body', '').strip()
        image_url = request.POST.get('image_url', '').strip()
        notification_type = request.POST.get('notification_type', 'normal').strip()
        
        # Validate required fields
        if not title or not body:
            messages.error(request, 'Title and message are required.')
            return redirect('customadmin:notification_send')
        
        # Validate notification type
        valid_types = ['normal', 'fix', 'update', 'error']
        if notification_type not in valid_types:
            notification_type = 'normal'
        
        # Validate image URL if provided
        if image_url and not (image_url.startswith('http://') or image_url.startswith('https://')):
            messages.error(request, 'Image URL must be a valid HTTP/HTTPS URL.')
            return redirect('customadmin:notification_send')
        
        try:
            # Send notification using FCM Topics (single API call)
            log = send_notification_to_all_users_topic(
                title=title,
                body=body,
                notification_type=notification_type,
                data={
                    'sent_from': 'dashboard',
                    'sent_by': request.user.email,
                    'timestamp': str(timezone.now())
                },
                image_url=image_url if image_url else None
            )
            
            # Show success message
            if log.successful_sends > 0:
                messages.success(
                    request,
                    f'✅ Notification sent to all users via Topics! '
                    f'Check Firebase Console for delivery statistics.'
                )
            else:
                messages.error(
                    request,
                    f'❌ Failed to send notification. Check logs for details.'
                )
                
        except Exception as e:
            messages.error(request, f'Error sending notification: {str(e)}')
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Notification send error: {e}", exc_info=True)
        
        return redirect('customadmin:notification_send')
```

---

## Summary of Changes

### Minimal Changes (Option 1)
1. Change import line (1 line)
2. Change function name (1 line)
3. Update success message (1 line)

**Total: 3 lines changed**

### No Changes Required (Option 3)
- Keep using `send_notification_to_all_devices()`
- Everything works as before
- Can switch to topics later

---

## Testing After Changes

### 1. Send Test Notification
1. Login to admin dashboard
2. Navigate to Notifications → Send Notification
3. Fill in form:
   - Title: "Test Topic Notification"
   - Message: "Testing new topic-based system"
   - Type: Normal
4. Click "Send Notification"

### 2. Verify Receipt
- Check your mobile device
- Should receive notification within 1-2 seconds
- Check notification appears correctly

### 3. Check Logs
```bash
# Check Django logs
tail -f /root/game/logs/django.log | grep -i "topic"

# Expected output:
# Topic notification sent: Test Topic Notification | Topic: all_users | Status: SUCCESS
```

### 4. Firebase Console
1. Go to Firebase Console
2. Navigate to Cloud Messaging
3. Check 'all_users' topic statistics
4. Verify send count incremented

---

## Rollback

If you need to rollback:

```python
# Just change back to original import
from notifications.fcm_service import send_notification_to_all_devices

# And use original function
log = send_notification_to_all_devices(...)
```

Both methods work, so you can switch back and forth!

---

## Recommendation

**Use Option 1** (Simple Update) for best performance:
- Single API call
- Faster delivery
- Simpler code
- Better scalability

The old method still works if needed, but topics are the recommended approach for broadcasting to all users.
