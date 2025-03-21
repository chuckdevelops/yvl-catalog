# Manual Process for Krakenfiles Link Processing

This document outlines the process for handling krakenfiles.com links that fail to be processed automatically by the `fix_krakenfiles_links.py` script.

## Overview

The krakenfiles.com website uses anti-bot measures that prevent simple direct access to their audio files. While we've successfully implemented a solution that works for many krakenfiles URLs (those that include a media player on the page), some URLs only offer download forms with reCAPTCHA protection.

This process provides a semi-automated approach for handling those files that require manual download.

## Step 1: Identify Failed Songs

Run the identification script to find songs with krakenfiles links that couldn't be processed automatically:

```bash
python identify_failed_krakenfiles.py
```

This script will:
1. Check all songs with krakenfiles.com links in the database
2. Identify which ones have working preview files and which don't
3. Generate a report file in the `reports` directory:
   - A detailed JSON report with all information
   - A simple CSV file with song IDs, names, and krakenfiles URLs

The CSV file will be named like `failed_krakenfiles_20250320_123456.csv` and located in the `reports` directory.

## Step 2: Manually Download Files

For each song in the CSV file, you'll need to:

1. Open the krakenfiles URL in a web browser
2. Solve the reCAPTCHA and download the audio file
3. Rename the downloaded file to match its song ID, like `123.mp3` (where 123 is the song ID)
4. Place all downloaded files in the `manual_downloads` directory

## Step 3: Process the Manual Files

Run the processing script to handle the manually downloaded files:

```bash
python manual_process_krakenfiles.py
```

This script will:
1. Scan the `manual_downloads` directory for MP3 files
2. Process each file to create a standardized 30-second preview
3. Update the database with the new preview URLs
4. Generate a report of successfully processed files

You can also run it with `--debug` to see what would happen without making changes:

```bash
python manual_process_krakenfiles.py --debug
```

## Requirements

- FFmpeg must be installed and available in the system PATH
- Python dependencies as per project requirements.txt
- Django environment set up correctly

## Troubleshooting

- If a file fails to process, check the log file `manual_krakenfiles_process.log` for details
- Verify that the file naming follows the pattern `song_id.mp3` (e.g., `123.mp3`)
- Make sure the directory structure exists as expected