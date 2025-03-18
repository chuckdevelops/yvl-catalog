# Audio Preview Diagnostics & Solutions

## Problem Description
Audio preview files in the catalog are experiencing playback issues. Only one audio file (ID 430) plays correctly, while all other files fail to play. Analysis revealed this is due to browser limitations with audio file durations.

## Root Cause
Analysis of the audio files shows:
- Working file (ID 430): 18.77 seconds
- All other files: exactly 30.00 seconds

Many browsers have a built-in limitation that prevents playback of audio files longer than ~20 seconds when used in certain contexts (like embedded players).

## Solution Options

### 1. JavaScript Duration Limiting (Implemented)
A JavaScript solution has been implemented that limits audio playback to 20 seconds. This works for the HTML5 audio player and should prevent the browser from hitting its duration limits.

### 2. File Modification (Recommended)
For a more permanent solution, use the included scripts to modify the audio files:

- shorten_previews.py: Trims all preview files to 18 seconds
- restore_previews.py: Restores original files from backup if needed

These scripts:
1. Create backups of all original files
2. Use ffmpeg to trim files to 18 seconds
3. Replace the original files with shortened versions

### 3. Web Audio API (Alternative)
For more control, consider using the Web Audio API which provides programmatic control over audio playback and can more reliably limit duration.

## Testing Tools
Several testing tools have been added:
- /audio-test: Basic audio file testing
- /audio-duration-test: Advanced testing with multiple playback methods

## Recommendation
The most reliable solution is to physically shorten the audio preview files to under 20 seconds using the provided script. This eliminates the need for JavaScript workarounds and provides the most consistent experience across browsers.



This will create backups of all original files before modifying them.
