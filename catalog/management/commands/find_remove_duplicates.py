from django.core.management.base import BaseCommand
from catalog.models import CartiCatalog, SongMetadata
from django.db import transaction
from collections import defaultdict

class Command(BaseCommand):
    help = 'Find and remove duplicate songs in Playboi Carti era with Released sheet tab and Streaming type'

    def handle(self, *args, **options):
        # Find all songs from Playboi Carti era with Streaming type
        playboi_carti_streaming = CartiCatalog.objects.filter(
            era='Playboi Carti', 
            type='Streaming'
        )
        
        # Get metadata for these songs with "Released" sheet tab
        metadata = SongMetadata.objects.filter(
            song__in=playboi_carti_streaming, 
            sheet_tab__name='Released'
        ).select_related('song')
        
        # Group songs by name to find duplicates
        songs_by_name = defaultdict(list)
        for meta in metadata:
            songs_by_name[meta.song.name].append(meta.song.id)
        
        # Find duplicates (songs with same name but multiple entries)
        duplicates = {name: ids for name, ids in songs_by_name.items() if len(ids) > 1}
        
        if not duplicates:
            self.stdout.write(self.style.SUCCESS(f'No duplicates found'))
            return
            
        self.stdout.write(f'Found {len(duplicates)} song names with duplicates:')
        for name, ids in duplicates.items():
            self.stdout.write(f'{name}: {ids}')
            
        # For each duplicate, keep the first one and delete the rest
        with transaction.atomic():
            deleted_count = 0
            for name, ids in duplicates.items():
                # Keep the first ID, delete the rest
                keep_id = ids[0]
                delete_ids = ids[1:]
                
                # Display which one we're keeping
                keep_song = CartiCatalog.objects.get(id=keep_id)
                self.stdout.write(f'Keeping: ID {keep_id} - {keep_song.name} - {keep_song.file_date}')
                
                # Show what we're deleting
                for del_id in delete_ids:
                    del_song = CartiCatalog.objects.get(id=del_id)
                    self.stdout.write(f'Deleting: ID {del_id} - {del_song.name} - {del_song.file_date}')
                    
                # Delete the duplicates
                deleted_items = CartiCatalog.objects.filter(id__in=delete_ids).delete()
                deleted_count += len(delete_ids)
            
            self.stdout.write(self.style.SUCCESS(f'Successfully deleted {deleted_count} duplicate songs'))