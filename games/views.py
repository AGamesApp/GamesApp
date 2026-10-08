from rest_framework import viewsets, status, permissions, filters
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.pagination import PageNumberPagination
from django.db.models import Count, Avg, Q, Value, IntegerField, Case, When, F, Subquery, OuterRef, FloatField
from django.db.models.functions import Length, Coalesce
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_cookie, vary_on_headers
from django.utils.decorators import method_decorator
from django.core.cache import cache
from .models import Emulator, Game, GameRating, GameReview, GameLove, AppSettings
from .serializers import (
    EmulatorSerializer,
    GameListSerializer,
    GameDetailSerializer,
    GameRatingSerializer,
    GameReviewSerializer,
    AppSettingsSerializer,
)
from django.shortcuts import get_object_or_404
from functools import wraps


# ----------------------------
# Custom Permissions
# ----------------------------

class ReadOnlyOrAdminPermission(permissions.BasePermission):
    """
    Custom permission: Allow read-only for everyone, but only admins can create/update/delete.
    Protects games, emulators, and appsettings from being modified by regular users.
    """
    def has_permission(self, request, view):
        # Allow all read operations (GET, HEAD, OPTIONS)
        if request.method in permissions.SAFE_METHODS:
            return True
        # Only allow write operations (POST, PUT, PATCH, DELETE) for admin users
        return request.user and request.user.is_authenticated and request.user.is_staff


class IsPremiumUser(permissions.BasePermission):
    """
    Object-level permission: grants access to a game only when:
      - The game is NOT premium  → always allow
      - The game IS premium:
          * User must be authenticated  → else 401
          * User must have is_premium=True  → else 403
    Used in game list (filters queryset) and retrieve (blocks detail view).
    """
    message = 'A premium subscription is required to access this game.'

    def has_object_permission(self, request, view, obj):
        if not obj.is_premium:
            return True
        if not request.user or not request.user.is_authenticated:
            return False
        return bool(getattr(request.user, 'is_premium', False))

# Custom cache decorator that varies by authentication
def cache_for_anonymous_only(timeout):
    """Cache only for anonymous users, skip caching for authenticated users."""
    def decorator(func):
        @wraps(func)
        def wrapper(self, request, *args, **kwargs):
            # Don't cache for authenticated users
            if request.user.is_authenticated:
                return func(self, request, *args, **kwargs)
            
            # Build cache key based on view, method, and query params
            view_name = f"{self.__class__.__name__}.{func.__name__}"
            query_string = request.META.get('QUERY_STRING', '')
            cache_key = f"view_cache:{view_name}:{query_string}"
            
            # Try to get from cache
            cached_data = cache.get(cache_key)
            if cached_data is not None:
                # Return cached response data
                return Response(cached_data)
            
            # Execute view and cache the response data
            response = func(self, request, *args, **kwargs)
            
            # Only cache successful responses
            if hasattr(response, 'status_code') and response.status_code == 200:
                # Cache the data, not the Response object
                if hasattr(response, 'data'):
                    cache.set(cache_key, response.data, timeout)
            
            return response
        return wrapper
    return decorator

# ----------------------------
# Pagination Classes
# ----------------------------

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 50


# ----------------------------
# Emulator CRUD
# ----------------------------

class EmulatorViewSet(viewsets.ReadOnlyModelViewSet):
    """
    List all emulators (read-only for all users).
    Only admins can create/update/delete emulators via the admin dashboard.
    """
    queryset = Emulator.objects.all().order_by('-priority', 'name')
    serializer_class = EmulatorSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['name', 'created_at', 'priority']

    @cache_for_anonymous_only(60 * 10)  # Cache for 10 minutes (anonymous only)
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @cache_for_anonymous_only(60 * 10)  # Cache for 10 minutes (anonymous only)
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)


# ----------------------------
# Game CRUD
# ----------------------------

class GameViewSet(viewsets.ModelViewSet):
    """
    List games for a specific emulator (with pagination/infinite scroll).
    Show title, image, average rating, total loves, views.
    Advanced search with subsequence matching and relevance ranking.
    
    Permissions: Read-only for all users, write operations require admin privileges.
    """
    serializer_class = GameListSerializer
    permission_classes = [ReadOnlyOrAdminPermission]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    pagination_class = StandardResultsSetPagination
    ordering_fields = ['title', 'created_at', 'year', 'views', 'downloads']
    filterset_fields = ['is_premium', 'emulator', 'genres']

    def get_queryset(self):
        """Filter games by emulator with optimized query and advanced search.
        Premium games are hidden from non-premium / anonymous users.
        """
        emulator_id = self.request.query_params.get('emulator')
        search_query = self.request.query_params.get('search', '').strip()

        # Base queryset with optimizations
        queryset = Game.objects.select_related('emulator').prefetch_related('genres')

        # ── Premium gate: premium games appear in lists for everyone,
        # but the detail endpoint (retrieve) blocks non-premium users with 401.

        # Apply emulator filter EARLY (before annotations) to reduce dataset
        if emulator_id:
            queryset = queryset.filter(emulator_id=emulator_id)
        
        # Efficient Subquery annotations (avoid expensive JOINs)
        love_subquery = Subquery(
            GameLove.objects.filter(game=OuterRef('pk')).order_by().values('game').annotate(c=Count('id')).values('c')[:1],
            output_field=IntegerField()
        )
        rating_subquery = Subquery(
            GameRating.objects.filter(game=OuterRef('pk')).order_by().values('game').annotate(a=Avg('score')).values('a')[:1],
            output_field=FloatField()
        )
        
        # For list view, add annotations
        if self.action == 'list':
            queryset = queryset.annotate(
                love_count=Coalesce(love_subquery, Value(0)),
                avg_rating=rating_subquery
            )
        # For detail view, add images and all related data
        elif self.action == 'retrieve':
            queryset = queryset.prefetch_related('images').annotate(
                love_count=Coalesce(love_subquery, Value(0)),
                avg_rating=rating_subquery
            )
        
        # Apply search with ranking if search query provided
        if search_query:
            search_terms = search_query.lower().split()
            
            # Simple matching - no regex (regex causes full table scans)
            q_exact_title = Q(title__iexact=search_query)
            q_startswith_title = Q(title__istartswith=search_query)
            q_contains_title = Q(title__icontains=search_query)
            q_genre_exact = Q(genres__name__iexact=search_query)
            q_genre_contains = Q(genres__name__icontains=search_query)
            q_region_contains = Q(region__icontains=search_query)
            
            # Word-based matching for multiple words (no regex)
            q_word_match = Q()
            for term in search_terms:
                q_word_match |= Q(title__icontains=term) | Q(genres__name__icontains=term) | Q(region__icontains=term)
            
            # Combine matching conditions (no regex patterns)
            queryset = queryset.filter(
                q_exact_title | q_startswith_title | q_contains_title | 
                q_genre_exact | q_genre_contains | q_region_contains | 
                q_word_match
            ).distinct()
            
            # Add ranking/priority score
            queryset = queryset.annotate(
                search_rank=Case(
                    When(title__iexact=search_query, then=Value(100)),
                    When(title__istartswith=search_query, then=Value(90)),
                    When(genres__name__iexact=search_query, then=Value(80)),
                    When(title__icontains=search_query, then=Value(70)),
                    When(genres__name__icontains=search_query, then=Value(60)),
                    When(region__icontains=search_query, then=Value(55)),
                    default=Value(50),
                    output_field=IntegerField()
                )
            )
            
            queryset = queryset.order_by('-priority', '-search_rank', '-views', '-downloads', '-created_at')
        else:
            queryset = queryset.order_by('-priority', '-views', '-downloads', '-created_at')
        
        
        return queryset

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return GameDetailSerializer
        return GameListSerializer

    @cache_for_anonymous_only(60 * 10)  # Cache for 10 minutes (anonymous only)
    def list(self, request, *args, **kwargs):
        """List games. Premium games are hidden from non-premium / anonymous users."""
        return super().list(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        """Game detail — premium games require authentication + premium status."""
        instance = self.get_object()

        # ── Premium gate ──────────────────────────────────────────────────────
        if instance.is_premium:
            if not request.user.is_authenticated:
                return Response(
                    {'detail': 'Authentication required to access premium content.',
                     'code': 'not_authenticated'},
                    status=status.HTTP_401_UNAUTHORIZED,
                )
            if not getattr(request.user, 'is_premium', False):
                return Response(
                    {'detail': 'A premium subscription is required to access this game.',
                     'code': 'premium_required'},
                    status=status.HTTP_401_UNAUTHORIZED,
                )

        # Increment views atomically
        Game.objects.filter(pk=instance.pk).update(views=F('views') + 1)

        # Cache detail for anonymous users (non-premium games only reach here for anon)
        if not request.user.is_authenticated:
            cache_key = f"game_detail:{instance.pk}"
            cached_data = cache.get(cache_key)
            if cached_data is not None:
                return Response(cached_data)
            serializer = self.get_serializer(instance)
            cache.set(cache_key, serializer.data, 60 * 3)
            return Response(serializer.data)

        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    # ----------------------------
    # Custom Actions
    # ----------------------------

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def download(self, request, pk=None):
        """Increment download counter and return download URL."""
        game = self.get_object()
        user = request.user

        # Check premium access
        if game.is_premium and not getattr(user, 'is_premium', False):
            return Response({'error': 'Premium subscription required'}, status=status.HTTP_403_FORBIDDEN)

        # Increment download counter
        game.increment_downloads()

        return Response({
            'message': 'Download started',
            'download_url': game.download_url,
            'downloads': game.downloads
        }, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def love(self, request, pk=None):
        """Authenticated users can love/unlove a game (toggle)."""
        game = self.get_object()
        user = request.user

        love_obj = GameLove.objects.filter(user=user, game=game).first()
        if love_obj:
            love_obj.delete()
            return Response({
                'message': 'Game removed from loved games',
                'is_loved': False
            }, status=status.HTTP_200_OK)
        else:
            GameLove.objects.create(user=user, game=game)
            return Response({
                'message': 'Game added to loved games',
                'is_loved': True
            }, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def my_loved_games(self, request):
        """Return all games loved by the authenticated user."""
        user = request.user
        
        # Get loved games with optimized annotations and ordering
        loved_game_ids = GameLove.objects.filter(user=user).values_list('game_id', flat=True)
        love_sub = Subquery(
            GameLove.objects.filter(game=OuterRef('pk')).order_by().values('game').annotate(c=Count('id')).values('c')[:1],
            output_field=IntegerField()
        )
        rating_sub = Subquery(
            GameRating.objects.filter(game=OuterRef('pk')).order_by().values('game').annotate(a=Avg('score')).values('a')[:1],
            output_field=FloatField()
        )
        games = Game.objects.filter(id__in=loved_game_ids).select_related('emulator').prefetch_related('genres').annotate(
            love_count=Coalesce(love_sub, Value(0)),
            avg_rating=rating_sub
        ).order_by('-id')  # Order by ID descending to avoid pagination warning
        
        # Filter by emulator if provided
        emulator_id = request.query_params.get('emulator')
        if emulator_id:
            games = games.filter(emulator_id=emulator_id)
        
        paginator = StandardResultsSetPagination()
        page = paginator.paginate_queryset(games, request)
        serializer = GameListSerializer(page, many=True)
        
        return paginator.get_paginated_response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def rate(self, request, pk=None):
        """Authenticated users can rate a game (only one score per user per game)."""
        game = self.get_object()
        user = request.user
        score = request.data.get('score')

        if not score:
            return Response({'error': 'Score is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            score = float(score)
            if score < 1 or score > 5:
                return Response({'error': 'Score must be between 1 and 5'}, status=status.HTTP_400_BAD_REQUEST)
            if score % 0.5 != 0:
                return Response({'error': 'Score must be in 0.5 increments (e.g., 1.0, 1.5, 2.0)'}, status=status.HTTP_400_BAD_REQUEST)
        except (ValueError, TypeError):
            return Response({'error': 'Score must be a valid number'}, status=status.HTTP_400_BAD_REQUEST)

        rating, created = GameRating.objects.update_or_create(
            user=user, game=game,
            defaults={'score': score}
        )
        serializer = GameRatingSerializer(rating)
        message = 'Rating created successfully' if created else 'Rating updated successfully'
        return Response({
            'message': message,
            'rating': serializer.data
        }, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)

    @action(detail=True, methods=['get'])
    def ratings(self, request, pk=None):
        """Paginated ratings for a specific game."""
        game = self.get_object()
        ratings = game.ratings.select_related('user', 'game').all()
        paginator = StandardResultsSetPagination()
        page = paginator.paginate_queryset(ratings, request)
        serializer = GameRatingSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    # ----------------------------
    # Reviews
    # ----------------------------

    @action(detail=True, methods=['post', 'put'], permission_classes=[permissions.IsAuthenticated])
    def review(self, request, pk=None):
        """
        Create or update a review and rating for a game.
        User can only have one review per game.
        POST/PUT with: review (optional), score (optional)
        At least one field (review or score) must be provided.
        Returns: review, score, profile_picture, username, comment_date
        """
        game = self.get_object()
        user = request.user
        review_text = request.data.get('review')
        score = request.data.get('score')

        # At least one field must be provided
        if not review_text and score is None:
            return Response({'error': 'At least review text or score must be provided'}, status=status.HTTP_400_BAD_REQUEST)

        # Validate score if provided
        if score is not None:
            try:
                score = float(score)
                if not 1 <= score <= 5:
                    return Response({'error': 'Score must be between 1 and 5'}, status=status.HTTP_400_BAD_REQUEST)
                if score % 0.5 != 0:
                    return Response({'error': 'Score must be in 0.5 increments (e.g., 1.0, 1.5, 2.0)'}, status=status.HTTP_400_BAD_REQUEST)
            except (ValueError, TypeError):
                return Response({'error': 'Invalid score format'}, status=status.HTTP_400_BAD_REQUEST)

        # Get or create/update the review object
        defaults = {}
        if review_text is not None:
            defaults['review'] = review_text.strip()
        
        # Get existing review or create new one
        try:
            review_obj = GameReview.objects.get(user=user, game=game)
            # Update only if review text provided
            if review_text is not None:
                review_obj.review = review_text.strip()
                review_obj.save()
            created = False
        except GameReview.DoesNotExist:
            # Create new review (review can be empty string if only score provided)
            review_obj = GameReview.objects.create(
                user=user,
                game=game,
                review=review_text.strip() if review_text else ''
            )
            created = True

        # Handle rating if score provided
        if score is not None:
            GameRating.objects.update_or_create(
                user=user,
                game=game,
                defaults={'score': score}
            )

        # Prepare response data
        response_data = {
            'review': review_obj.review,
            'score': None,
            'profile_picture': user.profile_picture.url if user.profile_picture else None,
            'username': user.username,
            'comment_date': review_obj.updated_at
        }

        # Get the rating if exists
        try:
            rating = GameRating.objects.get(user=user, game=game)
            response_data['score'] = float(rating.score)
        except GameRating.DoesNotExist:
            pass

        message = 'Review created successfully' if created else 'Review updated successfully'
        
        return Response({
            'message': message,
            'data': response_data
        }, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)

    @action(detail=True, methods=['get'])
    def reviews(self, request, pk=None):
        """Paginated reviews for a specific game with ratings."""
        game = self.get_object()
        
        # Cache reviews for anonymous users
        cache_key = f"game_reviews:{game.pk}:{request.query_params.get('page', '1')}"
        if not request.user.is_authenticated:
            cached_data = cache.get(cache_key)
            if cached_data is not None:
                return Response(cached_data)
        
        # Optimized: prefetch ratings in bulk instead of N+1 individual queries
        reviews = game.reviews.select_related('user').all()
        user_ids = [r.user_id for r in reviews]
        ratings_map = {}
        if user_ids:
            ratings = GameRating.objects.filter(user_id__in=user_ids, game=game)
            ratings_map = {r.user_id: float(r.score) for r in ratings}
        
        reviews_data = []
        for review in reviews:
            reviews_data.append({
                'id': review.id,
                'review': review.review,
                'score': ratings_map.get(review.user_id),
                'profile_picture': review.user.profile_picture.url if review.user.profile_picture else None,
                'username': review.user.username,
                'comment_date': review.updated_at
            })
        
        paginator = StandardResultsSetPagination()
        page = paginator.paginate_queryset(reviews_data, request)
        response = paginator.get_paginated_response(page)
        
        if not request.user.is_authenticated:
            cache.set(cache_key, response.data, 60 * 5)
        
        return response

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def my_reviews(self, request):
        """Return all reviews of the authenticated user with ratings."""
        reviews = GameReview.objects.filter(user=request.user).select_related('game')
        
        # Prepare response with reviews and ratings
        reviews_data = []
        for review in reviews:
            # Get rating for this user and game
            try:
                rating = GameRating.objects.get(user=request.user, game=review.game)
                score = float(rating.score)
            except GameRating.DoesNotExist:
                score = None
            
            reviews_data.append({
                'id': review.id,
                'game_id': review.game.id,
                'game_title': review.game.title,
                'review': review.review,
                'score': score,
                'profile_picture': request.user.profile_picture.url if request.user.profile_picture else None,
                'username': request.user.username,
                'comment_date': review.updated_at
            })
        
        # Paginate
        paginator = StandardResultsSetPagination()
        page = paginator.paginate_queryset(reviews_data, request)
        return paginator.get_paginated_response(page)

    @action(detail=True, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def my_review(self, request, pk=None):
        """Get the authenticated user's review for a specific game."""
        game = self.get_object()
        
        try:
            review = GameReview.objects.get(user=request.user, game=game)
            
            # Get rating if exists
            try:
                rating = GameRating.objects.get(user=request.user, game=game)
                score = float(rating.score)
            except GameRating.DoesNotExist:
                score = None
            
            return Response({
                'id': review.id,
                'review': review.review,
                'score': score,
                'profile_picture': request.user.profile_picture.url if request.user.profile_picture else None,
                'username': request.user.username,
                'comment_date': review.updated_at
            })
        except GameReview.DoesNotExist:
            return Response({'error': 'You have not reviewed this game yet'}, status=status.HTTP_404_NOT_FOUND)


def game_redirect_view(request, game_id=None):
    """Redirect game URLs to Google Play Store."""
    from django.shortcuts import redirect
    return redirect('https://play.google.com/store/apps/details?id=com.agames.play', permanent=False)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def app_details(request):
    """Get app configuration details - cached for 10 minutes."""
    cache_key = 'app_details'
    cached_data = cache.get(cache_key)
    if cached_data is not None:
        return Response(cached_data)
    
    settings, created = AppSettings.objects.get_or_create(
        pk=1,
        defaults={
            'app_version': '1.0.0',
            'app_link': 'https://play.google.com/store/apps/details?id=com.agames.play',
            'under_maintenance': False
        }
    )
    serializer = AppSettingsSerializer(settings)
    cache.set(cache_key, serializer.data, 60 * 10)
    return Response(serializer.data)
