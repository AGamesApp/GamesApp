from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status

User = get_user_model()


class UserTests(TestCase):
    """Tests for User model and authentication."""
    
    def setUp(self):
        self.client = APIClient()
        self.user_data = {
            'email': 'test@example.com',
            'password': 'testpass123',
            'password_confirm': 'testpass123',
            'username': 'testuser'
        }
    
    def test_user_registration(self):
        """Test user registration."""
        response = self.client.post('/api/users/register/', self.user_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('token', response.data)
        self.assertIn('user', response.data)
    
    def test_user_login(self):
        """Test user login."""
        # Create user with verified email
        user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        user.is_email_verified = True
        user.save()
        
        # Try to login
        response = self.client.post('/api/users/login/', {
            'email': 'test@example.com',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)
    
    def test_user_profile(self):
        """Test retrieving user profile."""
        user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=user)
        
        response = self.client.get('/api/users/profile/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], 'test@example.com')
