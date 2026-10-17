from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from datetime import timedelta
from .models import SubscriptionPlan, Subscription
from .serializers import (
    SubscriptionPlanSerializer,
    SubscriptionSerializer,
    SubscriptionCreateSerializer
)


class IsAdminOrReadOnly(permissions.BasePermission):
    """Custom permission to only allow admins to edit."""
    
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_staff


class SubscriptionPlanViewSet(viewsets.ModelViewSet):
    """ViewSet for managing subscription plans."""
    
    queryset = SubscriptionPlan.objects.filter(is_active=True)
    serializer_class = SubscriptionPlanSerializer
    permission_classes = [IsAdminOrReadOnly]


class SubscriptionViewSet(viewsets.ModelViewSet):
    """ViewSet for managing subscriptions."""
    
    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer
    
    def get_queryset(self):
        # Users can only see their own subscriptions
        if self.request.user.is_staff:
            return Subscription.objects.all()
        return Subscription.objects.filter(user=self.request.user)
    
    @action(detail=False, methods=['post'])
    def subscribe(self, request):
        """Create a new subscription."""
        serializer = SubscriptionCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        plan_id = serializer.validated_data['plan_id']
        
        try:
            plan = SubscriptionPlan.objects.get(id=plan_id, is_active=True)
        except SubscriptionPlan.DoesNotExist:
            return Response(
                {'error': 'Invalid subscription plan'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Calculate end date based on plan duration
        start_date = timezone.now()
        if plan.duration == 'MONTHLY':
            end_date = start_date + timedelta(days=30)
        elif plan.duration == 'QUARTERLY':
            end_date = start_date + timedelta(days=90)
        elif plan.duration == 'SEMI_ANNUAL':
            end_date = start_date + timedelta(days=180)
        else:  # YEARLY
            end_date = start_date + timedelta(days=365)
        
        # Create subscription
        subscription = Subscription.objects.create(
            user=request.user,
            plan=plan,
            status='ACTIVE',
            end_date=end_date
        )
        
        # Update user premium status
        request.user.is_premium = True
        request.user.save()
        
        return Response(
            SubscriptionSerializer(subscription).data,
            status=status.HTTP_201_CREATED
        )
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancel a subscription."""
        subscription = self.get_object()
        
        if subscription.user != request.user and not request.user.is_staff:
            return Response(
                {'error': 'Permission denied'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        subscription.status = 'CANCELLED'
        subscription.auto_renew = False
        subscription.save()
        
        # Check if user has other active subscriptions
        active_subscriptions = Subscription.objects.filter(
            user=subscription.user,
            status='ACTIVE'
        ).exclude(id=subscription.id)
        
        if not active_subscriptions.exists():
            subscription.user.is_premium = False
            subscription.user.save()
        
        return Response(SubscriptionSerializer(subscription).data)
