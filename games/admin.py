from django.contrib import admin
from .models import Emulator, Game, GameRating, GameReview, Genre, GameLove, GameImage, AppSettings


# ----------------------------
# Emulator Admin
# ----------------------------
@admin.register(Emulator)
class EmulatorAdmin(admin.ModelAdmin):
    """Admin interface for Emulator model."""
    list_display = ['name', 'priority', 'download_url', 'created_at', 'updated_at']
    search_fields = ['name']
    ordering = ['-priority', 'name']
    date_hierarchy = 'created_at'
    readonly_fields = ['additional_files_display']
    
    def additional_files_display(self, obj):
        """Display additional files in a readable format"""
        if not obj.additional_files:
            return "No additional files"
        import json
        return json.dumps(obj.additional_files, indent=2)
    additional_files_display.short_description = 'Additional Files'


# ----------------------------
# Genre Admin
# ----------------------------
@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']
    ordering = ['name']


# ----------------------------
# GameImage Inline Admin
# ----------------------------
class GameImageInline(admin.TabularInline):
    """Inline admin for game images."""
    model = GameImage
    extra = 1
    fields = ['image_file', 'image_path', 'order']
    ordering = ['order']


# ----------------------------
# Game Admin
# ----------------------------
@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    """Admin interface for Game model."""
    list_display = ['title', 'priority', 'emulator', 'region', 'is_premium', 'year', 'views', 'average_rating', 'total_loves', 'downloads', 'created_at']
    list_filter = ['is_premium', 'emulator', 'created_at', 'genres']
    search_fields = ['title', 'region']
    ordering = ['-priority', '-views', '-downloads', '-created_at']  # Order by priority, then views, then downloads, then created_at
    date_hierarchy = 'created_at'
    filter_horizontal = ('genres',)  # easier ManyToMany management in admin
    inlines = [GameImageInline]  # Add images inline
    readonly_fields = ['additional_files_display']
    
    def additional_files_display(self, obj):
        """Display additional files in a readable format"""
        if not obj.additional_files:
            return "No additional files"
        import json
        return json.dumps(obj.additional_files, indent=2)
    additional_files_display.short_description = 'Additional Files'
    readonly_fields = ['views', 'downloads']  # Make views and downloads read-only in admin


# ----------------------------
# GameRating Admin
# ----------------------------
@admin.register(GameRating)
class GameRatingAdmin(admin.ModelAdmin):
    """Admin interface for GameRating model."""
    list_display = ['user', 'game', 'score', 'created_at', 'updated_at']
    list_filter = ['score', 'created_at']
    search_fields = ['user__email', 'game__title', 'review']
    ordering = ['-created_at']
    date_hierarchy = 'created_at'


# ----------------------------
# GameReview Admin
# ----------------------------
@admin.register(GameReview)
class GameReviewAdmin(admin.ModelAdmin):
    """Admin interface for GameReview model."""
    list_display = ['user', 'game', 'review_preview', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__email', 'game__title', 'review']
    ordering = ['-created_at']
    date_hierarchy = 'created_at'

    def review_preview(self, obj):
        return obj.review[:50] + '...' if len(obj.review) > 50 else obj.review
    review_preview.short_description = 'Review Preview'


# ----------------------------
# GameLove Admin
# ----------------------------
@admin.register(GameLove)
class GameLoveAdmin(admin.ModelAdmin):
    """Admin interface for GameLove model."""
    list_display = ['user', 'game', 'loved_at']
    list_filter = ['loved_at']
    search_fields = ['user__email', 'game__title']
    ordering = ['-loved_at']
    date_hierarchy = 'loved_at'


# ----------------------------
# AppSettings Admin
# ----------------------------
@admin.register(AppSettings)
class AppSettingsAdmin(admin.ModelAdmin):
    """Admin interface for AppSettings model."""
    list_display = ['app_version', 'app_link', 'under_maintenance', 'updated_at']
    readonly_fields = ['created_at', 'updated_at']
    
    def has_add_permission(self, request):
        """Only allow one instance."""
        return not AppSettings.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        """Prevent deletion."""
        return False
