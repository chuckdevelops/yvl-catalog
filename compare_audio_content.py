#!/usr/bin/env python3
"""
Script to compare audio content between MP3 files to check for uniqueness.

This script:
1. Lists all MP3 files in the previews directory
2. Extracts a 5-second audio sample from each file
3. Computes a hash of the audio content (not just the file)
4. Compares the hashes to identify duplicate audio content
"""

import os
import sys
import subprocess
import hashlib
import logging
from collections import defaultdict
from pathlib import Path

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("audio_comparison.log"),
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

def get_audio_sample(file_path, start_time=0, duration=5):
    """
    Extract a raw audio sample from the MP3 file.
    
    Arguments:
    file_path -- Path to the MP3 file
    start_time -- Start time in seconds (default: 0)
    duration -- Duration in seconds (default: 5)
    
    Returns:
    bytes -- Raw audio sample or None if extraction failed
    """
    try:
        # Create a temporary WAV file for the sample
        temp_wav = f"/tmp/{os.path.basename(file_path)}.wav"
        
        # Use ffmpeg to extract a segment of audio in raw PCM format
        cmd = [
            'ffmpeg',
            '-y',  # Overwrite output file
            '-i', file_path,  # Input file
            '-ss', str(start_time),  # Start time
            '-t', str(duration),  # Duration
            '-acodec', 'pcm_s16le',  # PCM 16-bit encoding
            '-ar', '16000',  # Sample rate 16kHz for consistency
            '-ac', '1',  # Mono audio
            '-f', 'wav',  # WAV format
            temp_wav  # Output file
        ]
        
        subprocess.run(cmd, check=True, capture_output=True)
        
        # Read the raw audio data from the WAV file
        # Skip the WAV header (first 44 bytes) to get just the audio data
        with open(temp_wav, 'rb') as f:
            f.seek(44)  # Skip the WAV header
            sample_data = f.read()
            
        # Clean up temporary file
        os.remove(temp_wav)
        
        return sample_data
        
    except subprocess.CalledProcessError as e:
        logger.error(f"Error extracting audio sample from {file_path}: {e}")
        logger.error(f"STDOUT: {e.stdout.decode('utf-8', errors='ignore')}")
        logger.error(f"STDERR: {e.stderr.decode('utf-8', errors='ignore')}")
        return None
    except Exception as e:
        logger.exception(f"Error extracting audio sample from {file_path}: {e}")
        return None

def compute_audio_hash(audio_data):
    """Compute a hash of the audio data"""
    if not audio_data or len(audio_data) == 0:
        return None
        
    return hashlib.md5(audio_data).hexdigest()

def compare_audio_files():
    """Compare all audio files in the previews directory for content uniqueness"""
    preview_dir = os.path.join(settings.MEDIA_ROOT, 'previews')
    
    # Check if directory exists
    if not os.path.exists(preview_dir):
        logger.error(f"Preview directory not found: {preview_dir}")
        return
    
    # Get all MP3 files
    mp3_files = [f for f in os.listdir(preview_dir) if f.endswith('.mp3')]
    logger.info(f"Found {len(mp3_files)} MP3 files in {preview_dir}")
    
    # Store file hashes and audio content hashes
    file_hashes = {}
    content_hashes = {}
    content_groups = defaultdict(list)
    
    for filename in mp3_files:
        file_path = os.path.join(preview_dir, filename)
        
        # Calculate file hash (MD5 of the complete file)
        try:
            with open(file_path, 'rb') as f:
                file_data = f.read()
                file_hash = hashlib.md5(file_data).hexdigest()
                file_hashes[filename] = file_hash
        except Exception as e:
            logger.exception(f"Error calculating file hash for {filename}: {e}")
            continue
        
        # Extract audio sample and calculate content hash
        try:
            # Try to extract from beginning of file
            sample_data = get_audio_sample(file_path, start_time=0, duration=5)
            
            if sample_data and len(sample_data) > 0:
                content_hash = compute_audio_hash(sample_data)
                if content_hash:
                    content_hashes[filename] = content_hash
                    content_groups[content_hash].append(filename)
                else:
                    logger.warning(f"Could not compute content hash for {filename}")
            else:
                logger.warning(f"Could not extract audio sample from {filename}")
                
        except Exception as e:
            logger.exception(f"Error processing audio sample for {filename}: {e}")
    
    # Print results
    logger.info("\nFile Hash Analysis:")
    logger.info("==================")
    
    # Check for duplicate file hashes
    file_hash_groups = defaultdict(list)
    for filename, file_hash in file_hashes.items():
        file_hash_groups[file_hash].append(filename)
    
    duplicate_file_count = 0
    for file_hash, filenames in file_hash_groups.items():
        if len(filenames) > 1:
            duplicate_file_count += 1
            logger.info(f"Duplicate files (identical byte content):")
            for filename in filenames:
                logger.info(f"  - {filename}")
    
    if duplicate_file_count == 0:
        logger.info("No duplicate files found (all files have unique byte content)")
    
    # Print content hash analysis
    logger.info("\nAudio Content Analysis:")
    logger.info("======================")
    
    # Check how many content groups we have
    unique_content_count = len(content_groups)
    if unique_content_count == len(mp3_files):
        logger.info("All files have unique audio content!")
    else:
        logger.info(f"Found {unique_content_count} unique audio signatures among {len(mp3_files)} files")
        
        # Print groups of files with the same content
        for content_hash, filenames in content_groups.items():
            if len(filenames) > 1:
                logger.info(f"\nFiles with identical audio content (hash: {content_hash}):")
                for filename in filenames:
                    logger.info(f"  - {filename}")
    
    # Print full results
    logger.info("\nDetailed Results:")
    logger.info("===============")
    
    for filename in sorted(mp3_files):
        file_hash = file_hashes.get(filename, "ERROR")
        content_hash = content_hashes.get(filename, "ERROR")
        logger.info(f"{filename}:")
        logger.info(f"  File Hash:    {file_hash}")
        logger.info(f"  Content Hash: {content_hash}")
        
    return {
        'file_count': len(mp3_files),
        'unique_file_count': len(file_hash_groups),
        'unique_content_count': unique_content_count,
        'content_groups': content_groups
    }

if __name__ == "__main__":
    print("Comparing audio content in preview files...")
    result = compare_audio_files()
    
    # Log summary to console
    if result:
        print("\nSummary:")
        print(f"Total files: {result['file_count']}")
        print(f"Unique files (by hash): {result['unique_file_count']}")
        print(f"Unique audio content: {result['unique_content_count']}")
        
        if result['unique_content_count'] < result['file_count']:
            print("\nSome files contain duplicate audio content!")
            print("See audio_comparison.log for details")
        else:
            print("\nAll files have unique audio content!")
    
    print("\nAnalysis complete. See audio_comparison.log for detailed results.")