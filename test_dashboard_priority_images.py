#!/usr/bin/env python
"""
Test Priority and Image Upload in Admin Dashboard
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gamezone.settings')
django.setup()

from django.test import RequestFactory, Client
from django.contrib.auth import get_user_model
from games.models import Game, Emulator, GameImage
from customadmin.forms import GameForm, EmulatorForm, GameImageForm
from io import BytesIO
from PIL import Image

def create_test_image():
    """Create a test image file"""
    image = Image.new('RGB', (100, 100), color='red')
    image_io = BytesIO()
    image.save(image_io, format='JPEG')
    image_io.seek(0)
    return image_io

def test_priority_fields_in_forms():
    """Test that priority fields are in the forms"""
    print("\n" + "="*80)
    print("TEST 1: Priority Fields in Forms")
    print("="*80)
    
    # Test Game Form
    game_form = GameForm()
    if 'priority' in game_form.fields:
        print("  ✅ GameForm includes 'priority' field")
        widget_type = type(game_form.fields['priority'].widget).__name__
        print(f"     Widget type: {widget_type}")
    else:
        print("  ❌ GameForm missing 'priority' field")
        return False
    
    # Test Emulator Form
    emu_form = EmulatorForm()
    if 'priority' in emu_form.fields:
        print("  ✅ EmulatorForm includes 'priority' field")
        widget_type = type(emu_form.fields['priority'].widget).__name__
        print(f"     Widget type: {widget_type}")
    else:
        print("  ❌ EmulatorForm missing 'priority' field")
        return False
    
    return True


def test_image_upload_field_in_form():
    """Test that image_file field is in GameImageForm"""
    print("\n" + "="*80)
    print("TEST 2: Image Upload Field in Form")
    print("="*80)
    
    image_form = GameImageForm()
    
    if 'image_path' in image_form.fields:
        print("  ✅ GameImageForm includes 'image_path' field (URL)")
    else:
        print("  ❌ GameImageForm missing 'image_path' field")
        return False
    
    if 'image_file' in image_form.fields:
        print("  ✅ GameImageForm includes 'image_file' field (Upload)")
        widget_type = type(image_form.fields['image_file'].widget).__name__
        print(f"     Widget type: {widget_type}")
    else:
        print("  ❌ GameImageForm missing 'image_file' field")
        return False
    
    return True


def test_priority_save():
    """Test that priority can be saved"""
    print("\n" + "="*80)
    print("TEST 3: Priority Save Functionality")
    print("="*80)
    
    # Test Game priority
    test_emu, _ = Emulator.objects.get_or_create(name="TEST_PRIORITY_EMU", defaults={'priority': 0})
    
    test_game, created = Game.objects.get_or_create(
        title="TEST_PRIORITY_GAME",
        emulator=test_emu,
        defaults={'priority': 50}
    )
    
    if created or test_game.priority != 50:
        test_game.priority = 50
        test_game.save()
    
    test_game.refresh_from_db()
    
    if test_game.priority == 50:
        print(f"  ✅ Game priority saved correctly: {test_game.priority}")
    else:
        print(f"  ❌ Game priority not saved. Expected 50, got {test_game.priority}")
        return False
    
    # Test Emulator priority
    test_emu.priority = 75
    test_emu.save()
    test_emu.refresh_from_db()
    
    if test_emu.priority == 75:
        print(f"  ✅ Emulator priority saved correctly: {test_emu.priority}")
    else:
        print(f"  ❌ Emulator priority not saved. Expected 75, got {test_emu.priority}")
        return False
    
    # Cleanup
    test_game.delete()
    test_emu.delete()
    
    return True


def test_image_file_save():
    """Test that image file can be saved"""
    print("\n" + "="*80)
    print("TEST 4: Image File Upload Functionality")
    print("="*80)
    
    # Create test game
    test_emu, _ = Emulator.objects.get_or_create(name="TEST_IMAGE_EMU", defaults={'priority': 0})
    test_game, _ = Game.objects.get_or_create(
        title="TEST_IMAGE_GAME",
        emulator=test_emu,
        defaults={'priority': 0}
    )
    
    # Test with URL only
    image_url = GameImage.objects.create(
        game=test_game,
        image_path="https://example.com/test.jpg"
    )
    
    if image_url.url == "https://example.com/test.jpg":
        print("  ✅ Image URL saved correctly")
    else:
        print(f"  ❌ Image URL incorrect. Got: {image_url.url}")
        return False
    
    # Test file upload capability (check field exists)
    from django.core.files.uploadedfile import SimpleUploadedFile
    from PIL import Image
    from io import BytesIO
    
    # Create a test image
    img = Image.new('RGB', (100, 100), color='blue')
    img_io = BytesIO()
    img.save(img_io, format='JPEG')
    img_io.seek(0)
    
    uploaded_file = SimpleUploadedFile(
        "test_image.jpg",
        img_io.read(),
        content_type="image/jpeg"
    )
    
    image_file = GameImage.objects.create(
        game=test_game,
        image_path="https://example.com/old.jpg",
        image_file=uploaded_file
    )
    
    if image_file.image_file:
        print(f"  ✅ Image file uploaded successfully: {image_file.image_file.name}")
        print(f"     URL property returns: {image_file.url}")
        
        # Verify uploaded file takes precedence
        if '/media/game_images/' in image_file.url:
            print("  ✅ Uploaded file takes precedence over URL")
        else:
            print(f"  ⚠️  URL property didn't return uploaded file path: {image_file.url}")
    else:
        print("  ❌ Image file not uploaded")
        return False
    
    # Cleanup
    if image_file.image_file:
        # Delete the actual file
        image_file.image_file.delete(save=False)
    image_url.delete()
    image_file.delete()
    test_game.delete()
    test_emu.delete()
    
    return True


def test_admin_views_handle_files():
    """Test that admin views properly handle file uploads"""
    print("\n" + "="*80)
    print("TEST 5: Admin Views Handle File Uploads")
    print("="*80)
    
    from customadmin.views import GameCreateView, GameUpdateView
    
    # Check if views use request.FILES
    import inspect
    
    create_view_source = inspect.getsource(GameCreateView.get_context_data)
    if 'self.request.FILES' in create_view_source:
        print("  ✅ GameCreateView.get_context_data handles FILES")
    else:
        print("  ❌ GameCreateView.get_context_data doesn't handle FILES")
        return False
    
    update_view_source = inspect.getsource(GameUpdateView.get_context_data)
    if 'self.request.FILES' in update_view_source:
        print("  ✅ GameUpdateView.get_context_data handles FILES")
    else:
        print("  ❌ GameUpdateView.get_context_data doesn't handle FILES")
        return False
    
    return True


def main():
    print("\n" + "="*80)
    print("ADMIN DASHBOARD - PRIORITY & IMAGE UPLOAD TEST")
    print("="*80)
    
    results = []
    
    # Run all tests
    results.append(("Priority Fields in Forms", test_priority_fields_in_forms()))
    results.append(("Image Upload Field in Form", test_image_upload_field_in_form()))
    results.append(("Priority Save Functionality", test_priority_save()))
    results.append(("Image File Upload", test_image_file_save()))
    results.append(("Admin Views Handle Files", test_admin_views_handle_files()))
    
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
        print("\n✅ Admin Dashboard Features:")
        print("  • Priority field visible in Game form")
        print("  • Priority field visible in Emulator form")
        print("  • Image URL field (image_path) available")
        print("  • Image File upload field (image_file) available")
        print("  • Priority values can be saved")
        print("  • Image files can be uploaded")
        print("  • Admin views properly handle file uploads")
        print("\n📋 Next Steps:")
        print("  1. Go to https://games.agames.cv/customadmin/games/")
        print("  2. Click Edit on any game")
        print("  3. You should now see:")
        print("     - Priority field (number input)")
        print("     - Game Images section with both URL and Upload options")
        print("  4. Test by setting priority and uploading an image")
        return 0
    else:
        print(f"\n⚠️  {total - passed} TEST(S) FAILED\n")
        return 1


if __name__ == '__main__':
    sys.exit(main())
