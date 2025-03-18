#!/usr/bin/env python3
"""
Script to restore the original audio files and database entries
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

def restore_audio_previews():
    try:
        # Directories
        preview_dir = os.path.join(settings.MEDIA_ROOT, 'previews')
        backup_dir = os.path.join(settings.MEDIA_ROOT, 'previews_backup')
        
        # Check if backup directory exists
        if not os.path.exists(backup_dir):
            print(f"ERROR: Backup directory not found: {backup_dir}")
            return
            
        # Get list of backup files
        backup_files = [f for f in os.listdir(backup_dir) if f.endswith('.mp3')]
        print(f"Found {len(backup_files)} backup files")
        
        # Find and delete temporary song files
        temp_files = [f for f in os.listdir(preview_dir) if f.startswith('song_') and f.endswith('.mp3')]
        for filename in temp_files:
            file_path = os.path.join(preview_dir, filename)
            os.remove(file_path)
            print(f"Deleted temporary file: {filename}")
        
        # Copy original files back
        restored_count = 0
        for filename in backup_files:
            src_path = os.path.join(backup_dir, filename)
            dst_path = os.path.join(preview_dir, filename)
            shutil.copy2(src_path, dst_path)
            restored_count += 1
            print(f"Restored: {filename}")
        
        print(f"Restored {restored_count} original audio files")
            
        # Restore database entries
        # Get all songs with preview URLs that start with /media/previews/song_
        songs_to_restore = CartiCatalog.objects.filter(preview_url__startswith='/media/previews/song_')
        
        # Mapping from song ID to original filename
        song_id_to_filename = {
            1248: '0e75dda9-fc84-4e1a-9b2d-85cec2dfbba6.mp3',
            412: '281810ee-3d37-43f6-91db-df2f9288d745.mp3',
            414: '8b98a2e1-08ad-47b5-bec9-7cb6b782e792.mp3',
            427: 'ceabdbdb-53ee-4048-a97d-f9344ae4e31a.mp3',
            420: 'a4306fb2-2d98-4a64-a1e9-1074b7884f7b.mp3',
            423: '54bfdce3-bfc3-45df-9004-7c571f8f8215.mp3',
            417: '29b7a015-5f74-4063-96b1-1a63bf7192a7.mp3',
            426: '1739d094-c523-4b22-b182-48f18586fcb6.mp3',
            1076: '836c4cc1-2814-4127-9233-1688b8bb2fc4.mp3',
            73: 'ee056a5a-e188-4667-a730-467ac2221ede.mp3'
        }
        
        for song in songs_to_restore:
            if song.id in song_id_to_filename:
                original_filename = song_id_to_filename[song.id]
                original_url = f"/media/previews/{original_filename}"
                
                # Update the database
                print(f"Restoring database entry for song ID {song.id}")
                print(f"  Current URL: {song.preview_url}")
                print(f"  Original URL: {original_url}")
                
                song.preview_url = original_url
                song.save(update_fields=['preview_url'])
                print(f"  Database entry restored")
            else:
                print(f"WARNING: No original filename found for song ID {song.id}")
        
        print("Database restoration complete")
        
    except Exception as e:
        print(f"ERROR: {str(e)}")

if __name__ == "__main__":
    restore_audio_previews()