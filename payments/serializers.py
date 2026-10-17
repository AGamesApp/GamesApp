from rest_framework import serializers
from .models import Payment, GooglePlayPurchase


class PaymentSerializer(serializers.ModelSerializer):
    """Serializer for Payment model."""
    
    user_email = serializers.CharField(source='user.email', read_only=True)
    
    class Meta:
        model = Payment
        fields = ['id', 'user', 'user_email', 'subscription', 'amount', 'currency',
                  'status', 'payment_method', 'transaction_id', 'created_at']
        read_only_fields = ['id', 'user', 'status', 'transaction_id', 'created_at']


class PaymentIntentSerializer(serializers.Serializer):
    """Serializer for creating payment intent."""
    
    subscription_id = serializers.IntegerField()
    payment_method = serializers.ChoiceField(
        choices=['STRIPE', 'PAYPAL'],
        default='STRIPE'
    )


class GooglePlayVerifySerializer(serializers.Serializer):
    """
    Serializer for POST /api/payments/verify
    The client sends its purchase token right after a successful Google Play purchase.
    """
    purchase_token = serializers.CharField(max_length=512)
    product_id = serializers.ChoiceField(
        choices=[
            ('agamespro_sub_1month', 'AGames Pro 1 Month Pass'),
            ('agamespro_sub_3months', 'AGames Pro 3 Months Pass'),
            ('agamespro_sub_6months', 'AGames Pro 6 Months Pass'),
        ]
    )
    # Optional: package name override (defaults to server config)
    package_name = serializers.CharField(max_length=255, required=False)


class GooglePlayPurchaseSerializer(serializers.ModelSerializer):
    """Read-only serializer for GooglePlayPurchase records."""

    user_email = serializers.CharField(source='user.email', read_only=True)

    class Meta:
        model = GooglePlayPurchase
        fields = [
            'id', 'user', 'user_email', 'purchase_token', 'product_id',
            'order_id', 'expiry_time', 'is_active', 'created_at',
        ]
        read_only_fields = fields

