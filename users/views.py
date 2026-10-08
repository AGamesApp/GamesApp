from rest_framework import status, generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate, get_user_model
from django.shortcuts import get_object_or_404
from django.core.mail import send_mail
from django.conf import settings
from .serializers import (
    UserSerializer, 
    UserRegistrationSerializer, 
    UserLoginSerializer,
    VerifyOTPSerializer,
    ResendOTPSerializer,
    PasswordResetRequestSerializer,
    VerifyPasswordResetOTPSerializer,
    ResetPasswordSerializer,
    ChangePasswordSerializer,
    UpdatePremiumStatusSerializer
)
from rest_framework.throttling import ScopedRateThrottle

User = get_user_model()


class UserRegistrationView(generics.CreateAPIView):
    """API endpoint for user registration."""
    
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token = Token.objects.get(user=user)
        
        return Response({
            'message': 'Registration successful! Please check your email for the verification code.',
            'user': UserSerializer(user).data,
            'token': token.key
        }, status=status.HTTP_201_CREATED)


class VerifyOTPView(APIView):
    """API endpoint for OTP verification."""
    
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = VerifyOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        email = serializer.validated_data['email']
        otp = serializer.validated_data['otp']
        
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({
                'error': 'User with this email does not exist.'
            }, status=status.HTTP_404_NOT_FOUND)
        
        if user.is_email_verified:
            return Response({
                'message': 'Email is already verified. You can login now.'
            }, status=status.HTTP_200_OK)
        
        if user.verify_otp(otp):
            return Response({
                'message': 'Email verified successfully! You can now login.',
                'user': UserSerializer(user).data
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'error': 'Invalid or expired OTP. Please request a new one.'
            }, status=status.HTTP_400_BAD_REQUEST)


class ResendOTPView(APIView):
    """API endpoint for resending OTP."""
    
    permission_classes = [permissions.AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'otp'
    
    def post(self, request):
        serializer = ResendOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        email = serializer.validated_data['email']
        
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({
                'error': 'User with this email does not exist.'
            }, status=status.HTTP_404_NOT_FOUND)
        
        if user.is_email_verified:
            return Response({
                'message': 'Email is already verified. You can login now.'
            }, status=status.HTTP_200_OK)
        
        # Generate new OTP
        otp = user.generate_otp()
        
        # Send OTP email with HTML template
        html_message = f'''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Email Verification - AGames</title>
</head>
<body style="margin: 0; padding: 0; font-family: 'Segoe UI', Arial, sans-serif; background-color: #f4f4f7;">
    <table role="presentation" style="width: 100%; border-collapse: collapse; background-color: #f4f4f7;">
        <tr>
            <td style="padding: 40px 20px;">
                <table role="presentation" style="max-width: 600px; margin: 0 auto; background-color: #ffffff; border-radius: 16px; box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1); overflow: hidden;">
                    
                    <!-- Header with gradient -->
                    <tr>
                        <td style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 40px 30px; text-align: center;">
                            <h1 style="margin: 0; color: #ffffff; font-size: 28px; font-weight: 700; letter-spacing: -0.5px;">
                                🎮 AGames
                            </h1>
                            <p style="margin: 8px 0 0 0; color: #e0e7ff; font-size: 14px;">
                                Your Gaming Platform
                            </p>
                        </td>
                    </tr>
                    
                    <!-- Main Content -->
                    <tr>
                        <td style="padding: 40px 30px;">
                            <h2 style="margin: 0 0 20px 0; color: #1f2937; font-size: 24px; font-weight: 600;">
                                New Verification Code 🔄
                            </h2>
                            
                            <p style="margin: 0 0 24px 0; color: #4b5563; font-size: 16px; line-height: 1.6;">
                                Hi <strong style="color: #667eea;">{user.username}</strong>,
                            </p>
                            
                            <p style="margin: 0 0 24px 0; color: #4b5563; font-size: 16px; line-height: 1.6;">
                                You requested a new verification code. Here's your new code:
                            </p>
                            
                            <!-- OTP Box -->
                            <table role="presentation" style="width: 100%; border-collapse: collapse; margin: 30px 0;">
                                <tr>
                                    <td style="text-align: center;">
                                        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 12px; padding: 24px; display: inline-block;">
                                            <p style="margin: 0 0 8px 0; color: #e0e7ff; font-size: 12px; text-transform: uppercase; letter-spacing: 1px; font-weight: 600;">
                                                Your Verification Code
                                            </p>
                                            <p style="margin: 0; color: #ffffff; font-size: 36px; font-weight: 700; letter-spacing: 8px; font-family: 'Courier New', monospace;">
                                                {otp}
                                            </p>
                                        </div>
                                    </td>
                                </tr>
                            </table>
                            
                            <!-- Important Notice -->
                            <table role="presentation" style="width: 100%; border-collapse: collapse; margin: 24px 0;">
                                <tr>
                                    <td style="background-color: #fef3c7; border-left: 4px solid #f59e0b; padding: 16px; border-radius: 8px;">
                                        <p style="margin: 0; color: #92400e; font-size: 14px; line-height: 1.5;">
                                            ⏰ <strong>Important:</strong> This code will expire in <strong>10 minutes</strong>. Please use it soon!
                                        </p>
                                    </td>
                                </tr>
                            </table>
                            
                            <p style="margin: 24px 0 0 0; color: #6b7280; font-size: 14px; line-height: 1.6;">
                                If you didn't request this code, please ignore this email or contact support if you're concerned about your account security.
                            </p>
                        </td>
                    </tr>
                    
                    <!-- Footer -->
                    <tr>
                        <td style="background-color: #f9fafb; padding: 30px; text-align: center; border-top: 1px solid #e5e7eb;">
                            <p style="margin: 0 0 12px 0; color: #667eea; font-size: 16px; font-weight: 600;">
                                Happy Gaming! 🎮
                            </p>
                            <p style="margin: 0 0 8px 0; color: #9ca3af; font-size: 13px;">
                                © 2025 AGames. All rights reserved.
                            </p>
                            <p style="margin: 0; color: #9ca3af; font-size: 12px;">
                                This is an automated message, please do not reply.
                            </p>
                        </td>
                    </tr>
                    
                </table>
            </td>
        </tr>
    </table>
</body>
</html>
'''
        
        plain_message = f'''Hi {user.username},

Your new email verification code is: {otp}

This code will expire in 10 minutes.

If you didn't request this code, please ignore this email.

Thank you for joining AGames!'''
        
        try:
            from django.core.mail import EmailMultiAlternatives
            
            email = EmailMultiAlternatives(
                subject='Your Verification Code - AGames',
                body=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[user.email]
            )
            email.attach_alternative(html_message, "text/html")
            email.send(fail_silently=False)

            # Email sent successfully — now persist the OTP
            user.commit_otp()
            
            return Response({
                'message': 'New verification code sent to your email.'
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'error': 'Failed to send email. Please try again later.'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserLoginView(APIView):
    """API endpoint for user login."""
    
    permission_classes = [permissions.AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'login'
    
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = authenticate(
            email=serializer.validated_data['email'],
            password=serializer.validated_data['password']
        )
        
        if user:
            if not user.is_email_verified:
                return Response({
                    'error': 'Email verification required',
                    'message': 'Your email address is not verified. Please check your email inbox and verify your account before logging in.',
                    'email': serializer.validated_data['email']
                }, status=status.HTTP_403_FORBIDDEN)
            
            # Rotate token on every login — the previous device's token is
            # immediately invalidated and it will get 401 on the next request.
            Token.objects.filter(user=user).delete()
            token = Token.objects.create(user=user)

            # Also rotate session_id so the session-aware auth layer fires too.
            session_id = user.rotate_session()

            # Auto-check premium expiration on login
            user.check_premium_expiration()

            return Response({
                'user': UserSerializer(user).data,
                'token': token.key,
                'session_id': session_id,
            })
        
        return Response(
            {'error': 'Invalid credentials'},
            status=status.HTTP_401_UNAUTHORIZED
        )


class UserLogoutView(APIView):
    """API endpoint for user logout."""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        if hasattr(request.user, 'auth_token'):
            request.user.auth_token.delete()
            # Clear session_id on logout
            request.user.session_id = None
            request.user.save(update_fields=['session_id'])
            return Response({'message': 'Successfully logged out'})
        return Response({'error': 'No active session found'}, status=status.HTTP_400_BAD_REQUEST)


class UserStatusView(APIView):
    """
    GET /api/users/status
    
    Called every time the app opens or resumes.
    Returns the user's current premium status and expiration.
    Also auto-expires premium if the date has passed.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user

        # Auto-expire premium if needed
        is_premium = user.check_premium_expiration()

        return Response({
            'is_premium': is_premium,
            'expiration_date': user.premium_expiration,
            'email': user.email,
            'username': user.username,
        }, status=status.HTTP_200_OK)


class UserProfileView(generics.RetrieveUpdateAPIView):
    """API endpoint for retrieving and updating user profile."""
    
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return self.request.user


class UpdateProfilePictureView(APIView):
    """Simple endpoint for updating profile picture only."""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        """
        Upload/update profile picture.
        Simply send the image file with key 'profile_picture'
        """
        if 'profile_picture' not in request.FILES:
            return Response({
                'error': 'No profile picture provided',
                'message': 'Please upload an image file with key "profile_picture"'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        profile_picture = request.FILES['profile_picture']
        
        # Validate file type
        allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp']
        if profile_picture.content_type not in allowed_types:
            return Response({
                'error': 'Invalid file type',
                'message': 'Only image files (JPG, PNG, GIF, WEBP) are allowed'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate file size (max 5MB)
        if profile_picture.size > 5 * 1024 * 1024:
            return Response({
                'error': 'File too large',
                'message': 'Profile picture must be less than 5MB'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Update user's profile picture
        user = request.user
        user.profile_picture = profile_picture
        user.save()
        
        return Response({
            'message': 'Profile picture updated successfully',
            'profile_picture': request.build_absolute_uri(user.profile_picture.url) if user.profile_picture else None
        }, status=status.HTTP_200_OK)


class PasswordResetRequestView(APIView):
    """API endpoint for requesting password reset OTP."""
    
    permission_classes = [permissions.AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'otp'
    
    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        email = serializer.validated_data['email']
        
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            # Don't reveal that the user doesn't exist for security
            return Response({
                'message': 'If an account with this email exists, a password reset code has been sent.'
            }, status=status.HTTP_200_OK)
        
        # Generate password reset OTP
        otp = user.generate_password_reset_otp()
        
        # Send OTP email with HTML template
        html_message = f'''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Password Reset - AGames</title>
</head>
<body style="margin: 0; padding: 0; font-family: 'Segoe UI', Arial, sans-serif; background-color: #f4f4f7;">
    <table role="presentation" style="width: 100%; border-collapse: collapse; background-color: #f4f4f7;">
        <tr>
            <td style="padding: 40px 20px;">
                <table role="presentation" style="max-width: 600px; margin: 0 auto; background-color: #ffffff; border-radius: 16px; box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1); overflow: hidden;">
                    
                    <!-- Header with gradient -->
                    <tr>
                        <td style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 40px 30px; text-align: center;">
                            <h1 style="margin: 0; color: #ffffff; font-size: 28px; font-weight: 700; letter-spacing: -0.5px;">
                                🎮 AGames
                            </h1>
                            <p style="margin: 8px 0 0 0; color: #e0e7ff; font-size: 14px;">
                                Your Gaming Platform
                            </p>
                        </td>
                    </tr>
                    
                    <!-- Main Content -->
                    <tr>
                        <td style="padding: 40px 30px;">
                            <h2 style="margin: 0 0 20px 0; color: #1f2937; font-size: 24px; font-weight: 600;">
                                Password Reset Request 🔐
                            </h2>
                            
                            <p style="margin: 0 0 24px 0; color: #4b5563; font-size: 16px; line-height: 1.6;">
                                Hi <strong style="color: #667eea;">{user.username}</strong>,
                            </p>
                            
                            <p style="margin: 0 0 24px 0; color: #4b5563; font-size: 16px; line-height: 1.6;">
                                We received a request to reset your password. Use the code below to reset your password:
                            </p>
                            
                            <!-- OTP Box -->
                            <table role="presentation" style="width: 100%; border-collapse: collapse; margin: 30px 0;">
                                <tr>
                                    <td style="text-align: center;">
                                        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 12px; padding: 24px; display: inline-block;">
                                            <p style="margin: 0 0 8px 0; color: #e0e7ff; font-size: 12px; text-transform: uppercase; letter-spacing: 1px; font-weight: 600;">
                                                Password Reset Code
                                            </p>
                                            <p style="margin: 0; color: #ffffff; font-size: 36px; font-weight: 700; letter-spacing: 8px; font-family: 'Courier New', monospace;">
                                                {otp}
                                            </p>
                                        </div>
                                    </td>
                                </tr>
                            </table>
                            
                            <!-- Important Notice -->
                            <table role="presentation" style="width: 100%; border-collapse: collapse; margin: 24px 0;">
                                <tr>
                                    <td style="background-color: #fef3c7; border-left: 4px solid #f59e0b; padding: 16px; border-radius: 8px;">
                                        <p style="margin: 0; color: #92400e; font-size: 14px; line-height: 1.5;">
                                            ⏰ <strong>Important:</strong> This code will expire in <strong>10 minutes</strong>. Please use it soon!
                                        </p>
                                    </td>
                                </tr>
                            </table>
                            
                            <!-- Security Warning -->
                            <table role="presentation" style="width: 100%; border-collapse: collapse; margin: 24px 0;">
                                <tr>
                                    <td style="background-color: #fee2e2; border-left: 4px solid #ef4444; padding: 16px; border-radius: 8px;">
                                        <p style="margin: 0; color: #991b1b; font-size: 14px; line-height: 1.5;">
                                            🔒 <strong>Security Alert:</strong> If you didn't request a password reset, please ignore this email and ensure your account is secure. Consider changing your password if you suspect unauthorized access.
                                        </p>
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>
                    
                    <!-- Footer -->
                    <tr>
                        <td style="background-color: #f9fafb; padding: 30px; text-align: center; border-top: 1px solid #e5e7eb;">
                            <p style="margin: 0 0 12px 0; color: #667eea; font-size: 16px; font-weight: 600;">
                                Stay Safe! 🛡️
                            </p>
                            <p style="margin: 0 0 8px 0; color: #9ca3af; font-size: 13px;">
                                © 2025 AGames. All rights reserved.
                            </p>
                            <p style="margin: 0; color: #9ca3af; font-size: 12px;">
                                This is an automated message, please do not reply.
                            </p>
                        </td>
                    </tr>
                    
                </table>
            </td>
        </tr>
    </table>
</body>
</html>
'''
        
        plain_message = f'''Hi {user.username},

Your password reset code is: {otp}

This code will expire in 10 minutes.

If you didn't request a password reset, please ignore this email.

AGames Security Team'''
        
        try:
            from django.core.mail import EmailMultiAlternatives
            
            email_msg = EmailMultiAlternatives(
                subject='Password Reset Code - AGames',
                body=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[user.email]
            )
            email_msg.attach_alternative(html_message, "text/html")
            email_msg.send(fail_silently=False)

            # Email sent successfully — now persist the OTP
            user.commit_password_reset_otp()
            
            return Response({
                'message': 'If an account with this email exists, a password reset code has been sent.'
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'error': 'Failed to send email. Please try again later.'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class VerifyPasswordResetOTPView(APIView):
    """API endpoint for verifying password reset OTP (optional step)."""
    
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = VerifyPasswordResetOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        email = serializer.validated_data['email']
        otp = serializer.validated_data['otp']
        
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({
                'error': 'Invalid credentials.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if user.verify_password_reset_otp(otp):
            return Response({
                'message': 'OTP verified successfully. You can now reset your password.'
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'error': 'Invalid or expired OTP. Please request a new one.'
            }, status=status.HTTP_400_BAD_REQUEST)


class ResetPasswordView(APIView):
    """API endpoint for resetting password with OTP (for forgotten passwords)."""
    
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        email = serializer.validated_data['email']
        otp = serializer.validated_data['otp']
        new_password = serializer.validated_data['new_password']
        
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({
                'error': 'Invalid credentials.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Verify OTP
        if not user.verify_password_reset_otp(otp):
            return Response({
                'error': 'Invalid or expired OTP. Please request a new one.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Reset password
        user.set_password(new_password)
        user.clear_password_reset_otp()
        
        return Response({
            'message': 'Password reset successfully. You can now login with your new password.'
        }, status=status.HTTP_200_OK)


class ChangePasswordView(APIView):
    """API endpoint for changing password when logged in (requires old password)."""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        old_password = serializer.validated_data['old_password']
        new_password = serializer.validated_data['new_password']
        
        user = request.user
        
        # Verify old password
        if not user.check_password(old_password):
            return Response({
                'error': 'Old password is incorrect.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Set new password
        user.set_password(new_password)
        user.save()
        
        # Update token (optional - invalidate old sessions)
        if hasattr(user, 'auth_token'):
            user.auth_token.delete()
        
        # Create new token
        token = Token.objects.create(user=user)
        
        return Response({
            'message': 'Password changed successfully. Please use your new password for future logins.',
            'token': token.key
        }, status=status.HTTP_200_OK)


class UpdatePremiumStatusView(APIView):
    """API endpoint for updating user premium status (Admin only)."""
    
    permission_classes = [permissions.IsAdminUser]
    
    def post(self, request):
        serializer = UpdatePremiumStatusSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user_id = serializer.validated_data.get('user_id')
        email = serializer.validated_data.get('email')
        is_premium = serializer.validated_data['is_premium']
        
        # Find user by ID or email
        try:
            if user_id:
                user = User.objects.get(id=user_id)
            else:
                user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({
                'error': 'User not found.'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Update premium status
        user.is_premium = is_premium
        user.save()
        
        return Response({
            'message': f'Premium status updated successfully.',
            'user': UserSerializer(user).data
        }, status=status.HTTP_200_OK)
