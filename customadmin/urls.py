from django.urls import path
from . import views
from support.views import SupportMessagesListView, ToggleReviewView, DeleteSupportMessageView, DeleteAllSupportMessagesView, MarkAllAsReviewedView

app_name = 'customadmin'

urlpatterns = [
    # Authentication
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    
    # Dashboard
    path('', views.DashboardView.as_view(), name='dashboard'),
    
    # Game URLs
    path('games/', views.GameListView.as_view(), name='game_list'),
    path('games/create/', views.GameCreateView.as_view(), name='game_create'),
    path('games/<int:pk>/edit/', views.GameUpdateView.as_view(), name='game_edit'),
    path('games/<int:pk>/delete/', views.GameDeleteView.as_view(), name='game_delete'),
    path('games/bulk-delete/', views.GameBulkDeleteView.as_view(), name='game_bulk_delete'),
    
    # Emulator URLs
    path('emulators/', views.EmulatorListView.as_view(), name='emulator_list'),
    path('emulators/create/', views.EmulatorCreateView.as_view(), name='emulator_create'),
    path('emulators/<int:pk>/edit/', views.EmulatorUpdateView.as_view(), name='emulator_edit'),
    path('emulators/<int:pk>/delete/', views.EmulatorDeleteView.as_view(), name='emulator_delete'),
    
    # Genre URLs
    path('genres/', views.GenreListView.as_view(), name='genre_list'),
    path('genres/create/', views.GenreCreateView.as_view(), name='genre_create'),
    path('genres/<int:pk>/edit/', views.GenreUpdateView.as_view(), name='genre_edit'),
    path('genres/<int:pk>/delete/', views.GenreDeleteView.as_view(), name='genre_delete'),
    
    # Page URLs
    path('pages/', views.PageListView.as_view(), name='page_list'),
    path('pages/create/', views.PageCreateView.as_view(), name='page_create'),
    path('pages/<int:pk>/edit/', views.PageUpdateView.as_view(), name='page_edit'),
    path('pages/<int:pk>/delete/', views.PageDeleteView.as_view(), name='page_delete'),
    
    # Notification URLs
    path('notifications/send/', views.NotificationSendView.as_view(), name='notification_send'),
    
    # App Settings URLs
    path('settings/', views.AppSettingsView.as_view(), name='app_settings'),

    # Import games via Excel file
    path('import/', views.ImportGamesView.as_view(), name='import_games'),
    
    # Export games to Excel
    path('export/', views.ExportGamesView.as_view(), name='export_games'),

    # User management
    path('users/', views.UserListView.as_view(), name='user_list'),
    path('users/<int:user_id>/delete/', views.UserDeleteView.as_view(), name='user_delete'),

    # Reviews management
    path('reviews/', views.ReviewListView.as_view(), name='review_list'),
    path('reviews/<int:review_id>/delete/', views.ReviewDeleteView.as_view(), name='review_delete'),
    path('reviews/bulk-delete/', views.ReviewBulkDeleteView.as_view(), name='review_bulk_delete'),
    
    # Support URLs
    path('support/', SupportMessagesListView.as_view(), name='support_messages'),
    path('support/<int:message_id>/toggle/', ToggleReviewView.as_view(), name='toggle_review'),
    path('support/<int:message_id>/delete/', DeleteSupportMessageView.as_view(), name='delete_support_message'),
    path('support/delete-all/', DeleteAllSupportMessagesView.as_view(), name='delete_all_support_messages'),
    path('support/mark-all-reviewed/', MarkAllAsReviewedView.as_view(), name='mark_all_reviewed'),
]
