from django.core.management.base import BaseCommand
from catalog.models import SheetTab, SongMetadata

class Command(BaseCommand):
    help = 'Checks the distribution of songs in the Stems tab by era'

    def handle(self, *args, **options):
        # Get the Stems tab
        stems_tab = SheetTab.objects.filter(name='Stems').first()
        if not stems_tab:
            self.stderr.write(self.style.ERROR('Stems tab not found!'))
            return
            
        self.stdout.write(f'Checking songs in Stems tab (ID: {stems_tab.id})')
        
        # Get all metadata entries associated with the Stems tab
        stems_metadata = SongMetadata.objects.filter(sheet_tab=stems_tab).select_related('song')
        
        # Count by era
        era_counts = {}
        for metadata in stems_metadata:
            era = metadata.song.era
            if era not in era_counts:
                era_counts[era] = []
            era_counts[era].append(metadata.song.name)
        
        # Print the counts
        self.stdout.write(f'Found songs in {len(era_counts)} different eras:')
        for era, songs in sorted(era_counts.items()):
            self.stdout.write(f'\n{era} ({len(songs)} songs):')
            for song in songs:
                self.stdout.write(f'  - {song}')