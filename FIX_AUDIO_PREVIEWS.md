# Fix for Audio Preview Issues

## Root Cause Identified

**Problem:** Audio previews aren't playing in browsers except for song ID 430.

**Root Cause:** Audio file bitrate issue
- Working file: 18.77s, **128kbps**, 48.0kHz
- Non-working files: 18.05s, **32kbps**, 44.1kHz

The extremely low bitrate (32kbps) is causing compatibility issues in browser audio players.

## Solution

### Step 1: Run the Fix Script

```
python3 fix_mp3_bitrates_corrected.py
```

This script will:
1. Back up all original audio files to `media/previews_backup/`
2. Convert all low bitrate files (32kbps) to standard quality (128kbps)
3. Leave already-good files unchanged

### Step 2: Verify the Fix

Open the audio comparison page in your browser:
- Go to any song detail page
- Click the "Audio Bitrate Analysis" button

You should see all audio files playing correctly after running the fix script.

### Technical Details

- Browser audio players often have issues with very low bitrate MP3 files
- 32kbps is significantly below the standard MP3 bitrate (128-320kbps)
- The conversion process keeps the same audio content but improves encoding quality
- This solution is permanent and doesn't require any JavaScript workarounds

If you need to restore the original files:
```
python3 restore_previews.py
```
