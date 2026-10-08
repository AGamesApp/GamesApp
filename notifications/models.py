from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class DeviceToken(models.Model):
    """Store FCM device tokens for push notifications."""
    
    PLATFORM_CHOICES = [
        ('android', 'Android'),
        ('ios', 'iOS'),
        ('web', 'Web'),
    ]
    
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='device_tokens',
        null=True,
        blank=True,
        help_text="Optional - can store anonymous device tokens"
    )
    token = models.CharField(
        max_length=500, 
        unique=True,
        help_text="FCM device token"
    )
    platform = models.CharField(
        max_length=10, 
        choices=PLATFORM_CHOICES,
        default='android'
    )
    device_id = models.CharField(
        max_length=255, 
        blank=True,
        help_text="Unique device identifier"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this token is still valid"
    )
    failure_count = models.IntegerField(
        default=0,
        help_text="Number of consecutive failures"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_used_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['is_active', '-created_at']),
        ]
    
    def __str__(self):
        user_info = self.user.email if self.user else "Anonymous"
        return f"{user_info} - {self.platform} - {self.token[:20]}..."
    
    def deactivate(self):
        """Deactivate token after too many failures."""
        self.is_active = False
        self.save(update_fields=['is_active'])


class NotificationLog(models.Model):
    """Log all sent notifications for tracking and analytics."""
    
    TYPE_CHOICES = [
        ('normal', '📢 Normal'),
        ('fix', '🔧 Fix'),
        ('update', '🆙 Update'),
        ('error', '⚠️ Error'),
        ('new_game', '🎮 New Game Added'),
        ('trending', '🔥 Trending Game'),
        ('high_downloads', '📥 High Downloads'),
        ('milestone', '🎉 Milestone Reached'),
        ('new_emulator', '🕹️ New Emulator'),
        ('engagement', '💡 User Engagement'),
        ('custom', '📢 Custom'),
    ]
    
    notification_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='normal')
    title = models.CharField(max_length=200)
    body = models.TextField()
    image_url = models.URLField(
        max_length=500,
        blank=True,
        null=True,
        help_text="URL of notification image (optional)"
    )
    data = models.JSONField(
        default=dict,
        blank=True,
        help_text="Additional data payload (game_id, etc.)"
    )
    
    # Targeting
    target_user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Specific user (if targeted notification)"
    )
    sent_to_all = models.BooleanField(
        default=False,
        help_text="Whether sent to all devices"
    )
    
    # Results
    total_devices = models.IntegerField(default=0)
    successful_sends = models.IntegerField(default=0)
    failed_sends = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['notification_type', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.get_notification_type_display()} - {self.title}"
    
    @property
    def success_rate(self):
        """Calculate success rate percentage."""
        if self.total_devices == 0:
            return 0
        return round((self.successful_sends / self.total_devices) * 100, 2)


class Notification(models.Model):
    """Store notifications for registered users in the database."""
    
    TYPE_CHOICES = [
        ('normal', '📢 Normal'),
        ('fix', '🔧 Fix'),
        ('update', '🆙 Update'),
        ('error', '⚠️ Error'),
    ]
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='notifications',
        help_text="User who will receive this notification"
    )
    notification_type = models.CharField(
        max_length=20,
        choices=TYPE_CHOICES,
        default='normal',
        help_text="Type of notification"
    )
    title = models.CharField(max_length=200)
    body = models.TextField()
    image_url = models.URLField(
        max_length=500,
        blank=True,
        null=True,
        help_text="URL of notification image (optional)"
    )
    data = models.JSONField(
        default=dict,
        blank=True,
        help_text="Additional data payload (game_id, url, etc.)"
    )
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['user', 'is_read', '-created_at']),
            models.Index(fields=['notification_type', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.get_notification_type_display()} - {self.title} ({self.user.email})"
    
    def mark_as_read(self):
        """Mark notification as read."""
        if not self.is_read:
            from django.utils import timezone
            self.is_read = True
            self.read_at = timezone.now()
            self.save(update_fields=['is_read', 'read_at'])

