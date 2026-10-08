"""
Script to purge ALL data from the database except superuser account(s).
Creates backups before deletion and requires confirmation.

WARNING: This will delete:
- All games, emulators, genres
- All device tokens, notifications, notification logs
- All user accounts (except superusers)
- All reviews, ratings, loves, images, files
- All support messages, payments, subscriptions

Run with: python3 manage.py shell < scripts/purge_all_data_keep_superuser.py
Or: python3 scripts/purge_all_data_keep_superuser.py (if configured as standalone)
"""

import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gamezone.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.core import serializers
from django.utils import timezone
from django.db import connection

User = get_user_model()

BACKUP_DIR = '/tmp/db_backups'
TIMESTAMP = timezone.now().strftime('%Y%m%d_%H%M%S')


def create_backup():
    """Create full database backup."""
    os.makedirs(BACKUP_DIR, exist_ok=True)
    
    print(f"\n{'='*60}")
    print("CREATING BACKUPS...")
    print(f"{'='*60}\n")
    
    # Import all models
    from games.models import (
        Game, Emulator, Genre, GameRating, GameImage, GameAdditionalFile,
        EmulatorAdditionalFile, GameReview, GameLove, AppSettings
    )
    from notifications.models import DeviceToken, Notification, NotificationLog
    from support.models import SupportMessage
    
    models_to_backup = [
        ('users', User.objects.all()),
        ('games', Game.objects.all()),
        ('emulators', Emulator.objects.all()),
        ('genres', Genre.objects.all()),
        ('game_ratings', GameRating.objects.all()),
        ('game_images', GameImage.objects.all()),
        ('game_additional_files', GameAdditionalFile.objects.all()),
        ('emulator_additional_files', EmulatorAdditionalFile.objects.all()),
        ('game_reviews', GameReview.objects.all()),
        ('game_loves', GameLove.objects.all()),
        ('app_settings', AppSettings.objects.all()),
        ('device_tokens', DeviceToken.objects.all()),
        ('notifications', Notification.objects.all()),
        ('notification_logs', NotificationLog.objects.all()),
        ('support_messages', SupportMessage.objects.all()),
    ]
    
    backup_files = []
    for name, queryset in models_to_backup:
        count = queryset.count()
        if count > 0:
            filename = os.path.join(BACKUP_DIR, f'{name}_backup_{TIMESTAMP}.json')
            with open(filename, 'w') as f:
                serializers.serialize('json', queryset, stream=f, indent=2)
            backup_files.append(filename)
            print(f"✓ Backed up {count} {name} to {filename}")
        else:
            print(f"⊘ Skipped {name} (empty)")
    
    print(f"\n{'='*60}")
    print(f"BACKUPS COMPLETED: {len(backup_files)} files created")
    print(f"Location: {BACKUP_DIR}")
    print(f"{'='*60}\n")
    
    return backup_files


def show_summary():
    """Show what will be deleted."""
    from games.models import (
        Game, Emulator, Genre, GameRating, GameImage, GameAdditionalFile,
        EmulatorAdditionalFile, GameReview, GameLove, AppSettings
    )
    from notifications.models import DeviceToken, Notification, NotificationLog
    from support.models import SupportMessage
    
    superusers = User.objects.filter(is_superuser=True)
    regular_users = User.objects.filter(is_superuser=False)
    
    print(f"\n{'='*60}")
    print("DATABASE PURGE SUMMARY")
    print(f"{'='*60}\n")
    
    print("WILL BE KEPT:")
    print(f"  ✓ Superuser accounts: {superusers.count()}")
    for su in superusers:
        print(f"    - {su.email} (id={su.id})")
    
    print("\n" + "="*60)
    print("WILL BE DELETED:")
    print(f"  ✗ Regular users: {regular_users.count()}")
    print(f"  ✗ Games: {Game.objects.count()}")
    print(f"  ✗ Emulators: {Emulator.objects.count()}")
    print(f"  ✗ Genres: {Genre.objects.count()}")
    print(f"  ✗ Game ratings: {GameRating.objects.count()}")
    print(f"  ✗ Game images: {GameImage.objects.count()}")
    print(f"  ✗ Game additional files: {GameAdditionalFile.objects.count()}")
    print(f"  ✗ Emulator additional files: {EmulatorAdditionalFile.objects.count()}")
    print(f"  ✗ Game reviews: {GameReview.objects.count()}")
    print(f"  ✗ Game loves: {GameLove.objects.count()}")
    print(f"  ✗ Device tokens: {DeviceToken.objects.count()}")
    print(f"  ✗ Notifications: {Notification.objects.count()}")
    print(f"  ✗ Notification logs: {NotificationLog.objects.count()}")
    print(f"  ✗ Support messages: {SupportMessage.objects.count()}")
    print(f"  ✗ App settings: {AppSettings.objects.count()}")
    print(f"{'='*60}\n")


def purge_data():
    """Delete all data except superusers."""
    from games.models import (
        Game, Emulator, Genre, GameRating, GameImage, GameAdditionalFile,
        EmulatorAdditionalFile, GameReview, GameLove, AppSettings
    )
    from notifications.models import DeviceToken, Notification, NotificationLog
    from support.models import SupportMessage
    
    print(f"\n{'='*60}")
    print("STARTING DATA PURGE...")
    print(f"{'='*60}\n")
    
    deleted_counts = {}
    
    # Delete in order to respect foreign key constraints
    print("Deleting game-related data...")
    deleted_counts['game_loves'] = GameLove.objects.all().delete()[0]
    deleted_counts['game_reviews'] = GameReview.objects.all().delete()[0]
    deleted_counts['game_ratings'] = GameRating.objects.all().delete()[0]
    deleted_counts['game_images'] = GameImage.objects.all().delete()[0]
    deleted_counts['game_additional_files'] = GameAdditionalFile.objects.all().delete()[0]
    deleted_counts['games'] = Game.objects.all().delete()[0]
    
    print("Deleting emulator-related data...")
    deleted_counts['emulator_additional_files'] = EmulatorAdditionalFile.objects.all().delete()[0]
    deleted_counts['emulators'] = Emulator.objects.all().delete()[0]
    deleted_counts['genres'] = Genre.objects.all().delete()[0]
    
    print("Deleting notification data...")
    deleted_counts['notifications'] = Notification.objects.all().delete()[0]
    deleted_counts['notification_logs'] = NotificationLog.objects.all().delete()[0]
    deleted_counts['device_tokens'] = DeviceToken.objects.all().delete()[0]
    
    print("Deleting support messages...")
    deleted_counts['support_messages'] = SupportMessage.objects.all().delete()[0]
    
    print("Deleting app settings...")
    deleted_counts['app_settings'] = AppSettings.objects.all().delete()[0]
    
    print("Deleting regular user accounts...")
    deleted_counts['regular_users'] = User.objects.filter(is_superuser=False).delete()[0]
    
    print(f"\n{'='*60}")
    print("DELETION SUMMARY:")
    print(f"{'='*60}")
    for key, count in deleted_counts.items():
        print(f"  ✗ {key}: {count} deleted")
    print(f"{'='*60}\n")
    
    # Verify superusers still exist
    remaining_superusers = User.objects.filter(is_superuser=True)
    print(f"✓ Verified: {remaining_superusers.count()} superuser(s) remain in database")
    for su in remaining_superusers:
        print(f"  - {su.email}")
    
    print(f"\n{'='*60}")
    print("DATABASE PURGE COMPLETE!")
    print(f"{'='*60}\n")


def main():
    """Main execution flow."""
    print("\n" + "="*60)
    print("DATABASE PURGE TOOL")
    print("="*60)
    print("This will DELETE ALL DATA except superuser accounts!")
    print("Backups will be created first.")
    print("="*60 + "\n")
    
    # Check if superusers exist
    superusers = User.objects.filter(is_superuser=True)
    if not superusers.exists():
        print("ERROR: No superuser accounts found in database!")
        print("Cannot proceed - at least one superuser must exist.")
        return
    
    # Show summary
    show_summary()
    
    # Confirm
    confirm = input("\nType 'DELETE ALL DATA' to proceed (or anything else to cancel): ")
    if confirm != "DELETE ALL DATA":
        print("\n✗ Operation cancelled. No changes made.")
        return
    
    # Create backups
    backup_files = create_backup()
    
    # Final confirmation
    confirm2 = input("\nBackups created. Type 'YES' to proceed with deletion: ")
    if confirm2 != "YES":
        print("\n✗ Operation cancelled. Backups are saved but no data was deleted.")
        return
    
    # Purge data
    purge_data()
    
    print(f"\nBackups are stored in: {BACKUP_DIR}")
    print("You can restore data from these JSON files if needed.")


if __name__ == '__main__':
    main()
