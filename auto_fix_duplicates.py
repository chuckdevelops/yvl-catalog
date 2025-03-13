#!/usr/bin/env python3
"""
Script to automatically fix duplicate songs that appear in both Released and Unreleased tabs.
"""

import os
import django
from collections import defaultdict

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'carti_project.settings')
django.setup()

# Import models
from catalog.models import CartiCatalog, SheetTab, SongMetadata

def fix_duplicates():
    """Find and fix songs that appear in both Released and Unreleased categories"""
    print("Finding and fixing duplicate songs...")
    
    # Get all songs
    all_songs = CartiCatalog.objects.select_related('metadata__sheet_tab').all()
    
    # Get released and unreleased tabs
    released_tab = SheetTab.objects.get(name="Released")
    unreleased_tab = SheetTab.objects.get(name="Unreleased")
    
    # Group songs by name (lowercase for case-insensitive comparison)
    songs_by_name = defaultdict(list)
    for song in all_songs:
        if song.name:
            # Use a standardized name for comparison
            # Remove common variations like [V1], (prod. X), etc.
            std_name = song.name.lower()
            std_name = std_name.split('[')[0].split('(')[0].strip()
            songs_by_name[std_name].append(song)
    
    fixed_count = 0
    # Process each group of songs with the same base name
    for name, songs in songs_by_name.items():
        if len(songs) <= 1:
            continue  # Skip single songs
        
        # Check if this group has both Released and Unreleased songs
        released_songs = [s for s in songs if hasattr(s, 'metadata') and s.metadata and s.metadata.sheet_tab == released_tab]
        unreleased_songs = [s for s in songs if hasattr(s, 'metadata') and s.metadata and s.metadata.sheet_tab == unreleased_tab]
        
        if not (released_songs and unreleased_songs):
            continue  # Skip if not both categories present
        
        print(f"\nDuplicates for '{name}':")
        for i, song in enumerate(songs):
            tab = song.metadata.sheet_tab.name if hasattr(song, 'metadata') and song.metadata and song.metadata.sheet_tab else "No tab"
            print(f"  {i+1}. ID: {song.id}, Name: {song.name}, Type: {song.type}, Tab: {tab}")
        
        # AUTO-FIX LOGIC:
        # 1. If any song has Album Track, Single, or Feature type, move all to Released
        # 2. If no clear type but any has Streaming note, move all to Released
        # 3. Otherwise, favor Released tab for consistency
        has_released_type = any(s.type in ["Album Track", "Single", "Feature"] for s in songs)
        has_streaming = any(s.notes and "Streaming" in s.notes for s in songs)
        
        if has_released_type or has_streaming:
            # Move unreleased duplicates to Released
            for song in unreleased_songs:
                if song.metadata:
                    print(f"  FIX: Moving '{song.name}' (ID: {song.id}) from Unreleased to Released")
                    song.metadata.sheet_tab = released_tab
                    song.metadata.save()
                    fixed_count += 1
    
    return fixed_count

if __name__ == "__main__":
    fixed = fix_duplicates()
    print(f"\nFixed {fixed} duplicate song issues")