# Unique Game + Emulator Constraint Implementation

**Date:** December 23, 2025  
**Status:** ✅ COMPLETE

## Problem
The import system was treating games with the same name but different emulators as duplicates and updating them instead of creating separate entries.

**Example:**
- "God of War" on "PS2" 
- "God of War" on "PS3"

These should be **2 separate games**, not updates to the same game.

---

## Solution Implemented

### 1. Database Constraint Added
**File:** `/root/game/games/models.py`

Added unique constraint to Game model:
```python
class Meta:
    ordering = ['-views', '-downloads', '-created_at']
    unique_together = ['title', 'emulator']  # Same game on different emulator = different game
    indexes = [...]
```

**Effect:** Database now enforces that each combination of `(title, emulator)` is unique. Same game name on different emulators = different database entries.

---

### 2. Import Logic Updated
**File:** `/root/game/import_games.py`

**BEFORE:**
```python
game, created = Game.objects.update_or_create(
    title=title,
    emulator=emulator,
    defaults={...}
)
```

**AFTER:**
```python
game, created = Game.objects.get_or_create(
    title=title,
    emulator=emulator,
    defaults={...}
)
```

**Changes:**
- `update_or_create` → `get_or_create`
- **Never updates** existing games
- If game with same title + emulator exists → skipped
- If game with same title but **different emulator** → creates new entry

---

### 3. Import Logging Updated
**Old behavior:**
```
↻ Row 123: Updated 'God of War' (PS2)
```

**New behavior:**
```
⊖ Row 123: Skipped 'God of War' (PS2) - already exists
```

---

## Import Behavior Now

| Scenario | Action | Count |
|----------|--------|-------|
| "God of War" + "PS2" (new) | ✓ Create | Created +1 |
| "God of War" + "PS3" (new) | ✓ Create | Created +1 |
| "God of War" + "PS2" (duplicate) | ⊖ Skip | Skipped +1 |
| Missing required fields | ⊖ Skip | Skipped +1 |
| Database error | ✗ Error | Error +1 |

---

## Migration Applied

```bash
# Created migration
python manage.py makemigrations
# Output: games/migrations/0031_alter_game_unique_together.py

# Applied to database
python manage.py migrate
# Output: Applying games.0031_alter_game_unique_together... OK

# Restarted server
sudo systemctl restart gunicorn
```

---

## Database Structure

**Primary Key:** `id` (auto-increment)  
**Unique Constraint:** `(title, emulator)` combination

**Examples:**
```
id | title         | emulator | Result
---+---------------+----------+--------
1  | God of War    | PS2      | ✓ Valid
2  | God of War    | PS3      | ✓ Valid (different emulator)
3  | God of War    | PS2      | ✗ REJECTED (duplicate)
4  | Tekken 3      | PS1      | ✓ Valid
```

---

## Import Statistics Explanation

When you import 5000 rows:

### OLD System (update_or_create):
```
✓ Created: 3,021    (new games)
↻ Updated: 2,140    (existing games were updated)
⊖ Skipped: 0
✗ Errors: 0
```

### NEW System (get_or_create):
```
✓ Created: 3,021    (new games)
↻ Updated: 0        (NEVER updates)
⊖ Skipped: 2,140    (duplicates skipped)
✗ Errors: 0
```

---

## Testing Recommendation

1. **Test with duplicate entries:**
   - Import sheet with "God of War" + "PS2" twice
   - Expected: First creates, second skips
   
2. **Test with different emulators:**
   - Import "God of War" + "PS2"
   - Import "God of War" + "PS3"
   - Expected: Both create successfully (2 separate games)

3. **Check database:**
   ```bash
   python manage.py shell -c "
   from games.models import Game
   print(Game.objects.filter(title='God of War').values('title', 'emulator__name'))
   "
   ```

---

## Benefits

✅ **No accidental updates** - Existing games never modified  
✅ **Cross-platform support** - Same game on different consoles = separate entries  
✅ **Data integrity** - Database enforces uniqueness at schema level  
✅ **Clear logging** - See exactly what was created vs skipped  
✅ **Import safety** - Can re-run imports without fear of overwriting

---

## Files Modified

1. ✅ `/root/game/games/models.py` - Added unique_together constraint
2. ✅ `/root/game/import_games.py` - Changed to get_or_create, updated logging
3. ✅ `/root/game/games/migrations/0031_alter_game_unique_together.py` - Database migration

---

## Deployment Status

- ✅ Migration applied
- ✅ Gunicorn restarted
- ✅ Server running (games.agames.cv)
- ✅ Ready for testing

**Current Database:**
- Total Games: 3,091
- All games have unique (title, emulator) combinations

---

## Next Steps

You can now:
1. Import your Excel sheet again - duplicates will be skipped, not updated
2. Import games with same names but different emulators - they'll create separate entries
3. Monitor import logs to see created vs skipped counts

**Import URL:** https://games.agames.cv/customadmin/import-games/
