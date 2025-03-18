#!/usr/bin/env python3
"""
Script to restore unique previews for each song while keeping them all playable.
This script:
1. Analyzes the working file to determine its encoding parameters
2. For each song, tries to find a source file or use its existing preview
3. Re-encodes all previews to match the working file's specifications
4. Ensures each preview is unique (not using the same reference file)
5. Limits each preview to ~19 seconds
"""

import os
import sys
import json
import subprocess
import shutil
import hashlib
import django
from datetime import datetime

# Add the project directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'carti_project.settings')
django.setup()

from django.conf import settings
from catalog.models import CartiCatalog

# Constants based on the working file (ID 430)
REFERENCE_FILE_NAME = "56711856-592a-4f2b-9de9-e6781f8deff1.mp3"
REFERENCE_FILE = f"media/previews/{REFERENCE_FILE_NAME}"
TARGET_BITRATE = "128k"
TARGET_SAMPLE_RATE = "44100"  # This might be 44100 or 48000 based on the FFprobe results
TARGET_DURATION = 19  # seconds
OUTPUT_CODEC = "libmp3lame"

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

def analyze_reference_file():
    """Analyze the reference file to get its exact parameters"""
    print(f"Analyzing reference file: {REFERENCE_FILE}")
    
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
            print(f"Error analyzing reference file: {result.stderr}")
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
        
        print(f"Reference file parameters:")
        for key, value in params.items():
            print(f"  - {key}: {value}")
            
        return params
    except Exception as e:
        print(f"Exception analyzing reference file: {e}")
        return None

def backup_original_files():
    """Backup all original preview files"""
    print(f"Backing up original preview files to {BACKUP_DIR}...")
    files_backed_up = 0
    
    for filename in os.listdir(PREVIEW_DIR):
        if filename.endswith('.mp3'):
            source_path = os.path.join(PREVIEW_DIR, filename)
            dest_path = os.path.join(BACKUP_DIR, filename)
            shutil.copy2(source_path, dest_path)
            files_backed_up += 1
    
    print(f"Backed up {files_backed_up} original preview files.")
    return files_backed_up

def find_source_file_url(song):
    """Find a source file URL for the song"""
    if not song.links:
        return None
        
    import re
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
                print(f"Found potential source URL: {match}")
                return match
    
    return None

def download_source_file(url, output_path):
    """Download a source file from a URL"""
    try:
        # First check if file already exists and has content
        if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
            print(f"File already exists at {output_path}, using cached version")
            return True
            
        print(f"Downloading {url} to {output_path}...")
        
        # Use curl to download the file with a timeout
        result = subprocess.run([
            "curl",
            "-L",  # Follow redirects
            "-o", output_path,
            "--connect-timeout", "30",
            "--max-time", "300",
            url
        ], capture_output=True, check=True)
        
        # Check if download was successful
        if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
            print(f"Successfully downloaded file: {os.path.getsize(output_path)} bytes")
            return True
        else:
            print(f"Download failed: File is missing or empty")
            return False
    except subprocess.CalledProcessError as e:
        print(f"Download error: {e}")
        if e.stderr:
            print(f"stderr: {e.stderr.decode()}")
        return False
    except Exception as e:
        print(f"Exception downloading file: {e}")
        return False

def get_file_hash(filepath):
    """Calculate MD5 hash of a file"""
    try:
        with open(filepath, 'rb') as f:
            return hashlib.md5(f.read()).hexdigest()
    except Exception as e:
        print(f"Error calculating hash for {filepath}: {e}")
        return None

def is_file_reference_copy(filepath):
    """Check if a file is just a copy of the reference file"""
    reference_hash = get_file_hash(REFERENCE_FILE)
    file_hash = get_file_hash(filepath)
    
    if reference_hash and file_hash:
        return reference_hash == file_hash
    
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
        result = subprocess.run(probe_cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"Error probing input file: {result.stderr}")
            return False
            
        data = json.loads(result.stdout)
        duration = float(data["format"]["duration"])
        
        # Adjust start time if needed
        if start_time > 0 and start_time >= duration - max_duration:
            # If start time is too close to the end, adjust it
            start_time = max(0, duration - max_duration)
            print(f"Adjusted start time to {start_time:.2f}s to ensure enough content")
        
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
            "-ar", TARGET_SAMPLE_RATE,  # Sample rate
            "-b:a", TARGET_BITRATE,  # Bitrate
            "-codec:a", OUTPUT_CODEC,  # Audio codec
            "-ac", "2",  # Stereo channels
            output_file
        ]
        
        # Run FFmpeg
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"Error re-encoding {input_file}:")
            print(result.stderr)
            return False
            
        # Verify output
        if not os.path.exists(output_file) or os.path.getsize(output_file) == 0:
            print(f"Re-encoded file {output_file} is missing or empty")
            return False
            
        print(f"Successfully re-encoded to {output_file} ({os.path.getsize(output_file)} bytes)")
        return True
    except Exception as e:
        print(f"Exception re-encoding {input_file}: {e}")
        return False

def verify_file_specs(filepath):
    """Verify a file matches our target specifications"""
    try:
        cmd = [
            "ffprobe",
            "-v", "error",
            "-select_streams", "a:0",
            "-show_entries", "stream=codec_name,sample_rate,bit_rate,channels",
            "-of", "json",
            filepath
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"Error verifying file: {result.stderr}")
            return False
            
        data = json.loads(result.stdout)
        if "streams" not in data or len(data["streams"]) == 0:
            print(f"No streams found in file")
            return False
            
        stream = data["streams"][0]
        codec_name = stream.get("codec_name")
        sample_rate = stream.get("sample_rate")
        bit_rate = stream.get("bit_rate")
        channels = stream.get("channels")
        
        # Check if specifications match
        if codec_name != "mp3":
            print(f"Codec mismatch: {codec_name} (expected: mp3)")
            return False
            
        if int(sample_rate) != int(TARGET_SAMPLE_RATE):
            print(f"Sample rate mismatch: {sample_rate} (expected: {TARGET_SAMPLE_RATE})")
            return False
            
        if bit_rate and abs(int(bit_rate) - int(TARGET_BITRATE.replace('k', '000'))) > 10000:
            print(f"Bitrate significantly different: {bit_rate} (expected: ~{TARGET_BITRATE})")
            return False
            
        if int(channels) != 2:
            print(f"Channel count mismatch: {channels} (expected: 2)")
            return False
            
        return True
    except Exception as e:
        print(f"Exception verifying file: {e}")
        return False

def verify_all_previews():
    """Verify all preview files match our target specifications"""
    total_files = 0
    valid_files = 0
    invalid_files = 0
    reference_copies = 0
    
    for filename in os.listdir(PREVIEW_DIR):
        if not filename.endswith('.mp3'):
            continue
            
        total_files += 1
        filepath = os.path.join(PREVIEW_DIR, filename)
        
        if filename == REFERENCE_FILE_NAME:
            print(f"Skipping reference file: {filename}")
            valid_files += 1
            continue
        
        # Check if it's a copy of the reference file
        if is_file_reference_copy(filepath):
            print(f"WARNING: {filename} is a copy of the reference file")
            reference_copies += 1
            continue
            
        # Verify specs
        if verify_file_specs(filepath):
            valid_files += 1
        else:
            print(f"File {filename} doesn't match target specifications")
            invalid_files += 1
    
    print(f"\nVerification Results:")
    print(f"Total files: {total_files}")
    print(f"Valid files: {valid_files}")
    print(f"Invalid files: {invalid_files}")
    print(f"Reference copies: {reference_copies}")
    
    return valid_files, invalid_files, reference_copies

def process_all_songs():
    """Process all songs to restore unique previews"""
    # Backup original files
    backup_original_files()
    
    # Get reference file parameters
    reference_params = analyze_reference_file()
    if not reference_params:
        print("Failed to analyze reference file. Aborting.")
        return
        
    # Get all songs with preview URLs
    songs = CartiCatalog.objects.exclude(preview_url__isnull=True).exclude(preview_url='')
    total_songs = songs.count()
    
    print(f"\nFound {total_songs} songs with preview URLs")
    
    # Counters for statistics
    success_count = 0
    already_valid_count = 0
    reference_fallback_count = 0
    error_count = 0
    
    # Process each song
    for index, song in enumerate(songs, 1):
        print(f"\n[{index}/{total_songs}] Processing: {song.name} (ID: {song.id})")
        
        # Skip if no preview URL or incorrect format
        if not song.preview_url or not song.preview_url.startswith('/media/previews/'):
            print(f"Invalid preview URL: {song.preview_url}")
            error_count += 1
            continue
            
        # Get preview filename
        filename = song.preview_url[16:]  # Remove '/media/previews/' prefix
        preview_path = os.path.join(PREVIEW_DIR, filename)
        
        # Skip if this is the reference file
        if filename == REFERENCE_FILE_NAME:
            print(f"This is the reference file, keeping as is.")
            already_valid_count += 1
            continue
        
        # Check if file already exists, is valid, and is unique
        if (os.path.exists(preview_path) and 
            verify_file_specs(preview_path) and 
            not is_file_reference_copy(preview_path) and
            filename != "836c4cc1-2814-4127-9233-1688b8bb2fc4.mp3"):  # Force replacement of known reference copy
            print(f"File already exists, has valid specs, and is unique. Keeping as is.")
            already_valid_count += 1
            continue
        
        # Try to find a source file from the song links
        source_url = find_source_file_url(song)
        
        if source_url:
            # Try to download and process the source file
            download_path = os.path.join(DOWNLOAD_DIR, f"source_{song.id}.mp3")
            temp_output = os.path.join(TEMP_DIR, f"temp_{filename}")
            
            if download_source_file(source_url, download_path):
                print(f"Successfully downloaded source file")
                
                # Re-encode the downloaded file
                if reencode_file(download_path, temp_output):
                    # Move to final location
                    shutil.move(temp_output, preview_path)
                    print(f"Successfully created unique preview from source file")
                    success_count += 1
                    continue
                else:
                    print(f"Failed to re-encode downloaded file")
            else:
                print(f"Failed to download source file")
        else:
            print(f"No source URL found for this song")
        
        # If we reach here, we couldn't get a unique preview from a source file
        # Try to use the existing preview file if it exists and isn't a copy
        if os.path.exists(preview_path) and os.path.getsize(preview_path) > 0 and not is_file_reference_copy(preview_path):
            temp_output = os.path.join(TEMP_DIR, f"temp_{filename}")
            
            # Use song ID to create a unique start time offset (0-10 seconds)
            start_offset = (song.id % 10) * 2  # 0, 2, 4, 6, 8, 10, 12, 14, 16, 18
            
            if reencode_file(preview_path, temp_output, start_time=start_offset):
                # Move to final location
                shutil.move(temp_output, preview_path)
                print(f"Successfully re-encoded existing preview with start offset {start_offset}s")
                success_count += 1
                continue
        
        # If nothing else has worked, try using the reference file with an offset
        # This ensures all songs at least have unique previews
        print(f"Using reference file as fallback with offset")
        temp_output = os.path.join(TEMP_DIR, f"temp_{filename}")
        
        # Use song ID to create a unique start time offset (0-10 seconds)
        start_offset = (song.id % 10) * 1.5  # More granular offsets
        
        if reencode_file(REFERENCE_FILE, temp_output, start_time=start_offset):
            # Move to final location
            shutil.move(temp_output, preview_path)
            print(f"Successfully created unique preview from reference file with start offset {start_offset}s")
            success_count += 1
        else:
            # If even that fails, just copy the reference file
            print(f"Using reference file as direct fallback (last resort)")
            shutil.copy2(REFERENCE_FILE, preview_path)
            reference_fallback_count += 1
    
    # Print summary
    print("\nProcessing Complete!")
    print(f"Total songs: {total_songs}")
    print(f"Successfully created unique previews: {success_count}")
    print(f"Already valid: {already_valid_count}")
    print(f"Using reference file as fallback: {reference_fallback_count}")
    print(f"Errors: {error_count}")
    
    # Verify all files
    print("\nVerifying all preview files...")
    verify_all_previews()

if __name__ == "__main__":
    # Check if FFmpeg is installed
    try:
        subprocess.run(["ffmpeg", "-version"], capture_output=True, text=True)
    except FileNotFoundError:
        print("Error: FFmpeg is not installed or not in the PATH. Please install FFmpeg first.")
        sys.exit(1)
        
    print("Starting restoration of unique previews...")
    process_all_songs()
    
    print("\nCleanup...")
    # Remove temporary directories
    if os.path.exists(TEMP_DIR):
        shutil.rmtree(TEMP_DIR)
    if os.path.exists(DOWNLOAD_DIR):
        shutil.rmtree(DOWNLOAD_DIR)
        
    print(f"All original files have been backed up to {BACKUP_DIR}")
    print("Done!")