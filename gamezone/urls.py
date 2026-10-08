"""
URL configuration for gamezone project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView, TemplateView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from .health import health_check
from .assetlinks import assetlinks_json, privacy_policy
from users.allauth_redirect import DisableAllauthWebUI
from games.views import game_redirect_view
from pages.csrf_views import CSRFSafeLandingView
from .integrity_views import VerifyDeviceTokenView

urlpatterns = [
    # Root - Landing page (with proper CSRF handling)
    path('', CSRFSafeLandingView.as_view(), name='home'),
    
    # Health check endpoint (for monitoring)
    path('health/', health_check, name='health_check'),
    
    # Android App Links verification
    path('.well-known/assetlinks.json', assetlinks_json, name='assetlinks'),
    
    # Privacy Policy
    path('privacy/', privacy_policy, name='privacy_policy'),
    
    # Game redirect to Play Store
    path('game/', game_redirect_view, name='game_redirect_base'),  # Redirect /game to Play Store
    path('game/<int:game_id>/', game_redirect_view, name='game_redirect'),
    
    # Redirect /admin/ to custom admin
    path('admin/', RedirectView.as_view(pattern_name='customadmin:dashboard', permanent=False)),
    # Custom Admin Dashboard (main admin interface)
    path('customadmin/', include('customadmin.urls')),
    # API endpoints
    path('api/users/', include('users.urls')),
    path('api/', include('games.urls')),
    path('api/', include('subscriptions.urls')),
    path('api/', include('payments.urls')),
    path('api/pages/', include('pages.urls')),
    path('api/notifications/', include('notifications.urls')),
    path('api/support/', include('support.urls')),
    # Google Play Integrity — device token verification
    path('api/verify-device/', VerifyDeviceTokenView.as_view(), name='verify-device'),
    
    # OAuth - Redirect web UI to API instructions (we use API-based auth)
    re_path(r'^accounts/google/', DisableAllauthWebUI.as_view(), name='allauth-redirect'),
    path('accounts/', include('allauth.urls')),
    
    # API Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

