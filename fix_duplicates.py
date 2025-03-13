#!/usr/bin/env python3
"""
Script to identify and resolve duplicate songs that appear in both Released and Unreleased tabs.
"""

import os
import django
import time
from collections import defaultdict

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'carti_project.settings')
django.setup()

# Import models and management command
from catalog.models import CartiCatalog, SheetTab, SongMetadata, SongCategory
from django.db.models import Count

def find_duplicate_songs():
    """Find songs that might be duplicates by their similar names"""
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
    
    # Find potential duplicates where one is Released and one is Unreleased
    duplicates = []
    for name, songs in songs_by_name.items():
        if len(songs) > 1:
            # Check if this group has both Released and Unreleased songs
            has_released = any(
                hasattr(song, 'metadata') and song.metadata and song.metadata.sheet_tab == released_tab 
                for song in songs
            )
            has_unreleased = any(
                hasattr(song, 'metadata') and song.metadata and song.metadata.sheet_tab == unreleased_tab 
                for song in songs
            )
            
            if has_released and has_unreleased:
                duplicates.append((name, songs))
    
    return duplicates

def print_duplicate_details(name, songs):
    """Print detailed information about duplicate songs"""
    print(f"\nPotential duplicates for '{name}':")
    
    # Sort songs so Released songs come first
    songs.sort(key=lambda s: 0 if hasattr(s, 'metadata') and s.metadata and s.metadata.sheet_tab and s.metadata.sheet_tab.name == "Released" else 1)
    
    # Print song details
    for i, song in enumerate(songs):
        tab = song.metadata.sheet_tab.name if hasattr(song, 'metadata') and song.metadata and song.metadata.sheet_tab else "No tab"
        print(f"  {i+1}. ID: {song.id}, Name: {song.name}, Type: {song.type}, Tab: {tab}")
        print(f"     Era: {song.era}, Notes: {song.notes[:100]}{'...' if song.notes and len(song.notes) > 100 else ''}")
        print(f"     Links: {song.links[:100]}{'...' if song.links and len(song.links) > 100 else ''}")

def fix_duplicate_songs(duplicates, auto_fix=False):
    """Resolve duplicate song issues"""
    released_tab = SheetTab.objects.get(name="Released")
    unreleased_tab = SheetTab.objects.get(name="Unreleased")
    
    fixed = 0
    
    for name, songs in duplicates:
        print_duplicate_details(name, songs)
        
        # Sort songs by released/unreleased
        released_songs = [s for s in songs if hasattr(s, 'metadata') and s.metadata and s.metadata.sheet_tab == released_tab]
        unreleased_songs = [s for s in songs if hasattr(s, 'metadata') and s.metadata and s.metadata.sheet_tab == unreleased_tab]
        
        if auto_fix:
            # Auto-fix:
            # 1. Always trust songs with type "Album Track" or "Single" to be Released
            # 2. If there's no explicit Released type, check for "Streaming" in notes
            has_released_type = any(s.type in ["Album Track", "Single", "Feature"] for s in songs)
            has_streaming = any(s.notes and "Streaming" in s.notes for s in songs)
            
            if has_released_type or has_streaming:
                # This should be a Released song - move all to Released
                for song in unreleased_songs:
                    if song.metadata:
                        print(f"  AUTO-FIX: Moving song {song.id} from Unreleased to Released tab")
                        song.metadata.sheet_tab = released_tab
                        song.metadata.save()
                        fixed += 1
            else:
                # This should be an Unreleased song - keep as is
                pass
        else:
            # Interactive mode - show options
            print("\nOptions:")
            print("  1. Move all to Released tab")
            print("  2. Move all to Unreleased tab")
            print("  3. Skip this set")
            print("  4. Delete Unreleased duplicates")
            print("  5. Delete Released duplicates")
            
            try:
                choice = input("Choose an option (1-5): ")
                
                if choice == "1":
                    # Move all to Released
                    for song in unreleased_songs:
                        if song.metadata:
                            print(f"  FIXING: Moving song {song.id} from Unreleased to Released tab")
                            song.metadata.sheet_tab = released_tab
                            song.metadata.save()
                            fixed += 1
                elif choice == "2":
                    # Move all to Unreleased
                    for song in released_songs:
                        if song.metadata:
                            print(f"  FIXING: Moving song {song.id} from Released to Unreleased tab")
                            song.metadata.sheet_tab = unreleased_tab
                            song.metadata.save()
                            fixed += 1
                elif choice == "3":
                    # Skip
                    print("  Skipping this set")
                    continue
                elif choice == "4":
                    # Delete Unreleased duplicates
                    for song in unreleased_songs:
                        print(f"  DELETING: Song {song.id} from Unreleased tab")
                        song.delete()
                        fixed += 1
                elif choice == "5":
                    # Delete Released duplicates
                    for song in released_songs:
                        print(f"  DELETING: Song {song.id} from Released tab")
                        song.delete()
                        fixed += 1
                else:
                    print("  Invalid choice, skipping this set")
            except (EOFError, KeyboardInterrupt):
                print("\nOperation cancelled.")
                return
    
    return fixed

def main():
    print("Searching for potential duplicate songs...")
    duplicates = find_duplicate_songs()
    print(f"Found {len(duplicates)} potential duplicate sets")
    
    if duplicates:
        try:
            # In an interactive environment
            auto_mode = input("Do you want to use auto-fix mode? (y/n): ").lower() == 'y'
            fixed = fix_duplicate_songs(duplicates, auto_fix=auto_mode)
        except (EOFError, KeyboardInterrupt):
            # In a non-interactive environment, use auto-fix
            print("Non-interactive environment detected, using auto-fix mode")
            fixed = fix_duplicate_songs(duplicates, auto_fix=True)
        
        print(f"Fixed {fixed} duplicate issues")

if __name__ == "__main__":
    main()