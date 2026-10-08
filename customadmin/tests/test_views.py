from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from unittest.mock import patch

from games.models import Emulator, Game, GameReview, GameRating, GameLove
from notifications.models import DeviceToken, Notification


class CustomAdminViewsTest(TestCase):
    def setUp(self):
        User = get_user_model()
        # Create a superuser for access
        self.admin = User.objects.create_superuser(email='admin@example.com', password='adminpass', username='admin')

        # Create an emulator and a game to attach reviews/ratings/loves
        self.emulator = Emulator.objects.create(name='TestEmu')
        self.game = Game.objects.create(title='TestGame', emulator=self.emulator)

    @patch('customadmin.views.importer.import_games_from_sheet')
    def test_import_view_get_and_post_invokes_importer(self, mock_import):
        self.client.force_login(self.admin)

        url = reverse('customadmin:import_games')
        # GET should return 200 and render the form
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)

        # POST should call the importer and redirect to game list
        sheet_url = 'https://docs.google.com/spreadsheets/d/FAKE_ID'
        resp = self.client.post(url, {'sheet_url': sheet_url})
        self.assertEqual(resp.status_code, 302)
        mock_import.assert_called_once_with(sheet_url)

    def test_user_delete_cascades_related_objects(self):
        User = get_user_model()
        # Create a normal user with related objects
        user = User.objects.create_user(email='user@example.com', password='userpass', username='user1')

        # Related objects
        GameReview.objects.create(user=user, game=self.game, review='Nice')
        GameRating.objects.create(user=user, game=self.game, score=4.5)
        GameLove.objects.create(user=user, game=self.game)
        DeviceToken.objects.create(user=user, token='tok123')
        Notification.objects.create(user=user, title='T', body='B')

        # Ensure they exist
        self.assertTrue(GameReview.objects.filter(user=user).exists())
        self.assertTrue(GameRating.objects.filter(user=user).exists())
        self.assertTrue(GameLove.objects.filter(user=user).exists())
        self.assertTrue(DeviceToken.objects.filter(user=user).exists())
        self.assertTrue(Notification.objects.filter(user=user).exists())

        # Delete via admin view
        self.client.force_login(self.admin)
        url = reverse('customadmin:user_delete', args=[user.id])
        resp = self.client.post(url)
        self.assertEqual(resp.status_code, 302)

        # User and related objects should be gone
        self.assertFalse(User.objects.filter(pk=user.pk).exists())
        self.assertFalse(GameReview.objects.filter(user=user).exists())
        self.assertFalse(GameRating.objects.filter(user=user).exists())
        self.assertFalse(GameLove.objects.filter(user=user).exists())
        self.assertFalse(DeviceToken.objects.filter(user=user).exists())
        self.assertFalse(Notification.objects.filter(user=user).exists())

    def test_review_delete_view_removes_review(self):
        User = get_user_model()
        user = User.objects.create_user(email='ruser@example.com', password='pass', username='ruser')
        review = GameReview.objects.create(user=user, game=self.game, review='To be deleted')

        self.client.force_login(self.admin)
        url = reverse('customadmin:review_delete', args=[review.id])
        resp = self.client.post(url)
        self.assertEqual(resp.status_code, 302)
        self.assertFalse(GameReview.objects.filter(pk=review.pk).exists())
