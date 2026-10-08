from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import DeviceToken, NotificationLog, Notification
from .serializers import (
    DeviceTokenSerializer,
    NotificationLogSerializer,
    SendNotificationSerializer,
    NotificationSerializer
)
from .fcm_service import send_notification_to_all_users_topic


class DeviceTokenViewSet(viewsets.ModelViewSet):
    """
    ViewSet for device token management.
    
    Allows:
    - Registering new device tokens (public)
    - Listing user's device tokens
    - Unregistering tokens
    """
    queryset = DeviceToken.objects.all()
    serializer_class = DeviceTokenSerializer
    permission_classes = [permissions.AllowAny]  # Allow anonymous registration
    
    def get_queryset(self):
        """Return user's tokens or all if admin."""
        if self.request.user.is_staff:
            return DeviceToken.objects.all()
        elif self.request.user.is_authenticated:
            return DeviceToken.objects.filter(user=self.request.user)
        else:
            # For anonymous users, return empty queryset for list
            # but allow creation via POST
            return DeviceToken.objects.none()
    
    def create(self, request, *args, **kwargs):
        """Register a new device token."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        device_token = serializer.save()
        
        return Response({
            'message': 'Device registered successfully',
            'device_token': DeviceTokenSerializer(device_token).data
        }, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny])
    def unregister(self, request):
        """Unregister a device token."""
        token = request.data.get('token')
        if not token:
            return Response(
                {'error': 'Token is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        deleted_count, _ = DeviceToken.objects.filter(token=token).delete()
        
        if deleted_count > 0:
            return Response({'message': 'Device unregistered successfully'})
        else:
            return Response(
                {'message': 'Token not found'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAdminUser])
    def stats(self, request):
        """Get device token statistics (admin only)."""
        total = DeviceToken.objects.count()
        active = DeviceToken.objects.filter(is_active=True).count()
        inactive = total - active
        
        by_platform = {}
        for platform, _ in DeviceToken.PLATFORM_CHOICES:
            by_platform[platform] = DeviceToken.objects.filter(
                platform=platform,
                is_active=True
            ).count()
        
        return Response({
            'total_devices': total,
            'active_devices': active,
            'inactive_devices': inactive,
            'by_platform': by_platform
        })


class NotificationLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for notification logs.
    
    Read-only access to notification history.
    Admin can also send custom notifications.
    """
    queryset = NotificationLog.objects.all()
    serializer_class = NotificationLogSerializer
    permission_classes = [permissions.IsAdminUser]
    
    @action(detail=False, methods=['post'])
    def send_notification(self, request):
        """Send a custom notification to all devices (admin only)."""
        serializer = SendNotificationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        data = serializer.validated_data
        
        # Determine target user
        target_user = None
        if data.get('target_user_id'):
            from django.contrib.auth import get_user_model
            User = get_user_model()
            try:
                target_user = User.objects.get(id=data['target_user_id'])
            except User.DoesNotExist:
                return Response(
                    {'error': 'User not found'},
                    status=status.HTTP_404_NOT_FOUND
                )
        
        # Send notification
        if target_user:
            # For specific user, we still need to use the old method
            # or implement a user-specific topic
            from .fcm_service import send_notification_to_all_devices
            log = send_notification_to_all_devices(
                title=data['title'],
                body=data['body'],
                notification_type=data['notification_type'],
                data=data.get('data', {}),
                user=target_user
            )
        else:
            # For all users, use topic
            log = send_notification_to_all_users_topic(
                title=data['title'],
                body=data['body'],
                notification_type=data['notification_type'],
                data=data.get('data', {})
            )
        
        return Response({
            'message': 'Notification sent successfully',
            'log': NotificationLogSerializer(log).data
        }, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['get'])
    def analytics(self, request):
        """Get notification analytics (admin only)."""
        from django.db.models import Sum, Avg
        
        total_notifications = NotificationLog.objects.count()
        total_sent = NotificationLog.objects.aggregate(
            Sum('total_devices')
        )['total_devices__sum'] or 0
        total_successful = NotificationLog.objects.aggregate(
            Sum('successful_sends')
        )['successful_sends__sum'] or 0
        
        avg_success_rate = (total_successful / total_sent * 100) if total_sent > 0 else 0
        
        by_type = {}
        for type_code, type_label in NotificationLog.TYPE_CHOICES:
            count = NotificationLog.objects.filter(
                notification_type=type_code
            ).count()
            if count > 0:
                by_type[type_label] = count
        
        return Response({
            'total_notifications': total_notifications,
            'total_devices_reached': total_sent,
            'total_successful_sends': total_successful,
            'average_success_rate': round(avg_success_rate, 2),
            'by_type': by_type
        })


class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for user notifications stored in database.
    
    Allows authenticated users to:
    - List their notifications
    - Mark notifications as read
    - Get unread count
    """
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Return notifications for the current user, sorted by most recent first."""
        return Notification.objects.filter(user=self.request.user).order_by('-created_at')
    
    @action(detail=False, methods=['get'])
    def unread(self, request):
        """Get unread notifications count and list, sorted by most recent first."""
        unread_notifications = self.get_queryset().filter(is_read=False)
        
        return Response({
            'count': unread_notifications.count(),
            'notifications': NotificationSerializer(unread_notifications, many=True).data
        })
    
    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        """Mark a specific notification as read."""
        notification = self.get_object()
        notification.mark_as_read()
        
        return Response({
            'message': 'Notification marked as read',
            'notification': NotificationSerializer(notification).data
        })
    
    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        """Delete all notifications for this user."""
        notifications = self.get_queryset()
        deleted_count = notifications.count()
        notifications.delete()
        
        return Response({
            'message': f'{deleted_count} notifications deleted',
            'count': deleted_count
        })

