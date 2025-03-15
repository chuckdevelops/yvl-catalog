from django.core.management.base import BaseCommand
from catalog.models import SheetTab, SongMetadata, CartiCatalog
from django.db.models import Q

class Command(BaseCommand):
    help = 'Check Released tab songs and filtering'

    def handle(self, *args, **options):
        # Find Released tab
        released_tab = SheetTab.objects.filter(name='Released').first()
        if not released_tab:
            self.stdout.write(self.style.ERROR("Released tab not found!"))
            return
            
        # Get all songs in Released tab
        metadata_entries = SongMetadata.objects.filter(sheet_tab=released_tab).select_related('song')
        
        # Get the total count
        total_count = metadata_entries.count()
        self.stdout.write(f"Total songs in Released tab: {total_count}")
        
        # Check songs by era
        self.stdout.write("\nSongs by era:")
        era_counts = {}
        for meta in metadata_entries:
            era = meta.song.era
            if era not in era_counts:
                era_counts[era] = 0
            era_counts[era] += 1
        
        for era, count in sorted(era_counts.items(), key=lambda x: x[1], reverse=True):
            self.stdout.write(f"- {era}: {count} songs")
            
        # Check songs by type
        self.stdout.write("\nSongs by type:")
        type_counts = {}
        for meta in metadata_entries:
            song_type = meta.song.type
            if song_type not in type_counts:
                type_counts[song_type] = 0
            type_counts[song_type] += 1
        
        for song_type, count in sorted(type_counts.items(), key=lambda x: x[1], reverse=True):
            self.stdout.write(f"- {song_type}: {count} songs")
            
        # Test the filter query
        self.stdout.write("\nTesting Released tab + Playboi Carti era filtering:")
        playboi_carti_era = "Playboi Carti"
        
        # This simulates the filter in views.py
        filtered_songs = CartiCatalog.objects.filter(
            metadata__sheet_tab=released_tab,
            era=playboi_carti_era
        )
        filtered_count = filtered_songs.count()
        
        self.stdout.write(f"Songs in Released tab with era '{playboi_carti_era}': {filtered_count}")
        
        if filtered_count == 0:
            self.stdout.write("\nChecking if any Playboi Carti era songs exist at all:")
            all_pc_songs = CartiCatalog.objects.filter(era=playboi_carti_era).count()
            self.stdout.write(f"Total Playboi Carti era songs in database: {all_pc_songs}")
            
            # Check if any of these have metadata
            pc_with_metadata = CartiCatalog.objects.filter(
                era=playboi_carti_era,
                metadata__isnull=False
            ).count()
            self.stdout.write(f"Playboi Carti era songs with metadata: {pc_with_metadata}")
            
            # Check if any of these should be in Released tab
            pc_for_release = CartiCatalog.objects.filter(
                era=playboi_carti_era,
                type='Streaming'
            ).count()
            self.stdout.write(f"Playboi Carti era songs with 'Streaming' type: {pc_for_release}")
            
            # List some examples
            self.stdout.write("\nSample Playboi Carti era songs that should be in Released tab:")
            samples = CartiCatalog.objects.filter(
                era=playboi_carti_era,
                type='Streaming'
            )[:5]
            
            for song in samples:
                # Check if there's metadata
                try:
                    meta = SongMetadata.objects.get(song=song)
                    tab_name = meta.sheet_tab.name if meta.sheet_tab else "No tab"
                except SongMetadata.DoesNotExist:
                    tab_name = "No metadata"
                    
                self.stdout.write(f"- ID: {song.id}, Name: {song.name}, Type: {song.type}, Tab: {tab_name}")