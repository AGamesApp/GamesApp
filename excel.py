"""
Import Emulators from Google Sheets to Django Database
Expected Sheet Columns: name, download_url, video_url (optional), icon (optional)
"""

import os
import sys
import django
import pandas as pd
import re

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gamezone.settings')
django.setup()

from games.models import Emulator


def import_emulators_from_sheet(sheet_url):
    """
    Takes a Google Sheets or Google Drive shareable link, reads emulator data,
    and imports it into the Django database.
    
    Expected columns in sheet:
    - name (required): Emulator name
    - download_url (optional): Download link
    - video_url (optional): Video tutorial link
    - icon (optional): Icon URL or path
    """
    
    # 1. Extract the Sheet/File ID using Regex
    # Support both /spreadsheets/d/ and /file/d/ formats
    match = re.search(r'/d/([a-zA-Z0-9-_]+)', sheet_url)
    
    if not match:
        print("\n❌ Error: Invalid Google Sheet/Drive URL.") 
        print("   Could not find the file ID. Make sure it is a Google Sheet or Drive link.")
        return

    sheet_id = match.group(1)
    
    # 2. Construct the CSV export URL (works for both Sheets and Drive shared files)
    csv_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"
    
    print(f"\n📊 Processing File ID: {sheet_id}...")

    try:
        # 3. Read the data using Pandas
        df = pd.read_csv(csv_url)
        
        # 4. Replace NaN with empty strings
        df = df.fillna('')
        
        # 5. Convert to list of dictionaries
        rows = df.to_dict(orient='records')
        
        print(f"✓ Found {len(rows)} rows in the sheet\n")
        
        # Statistics
        created_count = 0
        updated_count = 0
        skipped_count = 0
        error_count = 0
        
        # 6. Import each row into database
        for i, row in enumerate(rows, 1):
            try:
                # Get required field
                name = str(row.get('name', '')).strip()
                
                if not name:
                    print(f"⊖ Row {i}: Skipped (no name provided)")
                    skipped_count += 1
                    continue
                
                # Get optional fields
                download_url = str(row.get('download_url', '')).strip()
                video_url = str(row.get('video_url', '')).strip()
                icon_url = str(row.get('icon', '')).strip()
                
                # Create or update emulator
                emulator, created = Emulator.objects.update_or_create(
                    name=name,
                    defaults={
                        'download_url': download_url,
                        'video_url': video_url if video_url else '',
                        # Note: icon field expects ImageField, would need separate handling for URLs
                    }
                )
                
                if created:
                    print(f"✓ Row {i}: Created '{name}'")
                    created_count += 1
                else:
                    print(f"↻ Row {i}: Updated '{name}'")
                    updated_count += 1
                    
            except Exception as e:
                print(f"✗ Row {i}: Error - {str(e)}")
                error_count += 1
        
        # 7. Print summary
        print("\n" + "="*60)
        print("📈 IMPORT SUMMARY")
        print("="*60)
        print(f"Total rows processed: {len(rows)}")
        print(f"✓ Created: {created_count}")
        print(f"↻ Updated: {updated_count}")
        print(f"⊖ Skipped: {skipped_count}")
        print(f"✗ Errors: {error_count}")
        print("="*60)
        
        # 8. Show total emulators in database
        total_emulators = Emulator.objects.count()
        print(f"\n📦 Total Emulators in Database: {total_emulators}")
        
    except Exception as e:
        print(f"\n❌ Error: Could not read the sheet.")
        print(f"   Details: {e}")
        print("\nMake sure:")
        print("  1. The Google Sheet is set to 'Anyone with the link can view'")
        print("  2. The first row contains column headers: name, download_url, video_url")
        print("  3. The sheet has at least one data row")


def show_all_emulators():
    """Display all emulators currently in the database"""
    emulators = Emulator.objects.all()
    
    if not emulators:
        print("\n📭 No emulators found in database.")
        return
    
    print(f"\n📦 Current Emulators in Database ({emulators.count()}):")
    print("-" * 60)
    for i, emulator in enumerate(emulators, 1):
        print(f"{i}. {emulator.name}")
        if emulator.download_url:
            print(f"   Download: {emulator.download_url[:60]}...")
        if emulator.video_url:
            print(f"   Video: {emulator.video_url[:60]}...")
        print()


# --- MAIN EXECUTION ---
if __name__ == "__main__":
    print("="*60)
    print("🎮 EMULATOR DATA IMPORTER - GameZone Project")
    print("="*60)
    
    while True:
        print("\nOptions:")
        print("1. Import emulators from Google Sheet")
        print("2. View all emulators in database")
        print("3. Exit")
        
        choice = input("\nSelect option (1-3): ").strip()
        
        if choice == '1':
            user_link = input("\nPaste your Google Sheet link here: ").strip()
            
            if user_link:
                import_emulators_from_sheet(user_link)
            else:
                print("❌ No link provided.")
        
        elif choice == '2':
            show_all_emulators()
        
        elif choice == '3':
            print("\n👋 Goodbye!")
            break
        
        else:
            print("❌ Invalid option. Please select 1, 2, or 3.")
    
    input("\nPress Enter to exit...")