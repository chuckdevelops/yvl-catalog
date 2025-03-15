from django.core.management.base import BaseCommand
from catalog.models import CartiCatalog, SongMetadata, SheetTab
from django.db import transaction
from collections import defaultdict

class Command(BaseCommand):
    help = 'Find duplicate songs using broader criteria'

    def handle(self, *args, **options):
        # Find all sheet tabs
        self.stdout.write("Available sheet tabs:")
        sheet_tabs = SheetTab.objects.all().values_list('name', flat=True)
        for tab in sheet_tabs:
            self.stdout.write(f"- {tab}")
        
        # Look for duplicates based on name only in the full database
        all_songs = CartiCatalog.objects.all()
        songs_by_name = defaultdict(list)
        
        for song in all_songs:
            songs_by_name[song.name].append(song.id)
        
        # Find duplicates (songs with same name but multiple entries)
        duplicates = {name: ids for name, ids in songs_by_name.items() if len(ids) > 1}
        
        if not duplicates:
            self.stdout.write(self.style.SUCCESS('No duplicates found by name'))
            return
        
        # Look specifically at duplicates on pages 4-5 of Playboi Carti
        self.stdout.write(f'Found {len(duplicates)} song names with duplicates in the entire database')
        
        # Now get details about the duplicates to find the ones on pages 4-5
        for name, ids in duplicates.items():
            songs = CartiCatalog.objects.filter(id__in=ids)
            # Only show duplicates from Playboi Carti era
            if any(song.era == 'Playboi Carti' for song in songs):
                self.stdout.write(f'\nDuplicates for: {name}')
                for song in songs:
                    # Get the metadata to find the sheet tab
                    try:
                        meta = SongMetadata.objects.get(song=song)
                        sheet_tab = meta.sheet_tab.name if meta.sheet_tab else "No tab"
                    except SongMetadata.DoesNotExist:
                        sheet_tab = "No metadata"
                    except SongMetadata.MultipleObjectsReturned:
                        sheet_tab = "Multiple tabs"
                        
                    self.stdout.write(f'ID: {song.id}, Era: {song.era}, Type: {song.type}, Tab: {sheet_tab}, File Date: {song.file_date}')