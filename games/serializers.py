from rest_framework import serializers
from .models import Emulator, Game, GameRating, GameReview, Genre, GameLove, GameImage, GameAdditionalFile, EmulatorAdditionalFile, AppSettings


class GameAdditionalFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = GameAdditionalFile
        fields = ['id', 'file_name', 'download_link', 'file_path', 'order']
        read_only_fields = ['id', 'order']


class EmulatorAdditionalFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmulatorAdditionalFile
        fields = ['id', 'file_name', 'download_link', 'file_path', 'order']
        read_only_fields = ['id', 'order']


class EmulatorSerializer(serializers.ModelSerializer):
    additional_files = EmulatorAdditionalFileSerializer(many=True, read_only=True)
    
    class Meta:
        model = Emulator
        fields = ['id', 'name', 'icon', 'package_name', 'download_url', 'video_url', 'open_outside', 'additional_files', 'created_at']
        read_only_fields = ['id', 'created_at']


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ['id', 'name']


class GameImageSerializer(serializers.ModelSerializer):
    image_path = serializers.SerializerMethodField()

    class Meta:
        model = GameImage
        fields = ['id', 'image_path', 'order']
        read_only_fields = ['id', 'image_path']
    
    def get_image_path(self, obj):
        """Return single image URL - uploaded file takes precedence over external URL."""
        if obj.image_file:
            try:
                # Build full URL with domain for uploaded files
                request = self.context.get('request')
                if request is not None:
                    return request.build_absolute_uri(obj.image_file.url)
                # Fallback to relative URL if no request context
                return obj.image_file.url
            except Exception:
                # If file URL fails, try the image_path field
                return obj.image_path if obj.image_path else ''
        # Return external URL if no file uploaded
        return obj.image_path if obj.image_path else ''


class GameListSerializer(serializers.ModelSerializer):
    average_rating = serializers.DecimalField(source='avg_rating', max_digits=2, decimal_places=1, read_only=True)
    total_loves = serializers.IntegerField(source='love_count', read_only=True)
    total_downloads = serializers.IntegerField(source='downloads', read_only=True)

    class Meta:
        model = Game
        fields = ['id', 'title', 'description', 'image_url', 'views', 'average_rating', 'total_loves', 'total_downloads', 'is_premium']


class GameSerializer(serializers.ModelSerializer):
    emulator_name = serializers.CharField(source='emulator.name', read_only=True)
    average_rating = serializers.DecimalField(source='avg_rating', max_digits=2, decimal_places=1, read_only=True)
    total_downloads = serializers.IntegerField(source='downloads', read_only=True)
    total_loves = serializers.IntegerField(source='love_count', read_only=True)
    genres = serializers.SlugRelatedField(
        many=True, slug_field='name', queryset=Genre.objects.all(), required=False
    )
    additional_files = GameAdditionalFileSerializer(many=True, read_only=True)

    class Meta:
        model = Game
        fields = [
            'id', 'title', 'description', 'emulator', 'emulator_name',
            'image_url', 'size', 'download_url', 'game_url', 'video_url', 'additional_files', 'region', 'is_premium', 'year',
            'genres', 'views', 'average_rating', 'total_downloads', 'total_loves', 'created_at'
        ]
        read_only_fields = ['id', 'views', 'average_rating', 'total_downloads', 'total_loves', 'created_at']


class GameDetailSerializer(serializers.ModelSerializer):
    emulator = EmulatorSerializer(read_only=True)
    average_rating = serializers.DecimalField(source='avg_rating', max_digits=2, decimal_places=1, read_only=True)
    total_downloads = serializers.IntegerField(source='downloads', read_only=True)
    total_loves = serializers.IntegerField(source='love_count', read_only=True)
    genres = GenreSerializer(many=True, read_only=True)
    images = GameImageSerializer(many=True, read_only=True)
    additional_files = GameAdditionalFileSerializer(many=True, read_only=True)
    related_games = serializers.SerializerMethodField()

    class Meta:
        model = Game
        fields = [
            'id', 'title', 'description', 'emulator', 'image_url', 'images',
            'size', 'download_url', 'game_url', 'video_url', 'additional_files', 'region', 'is_premium', 'year', 'genres',
            'views', 'average_rating', 'total_downloads', 'total_loves', 
            'created_at', 'updated_at', 'related_games'
        ]
        read_only_fields = ['id', 'views', 'average_rating', 'total_downloads', 'total_loves', 'created_at', 'updated_at']
    
    def get_related_games(self, obj):
        """Get related games - same emulator and similar title or genres (limit 20)."""
        from django.db.models import Q, Count, Avg, Subquery, OuterRef, IntegerField, FloatField, Value
        from django.db.models.functions import Coalesce
        from django.core.cache import cache
        
        # Get pagination parameters from context
        request = self.context.get('request')
        page = int(request.query_params.get('related_page', 1)) if request else 1
        page_size = 20
        offset = (page - 1) * page_size
        
        # Cache key
        cache_key = f'related_games:{obj.id}:p{page}'
        cached = cache.get(cache_key)
        if cached:
            return cached
        
        # Efficient Subquery for love_count
        love_sub = Subquery(
            GameLove.objects.filter(game=OuterRef('pk')).order_by().values('game').annotate(c=Count('id')).values('c')[:1],
            output_field=IntegerField()
        )
        
        # Find related games with same emulator and similar title or shared genres
        related = Game.objects.filter(
            emulator=obj.emulator
        ).exclude(
            id=obj.id
        ).prefetch_related('genres').annotate(
            shared_genres=Count('genres', filter=Q(genres__in=obj.genres.all()))
        ).filter(
            Q(title__icontains=obj.title.split()[0]) |  # Similar title (first word)
            Q(shared_genres__gte=1)  # At least one shared genre
        ).select_related('emulator').annotate(
            love_count=Coalesce(love_sub, Value(0))
        ).order_by('-views', '-created_at').distinct()[offset:offset + page_size]
        
        result = GameListSerializer(related, many=True).data
        cache.set(cache_key, result, 600)  # Cache 10 min
        return result


class GameRatingSerializer(serializers.ModelSerializer):
    user_email = serializers.CharField(source='user.email', read_only=True)
    game_title = serializers.CharField(source='game.title', read_only=True)

    class Meta:
        model = GameRating
        fields = ['id', 'user', 'user_email', 'game', 'game_title', 'score', 'created_at', 'updated_at']
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']

    def validate_score(self, value):
        if not 1 <= value <= 5:
            raise serializers.ValidationError("Score must be between 1 and 5")
        # Ensure score is in 0.5 increments (1.0, 1.5, 2.0, 2.5, etc.)
        if float(value) % 0.5 != 0:
            raise serializers.ValidationError("Score must be in 0.5 increments (e.g., 1.0, 1.5, 2.0)")
        return value


class GameReviewSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    profile_picture = serializers.CharField(source='user.profile_picture', read_only=True)
    game_title = serializers.CharField(source='game.title', read_only=True)
    score = serializers.DecimalField(max_digits=2, decimal_places=1, write_only=False, required=False)
    comment_date = serializers.DateTimeField(source='updated_at', read_only=True)

    class Meta:
        model = GameReview
        fields = ['id', 'user', 'username', 'profile_picture', 'game', 'game_title', 'review', 'score', 'comment_date', 'created_at', 'updated_at']
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']
    
    def validate_score(self, value):
        """Validate score if provided."""
        if value is not None:
            if not 1 <= value <= 5:
                raise serializers.ValidationError("Score must be between 1 and 5")
            # Ensure score is in 0.5 increments (1.0, 1.5, 2.0, 2.5, etc.)
            if float(value) % 0.5 != 0:
                raise serializers.ValidationError("Score must be in 0.5 increments (e.g., 1.0, 1.5, 2.0)")
        return value


class GameLoveSerializer(serializers.ModelSerializer):
    user_email = serializers.CharField(source='user.email', read_only=True)
    game_title = serializers.CharField(source='game.title', read_only=True)

    class Meta:
        model = GameLove
        fields = ['id', 'user', 'user_email', 'game', 'game_title', 'loved_at']
        read_only_fields = ['id', 'user', 'loved_at']


class AppSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppSettings
        fields = ['app_version', 'app_link', 'under_maintenance', 'show_popup', 'popup_title', 'popup_description', 'popup_link']
