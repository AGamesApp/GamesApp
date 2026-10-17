from rest_framework import serializers
from .models import SubscriptionPlan, Subscription


class SubscriptionPlanSerializer(serializers.ModelSerializer):
    """Serializer for SubscriptionPlan model."""
    
    class Meta:
        model = SubscriptionPlan
        fields = ['id', 'product_id', 'name', 'description', 'price', 'duration', 'features', 
                  'is_active', 'created_at']
        read_only_fields = ['id', 'created_at']


class SubscriptionSerializer(serializers.ModelSerializer):
    """Serializer for Subscription model."""
    
    plan_name = serializers.CharField(source='plan.name', read_only=True)
    plan_price = serializers.DecimalField(source='plan.price', max_digits=10, 
                                          decimal_places=2, read_only=True)
    is_active = serializers.ReadOnlyField()
    
    class Meta:
        model = Subscription
        fields = ['id', 'user', 'plan', 'plan_name', 'plan_price', 'status', 
                  'start_date', 'end_date', 'auto_renew', 'is_active', 'created_at']
        read_only_fields = ['id', 'user', 'status', 'start_date', 'created_at']


class SubscriptionCreateSerializer(serializers.Serializer):
    """Serializer for creating subscriptions."""
    
    plan_id = serializers.IntegerField()
    payment_method = serializers.CharField(default='stripe')
