#!/usr/bin/env python3
"""
Script to fix all krakenfiles.com preview issues by:
1. Creating a backup of all current preview files
2. Identifying all songs with krakenfiles.com links in the database
3. Downloading audio content directly from krakenfiles.com using browser automation
4. Re-encoding with standardized parameters (128kbps, 48kHz, 30-second duration)
5. Updating the database with new preview URLs

This script prioritizes getting correct audio content while maintaining
consistent format across all files.

Usage:
  python fix_krakenfiles_links.py [--debug] [--limit=N] [--song-id=ID]

Requirements:
  - selenium
  - webdriver-manager
  - ffmpeg
  - curl

Install with:
  pip install selenium webdriver-manager
"""

import os
import sys
import json
import uuid
import re
import subprocess
import logging
import time
import argparse
import hashlib
from datetime import datetime
from pathlib import Path

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("fix_krakenfiles_links.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Check for required Python packages
try:
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from webdriver_manager.chrome import ChromeDriverManager
except ImportError:
    logger.error("Required packages not installed. Run: pip install selenium webdriver-manager")
    sys.exit(1)

# Set up Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'carti_project.settings')

import django
django.setup()

from django.conf import settings
from catalog.models import CartiCatalog
from django.db import transaction

# Directories
MEDIA_ROOT = settings.MEDIA_ROOT
PREVIEW_DIR = os.path.join(MEDIA_ROOT, 'previews')
TEMP_DIR = os.path.join(settings.BASE_DIR, 'temp_previews')
BACKUP_DIR = os.path.join(settings.BASE_DIR, 'backup_previews', 
                         datetime.now().strftime('%Y%m%d_%H%M%S'))
DOWNLOAD_DIR = os.path.join(settings.BASE_DIR, 'temp_downloads')

# Hash file location
AUDIO_HASHES_FILE = os.path.join(settings.BASE_DIR, 'audio_content_hashes_fixed.json')

# Create necessary directories
os.makedirs(TEMP_DIR, exist_ok=True)
os.makedirs(BACKUP_DIR, exist_ok=True)
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

def get_file_md5(file_path):
    """Calculate MD5 hash of a file"""
    try:
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    except Exception as e:
        logger.error(f"Error calculating MD5 for {file_path}: {e}")
        return None

def backup_current_previews():
    """Backup all current preview files"""
    logger.info(f"Backing up all current previews to {BACKUP_DIR}")
    count = 0
    for filename in os.listdir(PREVIEW_DIR):
        if filename.endswith('.mp3'):
            src_path = os.path.join(PREVIEW_DIR, filename)
            dst_path = os.path.join(BACKUP_DIR, filename)
            try:
                import shutil
                shutil.copy2(src_path, dst_path)
                count += 1
            except Exception as e:
                logger.error(f"Failed to backup {filename}: {e}")
    logger.info(f"Backed up {count} preview files")
    return count

def extract_krakenfiles_urls(links_text):
    """Extract all krakenfiles.com URLs from the links text"""
    if not links_text:
        return []
    
    # Log the full links for debugging
    logger.info(f"Checking links text: {links_text}")
    
    # Basic pattern for krakenfiles URLs
    basic_urls = re.findall(r'https?://(?:www\.)?krakenfiles\.com/(?:view|file)/[a-zA-Z0-9_-]+/?[^"\'\s]*', links_text)
    
    # Look for href attributes containing krakenfiles
    href_matches = re.findall(r'href=["\'](https?://(?:www\.)?krakenfiles\.com/[^"\']+)["\']', links_text)
    
    # Combine results
    all_urls = list(set(basic_urls + href_matches))
    
    if all_urls:
        logger.info(f"Found krakenfiles URLs: {all_urls}")
    else:
        logger.info("No krakenfiles URLs found in basic or href patterns")
        
        # Try simpler pattern just to find any mention of krakenfiles
        simple_matches = re.findall(r'krakenfiles\.com/[a-zA-Z0-9/_-]+', links_text)
        if simple_matches:
            all_urls = [f"https://{match}" for match in simple_matches]
            logger.info(f"Found krakenfiles mentions: {all_urls}")
    
    return all_urls

def download_from_krakenfiles_browser(url):
    """Download a file from krakenfiles.com using browser automation"""
    logger.info(f"Attempting to download from krakenfiles URL: {url}")
    
    # Set up headless browser
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    driver = None
    try:
        # Initialize the browser
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        
        # Visit the page
        driver.get(url)
        logger.info(f"Loaded URL: {url}")
        
        # Wait for page to load fully
        time.sleep(5)  # Allow JavaScript to execute
        wait = WebDriverWait(driver, 20)
        
        download_url = None
        
        # Step 1: Look for <audio> tag with id "jp_audio_0"
        try:
            logger.info("Looking for audio element with id 'jp_audio_0'")
            audio_element = driver.find_element(By.ID, "jp_audio_0")
            download_url = audio_element.get_attribute("src")
            if download_url:
                logger.info(f"Found direct audio URL in jp_audio_0: {download_url}")
                return download_url
        except Exception as e:
            logger.warning(f"Could not find jp_audio_0 element: {str(e)}")
        
        # Step 2: Look for JavaScript variables with .m4a URLs
        logger.info("Looking for .m4a URLs in JavaScript variables")
        m4a_js_check = """
        // Search for m4a URLs in all script tags and global variables
        function findM4aUrls() {
            const m4aUrls = [];
            
            // Check window variables
            for (let prop in window) {
                try {
                    if (typeof window[prop] === 'string' && 
                        window[prop].includes('.m4a') && 
                        window[prop].startsWith('http')) {
                        m4aUrls.push(window[prop]);
                    }
                } catch (e) { /* ignore errors */ }
            }
            
            // Check script content
            const scripts = document.querySelectorAll('script');
            for (const script of scripts) {
                if (!script.textContent) continue;
                
                const content = script.textContent;
                const matches = content.match(/['"]https?:\/\/[^'"]+\.m4a['"]/g);
                if (matches) {
                    matches.forEach(match => {
                        m4aUrls.push(match.replace(/['"]/g, ''));
                    });
                }
            }
            
            return m4aUrls;
        }
        
        return findM4aUrls();
        """
        
        try:
            m4a_urls = driver.execute_script(m4a_js_check)
            if m4a_urls and len(m4a_urls) > 0:
                download_url = m4a_urls[0]
                logger.info(f"Found .m4a URL in JavaScript: {download_url}")
                return download_url
        except Exception as e:
            logger.warning(f"Error executing JavaScript to find m4a URLs: {str(e)}")
        
        # Step 3: Look for download button elements
        logger.info("Looking for download button elements")
        download_button_selectors = [
            "div.download-now-text",
            "a.download-button",
            "a[href*='download']",
            "button.download-button",
            "div.dl-btn",
            "a.dl-btn"
        ]
        
        download_button = None
        for selector in download_button_selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    download_button = elements[0]
                    logger.info(f"Found download button with selector: {selector}")
                    break
            except Exception as e:
                pass
        
        if download_button:
            # Check parent <a> tag for href
            try:
                parent_a = download_button.find_element(By.XPATH, "./ancestor::a[1]")
                href = parent_a.get_attribute("href")
                if href and (href.startswith("http") and 
                           (href.endswith(".mp3") or 
                            href.endswith(".m4a") or 
                            "download" in href)):
                    download_url = href
                    logger.info(f"Found download URL in parent a tag: {download_url}")
                    return download_url
            except Exception as e:
                logger.warning(f"No valid parent a tag found: {str(e)}")
            
            # If download URL not found, analyze JavaScript for download links
            logger.info("Looking for JavaScript download functions")
            js_analysis = """
            function analyzeForDownloadUrl() {
                // Look for onclick handlers that contain download URLs
                const clickElements = document.querySelectorAll('[onclick]');
                for (const el of clickElements) {
                    const onclick = el.getAttribute('onclick');
                    if (onclick && onclick.includes('download')) {
                        // Extract URL if present in onclick
                        const matches = onclick.match(/['"]https?:\/\/[^'"]+['"]/);
                        if (matches) return matches[0].replace(/['"]/g, '');
                    }
                }
                
                // Look for data attributes that might contain download URLs
                const dataElements = document.querySelectorAll('[data-url], [data-href], [data-download]');
                for (const el of dataElements) {
                    if (el.dataset.url) return el.dataset.url;
                    if (el.dataset.href) return el.dataset.href;
                    if (el.dataset.download) return el.dataset.download;
                }
                
                // Look for any URL in window variables
                for (let prop in window) {
                    try {
                        if (typeof window[prop] === 'string' && 
                            window[prop].startsWith('http') && 
                            (window[prop].includes('/download/') || 
                             window[prop].endsWith('.mp3') || 
                             window[prop].endsWith('.m4a'))) {
                            return window[prop];
                        }
                    } catch (e) { /* ignore errors */ }
                }
                
                return null;
            }
            
            return analyzeForDownloadUrl();
            """
            
            try:
                js_url = driver.execute_script(js_analysis)
                if js_url:
                    download_url = js_url
                    logger.info(f"Found download URL from JavaScript analysis: {download_url}")
                    return download_url
            except Exception as e:
                logger.warning(f"Error in JavaScript analysis: {str(e)}")
            
            # Last resort: Attempt to click the button and monitor network requests
            logger.info("Attempting to click download button and monitor network")
            try:
                # Set up interceptor before clicking
                driver.execute_script("""
                    window.downloadUrls = [];
                    const originalOpen = XMLHttpRequest.prototype.open;
                    XMLHttpRequest.prototype.open = function(method, url) {
                        if (url.includes('.mp3') || url.includes('.m4a') || 
                            url.includes('/download/') || url.includes('/stream/')) {
                            window.downloadUrls.push(url);
                        }
                        return originalOpen.apply(this, arguments);
                    };
                    
                    // Also monitor fetch requests
                    const originalFetch = window.fetch;
                    window.fetch = function(url, options) {
                        if (typeof url === 'string' && 
                           (url.includes('.mp3') || url.includes('.m4a') || 
                            url.includes('/download/') || url.includes('/stream/'))) {
                            window.downloadUrls.push(url);
                        }
                        return originalFetch.apply(this, arguments);
                    };
                """)
                
                # Click the button
                download_button.click()
                
                # Wait for any network requests to complete
                time.sleep(3)
                
                # Check if we captured any download URLs
                download_urls = driver.execute_script("return window.downloadUrls;")
                if download_urls and len(download_urls) > 0:
                    download_url = download_urls[0]
                    logger.info(f"Captured download URL after click: {download_url}")
                    return download_url
            except Exception as e:
                logger.warning(f"Error clicking button or capturing network: {str(e)}")
        
        # If we still don't have a URL, search the entire page source for audio files
        if not download_url:
            logger.info("Searching page source for audio file URLs")
            page_source = driver.page_source
            url_patterns = [
                r'(https?://[^"\'\s]+\.mp3)',
                r'(https?://[^"\'\s]+\.m4a)',
                r'(https?://[^"\'\s]+/download/[^"\'\s]+)',
                r'(https?://[^"\'\s]+/stream/[^"\'\s]+)'
            ]
            
            for pattern in url_patterns:
                matches = re.findall(pattern, page_source)
                if matches:
                    download_url = matches[0]
                    logger.info(f"Found audio URL in page source: {download_url}")
                    return download_url
        
        if not download_url:
            logger.error("Download not available - could not extract audio URL")
            # Take screenshot for debugging
            debug_path = os.path.join(TEMP_DIR, f"krakenfiles_debug_{uuid.uuid4()}.png")
            driver.save_screenshot(debug_path)
            logger.info(f"Saved debug screenshot to {debug_path}")
            return None
            
        # Now download the file using curl
        output_path = os.path.join(DOWNLOAD_DIR, f"kraken_{uuid.uuid4()}.mp3")
        
        cmd = [
            "curl",
            "-L",
            "-A", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "-o", output_path,
            "--max-time", "300",  # Longer timeout for larger files
            download_url
        ]
        
        result = subprocess.run(cmd, capture_output=True, check=False)
        
        # Check if download succeeded
        if result.returncode == 0 and os.path.exists(output_path) and os.path.getsize(output_path) > 10000:
            logger.info(f"Successfully downloaded from Krakenfiles: {os.path.getsize(output_path)} bytes")
            return output_path
        else:
            logger.error(f"Krakenfiles download failed: {result.stderr.decode() if hasattr(result, 'stderr') else 'Unknown error'}")
            if os.path.exists(output_path):
                os.remove(output_path)
            return None
    
    except Exception as e:
        logger.exception(f"Error downloading from Krakenfiles: {e}")
        return None
    
    finally:
        # Always close the browser
        if driver:
            try:
                driver.quit()
            except:
                pass

def download_audio_from_krakenfiles(song):
    """Try to download audio content from krakenfiles.com links in the song"""
    if not song.links:
        return None
    
    # Extract all krakenfiles URLs from the song links
    krakenfiles_urls = extract_krakenfiles_urls(song.links)
    
    if not krakenfiles_urls:
        logger.warning(f"No krakenfiles.com links found for song {song.id}: {song.name}")
        return None
    
    # Try each URL until we get a successful download
    for url in krakenfiles_urls:
        downloaded_file = download_from_krakenfiles_browser(url)
        if downloaded_file:
            logger.info(f"Successfully downloaded from krakenfiles.com URL: {url}")
            return downloaded_file
    
    # If we get here, we failed to download from any URL
    logger.error(f"Failed to download from any krakenfiles.com URL for song {song.id}: {song.name}")
    return None

def verify_audio_has_sound(file_path):
    """Verify that an audio file actually contains sound (not silence)"""
    try:
        # Use ffprobe to get audio specs
        cmd = [
            'ffprobe',
            '-v', 'error',
            '-select_streams', 'a:0',
            '-show_entries', 'stream=duration,bit_rate,sample_rate',
            '-of', 'json',
            file_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
        
        if result.returncode != 0:
            logger.warning(f"FFprobe failed: {result.stderr}")
            return False
            
        # Parse the JSON output
        try:
            data = json.loads(result.stdout)
            if 'streams' not in data or len(data['streams']) == 0:
                logger.warning("No audio streams found")
                return False
                
            # File needs to have reasonable properties
            stream = data['streams'][0]
            
            # Perform sound detection using ffmpeg's volumedetect filter
            volume_cmd = [
                'ffmpeg',
                '-i', file_path,
                '-af', 'volumedetect',
                '-f', 'null',
                '-y',
                '/dev/null'
            ]
            
            volume_result = subprocess.run(volume_cmd, capture_output=True, text=True, check=False)
            
            # Check for mean_volume in the output
            if 'mean_volume' in volume_result.stderr:
                # Extract the mean volume value
                mean_vol_match = re.search(r'mean_volume: ([-\d.]+) dB', volume_result.stderr)
                if mean_vol_match:
                    mean_vol = float(mean_vol_match.group(1))
                    # If mean volume is very low (e.g., below -50dB), it might be silent
                    if mean_vol < -50:
                        logger.warning(f"Audio file has very low volume: {mean_vol} dB")
                        return False
            
            return True
            
        except json.JSONDecodeError:
            logger.warning("Could not parse FFprobe output")
            return False
            
    except Exception as e:
        logger.exception(f"Error verifying audio: {e}")
        return False

def create_standardized_preview(input_file, output_file):
    """Create a standardized preview with consistent parameters"""
    try:
        logger.info(f"Creating standardized preview from {input_file}")
        
        # Get duration of input file
        cmd = [
            'ffprobe',
            '-v', 'error',
            '-show_entries', 'format=duration',
            '-of', 'default=noprint_wrappers=1:nokey=1',
            input_file
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
        
        # Default parameters
        start_time = 0
        duration = 30  # Target 30 seconds for previews
        
        # If we can get the duration, calculate a good starting point
        if result.returncode == 0:
            file_duration = float(result.stdout.strip())
            logger.info(f"Source file duration: {file_duration} seconds")
            
            # Choose start point based on file length
            if file_duration > 90:
                # For longer tracks, skip intro and start at 10% of duration
                start_time = min(file_duration * 0.1, 30)
            elif file_duration > 45:
                # For medium tracks, start a bit in
                start_time = 5
            
            logger.info(f"Using start time: {start_time} seconds")
        
        # Process with ffmpeg - use high quality settings
        cmd = [
            'ffmpeg',
            '-y',
            '-ss', str(start_time),
            '-i', input_file,
            '-t', str(duration),
            '-c:a', 'libmp3lame',
            '-ar', '48000',  # 48kHz sample rate
            '-ac', '2',      # Stereo
            '-b:a', '128k',  # 128kbps bitrate
            output_file
        ]
        
        result = subprocess.run(cmd, capture_output=True, check=False)
        
        if result.returncode != 0:
            logger.error(f"FFmpeg failed: {result.stderr.decode() if hasattr(result, 'stderr') else 'Unknown error'}")
            
            # Try simpler approach without fades
            logger.info("Trying simpler FFmpeg approach")
            simple_cmd = [
                'ffmpeg',
                '-y',
                '-ss', str(start_time),
                '-i', input_file,
                '-t', str(duration),
                '-c:a', 'libmp3lame',
                '-ar', '48000',
                '-b:a', '128k',
                output_file
            ]
            
            simple_result = subprocess.run(simple_cmd, capture_output=True, check=False)
            
            if simple_result.returncode != 0:
                logger.error(f"Simple FFmpeg approach also failed")
                return False
        
        # Verify the output file
        if os.path.exists(output_file) and os.path.getsize(output_file) > 10000:
            if verify_audio_has_sound(output_file):
                logger.info(f"Successfully created standardized preview: {os.path.getsize(output_file)} bytes")
                
                # Calculate hash for the new file
                file_hash = get_file_md5(output_file)
                if file_hash:
                    logger.info(f"Preview file hash: {file_hash}")
                
                return True
            else:
                logger.error("Created preview has no sound")
                return False
        else:
            logger.error(f"Output file is missing or too small")
            return False
            
    except Exception as e:
        logger.exception(f"Error creating standardized preview: {e}")
        return False

def update_audio_hashes_file(song_id, song_name, filename, file_path):
    """Update the audio hashes file with the new preview information"""
    try:
        # Calculate hash for the file
        file_hash = get_file_md5(file_path)
        if not file_hash:
            logger.error(f"Could not calculate hash for {file_path}")
            return False
            
        # Load existing hashes if available
        audio_hashes = {}
        if os.path.exists(AUDIO_HASHES_FILE):
            try:
                with open(AUDIO_HASHES_FILE, 'r') as f:
                    audio_hashes = json.load(f)
            except json.JSONDecodeError:
                logger.error(f"Error parsing {AUDIO_HASHES_FILE}, creating new file")
        
        # Add or update the entry
        audio_hashes[file_hash] = {
            "song_id": song_id,
            "song_name": song_name,
            "filename": filename,
            "timestamp": time.time()
        }
        
        # Save the updated file
        with open(AUDIO_HASHES_FILE, 'w') as f:
            json.dump(audio_hashes, f, indent=2)
            
        logger.info(f"Updated {AUDIO_HASHES_FILE} with hash for song {song_id}")
        return True
        
    except Exception as e:
        logger.exception(f"Error updating audio hashes file: {e}")
        return False

def find_songs_with_krakenfiles_links():
    """Find all songs with krakenfiles.com links"""
    try:
        # Get all songs that have "krakenfiles.com" in their links
        songs = CartiCatalog.objects.filter(links__icontains="krakenfiles.com")
        logger.info(f"Found {songs.count()} songs with krakenfiles.com links")
        return songs
    except Exception as e:
        logger.exception(f"Exception finding songs: {e}")
        return []

def find_song_by_id(song_id):
    """Find a specific song by ID"""
    try:
        song = CartiCatalog.objects.get(id=song_id)
        return [song]  # Return as list for consistency with other find functions
    except CartiCatalog.DoesNotExist:
        logger.error(f"Song with ID {song_id} not found")
        return []
    except Exception as e:
        logger.exception(f"Error finding song by ID: {e}")
        return []

def fix_krakenfiles_link_previews(debug=False, limit=None, song_id=None):
    """Fix all songs with krakenfiles.com links that have broken previews"""
    # First, back up all current previews
    if not debug:
        backup_count = backup_current_previews()
        logger.info(f"Backed up {backup_count} preview files")
    
    # Find songs to process
    if song_id:
        songs = find_song_by_id(song_id)
        logger.info(f"Processing specific song ID: {song_id}")
    else:
        songs = find_songs_with_krakenfiles_links()
    
    if limit and not song_id:
        songs = songs[:limit]
    
    total_count = len(songs)
    if total_count == 0:
        logger.warning("No songs found to process")
        return {
            'total': 0,
            'success': 0,
            'failed': 0
        }
    
    success_count = 0
    failed_count = 0
    
    for i, song in enumerate(songs, 1):
        logger.info(f"[{i}/{total_count}] Processing: {song.name} (ID: {song.id})")
        
        if debug:
            logger.info(f"Debug mode: would download and process audio for song {song.id}")
            continue
            
        # Download audio from krakenfiles.com
        downloaded_file = download_audio_from_krakenfiles(song)
        
        if not downloaded_file:
            logger.error(f"Failed to download audio for song {song.id}: {song.name}")
            failed_count += 1
            continue
        
        try:
            # Create a new preview filename
            preview_filename = f"{uuid.uuid4()}.mp3"
            preview_path = os.path.join(PREVIEW_DIR, preview_filename)
            
            # Create the standardized preview
            if create_standardized_preview(downloaded_file, preview_path):
                # Update the song preview URL in the database
                with transaction.atomic():
                    old_preview_url = song.preview_url
                    song.preview_url = f"/media/previews/{preview_filename}"
                    song.save(update_fields=['preview_url'])
                    
                logger.info(f"Updated preview URL from {old_preview_url} to {song.preview_url}")
                
                # Update the audio hashes file
                update_audio_hashes_file(song.id, song.name, preview_filename, preview_path)
                
                success_count += 1
                logger.info(f"Successfully updated preview for song {song.id}: {song.name}")
            else:
                logger.error(f"Failed to create preview for song {song.id}: {song.name}")
                failed_count += 1
        finally:
            # Clean up downloaded file
            if downloaded_file and os.path.exists(downloaded_file):
                os.remove(downloaded_file)
    
    logger.info(f"\nProcessing complete!")
    logger.info(f"Total songs: {total_count}")
    logger.info(f"Successfully fixed: {success_count}")
    logger.info(f"Failed: {failed_count}")
    
    return {
        'total': total_count,
        'success': success_count,
        'failed': failed_count
    }

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Fix preview issues for krakenfiles.com links.')
    parser.add_argument('--debug', action='store_true', help='Run in debug mode without making changes')
    parser.add_argument('--limit', type=int, help='Limit the number of songs to process')
    parser.add_argument('--song-id', type=int, help='Process only a specific song ID')
    args = parser.parse_args()
    
    # Check if FFmpeg and curl are installed
    try:
        subprocess.run(["ffmpeg", "-version"], capture_output=True, text=True, check=True)
        subprocess.run(["curl", "--version"], capture_output=True, text=True, check=True)
    except (FileNotFoundError, subprocess.SubprocessError):
        logger.error("Error: FFmpeg or curl is not installed or not in the PATH. Please install them first.")
        sys.exit(1)
        
    logger.info(f"Starting {'debug check' if args.debug else 'fix'} of krakenfiles.com previews...")
    
    # Process songs
    results = fix_krakenfiles_link_previews(debug=args.debug, limit=args.limit, song_id=args.song_id)
    
    # Print final results
    print("\nProcess complete!")
    print(f"Total songs processed: {results['total']}")
    print(f"Successfully fixed: {results['success']}")
    print(f"Failed: {results['failed']}")
    print("\nSee fix_krakenfiles_links.log for detailed logs")