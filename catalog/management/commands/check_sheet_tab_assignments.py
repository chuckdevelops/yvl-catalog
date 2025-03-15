from django.core.management.base import BaseCommand
from catalog.models import SheetTab, SongMetadata, SongCategory

class Command(BaseCommand):
    help = 'Check sheet tab assignments for all tabs'

    def handle(self, *args, **options):
        # Get all sheet tabs
        sheet_tabs = SheetTab.objects.all()
        
        self.stdout.write("Sheet tab assignments:")
        for tab in sheet_tabs:
            # Count primary assignments (SongMetadata)
            primary_count = SongMetadata.objects.filter(sheet_tab=tab).count()
            
            # Count secondary assignments (SongCategory)
            secondary_count = SongCategory.objects.filter(sheet_tab=tab).count()
            
            self.stdout.write(f"Tab: {tab.name}")
            self.stdout.write(f"  - ID: {tab.id}")
            self.stdout.write(f"  - Primary song assignments: {primary_count}")
            self.stdout.write(f"  - Secondary song assignments: {secondary_count}")
            
        # Specifically check for Released tab
        released_tab = SheetTab.objects.filter(name='Released').first()
        if released_tab:
            # Get sample songs
            self.stdout.write("\nSample songs from Released tab (primary assignment):")
            primary_songs = SongMetadata.objects.filter(sheet_tab=released_tab).select_related('song')[:5]
            for meta in primary_songs:
                song = meta.song
                self.stdout.write(f"- ID: {song.id}, Name: {song.name}, Era: {song.era}, Type: {song.type}")
                
            # Check if there are any songs with metadata but no sheet_tab
            missing_tab = SongMetadata.objects.filter(sheet_tab__isnull=True).count()
            if missing_tab > 0:
                self.stdout.write(f"\nFound {missing_tab} songs with metadata but no sheet tab assigned!")
                
            # Check for songs with no metadata at all
            from catalog.models import CartiCatalog
            no_metadata = CartiCatalog.objects.filter(metadata__isnull=True).count()
            if no_metadata > 0:
                self.stdout.write(f"Found {no_metadata} songs with no metadata at all!")