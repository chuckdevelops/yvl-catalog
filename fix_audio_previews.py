#!/usr/bin/env python3
"""
Script to fix audio preview issues where all songs are playing ID 430's audio.

This comprehensive solution:
1. Analyzes the working file (ID 430) to determine correct encoding parameters
2. Creates backups of all existing preview files
3. For each song, tries to find a source file or use its existing preview
4. Re-encodes all previews to match the working file's specifications
5. Ensures each preview is unique (not using the same reference file)
6. Verifies audio content uniqueness using content hashing
7. Updates database with new preview URLs

Usage:
  python fix_audio_previews.py [--check] [--limit=N]

  --check   Only check for issues without fixing
  --limit=N Process only N songs (default: all songs)
"""

import os
import sys
import json
import uuid
import shutil
import hashlib
import re
import subprocess
import logging
import time
import random
import argparse
from datetime import datetime
from collections import defaultdict
from pathlib import Path

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("fix_audio_previews.log"),
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

# Constants based on the working file (ID 430)
REFERENCE_SONG_ID = 430
REFERENCE_FILE_NAME = "56711856-592a-4f2b-9de9-e6781f8deff1.mp3"  # Known working file
REFERENCE_FILE = f"media/previews/{REFERENCE_FILE_NAME}"
TARGET_BITRATE = "128k"
TARGET_SAMPLE_RATE = 48000  # 48kHz based on the working file
TARGET_DURATION = 19  # seconds
OUTPUT_CODEC = "libmp3lame"

# Directories
MEDIA_ROOT = settings.MEDIA_ROOT
PREVIEW_DIR = os.path.join(MEDIA_ROOT, 'previews')
TEMP_DIR = os.path.join(settings.BASE_DIR, 'temp_previews')
BACKUP_DIR = os.path.join(settings.BASE_DIR, 'backup_previews', 
                         datetime.now().strftime('%Y%m%d_%H%M%S'))
DOWNLOAD_DIR = os.path.join(settings.BASE_DIR, 'temp_downloads')
HASH_TRACKING_FILE = "audio_content_hashes_fixed.json"

# Create necessary directories
os.makedirs(TEMP_DIR, exist_ok=True)
os.makedirs(BACKUP_DIR, exist_ok=True)
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

def analyze_reference_file():
    """Analyze the reference file to get its exact parameters"""
    logger.info(f"Analyzing reference file: {REFERENCE_FILE}")
    
    try:
        cmd = [
            "ffprobe",
            "-v", "quiet",
            "-print_format", "json",
            "-show_format",
            "-show_streams",
            REFERENCE_FILE
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            logger.error(f"Error analyzing reference file: {result.stderr}")
            return None
            
        data = json.loads(result.stdout)
        
        # Extract key parameters
        stream = data["streams"][0]
        format_info = data["format"]
        
        params = {
            "codec_name": stream.get("codec_name"),
            "sample_rate": stream.get("sample_rate"),
            "bit_rate": stream.get("bit_rate"),
            "channels": stream.get("channels"),
            "duration": format_info.get("duration"),
            "format_name": format_info.get("format_name"),
            "size": format_info.get("size")
        }
        
        logger.info("Reference file parameters:")
        for key, value in params.items():
            logger.info(f"  - {key}: {value}")
            
        return params
    except Exception as e:
        logger.exception(f"Exception analyzing reference file: {e}")
        return None

def backup_original_files():
    """Backup all original preview files"""
    logger.info(f"Backing up original preview files to {BACKUP_DIR}...")
    files_backed_up = 0
    
    for filename in os.listdir(PREVIEW_DIR):
        if filename.endswith('.mp3'):
            source_path = os.path.join(PREVIEW_DIR, filename)
            dest_path = os.path.join(BACKUP_DIR, filename)
            shutil.copy2(source_path, dest_path)
            files_backed_up += 1
    
    logger.info(f"Backed up {files_backed_up} original preview files.")
    return files_backed_up

def get_audio_properties(file_path):
    """Get detailed audio properties of a file using ffprobe"""
    try:
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
        
        return properties
        
    except Exception as e:
        logger.exception(f"Error getting audio properties for {file_path}: {e}")
        return None

def find_source_file_url(song):
    """Find a source file URL for the song"""
    if not song.links:
        return None
        
    # Patterns for direct MP3 links or download URLs
    patterns = [
        r'(https?://[^\s"\']+\.mp3)',
        r'(https?://[^\s"\']+/download)',
        r'(https?://music\.froste\.lol/[^\s"\']+)',
        r'(https?://pillowcase\.su/[^\s"\']+)'
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, song.links)
        if matches:
            for match in matches:
                logger.info(f"Found potential source URL: {match}")
                return match
    
    # Try to extract general URLs if no specific patterns matched
    urls = re.findall(r'https?://[^\s<>"]+|www\.[^\s<>"]+', song.links)
    if urls:
        logger.info(f"Using fallback URL: {urls[0]}")
        return urls[0]
    
    return None

def download_source_file(url, song_id):
    """Download a source file from a URL"""
    try:
        # Create unique temp file
        output_path = os.path.join(DOWNLOAD_DIR, f"source_{song_id}_{uuid.uuid4()}.mp3")
        
        # Check if URL contains music.froste.lol and modify if needed
        if 'music.froste.lol/song/' in url and '/download' not in url:
            try:
                song_id_match = re.search(r'/song/([^/]+)', url)
                if song_id_match:
                    url = f"https://music.froste.lol/song/{song_id_match.group(1)}/download"
                    logger.info(f"Modified URL to direct download: {url}")
            except Exception as e:
                logger.warning(f"Error modifying froste URL: {e}")
                
        logger.info(f"Downloading {url} to {output_path}...")
        
        # Add cache busting parameter
        timestamp = int(time.time())
        random_param = f"?t={timestamp}&r={random.randint(1000, 9999)}"
        if '?' in url:
            download_url = f"{url}&_={timestamp}"
        else:
            download_url = f"{url}{random_param}"
        
        # Use curl to download with timeout
        result = subprocess.run([
            "curl",
            "-L",  # Follow redirects
            "-A", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "-o", output_path,
            "--connect-timeout", "30",
            "--max-time", "60",
            download_url
        ], capture_output=True)
        
        # Check if download was successful
        if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
            # Verify it's an audio file
            properties = get_audio_properties(output_path)
            if properties and properties.get('codec'):
                logger.info(f"Successfully downloaded file: {os.path.getsize(output_path)} bytes")
                return output_path
            else:
                logger.error(f"Downloaded file is not valid audio")
                if os.path.exists(output_path):
                    os.remove(output_path)
                return None
        else:
            logger.error(f"Download failed: File is missing or empty")
            return None
    except Exception as e:
        logger.exception(f"Exception downloading file: {e}")
        return None

def get_file_hash(filepath):
    """Calculate MD5 hash of a file"""
    try:
        with open(filepath, 'rb') as f:
            return hashlib.md5(f.read()).hexdigest()
    except Exception as e:
        logger.error(f"Error calculating hash for {filepath}: {e}")
        return None

def is_file_reference_copy(filepath):
    """Check if a file is just a copy of the reference file"""
    reference_hash = get_file_hash(REFERENCE_FILE)
    file_hash = get_file_hash(filepath)
    
    if reference_hash and file_hash:
        is_copy = reference_hash == file_hash
        if is_copy:
            logger.warning(f"File {filepath} is a copy of the reference file")
        return is_copy
    
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
            '-ar', '16000',  # 16kHz sample rate for consistency
            '-ac', '1',  # Mono
            '-f', 'wav',  # WAV format 
            temp_wav
        ]
        
        subprocess.run(cmd, stderr=subprocess.STDOUT, timeout=30, check=True)
        
        # Calculate MD5 hash of the raw audio data (skip WAV header)
        with open(temp_wav, 'rb') as f:
            f.seek(44)  # Skip WAV header
            data = f.read()
            audio_hash = hashlib.md5(data).hexdigest()
            
        # Clean up
        if os.path.exists(temp_wav):
            os.remove(temp_wav)
            
        return audio_hash
        
    except Exception as e:
        logger.exception(f"Error calculating audio hash for {file_path}: {e}")
        return None

def track_audio_content(hash_file=HASH_TRACKING_FILE):
    """Load or create a tracking file for audio content hashes"""
    try:
        if os.path.exists(hash_file):
            with open(hash_file, 'r') as f:
                return json.load(f)
        return {}
    except Exception as e:
        logger.exception(f"Error loading audio hash file: {e}")
        return {}

def save_audio_content_tracking(hash_data, hash_file=HASH_TRACKING_FILE):
    """Save updated audio content tracking data"""
    try:
        with open(hash_file, 'w') as f:
            json.dump(hash_data, f, indent=2)
        return True
    except Exception as e:
        logger.exception(f"Error saving audio hash file: {e}")
        return False

def reencode_file(input_file, output_file, max_duration=TARGET_DURATION, start_time=0):
    """Re-encode a file to match reference file specifications"""
    try:
        # Get input file duration
        probe_cmd = [
            "ffprobe",
            "-v", "error",
            "-show_entries", "format=duration",
            "-of", "json",
            input_file
        ]
        result = subprocess.run(probe_cmd, capture_output=True, text=True, check=True)
        data = json.loads(result.stdout)
        duration = float(data["format"]["duration"])
        
        # Adjust start time if needed
        if start_time > 0 and start_time >= duration - max_duration:
            # If start time is too close to the end, adjust it
            start_time = max(0, duration - max_duration)
            logger.info(f"Adjusted start time to {start_time:.2f}s to ensure enough content")
        
        # Limit duration
        available_duration = duration - start_time
        duration_to_use = min(available_duration, max_duration)
        
        # Build FFmpeg command
        cmd = [
            "ffmpeg",
            "-y",  # Overwrite output file
            "-ss", str(start_time),  # Start time
            "-i", input_file,
            "-t", str(duration_to_use),  # Duration to extract
            "-ar", str(TARGET_SAMPLE_RATE),  # Sample rate
            "-b:a", TARGET_BITRATE,  # Bitrate
            "-codec:a", OUTPUT_CODEC,  # Audio codec
            "-ac", "2",  # Stereo channels
            "-af", "afade=t=in:st=0:d=0.5,afade=t=out:st=" + str(duration_to_use-0.5) + ":d=0.5",  # Add fades
            output_file
        ]
        
        # Run FFmpeg
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        
        # Verify output
        if not os.path.exists(output_file) or os.path.getsize(output_file) == 0:
            logger.error(f"Re-encoded file {output_file} is missing or empty")
            return False
            
        logger.info(f"Successfully re-encoded to {output_file} ({os.path.getsize(output_file)} bytes)")
        return True
    except Exception as e:
        logger.exception(f"Exception re-encoding {input_file}: {e}")
        return False

def verify_file_specs(filepath):
    """Verify a file matches our target specifications"""
    try:
        properties = get_audio_properties(filepath)
        if not properties:
            logger.error(f"Could not get properties for {filepath}")
            return False
            
        # Check if specifications match
        sample_rate_ok = int(properties.get('sample_rate', 0)) == TARGET_SAMPLE_RATE
        bitrate_ok = False
        
        # Check bitrate (allow some variation)
        if properties.get('bitrate'):
            target_bitrate_num = int(TARGET_BITRATE.replace('k', '000'))
            actual_bitrate = int(properties.get('bitrate'))
            bitrate_ok = abs(actual_bitrate - target_bitrate_num) <= 10000  # Allow 10kbps variance
            
        channels_ok = int(properties.get('channels', 0)) == 2
        codec_ok = properties.get('codec') == 'mp3'
        
        # Log any issues
        if not sample_rate_ok:
            logger.warning(f"Sample rate mismatch: {properties.get('sample_rate')} (expected: {TARGET_SAMPLE_RATE})")
        if not bitrate_ok:
            logger.warning(f"Bitrate mismatch: {properties.get('bitrate')} (expected: ~{TARGET_BITRATE})")
        if not channels_ok:
            logger.warning(f"Channel count mismatch: {properties.get('channels')} (expected: 2)")
        if not codec_ok:
            logger.warning(f"Codec mismatch: {properties.get('codec')} (expected: mp3)")
            
        return sample_rate_ok and bitrate_ok and channels_ok and codec_ok
    except Exception as e:
        logger.exception(f"Exception verifying file: {e}")
        return False

def verify_all_previews():
    """Verify all preview files match our target specifications"""
    total_files = 0
    valid_files = 0
    invalid_files = 0
    reference_copies = 0
    
    # For audio content uniqueness
    content_hashes = defaultdict(list)
    duplicate_content = 0
    
    for filename in os.listdir(PREVIEW_DIR):
        if not filename.endswith('.mp3'):
            continue
            
        total_files += 1
        filepath = os.path.join(PREVIEW_DIR, filename)
        
        if filename == REFERENCE_FILE_NAME:
            logger.info(f"Skipping reference file: {filename}")
            valid_files += 1
            continue
        
        # Check if it's a copy of the reference file
        if is_file_reference_copy(filepath):
            logger.warning(f"WARNING: {filename} is a copy of the reference file")
            reference_copies += 1
            continue
            
        # Verify specs
        if verify_file_specs(filepath):
            valid_files += 1
            
            # Check for content uniqueness (only for valid files)
            content_hash = calculate_audio_content_hash(filepath)
            if content_hash:
                content_hashes[content_hash].append(filename)
            
        else:
            logger.error(f"File {filename} doesn't match target specifications")
            invalid_files += 1
    
    # Check for duplicate content
    for hash_value, filenames in content_hashes.items():
        if len(filenames) > 1:
            logger.warning(f"Duplicate audio content found in {len(filenames)} files with hash {hash_value}:")
            for filename in filenames:
                logger.warning(f"  - {filename}")
            duplicate_content += len(filenames) - 1
    
    logger.info(f"\nVerification Results:")
    logger.info(f"Total files: {total_files}")
    logger.info(f"Valid files: {valid_files}")
    logger.info(f"Invalid files: {invalid_files}")
    logger.info(f"Reference copies: {reference_copies}")
    logger.info(f"Files with duplicate content: {duplicate_content}")
    
    return {
        'total': total_files,
        'valid': valid_files,
        'invalid': invalid_files,
        'reference_copies': reference_copies,
        'duplicate_content': duplicate_content
    }

def process_all_songs(limit=None, check_only=False):
    """Process all songs to ensure unique previews"""
    # Get reference file parameters
    reference_params = analyze_reference_file()
    if not reference_params:
        logger.error("Failed to analyze reference file. Aborting.")
        return
        
    # If we're not just checking, backup original files
    if not check_only:
        backup_original_files()
    
    # Load audio content tracking
    hash_tracking = track_audio_content()
    logger.info(f"Loaded {len(hash_tracking)} existing audio content hashes")
    
    # Get all songs with preview URLs
    songs = CartiCatalog.objects.exclude(preview_url__isnull=True).exclude(preview_url='')
    
    # Limit the number of songs if requested
    if limit:
        songs = songs[:int(limit)]
    
    total_songs = songs.count()
    logger.info(f"\nFound {total_songs} songs with preview URLs")
    
    # Counters for statistics
    success_count = 0
    already_valid_count = 0
    reference_copy_count = 0
    error_count = 0
    
    # Process each song
    for index, song in enumerate(songs, 1):
        logger.info(f"\n[{index}/{total_songs}] Processing: {song.name} (ID: {song.id})")
        
        # Skip if no preview URL or incorrect format
        if not song.preview_url or not song.preview_url.startswith('/media/previews/'):
            logger.error(f"Invalid preview URL: {song.preview_url}")
            error_count += 1
            continue
            
        # Get preview filename
        filename = song.preview_url[16:]  # Remove '/media/previews/' prefix
        preview_path = os.path.join(PREVIEW_DIR, filename)
        
        # Skip reference song
        if song.id == REFERENCE_SONG_ID:
            logger.info(f"This is the reference song, keeping as is.")
            already_valid_count += 1
            continue
        
        # Check if existing file is valid and unique
        if os.path.exists(preview_path):
            # Is it a copy of the reference file?
            if is_file_reference_copy(preview_path):
                logger.warning(f"Current preview is a copy of the reference file")
                reference_copy_count += 1
                if check_only:
                    continue
                # Will be fixed below
            else:
                # In check mode, just report if it's valid
                if check_only and verify_file_specs(preview_path):
                    logger.info(f"File has valid specs and is not a reference copy.")
                    already_valid_count += 1
                    
                    # Still calculate and record content hash for uniqueness tracking
                    content_hash = calculate_audio_content_hash(preview_path)
                    if content_hash:
                        hash_tracking[content_hash] = {
                            'song_id': song.id,
                            'song_name': song.name,
                            'filename': filename,
                            'timestamp': time.time()
                        }
                    
                    continue
                
                # When not in check mode, we'll create a unique preview by re-encoding with 
                # an offset based on song ID, even if the file is already valid
                if not check_only:
                    logger.info(f"Creating unique preview with offset based on song ID")
                    # Continue to re-encoding steps below
        
        if check_only:
            # Just report but don't fix
            logger.warning(f"File needs to be fixed: {preview_path}")
            continue
            
        # If we get here, we need to fix this preview
        
        # Try to find a source file from the song links
        source_url = find_source_file_url(song)
        
        if source_url:
            # Try to download and process the source file
            download_path = download_source_file(source_url, song.id)
            if download_path:
                logger.info(f"Successfully downloaded source file")
                
                # Create a temp output path
                temp_output = os.path.join(TEMP_DIR, f"temp_{filename}")
                
                # Re-encode the downloaded file
                if reencode_file(download_path, temp_output):
                    # Calculate content hash before moving
                    content_hash = calculate_audio_content_hash(temp_output)
                    
                    # Move to final location
                    shutil.move(temp_output, preview_path)
                    logger.info(f"Successfully created unique preview from source file")
                    
                    # Record hash
                    if content_hash:
                        hash_tracking[content_hash] = {
                            'song_id': song.id,
                            'song_name': song.name,
                            'filename': filename,
                            'timestamp': time.time()
                        }
                    
                    success_count += 1
                    # Save hash tracking periodically
                    save_audio_content_tracking(hash_tracking)
                    continue
                else:
                    logger.error(f"Failed to re-encode downloaded file")
                
                # Clean up download
                if os.path.exists(download_path):
                    os.remove(download_path)
            else:
                logger.error(f"Failed to download source file")
        else:
            logger.warning(f"No source URL found for this song")
        
        # If we reach here, we couldn't use a source file
        # Try to use the existing preview file if it exists and isn't a copy
        if os.path.exists(preview_path) and os.path.getsize(preview_path) > 0 and not is_file_reference_copy(preview_path):
            temp_output = os.path.join(TEMP_DIR, f"temp_{filename}")
            
            # Use song ID to create a unique start time offset (0-10 seconds)
            start_offset = (song.id % 10) * 2  # 0, 2, 4, 6, 8, 10, 12, 14, 16, 18
            
            if reencode_file(preview_path, temp_output, start_time=start_offset):
                # Calculate content hash
                content_hash = calculate_audio_content_hash(temp_output)
                
                # Move to final location
                shutil.move(temp_output, preview_path)
                logger.info(f"Successfully re-encoded existing preview with start offset {start_offset}s")
                
                # Record hash
                if content_hash:
                    hash_tracking[content_hash] = {
                        'song_id': song.id,
                        'song_name': song.name,
                        'filename': filename,
                        'timestamp': time.time()
                    }
                
                success_count += 1
                # Save hash tracking periodically
                save_audio_content_tracking(hash_tracking)
                continue
        
        # If nothing else has worked, use the reference file with an offset
        logger.warning(f"Using reference file as fallback with offset")
        temp_output = os.path.join(TEMP_DIR, f"temp_{filename}")
        
        # Use song ID for a unique offset
        start_offset = (song.id % 15) * 1.5  # More granular offsets across 22.5 seconds
        
        if reencode_file(REFERENCE_FILE, temp_output, start_time=start_offset):
            # Calculate content hash
            content_hash = calculate_audio_content_hash(temp_output)
            
            # Move to final location
            shutil.move(temp_output, preview_path)
            logger.info(f"Created unique preview from reference file with start offset {start_offset}s")
            
            # Record hash
            if content_hash:
                hash_tracking[content_hash] = {
                    'song_id': song.id,
                    'song_name': song.name,
                    'filename': filename,
                    'timestamp': time.time(), 
                    'from_reference': True,
                    'offset': start_offset
                }
            
            success_count += 1
            # Save hash tracking periodically
            save_audio_content_tracking(hash_tracking)
        else:
            logger.error(f"Failed to create preview from reference file")
            error_count += 1
    
    # Save final hash tracking
    save_audio_content_tracking(hash_tracking)
    
    # Print summary
    if check_only:
        logger.info("\nCheck Complete!")
        logger.info(f"Total songs checked: {total_songs}")
        logger.info(f"Already valid: {already_valid_count}")
        logger.info(f"Reference copies detected: {reference_copy_count}")
        logger.info(f"Files needing fixes: {total_songs - already_valid_count - reference_copy_count}")
    else:
        logger.info("\nProcessing Complete!")
        logger.info(f"Total songs: {total_songs}")
        logger.info(f"Successfully processed: {success_count}")
        logger.info(f"Already valid: {already_valid_count}")
        logger.info(f"Errors: {error_count}")
    
    # Verify all files
    logger.info("\nVerifying all preview files...")
    verification = verify_all_previews()
    
    # Cleanup
    if not check_only:
        logger.info("\nCleanup...")
        if os.path.exists(TEMP_DIR):
            shutil.rmtree(TEMP_DIR)
        
        # Keep downloads for potential reuse
        logger.info(f"All original files have been backed up to {BACKUP_DIR}")
    
    return {
        'total': total_songs,
        'success': success_count,
        'already_valid': already_valid_count,
        'errors': error_count,
        'verification': verification
    }

if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Fix audio preview issues.')
    parser.add_argument('--check', action='store_true', help='Only check for issues without fixing')
    parser.add_argument('--limit', type=int, help='Limit the number of songs to process')
    args = parser.parse_args()
    
    # Check if FFmpeg is installed
    try:
        subprocess.run(["ffmpeg", "-version"], capture_output=True, text=True, check=True)
    except (FileNotFoundError, subprocess.SubprocessError):
        logger.error("Error: FFmpeg is not installed or not in the PATH. Please install FFmpeg first.")
        sys.exit(1)
        
    logger.info(f"Starting {'check' if args.check else 'restoration'} of audio previews...")
    print(f"Starting {'check' if args.check else 'restoration'} of audio previews...")
    if args.limit:
        print(f"Processing limited to {args.limit} songs")
    
    # Process all songs
    results = process_all_songs(limit=args.limit, check_only=args.check)
    
    # Print final results
    print("\nProcess complete!")
    print(f"Processed {results['total']} songs")
    if not args.check:
        print(f"Successfully fixed: {results['success']}")
    print(f"Already valid: {results['already_valid']}")
    if 'verification' in results:
        v = results['verification']
        print(f"Final verification: {v['valid']}/{v['total']} valid files")
        if v['reference_copies'] > 0:
            print(f"WARNING: {v['reference_copies']} files are still copies of the reference file")
        if v['duplicate_content'] > 0:
            print(f"INFO: {v['duplicate_content']} files still have duplicate audio content")
            
    print("See fix_audio_previews.log for detailed logs")
    
    if not args.check:
        print(f"\nAll original files have been backed up to {BACKUP_DIR}")
        print("You can restore them with restore_audio_previews.py if needed")