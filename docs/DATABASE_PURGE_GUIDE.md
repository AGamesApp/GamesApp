# Database Purge Tools

## Overview
Tools to safely delete ALL data from the database while preserving superuser account(s).

⚠️ **WARNING**: These tools will DELETE ALL DATA except superuser accounts!
- All games, emulators, genres
- All user accounts (except superusers)
- All reviews, ratings, loves, images
- All notifications and device tokens
- All support messages
- All app settings

## What Gets Kept
- ✅ Superuser accounts (is_superuser=True)

## Tools Available

### Option 1: Django Management Command (Recommended)
```bash
# Dry run - see what would be deleted (no actual deletion)
python3 manage.py purge_all_data

# Actually delete with backups
python3 manage.py purge_all_data --confirm

# Delete without creating backups (NOT RECOMMENDED)
python3 manage.py purge_all_data --confirm --skip-backup
```

### Option 2: Standalone Python Script
```bash
# Interactive mode with confirmations
python3 scripts/purge_all_data_keep_superuser.py
```

## Safety Features

### 1. Backups Created First
Before any deletion, full JSON backups are created in `/tmp/db_backups/` with timestamps:
- `users_backup_YYYYMMDD_HHMMSS.json`
- `games_backup_YYYYMMDD_HHMMSS.json`
- `emulators_backup_YYYYMMDD_HHMMSS.json`
- etc.

### 2. Multiple Confirmations
The standalone script requires:
1. Type `DELETE ALL DATA` to proceed
2. Type `YES` to confirm after backups

The management command requires:
- `--confirm` flag to actually delete (otherwise dry run)

### 3. Superuser Check
Will not run if no superuser accounts exist in the database.

## Usage Example

```bash
# Step 1: Check what will be deleted (dry run)
python3 manage.py purge_all_data

# Output will show:
# WILL BE KEPT:
#   ✓ Superuser accounts: 1
#     - admin@example.com (id=1)
#
# WILL BE DELETED:
#   ✗ Regular users: 45
#   ✗ Games: 1234
#   ✗ Emulators: 15
#   ... etc

# Step 2: If you're sure, run with --confirm
python3 manage.py purge_all_data --confirm

# Step 3: Verify backups were created
ls -lh /tmp/db_backups/

# Step 4: Verify superuser still exists
python3 manage.py shell
>>> from django.contrib.auth import get_user_model
>>> User = get_user_model()
>>> User.objects.filter(is_superuser=True)
```

## Restoring from Backup

If you need to restore data from the JSON backups:

```bash
# Restore specific model
python3 manage.py loaddata /tmp/db_backups/games_backup_20251210_143022.json

# Or restore all backups
python3 manage.py loaddata /tmp/db_backups/*_backup_20251210_143022.json
```

## After Purge

The database will be clean with only:
- Superuser account(s)
- No games, emulators, or genres
- No regular users
- No notifications or device tokens
- No reviews, ratings, or loves

You can now:
1. Start fresh with new data
2. Import games from scratch
3. Let users register new accounts

## Disable Automatic Notifications

After purge, you may also want to disable automatic notifications:

```bash
python3 manage.py shell
```

```python
from games.models import AppSettings

# Create or get app settings
settings = AppSettings.objects.first()
if not settings:
    settings = AppSettings.objects.create(
        app_version='1.0.0',
        app_link='https://play.google.com/store/apps/details?id=your.package.name'
    )

# Disable automatic notifications
settings.disable_automatic_notifications = True
settings.save()

print("✓ Automatic notifications disabled")
```

## Troubleshooting

### Error: "No superuser accounts found"
Create a superuser first:
```bash
python3 manage.py createsuperuser
```

### Error: "Permission denied: /tmp/db_backups"
```bash
sudo mkdir -p /tmp/db_backups
sudo chmod 777 /tmp/db_backups
```

### Want to keep specific users (not just superusers)?
Edit the script to modify the user deletion query:
```python
# Instead of:
User.objects.filter(is_superuser=False).delete()

# Use something like:
User.objects.exclude(email__in=['admin@example.com', 'keep@example.com']).delete()
```

## Important Notes

1. **Backups are in JSON format** - they can be viewed and edited in a text editor
2. **Backup location**: `/tmp/db_backups/` (on Linux, /tmp may be cleared on reboot - move important backups elsewhere)
3. **Foreign key cascade**: Deletions respect Django's foreign key relationships
4. **No database dump**: These tools use Django's serialization, not SQL dumps
5. **Media files**: This does NOT delete uploaded media files (images, etc.) - only database records

## Related Commands

```bash
# See all available management commands
python3 manage.py help

# Create new superuser
python3 manage.py createsuperuser

# Check current user count
python3 manage.py shell -c "from django.contrib.auth import get_user_model; print(get_user_model().objects.count())"

# Check game count
python3 manage.py shell -c "from games.models import Game; print(Game.objects.count())"
```
