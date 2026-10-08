from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token
from django.core.mail import send_mail
from django.conf import settings

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model."""
    
    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'profile_picture', 'is_premium',
                  'premium_expiration', 'is_email_verified', 'created_at']
        read_only_fields = ['id', 'is_premium', 'premium_expiration', 'is_email_verified', 'created_at']


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration."""
    
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True, min_length=8)
    
    class Meta:
        model = User
        fields = ['email', 'password', 'password_confirm', 'username']
        extra_kwargs = {
            'username': {'required': True}
        }

    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError("Passwords do not match")
        return data
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        user.is_active = True  # User is active but not verified
        user.save()
        
        # Generate OTP
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
                                Welcome to AGames! 👋
                            </h2>
                            
                            <p style="margin: 0 0 24px 0; color: #4b5563; font-size: 16px; line-height: 1.6;">
                                Hi <strong style="color: #667eea;">{user.username}</strong>,
                            </p>
                            
                            <p style="margin: 0 0 24px 0; color: #4b5563; font-size: 16px; line-height: 1.6;">
                                Thank you for joining AGames! To complete your registration and start gaming, please verify your email address using the code below:
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
                                If you didn't create an AGames account, you can safely ignore this email.
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

Your email verification code is: {otp}

This code will expire in 10 minutes.

If you didn't request this code, please ignore this email.

Thank you for joining AGames!'''
        
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

        Token.objects.create(user=user)
        return user


class VerifyOTPSerializer(serializers.Serializer):
    """Serializer for OTP verification."""
    
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6, min_length=6)
    
    def validate_otp(self, value):
        """Validate that OTP is 6 digits."""
        if not value.isdigit():
            raise serializers.ValidationError("OTP must be 6 digits")
        return value


class ResendOTPSerializer(serializers.Serializer):
    """Serializer for resending OTP."""
    
    email = serializers.EmailField()


class UserLoginSerializer(serializers.Serializer):
    """Serializer for user login."""
    
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)


class PasswordResetRequestSerializer(serializers.Serializer):
    """Serializer for requesting password reset OTP."""
    
    email = serializers.EmailField()


class VerifyPasswordResetOTPSerializer(serializers.Serializer):
    """Serializer for verifying password reset OTP."""
    
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6, min_length=6)
    
    def validate_otp(self, value):
        """Validate that OTP is 6 digits."""
        if not value.isdigit():
            raise serializers.ValidationError("OTP must be 6 digits")
        return value


class ResetPasswordSerializer(serializers.Serializer):
    """Serializer for resetting password with OTP."""
    
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6, min_length=6)
    new_password = serializers.CharField(write_only=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True, min_length=8)
    
    def validate_otp(self, value):
        """Validate that OTP is 6 digits."""
        if not value.isdigit():
            raise serializers.ValidationError("OTP must be 6 digits")
        return value
    
    def validate(self, data):
        """Validate that passwords match."""
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError("Passwords do not match")
        return data


class ChangePasswordSerializer(serializers.Serializer):
    """Serializer for changing password when logged in (requires old password)."""
    
    old_password = serializers.CharField(write_only=True, min_length=8)
    new_password = serializers.CharField(write_only=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True, min_length=8)
    
    def validate(self, data):
        """Validate that new passwords match."""
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError("New passwords do not match")
        
        if data['old_password'] == data['new_password']:
            raise serializers.ValidationError("New password must be different from old password")
        
        return data


class UpdatePremiumStatusSerializer(serializers.Serializer):
    """Serializer for updating user premium status (Admin only)."""
    
    user_id = serializers.IntegerField(required=False)
    email = serializers.EmailField(required=False)
    is_premium = serializers.BooleanField()
    
    def validate(self, data):
        """Validate that either user_id or email is provided."""
        if not data.get('user_id') and not data.get('email'):
            raise serializers.ValidationError("Either user_id or email must be provided")
        return data
