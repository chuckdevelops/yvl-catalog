from django.core.management.base import BaseCommand
from catalog.models import SheetTab, SongMetadata, SongCategory, CartiCatalog

class Command(BaseCommand):
    help = 'Check the Recent tab and its songs'

    def handle(self, *args, **options):
        # Check if the Recent tab exists
        recent_tab = SheetTab.objects.filter(name='Recent').first()
        if not recent_tab:
            self.stdout.write(self.style.ERROR('Recent tab does not exist!'))
            return
        
        self.stdout.write(f'Recent tab exists with ID: {recent_tab.id}')
        
        # Check primary assignments (in SongMetadata)
        primary_count = SongMetadata.objects.filter(sheet_tab=recent_tab).count()
        self.stdout.write(f'Primary assignments (in SongMetadata): {primary_count}')
        
        # Check secondary assignments (in SongCategory)
        secondary_count = SongCategory.objects.filter(sheet_tab=recent_tab).count()
        self.stdout.write(f'Secondary assignments (in SongCategory): {secondary_count}')
        
        # Check how the Recent tab is being populated in views.py
        self.stdout.write('\nInvestigating how Recent tab is populated:')
        
        # Look at the index view which uses Recent tab
        self.stdout.write('Check for songs with Recent category:')
        songs_with_recent_category = CartiCatalog.objects.filter(categories__sheet_tab=recent_tab).count()
        self.stdout.write(f'- Songs with Recent as secondary category: {songs_with_recent_category}')
        
        # Check if there are any songs that should be in Recent
        self.stdout.write('\nSample songs that might belong in Recent:')
        recent_songs = CartiCatalog.objects.order_by('-id')[:5]
        
        for song in recent_songs:
            self.stdout.write(f'ID: {song.id}, Name: {song.name}, Era: {song.era}')
            
            # Check if this song has Recent as a category
            is_in_recent = SongCategory.objects.filter(song=song, sheet_tab=recent_tab).exists()
            self.stdout.write(f'- In Recent tab: {is_in_recent}')
            
            # Check when this was added
            try:
                self.stdout.write(f'- Scraped at: {song.scraped_at}')
            except:
                self.stdout.write('- Scraped at: None')
                
        # Check the sort_recent_tab command
        self.stdout.write('\nLooking for sort_recent_tab command:')
        try:
            from django.core.management import get_commands
            commands = get_commands()
            if 'sort_recent_tab' in commands:
                self.stdout.write('- sort_recent_tab command exists')
            else:
                self.stdout.write('- sort_recent_tab command not found')
                
            if 'sort_recent_tab_2025' in commands:
                self.stdout.write('- sort_recent_tab_2025 command exists')
            else:
                self.stdout.write('- sort_recent_tab_2025 command not found')
        except Exception as e:
            self.stdout.write(f'Error checking commands: {str(e)}')