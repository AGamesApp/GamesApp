#!/usr/bin/env python3
"""
Quick Production Feature Test for agames
Tests major functionality without disrupting production
"""
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gamezone.settings')
django.setup()

from django.db import connection
from django.core.cache import cache
from games.models import Game, Emulator, GameReview, GameLove
from users.models import User

print("\n" + "="*60)
print("🎮 AGAMES PRODUCTION FEATURE TEST")
print("="*60 + "\n")

passed = 0
failed = 0

def test(name, func):
    global passed, failed
    try:
        result = func()
        if result:
            print(f"✅ {name}: PASS")
            passed += 1
        else:
            print(f"❌ {name}: FAIL")
            failed += 1
    except Exception as e:
        print(f"❌ {name}: ERROR - {e}")
        failed += 1

# 1. Database Connectivity
print("\n" + "-"*60)
print("1. DATABASE CONNECTIVITY")
print("-"*60)
test("PostgreSQL connection", lambda: connection.cursor() is not None)

# 2. Model Counts
print("\n" + "-"*60)
print("2. DATA INTEGRITY")
print("-"*60)
test("Games exist", lambda: Game.objects.count() > 0)
test("Emulators exist", lambda: Emulator.objects.count() > 0)
test("Users exist", lambda: User.objects.count() > 0)
test("Reviews exist", lambda: GameReview.objects.count() > 0)
print(f"\n   📊 Total Games: {Game.objects.count()}")
print(f"   📊 Total Emulators: {Emulator.objects.count()}")
print(f"   📊 Total Users: {User.objects.count()}")
print(f"   📊 Total Reviews: {GameReview.objects.count()}")
print(f"   📊 Total Loves: {GameLove.objects.count()}")

# 3. Cache System
print("\n" + "-"*60)
print("3. CACHE SYSTEM")
print("-"*60)
try:
    cache.set('test_key', 'test_value', 30)
    result = cache.get('test_key') == 'test_value'
    cache.delete('test_key')
    test("Redis cache read/write", lambda: result)
except Exception as e:
    print(f"❌ Redis cache: ERROR - {e}")
    failed += 1

# 4. Sample Data Queries
print("\n" + "-"*60)
print("4. SAMPLE DATA QUERIES")
print("-"*60)

first_game = Game.objects.first()
if first_game:
    print(f"✅ Sample game: {first_game.title}")
    print(f"   - ID: {first_game.id}")
    print(f"   - Emulator: {first_game.emulator.title if first_game.emulator else 'N/A'}")
    print(f"   - Rating: {first_game.rating if hasattr(first_game, 'rating') else 'N/A'}")
    test("Game has emulator", lambda: first_game.emulator is not None)
else:
    print("❌ No games found")
    failed += 1

first_emulator = Emulator.objects.first()
if first_emulator:
    print(f"\n✅ Sample emulator: {first_emulator.title}")
    print(f"   - ID: {first_emulator.id}")
    print(f"   - Games count: {first_emulator.games.count()}")
    test("Emulator has games", lambda: first_emulator.games.count() > 0)
else:
    print("❌ No emulators found")
    failed += 1

# 5. Review System
print("\n" + "-"*60)
print("5. REVIEW SYSTEM")
print("-"*60)

recent_review = GameReview.objects.order_by('-created_at').first()
if recent_review:
    print(f"✅ Most recent review:")
    print(f"   - Game: {recent_review.game.title}")
    print(f"   - User: {recent_review.user.username if recent_review.user else 'Anonymous'}")
    print(f"   - Rating: {recent_review.rating}/5")
    print(f"   - Date: {recent_review.created_at}")
    test("Reviews have ratings", lambda: recent_review.rating is not None)
else:
    print("ℹ️  No reviews found")

# 6. Love/Favorite System
print("\n" + "-"*60)
print("6. LOVE/FAVORITE SYSTEM")
print("-"*60)

recent_love = GameLove.objects.order_by('-created_at').first()
if recent_love:
    print(f"✅ Most recent love:")
    print(f"   - Game: {recent_love.game.title}")
    print(f"   - User: {recent_love.user.username if recent_love.user else 'Anonymous'}")
    print(f"   - Date: {recent_love.created_at}")
    test("Loves have games", lambda: recent_love.game is not None)
else:
    print("ℹ️  No loves found")

# 7. Game Search
print("\n" + "-"*60)
print("7. SEARCH FUNCTIONALITY")
print("-"*60)

search_results = Game.objects.filter(name__icontains="Super")[:5]
print(f"✅ Search for 'Super': {search_results.count()} results")
for game in search_results:
    print(f"   - {game.title}")
test("Search returns results", lambda: search_results.count() > 0)

# 8. Emulator Filtering
print("\n" + "-"*60)
print("8. EMULATOR FILTERING")
print("-"*60)

for emulator in Emulator.objects.all()[:3]:
    games_count = emulator.games.count()
    print(f"✅ {emulator.title}: {games_count} games")
    test(f"{emulator.title} has games", lambda e=emulator: e.games.count() > 0)

# Final Summary
print("\n" + "="*60)
print("📊 TEST SUMMARY")
print("="*60)
print(f"✅ Passed: {passed}")
print(f"❌ Failed: {failed}")
print(f"📈 Success Rate: {(passed/(passed+failed)*100):.1f}%")
print("="*60 + "\n")

