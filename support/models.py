from django.db import models
from django.conf import settings


class SupportMessage(models.Model):
    """Model for storing support messages from users"""
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('reviewed', 'Reviewed'),
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='support_messages',
        null=True,
        blank=True,
        help_text='User who sent the message (optional for anonymous submissions)'
    )
    name = models.CharField(
        max_length=200,
        help_text='Name of the person sending the message'
    )
    email = models.EmailField(
        help_text='Email address for response'
    )
    subject = models.CharField(
        max_length=300,
        help_text='Subject of the support message'
    )
    message = models.TextField(
        help_text='The support message content'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        db_index=True,
        help_text='Review status of the message'
    )
    is_reviewed = models.BooleanField(
        default=False,
        db_index=True,
        help_text='Whether the message has been reviewed by admin'
    )
    reviewed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text='When the message was reviewed'
    )
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_support_messages',
        help_text='Admin who reviewed this message'
    )
    admin_notes = models.TextField(
        blank=True,
        help_text='Internal notes from admin (not visible to user)'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True
    )
    updated_at = models.DateTimeField(
        auto_now=True
    )
    
    class Meta:
        ordering = ['is_reviewed', '-created_at']  # Unreviewed first, then newest
        verbose_name = 'Support Message'
        verbose_name_plural = 'Support Messages'
        indexes = [
            models.Index(fields=['is_reviewed', '-created_at']),
            models.Index(fields=['status', '-created_at']),
        ]
    
    def __str__(self):
        status_icon = '✓' if self.is_reviewed else '●'
        return f"{status_icon} {self.subject} - {self.name}"
    
    def mark_as_reviewed(self, admin_user=None):
        """Mark the message as reviewed"""
        from django.utils import timezone
        self.is_reviewed = True
        self.status = 'reviewed'
        self.reviewed_at = timezone.now()
        if admin_user:
            self.reviewed_by = admin_user
        self.save()
    
    def mark_as_pending(self):
        """Mark the message as pending (unreviewed)"""
        self.is_reviewed = False
        self.status = 'pending'
        self.reviewed_at = None
        self.reviewed_by = None
        self.save()
