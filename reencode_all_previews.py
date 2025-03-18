#\!/usr/bin/env python3
import os
import subprocess
import time
from mutagen.mp3 import MP3

# Source and destination directories
preview_dir = 'media/previews'
backup_dir = 'media/previews_backup'

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

# Process each file - FULL RE-ENCODE (not just bitrate change)
print('Processing files...')
for filename in mp3_files:
    filepath = os.path.join(preview_dir, filename)
    
    # Create a temporary output file
    temp_output = f'media/previews/temp_{filename}'
    
    # Use ffmpeg to re-encode the entire file
    try:
        print(f'Re-encoding {filename}...')
        
        # Complete re-encoding with standard parameters
        subprocess.run([
            'ffmpeg', '-y', '-i', filepath,
            '-c:a', 'libmp3lame',  # MP3 encoder
            '-b:a', '128k',        # Bitrate
            '-ar', '44100',        # Sample rate
            '-ac', '2',            # Stereo
            '-write_xing', '0',    # No Xing/Info tag
            temp_output
        ], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Replace original with re-encoded version
        os.replace(temp_output, filepath)
        print(f'  ✓ Successfully re-encoded {filename}')
    except subprocess.CalledProcessError as e:
        print(f'  ✗ Error processing {filename}: {e}')
        # Delete temp file if it exists
        if os.path.exists(temp_output):
            os.remove(temp_output)

print('Verification:')
for filename in mp3_files:
    filepath = os.path.join(preview_dir, filename)
    try:
        audio = MP3(filepath)
        print(f'{filename}: {audio.info.length:.2f}s, {audio.info.bitrate/1000:.0f}kbps')
    except Exception as e:
        print(f'{filename}: Error - {e}')

print('Done\! Original files have been backed up to', backup_dir)
print('To restore the original files, run restore_previews.py')
