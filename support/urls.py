from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# API Router
router = DefaultRouter()
router.register(r'messages', views.SupportMessageViewSet, basename='support-message')

app_name = 'support'

urlpatterns = [
    # API endpoints (no 'api/' prefix here since it's already in main urls.py)
    path('', include(router.urls)),
]
