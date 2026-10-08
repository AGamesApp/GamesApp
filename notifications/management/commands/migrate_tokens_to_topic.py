"""
Django management command to migrate existing device tokens to FCM topic subscription.
This subscribes all active device tokens to the 'all_users' topic.

Usage:
    python manage.py migrate_tokens_to_topic
    python manage.py migrate_tokens_to_topic --dry-run
    python manage.py migrate_tokens_to_topic --batch-size 500
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from notifications.models import DeviceToken
from firebase_admin import messaging
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Subscribe all active device tokens to the all_users FCM topic'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be done without actually subscribing tokens',
        )
        parser.add_argument(
            '--batch-size',
            type=int,
            default=1000,
            help='Number of tokens to subscribe per batch (max 1000)',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        batch_size = min(options['batch_size'], 1000)  # FCM limit is 1000
        
        topic_name = 'all_users'
        
        self.stdout.write(self.style.WARNING('=' * 70))
        self.stdout.write(self.style.WARNING('FCM Topic Migration Script'))
        self.stdout.write(self.style.WARNING('=' * 70))
        
        if dry_run:
            self.stdout.write(self.style.NOTICE('\n🔍 DRY RUN MODE - No actual subscriptions will be made\n'))
        
        # Get all active device tokens
        active_tokens = DeviceToken.objects.filter(is_active=True)
        total_tokens = active_tokens.count()
        
        if total_tokens == 0:
            self.stdout.write(self.style.WARNING('⚠️  No active device tokens found.'))
            return
        
        self.stdout.write(f'📊 Found {total_tokens} active device tokens')
        self.stdout.write(f'📦 Batch size: {batch_size} tokens per batch')
        self.stdout.write(f'🎯 Target topic: {topic_name}\n')
        
        if dry_run:
            self.stdout.write(self.style.SUCCESS(f'✅ Would subscribe {total_tokens} tokens to topic "{topic_name}"'))
            self.stdout.write(self.style.NOTICE(f'   Estimated batches: {(total_tokens + batch_size - 1) // batch_size}'))
            return
        
        # Confirm before proceeding
        self.stdout.write(self.style.WARNING('⚠️  This will subscribe all tokens to the FCM topic.'))
        confirm = input('Do you want to continue? (yes/no): ')
        
        if confirm.lower() not in ['yes', 'y']:
            self.stdout.write(self.style.ERROR('❌ Migration cancelled.'))
            return
        
        self.stdout.write('\n🚀 Starting migration...\n')
        
        # Process tokens in batches
        tokens_list = list(active_tokens.values_list('token', flat=True))
        
        total_success = 0
        total_failed = 0
        batch_num = 0
        
        for i in range(0, len(tokens_list), batch_size):
            batch_num += 1
            batch_tokens = tokens_list[i:i + batch_size]
            
            self.stdout.write(f'Processing batch {batch_num} ({len(batch_tokens)} tokens)...', ending=' ')
            
            try:
                # Subscribe tokens to topic
                response = messaging.subscribe_to_topic(batch_tokens, topic_name)
                
                success_count = response.success_count
                failure_count = response.failure_count
                
                total_success += success_count
                total_failed += failure_count
                
                if failure_count > 0:
                    self.stdout.write(self.style.WARNING(f'⚠️  {success_count} succeeded, {failure_count} failed'))
                    
                    # Log failed tokens
                    for idx, error in enumerate(response.errors):
                        failed_token = batch_tokens[error.index]
                        self.stdout.write(
                            self.style.ERROR(f'   Failed token #{idx + 1}: {error.reason}')
                        )
                        
                        # Optionally deactivate tokens with permanent errors
                        if error.reason in ['INVALID_ARGUMENT', 'NOT_FOUND']:
                            DeviceToken.objects.filter(token=failed_token).update(is_active=False)
                            self.stdout.write(self.style.NOTICE(f'   Deactivated invalid token'))
                else:
                    self.stdout.write(self.style.SUCCESS(f'✅ {success_count} succeeded'))
                    
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'❌ Error: {str(e)}'))
                logger.error(f'Error subscribing batch {batch_num} to topic: {e}')
                total_failed += len(batch_tokens)
        
        # Summary
        self.stdout.write('\n' + '=' * 70)
        self.stdout.write(self.style.SUCCESS('📊 Migration Summary'))
        self.stdout.write('=' * 70)
        self.stdout.write(f'Total tokens processed: {total_tokens}')
        self.stdout.write(self.style.SUCCESS(f'✅ Successfully subscribed: {total_success}'))
        
        if total_failed > 0:
            self.stdout.write(self.style.ERROR(f'❌ Failed subscriptions: {total_failed}'))
        else:
            self.stdout.write(self.style.SUCCESS('🎉 All tokens successfully subscribed!'))
        
        success_rate = (total_success / total_tokens * 100) if total_tokens > 0 else 0
        self.stdout.write(f'Success rate: {success_rate:.2f}%')
        
        self.stdout.write('\n' + '=' * 70)
        self.stdout.write(self.style.SUCCESS('✅ Migration completed!'))
        self.stdout.write('=' * 70)
        
        # Next steps
        self.stdout.write('\n📝 Next Steps:')
        self.stdout.write('   1. Update your mobile apps to subscribe new users to the topic')
        self.stdout.write('   2. Use send_notification_to_all_users_topic() for future broadcasts')
        self.stdout.write('   3. Monitor notification delivery in Firebase Console\n')
