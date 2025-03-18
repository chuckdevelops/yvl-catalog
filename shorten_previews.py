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

# Process each file - trim to 18 seconds
print('Processing files...')
for filename in mp3_files:
    filepath = os.path.join(preview_dir, filename)
    audio = MP3(filepath)
    duration = audio.info.length
    
    # Skip if already under 20 seconds
    if duration <= 20:
        print(f'Skipping {filename} - already {duration:.2f}s')
        continue
        
    print(f'Trimming {filename} from {duration:.2f}s to 18.0s...')
    
    # Create a temporary output file
    temp_output = f'media/previews/temp_{filename}'
    
    # Use ffmpeg to trim the audio
    try:
        # Copy the first 18 seconds of audio
        subprocess.run([
            'ffmpeg', '-y', '-i', filepath, 
            '-t', '18', '-c:a', 'libmp3lame', '-q:a', '2',
            temp_output
        ], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Replace original with shortened version
        os.replace(temp_output, filepath)
        print(f'  ✓ Successfully trimmed {filename}')
    except subprocess.CalledProcessError as e:
        print(f'  ✗ Error processing {filename}: {e}')
        # Delete temp file if it exists
        if os.path.exists(temp_output):
            os.remove(temp_output)

print('Verification:')
for filename in mp3_files:
    filepath = os.path.join(preview_dir, filename)
    audio = MP3(filepath)
    print(f'{filename}: {audio.info.length:.2f}s')

print('Done! Original files have been backed up to', backup_dir)
print('To restore the original files, run the restore script.')
