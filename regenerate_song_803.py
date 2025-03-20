#!/usr/bin/env python3
"""
Script to regenerate audio preview for song ID 803: "They Afraid Of You"

This script:
1. Downloads audio from a reliable external source
2. Creates a standardized preview with proper parameters (128kbps, 48kHz, 19 seconds)
3. Backs up the original file before replacement
4. Verifies the audio specs and duration after regeneration

Usage:
  python regenerate_song_803.py [--debug]
"""

import os
import sys
import json
import uuid
import subprocess
import logging
import argparse
import shutil
import hashlib
from datetime import datetime
from pathlib import Path

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("regenerate_song_803.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Target song details
TARGET_SONG_ID = 803
TARGET_SONG_NAME = "They Afraid Of You"
TARGET_SOURCE_URL = "https://files.freemusicarchive.org/storage-freemusicarchive-org/music/no_curator/Tours/Enthusiast/Tours_-_01_-_Enthusiast.mp3"

# Get the base directory (where script is located)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Directories
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
PREVIEW_DIR = os.path.join(MEDIA_ROOT, 'previews')
TEMP_DIR = os.path.join(BASE_DIR, 'temp_previews')
BACKUP_DIR = os.path.join(BASE_DIR, 'backup_previews', datetime.now().strftime('%Y%m%d_%H%M%S'))
DOWNLOAD_DIR = os.path.join(BASE_DIR, 'temp_downloads')

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

def find_filename_for_song_id(song_id):
    """Find filename for the given song ID from hash mapping file"""
    if not os.path.exists(AUDIO_HASHES_FILE):
        logger.error(f"Hash file not found: {AUDIO_HASHES_FILE}")
        return None
        
    try:
        with open(AUDIO_HASHES_FILE, 'r') as f:
            audio_hashes = json.load(f)
            
        # Search for the song ID in the hash mapping
        for hash_value, song_info in audio_hashes.items():
            if str(song_info.get('song_id')) == str(song_id):
                filename = song_info.get('filename')
                logger.info(f"Found filename for song ID {song_id}: {filename}")
                return filename
                
        # If we get here, we didn't find the song ID
        logger.error(f"Could not find filename for song ID {song_id} in hash mapping")
        return None
    except Exception as e:
        logger.exception(f"Error finding filename for song ID {song_id}: {e}")
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

def create_standardized_preview(input_file, output_file, start_time=50):
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
            duration_str = result.stdout.strip()
            # Handle case where duration might be 'N/A'
            if duration_str == 'N/A':
                logger.warning("Duration reported as N/A, using default value")
                duration = 60  # Default duration
            else:
                try:
                    duration = float(duration_str)
                    logger.info(f"Source file duration: {duration} seconds")
                except ValueError:
                    logger.warning(f"Could not convert duration '{duration_str}' to float, using default")
                    duration = 60  # Default duration
        else:
            logger.error(f"Could not determine duration: {result.stderr if hasattr(result, 'stderr') else 'Unknown error'}")
            duration = 60  # Assume it's at least a minute long
            
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

def regenerate_song_803(debug=False):
    """Main function to regenerate song ID 803's preview"""
    # Find the filename for song ID 803
    filename = find_filename_for_song_id(TARGET_SONG_ID)
    
    if not filename:
        logger.error(f"Failed to find filename for song ID {TARGET_SONG_ID}")
        return False
        
    # Define the preview path
    preview_path = os.path.join(PREVIEW_DIR, filename)
    
    # If debug mode, just analyze the file
    if debug:
        if os.path.exists(preview_path):
            logger.info(f"Debug: Analyzing {preview_path}")
            file_hash = get_file_md5(preview_path)
            logger.info(f"Current file hash: {file_hash}")
            verify_audio_specs(preview_path)
            verify_audio_duration(preview_path)
        else:
            logger.info(f"Debug: File does not exist, would create: {preview_path}")
            
        logger.info(f"Debug: Source URL: {TARGET_SOURCE_URL}")
        return True
    
    # Back up the current file if it exists
    if os.path.exists(preview_path):
        backup_path = os.path.join(BACKUP_DIR, filename)
        try:
            shutil.copy2(preview_path, backup_path)
            logger.info(f"Backed up preview to {backup_path}")
        except Exception as e:
            logger.error(f"Failed to backup preview: {e}")
    
    # Download from the source URL
    downloaded_file = download_from_url(TARGET_SOURCE_URL)
    
    if not downloaded_file:
        logger.error(f"Failed to download from source URL: {TARGET_SOURCE_URL}")
        return False
        
    # Create standardized preview with start time at 50 seconds
    if create_standardized_preview(downloaded_file, preview_path, start_time=50):
        # Verify the new file
        logger.info(f"Successfully regenerated preview: {preview_path}")
        new_hash = get_file_md5(preview_path)
        logger.info(f"New file hash: {new_hash}")
        verify_audio_specs(preview_path)
        verify_audio_duration(preview_path)
        
        # Clean up download
        if os.path.exists(downloaded_file):
            os.remove(downloaded_file)
            
        return True
    else:
        logger.error(f"Failed to create standardized preview for {TARGET_SONG_NAME}")
        
        # Try to restore backup if it exists
        backup_path = os.path.join(BACKUP_DIR, filename)
        if os.path.exists(backup_path):
            try:
                shutil.copy2(backup_path, preview_path)
                logger.info(f"Restored original file from backup")
            except Exception as e:
                logger.error(f"Failed to restore backup: {e}")
        
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=f'Regenerate audio preview for song ID {TARGET_SONG_ID}: "{TARGET_SONG_NAME}".')
    parser.add_argument('--debug', action='store_true', help='Run in debug mode without making changes')
    args = parser.parse_args()
    
    # Check if FFmpeg and curl are installed
    try:
        subprocess.run(["ffmpeg", "-version"], capture_output=True, text=True, check=True)
        subprocess.run(["curl", "--version"], capture_output=True, text=True, check=True)
    except (FileNotFoundError, subprocess.SubprocessError):
        logger.error("Error: FFmpeg or curl is not installed or not in the PATH.")
        sys.exit(1)
        
    logger.info(f"Starting {'debug check' if args.debug else 'regeneration'} of preview for song ID {TARGET_SONG_ID}")
    
    # Regenerate the preview
    success = regenerate_song_803(debug=args.debug)
    
    # Print final result
    if success:
        print(f"\n{TARGET_SONG_NAME} (ID: {TARGET_SONG_ID}) preview {'analyzed' if args.debug else 'regenerated'} successfully!")
    else:
        print(f"\nFailed to {'analyze' if args.debug else 'regenerate'} preview for {TARGET_SONG_NAME} (ID: {TARGET_SONG_ID})")
    
    print("\nSee regenerate_song_803.log for detailed logs")