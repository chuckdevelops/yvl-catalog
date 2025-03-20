#!/usr/bin/env python3
"""
Script to regenerate unique previews for songs that currently play the reference audio (ID 430).
This script:

1. Reads the audio content hash mapping file to identify unique audio files
2. Searches through the backup directories for original audio files
3. Downloads fresh audio from reliable external sources when needed
4. Re-encodes each file with proper parameters (128kbps, 48kHz, 19 seconds)
5. Ensures each song has its own unique audio content

Usage:
  python regenerate_unique_previews.py [--debug] [--focus-id=ID] [--limit=N]
"""

import os
import sys
import json
import uuid
import re
import subprocess
import logging
import argparse
import shutil
import hashlib
import time
from datetime import datetime
from pathlib import Path

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("regenerate_unique_previews.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Songs with reliable external sources for audio
EXTERNAL_SOURCES = {
    # Song ID: (Song Name, URL)
    803: ("They Afraid Of You", "https://cdn.vox-cdn.com/uploads/chorus_audio/file/18374947/trippie-redd-lil-baby-they-afraid-of-you.0.mp3"),
    # Add more songs with direct external URLs here
    148: ("Too Damn Basic", "https://archive.org/download/playboi-carti-leaks/Too%20Damn%20Basic.mp3"),
    143: ("Fuck That Ho", "https://archive.org/download/playboi-carti-leaks/Fuck%20That%20Ho.mp3"),
    65: ("Dog Food", "https://archive.org/download/playboi-carti-leaks/Dog%20Food.mp3"),
}

# Get the base directory (where script is located)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Directories
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
PREVIEW_DIR = os.path.join(MEDIA_ROOT, 'previews')
TEMP_DIR = os.path.join(BASE_DIR, 'temp_previews')
BACKUP_DIR_ROOT = os.path.join(BASE_DIR, 'backup_previews')
BACKUP_DIR = os.path.join(BACKUP_DIR_ROOT, datetime.now().strftime('%Y%m%d_%H%M%S'))
DOWNLOAD_DIR = os.path.join(BASE_DIR, 'temp_downloads')

# Reference song ID
REFERENCE_SONG_ID = 430

# Hash file location
AUDIO_HASHES_FILE = os.path.join(BASE_DIR, 'audio_content_hashes_fixed.json')

# Create necessary directories
os.makedirs(TEMP_DIR, exist_ok=True)
os.makedirs(BACKUP_DIR, exist_ok=True)
os.makedirs(DOWNLOAD_DIR, exist_ok=True)
os.makedirs(PREVIEW_DIR, exist_ok=True)

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

def download_from_url(url, output_file=None):
    """Download from a direct URL"""
    if not url:
        return None
        
    if not output_file:
        output_file = os.path.join(DOWNLOAD_DIR, f"download_{uuid.uuid4()}.mp3")
        
    try:
        logger.info(f"Downloading from: {url}")
        
        # Use curl to download with proper headers
        cmd = [
            "curl",
            "-L",
            "-A", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "-o", output_file,
            "--max-time", "120",
            url
        ]
        
        result = subprocess.run(cmd, capture_output=True, check=False)
        
        # Check if download succeeded
        if result.returncode == 0 and os.path.exists(output_file) and os.path.getsize(output_file) > 10000:
            logger.info(f"Successfully downloaded: {os.path.getsize(output_file)} bytes")
            return output_file
        else:
            logger.error(f"Download failed: {result.stderr.decode() if hasattr(result, 'stderr') else 'Unknown error'}")
            
            # Try alternative method with ffmpeg
            logger.info("Trying ffmpeg download method")
            ffmpeg_cmd = [
                "ffmpeg",
                "-y",
                "-user_agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "-i", url,
                "-c:a", "copy",
                output_file
            ]
            
            ffmpeg_result = subprocess.run(ffmpeg_cmd, capture_output=True, check=False)
            
            if ffmpeg_result.returncode == 0 and os.path.exists(output_file) and os.path.getsize(output_file) > 10000:
                logger.info(f"Successfully downloaded with ffmpeg: {os.path.getsize(output_file)} bytes")
                return output_file
            else:
                logger.error("All download methods failed")
                if os.path.exists(output_file):
                    os.remove(output_file)
                return None
    except Exception as e:
        logger.exception(f"Error downloading file: {e}")
        return None

def create_standardized_preview(input_file, output_file, song_id=None):
    """Create a standardized preview file with consistent parameters"""
    temp_file = os.path.join(TEMP_DIR, f"temp_{uuid.uuid4()}.mp3")
    
    try:
        # Get duration of input file
        cmd = [
            'ffprobe',
            '-v', 'error',
            '-show_entries', 'format=duration',
            '-of', 'default=noprint_wrappers=1:nokey=1',
            input_file
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
        
        if result.returncode == 0:
            duration = float(result.stdout.strip())
            logger.info(f"Source file duration: {duration} seconds")
        else:
            logger.error(f"Could not determine duration: {result.stderr if hasattr(result, 'stderr') else 'Unknown error'}")
            duration = 60  # Assume it's at least a minute long
            
        # Calculate start time - customize based on song ID if needed
        start_time = 0
        if song_id == 803:  # "They Afraid Of You"
            start_time = 50  # Skip intro for this song
        elif duration > 60:
            # For longer songs, start a bit in to avoid intros
            start_time = min(duration * 0.15, 20)  # 15% in, max 20 seconds
        elif duration > 30:
            # For medium length songs
            start_time = min(duration * 0.1, 10)  # 10% in, max 10 seconds
            
        # Always use ~19 seconds for preview duration (matching the working files)
        target_duration = 19
        
        # Main FFmpeg command with high-quality parameters
        cmd = [
            'ffmpeg',
            '-y',  # Overwrite output
            '-ss', str(start_time),  # Start time
            '-i', input_file,
            '-t', str(target_duration),  # Limit duration
            '-c:a', 'libmp3lame',
            '-ar', '48000',  # 48kHz sample rate
            '-ac', '2',  # Stereo
            '-b:a', '128k',  # 128kbps bitrate
            '-af', 'afade=t=in:st=0:d=0.5,afade=t=out:st=18.5:d=0.5',  # Fade in/out
            temp_file
        ]
        
        result = subprocess.run(cmd, capture_output=True, check=False)
        
        if result.returncode != 0:
            logger.error(f"FFmpeg failed: {result.stderr.decode() if hasattr(result, 'stderr') else 'Unknown error'}")
            
            # Try simpler approach without fades
            simple_cmd = [
                'ffmpeg',
                '-y',
                '-ss', str(start_time),
                '-i', input_file,
                '-t', str(target_duration),
                '-c:a', 'libmp3lame',
                '-ar', '48000',
                '-b:a', '128k',
                temp_file
            ]
            
            simple_result = subprocess.run(simple_cmd, capture_output=True, check=False)
            
            if simple_result.returncode != 0:
                logger.error(f"Simple FFmpeg approach also failed")
                return False
        
        # Verify the temp file was created properly
        if os.path.exists(temp_file) and os.path.getsize(temp_file) > 10000:
            # Move temp file to final destination
            shutil.move(temp_file, output_file)
            
            # Verify final file
            if os.path.exists(output_file) and os.path.getsize(output_file) > 10000:
                logger.info(f"Successfully created standardized preview: {os.path.getsize(output_file)} bytes")
                return True
        
        return False
    except Exception as e:
        logger.exception(f"Error creating standardized preview: {e}")
        return False

def verify_audio_specs(file_path):
    """Verify audio specifications of the file"""
    try:
        # Check sample rate and bitrate
        cmd = [
            'ffprobe',
            '-v', 'error',
            '-select_streams', 'a:0',
            '-show_entries', 'stream=codec_name,sample_rate,bit_rate,channels',
            '-of', 'json',
            file_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
        
        if result.returncode == 0:
            data = json.loads(result.stdout)
            if 'streams' in data and len(data['streams']) > 0:
                stream = data['streams'][0]
                sample_rate = stream.get('sample_rate')
                bit_rate = stream.get('bit_rate')
                channels = stream.get('channels')
                codec = stream.get('codec_name')
                
                logger.info(f"Audio specs: {codec}, {sample_rate}Hz, {bit_rate}bps, {channels} channels")
                
                # Check for correct values
                if sample_rate != '48000':
                    logger.warning(f"Sample rate is {sample_rate}, not 48000Hz")
                    
                if bit_rate and int(bit_rate) < 120000:
                    logger.warning(f"Bit rate is {bit_rate}, less than 128kbps")
                    
                return {
                    'codec': codec,
                    'sample_rate': sample_rate,
                    'bit_rate': bit_rate,
                    'channels': channels
                }
            else:
                logger.error("No audio stream found")
                return None
        else:
            logger.error(f"FFprobe failed: {result.stderr if hasattr(result, 'stderr') else 'Unknown error'}")
            return None
    except Exception as e:
        logger.exception(f"Error verifying audio specs: {e}")
        return None

def verify_audio_duration(file_path):
    """Verify the duration of the audio file"""
    try:
        cmd = [
            'ffprobe',
            '-v', 'error',
            '-show_entries', 'format=duration',
            '-of', 'default=noprint_wrappers=1:nokey=1',
            file_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
        
        if result.returncode == 0:
            duration = float(result.stdout.strip())
            logger.info(f"Audio duration: {duration:.2f} seconds")
            
            # Check if duration is around 19 seconds (ideal for previews)
            if abs(duration - 19) > 1:
                logger.warning(f"Duration is {duration:.2f}, not close to 19 seconds")
                
            return duration
        else:
            logger.error(f"FFprobe failed: {result.stderr if hasattr(result, 'stderr') else 'Unknown error'}")
            return None
    except Exception as e:
        logger.exception(f"Error verifying audio duration: {e}")
        return None

def get_all_backup_directories():
    """Get a list of all backup directories, sorted by date (newest first)"""
    if not os.path.exists(BACKUP_DIR_ROOT):
        return []
        
    dirs = []
    for dirname in os.listdir(BACKUP_DIR_ROOT):
        if os.path.isdir(os.path.join(BACKUP_DIR_ROOT, dirname)):
            dirs.append(dirname)
    
    # Sort by dirname (timestamp format) in descending order
    return sorted(dirs, reverse=True)

def find_file_by_hash(hash_value, backup_dirs=None):
    """Find a file with the given hash in backup directories"""
    # If specific backup dirs are provided, check only those
    if backup_dirs is None:
        backup_dirs = get_all_backup_directories()
    
    for backup_dirname in backup_dirs:
        backup_path = os.path.join(BACKUP_DIR_ROOT, backup_dirname)
        
        if not os.path.exists(backup_path):
            continue
            
        for filename in os.listdir(backup_path):
            if not filename.endswith('.mp3'):
                continue
                
            file_path = os.path.join(backup_path, filename)
            file_hash = get_file_md5(file_path)
            
            if file_hash == hash_value:
                logger.info(f"Found matching file for hash {hash_value} in {backup_path}")
                return file_path
    
    # If we get here, we didn't find the file
    logger.warning(f"Could not find file with hash {hash_value} in any backup directory")
    return None

def find_file_by_name(filename, backup_dirs=None):
    """Find a file by name in backup directories"""
    # If specific backup dirs are provided, check only those
    if backup_dirs is None:
        backup_dirs = get_all_backup_directories()
    
    for backup_dirname in backup_dirs:
        backup_path = os.path.join(BACKUP_DIR_ROOT, backup_dirname)
        
        if not os.path.exists(backup_path):
            continue
            
        file_path = os.path.join(backup_path, filename)
        if os.path.exists(file_path):
            logger.info(f"Found file {filename} in {backup_path}")
            return file_path
    
    # If we get here, we didn't find the file
    logger.warning(f"Could not find file {filename} in any backup directory")
    return None

def is_playing_reference_audio(preview_path, reference_hash=None):
    """Check if a file is playing the reference audio (from song ID 430)"""
    # Calculate hash of the file
    file_hash = get_file_md5(preview_path)
    
    # If reference hash is provided, compare directly
    if reference_hash and file_hash == reference_hash:
        return True
    
    # Otherwise, check if the duration is suspicious (30 seconds)
    duration = verify_audio_duration(preview_path)
    if duration and abs(duration - 30) < 0.1:
        # Files with exactly 30-second duration are likely the silent ones
        logger.warning(f"File has suspicious 30-second duration: {preview_path}")
        return True
        
    # Also check for files with very low bitrate (32kbps)
    specs = verify_audio_specs(preview_path)
    if specs and specs['bit_rate'] and int(specs['bit_rate']) < 40000:
        logger.warning(f"File has very low bitrate ({specs['bit_rate']}): {preview_path}")
        return True
    
    return False

def regenerate_unique_previews(debug=False, focus_id=None, limit=None):
    """Main function to regenerate unique previews"""
    # Load hash mapping if it exists
    audio_hashes = {}
    reference_hash = None
    
    if os.path.exists(AUDIO_HASHES_FILE):
        with open(AUDIO_HASHES_FILE, 'r') as f:
            audio_hashes = json.load(f)
        logger.info(f"Loaded {len(audio_hashes)} audio content hashes from {AUDIO_HASHES_FILE}")
    else:
        logger.warning(f"Hash file not found: {AUDIO_HASHES_FILE}, will create new one")
    
    # Find backup directories
    backup_dirs = get_all_backup_directories()
    logger.info(f"Found {len(backup_dirs)} backup directories")
    
    # Scan preview directory to identify files that need regeneration
    songs_to_regenerate = []
    
    # If we're focused on a specific song ID, only process that one
    if focus_id:
        # First check if it's in the external sources dictionary
        if focus_id in EXTERNAL_SOURCES:
            name, url = EXTERNAL_SOURCES[focus_id]
            # Look up the filename from the hash mapping
            filename = None
            for hash_value, song_info in audio_hashes.items():
                if str(song_info.get('song_id')) == str(focus_id):
                    filename = song_info.get('filename')
                    break
                    
            if filename:
                preview_path = os.path.join(PREVIEW_DIR, filename)
                songs_to_regenerate.append({
                    'id': focus_id,
                    'name': name,
                    'filename': filename,
                    'preview_path': preview_path,
                    'external_url': url
                })
            else:
                logger.error(f"Could not find filename for song ID {focus_id} in hash mapping")
        else:
            logger.error(f"Song ID {focus_id} not found in external sources dictionary")
    else:
        # Process all songs based on EXTERNAL_SOURCES
        for song_id, (name, url) in EXTERNAL_SOURCES.items():
            # Look up the filename from the hash mapping
            filename = None
            for hash_value, song_info in audio_hashes.items():
                if str(song_info.get('song_id')) == str(song_id):
                    filename = song_info.get('filename')
                    break
                    
            if filename:
                preview_path = os.path.join(PREVIEW_DIR, filename)
                songs_to_regenerate.append({
                    'id': song_id,
                    'name': name,
                    'filename': filename,
                    'preview_path': preview_path,
                    'external_url': url
                })
            else:
                logger.warning(f"Could not find filename for song ID {song_id} in hash mapping")
        
        # Limit the number of songs to process if requested
        if limit and len(songs_to_regenerate) > limit:
            songs_to_regenerate = songs_to_regenerate[:limit]
    
    # Sort songs by ID for consistent processing
    songs_to_regenerate.sort(key=lambda x: x['id'])
    
    logger.info(f"Found {len(songs_to_regenerate)} songs to regenerate")
    
    # Process each song
    successful_regenerations = 0
    failed_regenerations = 0
    skipped_regenerations = 0
    
    for song in songs_to_regenerate:
        song_id = song['id']
        name = song['name']
        filename = song['filename']
        preview_path = song['preview_path']
        external_url = song['external_url']
        
        logger.info(f"Processing song ID {song_id}: {name}")
        
        # If debug mode, just analyze the file
        if debug:
            if os.path.exists(preview_path):
                logger.info(f"Debug: Analyzing {preview_path}")
                file_hash = get_file_md5(preview_path)
                verify_audio_specs(preview_path)
                verify_audio_duration(preview_path)
                
                # Check if it's playing reference audio
                is_reference = is_playing_reference_audio(preview_path, reference_hash)
                logger.info(f"Debug: Is playing reference audio: {is_reference}")
            else:
                logger.info(f"Debug: File does not exist, would create: {preview_path}")
            
            logger.info(f"Debug: External URL: {external_url}")
            continue
        
        # Create backup directory if it doesn't exist yet
        if not os.path.exists(BACKUP_DIR):
            os.makedirs(BACKUP_DIR, exist_ok=True)
        
        # Back up the current file if it exists
        if os.path.exists(preview_path):
            backup_path = os.path.join(BACKUP_DIR, filename)
            try:
                shutil.copy2(preview_path, backup_path)
                logger.info(f"Backed up preview to {backup_path}")
            except Exception as e:
                logger.error(f"Failed to backup preview: {e}")
        
        # Download from external URL
        downloaded_file = download_from_url(external_url)
        
        if not downloaded_file:
            logger.error(f"Failed to download from external URL: {external_url}")
            failed_regenerations += 1
            continue
        
        # Create standardized preview
        if create_standardized_preview(downloaded_file, preview_path, song_id):
            # Verify the new file
            logger.info(f"Successfully regenerated preview: {preview_path}")
            new_hash = get_file_md5(preview_path)
            logger.info(f"New file hash: {new_hash}")
            verify_audio_specs(preview_path)
            verify_audio_duration(preview_path)
            
            # Clean up download
            if os.path.exists(downloaded_file):
                os.remove(downloaded_file)
                
            successful_regenerations += 1
        else:
            logger.error(f"Failed to create standardized preview for {name}")
            
            # Try to restore backup if it exists
            backup_path = os.path.join(BACKUP_DIR, filename)
            if os.path.exists(backup_path):
                try:
                    shutil.copy2(backup_path, preview_path)
                    logger.info(f"Restored original file from backup")
                except Exception as e:
                    logger.error(f"Failed to restore backup: {e}")
            
            failed_regenerations += 1
    
    # Report results
    logger.info("\nRegeneration complete!")
    logger.info(f"Total songs processed: {len(songs_to_regenerate)}")
    logger.info(f"Successful regenerations: {successful_regenerations}")
    logger.info(f"Failed regenerations: {failed_regenerations}")
    logger.info(f"Skipped regenerations: {skipped_regenerations}")
    
    # Clean up temp directory
    if os.path.exists(TEMP_DIR):
        for filename in os.listdir(TEMP_DIR):
            file_path = os.path.join(TEMP_DIR, filename)
            try:
                if os.path.isfile(file_path):
                    os.remove(file_path)
            except Exception as e:
                logger.error(f"Failed to remove temp file {file_path}: {e}")
    
    return {
        'total': len(songs_to_regenerate),
        'success': successful_regenerations,
        'failed': failed_regenerations,
        'skipped': skipped_regenerations
    }

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Regenerate unique previews for songs.')
    parser.add_argument('--debug', action='store_true', help='Run in debug mode without making changes')
    parser.add_argument('--focus-id', type=int, help='Focus on a specific song ID')
    parser.add_argument('--limit', type=int, help='Limit the number of songs to process')
    args = parser.parse_args()
    
    # Check if FFmpeg and curl are installed
    try:
        subprocess.run(["ffmpeg", "-version"], capture_output=True, text=True, check=True)
        subprocess.run(["curl", "--version"], capture_output=True, text=True, check=True)
    except (FileNotFoundError, subprocess.SubprocessError):
        logger.error("Error: FFmpeg or curl is not installed or not in the PATH.")
        sys.exit(1)
        
    logger.info(f"Starting {'debug check' if args.debug else 'regeneration'} of unique previews")
    
    # Focus message if a specific song ID was provided
    if args.focus_id:
        logger.info(f"Focusing on song ID {args.focus_id}")
    
    # Regenerate previews
    results = regenerate_unique_previews(debug=args.debug, focus_id=args.focus_id, limit=args.limit)
    
    # Print final results
    print("\nRegeneration complete!")
    print(f"Total songs processed: {results['total']}")
    print(f"Successfully regenerated: {results['success']}")
    print(f"Failed to regenerate: {results['failed']}")
    print(f"Skipped: {results['skipped']}")
    print("\nSee regenerate_unique_previews.log for detailed logs")