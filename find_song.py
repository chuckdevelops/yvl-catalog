#!/usr/bin/env python3
import os
import django

# Set the Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'carti_project.settings')
django.setup()

from catalog.models import CartiCatalog

# Use more flexible search
songs = CartiCatalog.objects.filter(name__icontains='Kid Cudi') | \
        CartiCatalog.objects.filter(name__icontains='Solo Dolo')

print(f"Found {songs.count()} songs:")
for song in songs:
    print(f"{song.id}: {song.name}")
    print(f"  Era: {song.era}")
    print(f"  Type: {song.type}")
    print(f"  Leak Date: {song.leak_date}")
    print("---")