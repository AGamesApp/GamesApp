from django.contrib import admin
from .models import SubscriptionPlan, Subscription


@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    """Admin interface for SubscriptionPlan model."""
    
    list_display = ['name', 'price', 'duration', 'is_active', 'created_at']
    list_filter = ['duration', 'is_active', 'created_at']
    search_fields = ['name', 'description']
    ordering = ['price']


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    """Admin interface for Subscription model."""
    
    list_display = ['user', 'plan', 'status', 'start_date', 'end_date', 'auto_renew']
    list_filter = ['status', 'auto_renew', 'created_at']
    search_fields = ['user__email', 'plan__name']
    ordering = ['-created_at']
    date_hierarchy = 'created_at'
