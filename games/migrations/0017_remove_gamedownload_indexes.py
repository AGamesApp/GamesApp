# Generated manually - Remove GameDownload indexes before deleting model

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('games', '0016_emulator_video_url_game_video_url'),
    ]

    operations = [
        # Remove indexes from GameDownload first
        migrations.RemoveIndex(
            model_name='gamedownload',
            name='games_gamed_game_id_87c671_idx',
        ),
        migrations.RemoveIndex(
            model_name='gamedownload',
            name='games_gamed_user_id_f1811c_idx',
        ),
        migrations.RemoveIndex(
            model_name='gamedownload',
            name='games_gamed_user_id_15f146_idx',
        ),
    ]
