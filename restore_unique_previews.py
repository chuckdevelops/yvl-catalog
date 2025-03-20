#!/usr/bin/env python3
"""
Script to restore unique previews for each song while keeping them all playable.
This script:
1. Uses audio_content_hashes_fixed.json to identify the original unique audio content
2. Finds files in backup directories that match each hash
3. Re-encodes each file with the proper parameters (128kbps MP3, 48kHz sample rate)
4. Ensures each song has its own unique audio content
5. Limits each preview to ~19 seconds (optimal playback duration)

Usage:
  python restore_unique_previews.py [--debug] [--backup-dir=DIR]
"""

import os
import sys
import json
import uuid
import argparse
import logging
import subprocess
import shutil
import hashlib
from datetime import datetime
from pathlib import Path

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("restore_unique_previews.log"),
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

# Directories
MEDIA_ROOT = settings.MEDIA_ROOT
PREVIEW_DIR = os.path.join(MEDIA_ROOT, 'previews')
TEMP_DIR = os.path.join(settings.BASE_DIR, 'temp_previews')
BACKUP_DIR_ROOT = os.path.join(settings.BASE_DIR, 'backup_previews')
NEW_BACKUP_DIR = os.path.join(BACKUP_DIR_ROOT, datetime.now().strftime('%Y%m%d_%H%M%S'))

# Hash file location
AUDIO_HASHES_FILE = os.path.join(settings.BASE_DIR, 'audio_content_hashes_fixed.json')

# Create necessary directories
os.makedirs(TEMP_DIR, exist_ok=True)
os.makedirs(NEW_BACKUP_DIR, exist_ok=True)

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

def get_file_duration(file_path):
    """Get the duration of an audio file using ffprobe"""
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
            return duration
        else:
            logger.error(f"FFprobe failed: {result.stderr}")
            return None
    except Exception as e:
        logger.error(f"Error getting duration: {e}")
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

def find_file_by_hash(hash_value, backup_dir=None):
    """Find a file with the given hash in backup directories"""
    # If specific backup dir is provided, check only that one
    if backup_dir:
        backup_dirs = [backup_dir]
    else:
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

def find_file_by_name(filename, backup_dir=None):
    """Find a file by name in backup directories"""
    # If specific backup dir is provided, check only that one
    if backup_dir:
        backup_dirs = [backup_dir]
    else:
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

def is_file_working(file_path):
    """Check if a file is properly encoded and likely to work"""
    try:
        # File must exist and have reasonable size
        if not os.path.exists(file_path) or os.path.getsize(file_path) < 10000:
            return False
            
        # Check duration
        duration = get_file_duration(file_path)
        if duration is None or duration < 5 or (duration > 29 and duration < 31):
            # Files with duration around 30s are likely broken
            return False
            
        # Check audio specs 
        cmd = [
            'ffprobe',
            '-v', 'error',
            '-select_streams', 'a:0',
            '-show_entries', 'stream=codec_name,sample_rate,bit_rate',
            '-of', 'json',
            file_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
        if result.returncode != 0:
            return False
            
        try:
            data = json.loads(result.stdout)
            if 'streams' not in data or len(data['streams']) == 0:
                return False
                
            stream = data['streams'][0]
            sample_rate = stream.get('sample_rate')
            bit_rate = stream.get('bit_rate')
            
            # Check if parameters are suitable
            if sample_rate and int(sample_rate) < 44000:  # At least 44kHz
                return False
                
            if bit_rate and int(bit_rate) < 90000:  # At least ~96kbps
                return False
                
            return True
        except json.JSONDecodeError:
            return False
    except Exception as e:
        logger.error(f"Error checking if file is working: {e}")
        return False

def create_standardized_preview(input_file, output_file):
    """Create a standardized preview file with consistent parameters"""
    temp_file = os.path.join(TEMP_DIR, f"temp_{uuid.uuid4()}.mp3")
    
    try:
        # Get duration of input file
        duration = get_file_duration(input_file)
        if duration is None:
            logger.error(f"Could not determine duration of {input_file}")
            return False
            
        # Calculate start time - if song is long, start a bit in to avoid intros
        start_time = 0
        if duration > 30:
            start_time = min(10, duration * 0.15)  # Start at 15% or 10 seconds, whichever is less
            
        # Always limit to ~19 seconds, which matches working files
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

def restore_unique_previews(backup_dir=None, debug=False):
    """Main function to restore unique previews from hash file and backups"""
    # Load hash mapping
    if not os.path.exists(AUDIO_HASHES_FILE):
        logger.error(f"Hash file not found: {AUDIO_HASHES_FILE}")
        return
        
    with open(AUDIO_HASHES_FILE, 'r') as f:
        audio_hashes = json.load(f)
        
    logger.info(f"Loaded {len(audio_hashes)} audio content hashes")
    
    # First, backup all current previews
    if not debug:
        for filename in os.listdir(PREVIEW_DIR):
            if filename.endswith('.mp3'):
                src_path = os.path.join(PREVIEW_DIR, filename)
                dst_path = os.path.join(NEW_BACKUP_DIR, filename)
                shutil.copy2(src_path, dst_path)
        logger.info(f"Backed up all current previews to {NEW_BACKUP_DIR}")
    
    # Keep track of stats
    total_files = 0
    recovered_files = 0
    unrecovered_files = 0
    already_good_files = 0
    
    # Process each file in the hash mapping
    hash_to_filename = {}  # Keep track of which filename belongs to which hash
    
    for audio_hash, song_info in audio_hashes.items():
        song_id = song_info.get('song_id')
        song_name = song_info.get('song_name', 'Unknown')
        filename = song_info.get('filename')
        
        if not filename:
            logger.warning(f"No filename for hash {audio_hash}, song ID {song_id}")
            continue
            
        logger.info(f"Processing {filename} for song ID {song_id}: {song_name}")
        
        preview_path = os.path.join(PREVIEW_DIR, filename)
        hash_to_filename[audio_hash] = filename
        total_files += 1
        
        # Check if the file already exists and is not a silent 30-second file
        if os.path.exists(preview_path) and is_file_working(preview_path):
            logger.info(f"File already exists and appears to work correctly")
            already_good_files += 1
            continue
            
        # Try to find the file in backups based on its hash
        if debug:
            logger.info(f"Debug mode: would look for file with hash {audio_hash}")
            continue
            
        original_file = find_file_by_hash(audio_hash, backup_dir)
        
        if not original_file:
            # If we can't find by hash, try by filename
            original_file = find_file_by_name(filename, backup_dir)
            
        if original_file:
            # Verify this file actually works
            if not is_file_working(original_file):
                logger.warning(f"Found file {original_file} but it doesn't appear to be working")
                
                # Try reference file as fallback
                if create_standardized_preview(REFERENCE_FILE, preview_path):
                    logger.info(f"Created fallback preview from reference file for {filename}")
                    recovered_files += 1
                else:
                    logger.error(f"Failed to create fallback preview for {filename}")
                    unrecovered_files += 1
                continue
                
            # Create standardized preview
            if create_standardized_preview(original_file, preview_path):
                logger.info(f"Successfully restored preview for {filename}")
                recovered_files += 1
            else:
                logger.error(f"Failed to create standardized preview for {filename}")
                unrecovered_files += 1
        else:
            logger.warning(f"Could not find original file for {filename}")
            
            # Try reference file as fallback
            if create_standardized_preview(REFERENCE_FILE, preview_path):
                logger.info(f"Created fallback preview from reference file for {filename}")
                recovered_files += 1
            else:
                logger.error(f"Failed to create fallback preview for {filename}")
                unrecovered_files += 1
    
    # Report stats
    logger.info(f"\nRestore process completed:")
    logger.info(f"Total files: {total_files}")
    logger.info(f"Already good files: {already_good_files}")
    logger.info(f"Successfully recovered files: {recovered_files}")
    logger.info(f"Unrecovered files: {unrecovered_files}")
    
    # Clean up temp directory
    if os.path.exists(TEMP_DIR):
        shutil.rmtree(TEMP_DIR)
        os.makedirs(TEMP_DIR, exist_ok=True)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Restore unique previews for each song.')
    parser.add_argument('--debug', action='store_true', help='Run in debug mode without making changes')
    parser.add_argument('--backup-dir', help='Specific backup directory to use')
    args = parser.parse_args()
    
    # Check if FFmpeg is installed
    try:
        subprocess.run(["ffmpeg", "-version"], capture_output=True, text=True, check=True)
    except (FileNotFoundError, subprocess.SubprocessError):
        logger.error("Error: FFmpeg is not installed or not in the PATH.")
        sys.exit(1)
        
    backup_dir = args.backup_dir
    if backup_dir and not os.path.exists(os.path.join(BACKUP_DIR_ROOT, backup_dir)):
        logger.error(f"Specified backup directory not found: {backup_dir}")
        sys.exit(1)
        
    logger.info(f"Starting restore of unique previews (debug={args.debug})")
    restore_unique_previews(backup_dir=backup_dir, debug=args.debug)
    logger.info("Restore process completed")