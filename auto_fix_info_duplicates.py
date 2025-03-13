#!/usr/bin/env python3
"""
Script to automatically fix duplicate songs by keeping the version with most information.
"""

import os
import django
from collections import defaultdict

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'carti_project.settings')
django.setup()

# Import models
from catalog.models import CartiCatalog, SheetTab, SongMetadata

def clean_duplicates():
    """Find and clean up duplicate songs within the same category"""
    print("Finding and cleaning duplicate songs...")
    
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
    
    fixed_count = 0
    
    # Process each group
    for name, songs in songs_by_name.items():
        if len(songs) <= 1:
            continue  # Skip if no duplicates
            
        # Group by primary category
        by_category = defaultdict(list)
        for song in songs:
            tab = "Unknown"
            if hasattr(song, 'metadata') and song.metadata and song.metadata.sheet_tab:
                tab = song.metadata.sheet_tab.name
            by_category[tab].append(song)
        
        # Process each category's duplicates
        for category, category_songs in by_category.items():
            if len(category_songs) <= 1:
                continue  # Skip if no duplicates in this category
                
            print(f"\nDuplicates for '{name}' in category '{category}':")
            
            # Calculate information scores
            songs_with_scores = []
            for song in category_songs:
                # Calculate info score based on field completeness
                score = 0
                
                # Notes
                if song.notes:
                    score += len(song.notes) / 100
                
                # Links
                if song.links:
                    score += len(song.links) / 100
                
                # Primary link
                if song.primary_link:
                    score += 2
                
                # Other fields
                if song.quality: score += 1
                if song.type: score += 1
                if song.available_length: score += 1
                if song.leak_date: score += 1
                if song.file_date: score += 1
                if song.era: score += 1
                
                songs_with_scores.append((song, score))
                print(f"  ID: {song.id}, Name: {song.name}, Score: {score:.2f}")
                print(f"    Type: {song.type if song.type else 'None'}")
                print(f"    Era: {song.era if song.era else 'None'}")
                
                # Notes preview
                if song.notes:
                    notes_preview = song.notes[:100] + ('...' if len(song.notes) > 100 else '')
                else:
                    notes_preview = 'None'
                print(f"    Notes: {notes_preview}")
                
                # Links preview
                if song.links:
                    links_preview = song.links[:100] + ('...' if len(song.links) > 100 else '')
                else:
                    links_preview = 'None'
                print(f"    Links: {links_preview}")
            
            # Sort by score (highest first)
            songs_with_scores.sort(key=lambda x: x[1], reverse=True)
            
            # Keep the highest scored song, delete the rest
            keep_song, keep_score = songs_with_scores[0]
            print(f"  KEEPING: ID: {keep_song.id}, Name: {keep_song.name} (score: {keep_score:.2f})")
            
            for song, score in songs_with_scores[1:]:
                print(f"  DELETING: ID: {song.id}, Name: {song.name} (score: {score:.2f})")
                song.delete()
                fixed_count += 1
    
    return fixed_count

if __name__ == "__main__":
    fixed = clean_duplicates()
    print(f"\nRemoved {fixed} duplicate songs")