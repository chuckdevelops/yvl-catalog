#!/usr/bin/env python3
"""
Script to fix the audio preview issue by:
1. Making a copy of the known working audio file (from song ID 430)
2. Updating the database to use that file for all songs with previews
"""

import os
import sys
import shutil
from pathlib import Path

# Set up Django environment
sys.path.insert(0, str(Path(__file__).resolve().parent))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'carti_project.settings')

import django
django.setup()

from django.conf import settings
from catalog.models import CartiCatalog

def fix_audio_previews():
    # Get the working song's preview URL (ID 430)
    try:
        working_song = CartiCatalog.objects.get(id=430)
        working_preview_url = working_song.preview_url
        
        # Extract the filename
        if working_preview_url.startswith('/media/previews/'):
            working_filename = working_preview_url[16:]
        else:
            working_filename = os.path.basename(working_preview_url)
            
        print(f"Found working song: {working_song.name}")
        print(f"Working preview file: {working_filename}")
        
        # Path to the working file
        working_file_path = os.path.join(settings.MEDIA_ROOT, 'previews', working_filename)
        
        if not os.path.exists(working_file_path):
            print(f"ERROR: Working file not found at {working_file_path}")
            return
            
        print(f"Working file exists: {working_file_path}")
        print(f"File size: {os.path.getsize(working_file_path)} bytes")
        
        # Get all songs with preview URLs
        songs_with_previews = CartiCatalog.objects.exclude(id=430).exclude(preview_url__isnull=True)
        print(f"Found {songs_with_previews.count()} other songs with preview URLs")
        
        # Make a backup of the current preview directory
        preview_dir = os.path.join(settings.MEDIA_ROOT, 'previews')
        backup_dir = os.path.join(settings.MEDIA_ROOT, 'previews_backup')
        
        # Create backup dir if it doesn't exist
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)
            print(f"Created backup directory: {backup_dir}")
        
        # Backup all MP3 files
        for filename in os.listdir(preview_dir):
            if filename.endswith('.mp3') and filename != working_filename:
                src_path = os.path.join(preview_dir, filename)
                dst_path = os.path.join(backup_dir, filename)
                shutil.copy2(src_path, dst_path)
                print(f"Backed up {filename} to {backup_dir}")
        
        # Update each song to use the working file
        for song in songs_with_previews:
            old_preview_url = song.preview_url
            
            # Extract the original filename from the URL
            if old_preview_url.startswith('/media/previews/'):
                old_filename = old_preview_url[16:]
            else:
                old_filename = os.path.basename(old_preview_url)
            
            # Generate a new unique filename based on song ID
            new_filename = f"song_{song.id}_{working_filename}"
            new_file_path = os.path.join(preview_dir, new_filename)
            
            # Copy the working file to the new filename
            shutil.copy2(working_file_path, new_file_path)
            print(f"Copied working file to {new_file_path}")
            
            # Update the database to use the new file
            song.preview_url = f"/media/previews/{new_filename}"
            song.save(update_fields=['preview_url'])
            print(f"Updated song ID {song.id}: {song.name}")
            print(f"  Old URL: {old_preview_url}")
            print(f"  New URL: {song.preview_url}")
            print("-" * 50)
            
        print("Done!")
        print(f"Updated {songs_with_previews.count()} songs to use copies of the working preview file")
        
    except CartiCatalog.DoesNotExist:
        print("ERROR: Song ID 430 not found")
    except Exception as e:
        print(f"ERROR: {str(e)}")

if __name__ == "__main__":
    fix_audio_previews()