from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token
from django.core.files.uploadedfile import SimpleUploadedFile
from .models import (
    Emulator, Game, GameLove, GameRating, GameReview, Genre,
    GameImage, GameAdditionalFile, EmulatorAdditionalFile
)
import uuid

User = get_user_model()


def unique_username():
    return f"user_{uuid.uuid4().hex[:6]}"


class EmulatorTests(APITestCase):
    """Test suite for Emulator model and endpoints."""
    
    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        self.emulator1 = Emulator.objects.create(
            name="PlayStation 2",
            download_url="https://example.com/ps2.zip",
            video_url="https://youtube.com/ps2-tutorial"
        )
        self.emulator2 = Emulator.objects.create(
            name="Nintendo 64",
            download_url="https://example.com/n64.zip"
        )
    
    def test_list_emulators(self):
        """Test listing all emulators."""
        url = reverse('games:emulator-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # API returns paginated results
        self.assertEqual(response.data['count'], 2)
        self.assertEqual(response.data['results'][0]['name'], "Nintendo 64")  # Ordered by name
        self.assertEqual(response.data['results'][1]['name'], "PlayStation 2")
    
    def test_retrieve_emulator(self):
        """Test retrieving a single emulator."""
        url = reverse('games:emulator-detail', kwargs={'pk': self.emulator1.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], "PlayStation 2")
        self.assertEqual(response.data['download_url'], "https://example.com/ps2.zip")
        self.assertEqual(response.data['video_url'], "https://youtube.com/ps2-tutorial")
    
    def test_search_emulators(self):
        """Test searching emulators by name."""
        url = reverse('games:emulator-list')
        response = self.client.get(url, {'search': 'Play'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['name'], "PlayStation 2")
    
    def test_emulator_additional_files(self):
        """Test adding additional files to emulator."""
        file1 = EmulatorAdditionalFile.objects.create(
            emulator=self.emulator1,
            file_name="BIOS Pack",
            download_link="https://example.com/bios.zip",
            file_path="emulators/ps2/bios/",
            order=0
        )
        file2 = EmulatorAdditionalFile.objects.create(
            emulator=self.emulator1,
            file_name="Graphics Plugin",
            download_link="https://example.com/plugin.zip",
            order=1
        )
        
        # Test that files are ordered correctly
        files = self.emulator1.additional_files.all()
        self.assertEqual(files.count(), 2)
        self.assertEqual(files[0].file_name, "BIOS Pack")
        self.assertEqual(files[1].file_name, "Graphics Plugin")
        self.assertEqual(str(files[0]), "PlayStation 2 - BIOS Pack")


class GameModelTests(APITestCase):
    """Test suite for Game model."""
    
    def setUp(self):
        """Set up test data."""
        self.emulator = Emulator.objects.create(name="Test Emulator")
        self.genre1 = Genre.objects.create(name="Action")
        self.genre2 = Genre.objects.create(name="RPG")
        
        self.game = Game.objects.create(
            title="Test Game",
            emulator=self.emulator,
            image_url="https://example.com/game.jpg",
            size="500MB",
            download_url="https://example.com/game.zip",
            region="USA",
            year="2020",
            is_premium=False
        )
        self.game.genres.add(self.genre1, self.genre2)
    
    def test_game_creation(self):
        """Test game is created with correct attributes."""
        self.assertEqual(self.game.title, "Test Game")
        self.assertEqual(self.game.emulator.name, "Test Emulator")
        self.assertEqual(self.game.views, 0)
        self.assertEqual(self.game.downloads, 0)
        self.assertEqual(self.game.genres.count(), 2)
    
    def test_increment_views(self):
        """Test incrementing view count."""
        initial_views = self.game.views
        self.game.increment_views()
        
        self.game.refresh_from_db()
        self.assertEqual(self.game.views, initial_views + 1)
        
        # Increment multiple times
        self.game.increment_views()
        self.game.increment_views()
        self.game.refresh_from_db()
        self.assertEqual(self.game.views, initial_views + 3)
    
    def test_increment_downloads(self):
        """Test incrementing download count."""
        initial_downloads = self.game.downloads
        self.game.increment_downloads()
        
        self.game.refresh_from_db()
    def test_game_images(self):
        """Test adding multiple images to a game."""
        img1 = GameImage.objects.create(
            game=self.game,
            image_path="https://example.com/screenshot1.jpg",
            order=0
        )
        img2 = GameImage.objects.create(
            game=self.game,
            image_path="https://example.com/screenshot2.jpg",
            order=1
        )
        img3 = GameImage.objects.create(
            game=self.game,
            image_path="https://example.com/screenshot3.jpg",
            order=2
        )
        
        # Test ordering
        images = self.game.images.all()
        self.assertEqual(images.count(), 3)
        self.assertEqual(images[0].image_path, "https://example.com/screenshot1.jpg")
        self.assertEqual(images[1].image_path, "https://example.com/screenshot2.jpg")
        self.assertEqual(images[2].image_path, "https://example.com/screenshot3.jpg")
        self.assertEqual(images[1].order, 1)
        self.assertEqual(images[2].order, 2)
    
    def test_game_additional_files(self):
        """Test adding additional files to a game."""
        file1 = GameAdditionalFile.objects.create(
            game=self.game,
            file_name="Patch 1.5",
            download_link="https://example.com/patch.zip",
            file_path="games/patches/v1.5"
        )
        file2 = GameAdditionalFile.objects.create(
            game=self.game,
            file_name="DLC Pack",
            download_link="https://example.com/dlc.zip"
        )
        
        files = self.game.additional_files.all()
        self.assertEqual(files.count(), 2)
        self.assertEqual(files[0].file_name, "Patch 1.5")
        self.assertEqual(str(files[1]), "Test Game - DLC Pack")


class GameRatingTests(APITestCase):
    """Test suite for Game rating system."""
    
    def setUp(self):
        """Set up test data."""
        self.user1 = User.objects.create_user(
            email="user1@test.com",
            username=unique_username(),
            password="testpass"
        )
        self.user2 = User.objects.create_user(
            email="user2@test.com",
            username=unique_username(),
            password="testpass"
        )
        
        self.token1 = Token.objects.create(user=self.user1)
        self.token2 = Token.objects.create(user=self.user2)
        
        self.client1 = APIClient()
        self.client1.credentials(HTTP_AUTHORIZATION='Token ' + self.token1.key)
        
        self.client2 = APIClient()
        self.client2.credentials(HTTP_AUTHORIZATION='Token ' + self.token2.key)
        
        self.emulator = Emulator.objects.create(name="Test Emulator")
        self.game = Game.objects.create(
            title="Test Game",
            emulator=self.emulator
        )
    
    def test_rate_game(self):
        """Test user can rate a game."""
        url = reverse('games:game-rate', kwargs={'pk': self.game.pk})
        response = self.client1.post(url, {'score': 4.5})
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('Rating created successfully', response.data['message'])
        
        # Verify rating was created
        rating = GameRating.objects.filter(user=self.user1, game=self.game).first()
        self.assertIsNotNone(rating)
        self.assertEqual(float(rating.score), 4.5)
    
    def test_update_rating(self):
        """Test user can update their rating."""
        url = reverse('games:game-rate', kwargs={'pk': self.game.pk})
        
        # Create initial rating
        self.client1.post(url, {'score': 3.0})
        
        # Update rating
        response = self.client1.post(url, {'score': 5.0})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('Rating updated successfully', response.data['message'])
        
        # Verify only one rating exists
        ratings = GameRating.objects.filter(user=self.user1, game=self.game)
        self.assertEqual(ratings.count(), 1)
        self.assertEqual(float(ratings.first().score), 5.0)
    
    def test_rating_validation(self):
        """Test rating score validation."""
        url = reverse('games:game-rate', kwargs={'pk': self.game.pk})
        
        # Test score too low
        response = self.client1.post(url, {'score': 0.5})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Test score too high
        response = self.client1.post(url, {'score': 5.5})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Test invalid increment
        response = self.client1.post(url, {'score': 3.3})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Test valid scores
        valid_scores = [1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0]
        for score in valid_scores:
            response = self.client1.post(url, {'score': score})
            self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_201_CREATED])
    
    def test_average_rating(self):
        """Test average rating calculation."""
        # Create multiple ratings
        GameRating.objects.create(user=self.user1, game=self.game, score=4.0)
        GameRating.objects.create(user=self.user2, game=self.game, score=5.0)
        
        # Test average
        avg = self.game.average_rating
        self.assertEqual(avg, 4.5)
    
    def test_list_game_ratings(self):
        """Test listing all ratings for a game."""
        GameRating.objects.create(user=self.user1, game=self.game, score=4.0)
        GameRating.objects.create(user=self.user2, game=self.game, score=5.0)
        
        url = reverse('games:game-ratings', kwargs={'pk': self.game.pk})
        response = self.client1.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)


class GameReviewTests(APITestCase):
    """Test suite for Game review system."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            email="reviewer@test.com",
            username=unique_username(),
            password="testpass"
        )
        self.token = Token.objects.create(user=self.user)
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        
        self.emulator = Emulator.objects.create(name="Test Emulator")
        self.game = Game.objects.create(
            title="Test Game",
            emulator=self.emulator
        )
    
    def test_add_review(self):
        """Test user can add a review."""
        url = reverse('games:game-add-review', kwargs={'pk': self.game.pk})
        response = self.client.post(url, {'review': 'Great game!'})
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('Review added successfully', response.data['message'])
        
        # Verify review was created
        review = GameReview.objects.filter(user=self.user, game=self.game).first()
        self.assertIsNotNone(review)
        self.assertEqual(review.review, 'Great game!')
    
    def test_add_multiple_reviews(self):
        """Test user can add multiple reviews."""
        url = reverse('games:game-add-review', kwargs={'pk': self.game.pk})
        
        self.client.post(url, {'review': 'First review'})
        self.client.post(url, {'review': 'Second review'})
        self.client.post(url, {'review': 'Third review'})
        
        reviews = GameReview.objects.filter(user=self.user, game=self.game)
        self.assertEqual(reviews.count(), 3)
    
    def test_list_game_reviews(self):
        """Test listing all reviews for a game."""
        GameReview.objects.create(user=self.user, game=self.game, review='Review 1')
        GameReview.objects.create(user=self.user, game=self.game, review='Review 2')
        
        url = reverse('games:game-reviews', kwargs={'pk': self.game.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)
    
    def test_my_reviews(self):
        """Test listing user's own reviews."""
        # Create reviews for different games
        game2 = Game.objects.create(title="Game 2", emulator=self.emulator)
        
        GameReview.objects.create(user=self.user, game=self.game, review='Review 1')
        GameReview.objects.create(user=self.user, game=game2, review='Review 2')
        
        url = reverse('games:game-my-reviews')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)


class GameLoveTests(APITestCase):
    """Test suite for Game love/favorite system."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            email="lover@test.com",
            username=unique_username(),
            password="testpass"
        )
        self.token = Token.objects.create(user=self.user)
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        
        self.emulator = Emulator.objects.create(name="Test Emulator")
        self.game = Game.objects.create(
            title="Test Game",
            emulator=self.emulator
        )
    
    def test_love_game(self):
        """Test user can love a game."""
        url = reverse('games:game-love', kwargs={'pk': self.game.pk})
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['is_loved'])
        self.assertIn('added to loved games', response.data['message'])
        
        # Verify love was created
        love = GameLove.objects.filter(user=self.user, game=self.game).first()
        self.assertIsNotNone(love)
    
    def test_unlove_game(self):
        """Test user can unlove a game (toggle)."""
        url = reverse('games:game-love', kwargs={'pk': self.game.pk})
        
        # First love the game
        self.client.post(url)
        
        # Then unlove it
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['is_loved'])
        self.assertIn('removed from loved games', response.data['message'])
        
        # Verify love was deleted
        love = GameLove.objects.filter(user=self.user, game=self.game).first()
        self.assertIsNone(love)
    
    def test_total_loves(self):
        """Test total loves count."""
        user2 = User.objects.create_user(
            email="lover2@test.com",
            username=unique_username(),
            password="testpass"
        )
        
        GameLove.objects.create(user=self.user, game=self.game)
        GameLove.objects.create(user=user2, game=self.game)
        
        self.assertEqual(self.game.total_loves, 2)
    
    def test_my_loved_games(self):
        """Test listing user's loved games."""
        game2 = Game.objects.create(title="Game 2", emulator=self.emulator)
        game3 = Game.objects.create(title="Game 3", emulator=self.emulator)
        
        GameLove.objects.create(user=self.user, game=self.game)
        GameLove.objects.create(user=self.user, game=game2)
        GameLove.objects.create(user=self.user, game=game3)
        
        url = reverse('games:game-my-loved-games')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 3)


class GameAPITests(APITestCase):
    """Test suite for Game API endpoints."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            email="apiuser@test.com",
            username=unique_username(),
            password="testpass",
            is_premium=True
        )
        self.non_premium_user = User.objects.create_user(
            email="nonpremium@test.com",
            username=unique_username(),
            password="testpass",
            is_premium=False
        )
        
        self.token = Token.objects.create(user=self.user)
        self.non_premium_token = Token.objects.create(user=self.non_premium_user)
        
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        
        self.non_premium_client = APIClient()
        self.non_premium_client.credentials(HTTP_AUTHORIZATION='Token ' + self.non_premium_token.key)
        
        self.emulator = Emulator.objects.create(name="Test Emulator")
        self.genre1 = Genre.objects.create(name="Action")
        self.genre2 = Genre.objects.create(name="Adventure")
        
        self.game_free = Game.objects.create(
            title="Free Game",
            emulator=self.emulator,
            download_url="https://example.com/free.zip",
            is_premium=False
        )
        self.game_free.genres.add(self.genre1)
        
        self.game_premium = Game.objects.create(
            title="Premium Game",
            emulator=self.emulator,
            download_url="https://example.com/premium.zip",
            is_premium=True
        )
        self.game_premium.genres.add(self.genre2)
    
    def test_list_games(self):
        """Test listing all games."""
        url = reverse('games:game-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)
    
    def test_retrieve_game_increments_views(self):
        """Test retrieving a game increments view count."""
        initial_views = self.game_free.views
        
        url = reverse('games:game-detail', kwargs={'pk': self.game_free.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.game_free.refresh_from_db()
        self.assertEqual(self.game_free.views, initial_views + 1)
    
    def test_filter_by_emulator(self):
        """Test filtering games by emulator."""
        emulator2 = Emulator.objects.create(name="Another Emulator")
        Game.objects.create(title="Game 3", emulator=emulator2)
        
        url = reverse('games:game-list')
        response = self.client.get(url, {'emulator': self.emulator.pk})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)
    
    def test_filter_by_genre(self):
        """Test filtering games by genre."""
        url = reverse('games:game-list')
        response = self.client.get(url, {'genres': self.genre1.pk})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['title'], "Free Game")
    
    def test_filter_by_premium(self):
        """Test filtering premium games."""
        url = reverse('games:game-list')
        response = self.client.get(url, {'is_premium': 'true'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['title'], "Premium Game")
    
    def test_search_games(self):
        """Test searching games."""
        url = reverse('games:game-list')
        response = self.client.get(url, {'search': 'Free'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['title'], "Free Game")
    
    def test_download_free_game(self):
        """Test downloading a free game."""
        url = reverse('games:game-download', kwargs={'pk': self.game_free.pk})
        initial_downloads = self.game_free.downloads
        
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('Download started', response.data['message'])
        
        self.game_free.refresh_from_db()
        self.assertEqual(self.game_free.downloads, initial_downloads + 1)
    
    def test_download_premium_game_with_premium_user(self):
        """Test premium user can download premium game."""
        url = reverse('games:game-download', kwargs={'pk': self.game_premium.pk})
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_download_premium_game_without_premium(self):
        """Test non-premium user cannot download premium game."""
        url = reverse('games:game-download', kwargs={'pk': self.game_premium.pk})
        response = self.non_premium_client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn('Premium subscription required', response.data['error'])
    
    def test_ordering_games(self):
        """Test ordering games by different fields."""
        # Create games with different attributes
        game1 = Game.objects.create(title="A Game", emulator=self.emulator, views=100)
        game2 = Game.objects.create(title="B Game", emulator=self.emulator, views=200)
        game3 = Game.objects.create(title="C Game", emulator=self.emulator, downloads=50)
        
        url = reverse('games:game-list')
        
        # Test ordering by views
        response = self.client.get(url, {'ordering': '-views'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['results'][0]['title'], "B Game")
        
        # Test ordering by title
        response = self.client.get(url, {'ordering': 'title'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['results'][0]['title'], "A Game")


class AdvancedSearchTests(APITestCase):
    """Test suite for advanced search functionality."""
    
    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        self.emulator = Emulator.objects.create(name="Test Emulator")
        
        # Create games with various names
        Game.objects.create(title="Sonic Adventure", emulator=self.emulator)
        Game.objects.create(title="Super Mario Bros", emulator=self.emulator)
        Game.objects.create(title="Street Fighter", emulator=self.emulator)
        Game.objects.create(title="Final Fantasy VII", emulator=self.emulator)
    
    def test_exact_match(self):
        """Test exact title match gets highest priority."""
        url = reverse('games:game-list')
        response = self.client.get(url, {'search': 'Sonic Adventure'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(response.data['count'], 0)
        self.assertEqual(response.data['results'][0]['title'], "Sonic Adventure")
    
    def test_starts_with_match(self):
        """Test title starts with match."""
        url = reverse('games:game-list')
        response = self.client.get(url, {'search': 'Super'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['results'][0]['title'], "Super Mario Bros")
    
    def test_contains_match(self):
        """Test title contains match."""
        url = reverse('games:game-list')
        response = self.client.get(url, {'search': 'Fighter'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(response.data['count'], 0)
    
    def test_character_subsequence_match(self):
        """Test character subsequence matching."""
        url = reverse('games:game-list')
        # "sa" should match "Sonic Adventure" (S...a)
        response = self.client.get(url, {'search': 'sa'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(response.data['count'], 0)

