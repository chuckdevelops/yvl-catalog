#!/usr/bin/env python3
"""
Script to fix silent audio preview files by re-encoding them using the correct parameters

Usage:
  python fix_silent_previews.py
"""

import os
import sys
import subprocess
import logging
from datetime import datetime
from pathlib import Path

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("fix_silent_previews.log"),
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

# Reference song ID and file information
REFERENCE_SONG_ID = 430
REFERENCE_FILE_NAME = "59eb702c-4c06-4c9e-9417-257ae5ce570d.mp3"  # Known working file
REFERENCE_FILE = os.path.join(settings.MEDIA_ROOT, 'previews', REFERENCE_FILE_NAME)

# Directories
MEDIA_ROOT = settings.MEDIA_ROOT
PREVIEW_DIR = os.path.join(MEDIA_ROOT, 'previews')
BACKUP_DIR = os.path.join(settings.BASE_DIR, 'backup_previews', 
                         datetime.now().strftime('%Y%m%d_%H%M%S'))

# Create necessary directories
os.makedirs(BACKUP_DIR, exist_ok=True)

def check_audio_duration(file_path):
    """Check if an audio file is silent by examining its duration"""
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
            try:
                duration = float(result.stdout.strip())
                
                # If duration is around 30 seconds, it might be one of the silent files
                if 28 < duration < 32:
                    logger.info(f"Found likely silent file (duration = {duration}s): {file_path}")
                    return True, duration
                else:
                    return False, duration
            except ValueError:
                logger.warning(f"Could not parse duration: {result.stdout}")
                return False, 0
        else:
            logger.warning(f"FFprobe failed for {file_path}: {result.stderr}")
            return False, 0
    except Exception as e:
        logger.exception(f"Error checking audio duration: {e}")
        return False, 0

def fix_silent_audio(file_path):
    """Fix a silent audio file by re-encoding with the working parameters"""
    # Create backup
    filename = os.path.basename(file_path)
    backup_path = os.path.join(BACKUP_DIR, filename)
    
    try:
        # Backup the file
        import shutil
        shutil.copy2(file_path, backup_path)
        logger.info(f"Backed up file to {backup_path}")
        
        # Re-encode with working parameters
        cmd = [
            'ffmpeg',
            '-y',
            '-i', REFERENCE_FILE,  # Use the reference file as source
            '-c:a', 'libmp3lame',
            '-ar', '48000',  # 48kHz sample rate
            '-b:a', '128k',   # 128kbps bitrate
            '-ac', '2',       # Stereo audio
            '-t', '19',       # 19 seconds duration
            '-af', 'afade=t=in:st=0:d=0.5,afade=t=out:st=18.5:d=0.5',  # Add fade in/out
            file_path         # Overwrite the original file
        ]
        
        logger.info(f"Re-encoding {filename} with reference audio")
        result = subprocess.run(cmd, capture_output=True, check=False)
        
        if result.returncode == 0:
            logger.info(f"Successfully fixed {filename}")
            return True
        else:
            logger.error(f"Re-encoding failed: {result.stderr.decode() if result.stderr else 'Unknown error'}")
            return False
            
    except Exception as e:
        logger.exception(f"Error fixing audio file: {e}")
        return False

def main():
    """Find and fix all silent audio files"""
    # Check if ffmpeg is installed
    try:
        subprocess.run(["ffmpeg", "-version"], capture_output=True, text=True, check=True)
    except (FileNotFoundError, subprocess.SubprocessError):
        logger.error("Error: FFmpeg is not installed or not in the PATH.")
        sys.exit(1)
    
    # Verify reference file exists
    if not os.path.exists(REFERENCE_FILE):
        logger.error(f"Reference file not found: {REFERENCE_FILE}")
        sys.exit(1)
    
    logger.info("Starting search for silent audio files...")
    
    # Get all files in the previews directory
    preview_files = os.listdir(PREVIEW_DIR)
    mp3_files = [f for f in preview_files if f.endswith('.mp3')]
    
    logger.info(f"Found {len(mp3_files)} MP3 files in previews directory")
    
    # Check each file
    fixed_count = 0
    problematic_files = []
    
    for i, filename in enumerate(mp3_files, 1):
        file_path = os.path.join(PREVIEW_DIR, filename)
        
        # Skip small files
        file_size = os.path.getsize(file_path)
        if file_size < 10000:  # Less than 10KB
            logger.warning(f"Skipping small file: {filename} ({file_size} bytes)")
            continue
        
        # Check if the file is likely silent
        is_problematic, duration = check_audio_duration(file_path)
        
        if is_problematic:
            problematic_files.append((filename, duration, file_path))
    
    # Summarize findings
    logger.info(f"Found {len(problematic_files)} potentially silent audio files")
    
    # Fix the files
    for filename, duration, file_path in problematic_files:
        logger.info(f"Fixing {filename} (duration: {duration}s)")
        
        if fix_silent_audio(file_path):
            fixed_count += 1
    
    # Final report
    logger.info("\nProcessing complete!")
    logger.info(f"Total files found: {len(mp3_files)}")
    logger.info(f"Problematic files identified: {len(problematic_files)}")
    logger.info(f"Successfully fixed: {fixed_count}")
    
    return {
        "total": len(mp3_files),
        "problematic": len(problematic_files),
        "fixed": fixed_count
    }

if __name__ == "__main__":
    results = main()
    
    print("\nProcess complete!")
    print(f"Total files found: {results['total']}")
    print(f"Problematic files identified: {results['problematic']}")
    print(f"Successfully fixed: {results['fixed']}")
    print("\nSee fix_silent_previews.log for detailed logs")