#!/usr/bin/env python3
import os
import sys
import django
from pathlib import Path

# Set up Django environment
sys.path.insert(0, str(Path(__file__).resolve().parent))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'carti_project.settings')
django.setup()

# Import models after Django setup
from django.conf import settings
from catalog.models import CartiCatalog

def fix_preview_urls():
    """Fix preview URLs in the database to ensure correct format"""
    # Get all songs with preview URLs
    songs_with_previews = CartiCatalog.objects.exclude(preview_url__isnull=True)
    
    print(f"Found {songs_with_previews.count()} songs with preview URLs")
    
    fixed_count = 0
    missing_count = 0
    unchanged_count = 0
    
    # Create a list of valid preview files
    preview_dir = os.path.join(settings.MEDIA_ROOT, 'previews')
    valid_files = set(os.listdir(preview_dir)) if os.path.exists(preview_dir) else set()
    
    print(f"Found {len(valid_files)} valid preview files in {preview_dir}")
    
    for song in songs_with_previews:
        # Extract filename from preview URL
        preview_url = song.preview_url
        if preview_url.startswith('/media/previews/'):
            filename = preview_url[16:]
        else:
            filename = os.path.basename(preview_url)
        
        # Check if the file exists
        file_exists = filename in valid_files
        
        # Construct the correct URL format
        correct_url = f'/media/previews/{filename}'
        
        if not file_exists:
            print(f"WARNING: Missing file for song {song.id} ({song.name}): {filename}")
            missing_count += 1
            continue
        
        if preview_url != correct_url:
            print(f"Fixing URL for song {song.id}: {preview_url} -> {correct_url}")
            song.preview_url = correct_url
            song.save(update_fields=['preview_url'])
            fixed_count += 1
        else:
            print(f"URL is already correct for song {song.id}")
            unchanged_count += 1
    
    print(f"Fixed {fixed_count} URLs, {unchanged_count} were already correct, {missing_count} files missing")

if __name__ == "__main__":
    fix_preview_urls()