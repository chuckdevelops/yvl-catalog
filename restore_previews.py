#\!/usr/bin/env python3
import os
import subprocess
from mutagen.mp3 import MP3

# Source and destination directories
preview_dir = 'media/previews'
backup_dir = 'media/previews_backup'

# Verify backup directory exists
if not os.path.exists(backup_dir):
    print('Error: Backup directory not found!')
    exit(1)

# Get list of MP3 files from backup
backup_files = [f for f in os.listdir(backup_dir) if f.endswith('.mp3')]

if not backup_files:
    print('No backup files found!')
    exit(1)

print(f'Found {len(backup_files)} backup files to restore.')

# Restore each file
for filename in backup_files:
    backup_path = os.path.join(backup_dir, filename)
    target_path = os.path.join(preview_dir, filename)
    
    # Check if original file exists
    if not os.path.exists(target_path):
        print(f'Warning: Original file {filename} not found, will be created.')
    
    print(f'Restoring {filename}...')
    subprocess.run(['cp', backup_path, target_path], check=True)

print('\nVerification:')
for filename in backup_files:
    filepath = os.path.join(preview_dir, filename)
    try:
        audio = MP3(filepath)
        print(f'{filename}: {audio.info.length:.2f}s')
    except Exception as e:
        print(f'{filename}: Error reading file - {e}')

print('\nRestore complete! Original files have been restored from backup.')
