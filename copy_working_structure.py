#\!/usr/bin/env python3
import os
import subprocess
import tempfile
import time
import shutil
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, TIT2

# Source and destination directories
preview_dir = 'media/previews'
backup_dir = 'media/previews_backup'
WORKING_FILE = 'media/previews/56711856-592a-4f2b-9de9-e6781f8deff1.mp3'

# Ensure backup directory exists
if not os.path.exists(backup_dir):
    os.makedirs(backup_dir, exist_ok=True)

# Get list of MP3 files
mp3_files = [f for f in os.listdir(preview_dir) if f.endswith('.mp3')]

# Backup all files first
print('Backing up original files...')
for filename in mp3_files:
    source_path = os.path.join(preview_dir, filename)
    backup_path = os.path.join(backup_dir, filename)
    if not os.path.exists(backup_path):  # Don't overwrite existing backups
        shutil.copy2(source_path, backup_path)

# Ensure working file exists
if not os.path.exists(WORKING_FILE):
    print(f"ERROR: Working file {WORKING_FILE} not found\!")
    exit(1)

# Get existing working file info
try:
    working_audio = MP3(WORKING_FILE)
    print(f"Working file properties: {working_audio.info.length:.2f}s, {working_audio.info.bitrate/1000:.0f}kbps")
except Exception as e:
    print(f"Error reading working file: {e}")
    exit(1)

print("\n--- APPROACH: Copy working file but change ID3 tags ---")
print("This will copy the working file for each broken file, but preserve the original ID3 tags")

# Process each file
for filename in mp3_files:
    # Skip the known good file
    if filename == os.path.basename(WORKING_FILE):
        print(f'Skipping known working file: {filename}')
        continue
        
    filepath = os.path.join(preview_dir, filename)
    
    try:
        print(f'Processing {filename}...')
        
        # Read original ID3 tags
        try:
            orig_tags = ID3(filepath)
            print(f'  Read {len(orig_tags)} ID3 tags from original file')
        except Exception as e:
            print(f'  Warning: Could not read ID3 tags from original file: {e}')
            orig_tags = None
        
        # Create a temporary file
        with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as temp_file:
            temp_path = temp_file.name
        
        # Copy the working file to temp
        shutil.copy2(WORKING_FILE, temp_path)
        
        # Update ID3 tags if available
        if orig_tags:
            try:
                # First try to preserve all original tags
                new_tags = ID3(temp_path)
                for key in orig_tags:
                    new_tags[key] = orig_tags[key]
                new_tags.save()
                print(f'  Copied all tags from original file')
            except Exception as e:
                print(f'  Error copying all tags, falling back to simple title: {e}')
                try:
                    # Fallback: Just set the title tag
                    new_tags = ID3(temp_path)
                    if 'TIT2' in orig_tags:
                        new_tags['TIT2'] = orig_tags['TIT2']
                        new_tags.save()
                        print(f'  Set title tag only')
                except Exception as e:
                    print(f'  Error setting title tag: {e}')
        
        # Move temp file to replace original
        shutil.move(temp_path, filepath)
        print(f'  ✓ Replaced {filename} with working file structure')
        
    except Exception as e:
        print(f'  ✗ Error processing {filename}: {e}')
        # Clean up temp file if it exists
        if 'temp_path' in locals() and os.path.exists(temp_path):
            os.unlink(temp_path)

print('\nVerification:')
for filename in mp3_files:
    filepath = os.path.join(preview_dir, filename)
    try:
        audio = MP3(filepath)
        print(f'{filename}: {audio.info.length:.2f}s, {audio.info.bitrate/1000:.0f}kbps')
    except Exception as e:
        print(f'{filename}: Error - {e}')

print('\nDone\! Original files have been backed up to', backup_dir)
print('To restore the original files, run restore_previews.py')
