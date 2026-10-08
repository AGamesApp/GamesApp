#!/usr/bin/env python3
"""
game_sync_delete.py
===================
Keep ONLY the games listed in an Excel/CSV sheet for a specific emulator.
Any game that belongs to that emulator but is NOT in the sheet will be deleted.

What it does:
  - Asks for the emulator name
  - Asks for the Excel/CSV file path
  - Reads all game titles from the sheet
  - Deletes every game under that emulator whose title is NOT in the sheet
  - Shows a full preview and asks for confirmation before deleting anything

⚠️  DESTRUCTIVE — always review the preview before confirming.

Excel/CSV column required:
  game_name   → title to keep (all other columns are ignored by this script)

Usage:
  cd /root/game/agames
  source venv/bin/activate
  python scripts/game_sync_delete.py
"""

import os
import sys
import django

# ── Django setup ──────────────────────────────────────────────────────────────
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gamezone.settings')
django.setup()

import pandas as pd
from games.models import Game, Emulator


# ── Helpers ───────────────────────────────────────────────────────────────────

def safe_str(value, default=''):
    try:
        if pd.isna(value) or value is None:
            return default
        return str(value).strip()
    except Exception:
        return default


def load_file(path):
    if path.endswith('.csv'):
        df = pd.read_csv(path)
    elif path.endswith(('.xlsx', '.xls')):
        df = pd.read_excel(path)
    else:
        raise ValueError("Unsupported format — use .xlsx, .xls, or .csv")
    df.columns = df.columns.str.strip().str.lower()
    df = df.fillna('')
    return df


# ── Main logic ────────────────────────────────────────────────────────────────

def run():
    print("\n" + "=" * 60)
    print("  GAME SYNC / DELETE SCRIPT")
    print("=" * 60)
    print("  This script deletes games from an emulator that are")
    print("  NOT listed in your Excel sheet.")
    print("  Games IN the sheet are kept. All others are removed.")
    print("=" * 60)

    # 1. Ask for emulator
    emulator_name = input("\nEmulator name: ").strip()
    if not emulator_name:
        print("❌ Emulator name is required.")
        sys.exit(1)

    try:
        emulator = Emulator.objects.get(name__iexact=emulator_name)
        print(f"✓ Found emulator: {emulator.name} (id={emulator.id})")
    except Emulator.DoesNotExist:
        print(f"❌ Emulator '{emulator_name}' not found in database.")
        print("   Existing emulators:")
        for e in Emulator.objects.order_by('name'):
            print(f"     • {e.name}")
        sys.exit(1)

    # 2. Ask for file path
    file_path = input("Excel/CSV file path: ").strip().strip('"').strip("'")
    if not os.path.isfile(file_path):
        print(f"❌ File not found: {file_path}")
        sys.exit(1)

    # 3. Load file
    try:
        df = load_file(file_path)
    except Exception as e:
        print(f"❌ Could not read file: {e}")
        sys.exit(1)

    if 'game_name' not in df.columns:
        print("❌ Column 'game_name' is required but not found.")
        print(f"   Columns found: {', '.join(df.columns.tolist())}")
        sys.exit(1)

    # 4. Build set of titles to KEEP (case-insensitive)
    sheet_titles_raw = [
        safe_str(row.get('game_name', ''))
        for row in df.to_dict(orient='records')
    ]
    keep_titles = {t.lower() for t in sheet_titles_raw if t}
    print(f"\n✓ Sheet contains {len(keep_titles)} unique game titles to keep")

    # 5. Find games in DB for this emulator
    all_db_games = Game.objects.filter(emulator=emulator).order_by('title')
    total_db = all_db_games.count()
    print(f"✓ Database has {total_db} games for '{emulator.name}'")

    # 6. Separate into KEEP / DELETE lists
    to_keep = []
    to_delete = []

    for game in all_db_games:
        if game.title.lower() in keep_titles:
            to_keep.append(game)
        else:
            to_delete.append(game)

    # 7. Preview
    print(f"\n  Games to KEEP  : {len(to_keep)}")
    print(f"  Games to DELETE: {len(to_delete)}")

    if not to_delete:
        print("\n✅ Nothing to delete — all DB games are already in the sheet.")
        sys.exit(0)

    print("\n" + "-" * 60)
    print("  GAMES THAT WILL BE DELETED:")
    print("-" * 60)
    for g in to_delete:
        stats = f"views={g.views}, downloads={g.downloads}"
        premium = "  [PREMIUM]" if g.is_premium else ""
        print(f"  🗑  [{g.id:>7}]  {g.title}{premium}  ({stats})")

    print("-" * 60)

    # 8. Confirm
    print(f"\n⚠️  You are about to permanently delete {len(to_delete)} game(s)")
    print("   from emulator:", emulator.name)
    print("   This will also remove all related ratings, reviews, loves,")
    print("   images, and purchase records tied to these games.")
    confirm = input("\n   Type  DELETE  to confirm, or anything else to cancel: ").strip()

    if confirm != 'DELETE':
        print("\n🚫 Cancelled — nothing was deleted.")
        sys.exit(0)

    # 9. Delete
    print()
    deleted_count = 0
    error_count = 0

    for game in to_delete:
        try:
            title = game.title
            game_id = game.id
            game.delete()
            print(f"  🗑  Deleted [{game_id}] '{title}'")
            deleted_count += 1
        except Exception as e:
            print(f"  ✗  Error deleting [{game.id}] '{game.title}': {e}")
            error_count += 1

    # 10. Summary
    print("\n" + "=" * 60)
    print("  SUMMARY")
    print("=" * 60)
    print(f"  Emulator       : {emulator.name}")
    print(f"  File           : {os.path.basename(file_path)}")
    print(f"  Titles in sheet: {len(keep_titles)}")
    print(f"  Was in DB      : {total_db}")
    print(f"  ✅ Kept        : {len(to_keep)}")
    print(f"  🗑  Deleted     : {deleted_count}")
    if error_count:
        print(f"  ✗  Errors      : {error_count}")
    remaining = Game.objects.filter(emulator=emulator).count()
    print(f"\n  Remaining games for '{emulator.name}' in DB: {remaining}")
    print("=" * 60)


if __name__ == '__main__':
    run()
