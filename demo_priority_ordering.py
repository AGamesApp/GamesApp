#!/usr/bin/env python
"""
Demonstration of priority ordering for games and emulators
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gamezone.settings')
django.setup()

from games.models import Game, Emulator

def demo_priority_ordering():
    """Show how priority affects ordering"""
    
    print("\n" + "="*80)
    print("PRIORITY ORDERING DEMONSTRATION")
    print("="*80)
    
    # Show current emulators ordered by priority
    print("\n📋 EMULATORS (ordered by priority DESC, then name):")
    print("-" * 80)
    emulators = Emulator.objects.all().order_by('-priority', 'name')[:10]
    
    for idx, emu in enumerate(emulators, 1):
        print(f"  {idx}. {emu.name:40} | Priority: {emu.priority:3}")
    
    # Show current games ordered by priority
    print("\n📋 GAMES (ordered by priority DESC, then views DESC):")
    print("-" * 80)
    games = Game.objects.select_related('emulator').order_by('-priority', '-views')[:10]
    
    for idx, game in enumerate(games, 1):
        print(f"  {idx}. {game.title[:35]:35} | Priority: {game.priority:3} | Views: {game.views:6} | Emulator: {game.emulator.name}")
    
    # Explanation
    print("\n" + "="*80)
    print("HOW PRIORITY WORKS:")
    print("="*80)
    print("""
  1. Higher priority numbers appear first (sorted descending)
  2. Default priority is 0 for all items
  3. Set priority > 0 to feature items at the top
  4. Set priority < 0 to push items to the bottom
  
  Examples:
    priority = 100  → Featured (top of list)
    priority = 10   → Important
    priority = 0    → Normal (default)
    priority = -10  → Less visible
    priority = -100 → Hidden/deprecated (bottom of list)
  
  Ordering Rules:
    
    API Endpoints:
      - Emulators: ORDER BY -priority, name
      - Games: ORDER BY -priority, -views, -downloads, -created_at
      - Search: ORDER BY -priority, -search_rank, -views
    
    Admin Dashboard:
      - Emulators: ORDER BY -priority, -id
      - Games: ORDER BY -priority, -id
    
  How to Set Priority:
    
    Via Admin Dashboard:
      1. Go to https://games.agames.cv/customadmin/games/ (or /emulators/)
      2. Click Edit on any game/emulator
      3. Set the Priority field (integer)
      4. Save changes
    
    Via Django Admin:
      python manage.py shell
      >>> game = Game.objects.get(id=123)
      >>> game.priority = 100  # Feature this game
      >>> game.save()
      
      >>> emulator = Emulator.objects.get(id=5)
      >>> emulator.priority = 50  # Make this emulator prominent
      >>> emulator.save()
""")
    
    print("\n" + "="*80)
    print("IMAGE UPLOAD OPTIONS:")
    print("="*80)
    print("""
  GameImage supports TWO ways to add images:
  
  Option 1: External URL (image_path)
    - Store external image URL
    - Example: "https://example.com/game.jpg"
    - No server storage needed
    - Use when images are hosted elsewhere
    
  Option 2: File Upload (image_file)
    - Upload image file to server
    - Stored in media/game_images/
    - Use when you want to host images locally
    
  Priority: If both are set, image_file takes precedence
  
  Usage in Admin:
    1. Go to game edit page
    2. Scroll to "Game Images" section
    3. For each image:
       - Either enter a URL in "Image Path"
       - OR upload a file in "Image File"
    4. Save
    
  API Response:
    {
      "images": [
        {
          "id": 1,
          "image_path": "https://example.com/img.jpg",
          "image_file": "/media/game_images/uploaded.jpg",
          "url": "/media/game_images/uploaded.jpg",  ← This is what clients use
          "order": 0
        }
      ]
    }
    
    The "url" field automatically returns:
    - image_file URL if uploaded
    - image_path URL if no upload
""")


def show_how_to_set_priority():
    """Show practical example of setting priority"""
    
    print("\n" + "="*80)
    print("EXAMPLE: Setting Priority for Popular Game")
    print("="*80)
    
    # Find a game to feature
    game = Game.objects.filter(views__gt=0).order_by('-views').first()
    
    if game:
        print(f"\nLet's feature this popular game:")
        print(f"  Title: {game.title}")
        print(f"  Current Priority: {game.priority}")
        print(f"  Views: {game.views}")
        print(f"  Current Position in List: ?")
        
        print(f"\nTo make it appear first, set priority to 100:")
        print(f"  game = Game.objects.get(id={game.id})")
        print(f"  game.priority = 100")
        print(f"  game.save()")
        
        print(f"\nOr via admin dashboard:")
        print(f"  https://games.agames.cv/customadmin/games/{game.id}/edit/")
        print(f"  Change Priority field to 100")
        print(f"  Click Save")


if __name__ == '__main__':
    demo_priority_ordering()
    show_how_to_set_priority()
