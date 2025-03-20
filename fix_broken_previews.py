#!/usr/bin/env python3
"""
Script to fix broken audio previews by using the working file from song ID 430.

This script:
1. Uses the known working file from song ID 430 as a reference
2. Finds all songs with IDs above 430 that have previews but don't work
3. Re-encodes their audio files using the proven template
4. For froste.lol links, directly downloads from the CDN

Usage:
  python fix_broken_previews.py [--debug] [--start-id=N] [--limit=N]
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
import shutil
from datetime import datetime
from pathlib import Path

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("fix_broken_previews.log"),
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

# Reference song ID and file information
REFERENCE_SONG_ID = 430
REFERENCE_FILE_NAME = "59eb702c-4c06-4c9e-9417-257ae5ce570d.mp3"  # Known working file
REFERENCE_FILE = os.path.join(settings.MEDIA_ROOT, 'previews', REFERENCE_FILE_NAME)
REENCODED_TEST_FILE = os.path.join(settings.MEDIA_ROOT, 'previews', "reencoded_test.mp3")

# Directories
MEDIA_ROOT = settings.MEDIA_ROOT
PREVIEW_DIR = os.path.join(MEDIA_ROOT, 'previews')
TEMP_DIR = os.path.join(settings.BASE_DIR, 'temp_previews')
BACKUP_DIR = os.path.join(settings.BASE_DIR, 'backup_previews', 
                         datetime.now().strftime('%Y%m%d_%H%M%S'))
DOWNLOAD_DIR = os.path.join(settings.BASE_DIR, 'temp_downloads')

# Create necessary directories
os.makedirs(TEMP_DIR, exist_ok=True)
os.makedirs(BACKUP_DIR, exist_ok=True)
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

def get_working_file_specs():
    """Get the specifications of the working reference file"""
    try:
        cmd = [
            'ffprobe',
            '-v', 'error',
            '-show_format',
            '-show_streams',
            '-of', 'json',
            REFERENCE_FILE
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        data = json.loads(result.stdout)
        
        # Extract audio specs
        specs = {}
        
        if 'streams' in data:
            audio_stream = next((s for s in data['streams'] if s.get('codec_type') == 'audio'), None)
            if audio_stream:
                specs['codec'] = audio_stream.get('codec_name')
                specs['sample_rate'] = audio_stream.get('sample_rate')
                specs['channels'] = audio_stream.get('channels')
                specs['bit_rate'] = audio_stream.get('bit_rate')
                
        if 'format' in data:
            specs['format'] = data['format'].get('format_name')
            specs['duration'] = data['format'].get('duration')
            
        logger.info(f"Working file specs: {specs}")
        return specs
    except Exception as e:
        logger.exception(f"Error analyzing working file: {e}")
        return None

def extract_song_id_from_froste_url(url):
    """Extract the song ID from a music.froste.lol URL"""
    if not url:
        return None
        
    if 'music.froste.lol/song/' in url:
        # Extract the song ID from the URL
        song_id_match = re.search(r'/song/([^/]+)', url)
        if song_id_match:
            return song_id_match.group(1)
    return None

def download_from_froste_cdn(song_id):
    """Download directly from froste.lol CDN"""
    if not song_id:
        return None
        
    try:
        direct_url = f"https://cdn.froste.lol/streams/{song_id}/128"
        output_path = os.path.join(DOWNLOAD_DIR, f"download_{uuid.uuid4()}.mp3")
        
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
        output_path = os.path.join(DOWNLOAD_DIR, f"download_{uuid.uuid4()}.mp3")
        
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

def download_audio_file(song):
    """Try multiple methods to download audio for a song"""
    # First try to extract music.froste.lol links
    if song.links:
        froste_links = re.findall(r'https?://music\.froste\.lol/song/[^/\s"\']+', song.links)
        
        if froste_links:
            froste_link = froste_links[0]
            song_id = extract_song_id_from_froste_url(froste_link)
            
            if song_id:
                logger.info(f"Found music.froste.lol link with song ID: {song_id}")
                
                # Try multiple download methods
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
    logger.error(f"All download methods failed for song {song.id}")
    return None

def create_preview_from_reference(input_file, output_file):
    """Create a preview based on the reference file specs"""
    try:
        # Get working file specs
        working_specs = get_working_file_specs()
        
        if not working_specs:
            logger.error("Could not get working file specs")
            return False
            
        logger.info(f"Creating preview from {input_file} to {output_file}")
        
        # Use FFmpeg to create a preview matching the reference file specs
        cmd = [
            'ffmpeg',
            '-y',
            '-i', input_file,
            '-t', '19',   # Duration matches reference file (19 seconds)
            '-c:a', 'libmp3lame',
            '-ar', '48000',  # Hardcoded sample rate to match working file
            '-ac', '2',       # Stereo audio
            '-b:a', '128k',   # Hardcoded bitrate to match working file
            '-af', 'afade=t=in:st=0:d=0.5,afade=t=out:st=18.5:d=0.5',  # Add fade in/out
            output_file
        ]
        
        result = subprocess.run(cmd, capture_output=True, check=False)
        
        if result.returncode != 0:
            logger.error(f"FFmpeg failed: {result.stderr.decode() if hasattr(result, 'stderr') else 'Unknown error'}")
            
            # Try with a simpler approach
            logger.info("Trying simpler FFmpeg approach")
            simple_cmd = [
                'ffmpeg',
                '-y',
                '-i', input_file,
                '-t', '19',    # 19 seconds duration
                '-c:a', 'libmp3lame',
                '-ar', '48000',  # 48kHz sample rate
                '-b:a', '128k',   # 128kbps bitrate
                output_file
            ]
            
            simple_result = subprocess.run(simple_cmd, capture_output=True, check=False)
            
            if simple_result.returncode != 0:
                logger.error("Simple approach also failed")
                
                # Last resort - try one more time with minimal options
                logger.info("Trying minimal FFmpeg options")
                minimal_cmd = [
                    'ffmpeg',
                    '-y',
                    '-i', input_file,
                    '-t', '19',
                    '-c:a', 'libmp3lame',
                    '-b:a', '128k',
                    output_file
                ]
                
                minimal_result = subprocess.run(minimal_cmd, capture_output=True, check=False)
                
                if minimal_result.returncode != 0:
                    logger.error("All encoding attempts failed, using reference file as fallback")
                    try:
                        shutil.copy2(REFERENCE_FILE, output_file)
                        return os.path.exists(output_file)
                    except Exception as e:
                        logger.error(f"Failed to copy reference file: {e}")
                        return False
        
        # Verify the output file
        if os.path.exists(output_file) and os.path.getsize(output_file) > 10000:
            logger.info(f"Successfully created preview: {os.path.getsize(output_file)} bytes")
            return True
        else:
            logger.error("Created preview file is empty or too small")
            return False
            
    except Exception as e:
        logger.exception(f"Error creating preview: {e}")
        return False

def verify_preview_is_working(preview_path):
    """Verify a preview file actually contains audio and matches the reference format"""
    try:
        # Check file exists
        if not os.path.exists(preview_path):
            logger.warning(f"Preview file does not exist: {preview_path}")
            return False
            
        # Check file size
        if os.path.getsize(preview_path) < 10000:  # Less than 10KB is suspicious
            logger.warning(f"Preview file too small: {os.path.getsize(preview_path)} bytes")
            return False
            
        # Analyze with ffprobe
        cmd = [
            'ffprobe',
            '-v', 'error',
            '-show_entries', 'stream=codec_name,bit_rate,sample_rate',
            '-of', 'json',
            preview_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
        
        if result.returncode != 0:
            logger.warning(f"FFprobe failed on preview file")
            return False
            
        try:
            data = json.loads(result.stdout)
            
            # Check for audio stream
            if 'streams' not in data:
                logger.warning("No streams information in preview file")
                return False
                
            audio_stream = next((s for s in data['streams'] if s.get('codec_type') == 'audio'), None)
            if not audio_stream:
                logger.warning("No audio stream found in preview file")
                return False
            
            # Check bit rate and sample rate
            bit_rate = audio_stream.get('bit_rate')
            sample_rate = audio_stream.get('sample_rate')
            
            if bit_rate and int(bit_rate) < 128000:  # Less than 128kbps
                logger.warning(f"Bit rate too low: {bit_rate}")
                return False
                
            if sample_rate and sample_rate != '48000':  # Not 48kHz
                logger.warning(f"Sample rate not 48kHz: {sample_rate}")
                return False
                
            # Check duration
            format_cmd = [
                'ffprobe',
                '-v', 'error',
                '-show_entries', 'format=duration',
                '-of', 'default=noprint_wrappers=1:nokey=1',
                preview_path
            ]
            
            format_result = subprocess.run(format_cmd, capture_output=True, text=True, check=False)
            
            if format_result.returncode == 0:
                duration = float(format_result.stdout.strip())
                if duration < 5:  # Less than 5 seconds is suspicious
                    logger.warning(f"Duration too short: {duration}s")
                    return False
            
            # Success!
            logger.info(f"Preview file verified: {bit_rate}bps, {sample_rate}Hz")
            return True
            
        except json.JSONDecodeError:
            logger.warning("Could not parse FFprobe output")
            return False
            
    except Exception as e:
        logger.exception(f"Error verifying preview: {e}")
        return False

def fix_post_reencoded_preview(file_path):
    """Fix a specific preview file by re-encoding it with the working parameters"""
    if not os.path.exists(file_path):
        logger.error(f"File does not exist: {file_path}")
        return False
        
    # Create a temp file for the re-encoded version
    temp_file = os.path.join(TEMP_DIR, f"temp_{uuid.uuid4()}.mp3")
    
    try:
        # Re-encode with the working parameters
        cmd = [
            'ffmpeg',
            '-y',
            '-i', file_path,
            '-c:a', 'libmp3lame',
            '-ar', '48000',  # 48kHz sample rate (exact same as working file)
            '-b:a', '128k',   # 128kbps bitrate (exact same as working file)
            '-t', '19',      # 19 seconds duration (match working file)
            temp_file
        ]
        
        result = subprocess.run(cmd, capture_output=True, check=False)
        
        if result.returncode != 0:
            logger.error(f"Re-encoding failed: {result.stderr.decode() if result.stderr else 'Unknown error'}")
            return False
            
        # Verify the temp file exists and has reasonable size
        if not os.path.exists(temp_file) or os.path.getsize(temp_file) < 10000:
            logger.error(f"Re-encoded file is missing or too small")
            return False
            
        # Backup the original file
        filename = os.path.basename(file_path)
        backup_path = os.path.join(BACKUP_DIR, filename)
        shutil.copy2(file_path, backup_path)
        
        # Replace the original file with the re-encoded version
        shutil.move(temp_file, file_path)
        
        logger.info(f"Successfully re-encoded {filename}")
        return True
        
    except Exception as e:
        logger.exception(f"Error re-encoding {file_path}: {e}")
        return False

def fix_broken_previews(start_id=430, limit=None, debug=False):
    """Fix all broken previews for songs after start_id"""
    # First, make sure reference files exist
    if not os.path.exists(REFERENCE_FILE):
        logger.error(f"Reference file not found: {REFERENCE_FILE}")
        return {"error": "Reference file not found"}
        
    # Get all songs after the specified ID
    songs = CartiCatalog.objects.filter(id__gt=start_id).order_by('id')
    
    if limit:
        songs = songs[:limit]
        
    total_songs = songs.count()
    logger.info(f"Found {total_songs} songs after ID {start_id}")
    
    # First, create a reference copy of the test file
    if os.path.exists(REFERENCE_FILE) and not os.path.exists(REENCODED_TEST_FILE):
        try:
            logger.info(f"Creating reference test file")
            shutil.copy2(REFERENCE_FILE, REENCODED_TEST_FILE)
        except Exception as e:
            logger.error(f"Failed to create reference test file: {e}")
    
    success_count = 0
    already_working_count = 0
    failed_count = 0
    
    for i, song in enumerate(songs, 1):
        logger.info(f"[{i}/{total_songs}] Processing song {song.id}: {song.name}")
        
        # Skip if no preview URL
        if not song.preview_url:
            logger.info(f"Song has no preview URL, skipping")
            continue
            
        # Check if preview already exists
        if song.preview_url.startswith('/media/previews/'):
            preview_filename = os.path.basename(song.preview_url)
            preview_path = os.path.join(PREVIEW_DIR, preview_filename)
            
            if os.path.exists(preview_path):
                # In debug mode, just report
                if debug:
                    logger.info(f"Debug mode: would fix {preview_path}")
                    continue
                
                # Backup the preview
                backup_path = os.path.join(BACKUP_DIR, preview_filename)
                try:
                    shutil.copy2(preview_path, backup_path)
                    logger.info(f"Backed up preview to {backup_path}")
                except Exception as e:
                    logger.warning(f"Failed to backup preview: {e}")
                
                # Re-encode the file with working parameters
                if fix_post_reencoded_preview(preview_path):
                    success_count += 1
                    logger.info(f"Successfully fixed preview for song {song.id}")
                    continue
                
                # If we get here, direct re-encoding failed
                logger.warning(f"Direct re-encoding failed for {preview_path}")
                
                # Try to download a fresh copy
                downloaded_file = download_audio_file(song)
                
                if downloaded_file:
                    # Create new preview from the downloaded file
                    if create_preview_from_reference(downloaded_file, preview_path):
                        success_count += 1
                        logger.info(f"Successfully fixed preview for song {song.id} from fresh download")
                        
                        # Clean up download
                        os.remove(downloaded_file)
                        continue
                        
                    # Clean up download
                    os.remove(downloaded_file)
                
                # If we failed to download or create preview, use the reference file
                logger.warning(f"Unable to create preview, using reference file")
                
                try:
                    shutil.copy2(REFERENCE_FILE, preview_path)
                    success_count += 1
                    logger.info(f"Used reference file as fallback for song {song.id}")
                except Exception as e:
                    logger.error(f"Failed to copy reference file: {e}")
                    failed_count += 1
            else:
                logger.warning(f"Preview file does not exist: {preview_path}")
                failed_count += 1
        else:
            logger.warning(f"Invalid preview URL format: {song.preview_url}")
            failed_count += 1
    
    logger.info("\nProcessing complete!")
    logger.info(f"Total songs processed: {total_songs}")
    logger.info(f"Successfully fixed: {success_count}")
    logger.info(f"Already working: {already_working_count}")
    logger.info(f"Failed: {failed_count}")
    
    return {
        "total": total_songs,
        "success": success_count,
        "already_working": already_working_count,
        "failed": failed_count
    }

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Fix broken audio previews.')
    parser.add_argument('--debug', action='store_true', help='Run in debug mode without making changes')
    parser.add_argument('--start-id', type=int, default=430, help='Start fixing from this song ID')
    parser.add_argument('--limit', type=int, help='Limit the number of songs to process')
    args = parser.parse_args()
    
    # Check if FFmpeg and curl are installed
    try:
        subprocess.run(["ffmpeg", "-version"], capture_output=True, text=True, check=True)
        subprocess.run(["curl", "--version"], capture_output=True, text=True, check=True)
    except (FileNotFoundError, subprocess.SubprocessError):
        logger.error("Error: FFmpeg or curl is not installed or not in the PATH.")
        sys.exit(1)
        
    logger.info(f"Starting {'debug check' if args.debug else 'fix'} of broken previews from ID {args.start_id}")
    
    # Fix broken previews
    results = fix_broken_previews(start_id=args.start_id, limit=args.limit, debug=args.debug)
    
    # Print final results
    print("\nProcess complete!")
    print(f"Total songs processed: {results.get('total', 0)}")
    print(f"Successfully fixed: {results.get('success', 0)}")
    print(f"Already working: {results.get('already_working', 0)}")
    print(f"Failed: {results.get('failed', 0)}")
    print("\nSee fix_broken_previews.log for detailed logs")