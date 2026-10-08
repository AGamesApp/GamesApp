from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from dj_rest_auth.registration.views import SocialLoginView
import requests
import logging

User = get_user_model()
logger = logging.getLogger('users')


class GoogleLoginView(SocialLoginView):
    """
    Google OAuth2 login view.
    
    Frontend should send the Google access token received from Google Sign-In.
    """
    adapter_class = GoogleOAuth2Adapter
    callback_url = "https://games.agames.cv/api/users/auth/google/callback/"
    client_class = OAuth2Client
    permission_classes = [AllowAny]


class GoogleAuthView(APIView):
    """
    Custom Google authentication view that accepts Google ID token.
    
    This is easier for frontend - just send the ID token from Google Sign-In.
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        """
        Authenticate user with Google ID token.
        
        Request body:
        {
            "id_token": "google_id_token_here"
        }
        """
        id_token = request.data.get('id_token')
        
        if not id_token:
            return Response({
                'error': 'id_token is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Verify the token with Google
            google_response = requests.get(
                'https://oauth2.googleapis.com/tokeninfo',
                params={'id_token': id_token},
                timeout=10  # Add timeout to prevent hanging
            )
            
            if google_response.status_code != 200:
                error_details = google_response.text if google_response.text else 'Unknown error'
                return Response({
                    'error': 'Invalid Google token',
                    'details': f'Google API returned {google_response.status_code}: {error_details}'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            user_data = google_response.json()
            
            # Extract user information
            email = user_data.get('email')
            name = user_data.get('name', '')
            given_name = user_data.get('given_name', '')
            picture = user_data.get('picture', '')
            
            if not email:
                return Response({
                    'error': 'Email not provided by Google'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Check if email is verified
            if not user_data.get('email_verified'):
                return Response({
                    'error': 'Google email is not verified'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Create username from email
            username = email.split('@')[0]
            
            # Get or create user with simplified logic (no unique username constraint)
            try:
                user, created = User.objects.get_or_create(
                    email=email,
                    defaults={
                        'username': username,
                        'is_email_verified': True,  # Google already verified it
                    }
                )
            except Exception as db_error:
                logger.error(f"Failed to create user for {email}: {str(db_error)}")
                return Response({
                    'error': 'Failed to create user account',
                    'details': 'Database error during user creation'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            # Update user with Google data if needed
            updated = False
            if not created and not user.is_email_verified:
                user.is_email_verified = True
                updated = True
            
            # Save profile picture URL from Google if not already set
            if picture and not user.profile_picture:
                # Download and save the profile picture
                try:
                    import urllib.request
                    from django.core.files.base import ContentFile
                    from django.core.files.storage import default_storage
                    import os
                    
                    # Download the image from Google
                    picture_response = urllib.request.urlopen(picture)
                    picture_data = picture_response.read()
                    
                    # Generate filename
                    filename = f"profile_pictures/google_{user.id}_{email.split('@')[0]}.jpg"
                    
                    # Save the image
                    path = default_storage.save(filename, ContentFile(picture_data))
                    user.profile_picture = path
                    updated = True
                except Exception as img_error:
                    # If image download fails, just continue without it
                    print(f"Failed to download profile picture: {img_error}")
            
            if updated:
                user.save()
            
            # Re-use existing token (or create if first login).
            # Rotate token on every login — previous device is immediately invalidated.
            Token.objects.filter(user=user).delete()
            token = Token.objects.create(user=user)

            # Also rotate session_id.
            session_id = user.rotate_session()

            # Auto-check premium expiration on login
            user.check_premium_expiration()
            
            # Import serializer
            from users.serializers import UserSerializer
            
            return Response({
                'message': 'Login successful' if not created else 'Account created successfully',
                'user': UserSerializer(user).data,
                'token': token.key,
                'session_id': session_id,
                'is_new_user': created
            }, status=status.HTTP_200_OK)
            
        except requests.RequestException as e:
            # Log the detailed error for debugging
            logger.error(f"Google OAuth request failed: {str(e)}")
            
            return Response({
                'error': 'Failed to verify Google token',
                'details': 'Network error connecting to Google'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            # Log the detailed error for debugging
            logger.error(f"Google OAuth authentication failed: {str(e)}")
            
            return Response({
                'error': 'Authentication failed',
                'details': 'Internal server error during authentication'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class GoogleAuthCallbackView(APIView):
    """
    Callback view for Google OAuth (optional, for web-based flow).
    """
    permission_classes = [AllowAny]
    
    def get(self, request):
        return Response({
            'message': 'Google OAuth callback - use POST to /api/auth/google/ with id_token instead'
        })
