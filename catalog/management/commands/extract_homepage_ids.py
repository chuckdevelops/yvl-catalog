from django.core.management.base import BaseCommand
from catalog.models import CartiCatalog, SheetTab, SongMetadata
from django.db.models import Q

class Command(BaseCommand):
    help = 'Extract IDs for recent released songs to display on homepage'

    def handle(self, *args, **options):
        # Get the Released tab
        released_tab = SheetTab.objects.filter(name='Released').first()
        if not released_tab:
            self.stdout.write(self.style.ERROR('Released tab not found in the database'))
            return
        
        # Find recent Released songs with Album Track badge and Streaming type
        recent_released_songs = CartiCatalog.objects.filter(
            metadata__sheet_tab=released_tab,
            type='Streaming',
            file_date='Album Track'
        ).order_by('-id')[:10]
        
        # Print the songs for verification
        self.stdout.write('Recent Released songs for homepage:')
        for i, song in enumerate(recent_released_songs, 1):
            self.stdout.write(f'{i}. {song.name} (ID: {song.id}, Era: {song.era})')
        
        # Extract IDs for use in code
        song_ids = [song.id for song in recent_released_songs]
        id_str = ', '.join(str(id) for id in song_ids)
        
        self.stdout.write('\nIDs to use in views.py:')
        self.stdout.write(f'recent_song_ids = [{id_str}]')
        
        # Print Python code to update views.py
        self.stdout.write('\nPython code snippet to update views.py:')
        self.stdout.write('''
# Replace the Recent tab section in index view with this:
# Get recent Released songs for homepage
recent_song_ids = [{}]
recent_songs = []

# Get each song by ID in the order specified
for song_id in recent_song_ids:
    try:
        song = CartiCatalog.objects.select_related('metadata__sheet_tab').prefetch_related('categories__sheet_tab').get(id=song_id)
        recent_songs.append(song)
    except CartiCatalog.DoesNotExist:
        continue
        
# If we couldn't find the songs by ID, fall back to query by release date
if not recent_songs:
    # Fall back to recent songs by ID
    recent_songs = CartiCatalog.objects.select_related('metadata__sheet_tab').prefetch_related('categories__sheet_tab').all().order_by('-id')[:10]
'''.format(id_str))