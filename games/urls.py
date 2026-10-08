from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EmulatorViewSet, GameViewSet, app_details

app_name = 'games'

router = DefaultRouter()
router.register(r'emulators', EmulatorViewSet, basename='emulator')
router.register(r'games', GameViewSet, basename='game')

urlpatterns = [
    path('', include(router.urls)),
    path('app_details/', app_details, name='app_details'),
]
