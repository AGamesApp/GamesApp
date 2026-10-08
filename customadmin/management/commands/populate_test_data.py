from django.core.management.base import BaseCommand
from django.utils import timezone
from games.models import Game, Emulator, Tag
import random


class Command(BaseCommand):
    help = 'Populates the database with test data: 50 games, 5 emulators, and 20 tags'

    def handle(self, *args, **options):
        self.stdout.write('Creating test data...\n')
        
        # Create Emulators
        emulators_data = [
            {'name': 'NES Emulator', 'description': 'Nintendo Entertainment System emulator for classic 8-bit games', 'icon': '🎮'},
            {'name': 'SNES Emulator', 'description': 'Super Nintendo emulator for 16-bit gaming', 'icon': '🕹️'},
            {'name': 'PlayStation Emulator', 'description': 'Sony PlayStation 1 emulator', 'icon': '🎯'},
            {'name': 'Game Boy Emulator', 'description': 'Nintendo Game Boy and Game Boy Color emulator', 'icon': '📱'},
            {'name': 'Arcade Emulator', 'description': 'MAME arcade machine emulator', 'icon': '🎰'},
        ]
        
        emulators = []
        for data in emulators_data:
            emulator, created = Emulator.objects.get_or_create(
                name=data['name'],
                defaults={'description': data['description'], 'icon': data['icon']}
            )
            emulators.append(emulator)
            self.stdout.write(f"{'Created' if created else 'Found'} emulator: {emulator.name}")
        
        # Create Tags
        tags_data = [
            'Action', 'Adventure', 'RPG', 'Strategy', 'Sports', 
            'Racing', 'Fighting', 'Puzzle', 'Platform', 'Shooter',
            'Arcade', 'Retro', 'Classic', 'Multiplayer', 'Single-player',
            '2D', '3D', 'Story-Rich', 'Fast-Paced', 'Casual'
        ]
        
        tags = []
        for tag_name in tags_data:
            tag, created = Tag.objects.get_or_create(name=tag_name)
            tags.append(tag)
            self.stdout.write(f"{'Created' if created else 'Found'} tag: {tag.name}")
        
        # Create Games
        games_data = [
            # NES Games (10)
            {'title': 'Super Mario Bros', 'genre': 'PLATFORM', 'emulator': 0, 'description': 'Classic platformer featuring Mario'},
            {'title': 'The Legend of Zelda', 'genre': 'ADVENTURE', 'emulator': 0, 'description': 'Epic adventure quest'},
            {'title': 'Mega Man 2', 'genre': 'ACTION', 'emulator': 0, 'description': 'Action platformer with robot masters'},
            {'title': 'Metroid', 'genre': 'ADVENTURE', 'emulator': 0, 'description': 'Sci-fi exploration adventure'},
            {'title': 'Castlevania', 'genre': 'ACTION', 'emulator': 0, 'description': 'Gothic action platformer'},
            {'title': 'Punch-Out!!', 'genre': 'SPORTS', 'emulator': 0, 'description': 'Boxing game with unique characters'},
            {'title': 'Duck Hunt', 'genre': 'SHOOTER', 'emulator': 0, 'description': 'Light gun shooting game'},
            {'title': 'Excitebike', 'genre': 'RACING', 'emulator': 0, 'description': 'Motocross racing game'},
            {'title': 'Contra', 'genre': 'ACTION', 'emulator': 0, 'description': 'Run and gun action game'},
            {'title': 'Tetris', 'genre': 'PUZZLE', 'emulator': 0, 'description': 'Classic block puzzle game'},
            
            # SNES Games (15)
            {'title': 'Super Mario World', 'genre': 'PLATFORM', 'emulator': 1, 'description': 'Advanced Mario platformer'},
            {'title': 'The Legend of Zelda: A Link to the Past', 'genre': 'ADVENTURE', 'emulator': 1, 'description': 'Classic action RPG'},
            {'title': 'Super Metroid', 'genre': 'ADVENTURE', 'emulator': 1, 'description': 'Atmospheric exploration game'},
            {'title': 'Chrono Trigger', 'genre': 'RPG', 'emulator': 1, 'description': 'Time-traveling RPG masterpiece'},
            {'title': 'Final Fantasy VI', 'genre': 'RPG', 'emulator': 1, 'description': 'Epic fantasy RPG'},
            {'title': 'Donkey Kong Country', 'genre': 'PLATFORM', 'emulator': 1, 'description': 'Beautiful pre-rendered platformer'},
            {'title': 'Street Fighter II', 'genre': 'FIGHTING', 'emulator': 1, 'description': 'Classic fighting game'},
            {'title': 'Super Mario Kart', 'genre': 'RACING', 'emulator': 1, 'description': 'Kart racing with Mario characters'},
            {'title': 'Mega Man X', 'genre': 'ACTION', 'emulator': 1, 'description': 'Fast-paced action platformer'},
            {'title': 'Secret of Mana', 'genre': 'RPG', 'emulator': 1, 'description': 'Action RPG with multiplayer'},
            {'title': 'F-Zero', 'genre': 'RACING', 'emulator': 1, 'description': 'Futuristic racing game'},
            {'title': 'Earthbound', 'genre': 'RPG', 'emulator': 1, 'description': 'Quirky modern RPG'},
            {'title': 'Super Castlevania IV', 'genre': 'ACTION', 'emulator': 1, 'description': 'Enhanced Castlevania experience'},
            {'title': 'Star Fox', 'genre': 'SHOOTER', 'emulator': 1, 'description': '3D space shooter'},
            {'title': 'Yoshi\'s Island', 'genre': 'PLATFORM', 'emulator': 1, 'description': 'Colorful platformer'},
            
            # PlayStation Games (15)
            {'title': 'Final Fantasy VII', 'genre': 'RPG', 'emulator': 2, 'description': 'Legendary 3D RPG'},
            {'title': 'Metal Gear Solid', 'genre': 'ACTION', 'emulator': 2, 'description': 'Stealth action game'},
            {'title': 'Resident Evil', 'genre': 'ACTION', 'emulator': 2, 'description': 'Survival horror classic'},
            {'title': 'Crash Bandicoot', 'genre': 'PLATFORM', 'emulator': 2, 'description': '3D platformer adventure'},
            {'title': 'Tekken 3', 'genre': 'FIGHTING', 'emulator': 2, 'description': '3D fighting game'},
            {'title': 'Gran Turismo', 'genre': 'RACING', 'emulator': 2, 'description': 'Realistic racing simulator'},
            {'title': 'Spyro the Dragon', 'genre': 'PLATFORM', 'emulator': 2, 'description': 'Colorful 3D platformer'},
            {'title': 'Tony Hawk\'s Pro Skater 2', 'genre': 'SPORTS', 'emulator': 2, 'description': 'Skateboarding game'},
            {'title': 'Silent Hill', 'genre': 'ACTION', 'emulator': 2, 'description': 'Psychological horror'},
            {'title': 'Castlevania: Symphony of the Night', 'genre': 'ACTION', 'emulator': 2, 'description': 'Metroidvania masterpiece'},
            {'title': 'Twisted Metal 2', 'genre': 'ACTION', 'emulator': 2, 'description': 'Vehicular combat game'},
            {'title': 'Parasite Eve', 'genre': 'RPG', 'emulator': 2, 'description': 'RPG with survival horror'},
            {'title': 'PaRappa the Rapper', 'genre': 'MUSIC', 'emulator': 2, 'description': 'Rhythm game'},
            {'title': 'Xenogears', 'genre': 'RPG', 'emulator': 2, 'description': 'Complex RPG narrative'},
            {'title': 'Oddworld: Abe\'s Oddysee', 'genre': 'PLATFORM', 'emulator': 2, 'description': 'Puzzle platformer'},
            
            # Game Boy Games (5)
            {'title': 'Pokemon Red', 'genre': 'RPG', 'emulator': 3, 'description': 'Monster collecting RPG'},
            {'title': 'The Legend of Zelda: Link\'s Awakening', 'genre': 'ADVENTURE', 'emulator': 3, 'description': 'Portable Zelda adventure'},
            {'title': 'Tetris', 'genre': 'PUZZLE', 'emulator': 3, 'description': 'Portable puzzle game'},
            {'title': 'Super Mario Land', 'genre': 'PLATFORM', 'emulator': 3, 'description': 'Portable Mario platformer'},
            {'title': 'Kirby\'s Dream Land', 'genre': 'PLATFORM', 'emulator': 3, 'description': 'Cute platformer'},
            
            # Arcade Games (5)
            {'title': 'Pac-Man', 'genre': 'ARCADE', 'emulator': 4, 'description': 'Classic maze chase game'},
            {'title': 'Street Fighter II', 'genre': 'FIGHTING', 'emulator': 4, 'description': 'Arcade fighting classic'},
            {'title': 'Mortal Kombat', 'genre': 'FIGHTING', 'emulator': 4, 'description': 'Brutal fighting game'},
            {'title': 'Galaga', 'genre': 'SHOOTER', 'emulator': 4, 'description': 'Space shooter'},
            {'title': 'Donkey Kong', 'genre': 'ARCADE', 'emulator': 4, 'description': 'Original arcade platformer'},
        ]
        
        created_count = 0
        for i, game_data in enumerate(games_data):
            emulator = emulators[game_data['emulator']]
            
            # Check if game exists
            game, created = Game.objects.get_or_create(
                title=game_data['title'],
                emulator=emulator,
                defaults={
                    'description': game_data['description'],
                    'genre': game_data['genre'],
                    'file_size': random.randint(5, 500),
                    'download_url': f'https://example.com/games/{game_data["title"].lower().replace(" ", "-")}.zip',
                    'is_premium': random.choice([True, False]),
                    'release_date': timezone.now() - timezone.timedelta(days=random.randint(100, 10000))
                }
            )
            
            if created:
                # Add random tags (3-6 tags per game)
                num_tags = random.randint(3, 6)
                game_tags = random.sample(tags, num_tags)
                game.tags.set(game_tags)
                created_count += 1
                
            self.stdout.write(f"{'Created' if created else 'Found'} game: {game.title}")
        
        self.stdout.write(self.style.SUCCESS(f'\n✓ Test data creation complete!'))
        self.stdout.write(self.style.SUCCESS(f'  - {len(emulators)} emulators'))
        self.stdout.write(self.style.SUCCESS(f'  - {len(tags)} tags'))
        self.stdout.write(self.style.SUCCESS(f'  - {created_count} new games created ({Game.objects.count()} total)'))
