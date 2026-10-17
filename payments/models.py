from django.db import models
from django.contrib.auth import get_user_model
from subscriptions.models import Subscription

User = get_user_model()


class Payment(models.Model):
    """Model for payment transactions."""
    
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
        ('REFUNDED', 'Refunded'),
    ]
    
    PAYMENT_METHOD_CHOICES = [
        ('STRIPE', 'Stripe'),
        ('PAYPAL', 'PayPal'),
        ('CREDIT_CARD', 'Credit Card'),
        ('GOOGLE_PLAY', 'Google Play'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments')
    subscription = models.ForeignKey(Subscription, on_delete=models.SET_NULL, 
                                     null=True, blank=True, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING', db_index=True)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, db_index=True)
    transaction_id = models.CharField(max_length=255, unique=True, db_index=True)
    stripe_payment_intent_id = models.CharField(max_length=255, blank=True, null=True, db_index=True)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),  # User payment history
            models.Index(fields=['user', 'status']),  # User's pending/completed payments
            models.Index(fields=['status', '-created_at']),  # Recent payments by status
            models.Index(fields=['subscription', '-created_at']),  # Subscription payment history
        ]
    
    def __str__(self):
        return f"{self.user.email} - ${self.amount} - {self.status}"


class GooglePlayPurchase(models.Model):
    """
    Stores every verified Google Play purchase token.
    Each purchase_token can only be claimed ONCE (anti-fraud).
    """

    SUBSCRIPTION_PRODUCTS = {
        'agamespro_sub_1month': {'label': 'AGames Pro 1 Month Pass', 'days': 30},
        'agamespro_sub_3months': {'label': 'AGames Pro 3 Months Pass', 'days': 90},
        'agamespro_sub_6months': {'label': 'AGames Pro 6 Months Pass', 'days': 180},
    }

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='google_purchases')
    purchase_token = models.CharField(max_length=512, unique=True, db_index=True)
    product_id = models.CharField(max_length=128, db_index=True)
    order_id = models.CharField(max_length=255, blank=True, default='')
    expiry_time = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    raw_response = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
        ]

    def __str__(self):
        return f"{self.user.email} - {self.product_id} - {'Active' if self.is_active else 'Expired'}"
