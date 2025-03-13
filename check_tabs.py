import os
import django
from collections import defaultdict
import argparse

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "carti_project.settings")
django.setup()

from django.db import models
from catalog.models import SheetTab, SongMetadata, CartiCatalog

def check_tab_stats():
    """Print statistics on sheet tab assignments"""
    print("===== SHEET TAB STATISTICS =====")
    
    # Check basic stats on current tab assignments
    tabs = SheetTab.objects.all().order_by('name')
    for tab in tabs:
        song_count = SongMetadata.objects.filter(sheet_tab=tab).count()
        print(f'{tab.name}: {song_count} songs')
    
    # Check songs without tab assignments
    total_songs = CartiCatalog.objects.count()
    assigned_songs = SongMetadata.objects.filter(sheet_tab__isnull=False).count()
    unassigned = total_songs - assigned_songs
    
    print(f'\nTotal songs: {total_songs}')
    print(f'Assigned songs: {assigned_songs}')
    print(f'Unassigned songs: {unassigned}')

def check_era_distribution():
    """Print distribution of songs by era"""
    print("\n===== ERA DISTRIBUTION =====")
    
    era_dict = defaultdict(int)
    for song in CartiCatalog.objects.all():
        era = song.era if song.era else "Unknown"
        era_dict[era] += 1
    
    print("\nSongs by era:")
    for era, count in sorted(era_dict.items()):
        print(f'{era}: {count} songs')

def check_subsection_distribution():
    """Print distribution of songs by subsection"""
    print("\n===== SUBSECTION DISTRIBUTION =====")
    
    subsection_dict = defaultdict(int)
    for metadata in SongMetadata.objects.filter(subsection__isnull=False):
        subsection_dict[metadata.subsection] += 1
    
    print("\nSongs by subsection:")
    for subsection, count in sorted(subsection_dict.items()):
        print(f'{subsection}: {count} songs')
    
    # Count songs without subsections
    no_subsection = SongMetadata.objects.filter(subsection__isnull=True).count()
    print(f'No subsection: {no_subsection} songs')

def check_sheet_id_assignment():
    """Check if SheetTab objects have sheet_id values"""
    print("\n===== SHEET ID ASSIGNMENT =====")
    
    tabs_with_id = SheetTab.objects.filter(sheet_id__isnull=False).count()
    tabs_without_id = SheetTab.objects.filter(sheet_id__isnull=True).count()
    
    print(f'Sheet tabs with ID: {tabs_with_id}')
    print(f'Sheet tabs without ID: {tabs_without_id}')
    
    if tabs_without_id > 0:
        print("\nTabs without sheet_id:")
        for tab in SheetTab.objects.filter(sheet_id__isnull=True):
            print(f'- {tab.name}')

def check_potential_issues():
    """Check for potential issues with tab assignments"""
    print("\n===== POTENTIAL TAB ASSIGNMENT ISSUES =====")
    
    # Check for released songs not in Released tab
    released_songs = CartiCatalog.objects.filter(
        models.Q(type__in=["Single", "Album Track", "Feature"]) |
        models.Q(era__in=["Playboi Carti", "Die Lit", "Whole Lotta Red [V4]"]) |
        models.Q(notes__icontains="Streaming")
    ).exclude(
        metadata__sheet_tab__name="Released"
    )
    
    print(f"Found {released_songs.count()} potential Released songs not in the Released tab:")
    for song in released_songs[:20]:  # Show first 20
        current_tab = song.metadata.sheet_tab.name if hasattr(song, 'metadata') and song.metadata and song.metadata.sheet_tab else "No tab"
        streaming = "(Streaming)" if song.notes and "Streaming" in song.notes else ""
        print(f"- {song.name} (Era: {song.era}, Type: {song.type}) {streaming} is in {current_tab}")
    
    if released_songs.count() > 20:
        print(f"... and {released_songs.count() - 20} more.")
        
    # Check specifically for Streaming songs not in Released tab
    streaming_songs = CartiCatalog.objects.filter(
        notes__icontains="Streaming"
    ).exclude(
        metadata__sheet_tab__name="Released"
    )
    
    print(f"\nFound {streaming_songs.count()} songs with Streaming category not in the Released tab:")
    for song in streaming_songs[:20]:  # Show first 20
        current_tab = song.metadata.sheet_tab.name if hasattr(song, 'metadata') and song.metadata and song.metadata.sheet_tab else "No tab"
        print(f"- {song.name} (Era: {song.era}, Type: {song.type}) is in {current_tab}")
    
    # Check for songs with emojis in wrong tabs
    print("\nSongs with emoji markers in wrong tabs:")
    emoji_tabs = {
        "🏆": "🏆 Grails",
        "🥇": "🥇 Wanted",
        "⭐": "⭐ Best Of",
        "✨": "✨ Special",
        "🗑️": "🗑️ Worst Of",
        "🤖": "🤖 AI Tracks",
    }
    
    for emoji, expected_tab in emoji_tabs.items():
        misplaced_songs = CartiCatalog.objects.filter(
            name__contains=emoji
        ).exclude(
            metadata__sheet_tab__name=expected_tab
        )
        
        if misplaced_songs.count() > 0:
            print(f"\n{emoji} ({expected_tab}): {misplaced_songs.count()} songs in wrong tabs")
            for song in misplaced_songs[:10]:
                current_tab = song.metadata.sheet_tab.name if hasattr(song, 'metadata') and song.metadata and song.metadata.sheet_tab else "No tab"
                print(f"- {song.name} is in {current_tab}")
            
            if misplaced_songs.count() > 10:
                print(f"... and {misplaced_songs.count() - 10} more.")

def list_songs_for_tab(tab_name, limit=50):
    """List songs for a specific tab"""
    tab = SheetTab.objects.filter(name=tab_name).first()
    if not tab:
        print(f"Tab '{tab_name}' not found.")
        return
    
    songs = CartiCatalog.objects.filter(metadata__sheet_tab=tab)
    print(f"\n===== SONGS IN TAB: {tab_name} ({songs.count()} total) =====")
    
    for i, song in enumerate(songs[:limit]):
        print(f"{i+1}. {song.name} (Era: {song.era}, Type: {song.type})")
    
    if songs.count() > limit:
        print(f"... and {songs.count() - limit} more.")

def bulk_move_songs(tab_name, criteria_field, criteria_value, dest_tab_name):
    """Bulk move songs matching criteria to another tab"""
    # Find the tabs
    source_tab = SheetTab.objects.filter(name=tab_name).first()
    dest_tab = SheetTab.objects.filter(name=dest_tab_name).first()
    
    if not source_tab:
        print(f"Source tab '{tab_name}' not found.")
        return
    
    if not dest_tab:
        print(f"Destination tab '{dest_tab_name}' not found.")
        return
    
    # Build filter
    filters = {'metadata__sheet_tab': source_tab}
    
    if criteria_field and criteria_value:
        if criteria_field == 'name':
            filters['name__icontains'] = criteria_value
        elif criteria_field == 'era':
            filters['era__icontains'] = criteria_value
        elif criteria_field == 'type':
            filters['type__icontains'] = criteria_value
        elif criteria_field == 'notes':
            filters['notes__icontains'] = criteria_value
    
    # Find matching songs
    songs = CartiCatalog.objects.filter(**filters)
    
    if songs.count() == 0:
        print(f"No songs found matching criteria: {criteria_field}='{criteria_value}' in tab '{tab_name}'")
        return
    
    # Confirm
    print(f"Found {songs.count()} songs matching criteria: {criteria_field}='{criteria_value}' in tab '{tab_name}'")
    for i, song in enumerate(songs[:10]):
        print(f"{i+1}. {song.name} (Era: {song.era}, Type: {song.type})")
    
    if songs.count() > 10:
        print(f"... and {songs.count() - 10} more.")
    
    confirm = input(f"Move these {songs.count()} songs to '{dest_tab_name}'? (y/n): ")
    
    if confirm.lower() != 'y':
        print("Operation cancelled")
        return
    
    # Move songs
    moved = 0
    for song in songs:
        if hasattr(song, 'metadata') and song.metadata:
            song.metadata.sheet_tab = dest_tab
            song.metadata.save()
            moved += 1
    
    print(f"Moved {moved} songs from '{tab_name}' to '{dest_tab_name}'")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Check and fix tab assignments.')
    parser.add_argument('--stats', action='store_true', help='Show basic tab statistics')
    parser.add_argument('--eras', action='store_true', help='Show era distribution')
    parser.add_argument('--subsections', action='store_true', help='Show subsection distribution')
    parser.add_argument('--sheet-ids', action='store_true', help='Check sheet ID assignments')
    parser.add_argument('--issues', action='store_true', help='Check for potential tab assignment issues')
    parser.add_argument('--list-tab', type=str, help='List songs for a specific tab')
    parser.add_argument('--move-songs', nargs=4, metavar=('SOURCE_TAB', 'CRITERIA_FIELD', 'CRITERIA_VALUE', 'DEST_TAB'), 
                        help='Move songs matching criteria from one tab to another')
    
    args = parser.parse_args()
    
    # If no args, show everything
    if not any(vars(args).values()):
        check_tab_stats()
        check_era_distribution()
        check_subsection_distribution()
        check_sheet_id_assignment()
        check_potential_issues()
    else:
        if args.stats:
            check_tab_stats()
        if args.eras:
            check_era_distribution()
        if args.subsections:
            check_subsection_distribution()
        if args.sheet_ids:
            check_sheet_id_assignment()
        if args.issues:
            check_potential_issues()
        if args.list_tab:
            list_songs_for_tab(args.list_tab)
        if args.move_songs:
            source_tab, criteria_field, criteria_value, dest_tab = args.move_songs
            bulk_move_songs(source_tab, criteria_field, criteria_value, dest_tab)