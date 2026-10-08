# Database Purge - Ready to Execute

## Current Status ✅

All tools are installed and tested. The database contains:

### WILL BE KEPT:
- ✅ **Superuser account**: agames.app.dev@gmail.com (id=2)

### WILL BE DELETED:
- ❌ Regular users: **9**
- ❌ Games: **2,006**
- ❌ Emulators: **12**
- ❌ Genres: **47**
- ❌ Game ratings: **24**
- ❌ Game images: **7**
- ❌ Game reviews: **23**
- ❌ Game loves: **17**
- ❌ Device tokens: **0**
- ❌ Notifications: **40**
- ❌ Notification logs: **2,053**
- ❌ Support messages: **15**
- ❌ App settings: **1**

## How to Execute the Purge

### Step 1: Review (Already Done ✅)
```bash
cd /root/game
source venv/bin/activate
python manage.py purge_all_data
```

### Step 2: Execute the Purge
```bash
cd /root/game
source venv/bin/activate
python manage.py purge_all_data --confirm
```

This will:
1. ✅ Create JSON backups in `/tmp/db_backups/`
2. ✅ Delete all data except superuser
3. ✅ Show deletion summary
4. ✅ Verify superuser still exists

### Step 3: Verify Backups
```bash
ls -lh /tmp/db_backups/
```

### Step 4: Disable Automatic Notifications (Optional)
```bash
cd /root/game
source venv/bin/activate
python manage.py shell
```

Then in the shell:
```python
from games.models import AppSettings

# Get or create app settings
settings = AppSettings.objects.first()
if not settings:
    settings = AppSettings.objects.create()

# Disable automatic notifications
settings.disable_automatic_notifications = True
settings.save()

print("✓ Automatic notifications disabled")
exit()
```

## What Happens After Purge

Your database will contain:
- ✅ 1 superuser account (agames.app.dev@gmail.com)
- ✅ No games or emulators
- ✅ No regular users
- ✅ No notifications
- ✅ Clean slate to start fresh

## Safety Features Implemented

1. ✅ **Backups**: Full JSON exports before deletion
2. ✅ **Dry run**: Default mode shows what will be deleted
3. ✅ **Confirmation required**: Must use `--confirm` flag
4. ✅ **Superuser protection**: Cannot delete if no superuser exists
5. ✅ **Notification control**: Can disable automatic notifications via AppSettings

## Alternative: Skip Backups (Not Recommended)

If you're absolutely sure and want to skip backup creation:
```bash
python manage.py purge_all_data --confirm --skip-backup
```

## Restoring from Backup

If you need to restore later:
```bash
# Find your backup timestamp
ls /tmp/db_backups/

# Restore specific data (replace timestamp with yours)
python manage.py loaddata /tmp/db_backups/games_backup_20251210_*.json
python manage.py loaddata /tmp/db_backups/users_backup_20251210_*.json
```

## Files Created

1. `/root/game/games/management/commands/purge_all_data.py` - Django management command
2. `/root/game/scripts/purge_all_data_keep_superuser.py` - Standalone Python script
3. `/root/game/docs/DATABASE_PURGE_GUIDE.md` - Full documentation
4. `/root/game/games/models.py` - Added `disable_automatic_notifications` field to AppSettings
5. `/root/game/notifications/signals.py` - Updated all signal handlers to respect the toggle
6. `/root/game/games/migrations/0028_appsettings_disable_automatic_notifications.py` - Database migration (applied ✅)

## Need Help?

See full documentation: `/root/game/docs/DATABASE_PURGE_GUIDE.md`

---

**⚠️ IMPORTANT**: Once you run with `--confirm`, the data will be deleted. Make sure you're ready!

**✅ READY TO GO**: Just run the command when you're ready to purge the database.
