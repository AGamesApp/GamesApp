"""
Import Games from Google Sheets/Excel to Django Database

REQUIRED Columns:
  - game_name (required) → title (database)
  - console (required) → emulator (database)

OPTIONAL Columns:
  - priority (default: 0) → Higher values appear first
  - description → Game description text
  - image_url → Main game image URL
  - image_1, image_2, image_3, image_4, image_5 → Additional screenshot URLs
  - size (e.g., "500 MB")
  - download_url → Download link
  - game_url → Game page URL
  - video_url → Video preview URL
  - region (e.g., "USA", "Europe")
  - genres → Comma-separated (e.g., "Action, RPG")
  - is_premium → true/false, 1/0, yes/no
  - year → Release year

All optional fields will use safe defaults if empty or missing.
"""

import os
import sys
import django
import pandas as pd
import re

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gamezone.settings')
django.setup()

from games.models import Game, Emulator, Genre, GameImage


def safe_str(value, default=''):
    """Safely convert value to string with default."""
    try:
        if pd.isna(value) or value is None:
            return default
        return str(value).strip()
    except:
        return default


def safe_int(value, default=0):
    """Safely convert value to integer with default."""
    try:
        if pd.isna(value) or value is None or value == '':
            return default
        # Remove any non-numeric characters except minus sign
        cleaned = re.sub(r'[^\d-]', '', str(value))
        return int(cleaned) if cleaned and cleaned != '-' else default
    except:
        return default


def safe_bool(value, default=False):
    """Safely convert value to boolean with default."""
    try:
        if pd.isna(value) or value is None:
            return default
        str_val = str(value).strip().lower()
        return str_val in ['true', '1', 'yes', 'premium', 'y', 't']
    except:
        return default


def import_games_from_sheet(sheet_url):
    """
    Takes a Google Sheets or Google Drive shareable link, reads game data,
    and imports it into the Django database.
    
    REQUIRED columns:
    - game_name → Game title
    - console → Emulator/Console name
    
    OPTIONAL columns (with safe defaults):
    - priority (default: 0)
    - description (default: '')
    - image_url (default: '')
    - image_1 to image_5 (default: '')
    - size (default: '')
    - download_url (default: '')
    - game_url (default: '')
    - video_url (default: '')
    - region (default: '')
    - genres (default: '')
    - is_premium (default: false)
    - year (default: '')
    """
    
    # 1. Extract the Sheet/File ID using Regex
    # Support both /spreadsheets/d/ and /file/d/ formats
    match = re.search(r'/d/([a-zA-Z0-9-_]+)', sheet_url)
    
    if not match:
        print("\n❌ Error: Invalid Google Sheet/Drive URL.") 
        print("   Could not find the file ID. Make sure it is a Google Sheet or Drive link.")
        return

    sheet_id = match.group(1)
    
    # 2. Try multiple URL formats (Google Sheets and Google Drive)
    urls_to_try = [
        f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv",
        f"https://drive.google.com/uc?export=download&id={sheet_id}",
        f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid=0",
    ]
    
    print(f"\n📊 Processing File ID: {sheet_id}...")
    
    df = None
    for url in urls_to_try:
        try:
            df = pd.read_csv(url)
            print(f"✓ Successfully accessed the file!")
            break
        except Exception as e:
            continue
    
    if df is None:
        print("\n❌ Error: Could not access the file with any URL format.")
        print("   Make sure the file is set to 'Anyone with the link can view'")
        return

    try:
        # 3. Normalize column names (lowercase, strip spaces)
        df.columns = df.columns.str.strip().str.lower()
        
        # 4. Replace NaN/null with empty strings for safe processing
        df = df.fillna('')
        
        # 5. Convert to list of dictionaries
        rows = df.to_dict(orient='records')
        
        print(f"✓ Found {len(rows)} rows in the sheet")
        print(f"✓ Columns detected: {', '.join(df.columns.tolist())}\n")
        
        # Statistics
        created_count = 0
        updated_count = 0
        skipped_count = 0
        error_count = 0
        images_added_count = 0
        
        # 6. REVERSE the rows to import from last to first (descending order)
        rows.reverse()
        print(f"✓ Processing in reverse order (last row first)\n")
        
        # 7. Import each row into database with error handling
        for i, row in enumerate(rows, 1):
            try:
                # ===== GET REQUIRED FIELDS =====
                title = safe_str(row.get('game_name', ''))
                console_name = safe_str(row.get('console', ''))
                
                # Skip if missing required fields
                if not title:
                    print(f"⊖ Row {i}: Skipped (no game_name provided)")
                    skipped_count += 1
                    continue
                
                if not console_name:
                    print(f"⊖ Row {i}: Skipped '{title}' (no console/emulator provided)")
                    skipped_count += 1
                    continue
                
                # ===== FIND OR CREATE EMULATOR =====
                try:
                    emulator = Emulator.objects.get(name__iexact=console_name)
                except Emulator.DoesNotExist:
                    print(f"⚠ Row {i}: Emulator '{console_name}' not found. Creating it...")
                    emulator, _ = Emulator.objects.get_or_create(
                        name=console_name,
                        defaults={
                            'download_url': '',
                            'video_url': '',
                            'priority': 0,
                        }
                    )
                except Exception as e:
                    print(f"✗ Row {i}: Error finding/creating emulator - {str(e)}")
                    error_count += 1
                    continue
                
                # ===== GET ALL OPTIONAL FIELDS WITH SAFE DEFAULTS =====
                priority = safe_int(row.get('priority', 0), default=0)
                description = safe_str(row.get('description', ''))
                image_url = safe_str(row.get('image_url', ''))
                size = safe_str(row.get('size', ''))
                download_url = safe_str(row.get('download_url', ''))
                game_url = safe_str(row.get('game_url', ''))
                video_url = safe_str(row.get('video_url', ''))
                region = safe_str(row.get('region', ''))
                year = safe_str(row.get('year', ''))
                is_premium = safe_bool(row.get('is_premium', False), default=False)
                
                # Handle genres (comma-separated) with safe processing
                genres_raw = safe_str(row.get('genres', ''))
                genre_list = []
                if genres_raw:
                    genre_list = [g.strip() for g in genres_raw.split(',') if g.strip()]
                
                # Collect additional image URLs (image_1 to image_5)
                additional_images = []
                for img_num in range(1, 6):
                    img_url = safe_str(row.get(f'image_{img_num}', ''))
                    if img_url:
                        additional_images.append(img_url)
                
                # ===== CREATE GAME (ALWAYS CREATE, NEVER SKIP) =====
                # Every row is treated as unique - no duplicate checking
                game = Game.objects.create(
                    title=title,
                    emulator=emulator,
                    priority=priority,
                    description=description,
                    image_url=image_url,
                    size=size,
                    download_url=download_url,
                    game_url=game_url,
                    video_url=video_url,
                    region=region,
                    is_premium=is_premium,
                    year=year,
                )
                created = True
                # ===== HANDLE GENRES (ManyToMany relationship) =====
                if genre_list:
                    try:
                        genre_objects = []
                        for genre_name in genre_list:
                            genre, _ = Genre.objects.get_or_create(name=genre_name)
                            genre_objects.append(genre)
                        game.genres.set(genre_objects)
                    except Exception as e:
                        print(f"  ⚠ Warning: Could not add genres - {str(e)}")
                
                # ===== ADD ADDITIONAL IMAGES AS GameImage OBJECTS =====
                if additional_images:
                    try:
                        # Clear existing images for this game to avoid duplicates
                        if created:
                            game.images.all().delete()
                        
                        # Add new images
                        for order, img_url in enumerate(additional_images, start=1):
                            GameImage.objects.update_or_create(
                                game=game,
                                image_path=img_url,
                                defaults={
                                    'order': order,
                                }
                            )
                        images_added_count += len(additional_images)
                        image_info = f" (+{len(additional_images)} images)"
                    except Exception as e:
                        print(f"  ⚠ Warning: Could not add images - {str(e)}")
                        image_info = ""
                else:
                    image_info = ""
                
                # ===== LOG SUCCESS =====
                priority_tag = f" [Priority: {priority}]" if priority != 0 else ""
                premium_tag = " [PREMIUM]" if is_premium else ""
                
                print(f"✓ Row {i}: Created '{title}' ({console_name}){priority_tag}{premium_tag}{image_info}")
                created_count += 1
                    
            except Exception as e:
                print(f"✗ Row {i}: Unexpected error - {str(e)}")
                error_count += 1
                # Continue processing other rows even if one fails
        
        # 7. Print summary
        print("\n" + "="*60)
        print("📈 IMPORT SUMMARY")
        print("="*60)
        print(f"Total rows processed: {len(rows)}")
        print(f"✓ Created: {created_count}")
        print(f"↻ Updated: {updated_count}")
        print(f"⊖ Skipped: {skipped_count}")
        print(f"✗ Errors: {error_count}")
        print(f"📸 Images added: {images_added_count}")
        print("="*60)
        
        # 8. Show total games in database
        total_games = Game.objects.count()
        print(f"\n📦 Total Games in Database: {total_games}")
        
    except Exception as e:
        print(f"\n❌ Fatal Error: Could not process the sheet.")
        print(f"   Details: {str(e)}")
        print("\n🔍 Troubleshooting:")
        print("  1. Make sure the Google Sheet/Drive file is set to 'Anyone with the link can view'")
        print("  2. If using Google Drive link, ensure it's a Google Sheets file")
        print("  3. The first row must contain column headers")
        print("  4. Required columns: game_name, console")
        print("  5. Optional columns: priority, description, image_url, image_1-5, size,")
        print("     download_url, game_url, video_url, region, genres, is_premium, year")


def import_games_from_file(file_path):
    """
    Import games from a local Excel or CSV file.
    
    REQUIRED columns:
    - game_name → Game title
    - console → Emulator/Console name
    
    OPTIONAL columns (with safe defaults):
    - priority, description, image_url, image_1-5, size,
    - download_url, game_url, video_url, region, genres, is_premium, year
    """
    
    print(f"\n📊 Processing file: {file_path}...")
    
    try:
        # Read the file based on extension
        if file_path.endswith('.csv'):
            df = pd.read_csv(file_path)
        elif file_path.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(file_path)
        else:
            print(f"❌ Error: Unsupported file format. Use .xlsx, .xls, or .csv")
            return
        
        print(f"✓ Successfully loaded the file!")
        _process_import_dataframe(df)
        
    except Exception as e:
        print(f"\n❌ Fatal Error: Could not process the file.")
        print(f"   Details: {str(e)}")
        print("\n🔍 Troubleshooting:")
        print("  1. Make sure the file is a valid Excel (.xlsx, .xls) or CSV file")
        print("  2. The first row must contain column headers")
        print("  3. Required columns: game_name, console")
        print("  4. Optional columns: priority, description, image_url, image_1-5, size,")
        print("     download_url, game_url, video_url, region, genres, is_premium, year")


def import_games_from_memory(file_content, file_name):
    """
    Import games from a file object in memory (BytesIO).
    
    REQUIRED columns:
    - game_name → Game title
    - console → Emulator/Console name
    """
    
    print(f"\n📊 Processing uploaded file: {file_name}...")
    
    try:
        # Read the file based on extension
        if file_name.endswith('.csv'):
            df = pd.read_csv(file_content)
        elif file_name.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(file_content)
        else:
            print(f"❌ Error: Unsupported file format. Use .xlsx, .xls, or .csv")
            return
        
        print(f"✓ Successfully loaded the file!")
        _process_import_dataframe(df)
        
    except Exception as e:
        print(f"\n❌ Fatal Error: Could not process the file.")
        print(f"   Details: {str(e)}")


def _process_import_dataframe(df):
    """
    Common processing logic for both file and memory imports.
    Takes a pandas DataFrame and imports all rows.
    """
    try:
        # Normalize column names (lowercase, strip spaces)
        df.columns = df.columns.str.strip().str.lower()
        
        # Replace NaN/null with empty strings for safe processing
        df = df.fillna('')
        
        # Convert to list of dictionaries
        rows = df.to_dict(orient='records')
        
        print(f"✓ Found {len(rows)} rows in the file")
        print(f"✓ Columns detected: {', '.join(df.columns.tolist())}\n")
        
        # Statistics
        created_count = 0
        updated_count = 0
        skipped_count = 0
        error_count = 0
        images_added_count = 0
        
        # REVERSE the rows to import from last to first (descending order)
        rows.reverse()
        print(f"✓ Processing in reverse order (last row first)\n")
        
        # Import each row into database with error handling
        for i, row in enumerate(rows, 1):
            try:
                # ===== GET REQUIRED FIELDS =====
                title = safe_str(row.get('game_name', ''))
                console_name = safe_str(row.get('console', ''))
                
                # Skip if missing required fields
                if not title:
                    print(f"⊖ Row {i}: Skipped (no game_name provided)")
                    skipped_count += 1
                    continue
                
                if not console_name:
                    print(f"⊖ Row {i}: Skipped '{title}' (no console/emulator provided)")
                    skipped_count += 1
                    continue
                
                # ===== FIND OR CREATE EMULATOR =====
                try:
                    emulator = Emulator.objects.get(name__iexact=console_name)
                except Emulator.DoesNotExist:
                    print(f"⚠ Row {i}: Emulator '{console_name}' not found. Creating it...")
                    emulator, _ = Emulator.objects.get_or_create(
                        name=console_name,
                        defaults={
                            'download_url': '',
                            'video_url': '',
                            'priority': 0,
                        }
                    )
                except Exception as e:
                    print(f"✗ Row {i}: Error finding/creating emulator - {str(e)}")
                    error_count += 1
                    continue
                
                # ===== GET ALL OPTIONAL FIELDS WITH SAFE DEFAULTS =====
                priority = safe_int(row.get('priority', 0), default=0)
                description = safe_str(row.get('description', ''))
                image_url = safe_str(row.get('image_url', ''))
                size = safe_str(row.get('size', ''))
                download_url = safe_str(row.get('download_url', ''))
                game_url = safe_str(row.get('game_url', ''))
                video_url = safe_str(row.get('video_url', ''))
                region = safe_str(row.get('region', ''))
                year = safe_str(row.get('year', ''))
                is_premium = safe_bool(row.get('is_premium', False), default=False)
                
                # Handle genres (comma-separated) with safe processing
                genres_raw = safe_str(row.get('genres', ''))
                genre_list = []
                if genres_raw:
                    genre_list = [g.strip() for g in genres_raw.split(',') if g.strip()]
                
                # Collect additional image URLs (image_1 to image_5)
                additional_images = []
                for img_num in range(1, 6):
                    img_url = safe_str(row.get(f'image_{img_num}', ''))
                    if img_url:
                        additional_images.append(img_url)
                
                # ===== CREATE GAME (ALWAYS CREATE, NEVER SKIP) =====
                # Every row is treated as unique - no duplicate checking
                game = Game.objects.create(
                    title=title,
                    emulator=emulator,
                    priority=priority,
                    description=description,
                    image_url=image_url,
                    size=size,
                    download_url=download_url,
                    game_url=game_url,
                    video_url=video_url,
                    region=region,
                    is_premium=is_premium,
                    year=year,
                )
                created = True
                
                # ===== HANDLE GENRES (ManyToMany relationship) =====
                if genre_list:
                    try:
                        genre_objects = []
                        for genre_name in genre_list:
                            genre, _ = Genre.objects.get_or_create(name=genre_name)
                            genre_objects.append(genre)
                        game.genres.set(genre_objects)
                    except Exception as e:
                        print(f"  ⚠ Warning: Could not add genres - {str(e)}")
                
                # ===== ADD ADDITIONAL IMAGES AS GameImage OBJECTS =====
                image_info = ""
                if additional_images:
                    try:
                        # Add new images
                        for order, img_url in enumerate(additional_images, start=1):
                            GameImage.objects.update_or_create(
                                game=game,
                                image_path=img_url,
                                defaults={
                                    'order': order,
                                }
                            )
                        images_added_count += len(additional_images)
                        image_info = f" (+{len(additional_images)} images)"
                    except Exception as e:
                        print(f"  ⚠ Warning: Could not add images - {str(e)}")
                        image_info = ""
                else:
                    image_info = ""
                
                # ===== LOG SUCCESS =====
                priority_tag = f" [Priority: {priority}]" if priority != 0 else ""
                premium_tag = " [PREMIUM]" if is_premium else ""
                
                print(f"✓ Row {i}: Created '{title}' ({console_name}){priority_tag}{premium_tag}{image_info}")
                created_count += 1
                    
            except Exception as e:
                print(f"✗ Row {i}: Unexpected error - {str(e)}")
                error_count += 1
                # Continue processing other rows even if one fails
        
        # 8. Print summary
        print("\n" + "="*60)
        print("📈 IMPORT SUMMARY")
        print("="*60)
        print(f"Total rows processed: {len(rows)}")
        print(f"✓ Created: {created_count}")
        print(f"↻ Updated: {updated_count}")
        print(f"⊖ Skipped: {skipped_count}")
        print(f"✗ Errors: {error_count}")
        print(f"📸 Images added: {images_added_count}")
        print("="*60)
        
        # 9. Show total games in database
        total_games = Game.objects.count()
        print(f"\n📦 Total Games in Database: {total_games}")
        
    except Exception as e:
        print(f"\n❌ Fatal Error: Could not process the file.")
        print(f"   Details: {str(e)}")
        print("\n🔍 Troubleshooting:")
        print("  1. Make sure the file is a valid Excel (.xlsx, .xls) or CSV file")
        print("  2. The first row must contain column headers")
        print("  3. Required columns: game_name, console")
        print("  4. Optional columns: priority, description, image_url, image_1-5, size,")
        print("     download_url, game_url, video_url, region, genres, is_premium, year")


def show_all_games():
    """Display all games currently in the database"""
    games = Game.objects.select_related('emulator').prefetch_related('genres').all()
    
    if not games:
        print("\n📭 No games found in database.")
        return
    
    print(f"\n📦 Current Games in Database ({games.count()}):")
    print("-" * 80)
    for i, game in enumerate(games, 1):
        priority_tag = f" [P:{game.priority}]" if game.priority != 0 else ""
        premium_tag = " [PREMIUM]" if game.is_premium else ""
        genres_str = ", ".join([g.name for g in game.genres.all()]) if game.genres.exists() else "No genres"
        
        print(f"{i}. {game.title} ({game.emulator.name}){priority_tag}{premium_tag}")
        print(f"   Genres: {genres_str}")
        if game.region:
            print(f"   Region: {game.region}")
        if game.year:
            print(f"   Year: {game.year}")
        if game.size:
            print(f"   Size: {game.size}")
        print(f"   Views: {game.views} | Downloads: {game.downloads}")
        
        # Show image count
        image_count = game.images.count()
        if image_count > 0:
            print(f"   📸 Images: {image_count}")
        
        print()


def show_stats():
    """Display database statistics"""
    total_games = Game.objects.count()
    total_emulators = Emulator.objects.count()
    total_genres = Genre.objects.count()
    premium_games = Game.objects.filter(is_premium=True).count()
    free_games = Game.objects.filter(is_premium=False).count()
    
    print("\n" + "="*60)
    print("📊 DATABASE STATISTICS")
    print("="*60)
    print(f"Total Games: {total_games}")
    print(f"  ├─ Premium: {premium_games}")
    print(f"  └─ Free: {free_games}")
    print(f"Total Emulators: {total_emulators}")
    print(f"Total Genres: {total_genres}")
    print("="*60)
    
    # Show games per emulator
    print("\n📱 Games per Emulator:")
    from django.db.models import Count
    emulators = Emulator.objects.annotate(game_count=Count('games')).order_by('-game_count')
    for emulator in emulators:
        print(f"  • {emulator.name}: {emulator.game_count} games")


if __name__ == "__main__":
    print("="*60)
    print("🎮 GAME DATA IMPORTER - GameZone Project")
    print("="*60)
    print("\n📋 EXCEL/GOOGLE SHEETS COLUMN SPECIFICATION:")
    print("\n✅ REQUIRED Columns:")
    print("  • game_name      → Game title (required)")
    print("  • console        → Emulator/Console name (required)")
    print("\n⭐ OPTIONAL Columns (with safe defaults):")
    print("  • priority       → Number (higher = appears first), default: 0")
    print("  • description    → Game description text, default: empty")
    print("  • image_url      → Main game image URL, default: empty")
    print("  • image_1        → Additional screenshot URL #1, default: empty")
    print("  • image_2        → Additional screenshot URL #2, default: empty")
    print("  • image_3        → Additional screenshot URL #3, default: empty")
    print("  • image_4        → Additional screenshot URL #4, default: empty")
    print("  • image_5        → Additional screenshot URL #5, default: empty")
    print("  • size           → File size (e.g., '500 MB'), default: empty")
    print("  • download_url   → Download link, default: empty")
    print("  • game_url       → Game page URL, default: empty")
    print("  • video_url      → Video preview URL, default: empty")
    print("  • region         → Region (e.g., 'USA', 'Europe'), default: empty")
    print("  • genres         → Comma-separated (e.g., 'Action, RPG'), default: empty")
    print("  • is_premium     → true/false, 1/0, yes/no, default: false")
    print("  • year           → Release year, default: empty")
    print("\n💡 Tips:")
    print("  • All empty cells will use safe default values")
    print("  • Script will never crash - errors are logged and skipped")
    print("  • Images (image_1 to image_5) are added as links to GameImage table")
    print("  • Column names are case-insensitive")
    
    while True:
        print("\n" + "-"*60)
        print("Options:")
        print("1. Import games from Google Sheet")
        print("2. View all games in database")
        print("3. Show database statistics")
        print("4. Exit")
        
        choice = input("\nSelect option (1-4): ").strip()
        
        if choice == '1':
            user_link = input("\nPaste your Google Sheet link here: ").strip()
            
            if user_link:
                import_games_from_sheet(user_link)
            else:
                print("❌ No link provided.")
        
        elif choice == '2':
            show_all_games()
        
        elif choice == '3':
            show_stats()
        
        elif choice == '4':
            print("\n👋 Goodbye!")
            break
        
        else:
            print("❌ Invalid option. Please select 1, 2, 3, or 4.")
    
    input("\nPress Enter to exit...")
