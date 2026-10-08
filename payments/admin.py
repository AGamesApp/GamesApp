from django.contrib import admin
from .models import Payment, GooglePlayPurchase


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    """Admin interface for Payment model."""
    
    list_display = ['user', 'amount', 'currency', 'status', 'payment_method', 
                    'transaction_id', 'created_at']
    list_filter = ['status', 'payment_method', 'created_at']
    search_fields = ['user__email', 'transaction_id', 'stripe_payment_intent_id']
    ordering = ['-created_at']
    date_hierarchy = 'created_at'
    readonly_fields = ['transaction_id', 'created_at', 'updated_at']


@admin.register(GooglePlayPurchase)
class GooglePlayPurchaseAdmin(admin.ModelAdmin):
    """Admin interface for Google Play Purchase tokens (anti-fraud)."""

    list_display = ['user', 'product_id', 'order_id', 'is_active', 'expiry_time', 'created_at']
    list_filter = ['product_id', 'is_active', 'created_at']
    search_fields = ['user__email', 'order_id', 'purchase_token']
    ordering = ['-created_at']
    date_hierarchy = 'created_at'
    readonly_fields = ['purchase_token', 'raw_response', 'created_at']
