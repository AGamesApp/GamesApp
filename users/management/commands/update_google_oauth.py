from django.core.management.base import BaseCommand
from allauth.socialaccount.models import SocialApp
from django.contrib.sites.models import Site


from decouple import config

class Command(BaseCommand):
    help = 'Update Google OAuth credentials'

    def handle(self, *args, **options):
        site = Site.objects.get_current()
        client_id = config('GOOGLE_CLIENT_ID', default='your-google-client-id')
        secret = config('GOOGLE_CLIENT_SECRET', default='your-google-client-secret')
        
        # Update or create Google Social App
        google_app, created = SocialApp.objects.get_or_create(
            provider='google',
            defaults={
                'name': 'Google',
                'client_id': client_id,
                'secret': secret,
            }
        )
        
        if not created:
            # Update existing app
            google_app.client_id = client_id
            google_app.secret = secret
            google_app.save()
            self.stdout.write(self.style.SUCCESS('✓ Google OAuth credentials updated'))
        else:
            self.stdout.write(self.style.SUCCESS('✓ Google OAuth app created'))
        
        # Add site to the app
        if site not in google_app.sites.all():
            google_app.sites.add(site)
            self.stdout.write(self.style.SUCCESS(f'✓ Added site: {site.domain}'))
        
        self.stdout.write(self.style.SUCCESS('\n=== Google OAuth Configuration ==='))
        self.stdout.write(f'Client ID: {google_app.client_id}')
        self.stdout.write(f'Email: agames.app.dev@gmail.com')
        self.stdout.write(f'Site: {site.domain}')
        self.stdout.write(self.style.SUCCESS('\n✓ Configuration complete!'))
