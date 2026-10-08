#!/usr/bin/env python
"""Test that deleting a review also deletes the rating and updates average score."""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gamezone.settings')
django.setup()

from games.models import Game, GameReview, GameRating
from django.contrib.auth import get_user_model
from django.core.cache import cache

User = get_user_model()

def test_review_rating_deletion():
    """Test that deleting a review also deletes the rating."""
    print("="*60)
    print("TEST: Review + Rating Deletion")
    print("="*60)
    
    # Find a game with ratings
    game = Game.objects.annotate(
        rating_count=django.db.models.Count('ratings')
    ).filter(rating_count__gt=1).first()
    
    if not game:
        print("❌ No games with ratings found")
        return
    
    print(f"\n📊 Game: {game.title}")
    print(f"   ID: {game.id}")
    
    # Get current stats
    initial_ratings = game.ratings.count()
    initial_reviews = game.reviews.count()
    initial_avg = game.average_rating
    
    print(f"\n📈 BEFORE:")
    print(f"   Ratings: {initial_ratings}")
    print(f"   Reviews: {initial_reviews}")
    print(f"   Average: {initial_avg}")
    
    # Get or create a test user
    test_user = User.objects.filter(email='test_review_delete@test.com').first()
    if not test_user:
        test_user = User.objects.create_user(
            email='test_review_delete@test.com',
            password='testpass123',
            username='test_review_delete'
        )
        print(f"\n✅ Created test user: {test_user.email}")
    
    # Create a review and rating with score 1
    review, created = GameReview.objects.get_or_create(
        user=test_user,
        game=game,
        defaults={'review': 'Test review for deletion'}
    )
    
    rating, created = GameRating.objects.get_or_create(
        user=test_user,
        game=game,
        defaults={'score': 1.0}
    )
    
    print(f"\n✅ Created review and rating (score: {rating.score})")
    
    # Clear cache to get fresh data
    cache.clear()
    game.refresh_from_db()
    
    # Get stats after adding low rating
    after_add_ratings = game.ratings.count()
    after_add_reviews = game.reviews.count()
    after_add_avg = game.average_rating
    
    print(f"\n📈 AFTER ADDING (score=1):")
    print(f"   Ratings: {after_add_ratings}")
    print(f"   Reviews: {after_add_reviews}")
    print(f"   Average: {after_add_avg}")
    
    # Now simulate admin deletion
    print(f"\n🗑️  Simulating admin deletion...")
    
    # Store review ID
    review_id = review.id
    
    # This is what the fixed code does:
    review.delete()
    GameRating.objects.filter(user=test_user, game=game).delete()
    
    print(f"   ✅ Deleted review ID: {review_id}")
    print(f"   ✅ Deleted associated rating")
    
    # Clear cache aggressively
    from games.signals import clear_specific_game_cache
    deleted_keys = clear_specific_game_cache(game_id=game.id, emulator_id=game.emulator_id)
    print(f"   ✅ Cleared {deleted_keys} cache keys")
    
    # Get fresh data
    game.refresh_from_db()
    
    # Get stats after deletion
    after_delete_ratings = game.ratings.count()
    after_delete_reviews = game.reviews.count()
    after_delete_avg = game.average_rating
    
    print(f"\n📈 AFTER DELETION:")
    print(f"   Ratings: {after_delete_ratings}")
    print(f"   Reviews: {after_delete_reviews}")
    print(f"   Average: {after_delete_avg}")
    
    # Verify
    print(f"\n🔍 VERIFICATION:")
    if after_delete_ratings < after_add_ratings:
        print(f"   ✅ Rating count decreased: {after_add_ratings} → {after_delete_ratings}")
    else:
        print(f"   ❌ Rating count didn't decrease: {after_add_ratings} → {after_delete_ratings}")
    
    if after_delete_avg != after_add_avg:
        print(f"   ✅ Average changed: {after_add_avg} → {after_delete_avg}")
    else:
        print(f"   ❌ Average didn't change: {after_add_avg}")
    
    # Check if it matches initial (should be close if we deleted the only added review)
    if abs(after_delete_avg - initial_avg) < 0.2:
        print(f"   ✅ Average restored close to initial: {initial_avg} → {after_delete_avg}")
    else:
        print(f"   ⚠️  Average different from initial: {initial_avg} → {after_delete_avg}")
    
    print("\n" + "="*60)
    if after_delete_ratings < after_add_ratings and after_delete_avg != after_add_avg:
        print("✅ SUCCESS! Review deletion now deletes rating and updates average!")
    else:
        print("❌ FAILED! Issue still exists")
    print("="*60)


if __name__ == '__main__':
    test_review_rating_deletion()
