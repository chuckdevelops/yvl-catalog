from django.core.management.base import BaseCommand
from catalog.models import CartiCatalog, SheetTab, SongCategory
from django.db import transaction

class Command(BaseCommand):
    help = 'Update homepage Recent Songs section with the top 10 Released songs'

    def handle(self, *args, **options):
        # Get the Recent tab
        recent_tab = SheetTab.objects.filter(name='Recent').first()
        if not recent_tab:
            self.stdout.write(self.style.ERROR('Recent tab not found in the database'))
            return
            
        # Get the Released tab
        released_tab = SheetTab.objects.filter(name='Released').first()
        if not released_tab:
            self.stdout.write(self.style.ERROR('Released tab not found in the database'))
            return
            
        # Find top 10 Released songs (ordered by ID, newest first)
        released_songs = CartiCatalog.objects.filter(
            metadata__sheet_tab=released_tab
        ).order_by('-id')[:10]
        
        self.stdout.write(f'Found {released_songs.count()} recent Released songs')
        
        # List the songs we'll use for the homepage
        self.stdout.write('\nSongs to add to homepage Recent section:')
        for i, song in enumerate(released_songs, 1):
            self.stdout.write(f'{i}. {song.name} (ID: {song.id}, Era: {song.era})')
            
        # Update the Recent tab 
        with transaction.atomic():
            # Clear existing songs from Recent tab
            SongCategory.objects.filter(sheet_tab=recent_tab).delete()
            self.stdout.write('Cleared existing songs from Recent tab')
            
            # Add top Released songs to Recent tab
            for i, song in enumerate(released_songs, 1):
                SongCategory.objects.create(
                    song=song,
                    sheet_tab=recent_tab
                )
                self.stdout.write(f'Added {song.name} to Recent tab (position {i})')
                
        self.stdout.write(self.style.SUCCESS(f'\nSuccessfully updated homepage Recent section with {released_songs.count()} Released songs'))