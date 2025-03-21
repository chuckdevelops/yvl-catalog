#!/usr/bin/env python3
"""
Script to process manually downloaded krakenfiles audio files.

After running identify_failed_krakenfiles.py, you can manually download the audio files
from the URLs in the CSV file. Place them in the 'manual_downloads' directory and then
run this script to process them.

This script:
1. Expects MP3 files to be placed in a 'manual_downloads' directory
2. Identifies files by their song_id (name each file as song_id.mp3, e.g., "123.mp3")
3. Processes each file to create a standardized preview
4. Updates the database with the new preview URLs

Usage:
  python manual_process_krakenfiles.py [--debug]

Requirements:
  - ffmpeg
  - Django setup
"""

import os
import sys
import json
import uuid
import logging
import argparse
import subprocess
import hashlib
import time
from datetime import datetime
from pathlib import Path

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("manual_krakenfiles_process.log"),
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
MANUAL_DIR = os.path.join(settings.BASE_DIR, 'manual_downloads')
BACKUP_DIR = os.path.join(settings.BASE_DIR, 'backup_previews', 
                        datetime.now().strftime('%Y%m%d_%H%M%S'))
REPORTS_DIR = os.path.join(settings.BASE_DIR, 'reports')

# Hash file location
AUDIO_HASHES_FILE = os.path.join(settings.BASE_DIR, 'audio_content_hashes_fixed.json')

# Create necessary directories
os.makedirs(MANUAL_DIR, exist_ok=True)
os.makedirs(BACKUP_DIR, exist_ok=True)
os.makedirs(PREVIEW_DIR, exist_ok=True)
os.makedirs(REPORTS_DIR, exist_ok=True)

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

def backup_current_preview(song_id):
    """Backup the current preview file for a song"""
    try:
        song = CartiCatalog.objects.get(id=song_id)
        if song.preview_url:
            # Extract filename from preview_url
            filename = os.path.basename(song.preview_url)
            src_path = os.path.join(PREVIEW_DIR, filename)
            
            if os.path.exists(src_path):
                dst_path = os.path.join(BACKUP_DIR, filename)
                import shutil
                shutil.copy2(src_path, dst_path)
                logger.info(f"Backed up preview for song {song_id}: {filename}")
                return True
    except Exception as e:
        logger.error(f"Failed to backup preview for song {song_id}: {e}")
    
    return False

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
                import re
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

def process_manual_files(debug=False):
    """Process manually downloaded files"""
    # Get list of files in manual directory
    manual_files = [f for f in os.listdir(MANUAL_DIR) if f.endswith('.mp3')]
    logger.info(f"Found {len(manual_files)} manual files")
    
    if not manual_files:
        logger.warning("No manual files found in directory")
        return {'total': 0, 'success': 0, 'failed': 0}
    
    # Process each file
    successful = []
    failed = []
    
    for filename in manual_files:
        # Extract song ID from filename (expected format: "123.mp3")
        try:
            song_id = int(filename.split('.')[0])
        except ValueError:
            logger.error(f"Could not extract song ID from filename: {filename}")
            failed.append({
                'filename': filename,
                'error': 'Invalid filename format. Expected: "song_id.mp3"'
            })
            continue
        
        logger.info(f"Processing manual file for song {song_id}: {filename}")
        
        # Skip in debug mode
        if debug:
            logger.info(f"Debug mode: Would process {filename} for song {song_id}")
            continue
        
        try:
            # Get the song from database
            song = CartiCatalog.objects.get(id=song_id)
            
            # Backup current preview
            backup_current_preview(song_id)
            
            # Path to manual file
            manual_file_path = os.path.join(MANUAL_DIR, filename)
            
            # Create new preview filename
            preview_filename = f"{uuid.uuid4()}.mp3"
            preview_path = os.path.join(PREVIEW_DIR, preview_filename)
            
            # Create standardized preview
            if create_standardized_preview(manual_file_path, preview_path):
                # Update song in database
                with transaction.atomic():
                    old_preview_url = song.preview_url
                    song.preview_url = f"/media/previews/{preview_filename}"
                    song.save(update_fields=['preview_url'])
                
                logger.info(f"Updated preview URL from {old_preview_url} to {song.preview_url}")
                
                # Update audio hashes file
                update_audio_hashes_file(song.id, song.name, preview_filename, preview_path)
                
                successful.append({
                    'id': song.id,
                    'name': song.name,
                    'old_preview_url': old_preview_url,
                    'new_preview_url': song.preview_url
                })
                
                logger.info(f"Successfully processed manual file for song {song_id}")
            else:
                logger.error(f"Failed to create preview for song {song_id}")
                failed.append({
                    'id': song_id,
                    'filename': filename,
                    'error': 'Failed to create standardized preview'
                })
        except Exception as e:
            logger.exception(f"Error processing manual file for song {song_id}: {e}")
            failed.append({
                'id': song_id,
                'filename': filename,
                'error': str(e)
            })
    
    # Generate report
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    report_path = os.path.join(REPORTS_DIR, f"manual_process_report_{timestamp}.json")
    
    report = {
        'timestamp': timestamp,
        'total_processed': len(successful) + len(failed),
        'success_count': len(successful),
        'failed_count': len(failed),
        'successful': successful,
        'failed': failed
    }
    
    # Write report
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)
    
    logger.info(f"Report saved to {report_path}")
    
    return {
        'total': len(successful) + len(failed),
        'success': len(successful),
        'failed': len(failed)
    }

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process manually downloaded krakenfiles audio files.')
    parser.add_argument('--debug', action='store_true', help='Run in debug mode without making changes')
    args = parser.parse_args()
    
    # Check if FFmpeg is installed
    try:
        subprocess.run(["ffmpeg", "-version"], capture_output=True, text=True, check=True)
    except (FileNotFoundError, subprocess.SubprocessError):
        logger.error("Error: FFmpeg is not installed or not in the PATH. Please install it first.")
        sys.exit(1)
    
    # Create the manual_downloads directory if it doesn't exist
    os.makedirs(MANUAL_DIR, exist_ok=True)
    
    # Show instructions
    print("\nManual Krakenfiles Processing")
    print("============================")
    print("This script processes manually downloaded krakenfiles audio files.")
    print(f"1. Place the manually downloaded MP3 files in: {MANUAL_DIR}")
    print("2. Name each file as 'song_id.mp3' (e.g., '123.mp3')")
    print("3. Run this script to process the files\n")
    
    # Check if manual_downloads directory has files
    if not os.path.exists(MANUAL_DIR) or not os.listdir(MANUAL_DIR):
        print(f"No files found in {MANUAL_DIR}")
        print("Please download the files manually and place them in this directory.")
        print("You can use the CSV file generated by identify_failed_krakenfiles.py for the list of failed songs.")
        sys.exit(1)
    
    # Process files
    print(f"{'Debug mode: ' if args.debug else ''}Processing files from {MANUAL_DIR}...")
    results = process_manual_files(debug=args.debug)
    
    # Print summary
    print("\nProcess complete!")
    print(f"Total files processed: {results['total']}")
    print(f"Successfully processed: {results['success']}")
    print(f"Failed: {results['failed']}")
    print("\nSee manual_krakenfiles_process.log for detailed logs")