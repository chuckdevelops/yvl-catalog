#!/usr/bin/env python3
"""
Script to identify and resolve duplicate songs based on information completeness.
Prioritizes keeping versions with more complete information (links, notes, etc.)
"""

import os
import django
from collections import defaultdict

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'carti_project.settings')
django.setup()

# Import models
from catalog.models import CartiCatalog, SheetTab, SongMetadata
from django.db.models import Count

def find_info_duplicates():
    """Find duplicate songs and evaluate which has more information"""
    # Get all songs
    all_songs = CartiCatalog.objects.all()
    
    # Group songs by name (lowercase for case-insensitive comparison)
    songs_by_name = defaultdict(list)
    for song in all_songs:
        if song.name:
            # Use a standardized name for comparison
            # Remove common variations like [V1], (prod. X), etc.
            std_name = song.name.lower()
            std_name = std_name.split('[')[0].split('(')[0].strip()
            songs_by_name[std_name].append(song)
    
    # Find duplicates and evaluate information completeness
    duplicates = []
    for name, songs in songs_by_name.items():
        if len(songs) > 1:
            # Only consider as duplicates if they're in the same primary category
            # (we expect some songs to exist in both Released and Unreleased if they're different versions)
            by_category = defaultdict(list)
            for song in songs:
                if hasattr(song, 'metadata') and song.metadata and song.metadata.sheet_tab:
                    category = song.metadata.sheet_tab.name
                    by_category[category].append(song)
            
            # Check each category for duplicates
            for category, category_songs in by_category.items():
                if len(category_songs) > 1:
                    duplicates.append((name, category, category_songs))
    
    return duplicates

def calculate_info_score(song):
    """Calculate an information score for a song based on completeness"""
    score = 0
    
    # Notes information
    if song.notes:
        score += len(song.notes) / 100  # Longer notes are more valuable
    
    # Links information
    if song.links:
        score += len(song.links) / 100
    
    # Primary link
    if song.primary_link:
        score += 2
    
    # Quality information
    if song.quality:
        score += 1
    
    # Type information
    if song.type:
        score += 1
    
    # Available length information
    if song.available_length:
        score += 1
    
    # Leak date information
    if song.leak_date:
        score += 1
    
    # File date information
    if song.file_date:
        score += 1
    
    # Era information
    if song.era:
        score += 1
    
    return score

def fix_info_duplicates(duplicates, auto_fix=False):
    """Resolve duplicate songs by keeping the most informative version"""
    fixed_count = 0
    
    for name, category, songs in duplicates:
        print(f"\nDuplicates for '{name}' in category '{category}':")
        
        # Calculate info score for each song
        songs_with_scores = []
        for song in songs:
            score = calculate_info_score(song)
            songs_with_scores.append((song, score))
            print(f"  ID: {song.id}, Name: {song.name}, Score: {score:.2f}")
            print(f"    Type: {song.type if song.type else 'None'}")
            print(f"    Era: {song.era if song.era else 'None'}")
            
            # Handle None values for notes
            if song.notes:
                notes_preview = song.notes[:100] + ('...' if len(song.notes) > 100 else '')
            else:
                notes_preview = 'None'
            print(f"    Notes: {notes_preview}")
            
            # Handle None values for links
            if song.links:
                links_preview = song.links[:100] + ('...' if len(song.links) > 100 else '')
            else:
                links_preview = 'None'
            print(f"    Links: {links_preview}")
        
        # Sort by info score (highest first)
        songs_with_scores.sort(key=lambda x: x[1], reverse=True)
        
        if auto_fix:
            # Keep the song with the highest score, delete the rest
            keep_song, keep_score = songs_with_scores[0]
            for song, score in songs_with_scores[1:]:
                print(f"  AUTO-DELETE: Removing duplicate ID: {song.id} (score: {score:.2f})")
                song.delete()
                fixed_count += 1
        else:
            # Ask the user what to do
            choice = input("Delete all duplicates except the highest scored one? (y/n/s to skip): ")
            if choice.lower() == 'y':
                keep_song, keep_score = songs_with_scores[0]
                print(f"  Keeping: ID: {keep_song.id}, Name: {keep_song.name} (score: {keep_score:.2f})")
                
                for song, score in songs_with_scores[1:]:
                    print(f"  Deleting: ID: {song.id}, Name: {song.name} (score: {score:.2f})")
                    song.delete()
                    fixed_count += 1
            elif choice.lower() == 's':
                print("  Skipping this set of duplicates")
                continue
    
    return fixed_count

def main():
    print("Searching for duplicate songs based on information completeness...")
    duplicates = find_info_duplicates()
    print(f"Found {len(duplicates)} duplicate sets with varying information")
    
    if duplicates:
        try:
            # In an interactive environment, ask for auto mode
            auto_mode = input("Do you want to use auto-fix mode? (y/n): ").lower() == 'y'
            fixed = fix_info_duplicates(duplicates, auto_fix=auto_mode)
        except (EOFError, KeyboardInterrupt):
            # In a non-interactive environment, use auto-fix
            print("Non-interactive environment detected, using auto-fix mode")
            fixed = fix_info_duplicates(duplicates, auto_fix=True)
        
        print(f"Fixed {fixed} information duplicate issues")

if __name__ == "__main__":
    main()