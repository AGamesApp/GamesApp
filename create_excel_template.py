"""
Generate a sample Excel template for game imports
"""
import pandas as pd

# Create sample data with all columns
sample_data = [
    {
        'game_name': 'Super Mario Bros',
        'console': 'NES',
        'priority': 100,
        'description': 'Classic platformer game featuring Mario and Luigi',
        'image_url': 'https://example.com/mario.jpg',
        'image_1': 'https://example.com/mario_screenshot1.jpg',
        'image_2': 'https://example.com/mario_screenshot2.jpg',
        'image_3': 'https://example.com/mario_screenshot3.jpg',
        'image_4': '',
        'image_5': '',
        'size': '40 KB',
        'download_url': 'https://example.com/mario_download',
        'game_url': 'https://example.com/mario_page',
        'video_url': 'https://youtube.com/mario_video',
        'region': 'USA',
        'genres': 'Action, Platform',
        'is_premium': 'false',
        'year': '1985'
    },
    {
        'game_name': 'The Legend of Zelda',
        'console': 'NES',
        'priority': 95,
        'description': 'Action-adventure game with exploration and puzzle-solving',
        'image_url': 'https://example.com/zelda.jpg',
        'image_1': 'https://example.com/zelda_screenshot1.jpg',
        'image_2': 'https://example.com/zelda_screenshot2.jpg',
        'image_3': '',
        'image_4': '',
        'image_5': '',
        'size': '128 KB',
        'download_url': 'https://example.com/zelda_download',
        'game_url': 'https://example.com/zelda_page',
        'video_url': 'https://youtube.com/zelda_video',
        'region': 'USA',
        'genres': 'Action, Adventure, RPG',
        'is_premium': 'true',
        'year': '1986'
    },
    {
        'game_name': 'Sonic the Hedgehog',
        'console': 'Genesis',
        'priority': 90,
        'description': 'High-speed platformer with Sonic',
        'image_url': 'https://example.com/sonic.jpg',
        'image_1': 'https://example.com/sonic_screenshot1.jpg',
        'image_2': '',
        'image_3': '',
        'image_4': '',
        'image_5': '',
        'size': '512 KB',
        'download_url': 'https://example.com/sonic_download',
        'game_url': '',
        'video_url': '',
        'region': 'USA',
        'genres': 'Action, Platform',
        'is_premium': 'false',
        'year': '1991'
    },
    {
        'game_name': 'Minimal Game Example',
        'console': 'SNES',
        'priority': '',
        'description': '',
        'image_url': '',
        'image_1': '',
        'image_2': '',
        'image_3': '',
        'image_4': '',
        'image_5': '',
        'size': '',
        'download_url': '',
        'game_url': '',
        'video_url': '',
        'region': '',
        'genres': '',
        'is_premium': '',
        'year': ''
    }
]

# Create DataFrame
df = pd.DataFrame(sample_data)

# Save to Excel
output_file = 'games_import_template.xlsx'
df.to_excel(output_file, index=False, engine='openpyxl')

print(f"✅ Sample Excel template created: {output_file}")
print("\n📋 Template includes:")
print("  • 3 example games with all fields filled")
print("  • 1 minimal example showing only required fields")
print("\n💡 Instructions:")
print("  1. Open the Excel file")
print("  2. Edit or add your game data")
print("  3. Upload to Google Sheets")
print("  4. Share with 'Anyone with the link can view'")
print("  5. Copy the share link")
print("  6. Run import_games.py and paste the link")
print("\n📝 Column Order:")
for i, col in enumerate(df.columns, 1):
    required = "✅ REQUIRED" if col in ['game_name', 'console'] else "⭐ Optional"
    print(f"  {i:2d}. {col:20s} {required}")
