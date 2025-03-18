#!/usr/bin/env python3
import os
import django
import subprocess
import uuid
import logging
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'carti_project.settings')
django.setup()

from django.conf import settings
from catalog.models import CartiCatalog

def main():
    # Fix 1: Make sure media/previews directory exists
    preview_dir = os.path.join(settings.MEDIA_ROOT, 'previews')
    os.makedirs(preview_dir, exist_ok=True)
    logger.info(f"Ensuring preview directory exists: {preview_dir}")

    # Fix 2: Copy the working preview to a standard format
    working_preview = os.path.join(preview_dir, '56711856-592a-4f2b-9de9-e6781f8deff1.mp3')
    if not os.path.exists(working_preview):
        logger.error(f"Working preview file not found: {working_preview}")
        return
        
    logger.info(f"Using working preview as template: {working_preview}")
    
    # Get songs with existing previews
    songs_with_previews = CartiCatalog.objects.exclude(preview_url__isnull=True)
    logger.info(f"Found {songs_with_previews.count()} songs with previews")
    
    success_count = 0
    
    for song in songs_with_previews:
        try:
            # Skip the working preview
            if "56711856-592a-4f2b-9de9-e6781f8deff1" in song.preview_url:
                logger.info(f"Skipping working preview for song {song.id}: {song.name}")
                success_count += 1
                continue
                
            # Extract filename from preview URL
            filename = Path(song.preview_url).name
            preview_path = os.path.join(preview_dir, filename)
            
            # Generate a new standard preview using ffmpeg
            logger.info(f"Regenerating preview for song {song.id}: {song.name}")
            
            # Copy formatting from the working preview
            cmd = [
                'ffmpeg',
                '-y',  # Overwrite output
                '-i', working_preview,  # Input (working template)
                '-i', preview_path,  # Input (existing preview)
                '-map', '1:a',  # Take audio from second input
                '-c:a', 'libmp3lame',  # MP3 codec
                '-ar', '48000',  # Sample rate matching working preview
                '-b:a', '128k',  # Bitrate
                preview_path  # Output to same path
            ]
            
            subprocess.check_call(cmd, stderr=subprocess.STDOUT)
            
            # Verify the file exists
            if os.path.exists(preview_path) and os.path.getsize(preview_path) > 0:
                logger.info(f"Successfully regenerated preview: {preview_path}")
                success_count += 1
            else:
                logger.error(f"Failed to create preview file: {preview_path}")
                
        except Exception as e:
            logger.exception(f"Error processing song {song.id}: {str(e)}")
    
    logger.info(f"Completed processing: {success_count} successes out of {songs_with_previews.count()} songs")

if __name__ == "__main__":
    main()