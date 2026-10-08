# 🎮 QUICK REFERENCE - Excel Import Columns

## ✅ REQUIRED (Must Have)
```
game_name    | Game title - REQUIRED
console      | Emulator/Console name - REQUIRED
```

## ⭐ OPTIONAL (Can Be Empty - Uses Defaults)

### Core Info
```
priority     | Number (higher appears first) - Default: 0
description  | Game description text - Default: empty
```

### Images (All as URLs/Links)
```
image_url    | Main cover image URL - Default: empty
image_1      | Screenshot #1 URL - Default: empty
image_2      | Screenshot #2 URL - Default: empty
image_3      | Screenshot #3 URL - Default: empty
image_4      | Screenshot #4 URL - Default: empty
image_5      | Screenshot #5 URL - Default: empty
```

### Game Details
```
size         | File size (e.g., "500 MB") - Default: empty
download_url | Download link URL - Default: empty
game_url     | Game page URL - Default: empty
video_url    | Video preview URL - Default: empty
region       | Region (USA, Europe, etc.) - Default: empty
year         | Release year - Default: empty
```

### Categories & Premium
```
genres       | Comma-separated (e.g., "Action, RPG") - Default: empty
is_premium   | true/false, 1/0, yes/no - Default: false
```

## 💡 Example Data

### Minimal (Required Only)
```
game_name          | console
-------------------|----------
Super Mario Bros   | NES
Sonic             | Genesis
```

### Full Example
```
game_name | console | priority | image_url | image_1 | image_2 | size | genres | is_premium | year
----------|---------|----------|-----------|---------|---------|------|--------|------------|------
Mario     | NES     | 100      | http://.. | http:// | http:// | 40KB | Action | true       | 1985
```

## 🚀 Quick Start

1. **Create Excel** with columns (at minimum: game_name, console)
2. **Upload to Google Sheets** → Share → "Anyone with link can view"
3. **Copy link**
4. **Run:** `python import_games.py`
5. **Select option 1** and paste link

## ✨ Key Features

- ✅ **Never crashes** - all errors caught and logged
- 🛡️ **Safe defaults** - empty cells = default values
- 📸 **5 images per game** - added as links to GameImage table
- 🔄 **Smart update** - creates new or updates existing
- 🏆 **Priority ordering** - higher priority = appears first

## 📝 Notes

- **Column names** are case-insensitive
- **Empty cells** are safe - uses defaults
- **Images** must be URLs (http:// or https://)
- **Emulators** are auto-created if not found
- **Genres** are auto-created if not found
- **is_premium**: accepts true/false/1/0/yes/no
- **priority**: higher number = appears first in lists

## 🛡️ Error Handling

| Issue | Result |
|-------|--------|
| Missing game_name | Row skipped |
| Missing console | Row skipped |
| Invalid number | Uses 0 |
| Invalid boolean | Uses false |
| Missing emulator | Auto-created |
| Error in row | Logged, continues with next |

---
See **IMPORT_GAMES_GUIDE.md** for detailed documentation
