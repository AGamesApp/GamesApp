from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = 'Creates a test superuser for customadmin'

    def handle(self, *args, **options):
        email = 'admin@admin.com'
        password = 'admin123'
        username = 'admin'
        
        # Delete if exists
        User.objects.filter(email=email).delete()
        
        # Create new
        user = User.objects.create_superuser(
            email=email,
            username=username,
            password=password
        )
        
        self.stdout.write(self.style.SUCCESS(f'✓ Created superuser:'))
        self.stdout.write(f'  Email: {email}')
        self.stdout.write(f'  Password: {password}')
        self.stdout.write(f'  Username: {username}')
        self.stdout.write(f'\nLogin at: http://127.0.0.1:8000/customadmin/login/')
