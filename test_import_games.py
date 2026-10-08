"""
Test the import_games.py script functionality
"""
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gamezone.settings')
django.setup()

from games.models import Game, Emulator, Genre, GameImage
from import_games import safe_str, safe_int, safe_bool
import pandas as pd

def test_safe_functions():
    """Test the safe conversion functions"""
    print("Testing safe conversion functions...")
    
    # Test safe_str
    assert safe_str("hello") == "hello"
    assert safe_str(None) == ""
    assert safe_str(pd.NA) == ""
    assert safe_str(123) == "123"
    assert safe_str("  test  ") == "test"
    print("✓ safe_str works correctly")
    
    # Test safe_int
    assert safe_int(10) == 10
    assert safe_int("20") == 20
    assert safe_int(None) == 0
    assert safe_int("") == 0
    assert safe_int(pd.NA) == 0
    assert safe_int("abc") == 0
    assert safe_int("100 priority") == 100  # Extract number
    print("✓ safe_int works correctly")
    
    # Test safe_bool
    assert safe_bool(True) == True
    assert safe_bool("true") == True
    assert safe_bool("1") == True
    assert safe_bool("yes") == True
    assert safe_bool("premium") == True
    assert safe_bool(False) == False
    assert safe_bool("false") == False
    assert safe_bool("0") == False
    assert safe_bool(None) == False
    assert safe_bool("") == False
    print("✓ safe_bool works correctly")
    
    print("\n✅ All safe functions passed!\n")


def test_game_creation():
    """Test creating a game with all fields"""
    print("Testing game creation with all fields...")
    
    # Create or get emulator
    emulator, _ = Emulator.objects.get_or_create(
        name="Test Emulator",
        defaults={'priority': 10}
    )
    
    # Create game with all fields
    game, created = Game.objects.update_or_create(
        title="Test Game Import",
        emulator=emulator,
        defaults={
            'priority': 100,
            'description': 'Test description',
            'image_url': 'https://example.com/image.jpg',
            'size': '500 MB',
            'download_url': 'https://example.com/download',
            'game_url': 'https://example.com/game',
            'video_url': 'https://example.com/video',
            'region': 'USA',
            'is_premium': True,
            'year': '2025',
        }
    )
    
    print(f"Game created: {game.title}")
    print(f"  Priority: {game.priority}")
    print(f"  Description: {game.description}")
    print(f"  Is Premium: {game.is_premium}")
    print(f"  Year: {game.year}")
    
    # Add genres
    action, _ = Genre.objects.get_or_create(name="Action")
    rpg, _ = Genre.objects.get_or_create(name="RPG")
    game.genres.set([action, rpg])
    
    print(f"  Genres: {', '.join([g.name for g in game.genres.all()])}")
    
    # Add images
    for i in range(1, 4):
        GameImage.objects.update_or_create(
            game=game,
            image_path=f"https://example.com/image{i}.jpg",
            defaults={'order': i}
        )
    
    image_count = game.images.count()
    print(f"  Images: {image_count}")
    
    assert game.priority == 100
    assert game.is_premium == True
    assert game.genres.count() == 2
    assert game.images.count() == 3
    
    print("\n✅ Game creation test passed!\n")
    
    # Cleanup
    game.delete()
    if emulator.games.count() == 0:
        emulator.delete()


def test_empty_values():
    """Test that empty values are handled correctly"""
    print("Testing empty value handling...")
    
    # Create emulator
    emulator, _ = Emulator.objects.get_or_create(
        name="Test Empty Values",
        defaults={'priority': 0}
    )
    
    # Create game with minimal data
    game, created = Game.objects.update_or_create(
        title="Minimal Test Game",
        emulator=emulator,
        defaults={
            'priority': 0,
            'description': '',
            'image_url': '',
            'size': '',
            'download_url': '',
            'game_url': '',
            'video_url': '',
            'region': '',
            'is_premium': False,
            'year': '',
        }
    )
    
    print(f"Game created with empty values: {game.title}")
    assert game.priority == 0
    assert game.description == ''
    assert game.is_premium == False
    
    print("✅ Empty value test passed!\n")
    
    # Cleanup
    game.delete()
    if emulator.games.count() == 0:
        emulator.delete()


def show_column_list():
    """Display the column list for Excel"""
    print("\n" + "="*60)
    print("📋 EXCEL/GOOGLE SHEETS COLUMN NAMES")
    print("="*60)
    print("\n✅ REQUIRED (must have these):")
    print("  1. game_name")
    print("  2. console")
    print("\n⭐ OPTIONAL (can be empty - will use defaults):")
    print("  3. priority")
    print("  4. description")
    print("  5. image_url")
    print("  6. image_1")
    print("  7. image_2")
    print("  8. image_3")
    print("  9. image_4")
    print("  10. image_5")
    print("  11. size")
    print("  12. download_url")
    print("  13. game_url")
    print("  14. video_url")
    print("  15. region")
    print("  16. genres")
    print("  17. is_premium")
    print("  18. year")
    print("\n💡 Example Excel Header Row:")
    print("  game_name | console | priority | description | image_url | image_1 | image_2 | image_3 | image_4 | image_5 | size | download_url | game_url | video_url | region | genres | is_premium | year")
    print("\n💡 Minimal Excel (only required):")
    print("  game_name | console")
    print("\n💡 Example Data Row:")
    print("  Super Mario Bros | NES | 100 | Classic platformer | https://... | https://img1 | https://img2 | | | | 500 KB | https://... | https://... | https://... | USA | Action, Platform | true | 1985")
    print("="*60)


if __name__ == "__main__":
    print("\n" + "="*60)
    print("🧪 Testing Import Games Script")
    print("="*60 + "\n")
    
    try:
        test_safe_functions()
        test_game_creation()
        test_empty_values()
        
        print("="*60)
        print("✅ ALL TESTS PASSED!")
        print("="*60)
        
        show_column_list()
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {str(e)}")
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
