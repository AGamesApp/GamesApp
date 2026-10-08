# Generated migration to add additional files models for Game and Emulator

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('games', '0019_alter_game_options'),
    ]

    operations = [
        migrations.CreateModel(
            name='GameAdditionalFile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file_name', models.CharField(help_text='Name of the file (e.g., Patch 1.5, DLC Pack)', max_length=200)),
                ('download_link', models.TextField(help_text='Download link for the file', max_length=1000)),
                ('file_path', models.TextField(blank=True, default='', help_text='File path or identifier', max_length=500)),
                ('order', models.PositiveIntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('game', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='additional_files', to='games.game')),
            ],
            options={
                'ordering': ['order', 'created_at'],
                'indexes': [
                    models.Index(fields=['game', 'order'], name='games_gamea_game_id_0a1b2c_idx'),
                ],
            },
        ),
        migrations.CreateModel(
            name='EmulatorAdditionalFile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file_name', models.CharField(help_text='Name of the file (e.g., BIOS Files, Graphics Plugin)', max_length=200)),
                ('download_link', models.TextField(help_text='Download link for the file', max_length=1000)),
                ('file_path', models.TextField(blank=True, default='', help_text='File path or identifier', max_length=500)),
                ('order', models.PositiveIntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('emulator', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='additional_files', to='games.emulator')),
            ],
            options={
                'ordering': ['order', 'created_at'],
                'indexes': [
                    models.Index(fields=['emulator', 'order'], name='games_emula_emulato_1a2b3c_idx'),
                ],
            },
        ),
    ]
