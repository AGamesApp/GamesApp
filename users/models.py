from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils.crypto import get_random_string
import random
import uuid
from django.utils import timezone
from datetime import timedelta


class UserManager(BaseUserManager):
    """Custom user manager for email-based authentication."""
    
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        
        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    """Custom User model with email as username."""
    
    username = models.CharField(max_length=50, unique=False, default='user')
    email = models.EmailField(unique=True, db_index=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    is_premium = models.BooleanField(default=False, db_index=True)
    premium_expiration = models.DateTimeField(null=True, blank=True)
    session_id = models.CharField(max_length=64, null=True, blank=True, db_index=True)
    is_email_verified = models.BooleanField(default=False)
    email_verification_otp = models.CharField(max_length=6, blank=True, null=True)
    otp_created_at = models.DateTimeField(blank=True, null=True)
    password_reset_otp = models.CharField(max_length=6, blank=True, null=True)
    password_reset_otp_created_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    objects = UserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['is_premium', 'is_email_verified']),
        ]
    
    def __str__(self):
        return self.email
    
    def generate_otp(self):
        """Generate a 6-digit OTP for email verification (in memory only).
        Caller must call commit_otp() after the email is successfully sent."""
        self.email_verification_otp = str(random.randint(100000, 999999))
        self.otp_created_at = timezone.now()
        return self.email_verification_otp

    def commit_otp(self):
        """Persist the OTP to the database. Call only after email is sent."""
        self.save(update_fields=['email_verification_otp', 'otp_created_at'])
    
    def verify_otp(self, otp):
        """Verify the OTP and check if it's still valid (10 minutes expiry)."""
        if not self.email_verification_otp or not self.otp_created_at:
            return False
        
        # Check if OTP matches
        if self.email_verification_otp != otp:
            return False
        
        # Check if OTP is expired (10 minutes)
        expiry_time = self.otp_created_at + timedelta(minutes=10)
        if timezone.now() > expiry_time:
            return False
        
        # OTP is valid
        self.is_email_verified = True
        self.email_verification_otp = None
        self.otp_created_at = None
        self.save()
        return True
    
    def generate_password_reset_otp(self):
        """Generate a 6-digit OTP for password reset (in memory only).
        Caller must call commit_password_reset_otp() after the email is successfully sent."""
        self.password_reset_otp = str(random.randint(100000, 999999))
        self.password_reset_otp_created_at = timezone.now()
        return self.password_reset_otp

    def commit_password_reset_otp(self):
        """Persist the password-reset OTP to the database. Call only after email is sent."""
        self.save(update_fields=['password_reset_otp', 'password_reset_otp_created_at'])
    
    def verify_password_reset_otp(self, otp):
        """Verify the password reset OTP and check if it's still valid (10 minutes expiry)."""
        if not self.password_reset_otp or not self.password_reset_otp_created_at:
            return False
        
        # Check if OTP matches
        if self.password_reset_otp != otp:
            return False
        
        # Check if OTP is expired (10 minutes)
        expiry_time = self.password_reset_otp_created_at + timedelta(minutes=10)
        if timezone.now() > expiry_time:
            return False
        
        return True
    
    def clear_password_reset_otp(self):
        """Clear password reset OTP after successful password reset."""
        self.password_reset_otp = None
        self.password_reset_otp_created_at = None
        self.save()
    
    def update_premium_status(self):
        """Update premium status based on active subscriptions."""
        from subscriptions.models import Subscription
        
        has_active_subscription = Subscription.objects.filter(
            user=self,
            status='ACTIVE'
        ).exists()
        
        if self.is_premium != has_active_subscription:
            self.is_premium = has_active_subscription
            self.save(update_fields=['is_premium'])
        
        return self.is_premium

    def rotate_session(self):
        """Generate a new session_id, invalidating any previous device."""
        self.session_id = uuid.uuid4().hex
        self.save(update_fields=['session_id'])
        return self.session_id

    def check_premium_expiration(self):
        """Auto-expire premium if expiration date has passed. Returns True if still premium."""
        if self.is_premium and self.premium_expiration:
            if timezone.now() >= self.premium_expiration:
                self.is_premium = False
                self.premium_expiration = None
                self.save(update_fields=['is_premium', 'premium_expiration'])
                return False
        return self.is_premium
