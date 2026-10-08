#!/usr/bin/env python3
"""
game_import_update.py
=====================
Add new games + update existing game attributes from an Excel/CSV sheet.

What it does:
  - Asks for the emulator name
  - Asks for the Excel/CSV file path
  - For each row in the sheet:
      ✅ NEW game (title not found under that emulator) → creates it
      ♻️  EXISTING game (same title + same emulator) → updates content fields ONLY
          ❌ NEVER touches: views, downloads, created_at, ratings, reviews, loves

Safe to run multiple times — it is fully idempotent.

Excel/CSV columns:
  REQUIRED:
    game_name        → title
  OPTIONAL (leave blank to keep existing value on update):
    priority         → integer, default 0
    description
    image_url        → main cover image  (alt: cover_image_url)
    image_1 … image_5 → additional screenshot URLs
    size             → e.g. "500 MB"
    download_url     → (alt: download_link)
    game_url
    video_url
    region           → e.g. "USA"
    genres           → comma-separated, e.g. "Action, RPG"
    is_premium       → true/false/1/0/yes/no
    year             → e.g. "1998"  (alt: release_date — year extracted automatically)
    article          → if present, used as description (rich content preferred)

Usage:
  cd /root/game/agames
  source venv/bin/activate
  python scripts/game_import_update.py
"""

import os
import sys
import django
import re

# ── Django setup ──────────────────────────────────────────────────────────────
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gamezone.settings')
django.setup()

import pandas as pd
from games.models import Game, Emulator, Genre, GameImage

# ── Fields that belong to the content editor (safe to update from sheet) ─────
CONTENT_FIELDS = [
    'priority', 'description', 'image_url',
    'download_url', 'game_url', 'video_url', 'region',
    'is_premium', 'year',
]  # 'size' intentionally excluded — never overwritten from sheet

# ── Fields that belong to users / stats — NEVER overwrite ────────────────────
PROTECTED_FIELDS = ['views', 'downloads', 'created_at', 'updated_at']


# ── Helpers ───────────────────────────────────────────────────────────────────

def safe_str(value, default=''):
    try:
        if pd.isna(value) or value is None:
            return default
        return str(value).strip()
    except Exception:
        return default


def safe_int(value, default=0):
    try:
        if pd.isna(value) or value is None or str(value).strip() == '':
            return default
        cleaned = re.sub(r'[^\d-]', '', str(value))
        return int(cleaned) if cleaned and cleaned != '-' else default
    except Exception:
        return default


def safe_bool(value, default=False):
    try:
        if pd.isna(value) or value is None:
            return default
        return str(value).strip().lower() in ('true', '1', 'yes', 'y', 't', 'premium')
    except Exception:
        return default


COLUMN_ALIASES = {
    'cover_image_url': 'image_url',
    'download_link':   'download_url',
}


def load_file(path):
    """Load Excel or CSV into a normalised DataFrame."""
    if path.endswith('.csv'):
        df = pd.read_csv(path)
    elif path.endswith(('.xlsx', '.xls')):
        df = pd.read_excel(path)
    else:
        raise ValueError("Unsupported format — use .xlsx, .xls, or .csv")
    df.columns = df.columns.str.strip().str.lower()
    df = df.fillna('')

    # ── Normalise alternate column names ──────────────────────────────────
    df.rename(columns={k: v for k, v in COLUMN_ALIASES.items()
                       if k in df.columns}, inplace=True)

    # If 'article' column has rich descriptions, prefer it over short 'description'
    if 'article' in df.columns:
        for idx, row in df.iterrows():
            article = str(row.get('article', '')).strip()
            if article:
                df.at[idx, 'description'] = article
        df.drop(columns=['article'], inplace=True, errors='ignore')

    # Extract year from 'release_date' if 'year' column is missing
    if 'release_date' in df.columns and 'year' not in df.columns:
        def extract_year(val):
            s = str(val).strip()
            if not s:
                return ''
            # "2010-11-02 00:00:00" → "2010"
            match = re.search(r'(\d{4})', s)
            return match.group(1) if match else ''
        df['year'] = df['release_date'].apply(extract_year)
        df.drop(columns=['release_date'], inplace=True, errors='ignore')

    return df


def parse_row(row):
    """Extract all content fields from a row dict."""
    return {
        'priority':     safe_int(row.get('priority', 0)),
        'description':  safe_str(row.get('description', '')),
        'image_url':    safe_str(row.get('image_url', '')),
        'size':         '',  # ignored — not imported from sheet
        'download_url': safe_str(row.get('download_url', '')),
        'game_url':     safe_str(row.get('game_url', '')),
        'video_url':    safe_str(row.get('video_url', '')),
        'region':       safe_str(row.get('region', '')),
        'is_premium':   safe_bool(row.get('is_premium', False)),
        'year':         safe_str(row.get('year', '')),
        'genres': [
            g.strip()
            for g in safe_str(row.get('genres', '')).split(',')
            if g.strip()
        ],
        'images': [
            safe_str(row.get(f'image_{n}', ''))
            for n in range(1, 6)
            if safe_str(row.get(f'image_{n}', ''))
        ],
    }


def sync_images(game, image_urls):
    """Replace additional screenshots for a game."""
    game.images.all().delete()
    for order, url in enumerate(image_urls, start=1):
        GameImage.objects.create(game=game, image_path=url, order=order)


def sync_genres(game, genre_names):
    """Replace genres for a game."""
    genre_objects = [
        Genre.objects.get_or_create(name=name)[0]
        for name in genre_names
    ]
    game.genres.set(genre_objects)


# ── Main logic ────────────────────────────────────────────────────────────────

def run():
    print("\n" + "=" * 60)
    print("  GAME IMPORT / UPDATE SCRIPT")
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

    rows = df.to_dict(orient='records')
    print(f"\n✓ Loaded {len(rows)} rows from: {os.path.basename(file_path)}")
    print(f"✓ Columns: {', '.join(df.columns.tolist())}\n")

    # 4. Process each row
    created = updated = skipped = errors = 0

    for i, row in enumerate(rows, 1):
        title = safe_str(row.get('game_name', ''))
        if not title:
            print(f"  ⊖ Row {i}: Skipped — no game_name")
            skipped += 1
            continue

        data = parse_row(row)

        try:
            existing = Game.objects.filter(
                title__iexact=title,
                emulator=emulator,
            ).first()

            if existing is None:
                # ── CREATE ────────────────────────────────────────────────────
                game = Game.objects.create(
                    title=title,
                    emulator=emulator,
                    priority=data['priority'],
                    description=data['description'],
                    image_url=data['image_url'],
                    size=data['size'],
                    download_url=data['download_url'],
                    game_url=data['game_url'],
                    video_url=data['video_url'],
                    region=data['region'],
                    is_premium=data['is_premium'],
                    year=data['year'],
                    # views/downloads default to 0 automatically
                )
                if data['genres']:
                    sync_genres(game, data['genres'])
                if data['images']:
                    sync_images(game, data['images'])

                tags = []
                if data['is_premium']:
                    tags.append('PREMIUM')
                if data['priority']:
                    tags.append(f"priority={data['priority']}")
                tag_str = f"  [{', '.join(tags)}]" if tags else ''
                img_str = f"  (+{len(data['images'])} images)" if data['images'] else ''
                print(f"  ✅ Row {i}: CREATED  '{title}'{tag_str}{img_str}")
                created += 1

            else:
                # ── UPDATE (content only — never touch stats) ─────────────────
                changed_fields = []

                for field in CONTENT_FIELDS:
                    new_val = data[field]
                    old_val = getattr(existing, field)
                    if new_val != old_val:
                        setattr(existing, field, new_val)
                        changed_fields.append(field)

                if changed_fields:
                    existing.save(update_fields=changed_fields)

                if data['genres']:
                    sync_genres(existing, data['genres'])
                if data['images']:
                    sync_images(existing, data['images'])
                    changed_fields.append(f"{len(data['images'])} images")

                if changed_fields:
                    print(f"  ♻️  Row {i}: UPDATED  '{title}'  [{', '.join(changed_fields)}]"
                          f"  (views={existing.views}, downloads={existing.downloads} preserved)")
                else:
                    print(f"  —  Row {i}: NO CHANGE '{title}'  (already up to date)")
                updated += 1

        except Exception as e:
            print(f"  ✗ Row {i}: ERROR on '{title}' — {e}")
            errors += 1

    # 5. Summary
    print("\n" + "=" * 60)
    print("  SUMMARY")
    print("=" * 60)
    print(f"  Emulator  : {emulator.name}")
    print(f"  File      : {os.path.basename(file_path)}")
    print(f"  Rows      : {len(rows)}")
    print(f"  ✅ Created : {created}")
    print(f"  ♻️  Updated : {updated}")
    print(f"  ⊖  Skipped : {skipped}")
    print(f"  ✗  Errors  : {errors}")
    total = Game.objects.filter(emulator=emulator).count()
    print(f"\n  Total games for '{emulator.name}' in DB: {total}")
    print("=" * 60)


if __name__ == '__main__':
    run()
