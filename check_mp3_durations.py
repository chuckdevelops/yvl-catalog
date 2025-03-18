#!/usr/bin/env python3
"""
Check the duration of all MP3 files in the previews directory
"""

import os
import json
import subprocess
from pathlib import Path

def get_duration(file_path):
    """Get the duration of an audio file using ffprobe"""
    try:
        cmd = [
            'ffprobe',
            '-v', 'error',
            '-show_entries', 'format=duration',
            '-of', 'json',
            str(file_path)
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        duration_info = json.loads(result.stdout)
        return float(duration_info['format']['duration'])
    except Exception as e:
        return f"Error: {str(e)}"

def main():
    # Path to previews directory
    preview_dir = Path('/Users/garypayton/Desktop/nberworking3/media/previews')
    
    # Check if directory exists
    if not preview_dir.exists():
        print(f"ERROR: Directory not found: {preview_dir}")
        return
    
    # Get all MP3 files
    mp3_files = list(preview_dir.glob('*.mp3'))
    print(f"Found {len(mp3_files)} MP3 files")
    
    # Create a list to store the results
    results = []
    
    # Process each file
    for file in mp3_files:
        file_size = os.path.getsize(file)
        duration = get_duration(file)
        
        if isinstance(duration, float):
            results.append((file.name, duration, file_size))
        else:
            print(f"{file.name}: {duration}")
    
    # Sort by duration (shortest first)
    results.sort(key=lambda x: x[1])
    
    # Print the results
    print("\nMP3 Files sorted by duration (shortest first):")
    print("-" * 60)
    print(f"{'Filename':<40} {'Duration':>10} {'Size':>10}")
    print("-" * 60)
    
    for filename, duration, file_size in results:
        print(f"{filename:<40} {duration:>8.2f}s {file_size/1024:>8.0f}KB")

if __name__ == "__main__":
    main()