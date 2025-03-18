#!/usr/bin/env python3
import os
import django
import time
import logging
import subprocess
import uuid
from pathlib import Path

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("preview_generation.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'carti_project.settings')
django.setup()

from django.conf import settings
from catalog.models import CartiCatalog

def download_audio(url):
    """Download audio file from URL to a temporary location"""
    try:
        temp_file = f"/tmp/{uuid.uuid4()}.mp3"
        logger.info(f"Attempting to download from {url} to {temp_file}")
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': url,
        }
        
        # Try different download methods
        if 'music.froste.lol' in url and 'download' in url:
            # Direct download via curl for music.froste.lol
            curl_cmd = [
                'curl',
                '-L',  # Follow redirects
                '-A', headers['User-Agent'],
                '-o', temp_file,
                '--max-time', '60',
                url
            ]
            subprocess.check_call(curl_cmd, stderr=subprocess.STDOUT)
            
        elif url.endswith('.mp3'):
            # Direct MP3 link
            curl_cmd = [
                'curl',
                '-L',
                '-o', temp_file,
                '--max-time', '60',
                url
            ]
            subprocess.check_call(curl_cmd, stderr=subprocess.STDOUT)
            
        else:
            # Try FFmpeg as a fallback
            cmd = [
                'ffmpeg',
                '-y',
                '-i', url,
                '-t', '60',  # Limit to 60 seconds (we'll trim later)
                '-c:a', 'libmp3lame',
                '-b:a', '128k',
                temp_file
            ]
            subprocess.check_call(cmd, stderr=subprocess.STDOUT)
        
        # Verify download worked
        if os.path.exists(temp_file) and os.path.getsize(temp_file) > 0:
            logger.info(f"Successfully downloaded to {temp_file}")
            return temp_file
            
    except Exception as e:
        logger.exception(f"Error downloading from {url}: {str(e)}")
    
    return None
    
def create_preview(input_file, output_file):
    """Create a standard 30-second preview clip"""
    try:
        # Get template properties from the working preview
        preview_dir = os.path.join(settings.MEDIA_ROOT, 'previews')
        working_template = os.path.join(preview_dir, '56711856-592a-4f2b-9de9-e6781f8deff1.mp3')
        
        if not os.path.exists(working_template):
            logger.warning(f"Working template not found: {working_template}")
            # Create without template
            cmd = [
                'ffmpeg',
                '-y',
                '-i', input_file,
                '-ss', '30',  # Start at 30 seconds
                '-t', '30',   # Duration 30 seconds
                '-c:a', 'libmp3lame',
                '-ar', '48000',  # 48 kHz sample rate
                '-b:a', '128k',
                '-af', 'afade=t=in:st=0:d=0.5,afade=t=out:st=29.5:d=0.5',  # Add fade in/out
                output_file
            ]
        else:
            # Copy format from template for consistency
            cmd = [
                'ffmpeg',
                '-y',
                '-i', input_file,
                '-i', working_template,
                '-ss', '30',  # Start at 30 seconds
                '-t', '30',   # Duration 30 seconds
                '-map', '0:a',  # Use audio from first input
                '-c:a', 'libmp3lame',
                '-ar', '48000',  # 48 kHz sample rate (match template)
                '-b:a', '128k',
                '-af', 'afade=t=in:st=0:d=0.5,afade=t=out:st=29.5:d=0.5',  # Add fade in/out
                output_file
            ]
            
        subprocess.check_call(cmd, stderr=subprocess.STDOUT)
        
        if os.path.exists(output_file) and os.path.getsize(output_file) > 0:
            logger.info(f"Successfully created preview: {output_file}")
            return True
    
    except Exception as e:
        logger.exception(f"Error creating preview: {str(e)}")
    
    return False

def generate_preview_for_song(song_id):
    """Generate a preview for a song"""
    try:
        song = CartiCatalog.objects.get(id=song_id)
        
        # Skip if no links
        if not song.links:
            logger.warning(f"Song {song_id} has no links")
            return None
        
        # Extract URLs from links field
        import re
        urls = re.findall(r'https?://[^\s<>"]+|www\.[^\s<>"]+', song.links)
        if not urls:
            logger.warning(f"No URLs found in links for song {song_id}")
            return None
        
        # Try to find a direct download link
        download_url = None
        for url in urls:
            if 'music.froste.lol/song/' in url:
                song_id_match = url.split('/song/')[1].split('/')[0]
                download_url = f"http://music.froste.lol/song/{song_id_match}/download"
                break
            elif url.endswith('.mp3'):
                download_url = url
                break
        
        # If no specific download URL found, use the first URL
        if not download_url:
            download_url = urls[0]
        
        # Download the audio
        temp_file = download_audio(download_url)
        if not temp_file:
            logger.error(f"Failed to download audio for song {song_id}")
            return None
        
        try:
            # Create unique filename and path for preview
            preview_dir = os.path.join(settings.MEDIA_ROOT, 'previews')
            os.makedirs(preview_dir, exist_ok=True)
            
            preview_filename = f"{uuid.uuid4()}.mp3"
            preview_path = os.path.join(preview_dir, preview_filename)
            
            # Create the preview
            if create_preview(temp_file, preview_path):
                # Update the song record
                preview_url = f"/media/previews/{preview_filename}"
                song.preview_url = preview_url
                song.save(update_fields=['preview_url'])
                
                return preview_url
            else:
                logger.error(f"Failed to create preview for song {song_id}")
                return None
                
        finally:
            # Clean up temp file
            if temp_file and os.path.exists(temp_file):
                os.remove(temp_file)
    
    except Exception as e:
        logger.exception(f"Error generating preview for song {song_id}: {str(e)}")
        return None

def main():
    """Process songs without previews"""
    # Ensure the previews directory exists
    preview_dir = os.path.join(settings.MEDIA_ROOT, 'previews')
    os.makedirs(preview_dir, exist_ok=True)
    
    # Check if we have the working template
    working_template = os.path.join(preview_dir, '56711856-592a-4f2b-9de9-e6781f8deff1.mp3')
    if not os.path.exists(working_template):
        logger.warning(f"Working template not found: {working_template}")
    else:
        logger.info(f"Found working template: {working_template}")
    
    # Get songs without previews
    songs = CartiCatalog.objects.filter(preview_url__isnull=True).filter(links__isnull=False)
    total_songs = songs.count()
    
    logger.info(f"Found {total_songs} songs without previews")
    
    success_count = 0
    failure_count = 0
    
    for i, song in enumerate(songs, 1):
        logger.info(f"Processing song {i}/{total_songs}: {song.id} - {song.name}")
        
        try:
            preview_url = generate_preview_for_song(song.id)
            
            if preview_url:
                success_count += 1
                logger.info(f"Successfully generated preview: {preview_url}")
            else:
                failure_count += 1
                logger.warning(f"Failed to generate preview")
                
            # Sleep a bit to avoid overloading the server
            time.sleep(1)
            
        except Exception as e:
            failure_count += 1
            logger.exception(f"Error processing song {song.id}: {str(e)}")
    
    logger.info(f"Completed processing:")
    logger.info(f"  Success: {success_count}")
    logger.info(f"  Failed: {failure_count}")
    
if __name__ == "__main__":
    main()