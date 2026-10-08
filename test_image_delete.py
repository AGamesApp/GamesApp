#!/usr/bin/env python
"""
Test Image Delete Functionality in Admin Dashboard
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gamezone.settings')
django.setup()

from games.models import Game, Emulator, GameImage
from django.forms import inlineformset_factory

def test_image_delete():
    """Test that DELETE checkbox works in formset"""
    print("\n" + "="*80)
    print("TEST: Image Delete Functionality")
    print("="*80)
    
    # Create test data
    test_emu, _ = Emulator.objects.get_or_create(name="TEST_DELETE_EMU", defaults={'priority': 0})
    test_game, _ = Game.objects.get_or_create(
        title="TEST_DELETE_GAME",
        emulator=test_emu,
        defaults={'priority': 0}
    )
    
    # Create test images
    image1 = GameImage.objects.create(
        game=test_game,
        image_path="https://example.com/image1.jpg"
    )
    image2 = GameImage.objects.create(
        game=test_game,
        image_path="https://example.com/image2.jpg"
    )
    
    print(f"\n  Created test game with 2 images:")
    print(f"    Image 1 ID: {image1.id}")
    print(f"    Image 2 ID: {image2.id}")
    
    # Create formset
    GameImageFormSet = inlineformset_factory(
        Game, 
        GameImage, 
        fields=('image_path', 'image_file'), 
        extra=0, 
        can_delete=True
    )
    
    # Simulate POST data with DELETE checkbox checked for image1
    post_data = {
        'images-TOTAL_FORMS': '2',
        'images-INITIAL_FORMS': '2',
        'images-MIN_NUM_FORMS': '0',
        'images-MAX_NUM_FORMS': '1000',
        
        # Image 1 - marked for deletion
        f'images-0-id': str(image1.id),
        f'images-0-game': str(test_game.id),
        f'images-0-image_path': image1.image_path,
        f'images-0-DELETE': 'on',  # This should delete the image
        
        # Image 2 - keep it
        f'images-1-id': str(image2.id),
        f'images-1-game': str(test_game.id),
        f'images-1-image_path': image2.image_path,
    }
    
    print("\n  Simulating form submission with image1 DELETE='on'...")
    
    # Process formset
    formset = GameImageFormSet(post_data, instance=test_game)
    
    if formset.is_valid():
        print("  ✅ Formset is valid")
        
        # Check which forms are marked for deletion
        deleted_forms = [form for form in formset if form.cleaned_data.get('DELETE')]
        print(f"  Forms marked for deletion: {len(deleted_forms)}")
        
        for form in deleted_forms:
            if form.instance.pk:
                print(f"    - Image ID {form.instance.pk} will be deleted")
        
        # Save the formset (this should delete image1)
        formset.save()
        
        # Verify deletion
        remaining_images = GameImage.objects.filter(game=test_game)
        print(f"\n  Images after save: {remaining_images.count()}")
        
        if remaining_images.count() == 1:
            remaining = remaining_images.first()
            if remaining.id == image2.id:
                print(f"  ✅ PASS: Image 1 deleted successfully")
                print(f"  ✅ PASS: Image 2 ({remaining.id}) still exists")
                print(f"         URL: {remaining.image_path}")
                
                # Cleanup
                remaining.delete()
                test_game.delete()
                test_emu.delete()
                return True
            else:
                print(f"  ❌ FAIL: Wrong image remains (expected {image2.id}, got {remaining.id})")
                test_game.delete()
                test_emu.delete()
                return False
        else:
            print(f"  ❌ FAIL: Expected 1 image, found {remaining_images.count()}")
            test_game.delete()
            test_emu.delete()
            return False
    else:
        print("  ❌ Formset is invalid")
        print(f"  Errors: {formset.errors}")
        test_game.delete()
        test_emu.delete()
        return False


def test_delete_checkbox_rendering():
    """Test that DELETE checkbox is properly rendered in template"""
    print("\n" + "="*80)
    print("TEST: DELETE Checkbox Rendering")
    print("="*80)
    
    # Check template has DELETE field
    with open('/root/game/customadmin/templates/customadmin/game_form.html', 'r') as f:
        template_content = f.read()
    
    if '{{ form.DELETE }}' in template_content:
        print("  ✅ Template includes {{ form.DELETE }}")
    else:
        print("  ❌ Template missing {{ form.DELETE }}")
        return False
    
    if 'deleteInput.checked = true' in template_content:
        print("  ✅ JavaScript sets deleteInput.checked = true")
    else:
        print("  ⚠️  JavaScript doesn't set deleteInput.checked")
    
    if "deleteInput.value = 'on'" in template_content:
        print("  ✅ JavaScript sets deleteInput.value = 'on'")
    else:
        print("  ⚠️  JavaScript doesn't set deleteInput.value")
    
    if 'input[name$="-DELETE"]' in template_content:
        print("  ✅ JavaScript queries DELETE input correctly")
    else:
        print("  ❌ JavaScript doesn't query DELETE input")
        return False
    
    return True


def main():
    print("\n" + "="*80)
    print("IMAGE DELETE FUNCTIONALITY TEST")
    print("="*80)
    
    results = []
    
    # Run tests
    results.append(("DELETE Checkbox Rendering", test_delete_checkbox_rendering()))
    results.append(("Image Delete Functionality", test_image_delete()))
    
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
        print("\n✅ Image Delete Feature:")
        print("  • DELETE checkbox rendered in template")
        print("  • JavaScript marks forms for deletion correctly")
        print("  • Formset processes DELETE correctly")
        print("  • Images are actually deleted from database")
        print("\n📋 How to Use:")
        print("  1. Go to game edit page")
        print("  2. Find image in 'Game Images & Screenshots' section")
        print("  3. Click 'Remove' button (🗑️)")
        print("  4. Image will be hidden")
        print("  5. Click 'Save' button at bottom of form")
        print("  6. Image will be deleted from database")
        return 0
    else:
        print(f"\n⚠️  {total - passed} TEST(S) FAILED\n")
        return 1


if __name__ == '__main__':
    sys.exit(main())
