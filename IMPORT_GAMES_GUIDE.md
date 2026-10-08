# 📊 Game Import Script - Complete Guide

## 🎯 Overview

The `import_games.py` script allows you to bulk import games from Excel/Google Sheets with **zero crashes** and **safe default values** for all empty cells.

## ✅ Features

- ✨ **Never crashes** - All errors are caught and logged
- 🛡️ **Safe defaults** - Empty cells automatically use sensible defaults
- 📸 **Multiple images** - Support for up to 5 additional screenshots per game
- 🔄 **Update or create** - Automatically updates existing games or creates new ones
- 🏆 **Priority support** - Control game ordering with priority field
- 📝 **Robust parsing** - Handles various formats for booleans, numbers, etc.

## 📋 Excel Column Specification

### ✅ REQUIRED Columns (must have):

| Column Name | Description | Example |
|-------------|-------------|---------|
| `game_name` | Game title | `Super Mario Bros` |
| `console` | Emulator/Console name | `NES` |

### ⭐ OPTIONAL Columns (can be empty):

| Column Name | Description | Default | Example |
|-------------|-------------|---------|---------|
| `priority` | Display order (higher = first) | `0` | `100` |
| `description` | Game description text | `''` | `Classic platformer game` |
| `image_url` | Main game cover image URL | `''` | `https://example.com/mario.jpg` |
| `image_1` | Additional screenshot #1 | `''` | `https://example.com/shot1.jpg` |
| `image_2` | Additional screenshot #2 | `''` | `https://example.com/shot2.jpg` |
| `image_3` | Additional screenshot #3 | `''` | `https://example.com/shot3.jpg` |
| `image_4` | Additional screenshot #4 | `''` | `https://example.com/shot4.jpg` |
| `image_5` | Additional screenshot #5 | `''` | `https://example.com/shot5.jpg` |
| `size` | File size | `''` | `500 MB` |
| `download_url` | Download link | `''` | `https://example.com/download` |
| `game_url` | Game page URL | `''` | `https://example.com/game` |
| `video_url` | Video preview URL | `''` | `https://youtube.com/video` |
| `region` | Game region | `''` | `USA`, `Europe`, `Japan` |
| `genres` | Comma-separated genres | `''` | `Action, Platform, RPG` |
| `is_premium` | Premium status | `false` | `true`, `false`, `1`, `0`, `yes`, `no` |
| `year` | Release year | `''` | `1985` |

## 📝 Excel Template

### Minimal Template (only required fields):

```
game_name          | console
-------------------|---------
Super Mario Bros   | NES
Sonic the Hedgehog | Genesis
```

### Full Template (all fields):

```
game_name | console | priority | description | image_url | image_1 | image_2 | size | download_url | game_url | video_url | region | genres | is_premium | year
```

**A sample Excel file is available:** `games_import_template.xlsx`

## 🚀 How to Use

### Step 1: Prepare Your Excel File

1. Create an Excel file with the column headers
2. Add your game data (at least `game_name` and `console`)
3. Leave any optional fields empty if you don't have the data

### Step 2: Upload to Google Sheets

1. Go to [Google Sheets](https://sheets.google.com/)
2. Upload your Excel file (File → Import → Upload)
3. Click "Share" button
4. Set to **"Anyone with the link can view"**
5. Copy the share link

### Step 3: Run Import Script

```bash
cd /root/game
source venv/bin/activate
python import_games.py
```

### Step 4: Select Option 1 and Paste Link

```
Select option (1-4): 1
Paste your Google Sheet link here: [paste your link]
```

The script will:
- ✅ Download and read your sheet
- ✅ Create or update games
- ✅ Add images to GameImage table
- ✅ Create genres if they don't exist
- ✅ Create emulators if they don't exist
- ✅ Show detailed progress and summary

## 💡 Tips & Best Practices

### Priority Field
- Higher numbers appear first in lists
- Use `100` for featured games, `50` for normal, `0` for default
- Negative numbers are allowed (will appear last)

### Images
- `image_url`: Main cover image for the game
- `image_1` to `image_5`: Additional screenshots stored in `GameImage` table
- All images must be valid URLs starting with `http://` or `https://`
- Empty image fields are skipped (no errors)

### Boolean Fields (is_premium)
Accepts any of these values:
- ✅ True: `true`, `True`, `1`, `yes`, `YES`, `premium`, `y`, `t`
- ❌ False: `false`, `False`, `0`, `no`, `NO`, `n`, `f`, empty

### Genres
- Use comma-separated values: `Action, RPG, Platform`
- Spaces are trimmed automatically
- Genres are created if they don't exist

### Emulators
- If emulator doesn't exist, it will be created automatically
- Emulator names are case-insensitive for matching

## 🛡️ Error Handling

The script is designed to **never crash**:

| Error Type | Behavior |
|------------|----------|
| Missing required field | Row is skipped, logged in summary |
| Invalid number | Uses default value (0) |
| Invalid boolean | Uses default value (false) |
| Invalid URL | Saved as-is (validated later by Django) |
| Missing emulator | Created automatically |
| Missing genre | Created automatically |
| Database error | Row is skipped, error logged, continues with next row |

## 📊 Output Example

```
📊 Processing File ID: abc123...
✓ Successfully accessed the file!
✓ Found 100 rows in the sheet
✓ Columns detected: game_name, console, priority, image_url, image_1, image_2

✓ Row 1: Created 'Super Mario Bros' (NES) [Priority: 100] (+2 images)
↻ Row 2: Updated 'Sonic' (Genesis) [Priority: 90] [PREMIUM] (+3 images)
⊖ Row 3: Skipped (no game_name provided)
✗ Row 4: Error - Database connection failed

============================================================
📈 IMPORT SUMMARY
============================================================
Total rows processed: 100
✓ Created: 85
↻ Updated: 10
⊖ Skipped: 4
✗ Errors: 1
📸 Images added: 250
============================================================

📦 Total Games in Database: 2,500
```

## 🧪 Testing

Run the test script to verify everything works:

```bash
cd /root/game
source venv/bin/activate
python test_import_games.py
```

## 📦 Database Structure

### Game Table
- Main game information (title, description, priority, etc.)
- One main `image_url` for the cover

### GameImage Table
- Multiple images per game
- Images from `image_1` to `image_5` columns
- Each with an `order` field for sorting
- Supports both URLs (`image_path`) and uploaded files (`image_file`)

### Genre Table
- Many-to-many relationship with games
- Auto-created from `genres` column

### Emulator Table
- Foreign key in Game
- Auto-created if not found

## 🔧 Advanced Usage

### View All Games
```bash
python import_games.py
# Select option 2
```

### Show Statistics
```bash
python import_games.py
# Select option 3
```

### Re-import (Update)
- Re-running import with the same games will **update** them
- Uses `game_name` + `console` as unique key
- All fields are updated with new values

## ❓ Troubleshooting

### "Could not access the file"
- Make sure Google Sheet is set to "Anyone with the link can view"
- Check if the link is a valid Google Sheets URL
- Try exporting as CSV and re-uploading

### "Skipped rows"
- Check if `game_name` and `console` columns exist
- Make sure column names match exactly (case-insensitive)
- Check for typos in column headers

### "Images not added"
- Verify URLs are valid (start with http:// or https://)
- Check if URLs are accessible
- Images are added to GameImage table, not the main image_url field

### "Emulator not found"
- Script auto-creates emulators, so this shouldn't happen
- If it does, check database permissions

## 📞 Support

For issues or questions:
1. Check the error message in the terminal
2. Review this guide
3. Run `python test_import_games.py` to verify setup
4. Check Django logs in `/root/game/logs/`

---

**Last Updated:** December 22, 2025
**Script Version:** 2.0 (Robust Edition)
