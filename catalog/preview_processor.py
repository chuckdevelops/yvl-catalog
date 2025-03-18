import os
import re
import uuid
import requests
import logging
import subprocess
import json
from pathlib import Path
from urllib.parse import urlparse, urljoin
from django.conf import settings
from django.db import transaction
from catalog.models import CartiCatalog

# Configure logging
logger = logging.getLogger(__name__)

# Configuration
PREVIEW_DIR = os.path.join(settings.MEDIA_ROOT, 'previews')
PREVIEW_LENGTH = 30 * 1000  # 30 seconds in milliseconds
START_AT = 30 * 1000  # Start preview 30 seconds into track

# Create directory if it doesn't exist
os.makedirs(PREVIEW_DIR, exist_ok=True)

def generate_preview_for_song(song_id):
    """Generate a 30-second preview for a specific song"""
    try:
        with transaction.atomic():
            song = CartiCatalog.objects.select_for_update().get(id=song_id)
            
            # Skip if no links or already has preview
            if not song.links:
                logger.warning(f"Song {song_id} has no links")
                return None
                
            # If preview already exists, return existing URL
            if song.preview_url and os.path.exists(os.path.join(settings.BASE_DIR, song.preview_url.lstrip('/'))):
                logger.info(f"Preview already exists for song {song_id}")
                return song.preview_url
            
            # Process download URL
            download_url = extract_download_url(song.links)
            if not download_url:
                logger.warning(f"Could not extract download URL for song {song_id}")
                return None
            
            # Download the full audio file
            temp_file = download_audio(download_url)
            if not temp_file:
                logger.error(f"Failed to download audio for song {song_id}")
                return None
            
            try:
                # Generate a unique filename
                preview_filename = f"{uuid.uuid4()}.mp3"
                preview_path = os.path.join(PREVIEW_DIR, preview_filename)
                
                # Process the audio file to create the preview
                create_preview_clip(temp_file, preview_path)
                
                # Update the song record with the preview URL
                preview_url = f"/media/previews/{preview_filename}"
                song.preview_url = preview_url
                song.save(update_fields=['preview_url'])
                
                logger.info(f"Successfully generated preview for song {song_id}")
                return preview_url
            finally:
                # Clean up temporary file
                if os.path.exists(temp_file):
                    os.remove(temp_file)
                    
    except Exception as e:
        logger.exception(f"Error generating preview for song {song_id}: {str(e)}")
        return None

def extract_download_url(links_text):
    """Extract download URL from song links"""
    if not links_text:
        return None
    
    # Extract all URLs from the links text
    urls = re.findall(r'https?://[^\s<>"]+|www\.[^\s<>"]+', links_text)
    if not urls:
        return None
    
    for url in urls:
        # Handle music.froste.lol links
        if 'music.froste.lol/song/' in url:
            song_id = url.split('/song/')[1].split('/')[0]
            download_url = f"http://music.froste.lol/song/{song_id}/download"
            logger.info(f"Found music.froste.lol URL: {url} -> {download_url}")
            return download_url
            
        # Handle pillowcase.su links
        elif 'pillowcase.su/f/' in url:
            file_id = url.split('/f/')[1]
            download_url = f"https://pillowcase.su/f/{file_id}/download"
            logger.info(f"Found pillowcase.su URL: {url} -> {download_url}")
            return download_url
            
        # Handle SoundCloud links - these require more complex handling
        elif 'soundcloud.com' in url:
            logger.info(f"Found SoundCloud URL: {url}")
            return url
            
        # Handle Spotify links
        elif 'spotify.com' in url:
            logger.info(f"Found Spotify URL: {url}")
            return url
    
    # If no supported URL found, return the first URL as fallback
    logger.info(f"Using fallback URL: {urls[0]}")
    return urls[0]

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
        
        # Try to directly download first - works for most direct links
        if 'download' in url or 'music.froste.lol' in url or 'pillowcase.su' in url:
            logger.info(f"Attempting direct download: {url}")
            response = requests.get(url, headers=headers, stream=True, timeout=60)
            
            if response.status_code == 200:
                content_type = response.headers.get('Content-Type', '')
                if 'audio' in content_type or 'octet-stream' in content_type:
                    logger.info(f"Direct download successful with content type: {content_type}")
                    with open(temp_file, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=1024):
                            if chunk:
                                f.write(chunk)
                    return temp_file
                else:
                    logger.warning(f"Unexpected content type: {content_type}")
        
        # Handle SoundCloud - requires a more complex approach with youtube-dl
        if 'soundcloud.com' in url:
            logger.info("Detected SoundCloud URL, using ffmpeg to download")
            try:
                cmd = [
                    'ffmpeg',
                    '-y',  # Overwrite output file
                    '-i', url,  # Input URL
                    '-acodec', 'libmp3lame',  # MP3 codec
                    '-b:a', '128k',  # Bitrate
                    temp_file  # Output file
                ]
                
                subprocess.check_call(cmd, stderr=subprocess.STDOUT)
                if os.path.exists(temp_file) and os.path.getsize(temp_file) > 0:
                    logger.info(f"Successfully downloaded via ffmpeg: {temp_file}")
                    return temp_file
            except Exception as e:
                logger.exception(f"Error downloading from SoundCloud: {str(e)}")
        
        # As a fallback, try curl with auto-redirect
        try:
            logger.info(f"Attempting fallback download with curl: {url}")
            curl_cmd = [
                'curl',
                '-L',  # Follow redirects
                '-o', temp_file,  # Output file
                '-A', headers['User-Agent'],  # User agent
                '--max-time', '60',  # Timeout
                url  # URL
            ]
            
            subprocess.check_call(curl_cmd, stderr=subprocess.STDOUT)
            if os.path.exists(temp_file) and os.path.getsize(temp_file) > 0:
                logger.info(f"Successfully downloaded via curl: {temp_file}")
                return temp_file
        except Exception as e:
            logger.exception(f"Error downloading with curl: {str(e)}")
        
    except Exception as e:
        logger.exception(f"Error downloading from {url}: {str(e)}")
    
    return None

def create_preview_clip(input_file, output_file):
    """Create a 30-second preview clip from the input file using ffmpeg directly"""
    try:
        # Get audio duration using ffprobe
        duration_cmd = [
            'ffprobe', 
            '-v', 'error', 
            '-show_entries', 'format=duration', 
            '-of', 'json', 
            input_file
        ]
        
        duration_output = subprocess.check_output(duration_cmd, stderr=subprocess.STDOUT)
        duration_data = json.loads(duration_output)
        total_duration = float(duration_data['format']['duration'])
        
        # Calculate start point (don't go beyond track length)
        start_seconds = min(START_AT / 1000, max(0, total_duration - (PREVIEW_LENGTH / 1000)))
        
        # Use ffmpeg to extract the segment
        extract_cmd = [
            'ffmpeg',
            '-y',  # Overwrite output file if it exists
            '-i', input_file,  # Input file
            '-ss', str(start_seconds),  # Start time
            '-t', str(PREVIEW_LENGTH / 1000),  # Duration in seconds
            '-af', 'afade=t=in:st=0:d=1,afade=t=out:st=' + str((PREVIEW_LENGTH / 1000) - 1) + ':d=1',  # Add fade in/out
            '-codec:a', 'libmp3lame',  # MP3 codec
            '-b:a', '128k',  # Bitrate
            output_file  # Output file
        ]
        
        subprocess.check_call(extract_cmd, stderr=subprocess.STDOUT)
        
        return True
    except Exception as e:
        logger.exception(f"Error creating preview clip: {str(e)}")
        return False

def process_all_songs():
    """Process all songs that don't have previews yet"""
    songs = CartiCatalog.objects.filter(preview_url__isnull=True).filter(links__isnull=False)
    logger.info(f"Found {songs.count()} songs without previews")
    
    results = {
        'success': 0,
        'failed': 0,
        'songs': []
    }
    
    for song in songs:
        logger.info(f"Processing song {song.id}: {song.name}")
        preview_url = generate_preview_for_song(song.id)
        
        if preview_url:
            results['success'] += 1
            results['songs'].append({
                'id': song.id,
                'name': song.name,
                'status': 'success',
                'preview_url': preview_url
            })
        else:
            results['failed'] += 1
            results['songs'].append({
                'id': song.id,
                'name': song.name,
                'status': 'failed'
            })
    
    return results