from django.db import models
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

User = get_user_model()


class SubscriptionPlan(models.Model):
    """Model for subscription plans."""
    
    DURATION_CHOICES = [
        ('MONTHLY', 'Monthly'),
        ('QUARTERLY', 'Quarterly'),
        ('YEARLY', 'Yearly'),
    ]
    
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    duration = models.CharField(max_length=20, choices=DURATION_CHOICES, default='MONTHLY')
    features = models.JSONField(default=list)  # List of features
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['price']
    
    def __str__(self):
        return f"{self.name} - ${self.price}/{self.duration}"


class Subscription(models.Model):
    """Model for user subscriptions."""
    
    STATUS_CHOICES = [
        ('ACTIVE', 'Active'),
        ('EXPIRED', 'Expired'),
        ('CANCELLED', 'Cancelled'),
        ('PENDING', 'Pending'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subscriptions')
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.CASCADE, related_name='subscriptions')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING', db_index=True)
    start_date = models.DateTimeField(auto_now_add=True, db_index=True)
    end_date = models.DateTimeField(db_index=True)
    auto_renew = models.BooleanField(default=True)
    stripe_subscription_id = models.CharField(max_length=255, blank=True, null=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'status']),  # Find user's active subscriptions
            models.Index(fields=['user', '-created_at']),  # User subscription history
            models.Index(fields=['status', 'end_date']),  # Find expiring subscriptions
        ]
    
    def __str__(self):
        return f"{self.user.email} - {self.plan.name} - {self.status}"
    
    @property
    def is_active(self):
        from django.utils import timezone
        return self.status == 'ACTIVE' and self.end_date > timezone.now()


# Signal handlers to auto-update user premium status
@receiver(post_save, sender=Subscription)
def update_user_premium_status(sender, instance, created, **kwargs):
    """Automatically update user's premium status when subscription changes."""
    user = instance.user
    
    # Check if user has any active subscriptions
    has_active_subscription = Subscription.objects.filter(
        user=user,
        status='ACTIVE'
    ).exists()
    
    # Update user's premium status
    if user.is_premium != has_active_subscription:
        user.is_premium = has_active_subscription
        user.save(update_fields=['is_premium'])
        
        if has_active_subscription:
            print(f"✅ User {user.email} is now PREMIUM (Subscription: {instance.plan.name})")
        else:
            print(f"❌ User {user.email} premium status removed (No active subscriptions)")


@receiver(post_delete, sender=Subscription)
def remove_premium_on_subscription_delete(sender, instance, **kwargs):
    """Remove premium status when subscription is deleted if no other active subscriptions."""
    user = instance.user
    
    # Check if user has any remaining active subscriptions
    has_active_subscription = Subscription.objects.filter(
        user=user,
        status='ACTIVE'
    ).exists()
    
    # Update user's premium status
    if not has_active_subscription and user.is_premium:
        user.is_premium = False
        user.save(update_fields=['is_premium'])
        print(f"❌ User {user.email} premium status removed (Subscription deleted)")
