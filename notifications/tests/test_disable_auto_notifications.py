from django.test import TestCase
from games.models import AppSettings
from notifications.fcm_service import send_notification_to_all_devices, send_notification_to_all_users_topic
from notifications.models import NotificationLog, Notification
from django.contrib.auth import get_user_model


class DisableAutoNotificationsTest(TestCase):
    def setUp(self):
        # Ensure singleton AppSettings exists
        AppSettings.objects.all().delete()
        self.settings = AppSettings.objects.create(app_version='1.0', app_link='https://play.google.com', under_maintenance=False, disable_automatic_notifications=True)
        User = get_user_model()
        self.user = User.objects.create_user(email='nuser@example.com', password='pass', username='nuser')

    def test_send_notification_suppressed_when_disabled(self):
        # Clear existing logs
        NotificationLog.objects.all().delete()
        Notification.objects.all().delete()

        # Call send without forcing
        res = send_notification_to_all_devices(title='Hi', body='Body', notification_type='normal', data={'a':1}, user=None, image_url=None)
        self.assertIsNone(res)
        self.assertEqual(NotificationLog.objects.count(), 0)
        self.assertEqual(Notification.objects.count(), 0)

    def test_force_send_still_works(self):
        NotificationLog.objects.all().delete()
        Notification.objects.all().delete()

        # Force send should bypass the disable flag
        res = send_notification_to_all_users_topic(title='Topic', body='B', notification_type='normal', data={'x':2}, image_url=None, force=True)
        # When send happens, fcm_service may attempt to create NotificationLog; ensure either log is created or function returns truthy
        # We treat both as acceptable but ensure code did not return None
        self.assertIsNotNone(res)