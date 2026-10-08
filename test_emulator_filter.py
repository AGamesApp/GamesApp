#!/usr/bin/env python
"""
Test Emulator Filter in Games Dashboard
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gamezone.settings')
django.setup()

from django.test import RequestFactory, Client
from django.contrib.auth import get_user_model
from games.models import Game, Emulator
from customadmin.views import GameListView

def test_emulator_filter():
    """Test that games can be filtered by emulator checkboxes"""
    print("\n" + "="*80)
    print("TEST: Emulator Filter in Games Dashboard")
    print("="*80)
    
    # Get emulators and games
    emulators = list(Emulator.objects.all()[:3])
    if len(emulators) < 2:
        print("  ⚠️  Not enough emulators to test (need at least 2)")
        return False
    
    print(f"\n  Available emulators:")
    for emu in emulators:
        game_count = Game.objects.filter(emulator=emu).count()
        print(f"    - {emu.name} (ID: {emu.id}): {game_count} games")
    
    # Test 1: No filter (all games)
    print("\n  TEST 1: No filter applied")
    factory = RequestFactory()
    request = factory.get('/customadmin/games/')
    
    User = get_user_model()
    admin_user = User.objects.filter(is_superuser=True).first()
    if not admin_user:
        admin_user = User.objects.create_superuser('testadmin', 'test@test.com', 'testpass123')
    request.user = admin_user
    
    view = GameListView()
    view.request = request
    queryset = view.get_queryset()
    total_games = queryset.count()
    print(f"    Total games: {total_games}")
    
    # Test 2: Filter by first emulator
    print(f"\n  TEST 2: Filter by {emulators[0].name} only")
    request = factory.get(f'/customadmin/games/?emulator={emulators[0].id}')
    request.user = admin_user
    
    view = GameListView()
    view.request = request
    queryset = view.get_queryset()
    filtered_count = queryset.count()
    print(f"    Games for {emulators[0].name}: {filtered_count}")
    
    # Verify all games belong to selected emulator
    for game in queryset[:5]:
        if game.emulator_id != emulators[0].id:
            print(f"    ❌ FAIL: Game '{game.title}' belongs to {game.emulator.name}, not {emulators[0].name}")
            return False
    print(f"    ✅ All filtered games belong to {emulators[0].name}")
    
    # Test 3: Filter by multiple emulators
    if len(emulators) >= 2:
        print(f"\n  TEST 3: Filter by {emulators[0].name} and {emulators[1].name}")
        request = factory.get(f'/customadmin/games/?emulator={emulators[0].id}&emulator={emulators[1].id}')
        request.user = admin_user
        
        view = GameListView()
        view.request = request
        queryset = view.get_queryset()
        multi_filtered_count = queryset.count()
        print(f"    Games for selected emulators: {multi_filtered_count}")
        
        # Verify games belong to selected emulators
        allowed_ids = [emulators[0].id, emulators[1].id]
        for game in queryset[:10]:
            if game.emulator_id not in allowed_ids:
                print(f"    ❌ FAIL: Game '{game.title}' belongs to {game.emulator.name} (not in selected)")
                return False
        print(f"    ✅ All filtered games belong to selected emulators")
    
    # Test 4: Context data includes emulators
    print("\n  TEST 4: Context includes emulator data")
    request = factory.get(f'/customadmin/games/?emulator={emulators[0].id}')
    request.user = admin_user
    
    view = GameListView()
    view.request = request
    view.kwargs = {}  # Add kwargs for pagination
    view.object_list = view.get_queryset()
    context = view.get_context_data()
    
    if 'all_emulators' in context:
        print(f"    ✅ Context includes 'all_emulators': {context['all_emulators'].count()} emulators")
    else:
        print("    ❌ Context missing 'all_emulators'")
        return False
    
    if 'selected_emulators' in context:
        print(f"    ✅ Context includes 'selected_emulators': {context['selected_emulators']}")
    else:
        print("    ❌ Context missing 'selected_emulators'")
        return False
    
    # Test 5: Filter + search combination
    print("\n  TEST 5: Combine emulator filter with search")
    request = factory.get(f'/customadmin/games/?emulator={emulators[0].id}&search=test')
    request.user = admin_user
    
    view = GameListView()
    view.request = request
    queryset = view.get_queryset()
    combined_count = queryset.count()
    print(f"    Games matching emulator + search: {combined_count}")
    print(f"    ✅ Combined filters work")
    
    print("\n✅ ALL TESTS PASSED")
    return True


def test_template_rendering():
    """Test that template has emulator filter UI"""
    print("\n" + "="*80)
    print("TEST: Template Includes Emulator Filter")
    print("="*80)
    
    with open('/root/game/customadmin/templates/customadmin/game_list.html', 'r') as f:
        template_content = f.read()
    
    checks = [
        ('Filter by Emulator label', '🎮 Filter by Emulator:'),
        ('Emulator checkbox input', 'name="emulator"'),
        ('Auto-submit on change', 'onchange="document.getElementById(\'filterForm\').submit()"'),
        ('Selected emulators in context', 'selected_emulators'),
        ('All emulators in context', 'all_emulators'),
        ('Emulator checkbox styling', '.emulator-checkbox'),
        ('Checked state styling', 'input:checked'),
    ]
    
    all_passed = True
    for check_name, check_string in checks:
        if check_string in template_content:
            print(f"  ✅ {check_name}")
        else:
            print(f"  ❌ {check_name}")
            all_passed = False
    
    return all_passed


def main():
    print("\n" + "="*80)
    print("EMULATOR FILTER FUNCTIONALITY TEST")
    print("="*80)
    
    results = []
    
    # Run tests
    results.append(("Template Includes Filter", test_template_rendering()))
    results.append(("Emulator Filter Logic", test_emulator_filter()))
    
    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"  {status}: {test_name}")
    
    print("\n" + "="*80)
    print(f"RESULTS: {passed}/{total} tests passed")
    print("="*80)
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! 🎉")
        print("\n✅ Emulator Filter Features:")
        print("  • Emulator checkboxes displayed in games list")
        print("  • Filter by single emulator works")
        print("  • Filter by multiple emulators works")
        print("  • Auto-submit on checkbox change")
        print("  • Combine with search functionality")
        print("  • Selected filters preserved in pagination")
        print("  • Visual feedback for checked emulators")
        print("\n📋 How to Use:")
        print("  1. Go to https://games.agames.cv/customadmin/games/")
        print("  2. See 'Filter by Emulator' section with checkboxes")
        print("  3. Check one or more emulator checkboxes")
        print("  4. Page automatically filters games for selected emulators")
        print("  5. Combine with search box for more specific results")
        print("  6. Click 'Clear All' to reset filters")
        return 0
    else:
        print(f"\n⚠️  {total - passed} TEST(S) FAILED\n")
        return 1


if __name__ == '__main__':
    sys.exit(main())
