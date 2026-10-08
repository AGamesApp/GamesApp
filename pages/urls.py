from django.urls import path
from .views import PageDetailView

app_name = 'pages'

urlpatterns = [
    path('<str:title>/', PageDetailView.as_view(), name='page-detail'),
]
