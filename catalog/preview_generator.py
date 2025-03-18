import os
import re
import requests
import uuid
import logging
from pydub import AudioSegment
from django.conf import settings
from celery import shared_task
from django.db import transaction
from catalog.models import CartiCatalog

# Set up logging
logger = logging.getLogger(__name__)

# Configuration
MEDIA_ROOT = settings.MEDIA_ROOT
PREVIEW_DIR = os.path.join(MEDIA_ROOT, 'previews')
PREVIEW_LENGTH = 30 * 1000  # 30 seconds in milliseconds
START_AT = 30 * 1000  # Start preview 30 seconds in

# Create directories if they don't exist
os.makedirs(PREVIEW_DIR, exist_ok=True)

@shared_task
def generate_all_previews():
    """Process all songs that don't have previews yet"""
    songs = CartiCatalog.objects.filter(preview_url__isnull=True).filter(links__isnull=False)
    count = songs.count()
    logger.info(f"Found {count} songs without previews")
    
    for song in songs:
        generate_preview.delay(song.id)
    
    return f"Queued {count} songs for preview generation"

@shared_task
def generate_preview(song_id):
    """Generate a preview for a single song"""
    try:
        with transaction.atomic():
            song = CartiCatalog.objects.select_for_update().get(id=song_id)
            
            # Skip if no links or already has preview
            if not song.links or song.preview_url:
                logger.info(f"Skipping song {song_id}: no links or already has preview")
                return f"Skipping song {song_id}: no links or already has preview"
            
            logger.info(f"Processing song {song_id}: {song.name}")
            
            # Extract useful links from the song
            download_url = extract_download_url(song.links)
            if not download_url:
                logger.warning(f"No usable download URL found for song {song_id}")
                return f"No usable download URL found for song {song_id}"
            
            # Download the song temporarily
            temp_file = download_audio(download_url)
            if not temp_file:
                logger.error(f"Failed to download audio for song {song_id}")
                return f"Failed to download audio for song {song_id}"
            
            try:
                # Generate preview
                preview_filename = f"{uuid.uuid4()}.mp3"
                preview_path = os.path.join(PREVIEW_DIR, preview_filename)
                
                # Load audio and extract segment
                audio = AudioSegment.from_file(temp_file)
                
                # Calculate start point (don't go beyond track length)
                start_point = min(START_AT, max(0, len(audio) - PREVIEW_LENGTH))
                
                # Extract the segment
                preview = audio[start_point:start_point + PREVIEW_LENGTH]
                
                # Export as MP3
                preview.export(preview_path, format="mp3")
                
                # Save preview URL to database
                song.preview_url = f"/media/previews/{preview_filename}"
                song.save()
                
                logger.info(f"Successfully generated preview for song {song_id}")
                return f"Successfully generated preview for song {song_id}"
            finally:
                # Clean up temp file
                if os.path.exists(temp_file):
                    os.remove(temp_file)
    except Exception as e:
        logger.exception(f"Error generating preview for song {song_id}: {str(e)}")
        return f"Error generating preview for song {song_id}: {str(e)}"

def extract_download_url(links_text):
    """Extract a usable download URL from the links text"""
    # This needs customization based on your file sharing sites
    
    # Example for common file sharing sites
    urls = re.findall(r'https?://[^\s<>"]+|www\.[^\s<>"]+', links_text)
    
    for url in urls:
        # Add handling for different file sharing sites
        if 'dropbox.com' in url:
            return url.replace('?dl=0', '?dl=1')
        elif 'drive.google.com' in url:
            # Convert Google Drive view URL to direct download
            file_id = re.search(r'/d/([^/]+)', url)
            if file_id:
                return f"https://drive.google.com/uc?export=download&id={file_id.group(1)}"
        elif 'mediafire.com' in url:
            # For MediaFire, we'd need to scrape the direct download link
            # This is a placeholder - would need selenium or requests with parsing
            return url
        elif 'mega.nz' in url:
            # MEGA needs special handling with their SDK
            return url
        # Add more site-specific handlers as needed
    
    # Return the first URL as fallback
    return urls[0] if urls else None

def download_audio(url):
    """Download audio file from URL to a temporary location"""
    try:
        temp_file = f"/tmp/{uuid.uuid4()}.mp3"
        
        # Handle YouTube links specially
        if 'youtube.com' in url or 'youtu.be' in url:
            try:
                from pytube import YouTube
                yt = YouTube(url)
                audio = yt.streams.filter(only_audio=True).first()
                audio.download(filename=temp_file)
                return temp_file
            except Exception as e:
                logger.error(f"Error downloading from YouTube {url}: {str(e)}")
                return None
        
        # Handle direct file downloads
        response = requests.get(url, stream=True, timeout=60)
        if response.status_code == 200:
            with open(temp_file, 'wb') as f:
                for chunk in response.iter_content(chunk_size=1024):
                    if chunk:
                        f.write(chunk)
            return temp_file
    except Exception as e:
        logger.error(f"Error downloading {url}: {str(e)}")
    
    return None