#!/usr/bin/env python3
"""
Complete solution to regenerate preview files from scratch:
1. Downloads original audio sources
2. Creates properly encoded preview clips
3. Verifies uniqueness of audio content
4. Updates database with preview URLs
"""

import os
import sys
import json
import uuid
import logging
import subprocess
import hashlib
import re
import requests
import random
import time
from pathlib import Path
from urllib.parse import urlparse, parse_qs

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("preview_refresh.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Set up Django environment
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'carti_project.settings')

import django
django.setup()

from django.conf import settings
from catalog.models import CartiCatalog
from django.db import transaction

# Configuration
PREVIEW_DIR = os.path.join(settings.MEDIA_ROOT, 'previews')
PREVIEW_BACKUP_DIR = os.path.join(settings.MEDIA_ROOT, 'previews_backup_refresh')
PREVIEW_LENGTH = 30  # 30 seconds
START_OFFSET = 30    # Start preview 30 seconds into track
BITRATE = '128k'     # Target bitrate
SAMPLE_RATE = 48000  # Target sample rate (48kHz)
AUDIO_HASH_FILE = "audio_content_hashes.json"  # For tracking uniqueness

# Create directories if they don't exist
os.makedirs(PREVIEW_DIR, exist_ok=True)
os.makedirs(PREVIEW_BACKUP_DIR, exist_ok=True)

def backup_existing_previews():
    """Backup all existing preview files"""
    if not os.path.exists(PREVIEW_DIR):
        logger.warning(f"Preview directory not found: {PREVIEW_DIR}")
        return
        
    # Get all MP3 files
    mp3_files = [f for f in os.listdir(PREVIEW_DIR) if f.endswith('.mp3')]
    logger.info(f"Backing up {len(mp3_files)} existing preview files")
    
    backed_up = 0
    for filename in mp3_files:
        src_path = os.path.join(PREVIEW_DIR, filename)
        dst_path = os.path.join(PREVIEW_BACKUP_DIR, filename)
        
        try:
            if not os.path.exists(dst_path):
                import shutil
                shutil.copy2(src_path, dst_path)
                backed_up += 1
        except Exception as e:
            logger.error(f"Error backing up {filename}: {str(e)}")
    
    logger.info(f"Successfully backed up {backed_up} preview files")

def get_audio_properties(file_path):
    """Get detailed audio properties using ffprobe"""
    try:
        # Get stream and format info in JSON format
        cmd = [
            'ffprobe',
            '-v', 'error',
            '-print_format', 'json',
            '-show_format',
            '-show_streams',
            file_path
        ]
        
        output = subprocess.check_output(cmd, text=True)
        data = json.loads(output)
        
        # Extract the relevant audio properties
        properties = {}
        
        # Get stream properties (codec, sample rate, etc.)
        if 'streams' in data:
            for stream in data['streams']:
                if stream.get('codec_type') == 'audio':
                    properties['codec'] = stream.get('codec_name')
                    properties['sample_rate'] = int(stream.get('sample_rate', 0))
                    properties['channels'] = stream.get('channels')
                    properties['bitrate'] = int(stream.get('bit_rate', 0)) if stream.get('bit_rate') else None
                    break
        
        # Get format properties (duration, overall bitrate)
        if 'format' in data:
            properties['format'] = data['format'].get('format_name')
            properties['duration'] = float(data['format'].get('duration', 0))
            
            # Use format bitrate if stream bitrate is not available
            if not properties.get('bitrate') and data['format'].get('bit_rate'):
                properties['bitrate'] = int(data['format'].get('bit_rate'))
            
            # Get metadata
            if 'tags' in data['format']:
                properties['metadata'] = data['format']['tags']
        
        return properties
        
    except Exception as e:
        logger.exception(f"Error getting audio properties for {file_path}: {str(e)}")
        return None

def extract_download_url(song):
    """Extract download URL from song links and information"""
    if not song.links:
        return None
    
    # Extract all URLs from the links text
    urls = re.findall(r'https?://[^\s<>"]+|www\.[^\s<>"]+', song.links)
    if not urls:
        return None
    
    # Prioritize music.froste.lol links (these seem most reliable)
    for url in urls:
        # Handle music.froste.lol links (direct download)
        if 'music.froste.lol/song/' in url:
            song_id = url.split('/song/')[1].split('/')[0]
            download_url = f"https://music.froste.lol/song/{song_id}/download"
            logger.info(f"Found music.froste.lol URL: {url} -> {download_url}")
            return download_url
    
    # If no specific download URL found, use the first URL
    logger.info(f"Using fallback URL: {urls[0]}")
    return urls[0]

def download_audio(url, song_id=None, song_name=None):
    """Download audio file from URL to a temporary location"""
    try:
        # Create a unique temp file
        temp_file = f"/tmp/song_{song_id or 'unknown'}_{uuid.uuid4()}.mp3"
        logger.info(f"Downloading from {url} to {temp_file} for song {song_id}: {song_name}")
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': 'https://music.froste.lol/',
        }
        
        # Download using curl (handles redirects better than requests)
        # Add a random parameter to bypass any caching
        timestamp = int(time.time())
        random_param = f"?t={timestamp}&r={random.randint(1000, 9999)}"
        if '?' in url:
            download_url = f"{url}&_={timestamp}"
        else:
            download_url = f"{url}{random_param}"
            
        logger.info(f"Using download URL with cache busting: {download_url}")
        
        curl_cmd = [
            'curl',
            '-L',  # Follow redirects
            '-A', headers['User-Agent'],
            '-H', f"Referer: {headers['Referer']}",
            '-o', temp_file,
            '--max-time', '90',
            download_url
        ]
        
        # Run curl command
        subprocess.check_call(curl_cmd, stderr=subprocess.STDOUT)
        
        # Verify file was downloaded and is a valid audio file
        if not os.path.exists(temp_file) or os.path.getsize(temp_file) == 0:
            logger.error(f"Downloaded file is empty or doesn't exist for song {song_id}")
            return None
            
        # Verify it's really an audio file using ffprobe
        try:
            properties = get_audio_properties(temp_file)
            if not properties or not properties.get('codec'):
                logger.error(f"Downloaded file is not valid audio for song {song_id}")
                if os.path.exists(temp_file):
                    os.remove(temp_file)
                return None
                
            logger.info(f"Successfully downloaded audio for song {song_id} ({properties.get('codec')}, {properties.get('duration')}s)")
            return temp_file
            
        except Exception as e:
            logger.exception(f"Error validating downloaded audio for song {song_id}: {str(e)}")
            if os.path.exists(temp_file):
                os.remove(temp_file)
            return None
            
    except Exception as e:
        logger.exception(f"Error downloading from {url} for song {song_id}: {str(e)}")
        return None

def create_preview(input_file, output_file, song_id=None):
    """Create standardized 30-second preview from source file"""
    try:
        # Get audio properties to determine best start point
        properties = get_audio_properties(input_file)
        if not properties:
            logger.error(f"Could not determine properties for song {song_id}")
            return False
            
        logger.info(f"Creating preview for song {song_id} from {properties.get('duration', 0)}s source")
            
        # Calculate best start point (avoid going beyond track length)
        total_duration = properties.get('duration', 0)
        if total_duration <= PREVIEW_LENGTH:
            # If the whole track is shorter than our preview length, use it all
            start_time = 0
            duration = total_duration
        else:
            # Start at specified offset or at a point that allows full preview length
            start_time = min(START_OFFSET, total_duration - PREVIEW_LENGTH)
            duration = PREVIEW_LENGTH
            
        logger.info(f"Using preview segment from {start_time}s to {start_time + duration}s")
        
        # Create the preview with consistent encoding parameters
        cmd = [
            'ffmpeg',
            '-y',  # Overwrite output if it exists
            '-i', input_file,
            '-ss', str(start_time),  # Start time
            '-t', str(duration),  # Duration
            '-c:a', 'libmp3lame',  # MP3 codec
            '-ar', str(SAMPLE_RATE),  # Sample rate (48kHz)
            '-b:a', BITRATE,  # Bitrate (128kbps)
            '-ac', '2',  # Stereo
            '-af', 'afade=t=in:st=0:d=0.5,afade=t=out:st=' + str(duration - 0.5) + ':d=0.5',  # Add fade in/out
            '-map_metadata', '0:s:0',  # Copy metadata from first stream
            output_file
        ]
        
        # Run ffmpeg
        subprocess.check_call(cmd, stderr=subprocess.STDOUT)
        
        # Verify output file
        if not os.path.exists(output_file) or os.path.getsize(output_file) == 0:
            logger.error(f"Failed to create preview for song {song_id}")
            return False
            
        # Verify output file encoding
        output_props = get_audio_properties(output_file)
        if not output_props:
            logger.error(f"Could not verify output preview for song {song_id}")
            return False
            
        logger.info(f"Created preview for song {song_id}: {output_props.get('duration')}s, {output_props.get('sample_rate')}Hz, {output_props.get('bitrate')/1000 if output_props.get('bitrate') else 'unknown'}kbps")
        return True
        
    except Exception as e:
        logger.exception(f"Error creating preview for song {song_id}: {str(e)}")
        return False

def calculate_audio_content_hash(file_path):
    """Calculate a hash of actual audio content (ignoring metadata)"""
    try:
        # Export 5 seconds of raw PCM from a consistent position to hash
        # This ensures we're comparing actual audio content, not metadata
        temp_wav = f"/tmp/{uuid.uuid4()}.wav"
        
        cmd = [
            'ffmpeg',
            '-y',
            '-i', file_path,
            '-ss', '5',  # Start 5 seconds in
            '-t', '5',   # Take 5 seconds
            '-c:a', 'pcm_s16le',  # Use raw PCM
            '-f', 'wav',  # WAV format 
            temp_wav
        ]
        
        subprocess.check_call(cmd, stderr=subprocess.STDOUT)
        
        # Calculate MD5 hash of the raw audio data
        with open(temp_wav, 'rb') as f:
            data = f.read()
            audio_hash = hashlib.md5(data).hexdigest()
            
        # Clean up
        if os.path.exists(temp_wav):
            os.remove(temp_wav)
            
        return audio_hash
        
    except Exception as e:
        logger.exception(f"Error calculating audio hash for {file_path}: {str(e)}")
        return None

def track_audio_content(hash_file=AUDIO_HASH_FILE):
    """Load or create a tracking file for audio content hashes"""
    try:
        if os.path.exists(hash_file):
            with open(hash_file, 'r') as f:
                return json.load(f)
        return {}
    except Exception as e:
        logger.exception(f"Error loading audio hash file: {str(e)}")
        return {}

def save_audio_content_tracking(hash_data, hash_file=AUDIO_HASH_FILE):
    """Save updated audio content tracking data"""
    try:
        with open(hash_file, 'w') as f:
            json.dump(hash_data, f, indent=2)
        return True
    except Exception as e:
        logger.exception(f"Error saving audio hash file: {str(e)}")
        return False

def process_song(song, hash_tracking):
    """Process a single song to create a proper preview"""
    logger.info(f"Processing song {song.id}: {song.name}")
    
    try:
        # Get the download URL
        download_url = extract_download_url(song)
        if not download_url:
            logger.warning(f"No download URL found for song {song.id}")
            return {
                'success': False,
                'song_id': song.id,
                'error': 'No download URL found'
            }
        
        # Download the audio file
        temp_file = download_audio(download_url, song.id, song.name)
        if not temp_file:
            logger.error(f"Failed to download audio for song {song.id}")
            return {
                'success': False,
                'song_id': song.id,
                'error': 'Failed to download audio'
            }
        
        try:
            # Create unique filename for preview
            preview_filename = f"{uuid.uuid4()}.mp3"
            preview_path = os.path.join(PREVIEW_DIR, preview_filename)
            
            # Create the preview
            if not create_preview(temp_file, preview_path, song.id):
                logger.error(f"Failed to create preview for song {song.id}")
                return {
                    'success': False,
                    'song_id': song.id,
                    'error': 'Failed to create preview'
                }
            
            # Verify audio content uniqueness
            audio_hash = calculate_audio_content_hash(preview_path)
            if not audio_hash:
                logger.error(f"Failed to calculate audio hash for song {song.id}")
                return {
                    'success': False,
                    'song_id': song.id,
                    'error': 'Failed to calculate audio hash'
                }
            
            # Check if this hash already exists in our tracking
            if audio_hash in hash_tracking:
                existing_song = hash_tracking[audio_hash]
                logger.warning(f"Duplicate audio content detected for song {song.id}! Matches song {existing_song['song_id']}")
            
            # Update hash tracking
            hash_tracking[audio_hash] = {
                'song_id': song.id,
                'song_name': song.name,
                'preview_filename': preview_filename,
                'timestamp': time.time()
            }
            
            # Update the song record with the new preview URL
            with transaction.atomic():
                # Get a fresh copy for updating
                song_to_update = CartiCatalog.objects.select_for_update().get(id=song.id)
                preview_url = f"/media/previews/{preview_filename}"
                song_to_update.preview_url = preview_url
                song_to_update.save(update_fields=['preview_url'])
            
            logger.info(f"Successfully created preview for song {song.id}: {preview_url}")
            return {
                'success': True,
                'song_id': song.id,
                'preview_url': preview_url,
                'audio_hash': audio_hash
            }
            
        finally:
            # Clean up temp file
            if temp_file and os.path.exists(temp_file):
                os.remove(temp_file)
                
    except Exception as e:
        logger.exception(f"Error processing song {song.id}: {str(e)}")
        return {
            'success': False,
            'song_id': song.id,
            'error': str(e)
        }

def process_all_songs():
    """Process all songs in the database to create previews"""
    # Backup existing previews
    backup_existing_previews()
    
    # Load audio content tracking
    hash_tracking = track_audio_content()
    logger.info(f"Loaded {len(hash_tracking)} existing audio content hashes")
    
    # Get songs with links (potential sources)
    songs = CartiCatalog.objects.exclude(links__isnull=True).exclude(links__exact='')
    total_count = songs.count()
    logger.info(f"Found {total_count} songs with links")
    
    # Process statistics
    results = {
        'total': total_count,
        'success': 0,
        'failed': 0,
        'duplicates': 0,
        'songs': []
    }
    
    # Process each song
    for i, song in enumerate(songs, 1):
        logger.info(f"Processing song {i}/{total_count}: {song.id} - {song.name}")
        
        # Skip processing if we already have this song in our tracking
        already_processed = False
        for hash_value, song_data in hash_tracking.items():
            if song_data.get('song_id') == song.id:
                logger.info(f"Song {song.id} already has preview in hash tracking, skipping")
                already_processed = True
                results['success'] += 1
                results['songs'].append({
                    'song_id': song.id,
                    'name': song.name,
                    'status': 'already processed',
                    'preview_url': song.preview_url
                })
                break
                
        if already_processed:
            continue
        
        # Process this song
        result = process_song(song, hash_tracking)
        
        if result['success']:
            results['success'] += 1
            results['songs'].append({
                'song_id': song.id,
                'name': song.name,
                'status': 'success',
                'preview_url': result['preview_url']
            })
            
            # Save hash tracking periodically
            if results['success'] % 10 == 0:
                save_audio_content_tracking(hash_tracking)
                
        else:
            results['failed'] += 1
            results['songs'].append({
                'song_id': song.id,
                'name': song.name,
                'status': 'failed',
                'error': result.get('error', 'Unknown error')
            })
        
        # Throttle requests to avoid overloading servers
        time.sleep(1)
    
    # Save final hash tracking
    save_audio_content_tracking(hash_tracking)
    
    # Return results
    logger.info(f"Completed processing {total_count} songs")
    logger.info(f"  Success: {results['success']}")
    logger.info(f"  Failed: {results['failed']}")
    
    return results

def verify_preview_files():
    """Verify all preview files have consistent encoding parameters"""
    if not os.path.exists(PREVIEW_DIR):
        logger.warning(f"Preview directory not found: {PREVIEW_DIR}")
        return
        
    # Get all MP3 files
    mp3_files = [f for f in os.listdir(PREVIEW_DIR) if f.endswith('.mp3')]
    logger.info(f"Verifying {len(mp3_files)} preview files")
    
    verified_count = 0
    issue_count = 0
    
    for filename in mp3_files:
        file_path = os.path.join(PREVIEW_DIR, filename)
        
        try:
            # Get properties
            properties = get_audio_properties(file_path)
            
            if not properties:
                logger.error(f"Could not determine properties for {filename}")
                issue_count += 1
                continue
                
            # Check for correct parameters
            correct_bitrate = properties.get('bitrate', 0) >= 128000
            correct_sample_rate = properties.get('sample_rate') == SAMPLE_RATE
            
            if correct_bitrate and correct_sample_rate:
                verified_count += 1
            else:
                issue_count += 1
                logger.warning(f"File {filename} has incorrect parameters: bitrate={properties.get('bitrate')}, sample_rate={properties.get('sample_rate')}")
                
        except Exception as e:
            logger.exception(f"Error verifying {filename}: {str(e)}")
            issue_count += 1
    
    logger.info(f"Verification complete:")
    logger.info(f"  Verified: {verified_count}")
    logger.info(f"  Issues: {issue_count}")
    
    return {
        'total': len(mp3_files),
        'verified': verified_count,
        'issues': issue_count
    }

def create_test_page():
    """Create a simple HTML page for testing the previews"""
    try:
        # Get a sample of preview files
        if not os.path.exists(PREVIEW_DIR):
            logger.warning(f"Preview directory not found: {PREVIEW_DIR}")
            return False
            
        # Get all MP3 files
        mp3_files = [f for f in os.listdir(PREVIEW_DIR) if f.endswith('.mp3')]
        
        # Limit to 10 random files for the test page
        import random
        sample_files = random.sample(mp3_files, min(10, len(mp3_files)))
        
        # Create the HTML
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Preview Test Page</title>
    <style>
        body {{ font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }}
        .player {{ margin-bottom: 30px; padding: 15px; border: 1px solid #ccc; border-radius: 5px; }}
        audio {{ width: 100%; margin: 10px 0; }}
        button {{ padding: 8px 15px; margin-right: 10px; }}
    </style>
</head>
<body>
    <h1>Audio Preview Test Page</h1>
    <p>This page tests if the audio previews play correctly.</p>
    
    <h2>Random Preview Files</h2>
    
"""
        
        # Add players for each sample file
        for i, filename in enumerate(sample_files, 1):
            html += f"""    <div class="player">
        <h3>File {i}</h3>
        <p>Filename: {filename}</p>
        <audio controls src="/media/previews/{filename}"></audio>
        <p>Direct URL: <a href="/media/previews/{filename}" target="_blank">/media/previews/{filename}</a></p>
        <p>Custom Handler: <a href="/audio-serve/{filename}" target="_blank">/audio-serve/{filename}</a></p>
    </div>
    
"""
        
        # Close the HTML
        html += """    <script>
        // Log when audio files are played
        document.querySelectorAll('audio').forEach(audio => {
            audio.addEventListener('play', function() {
                console.log('Playing:', this.src);
            });
        });
    </script>
</body>
</html>"""
        
        # Write to file
        test_page_path = os.path.join(settings.BASE_DIR, "static", "preview_test.html")
        os.makedirs(os.path.dirname(test_page_path), exist_ok=True)
        
        with open(test_page_path, 'w') as f:
            f.write(html)
            
        logger.info(f"Created test page at {test_page_path}")
        return True
        
    except Exception as e:
        logger.exception(f"Error creating test page: {str(e)}")
        return False

if __name__ == "__main__":
    logger.info("Starting preview refresh process")
    
    # Process all songs
    results = process_all_songs()
    
    # Verify all preview files
    verification = verify_preview_files()
    
    # Create test page
    create_test_page()
    
    # Output final summary
    logger.info("Process complete!")
    logger.info(f"Total songs processed: {results['total']}")
    logger.info(f"Successful previews: {results['success']}")
    logger.info(f"Failed previews: {results['failed']}")
    logger.info(f"Preview files verified: {verification['verified']}/{verification['total']}")