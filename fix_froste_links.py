#!/usr/bin/env python3
"""
Script to fix all music.froste.lol preview issues by:
1. Creating a backup of all current preview files
2. Identifying all songs with music.froste.lol links in the database
3. Downloading audio content directly from music.froste.lol
4. Re-encoding with standardized parameters (128kbps, 48kHz, 19-second duration)
5. Updating the database with new preview URLs

This script prioritizes getting correct audio content while maintaining
consistent format across all files.

Usage:
  python fix_froste_links.py [--debug] [--limit=N] [--song-id=ID]
"""

import os
import sys
import json
import uuid
import re
import subprocess
import logging
import time
import argparse
import hashlib
from datetime import datetime
from pathlib import Path

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("fix_froste_links.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Set up Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'carti_project.settings')

import django
django.setup()

from django.conf import settings
from catalog.models import CartiCatalog
from django.db import transaction

# Directories
MEDIA_ROOT = settings.MEDIA_ROOT
PREVIEW_DIR = os.path.join(MEDIA_ROOT, 'previews')
TEMP_DIR = os.path.join(settings.BASE_DIR, 'temp_previews')
BACKUP_DIR = os.path.join(settings.BASE_DIR, 'backup_previews', 
                         datetime.now().strftime('%Y%m%d_%H%M%S'))
DOWNLOAD_DIR = os.path.join(settings.BASE_DIR, 'temp_downloads')

# Hash file location
AUDIO_HASHES_FILE = os.path.join(settings.BASE_DIR, 'audio_content_hashes_fixed.json')

# Create necessary directories
os.makedirs(TEMP_DIR, exist_ok=True)
os.makedirs(BACKUP_DIR, exist_ok=True)
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

def get_file_md5(file_path):
    """Calculate MD5 hash of a file"""
    try:
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    except Exception as e:
        logger.error(f"Error calculating MD5 for {file_path}: {e}")
        return None

def backup_current_previews():
    """Backup all current preview files"""
    logger.info(f"Backing up all current previews to {BACKUP_DIR}")
    count = 0
    for filename in os.listdir(PREVIEW_DIR):
        if filename.endswith('.mp3'):
            src_path = os.path.join(PREVIEW_DIR, filename)
            dst_path = os.path.join(BACKUP_DIR, filename)
            try:
                import shutil
                shutil.copy2(src_path, dst_path)
                count += 1
            except Exception as e:
                logger.error(f"Failed to backup {filename}: {e}")
    logger.info(f"Backed up {count} preview files")
    return count

def extract_song_id_from_froste_url(url):
    """Extract the song ID from a music.froste.lol URL"""
    if not url or 'music.froste.lol/song/' not in url:
        return None
        
    # Extract the song ID from the URL
    song_id_match = re.search(r'/song/([^/\s"\']+)', url)
    if song_id_match:
        return song_id_match.group(1)
    return None

def download_from_froste_cdn(song_id):
    """Download directly from froste.lol CDN"""
    if not song_id:
        return None
        
    try:
        direct_url = f"https://cdn.froste.lol/streams/{song_id}/128"
        output_path = os.path.join(DOWNLOAD_DIR, f"cdn_{uuid.uuid4()}.mp3")
        
        logger.info(f"Downloading from CDN: {direct_url}")
        
        # Use curl to download with proper headers
        cmd = [
            "curl",
            "-L",
            "-A", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "-o", output_path,
            "--max-time", "60",
            direct_url
        ]
        
        result = subprocess.run(cmd, capture_output=True, check=False)
        
        # Check if download succeeded
        if result.returncode == 0 and os.path.exists(output_path) and os.path.getsize(output_path) > 10000:
            logger.info(f"Successfully downloaded from CDN: {os.path.getsize(output_path)} bytes")
            return output_path
        else:
            logger.error(f"CDN download failed: {result.stderr.decode() if hasattr(result, 'stderr') else 'Unknown error'}")
            if os.path.exists(output_path):
                os.remove(output_path)
            return None
            
    except Exception as e:
        logger.exception(f"Error downloading from CDN: {e}")
        return None

def download_from_froste_play(song_id):
    """Download from froste.lol player URL"""
    if not song_id:
        return None
        
    try:
        play_url = f"https://music.froste.lol/song/{song_id}/play"
        output_path = os.path.join(DOWNLOAD_DIR, f"play_{uuid.uuid4()}.mp3")
        
        logger.info(f"Downloading from player URL: {play_url}")
        
        # Use ffmpeg to download the stream
        cmd = [
            "ffmpeg",
            "-y",
            "-user_agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "-i", play_url,
            "-t", "60",  # Limit to 60 seconds
            "-c:a", "copy",
            output_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, check=False)
        
        # Check if download succeeded
        if result.returncode == 0 and os.path.exists(output_path) and os.path.getsize(output_path) > 10000:
            logger.info(f"Successfully downloaded from player URL: {os.path.getsize(output_path)} bytes")
            return output_path
        else:
            logger.error(f"Player URL download failed")
            if os.path.exists(output_path):
                os.remove(output_path)
            return None
            
    except Exception as e:
        logger.exception(f"Error downloading from player URL: {e}")
        return None

def download_from_froste_download(song_id):
    """Download from froste.lol download URL"""
    if not song_id:
        return None
        
    try:
        download_url = f"https://music.froste.lol/song/{song_id}/download"
        output_path = os.path.join(DOWNLOAD_DIR, f"download_{uuid.uuid4()}.mp3")
        
        logger.info(f"Downloading from download URL: {download_url}")
        
        # Use curl to download
        cmd = [
            "curl",
            "-L",
            "-A", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "-o", output_path,
            "--max-time", "60",
            download_url
        ]
        
        result = subprocess.run(cmd, capture_output=True, check=False)
        
        # Check if download succeeded
        if result.returncode == 0 and os.path.exists(output_path) and os.path.getsize(output_path) > 10000:
            logger.info(f"Successfully downloaded from download URL: {os.path.getsize(output_path)} bytes")
            return output_path
        else:
            logger.error(f"Download URL download failed")
            if os.path.exists(output_path):
                os.remove(output_path)
            return None
            
    except Exception as e:
        logger.exception(f"Error downloading from download URL: {e}")
        return None

def download_audio_from_froste(song):
    """Try multiple methods to download audio for a song from froste.lol"""
    # First try to extract music.froste.lol links
    if not song.links:
        return None
        
    froste_links = re.findall(r'https?://music\.froste\.lol/song/[^/\s"\']+', song.links)
    
    if not froste_links:
        logger.warning(f"No music.froste.lol links found for song {song.id}: {song.name}")
        return None
        
    froste_link = froste_links[0]
    song_id = extract_song_id_from_froste_url(froste_link)
    
    if not song_id:
        logger.warning(f"Could not extract song ID from link: {froste_link}")
        return None
        
    logger.info(f"Found music.froste.lol link with song ID: {song_id}")
    
    # Try multiple download methods in order of preference
    methods = [
        (download_from_froste_cdn, "CDN"),
        (download_from_froste_play, "Play URL"),
        (download_from_froste_download, "Download URL")
    ]
    
    for download_func, method_name in methods:
        downloaded_file = download_func(song_id)
        if downloaded_file:
            logger.info(f"Successfully downloaded using {method_name}")
            return downloaded_file
    
    # If we get here, we failed to download
    logger.error(f"All download methods failed for song {song.id}: {song.name}")
    return None

def verify_audio_has_sound(file_path):
    """Verify that an audio file actually contains sound (not silence)"""
    try:
        # Use ffprobe to get audio specs
        cmd = [
            'ffprobe',
            '-v', 'error',
            '-select_streams', 'a:0',
            '-show_entries', 'stream=duration,bit_rate,sample_rate',
            '-of', 'json',
            file_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
        
        if result.returncode != 0:
            logger.warning(f"FFprobe failed: {result.stderr}")
            return False
            
        # Parse the JSON output
        try:
            data = json.loads(result.stdout)
            if 'streams' not in data or len(data['streams']) == 0:
                logger.warning("No audio streams found")
                return False
                
            # File needs to have reasonable properties
            stream = data['streams'][0]
            
            # Perform sound detection using ffmpeg's volumedetect filter
            volume_cmd = [
                'ffmpeg',
                '-i', file_path,
                '-af', 'volumedetect',
                '-f', 'null',
                '-y',
                '/dev/null'
            ]
            
            volume_result = subprocess.run(volume_cmd, capture_output=True, text=True, check=False)
            
            # Check for mean_volume in the output
            if 'mean_volume' in volume_result.stderr:
                # Extract the mean volume value
                mean_vol_match = re.search(r'mean_volume: ([-\d.]+) dB', volume_result.stderr)
                if mean_vol_match:
                    mean_vol = float(mean_vol_match.group(1))
                    # If mean volume is very low (e.g., below -50dB), it might be silent
                    if mean_vol < -50:
                        logger.warning(f"Audio file has very low volume: {mean_vol} dB")
                        return False
            
            return True
            
        except json.JSONDecodeError:
            logger.warning("Could not parse FFprobe output")
            return False
            
    except Exception as e:
        logger.exception(f"Error verifying audio: {e}")
        return False

def create_standardized_preview(input_file, output_file):
    """Create a standardized preview with consistent parameters"""
    try:
        logger.info(f"Creating standardized preview from {input_file}")
        
        # Get duration of input file
        cmd = [
            'ffprobe',
            '-v', 'error',
            '-show_entries', 'format=duration',
            '-of', 'default=noprint_wrappers=1:nokey=1',
            input_file
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
        
        # Default parameters
        start_time = 0
        duration = 30  # Target 30 seconds for previews
        
        # If we can get the duration, calculate a good starting point
        if result.returncode == 0:
            file_duration = float(result.stdout.strip())
            logger.info(f"Source file duration: {file_duration} seconds")
            
            # Choose start point based on file length
            if file_duration > 90:
                # For longer tracks, skip intro and start at 10% of duration
                start_time = min(file_duration * 0.1, 30)
            elif file_duration > 45:
                # For medium tracks, start a bit in
                start_time = 5
            
            logger.info(f"Using start time: {start_time} seconds")
        
        # Process with ffmpeg - use high quality settings
        cmd = [
            'ffmpeg',
            '-y',
            '-ss', str(start_time),
            '-i', input_file,
            '-t', str(duration),
            '-c:a', 'libmp3lame',
            '-ar', '48000',  # 48kHz sample rate
            '-ac', '2',      # Stereo
            '-b:a', '128k',  # 128kbps bitrate
            output_file
        ]
        
        result = subprocess.run(cmd, capture_output=True, check=False)
        
        if result.returncode != 0:
            logger.error(f"FFmpeg failed: {result.stderr.decode() if hasattr(result, 'stderr') else 'Unknown error'}")
            
            # Try simpler approach without fades
            logger.info("Trying simpler FFmpeg approach")
            simple_cmd = [
                'ffmpeg',
                '-y',
                '-ss', str(start_time),
                '-i', input_file,
                '-t', str(duration),
                '-c:a', 'libmp3lame',
                '-ar', '48000',
                '-b:a', '128k',
                output_file
            ]
            
            simple_result = subprocess.run(simple_cmd, capture_output=True, check=False)
            
            if simple_result.returncode != 0:
                logger.error(f"Simple FFmpeg approach also failed")
                return False
        
        # Verify the output file
        if os.path.exists(output_file) and os.path.getsize(output_file) > 10000:
            if verify_audio_has_sound(output_file):
                logger.info(f"Successfully created standardized preview: {os.path.getsize(output_file)} bytes")
                
                # Calculate hash for the new file
                file_hash = get_file_md5(output_file)
                if file_hash:
                    logger.info(f"Preview file hash: {file_hash}")
                
                return True
            else:
                logger.error("Created preview has no sound")
                return False
        else:
            logger.error(f"Output file is missing or too small")
            return False
            
    except Exception as e:
        logger.exception(f"Error creating standardized preview: {e}")
        return False

def update_audio_hashes_file(song_id, song_name, filename, file_path):
    """Update the audio hashes file with the new preview information"""
    try:
        # Calculate hash for the file
        file_hash = get_file_md5(file_path)
        if not file_hash:
            logger.error(f"Could not calculate hash for {file_path}")
            return False
            
        # Load existing hashes if available
        audio_hashes = {}
        if os.path.exists(AUDIO_HASHES_FILE):
            try:
                with open(AUDIO_HASHES_FILE, 'r') as f:
                    audio_hashes = json.load(f)
            except json.JSONDecodeError:
                logger.error(f"Error parsing {AUDIO_HASHES_FILE}, creating new file")
        
        # Add or update the entry
        audio_hashes[file_hash] = {
            "song_id": song_id,
            "song_name": song_name,
            "filename": filename,
            "timestamp": time.time()
        }
        
        # Save the updated file
        with open(AUDIO_HASHES_FILE, 'w') as f:
            json.dump(audio_hashes, f, indent=2)
            
        logger.info(f"Updated {AUDIO_HASHES_FILE} with hash for song {song_id}")
        return True
        
    except Exception as e:
        logger.exception(f"Error updating audio hashes file: {e}")
        return False

def find_songs_with_froste_links():
    """Find all songs with music.froste.lol links"""
    try:
        # Get all songs that have "music.froste.lol" in their links
        songs = CartiCatalog.objects.filter(links__icontains="music.froste.lol")
        logger.info(f"Found {songs.count()} songs with music.froste.lol links")
        return songs
    except Exception as e:
        logger.exception(f"Exception finding songs: {e}")
        return []

def find_song_by_id(song_id):
    """Find a specific song by ID"""
    try:
        song = CartiCatalog.objects.get(id=song_id)
        return [song]  # Return as list for consistency with other find functions
    except CartiCatalog.DoesNotExist:
        logger.error(f"Song with ID {song_id} not found")
        return []
    except Exception as e:
        logger.exception(f"Error finding song by ID: {e}")
        return []

def fix_froste_link_previews(debug=False, limit=None, song_id=None):
    """Fix all songs with music.froste.lol links that have broken previews"""
    # First, back up all current previews
    if not debug:
        backup_count = backup_current_previews()
        logger.info(f"Backed up {backup_count} preview files")
    
    # Find songs to process
    if song_id:
        songs = find_song_by_id(song_id)
        logger.info(f"Processing specific song ID: {song_id}")
    else:
        songs = find_songs_with_froste_links()
    
    if limit and not song_id:
        songs = songs[:limit]
    
    total_count = len(songs)
    if total_count == 0:
        logger.warning("No songs found to process")
        return {
            'total': 0,
            'success': 0,
            'failed': 0
        }
    
    success_count = 0
    failed_count = 0
    
    for i, song in enumerate(songs, 1):
        logger.info(f"[{i}/{total_count}] Processing: {song.name} (ID: {song.id})")
        
        if debug:
            logger.info(f"Debug mode: would download and process audio for song {song.id}")
            continue
            
        # Download audio from froste.lol
        downloaded_file = download_audio_from_froste(song)
        
        if not downloaded_file:
            logger.error(f"Failed to download audio for song {song.id}: {song.name}")
            failed_count += 1
            continue
        
        try:
            # Create a new preview filename
            preview_filename = f"{uuid.uuid4()}.mp3"
            preview_path = os.path.join(PREVIEW_DIR, preview_filename)
            
            # Create the standardized preview
            if create_standardized_preview(downloaded_file, preview_path):
                # Update the song preview URL in the database
                with transaction.atomic():
                    old_preview_url = song.preview_url
                    song.preview_url = f"/media/previews/{preview_filename}"
                    song.save(update_fields=['preview_url'])
                    
                logger.info(f"Updated preview URL from {old_preview_url} to {song.preview_url}")
                
                # Update the audio hashes file
                update_audio_hashes_file(song.id, song.name, preview_filename, preview_path)
                
                success_count += 1
                logger.info(f"Successfully updated preview for song {song.id}: {song.name}")
            else:
                logger.error(f"Failed to create preview for song {song.id}: {song.name}")
                failed_count += 1
        finally:
            # Clean up downloaded file
            if downloaded_file and os.path.exists(downloaded_file):
                os.remove(downloaded_file)
    
    logger.info(f"\nProcessing complete!")
    logger.info(f"Total songs: {total_count}")
    logger.info(f"Successfully fixed: {success_count}")
    logger.info(f"Failed: {failed_count}")
    
    return {
        'total': total_count,
        'success': success_count,
        'failed': failed_count
    }

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Fix preview issues for music.froste.lol links.')
    parser.add_argument('--debug', action='store_true', help='Run in debug mode without making changes')
    parser.add_argument('--limit', type=int, help='Limit the number of songs to process')
    parser.add_argument('--song-id', type=int, help='Process only a specific song ID')
    args = parser.parse_args()
    
    # Check if FFmpeg and curl are installed
    try:
        subprocess.run(["ffmpeg", "-version"], capture_output=True, text=True, check=True)
        subprocess.run(["curl", "--version"], capture_output=True, text=True, check=True)
    except (FileNotFoundError, subprocess.SubprocessError):
        logger.error("Error: FFmpeg or curl is not installed or not in the PATH. Please install them first.")
        sys.exit(1)
        
    logger.info(f"Starting {'debug check' if args.debug else 'fix'} of music.froste.lol previews...")
    
    # Process songs
    results = fix_froste_link_previews(debug=args.debug, limit=args.limit, song_id=args.song_id)
    
    # Print final results
    print("\nProcess complete!")
    print(f"Total songs processed: {results['total']}")
    print(f"Successfully fixed: {results['success']}")
    print(f"Failed: {results['failed']}")
    print("\nSee fix_froste_links.log for detailed logs")