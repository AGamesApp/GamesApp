from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from .models import SubscriptionPlan, Subscription
from django.utils import timezone
from datetime import timedelta

User = get_user_model()


class SubscriptionTests(TestCase):
    """Tests for Subscription models and API."""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        
        self.plan = SubscriptionPlan.objects.create(
            name='Premium Monthly',
            description='Monthly premium subscription',
            price=9.99,
            duration='MONTHLY',
            features=['Unlimited downloads', 'Premium games access']
        )
    
    def test_list_subscription_plans(self):
        """Test listing subscription plans."""
        response = self.client.get('/api/plans/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Response is paginated or a list
        if isinstance(response.data, list):
            self.assertEqual(len(response.data), 1)
        else:
            self.assertIn('results', response.data)
    
    def test_create_subscription(self):
        """Test creating a subscription."""
        response = self.client.post('/api/subscriptions/subscribe/', {
            'plan_id': self.plan.id,
            'payment_method': 'stripe'
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_premium)
    
    def test_cancel_subscription(self):
        """Test cancelling a subscription."""
        subscription = Subscription.objects.create(
            user=self.user,
            plan=self.plan,
            status='ACTIVE',
            end_date=timezone.now() + timedelta(days=30)
        )
        
        response = self.client.post(f'/api/subscriptions/{subscription.id}/cancel/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        subscription.refresh_from_db()
        self.assertEqual(subscription.status, 'CANCELLED')
