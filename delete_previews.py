#!/usr/bin/env python3
"""
Script to delete all preview files and start fresh.
This script:
1. Backs up all current preview files to a timestamped directory
2. Deletes all preview files from the media/previews directory
3. Optionally resets preview_url fields in the database
4. Logs all actions for audit purposes

Usage:
  python delete_previews.py [--debug] [--reset-db]
"""

import os
import sys
import uuid
import logging
import argparse
import shutil
from datetime import datetime

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("delete_previews.log"),
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
from django.db import transaction

# Directories
MEDIA_ROOT = settings.MEDIA_ROOT
PREVIEW_DIR = os.path.join(MEDIA_ROOT, 'previews')
BACKUP_DIR = os.path.join(settings.BASE_DIR, 'backup_previews', 
                         datetime.now().strftime('%Y%m%d_%H%M%S'))

def backup_current_previews():
    """Backup all current preview files"""
    logger.info(f"Backing up all current previews to {BACKUP_DIR}")
    
    # Create backup directory
    os.makedirs(BACKUP_DIR, exist_ok=True)
    
    count = 0
    for filename in os.listdir(PREVIEW_DIR):
        if filename.endswith('.mp3'):
            src_path = os.path.join(PREVIEW_DIR, filename)
            dst_path = os.path.join(BACKUP_DIR, filename)
            try:
                shutil.copy2(src_path, dst_path)
                count += 1
            except Exception as e:
                logger.error(f"Failed to backup {filename}: {e}")
    
    logger.info(f"Backed up {count} preview files")
    return count

def delete_all_previews():
    """Delete all preview files from media/previews directory"""
    logger.info(f"Deleting all preview files from {PREVIEW_DIR}")
    
    count = 0
    for filename in os.listdir(PREVIEW_DIR):
        if filename.endswith('.mp3'):
            file_path = os.path.join(PREVIEW_DIR, filename)
            try:
                os.remove(file_path)
                count += 1
            except Exception as e:
                logger.error(f"Failed to delete {filename}: {e}")
    
    logger.info(f"Deleted {count} preview files")
    return count

def reset_preview_urls():
    """Reset all preview_url fields in the database"""
    logger.info("Resetting all preview_url fields in the database")
    
    try:
        with transaction.atomic():
            # Get count of songs with previews
            count = CartiCatalog.objects.exclude(preview_url='').count()
            
            # Reset all preview_url fields
            CartiCatalog.objects.all().update(preview_url='')
            
            logger.info(f"Reset preview_url field for {count} songs")
            return count
    except Exception as e:
        logger.exception(f"Error resetting preview_url fields: {e}")
        return 0

def main(debug=False, reset_db=False):
    """Main function to delete all previews"""
    logger.info(f"Starting {'debug check' if debug else 'deletion'} of all preview files")
    
    if debug:
        # Count files that would be affected
        preview_count = len([f for f in os.listdir(PREVIEW_DIR) if f.endswith('.mp3')])
        db_count = CartiCatalog.objects.exclude(preview_url='').count()
        
        logger.info(f"Debug mode: would delete {preview_count} preview files")
        if reset_db:
            logger.info(f"Debug mode: would reset preview_url field for {db_count} songs")
        
        return {
            'backup_count': preview_count,
            'delete_count': preview_count,
            'reset_count': db_count if reset_db else 0
        }
    
    # Backup current previews
    backup_count = backup_current_previews()
    
    # Delete all previews
    delete_count = delete_all_previews()
    
    # Reset database if requested
    reset_count = 0
    if reset_db:
        reset_count = reset_preview_urls()
    
    return {
        'backup_count': backup_count,
        'delete_count': delete_count,
        'reset_count': reset_count
    }

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Delete all preview files and start fresh.')
    parser.add_argument('--debug', action='store_true', help='Run in debug mode without making changes')
    parser.add_argument('--reset-db', action='store_true', help='Reset preview_url fields in the database')
    args = parser.parse_args()
    
    # Run main function
    results = main(debug=args.debug, reset_db=args.reset_db)
    
    # Print final results
    print("\nProcess complete!")
    print(f"Backup count: {results['backup_count']}")
    print(f"Delete count: {results['delete_count']}")
    if args.reset_db:
        print(f"Reset count: {results['reset_count']}")
    print("\nSee delete_previews.log for detailed logs")