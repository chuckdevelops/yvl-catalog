#!/usr/bin/env python3
import os
import sys
import mimetypes
import subprocess
from pathlib import Path

def check_mp3_file(file_path):
    """Check if the MP3 file is valid and playable"""
    try:
        # Get file info using ffprobe
        cmd = [
            'ffprobe',
            '-v', 'error',
            '-select_streams', 'a:0',
            '-show_entries', 'stream=codec_name,channels,sample_rate,bit_rate',
            '-of', 'json',
            file_path
        ]
        
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        
        if process.returncode != 0:
            return False, f"Error: {stderr.decode().strip()}"
        
        # Check file MIME type
        mime_type = mimetypes.guess_type(file_path)[0]
        if not mime_type or 'audio' not in mime_type:
            return False, f"Invalid MIME type: {mime_type}"
        
        file_size = os.path.getsize(file_path)
        if file_size < 1000:  # Suspicious if file is less than 1KB
            return False, f"Suspiciously small file size: {file_size} bytes"
        
        return True, "MP3 file appears valid"
    except Exception as e:
        return False, f"Exception: {str(e)}"

def main():
    # Set up path to media directory
    base_dir = Path(__file__).resolve().parent
    media_dir = os.path.join(base_dir, 'media')
    previews_dir = os.path.join(media_dir, 'previews')
    
    print(f"Checking MP3 files in: {previews_dir}")
    print('-' * 60)
    
    if not os.path.exists(previews_dir):
        print(f"Error: Directory {previews_dir} doesn't exist")
        return
    
    # Check each MP3 file in the directory
    valid_count = 0
    invalid_count = 0
    
    for filename in os.listdir(previews_dir):
        if not filename.endswith('.mp3'):
            continue
            
        file_path = os.path.join(previews_dir, filename)
        is_valid, message = check_mp3_file(file_path)
        
        status = "✅ VALID" if is_valid else "❌ INVALID"
        print(f"{status}: {filename}")
        print(f"  Details: {message}")
        print(f"  Size: {os.path.getsize(file_path)} bytes")
        print(f"  Path: {file_path}")
        print('-' * 60)
        
        if is_valid:
            valid_count += 1
        else:
            invalid_count += 1
    
    print(f"Summary: {valid_count} valid files, {invalid_count} invalid files")

if __name__ == "__main__":
    main()