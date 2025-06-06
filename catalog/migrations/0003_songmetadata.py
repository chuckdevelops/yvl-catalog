# Generated by Django 5.1.7 on 2025-03-13 00:06

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0002_sheettab'),
    ]

    operations = [
        migrations.CreateModel(
            name='SongMetadata',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('subsection', models.CharField(blank=True, max_length=100, null=True)),
                ('sheet_tab', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='songs', to='catalog.sheettab')),
                ('song', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='metadata', to='catalog.carticatalog')),
            ],
            options={
                'verbose_name': 'Song Metadata',
                'verbose_name_plural': 'Song Metadata',
                'db_table': 'song_metadata',
                'managed': True,
            },
        ),
    ]
