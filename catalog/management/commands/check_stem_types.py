from django.core.management.base import BaseCommand
from catalog.models import CartiCatalog, SongMetadata

class Command(BaseCommand):
    help = 'Check songs with specific type values and their tab assignments'

    def handle(self, *args, **options):
        # Types to check
        types_to_check = ['5.1 Stems', 'Acapella']
        
        for check_type in types_to_check:
            songs = CartiCatalog.objects.filter(type=check_type)
            self.stdout.write(f"\nSongs with type '{check_type}': {songs.count()}")
            
            for song in songs:
                try:
                    # Get primary metadata
                    meta = SongMetadata.objects.filter(song=song).first()
                    primary_tab = meta.sheet_tab.name if meta and meta.sheet_tab else "No primary tab"
                    
                    # Get secondary tabs
                    secondary_tabs = [c.sheet_tab.name for c in song.categories.all()] if hasattr(song, 'categories') else []
                    tabs_str = ", ".join(secondary_tabs) if secondary_tabs else "No secondary tabs"
                    
                    self.stdout.write(f"- ID: {song.id}, Name: {song.name}")
                    self.stdout.write(f"  Era: {song.era}, Primary Tab: {primary_tab}")
                    self.stdout.write(f"  Secondary Tabs: {tabs_str}")
                    
                except Exception as e:
                    self.stdout.write(f"Error processing song ID {song.id}: {str(e)}")