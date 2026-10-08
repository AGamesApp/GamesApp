from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DeviceTokenViewSet, NotificationLogViewSet, NotificationViewSet

app_name = 'notifications'

router = DefaultRouter()
router.register(r'devices', DeviceTokenViewSet, basename='device')
router.register(r'logs', NotificationLogViewSet, basename='log')
router.register(r'', NotificationViewSet, basename='notification')

urlpatterns = [
    path('', include(router.urls)),
]
