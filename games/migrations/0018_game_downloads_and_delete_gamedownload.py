# Generated manually - Add downloads field and delete GameDownload model

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('games', '0017_remove_gamedownload_indexes'),
    ]

    operations = [
        # Add downloads field to Game model
        migrations.AddField(
            model_name='game',
            name='downloads',
            field=models.PositiveIntegerField(db_index=True, default=0),
        ),
        # Add composite index for downloads and created_at
        migrations.AddIndex(
            model_name='game',
            index=models.Index(fields=['-downloads', '-created_at'], name='games_game_downloa_785cb3_idx'),
        ),
        # Delete GameDownload model entirely
        migrations.DeleteModel(
            name='GameDownload',
        ),
    ]
