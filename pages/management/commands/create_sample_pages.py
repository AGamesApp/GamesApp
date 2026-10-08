from django.core.management.base import BaseCommand
from pages.models import Page


class Command(BaseCommand):
    help = 'Creates sample pages (about, help, support) for testing'

    def handle(self, *args, **options):
        pages_data = [
            {
                'title': 'about',
                'content': '''
                    <h1>About AGames</h1>
                    <p>Welcome to <strong>AGames</strong>, your ultimate destination for retro gaming!</p>
                    <p>We provide a comprehensive collection of classic games and emulators, bringing back the nostalgia of gaming's golden age.</p>
                    
                    <h2>Our Mission</h2>
                    <p>To preserve and celebrate the history of video games by making classic titles accessible to everyone.</p>
                    
                    <h2>What We Offer</h2>
                    <ul>
                        <li>Extensive library of retro games</li>
                        <li>Multiple emulator support</li>
                        <li>Easy-to-use platform</li>
                        <li>Regular updates and new additions</li>
                    </ul>
                '''
            },
            {
                'title': 'help',
                'content': '''
                    <h1>Help Center</h1>
                    <p>Need assistance? We're here to help!</p>
                    
                    <h2>Getting Started</h2>
                    <ol>
                        <li><strong>Browse Games:</strong> Explore our collection by genre or emulator</li>
                        <li><strong>Download:</strong> Select your favorite games and download them</li>
                        <li><strong>Play:</strong> Use the recommended emulator to enjoy your games</li>
                    </ol>
                    
                    <h2>Frequently Asked Questions</h2>
                    
                    <h3>How do I download a game?</h3>
                    <p>Click on any game card, then click the download button. Premium users get faster download speeds!</p>
                    
                    <h3>Which emulator should I use?</h3>
                    <p>Each game shows its recommended emulator. Make sure to download the emulator before playing.</p>
                    
                    <h3>Is this service free?</h3>
                    <p>We offer both free and premium memberships. Premium members enjoy ad-free experience and priority downloads.</p>
                '''
            },
            {
                'title': 'support',
                'content': '''
                    <h1>Contact Support</h1>
                    <p>We're here to help! If you're experiencing any issues, please reach out to us.</p>
                    
                    <h2>Support Channels</h2>
                    <ul>
                        <li><strong>Email:</strong> support@agames.com</li>
                        <li><strong>Response Time:</strong> Within 24-48 hours</li>
                        <li><strong>Hours:</strong> Monday - Friday, 9 AM - 6 PM EST</li>
                    </ul>
                    
                    <h2>Before Contacting Us</h2>
                    <p>Please check our <a href="/api/pages/help/">Help Center</a> for quick answers to common questions.</p>
                    
                    <h2>When Reporting Issues</h2>
                    <p>Please include:</p>
                    <ul>
                        <li>Your browser and operating system</li>
                        <li>Screenshots if applicable</li>
                        <li>Steps to reproduce the issue</li>
                        <li>Game or emulator name (if relevant)</li>
                    </ul>
                    
                    <p><em>We appreciate your patience and will get back to you as soon as possible!</em></p>
                '''
            }
        ]
        
        created_count = 0
        for page_data in pages_data:
            page, created = Page.objects.get_or_create(
                title=page_data['title'],
                defaults={'content': page_data['content']}
            )
            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f'✓ Created page: {page.title}'))
            else:
                self.stdout.write(self.style.WARNING(f'⚠ Page already exists: {page.title}'))
        
        self.stdout.write(self.style.SUCCESS(f'\n✓ Sample pages setup complete! Created {created_count} new pages.'))
