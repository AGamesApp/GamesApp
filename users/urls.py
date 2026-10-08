from django.urls import path
from .views import (
    UserRegistrationView,
    UserLoginView,
    UserLogoutView,
    UserProfileView,
    UserStatusView,
    UpdateProfilePictureView,
    VerifyOTPView,
    ResendOTPView,
    PasswordResetRequestView,
    VerifyPasswordResetOTPView,
    ResetPasswordView,
    ChangePasswordView,
    UpdatePremiumStatusView
)
from .google_auth import GoogleAuthView, GoogleLoginView, GoogleAuthCallbackView

app_name = 'users'

urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('logout/', UserLogoutView.as_view(), name='logout'),
    path('profile/', UserProfileView.as_view(), name='profile'),
    path('profile/picture/', UpdateProfilePictureView.as_view(), name='update-profile-picture'),
    path('verify-otp/', VerifyOTPView.as_view(), name='verify-otp'),
    path('resend-otp/', ResendOTPView.as_view(), name='resend-otp'),
    
    # Premium status check (called on every app open)
    path('status/', UserStatusView.as_view(), name='user-status'),
    
    # Password management - for logged in users
    path('change-password/', ChangePasswordView.as_view(), name='change-password'),
    
    # Password reset - for forgotten passwords (uses OTP)
    path('password-reset/request/', PasswordResetRequestView.as_view(), name='password-reset-request'),
    path('password-reset/verify-otp/', VerifyPasswordResetOTPView.as_view(), name='password-reset-verify-otp'),
    path('password-reset/reset/', ResetPasswordView.as_view(), name='password-reset'),
    
    path('admin/update-premium/', UpdatePremiumStatusView.as_view(), name='update-premium'),
    
    # Google OAuth endpoints
    path('auth/google/', GoogleAuthView.as_view(), name='google-auth'),
    path('auth/google/login/', GoogleLoginView.as_view(), name='google-login'),
    path('auth/google/callback/', GoogleAuthCallbackView.as_view(), name='google-callback'),
]
