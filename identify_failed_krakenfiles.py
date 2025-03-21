#!/usr/bin/env python3
"""
Script to identify songs with krakenfiles links that failed to be processed.
This script checks songs from the CartiCatalog database with krakenfiles.com links
and identifies those without valid preview files, creating a report for manual handling.

Usage:
  python identify_failed_krakenfiles.py
"""

import os
import sys
import json
import logging
from datetime import datetime

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("failed_krakenfiles.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Set up Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'carti_project.settings')

import django
django.setup()

from django.conf import settings
from catalog.models import CartiCatalog

# Directories
MEDIA_ROOT = settings.MEDIA_ROOT
PREVIEW_DIR = os.path.join(MEDIA_ROOT, 'previews')
REPORTS_DIR = os.path.join(settings.BASE_DIR, 'reports')

# Create reports directory if it doesn't exist
os.makedirs(REPORTS_DIR, exist_ok=True)

def extract_krakenfiles_urls_from_links(links_text):
    """Extract all krakenfiles.com URLs from the links text"""
    import re
    
    if not links_text:
        return []
    
    # Basic pattern for krakenfiles URLs
    basic_urls = re.findall(r'https?://(?:www\.)?krakenfiles\.com/(?:view|file)/[a-zA-Z0-9_-]+/?[^"\'\s]*', links_text)
    
    # Look for href attributes containing krakenfiles
    href_matches = re.findall(r'href=["\'](https?://(?:www\.)?krakenfiles\.com/[^"\']+)["\']', links_text)
    
    # Combine results
    all_urls = list(set(basic_urls + href_matches))
    
    if not all_urls:
        # Try simpler pattern just to find any mention of krakenfiles
        simple_matches = re.findall(r'krakenfiles\.com/[a-zA-Z0-9/_-]+', links_text)
        if simple_matches:
            all_urls = [f"https://{match}" for match in simple_matches]
    
    return all_urls

def check_preview_file_exists(song):
    """Check if a valid preview file exists for a song"""
    # Skip songs without preview_url
    if not song.preview_url:
        return False
    
    # Extract filename from preview_url
    filename = os.path.basename(song.preview_url)
    file_path = os.path.join(PREVIEW_DIR, filename)
    
    # Check if file exists and has non-zero size
    if os.path.exists(file_path) and os.path.getsize(file_path) > 10000:
        return True
    
    return False

def find_failed_krakenfiles_songs():
    """Find songs with krakenfiles.com links that failed to be processed"""
    # Get all songs with krakenfiles.com in their links
    songs = CartiCatalog.objects.filter(links__icontains="krakenfiles.com")
    logger.info(f"Found {songs.count()} songs with krakenfiles.com links")
    
    # Lists to track songs
    failed_songs = []
    successful_songs = []
    
    # Check each song
    for song in songs:
        # Extract krakenfiles URLs
        krakenfiles_urls = extract_krakenfiles_urls_from_links(song.links)
        
        # If no krakenfiles URLs found, skip
        if not krakenfiles_urls:
            logger.warning(f"No krakenfiles.com URLs found in song {song.id}: {song.name}")
            continue
        
        # Check if preview file exists
        if check_preview_file_exists(song):
            successful_songs.append({
                'id': song.id,
                'name': song.name,
                'preview_url': song.preview_url,
                'links': song.links,
                'krakenfiles_urls': krakenfiles_urls
            })
        else:
            failed_songs.append({
                'id': song.id,
                'name': song.name,
                'preview_url': song.preview_url,
                'links': song.links,
                'krakenfiles_urls': krakenfiles_urls
            })
    
    logger.info(f"Found {len(successful_songs)} successfully processed songs")
    logger.info(f"Found {len(failed_songs)} failed songs")
    
    return successful_songs, failed_songs

def generate_report(successful_songs, failed_songs):
    """Generate a report of failed songs"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    report_path = os.path.join(REPORTS_DIR, f"krakenfiles_report_{timestamp}.json")
    
    report = {
        'timestamp': timestamp,
        'total_krakenfiles_songs': len(successful_songs) + len(failed_songs),
        'successful_count': len(successful_songs),
        'failed_count': len(failed_songs),
        'failed_songs': failed_songs
    }
    
    # Write report to file
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)
    
    # Create a simplified CSV list of failed songs
    csv_path = os.path.join(REPORTS_DIR, f"failed_krakenfiles_{timestamp}.csv")
    with open(csv_path, 'w') as f:
        f.write("id,name,krakenfiles_url\n")
        for song in failed_songs:
            # Use the first krakenfiles URL for simplicity
            krakenfiles_url = song['krakenfiles_urls'][0] if song['krakenfiles_urls'] else "No URL found"
            f.write(f"{song['id']},{song['name'].replace(',', ' ')},{krakenfiles_url}\n")
    
    logger.info(f"Report generated: {report_path}")
    logger.info(f"CSV file generated: {csv_path}")
    
    return report_path, csv_path

if __name__ == "__main__":
    logger.info("Starting identification of failed krakenfiles songs...")
    successful_songs, failed_songs = find_failed_krakenfiles_songs()
    report_path, csv_path = generate_report(successful_songs, failed_songs)
    
    # Print summary
    print("\nProcess complete!")
    print(f"Total songs with krakenfiles.com links: {len(successful_songs) + len(failed_songs)}")
    print(f"Successfully processed: {len(successful_songs)}")
    print(f"Failed to process: {len(failed_songs)}")
    print(f"Report saved to: {report_path}")
    print(f"CSV file saved to: {csv_path}")
    print("\nSee failed_krakenfiles.log for detailed logs")