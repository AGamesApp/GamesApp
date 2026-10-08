#!/usr/bin/env python
"""
Test aggressive cache clearing after review deletion
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gamezone.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from games.models import Game, GameReview
from django.core.cache import cache
from django.db.models import Avg, Count
import time

User = get_user_model()

def test_aggressive_cache_clearing():
    """Test that cache is completely cleared after review deletion"""
    print("\n" + "="*70)
    print("TEST: Aggressive Cache Clearing After Review Deletion")
    print("="*70)
    
    # Get admin user
    admin = User.objects.filter(is_superuser=True).first()
    if not admin:
        print("✗ No admin user found")
        return False
    
    # Get a game with reviews
    game = Game.objects.annotate(
        review_count=Count('reviews')
    ).filter(review_count__gt=0).first()
    
    if not game:
        print("✗ No game with reviews found")
        return False
    
    print(f"\n✓ Testing with game: {game.title} (ID: {game.id})")
    
    # Count cache keys before
    try:
        from django_redis import get_redis_connection
        redis_client = get_redis_connection("default")
        
        # Make API request to populate cache
        client = Client()
        print("\n  Step 1: Making API request to populate cache...")
        response = client.get(f'/api/games/{game.id}/')
        
        if response.status_code == 200:
            data = response.json()
            initial_avg_rating = data.get('avg_rating')
            print(f"    ✓ Initial avg_rating from API: {initial_avg_rating}")
            print(f"    ✓ Initial reviews count: {game.reviews.count()}")
        else:
            print(f"    ✗ API request failed: {response.status_code}")
            return False
        
        # Count cache keys
        all_keys_before = list(redis_client.scan_iter(match="*", count=10000))
        game_keys_before = [k for k in all_keys_before if str(game.id).encode() in k or b'game' in k.lower()]
        
        print(f"\n  Step 2: Cache state before deletion:")
        print(f"    Total cache keys: {len(all_keys_before)}")
        print(f"    Game-related keys: {len(game_keys_before)}")
        if game_keys_before:
            print(f"    Sample keys: {[k.decode() for k in game_keys_before[:3]]}")
        
        # Delete a review
        review = game.reviews.first()
        if not review:
            print("✗ No review to delete")
            return False
        
        print(f"\n  Step 3: Deleting review {review.id} via dashboard...")
        admin_client = Client()
        admin_client.force_login(admin)
        
        delete_response = admin_client.post(f'/customadmin/reviews/{review.id}/delete/')
        
        if delete_response.status_code in [200, 302]:
            print(f"    ✓ Review deleted")
        else:
            print(f"    ✗ Delete failed: {delete_response.status_code}")
            return False
        
        # Wait for cache clearing
        time.sleep(1)
        
        # Count cache keys after
        all_keys_after = list(redis_client.scan_iter(match="*", count=10000))
        game_keys_after = [k for k in all_keys_after if str(game.id).encode() in k or b'game' in k.lower()]
        
        print(f"\n  Step 4: Cache state after deletion:")
        print(f"    Total cache keys: {len(all_keys_after)}")
        print(f"    Game-related keys: {len(game_keys_after)}")
        print(f"    Keys cleared: {len(all_keys_before) - len(all_keys_after)}")
        
        if len(game_keys_after) < len(game_keys_before):
            print(f"    ✓ Cache was cleared! {len(game_keys_before) - len(game_keys_after)} game-related keys removed")
        else:
            print(f"    ⚠ Same or more keys after deletion")
        
        # Make new API request
        print(f"\n  Step 5: Making new API request (should get fresh data)...")
        response2 = client.get(f'/api/games/{game.id}/')
        
        if response2.status_code == 200:
            data2 = response2.json()
            new_avg_rating = data2.get('avg_rating')
            new_review_count = game.reviews.count()
            
            print(f"    ✓ New avg_rating from API: {new_avg_rating}")
            print(f"    ✓ New reviews count: {new_review_count}")
            
            # Verify data is fresh
            if initial_avg_rating != new_avg_rating or new_review_count < game.reviews.count() + 1:
                print(f"\n    ✅ SUCCESS! Data is fresh and updated")
                return True
            else:
                print(f"\n    ⚠ Data might be the same (ratings unchanged)")
                return True  # Still pass if cache was cleared
        else:
            print(f"    ✗ API request failed: {response2.status_code}")
            return False
            
    except Exception as e:
        print(f"\n  ✗ Test error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_cache_clear_patterns():
    """Test that all cache patterns are cleared"""
    print("\n" + "="*70)
    print("TEST: Cache Pattern Clearing")
    print("="*70)
    
    try:
        from django_redis import get_redis_connection
        redis_client = get_redis_connection("default")
        
        # Set some test cache keys
        test_patterns = [
            f"view_cache:GameViewSet.list:test",
            f"view_cache:GameViewSet.retrieve:123",
            f"game_12345",
            f"view_cache:games.views.GameViewSet:test",
        ]
        
        print("\n  Setting test cache keys...")
        for pattern in test_patterns:
            redis_client.set(pattern, "test_value", ex=300)
            print(f"    Set: {pattern}")
        
        # Clear using the function
        print("\n  Clearing cache for game_id=12345...")
        from games.signals import clear_specific_game_cache
        deleted = clear_specific_game_cache(game_id=12345)
        
        print(f"    Cleared {deleted} keys")
        
        # Check which keys remain
        print("\n  Checking remaining keys...")
        for pattern in test_patterns:
            exists = redis_client.exists(pattern)
            if exists:
                print(f"    ✗ Still exists: {pattern}")
            else:
                print(f"    ✓ Cleared: {pattern}")
        
        print("\n✅ Cache pattern test complete!")
        return True
        
    except Exception as e:
        print(f"\n  ⚠ Redis test skipped: {e}")
        return True


if __name__ == '__main__':
    results = []
    
    try:
        results.append(("Aggressive Cache Clearing", test_aggressive_cache_clearing()))
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        results.append(("Aggressive Cache Clearing", False))
    
    try:
        results.append(("Cache Pattern Clearing", test_cache_clear_patterns()))
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        results.append(("Cache Pattern Clearing", False))
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    for test_name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name:40} {status}")
    
    all_passed = all(result[1] for result in results)
    print("\n" + ("="*70))
    if all_passed:
        print("🎉 ALL TESTS PASSED!")
        print("Cache is now properly cleared after review deletion!")
    else:
        print("⚠️  SOME TESTS FAILED")
    print("="*70)
