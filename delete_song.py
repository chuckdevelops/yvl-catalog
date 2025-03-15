#!/usr/bin/env python3
import os
import django

# Set the Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'carti_project.settings')
django.setup()

from catalog.models import CartiCatalog, SongMetadata, SongCategory

def delete_song():
    """Delete the Kid Cudi Solo Dolo song and fix the Apr 15 type issue"""
    try:
        # Find the song
        song = CartiCatalog.objects.filter(name__contains='Solo Dolo Pt. IV').first()
        
        if not song:
            print("Song not found")
            return
            
        # Print song details before deletion
        print(f"Found song: {song.name} (ID: {song.id})")
        print(f"  Era: {song.era}")
        print(f"  Type: {song.type}")
        print(f"  Leak Date: {song.leak_date}")
        
        # Delete the song (Django will cascade delete related metadata and categories)
        song_id = song.id
        song.delete()
        
        print(f"Successfully deleted song with ID {song_id}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    delete_song()