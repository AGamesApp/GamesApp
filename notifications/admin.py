from django.contrib import admin
from django import forms
from django.shortcuts import render
from django.urls import path
from django.http import HttpResponseRedirect
from django.contrib import messages
from .models import DeviceToken, NotificationLog
from .fcm_service import send_notification_to_all_users_topic


class SendNotificationForm(forms.Form):
    """Form for sending custom notifications from admin."""
    
    title = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter notification title...',
            'class': 'vTextField',
            'style': 'width: 100%;'
        }),
        help_text="The notification title (e.g., 'Weekend Sale!')"
    )
    
    body = forms.CharField(
        widget=forms.Textarea(attrs={
            'placeholder': 'Enter notification message...',
            'class': 'vLargeTextField',
            'rows': 5,
            'style': 'width: 100%;'
        }),
        help_text="The notification message body"
    )
    
    image_url = forms.URLField(
        required=False,
        widget=forms.URLInput(attrs={
            'placeholder': 'https://example.com/image.jpg (optional)',
            'class': 'vTextField',
            'style': 'width: 100%;'
        }),
        help_text="Optional: URL of an image to display in the notification"
    )
    
    notification_type = forms.ChoiceField(
        choices=[
            ('custom', '📢 Custom Message'),
            ('engagement', '💡 User Engagement'),
            ('new_game', '🎮 New Game Announcement'),
            ('milestone', '🎉 Special Announcement'),
        ],
        initial='custom',
        widget=forms.Select(attrs={'class': 'vSelectField'}),
        help_text="Select the type of notification"
    )
    
    data_json = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'placeholder': '{"key": "value", "url": "/games/123"}',
            'class': 'vLargeTextField',
            'rows': 3,
            'style': 'width: 100%;'
        }),
        help_text='Optional: Additional data in JSON format (e.g., {"game_id": "123", "url": "/games"})'
    )


@admin.register(DeviceToken)
class DeviceTokenAdmin(admin.ModelAdmin):
    """Admin interface for device tokens."""
    
    list_display = [
        'id', 'user_email', 'platform_display', 'is_active',
        'failure_count', 'created_at', 'token_preview'
    ]
    list_filter = ['platform', 'is_active', 'created_at']
    search_fields = ['user__email', 'token', 'device_id']
    readonly_fields = ['created_at', 'updated_at', 'last_used_at']
    
    def user_email(self, obj):
        """Display user email or Anonymous."""
        return obj.user.email if obj.user else "Anonymous"
    user_email.short_description = 'User'
    
    def platform_display(self, obj):
        """Display platform with emoji."""
        emoji_map = {
            'android': '🤖',
            'ios': '🍎',
            'web': '🌐'
        }
        return f"{emoji_map.get(obj.platform, '')} {obj.get_platform_display()}"
    platform_display.short_description = 'Platform'
    
    def token_preview(self, obj):
        """Display token preview."""
        return obj.token[:30] + '...' if len(obj.token) > 30 else obj.token
    token_preview.short_description = 'Token'
    
    actions = ['deactivate_tokens', 'activate_tokens']
    
    def deactivate_tokens(self, request, queryset):
        """Deactivate selected tokens."""
        count = queryset.update(is_active=False)
        self.message_user(request, f'{count} token(s) deactivated.')
    deactivate_tokens.short_description = 'Deactivate selected tokens'
    
    def activate_tokens(self, request, queryset):
        """Activate selected tokens."""
        count = queryset.update(is_active=True, failure_count=0)
        self.message_user(request, f'{count} token(s) activated.')
    activate_tokens.short_description = 'Activate selected tokens'


@admin.register(NotificationLog)
class NotificationLogAdmin(admin.ModelAdmin):
    """Admin interface for notification logs."""
    
    list_display = [
        'id', 'notification_type_emoji', 'title', 'target_info',
        'total_devices', 'success_rate_display', 'has_image', 'created_at'
    ]
    list_filter = ['notification_type', 'sent_to_all', 'created_at']
    search_fields = ['title', 'body']
    readonly_fields = [
        'notification_type', 'title', 'body', 'image_url', 'data',
        'target_user', 'sent_to_all', 'total_devices',
        'successful_sends', 'failed_sends', 'success_rate',
        'created_at'
    ]
    
    def get_urls(self):
        """Add custom URL for sending notifications."""
        urls = super().get_urls()
        custom_urls = [
            path(
                'send-notification/',
                self.admin_site.admin_view(self.send_notification_view),
                name='notifications_send'
            ),
        ]
        return custom_urls + urls
    
    def send_notification_view(self, request):
        """Custom view for sending notifications."""
        if request.method == 'POST':
            form = SendNotificationForm(request.POST)
            if form.is_valid():
                import json
                
                title = form.cleaned_data['title']
                body = form.cleaned_data['body']
                image_url = form.cleaned_data['image_url']
                notification_type = form.cleaned_data['notification_type']
                
                # Parse data JSON if provided
                data = None
                if form.cleaned_data['data_json']:
                    try:
                        data = json.loads(form.cleaned_data['data_json'])
                    except json.JSONDecodeError:
                        messages.error(request, 'Invalid JSON format in data field')
                        return render(request, 'admin/notifications/send_notification.html', {
                            'form': form,
                            'title': 'Send Push Notification'
                        })
                
                # Send notification
                try:
                    log = send_notification_to_all_users_topic(
                        title=title,
                        body=body,
                        notification_type=notification_type,
                        data=data,
                        image_url=image_url
                    )
                    
                    messages.success(
                        request,
                        f'Notification sent successfully to all users via Topics! '
                        f'Delivered to {log.successful_sends} devices, '
                        f'{log.failed_sends} failed.'
                    )
                    return HttpResponseRedirect('../')
                except Exception as e:
                    messages.error(request, f'Error sending notification: {str(e)}')
        else:
            form = SendNotificationForm()
        
        context = {
            'form': form,
            'title': 'Send Push Notification',
            'opts': self.model._meta,
            'has_view_permission': True,
        }
        return render(request, 'admin/notifications/send_notification.html', context)
    
    def has_image(self, obj):
        """Display if notification has an image."""
        return "🖼️ Yes" if obj.image_url else "No"
    has_image.short_description = 'Image'
    
    def notification_type_emoji(self, obj):
        """Display notification type with emoji."""
        return obj.get_notification_type_display()
    notification_type_emoji.short_description = 'Type'
    
    def target_info(self, obj):
        """Display target information."""
        if obj.target_user:
            return f"👤 {obj.target_user.email}"
        elif obj.sent_to_all:
            return "🌍 All Devices"
        else:
            return "Unknown"
    target_info.short_description = 'Target'
    
    def success_rate_display(self, obj):
        """Display success rate with color coding."""
        rate = obj.success_rate
        if rate >= 90:
            color = 'green'
        elif rate >= 70:
            color = 'orange'
        else:
            color = 'red'
        return f'<span style="color: {color}; font-weight: bold;">{rate}%</span>'
    success_rate_display.short_description = 'Success Rate'
    success_rate_display.allow_tags = True
    
    def has_add_permission(self, request):
        """Prevent manual addition of logs."""
        return False
    
    def has_change_permission(self, request, obj=None):
        """Logs are read-only."""
        return False

