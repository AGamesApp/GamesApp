"""
Email template utilities for AGames
Handles loading and rendering branded email templates
"""
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.conf import settings


def send_verification_email(user, code):
    """
    Send verification code email with AGames branding
    
    Args:
        user: User instance
        code: 6-digit verification code
    """
    context = {
        'code': code,
        'username': user.username,
        'email': user.email
    }
    
    # Render HTML template
    html_message = render_to_string('emails/verification_code.html', context)
    
    # Plain text fallback
    plain_message = f'''Hi {user.username},

Welcome to AGames Pro! Your email verification code is:

{code}

This code will expire in 10 minutes.

If you didn't request this code, please ignore this email.

Thank you for joining AGames Pro!
---
AGames Pro - Your Ultimate Gaming Platform
GBA • NES • PS2 • PSP • PSX • Wii
© 2026 AGames Pro. All rights reserved.'''
    
    # Send email
    email = EmailMultiAlternatives(
        subject='Your Verification Code - AGames Pro',
        body=plain_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[user.email]
    )
    email.attach_alternative(html_message, "text/html")
    email.send(fail_silently=False)


def send_password_reset_email(user, code):
    """
    Send password reset code email with AGames Pro branding
    
    Args:
        user: User instance
        code: 6-digit reset code
    """
    context = {
        'code': code,
        'username': user.username,
        'email': user.email
    }
    
    # Render HTML template
    html_message = render_to_string('emails/password_reset.html', context)
    
    # Plain text fallback
    plain_message = f'''Hi {user.username},

You requested a password reset for your AGames Pro account.

Your password reset code is:

{code}

This code will expire in 10 minutes.

If you didn't request a password reset, please ignore this email and your password will remain unchanged.

---
AGames Pro Security Team
© 2026 AGames Pro. All rights reserved.'''
    
    # Send email
    email = EmailMultiAlternatives(
        subject='Password Reset Code - AGames Pro',
        body=plain_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[user.email]
    )
    email.attach_alternative(html_message, "text/html")
    email.send(fail_silently=False)
