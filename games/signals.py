from django.db.models.signals import post_save, post_delete, m2m_changed
from django.dispatch import receiver
from django.core.cache import cache
from .models import Game, Emulator, GameRating, GameReview, GameLove
import hashlib


def make_cache_key(view_name, *args, **kwargs):
    """Generate cache key similar to Django's cache_page decorator."""
    # This mirrors how Django generates cache keys
    key_parts = [view_name]
    if args:
        key_parts.extend(str(arg) for arg in args)
    if kwargs:
        key_parts.extend(f"{k}={v}" for k, v in sorted(kwargs.items()))
    return ':'.join(key_parts)


def clear_specific_game_cache(game_id=None, emulator_id=None):
    """Clear cache for specific game or emulator-related queries."""
    try:
        from django_redis import get_redis_connection
        redis_client = get_redis_connection("default")
        
        # Build patterns to match our custom cache keys
        patterns = []
        
        # Always clear list caches when any game changes
        patterns.extend([
            "*view_cache:GameViewSet.list*",
            "*view_cache:games.views.GameViewSet*",
            "*:1:views.decorators.cache*",
        ])
        
        if game_id:
            # Clear specific game detail cache - be very aggressive
            patterns.extend([
                f"*view_cache:GameViewSet.retrieve*",
                f"*game*{game_id}*",
                f"*Game*{game_id}*",
                f"*games*{game_id}*",
                f"*{game_id}*",
                f"*view_cache:GameViewSet.reviews*{game_id}*",
                f"*view_cache:GameViewSet.ratings*{game_id}*",
            ])
        
        if emulator_id:
            # Clear caches filtered by this emulator
            patterns.extend([
                f"*view_cache:GameViewSet.list*emulator={emulator_id}*",
                f"*view_cache:GameViewSet.list*emulator_id={emulator_id}*",
                f"*emulator={emulator_id}*",
                f"*emulator_id={emulator_id}*",
            ])
        
        # Delete matching keys
        deleted_count = 0
        for pattern in patterns:
            for key in redis_client.scan_iter(match=pattern, count=1000):
                redis_client.delete(key)
                deleted_count += 1
        
        # Also clear Django's default cache for this game
        if game_id:
            cache.delete(f"game_{game_id}")
            cache.delete(f"game_detail_{game_id}")
            cache.delete(f"game_reviews_{game_id}")
        
        return deleted_count
    except Exception as e:
        # Fallback: clear entire cache
        import logging
        logger = logging.getLogger(__name__)
        logger.warning(f"Failed to clear specific cache, clearing all: {e}")
        cache.clear()
        return -1


def clear_emulator_cache(emulator_id=None):
    """Clear cache for specific emulator."""
    try:
        from django_redis import get_redis_connection
        redis_client = get_redis_connection("default")
        
        patterns = [
            "*view_cache:EmulatorViewSet.list:*",
        ]
        
        if emulator_id:
            patterns.append(f"*view_cache:EmulatorViewSet.retrieve:*")
        
        deleted_count = 0
        for pattern in patterns:
            for key in redis_client.scan_iter(pattern):
                redis_client.delete(key)
                deleted_count += 1
        
        return deleted_count
    except Exception:
        cache.clear()
        return -1


@receiver([post_save], sender=Game)
def invalidate_game_cache_on_save(sender, instance, created, update_fields, **kwargs):
    """
    Invalidate game cache when a game is created or updated.
    Skip cache clearing for minor updates like view/download counters.
    """
    # Don't clear cache for view/download increments (too frequent)
    if update_fields and set(update_fields) <= {'views', 'downloads', 'updated_at'}:
        return
    
    # Clear cache for this specific game and its emulator's game list
    clear_specific_game_cache(game_id=instance.pk, emulator_id=instance.emulator_id)


@receiver([post_delete], sender=Game)
def invalidate_game_cache_on_delete(sender, instance, **kwargs):
    """Invalidate game cache when a game is deleted."""
    clear_specific_game_cache(game_id=instance.pk, emulator_id=instance.emulator_id)


@receiver([post_save, post_delete], sender=Emulator)
def invalidate_emulator_cache(sender, instance, **kwargs):
    """
    Invalidate emulator cache when an emulator is created, updated, or deleted.
    Also clear game cache since games are filtered by emulator.
    """
    clear_emulator_cache(emulator_id=instance.pk)
    # Also clear game lists since they show emulator info
    clear_specific_game_cache(emulator_id=instance.pk)


@receiver([post_save, post_delete], sender=GameRating)
def invalidate_rating_cache(sender, instance, **kwargs):
    """
    Invalidate cache for the specific game when rating changes.
    Only clear caches related to this game.
    """
    clear_specific_game_cache(game_id=instance.game_id, emulator_id=instance.game.emulator_id)


@receiver([post_save, post_delete], sender=GameReview)
def invalidate_review_cache(sender, instance, **kwargs):
    """
    Invalidate cache for the specific game when review changes.
    """
    clear_specific_game_cache(game_id=instance.game_id, emulator_id=instance.game.emulator_id)


@receiver([post_save, post_delete], sender=GameLove)
def invalidate_love_cache(sender, instance, **kwargs):
    """
    Invalidate cache for the specific game when love changes.
    """
    clear_specific_game_cache(game_id=instance.game_id, emulator_id=instance.game.emulator_id)


@receiver(m2m_changed, sender=Game.genres.through)
def invalidate_game_genres_cache(sender, instance, **kwargs):
    """
    Invalidate cache when game genres change.
    """
    if isinstance(instance, Game):
        clear_specific_game_cache(game_id=instance.pk, emulator_id=instance.emulator_id)
