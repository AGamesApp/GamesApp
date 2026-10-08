from rest_framework import serializers
from .models import DeviceToken, NotificationLog, Notification


class DeviceTokenSerializer(serializers.ModelSerializer):
    """Serializer for device token registration."""
    
    class Meta:
        model = DeviceToken
        fields = [
            'id', 'token', 'platform', 'device_id', 
            'is_active', 'created_at', 'updated_at', 'last_used_at'
        ]
        read_only_fields = ['id', 'is_active', 'created_at', 'updated_at', 'last_used_at']
    
    def create(self, validated_data):
        """Create or update device token."""
        token = validated_data.get('token')
        user = self.context['request'].user if self.context['request'].user.is_authenticated else None
        
        # Check if token already exists
        device_token, created = DeviceToken.objects.update_or_create(
            token=token,
            defaults={
                'user': user,
                'platform': validated_data.get('platform', 'android'),
                'device_id': validated_data.get('device_id', ''),
                'is_active': True,
                'failure_count': 0
            }
        )
        
        return device_token


class NotificationSerializer(serializers.ModelSerializer):
    """Serializer for user notifications."""
    
    notification_type_display = serializers.CharField(
        source='get_notification_type_display',
        read_only=True
    )
    
    class Meta:
        model = Notification
        fields = [
            'id', 'notification_type', 'notification_type_display',
            'title', 'body', 'image_url', 'data',
            'is_read', 'created_at', 'read_at'
        ]
        read_only_fields = ['id', 'created_at', 'read_at']


class NotificationLogSerializer(serializers.ModelSerializer):
    """Serializer for notification logs."""
    
    notification_type_display = serializers.CharField(
        source='get_notification_type_display', 
        read_only=True
    )
    success_rate = serializers.FloatField(read_only=True)
    
    class Meta:
        model = NotificationLog
        fields = [
            'id', 'notification_type', 'notification_type_display',
            'title', 'body', 'data', 'target_user', 'sent_to_all',
            'total_devices', 'successful_sends', 'failed_sends',
            'success_rate', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class SendNotificationSerializer(serializers.Serializer):
    """Serializer for sending custom notifications."""
    
    notification_type = serializers.ChoiceField(
        choices=[('normal', 'Normal'), ('fix', 'Fix'), ('update', 'Update'), ('error', 'Error')],
        default='normal'
    )
    title = serializers.CharField(max_length=200)
    body = serializers.CharField()
    notification_type = serializers.ChoiceField(
        choices=NotificationLog.TYPE_CHOICES,
        default='custom'
    )
    data = serializers.JSONField(required=False, default=dict)
    target_user_id = serializers.IntegerField(required=False, allow_null=True)
