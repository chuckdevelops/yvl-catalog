import os
import django
from collections import defaultdict

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "carti_project.settings")
django.setup()

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

if __name__ == "__main__":
    check_tab_stats()
    check_era_distribution()
    check_subsection_distribution()
    check_sheet_id_assignment()