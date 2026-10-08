#!/usr/bin/env python
"""Clean up orphaned ratings - ratings that exist without corresponding reviews."""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gamezone.settings')
django.setup()

from games.models import Game, GameReview, GameRating
from django.core.cache import cache
from games.signals import clear_specific_game_cache

def cleanup_orphaned_ratings():
    """Find and delete ratings that don't have corresponding reviews."""
    print("="*60)
    print("CLEANUP: Orphaned Ratings")
    print("="*60)
    
    orphaned_count = 0
    affected_games = set()
    
    # Get all ratings
    all_ratings = GameRating.objects.select_related('game', 'user').all()
    total_ratings = all_ratings.count()
    
    print(f"\n📊 Total ratings in database: {total_ratings}")
    print(f"\n🔍 Scanning for orphaned ratings...\n")
    
    for rating in all_ratings:
        # Check if there's a corresponding review
        has_review = GameReview.objects.filter(
            user=rating.user,
            game=rating.game
        ).exists()
        
        if not has_review:
            orphaned_count += 1
            affected_games.add(rating.game.id)
            
            print(f"   ❌ Orphan found:")
            print(f"      Game: {rating.game.title}")
            print(f"      User: {rating.user.email}")
            print(f"      Score: {rating.score}")
            print(f"      Deleting...")
            
            # Delete the orphaned rating
            rating.delete()
            print(f"      ✅ Deleted\n")
    
    print("="*60)
    print(f"✅ Cleanup complete!")
    print(f"   • Deleted {orphaned_count} orphaned ratings")
    print(f"   • Affected {len(affected_games)} games")
    print("="*60)
    
    # Clear cache for affected games
    if affected_games:
        print(f"\n🧹 Clearing cache for affected games...")
        total_cleared = 0
        for game_id in affected_games:
            try:
                game = Game.objects.get(id=game_id)
                deleted_keys = clear_specific_game_cache(
                    game_id=game_id, 
                    emulator_id=game.emulator_id
                )
                total_cleared += deleted_keys if deleted_keys else 0
                print(f"   Game {game_id}: {game.title}")
                print(f"      New average: {game.average_rating}")
            except Game.DoesNotExist:
                pass
        
        print(f"\n✅ Cleared {total_cleared} cache keys")
        print("="*60)


if __name__ == '__main__':
    cleanup_orphaned_ratings()
