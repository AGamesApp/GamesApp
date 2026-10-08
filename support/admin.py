from django.contrib import admin
from django.utils.html import format_html
from .models import SupportMessage


@admin.register(SupportMessage)
class SupportMessageAdmin(admin.ModelAdmin):
    """Django admin for support messages"""
    
    list_display = [
        'status_badge',
        'subject',
        'name',
        'email',
        'user',
        'created_at',
        'review_info',
    ]
    list_filter = [
        'is_reviewed',
        'status',
        'created_at',
        'reviewed_at',
    ]
    search_fields = [
        'subject',
        'name',
        'email',
        'message',
        'user__username',
        'user__email',
    ]
    readonly_fields = [
        'user',
        'created_at',
        'updated_at',
        'reviewed_at',
        'reviewed_by',
    ]
    fieldsets = (
        ('Message Information', {
            'fields': ('user', 'name', 'email', 'subject', 'message')
        }),
        ('Review Status', {
            'fields': ('status', 'is_reviewed', 'reviewed_at', 'reviewed_by', 'admin_notes')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    ordering = ['is_reviewed', '-created_at']
    
    def status_badge(self, obj):
        """Display a colored badge for the status"""
        if obj.is_reviewed:
            color = '#28a745'
            icon = '✓'
            text = 'Reviewed'
        else:
            color = '#ffc107'
            icon = '●'
            text = 'Pending'
        
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; '
            'border-radius: 3px; font-weight: bold;">{} {}</span>',
            color, icon, text
        )
    status_badge.short_description = 'Status'
    
    def review_info(self, obj):
        """Display review information"""
        if obj.is_reviewed and obj.reviewed_by:
            return format_html(
                '<small>By {} on {}</small>',
                obj.reviewed_by.username,
                obj.reviewed_at.strftime('%Y-%m-%d %H:%M') if obj.reviewed_at else 'N/A'
            )
        return format_html('<small style="color: #999;">Not reviewed</small>')
    review_info.short_description = 'Review Info'
    
    def save_model(self, request, obj, form, change):
        """Auto-set reviewed_by when marking as reviewed"""
        if obj.is_reviewed and not obj.reviewed_by:
            obj.reviewed_by = request.user
            if not obj.reviewed_at:
                from django.utils import timezone
                obj.reviewed_at = timezone.now()
        super().save_model(request, obj, form, change)
