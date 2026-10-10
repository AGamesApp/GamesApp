from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from urllib.parse import quote, urlparse

User = get_user_model()


def validate_flexible_url(value):
    """
    Custom URL validator that accepts URLs with spaces and special characters.
    Very permissive - only checks for http/https and domain.
    """
    if not value:
        return value
    
    # Just check if it starts with http:// or https:// and has a domain
    if not (value.startswith('http://') or value.startswith('https://')):
        raise ValidationError('URL must start with http:// or https://')
    
    # Check if there's something after the protocol
    if len(value) <= 8:  # "https://" is 8 chars
        raise ValidationError('Enter a complete URL')
    
    return value


class Emulator(models.Model):
    name = models.CharField(max_length=100, unique=True)
    icon = models.ImageField(upload_to='emulator_icons/', blank=True, null=True)
    # Priority for ordering in lists (higher number = higher priority)
    priority = models.IntegerField(default=0, db_index=True, help_text='Higher values appear first in lists')
    package_name = models.CharField(max_length=255, blank=True, default="", help_text="Optional Android package name for emulator (e.g. com.example.app)")
    download_url = models.TextField(max_length=1000, blank=True, default='')
    video_url = models.TextField(max_length=1000, blank=True, default='', validators=[validate_flexible_url])
    open_outside = models.BooleanField(default=False, help_text='If True, emulator opens in external browser/app')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Genre(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class Game(models.Model):
    title = models.CharField(max_length=200, db_index=True)
    description = models.TextField(blank=True, default='', help_text='Game description')
    emulator = models.ForeignKey(Emulator, on_delete=models.CASCADE, related_name='games')
    # Priority for ordering in lists (higher number = higher priority)
    priority = models.IntegerField(default=0, db_index=True, help_text='Higher values appear first in lists')
    image_url = models.TextField(max_length=500, blank=True, default='', validators=[validate_flexible_url])
    size = models.CharField(max_length=50, blank=True)
    download_url = models.TextField(max_length=1000, blank=True, default='', validators=[validate_flexible_url])
    game_url = models.TextField(max_length=1000, blank=True, default='', validators=[validate_flexible_url])
    video_url = models.TextField(max_length=1000, blank=True, default='', validators=[validate_flexible_url])
    region = models.CharField(max_length=100, blank=True, default='')
    genres = models.ManyToManyField(Genre, related_name='games', blank=True)
    is_premium = models.BooleanField(default=False, db_index=True)
    year = models.CharField(max_length=10, blank=True, default='')
    views = models.PositiveIntegerField(default=0, db_index=True)  # Track how many times game was viewed
    downloads = models.PositiveIntegerField(default=0, db_index=True)  # Track download count
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-views', '-downloads', '-created_at']  # Order by views (primary), downloads (secondary), created_at (tertiary)
        # No unique constraint - allow duplicate entries (each row is unique by ID)
        indexes = [
            models.Index(fields=['emulator', 'is_premium']),
            models.Index(fields=['-views', '-created_at']),
            models.Index(fields=['-downloads', '-created_at']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return self.title
    
    def increment_views(self):
        """Increment the view count for this game."""
        self.views += 1
        self.save(update_fields=['views'])
    
    def increment_downloads(self):
        """Increment the download count for this game."""
        self.downloads += 1
        self.save(update_fields=['downloads'])

    @property
    def average_rating(self):
        """Calculate average rating with aggregation (optimized)."""
        from django.db.models import Avg
        result = self.ratings.aggregate(avg=Avg('score'))
        return round(result['avg'], 1) if result['avg'] else 0

    @property
    def total_loves(self):
        """Count total loves (use prefetch_related for optimization)."""
        return self.loves.count()


class GameRating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ratings')
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='ratings')
    score = models.DecimalField(max_digits=2, decimal_places=1, validators=[MinValueValidator(1), MaxValueValidator(5)])
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['user', 'game']
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['game', '-created_at']),  # Optimize fetching ratings for a game
            models.Index(fields=['user', '-created_at']),  # Optimize fetching user's ratings
        ]

    def __str__(self):
        return f"{self.user.email} - {self.game.title} - {self.score}/5"


class GameImage(models.Model):
    """Store multiple images/screenshots for a game."""
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='images')
    # Either an external URL (image_path) or an uploaded file (image_file)
    image_path = models.TextField(max_length=500, blank=True, default='', validators=[validate_flexible_url])
    image_file = models.ImageField(upload_to='game_images/', blank=True, null=True)
    order = models.PositiveIntegerField(default=0)  # To maintain image order
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', 'created_at']
        indexes = [
            models.Index(fields=['game', 'order']),
        ]

    def __str__(self):
        return f"{self.game.title} - Image {self.order}"

    @property
    def url(self):
        """Return the URL of the image - uploaded file takes precedence."""
        if self.image_file:
            try:
                return self.image_file.url
            except Exception:
                return self.image_path
        return self.image_path
    
    def save(self, *args, **kwargs):
        """Auto-assign order if not set."""
        if not self.pk and self.order == 0:
            # Get the max order for this game and increment
            max_order = GameImage.objects.filter(game=self.game).aggregate(
                models.Max('order')
            )['order__max']
            self.order = (max_order or -1) + 1
        super().save(*args, **kwargs)


class GameAdditionalFile(models.Model):
    """Store additional files for a game (patches, DLCs, mods, etc.)."""
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='additional_files')
    file_name = models.CharField(max_length=200, help_text='Name of the file (e.g., Patch 1.5, DLC Pack)')
    download_link = models.TextField(max_length=1000, help_text='Download link for the file')
    file_path = models.TextField(max_length=500, blank=True, default='', help_text='File path or identifier')
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', 'created_at']
        indexes = [
            models.Index(fields=['game', 'order']),
        ]

    def __str__(self):
        return f"{self.game.title} - {self.file_name}"
    
    def save(self, *args, **kwargs):
        """Auto-assign order if not set."""
        if not self.pk and self.order == 0:
            # Get the max order for this game and increment
            max_order = GameAdditionalFile.objects.filter(game=self.game).aggregate(
                models.Max('order')
            )['order__max']
            self.order = (max_order or -1) + 1
        super().save(*args, **kwargs)


class EmulatorAdditionalFile(models.Model):
    """Store additional files for an emulator (BIOS, plugins, etc.)."""
    emulator = models.ForeignKey(Emulator, on_delete=models.CASCADE, related_name='additional_files')
    file_name = models.CharField(max_length=200, help_text='Name of the file (e.g., BIOS Files, Graphics Plugin)')
    download_link = models.TextField(max_length=1000, help_text='Download link for the file')
    file_path = models.TextField(max_length=500, blank=True, default='', help_text='File path or identifier')
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', 'created_at']
        indexes = [
            models.Index(fields=['emulator', 'order']),
        ]

    def __str__(self):
        return f"{self.emulator.name} - {self.file_name}"
    
    def save(self, *args, **kwargs):
        """Auto-assign order if not set."""
        if not self.pk and self.order == 0:
            # Get the max order for this emulator and increment
            max_order = EmulatorAdditionalFile.objects.filter(emulator=self.emulator).aggregate(
                models.Max('order')
            )['order__max']
            self.order = (max_order or -1) + 1
        super().save(*args, **kwargs)


class GameReview(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='reviews')
    review = models.TextField(blank=True, default='')  # Allow empty reviews
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['user', 'game']  # One review per user per game
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['game', '-created_at']),  # Optimize fetching reviews for a game
            models.Index(fields=['user', '-created_at']),  # Optimize fetching user's reviews
        ]

    def __str__(self):
        return f"{self.user.email} reviewed {self.game.title}"


class GameLove(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='loved_games')
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='loves')
    loved_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        unique_together = ['user', 'game']
        ordering = ['-loved_at']
        indexes = [
            models.Index(fields=['game', '-loved_at']),  # Optimize love stats for a game
            models.Index(fields=['user', '-loved_at']),  # Optimize user's loved games list
        ]

    def __str__(self):
        return f"{self.user.email} ❤️ {self.game.title}"


class AppSettings(models.Model):
    """App configuration settings - should only have one record."""
    app_version = models.CharField(max_length=50, default='1.0.0', help_text='Current app version')
    app_link = models.TextField(default='https://play.google.com/store/apps/details?id=get.orepsp2.emulatorgame', help_text='Link to app on Play Store')
    under_maintenance = models.BooleanField(default=False, help_text='Is the app under maintenance?')
    
    # New fields
    show_popup = models.BooleanField(default=False, help_text='Show popup dialog to users')
    popup_title = models.CharField(max_length=200, blank=True, default='', help_text='Title for the popup dialog')
    popup_description = models.TextField(blank=True, default='', help_text='Description/message for the popup dialog')
    popup_link = models.CharField(max_length=500, blank=True, default='', help_text='Optional link/URL for popup action')
    device_mode_required = models.BooleanField(
        default=False,
        help_text='Device Token Mode: ON = Required (strict, blocks requests without valid token) | OFF = Passive (observation only, all requests allowed)'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'App Settings'
        verbose_name_plural = 'App Settings'

    def __str__(self):
        return f"App Settings (v{self.app_version})"

    def save(self, *args, **kwargs):
        """Ensure only one instance exists."""
        if not self.pk and AppSettings.objects.exists():
            raise ValidationError('There can be only one AppSettings instance')
        return super().save(*args, **kwargs)
