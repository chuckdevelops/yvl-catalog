# Fixing Audio Preview Issues

This document describes how to fix audio preview issues in the music catalog.

## Issue Summary

The system had an issue where audio previews would stop working after a certain point in the catalog. Specifically:

1. Audio players would appear but wouldn't play sound after page 6 of the catalog
2. Affected files were correctly formatted MP3s but had incorrect encoding parameters
3. Files with ~30 second duration were silent, while 19-second files worked correctly
4. Files using 32kbps bitrate and 44.1kHz sample rate were not playing properly
5. Some URLs were using /audio-serve/ paths instead of direct /media/previews/ paths

## Root Causes

After investigation, we identified several issues:

1. **Encoding Parameters**: Working audio files use 128kbps bitrate and 48kHz sample rate, while problematic files were using 32kbps and 44.1kHz
2. **Duration**: Working files are ~19 seconds long, while broken files are exactly 30.024 seconds
3. **Browser Compatibility**: Modern browsers have trouble with low-bitrate MP3 files
4. **URL Routing**: The /audio-serve/ routes weren't properly resolving to actual files
5. **File Existence Check**: The preview_file_exists property in views.py was incorrectly returning False

## Solution Overview

We implemented a multi-part solution:

1. **Server-side Fixes**:
   - Fixed the preview_file_exists property in views.py
   - Created backup of all original audio files
   - Re-encoded problematic audio files with proper parameters (128kbps/48kHz/19s)

2. **Client-side Fixes**:
   - Added audio-url-fixer.js to transform /audio-serve/ URLs to /media/previews/ 
   - Enhanced audio-manager.js with better error handling and retry logic
   - Modified song_detail.html to prioritize direct media URLs

3. **Data Recovery**:
   - Used audio_content_hashes_fixed.json to map each file to its unique audio content
   - Created restore_unique_previews.py script to restore original audio while maintaining proper encoding

## Files Created/Modified

- **New Scripts**:
  - restore_unique_previews.py - Restores unique audio content while maintaining proper encoding
  - fix_broken_previews.py - Initial fix that replaced broken audio with the reference file

- **Modified Files**:
  - catalog/views.py - Fixed preview_file_exists property
  - catalog/static/catalog/js/audio-manager.js - Enhanced audio player with retry logic
  - catalog/static/catalog/js/audio-url-fixer.js - Added URL transformation for direct media access
  - catalog/templates/catalog/song_detail.html - Modified playWithDurationLimit function

## How to Run the Fix

To completely fix the issue while preserving unique audio content:

```bash
# First run in debug mode to check what would be modified
python restore_unique_previews.py --debug

# Then run for real
python restore_unique_previews.py

# Optionally specify a specific backup directory
python restore_unique_previews.py --backup-dir=20250318_192851
```

The script will:
1. Scan all files in the audio_content_hashes_fixed.json mapping
2. For each file, try to find a matching original in backup directories 
3. Re-encode each file with the correct parameters (128kbps, 48kHz, 19 seconds)
4. Ensure each song has unique audio content
5. Log all actions to restore_unique_previews.log

## Verification

After running the fix, verify that:

1. Audio plays correctly on all pages, not just the first few
2. Each song has its own unique audio, not all playing the same reference song
3. The duration of each audio file is around 19 seconds, not 30 seconds
4. Sample rate is 48kHz and bitrate is 128kbps for all files

## Troubleshooting

If any issues persist:

1. Check the logs in restore_unique_previews.log
2. Verify the audio files have proper encoding with:
   ```
   ffprobe -v error -select_streams a:0 -show_entries stream=codec_name,sample_rate,bit_rate,channels -of json /media/previews/filename.mp3
   ```
3. Test direct URL access in the browser using:
   ```
   http://yoursite.com/media/previews/filename.mp3
   ```
4. Clear browser cache and try again if needed

Original backups of all files are preserved in the backup_previews directory with timestamped folders.