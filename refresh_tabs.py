#!/usr/bin/env python3
"""
Script to refresh all song tab assignments, including the new multi-category system.
Run this after updating the categorization logic.
"""

import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'carti_project.settings')
django.setup()

# Import models and management command
from catalog.models import CartiCatalog, SheetTab, SongMetadata, SongCategory
from catalog.management.commands.associate_songs_with_tabs import Command

def main():
    # Clear existing secondary categories first
    print("Clearing existing song categories...")
    SongCategory.objects.all().delete()
    
    # Run the associate_songs_with_tabs command with force flag
    cmd = Command()
    print("Reassigning all song tabs...")
    cmd.handle(force=True, respect_scraper=False)
    
    print("Done!")

if __name__ == "__main__":
    main()