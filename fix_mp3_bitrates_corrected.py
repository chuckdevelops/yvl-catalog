#!/usr/bin/env python3
"""
Script to fix audio preview files by ensuring consistent encoding settings
- Ensures all files use 128kbps bitrate and 48kHz sample rate for browser compatibility
- Preserves all unique audio content (doesn't replace content, just re-encodes)
- Logs details about each file processing
"""

import os
import sys
import shutil
import subprocess
import uuid
import logging
from pathlib import Path

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("bitrate_fix.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Set up Django environment
sys.path.insert(0, str(Path(__file__).resolve().parent))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'carti_project.settings')

import django
django.setup()

from django.conf import settings
from catalog.models import CartiCatalog

def get_audio_properties(file_path):
    """Get audio properties using ffprobe"""
    try:
        # Get bitrate
        bitrate_cmd = [
            'ffprobe', 
            '-v', 'error', 
            '-select_streams', 'a:0',
            '-show_entries', 'stream=bit_rate', 
            '-of', 'default=noprint_wrappers=1:nokey=1', 
            file_path
        ]
        
        try:
            bitrate = subprocess.check_output(bitrate_cmd, text=True).strip()
            if not bitrate:
                # Try format bitrate as fallback
                bitrate_cmd = [
                    'ffprobe', 
                    '-v', 'error', 
                    '-show_entries', 'format=bit_rate', 
                    '-of', 'default=noprint_wrappers=1:nokey=1', 
                    file_path
                ]
                bitrate = subprocess.check_output(bitrate_cmd, text=True).strip()
            
            bitrate = int(bitrate) if bitrate.isdigit() else None
        except Exception as e:
            logger.warning(f"Error getting bitrate: {str(e)}")
            bitrate = None
        
        # Get sample rate
        samplerate_cmd = [
            'ffprobe', 
            '-v', 'error', 
            '-select_streams', 'a:0', 
            '-show_entries', 'stream=sample_rate', 
            '-of', 'default=noprint_wrappers=1:nokey=1', 
            file_path
        ]
        
        try:
            sample_rate = subprocess.check_output(samplerate_cmd, text=True).strip()
            sample_rate = int(sample_rate) if sample_rate.isdigit() else None
        except Exception as e:
            logger.warning(f"Error getting sample rate: {str(e)}")
            sample_rate = None
        
        # Get duration
        duration_cmd = [
            'ffprobe', 
            '-v', 'error', 
            '-show_entries', 'format=duration', 
            '-of', 'default=noprint_wrappers=1:nokey=1', 
            file_path
        ]
        
        try:
            duration = subprocess.check_output(duration_cmd, text=True).strip()
            duration = float(duration) if duration else None
        except Exception as e:
            logger.warning(f"Error getting duration: {str(e)}")
            duration = None
            
        return {
            'bitrate': bitrate,
            'sample_rate': sample_rate,
            'duration': duration
        }
        
    except Exception as e:
        logger.exception(f"Error getting audio properties for {file_path}: {str(e)}")
        return None

def fix_mp3_bitrates():
    """Fix MP3 files with low bitrates"""
    # Get the preview directory
    preview_dir = os.path.join(settings.MEDIA_ROOT, 'previews')
    if not os.path.exists(preview_dir):
        logger.error(f"Preview directory not found: {preview_dir}")
        return
    
    # Create a backup directory if it doesn't exist
    backup_dir = os.path.join(settings.MEDIA_ROOT, 'previews_backup_full')
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
        logger.info(f"Created backup directory: {backup_dir}")
    
    # Get all MP3 files
    mp3_files = [f for f in os.listdir(preview_dir) if f.endswith('.mp3')]
    logger.info(f"Found {len(mp3_files)} MP3 files")
    
    fixed_count = 0
    skipped_count = 0
    error_count = 0
    
    # Process working file last if it exists
    working_file = '56711856-592a-4f2b-9de9-e6781f8deff1.mp3'
    if working_file in mp3_files:
        mp3_files.remove(working_file)
        mp3_files.append(working_file)
    
    for filename in mp3_files:
        file_path = os.path.join(preview_dir, filename)
        
        try:
            # Get current properties
            logger.info(f"Processing {filename}")
            properties = get_audio_properties(file_path)
            
            if not properties:
                logger.error(f"Could not determine properties for {filename}")
                error_count += 1
                continue
                
            logger.info(f"Current properties: {properties}")
            
            # Determine if this file needs fixing
            needs_fixing = (
                properties['bitrate'] is None or 
                properties['bitrate'] < 128000 or  # < 128kbps
                properties['sample_rate'] is None or
                properties['sample_rate'] != 48000  # != 48kHz
            )
            
            if not needs_fixing:
                logger.info(f"File {filename} has good bitrate and sample rate, skipping")
                skipped_count += 1
                continue
            
            # Backup the file first
            backup_path = os.path.join(backup_dir, filename)
            shutil.copy2(file_path, backup_path)
            logger.info(f"Backed up to {backup_path}")
            
            # Re-encode the file with fixed parameters
            tmp_file = f"/tmp/{uuid.uuid4()}.mp3"
            
            cmd = [
                'ffmpeg',
                '-y',  # Overwrite output
                '-i', file_path,
                '-c:a', 'libmp3lame',
                '-ar', '48000',  # 48kHz sample rate
                '-b:a', '128k',   # 128kbps bitrate
                '-map_metadata', '0',  # Copy all metadata
                tmp_file
            ]
            
            subprocess.check_call(cmd, stderr=subprocess.STDOUT)
            
            # Verify the newly created file
            if os.path.exists(tmp_file) and os.path.getsize(tmp_file) > 0:
                # Get new properties
                new_properties = get_audio_properties(tmp_file)
                logger.info(f"New properties: {new_properties}")
                
                # Replace the original file
                shutil.move(tmp_file, file_path)
                logger.info(f"Successfully fixed {filename}")
                
                fixed_count += 1
            else:
                logger.error(f"Failed to create fixed file for {filename}")
                error_count += 1
                
        except Exception as e:
            logger.exception(f"Error processing {filename}: {str(e)}")
            error_count += 1
    
    logger.info("Finished processing all files")
    logger.info(f"  Fixed: {fixed_count}")
    logger.info(f"  Skipped: {skipped_count}")
    logger.info(f"  Errors: {error_count}")
    logger.info(f"  Total: {fixed_count + skipped_count + error_count}")

if __name__ == "__main__":
    fix_mp3_bitrates()