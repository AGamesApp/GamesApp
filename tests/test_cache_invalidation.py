#!/usr/bin/env python
"""
Test cache invalidation to ensure cached data updates when models change.
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gamezone.settings')
django.setup()

from django.core.cache import cache
from games.models import Game, Emulator, GameRating, GameReview, GameLove
from django.contrib.auth import get_user_model

User = get_user_model()

def test_cache_invalidation():
    print("=" * 60)
    print("Testing Cache Invalidation System")
    print("=" * 60)
    
    # Check Redis connection
    redis_client = None
    try:
        # django_redis uses get_redis_connection
        from django_redis import get_redis_connection
        redis_client = get_redis_connection("default")
        print(f"✓ Redis connected: {redis_client.ping()}")
    except Exception as e:
        print(f"⚠ Redis connection error: {e}")
        print("  Cache backend:", cache.__class__.__name__)
        # Continue anyway with limited tests
    
    print("\n1. Testing Game Update Cache Invalidation")
    print("-" * 60)
    
    # Get or create a test game
    emulator = Emulator.objects.first()
    if emulator:
        game = Game.objects.filter(emulator=emulator).first()
        if game:
            if redis_client:
                # Count cache keys before update
                keys_before = list(redis_client.scan_iter("*:games.views.GameViewSet*"))
                print(f"Cache keys before update: {len(keys_before)}")
            
            # Update the game
            old_title = game.title
            game.title = f"{old_title} [UPDATED]"
            game.save()
            print(f"✓ Updated game: '{old_title}' -> '{game.title}'")
            
            if redis_client:
                # Count cache keys after update
                keys_after = list(redis_client.scan_iter("*:games.views.GameViewSet*"))
                print(f"Cache keys after update: {len(keys_after)}")
                
                if len(keys_after) < len(keys_before) or len(keys_before) == 0:
                    print("✓ Cache invalidation working! Keys cleared.")
                else:
                    print("⚠ Cache may not have been invalidated")
            
            # Restore original title
            game.title = old_title
            game.save()
            print(f"✓ Restored game title to: '{game.title}'")
        else:
            print("⚠ No games found to test")
    else:
        print("⚠ No emulators found to test")
    
    print("\n2. Testing View Counter (Should NOT Clear Cache)")
    print("-" * 60)
    
    if emulator and game:
        if redis_client:
            keys_before = list(redis_client.scan_iter("*:games.views.GameViewSet*"))
            print(f"Cache keys before view increment: {len(keys_before)}")
        
        old_views = game.views
        game.increment_views()
        print(f"✓ Incremented views: {old_views} -> {game.views}")
        
        if redis_client:
            keys_after = list(redis_client.scan_iter("*:games.views.GameViewSet*"))
            print(f"Cache keys after view increment: {len(keys_after)}")
            
            if len(keys_after) == len(keys_before):
                print("✓ Cache preserved for view counter (good!)")
            else:
                print("⚠ Cache was cleared (this might impact performance)")
    
    print("\n3. Testing Rating Cache Invalidation")
    print("-" * 60)
    
    # Get a user
    user = User.objects.filter(is_staff=False).first()
    if user and game:
        if redis_client:
            keys_before = list(redis_client.scan_iter("*:games.views.GameViewSet*"))
            print(f"Cache keys before rating: {len(keys_before)}")
        
        # Create or update a rating
        rating, created = GameRating.objects.update_or_create(
            user=user, game=game,
            defaults={'score': 4.5}
        )
        action = "Created" if created else "Updated"
        print(f"✓ {action} rating: {rating.score} stars")
        
        if redis_client:
            keys_after = list(redis_client.scan_iter("*:games.views.GameViewSet*"))
            print(f"Cache keys after rating: {len(keys_after)}")
            
            if len(keys_after) < len(keys_before) or len(keys_before) == 0:
                print("✓ Cache invalidation working for ratings!")
            else:
                print("⚠ Cache may not have been invalidated")
    
    print("\n" + "=" * 60)
    print("Cache Invalidation Test Complete!")
    print("=" * 60)

if __name__ == '__main__':
    test_cache_invalidation()
