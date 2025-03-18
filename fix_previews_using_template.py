#\!/usr/bin/env python3
import os
import subprocess
import time
from mutagen.mp3 import MP3

# Known good file parameters
GOOD_SAMPLE_RATE = 48000  # 48kHz (from working file)
GOOD_BITRATE = '128k'     # 128kbps (from working file)

# Source and destination directories
preview_dir = 'media/previews'
backup_dir = 'media/previews_backup'
WORKING_FILE = 'media/previews/56711856-592a-4f2b-9de9-e6781f8deff1.mp3'

# Ensure backup directory exists
os.makedirs(backup_dir, exist_ok=True)

# Get list of MP3 files
mp3_files = [f for f in os.listdir(preview_dir) if f.endswith('.mp3')]

# Backup all files first
print('Backing up original files...')
for filename in mp3_files:
    source_path = os.path.join(preview_dir, filename)
    backup_path = os.path.join(backup_dir, filename)
    subprocess.run(['cp', source_path, backup_path], check=True)

# Process each file using the working file as a template
print('Processing files...')
for filename in mp3_files:
    # Skip the known good file
    if filename == '56711856-592a-4f2b-9de9-e6781f8deff1.mp3':
        print(f'Skipping known working file: {filename}')
        continue
        
    filepath = os.path.join(preview_dir, filename)
    
    # Create a temporary output file
    temp_output = f'media/previews/temp_{filename}'
    
    # Use ffmpeg to re-encode with EXACT SAME parameters as working file
    try:
        print(f'Re-encoding {filename} with parameters from working file...')
        
        # Use the exact encoder settings from the working file
        subprocess.run([
            'ffmpeg', '-y', '-i', filepath,
            '-c:a', 'libmp3lame',           # Same encoder as working file
            '-b:a', GOOD_BITRATE,           # Same bitrate as working file
            '-ar', str(GOOD_SAMPLE_RATE),   # Same sample rate as working file
            '-ac', '2',                     # Stereo (same as working file)
            '-id3v2_version', '4',          # ID3v2.4 tags (same as working)
            '-write_id3v1', '1',            # Write ID3v1 tag
            temp_output
        ], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Replace original with re-encoded version
        os.replace(temp_output, filepath)
        print(f'  ✓ Successfully re-encoded {filename} using working file template')
    except subprocess.CalledProcessError as e:
        print(f'  ✗ Error processing {filename}: {e}')
        # Delete temp file if it exists
        if os.path.exists(temp_output):
            os.remove(temp_output)

print('\nVerification:')
for filename in mp3_files:
    filepath = os.path.join(preview_dir, filename)
    try:
        audio = MP3(filepath)
        print(f'{filename}: {audio.info.length:.2f}s, {audio.info.bitrate/1000:.0f}kbps, {audio.info.sample_rate/1000:.1f}kHz')
    except Exception as e:
        print(f'{filename}: Error - {e}')

print('\nDone\! Original files have been backed up to', backup_dir)
print('To restore the original files, run restore_previews.py')
