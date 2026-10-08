from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from django.core import serializers
from django.utils import timezone
import os

User = get_user_model()

BACKUP_DIR = '/tmp/db_backups'


class Command(BaseCommand):
    help = 'Purge ALL data from database except superuser accounts. Creates backups first.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--confirm',
            action='store_true',
            help='Actually perform the deletion (required)',
        )
        parser.add_argument(
            '--skip-backup',
            action='store_true',
            help='Skip backup creation (NOT RECOMMENDED)',
        )

    def handle(self, *args, **options):
        confirm = options['confirm']
        skip_backup = options['skip_backup']
        timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')

        # Import all models
        from games.models import (
            Game, Emulator, Genre, GameRating, GameImage, GameAdditionalFile,
            EmulatorAdditionalFile, GameReview, GameLove, AppSettings
        )
        from notifications.models import DeviceToken, Notification, NotificationLog
        from support.models import SupportMessage

        # Check superusers exist
        superusers = User.objects.filter(is_superuser=True)
        if not superusers.exists():
            raise CommandError('No superuser accounts found! Cannot proceed.')

        self.stdout.write(self.style.WARNING('='*60))
        self.stdout.write(self.style.WARNING('DATABASE PURGE - WILL DELETE ALL DATA'))
        self.stdout.write(self.style.WARNING('='*60))

        # Show what will be kept
        self.stdout.write(self.style.SUCCESS('\nWILL BE KEPT:'))
        self.stdout.write(f'  ✓ Superuser accounts: {superusers.count()}')
        for su in superusers:
            self.stdout.write(f'    - {su.email} (id={su.id})')

        # Show what will be deleted
        regular_users = User.objects.filter(is_superuser=False)
        self.stdout.write(self.style.ERROR('\nWILL BE DELETED:'))
        self.stdout.write(f'  ✗ Regular users: {regular_users.count()}')
        self.stdout.write(f'  ✗ Games: {Game.objects.count()}')
        self.stdout.write(f'  ✗ Emulators: {Emulator.objects.count()}')
        self.stdout.write(f'  ✗ Genres: {Genre.objects.count()}')
        self.stdout.write(f'  ✗ Game ratings: {GameRating.objects.count()}')
        self.stdout.write(f'  ✗ Game images: {GameImage.objects.count()}')
        self.stdout.write(f'  ✗ Game additional files: {GameAdditionalFile.objects.count()}')
        self.stdout.write(f'  ✗ Emulator additional files: {EmulatorAdditionalFile.objects.count()}')
        self.stdout.write(f'  ✗ Game reviews: {GameReview.objects.count()}')
        self.stdout.write(f'  ✗ Game loves: {GameLove.objects.count()}')
        self.stdout.write(f'  ✗ Device tokens: {DeviceToken.objects.count()}')
        self.stdout.write(f'  ✗ Notifications: {Notification.objects.count()}')
        self.stdout.write(f'  ✗ Notification logs: {NotificationLog.objects.count()}')
        self.stdout.write(f'  ✗ Support messages: {SupportMessage.objects.count()}')
        self.stdout.write(f'  ✗ App settings: {AppSettings.objects.count()}')

        if not confirm:
            self.stdout.write(self.style.WARNING('\n⚠️  Dry run mode. Add --confirm to actually delete.'))
            return

        # Create backups
        if not skip_backup:
            self.stdout.write(self.style.NOTICE(f'\n{"="*60}'))
            self.stdout.write(self.style.NOTICE('CREATING BACKUPS...'))
            self.stdout.write(self.style.NOTICE(f'{"="*60}\n'))

            os.makedirs(BACKUP_DIR, exist_ok=True)

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
                    filename = os.path.join(BACKUP_DIR, f'{name}_backup_{timestamp}.json')
                    with open(filename, 'w') as f:
                        serializers.serialize('json', queryset, stream=f, indent=2)
                    backup_files.append(filename)
                    self.stdout.write(f'✓ Backed up {count} {name}')

            self.stdout.write(self.style.SUCCESS(f'\n✓ Created {len(backup_files)} backup files in {BACKUP_DIR}'))

        # Delete data
        self.stdout.write(self.style.ERROR(f'\n{"="*60}'))
        self.stdout.write(self.style.ERROR('STARTING DATA DELETION...'))
        self.stdout.write(self.style.ERROR(f'{"="*60}\n'))

        deleted_counts = {}

        self.stdout.write('Deleting game-related data...')
        deleted_counts['game_loves'] = GameLove.objects.all().delete()[0]
        deleted_counts['game_reviews'] = GameReview.objects.all().delete()[0]
        deleted_counts['game_ratings'] = GameRating.objects.all().delete()[0]
        deleted_counts['game_images'] = GameImage.objects.all().delete()[0]
        deleted_counts['game_additional_files'] = GameAdditionalFile.objects.all().delete()[0]
        deleted_counts['games'] = Game.objects.all().delete()[0]

        self.stdout.write('Deleting emulator-related data...')
        deleted_counts['emulator_additional_files'] = EmulatorAdditionalFile.objects.all().delete()[0]
        deleted_counts['emulators'] = Emulator.objects.all().delete()[0]
        deleted_counts['genres'] = Genre.objects.all().delete()[0]

        self.stdout.write('Deleting notification data...')
        deleted_counts['notifications'] = Notification.objects.all().delete()[0]
        deleted_counts['notification_logs'] = NotificationLog.objects.all().delete()[0]
        deleted_counts['device_tokens'] = DeviceToken.objects.all().delete()[0]

        self.stdout.write('Deleting support messages...')
        deleted_counts['support_messages'] = SupportMessage.objects.all().delete()[0]

        self.stdout.write('Deleting app settings...')
        deleted_counts['app_settings'] = AppSettings.objects.all().delete()[0]

        self.stdout.write('Deleting regular user accounts...')
        deleted_counts['regular_users'] = User.objects.filter(is_superuser=False).delete()[0]

        self.stdout.write(self.style.SUCCESS(f'\n{"="*60}'))
        self.stdout.write(self.style.SUCCESS('DELETION SUMMARY:'))
        self.stdout.write(self.style.SUCCESS(f'{"="*60}'))
        for key, count in deleted_counts.items():
            self.stdout.write(f'  ✗ {key}: {count} deleted')

        # Verify superusers remain
        remaining_superusers = User.objects.filter(is_superuser=True)
        self.stdout.write(self.style.SUCCESS(f'\n✓ Verified: {remaining_superusers.count()} superuser(s) remain'))
        for su in remaining_superusers:
            self.stdout.write(f'  - {su.email}')

        self.stdout.write(self.style.SUCCESS(f'\n{"="*60}'))
        self.stdout.write(self.style.SUCCESS('DATABASE PURGE COMPLETE!'))
        self.stdout.write(self.style.SUCCESS(f'{"="*60}'))

        if not skip_backup:
            self.stdout.write(f'\nBackups stored in: {BACKUP_DIR}')
