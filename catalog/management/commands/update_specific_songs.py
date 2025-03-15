from django.core.management.base import BaseCommand
from catalog.models import CartiCatalog
from django.db import transaction


class Command(BaseCommand):
    help = 'Removes Album Track badge from specific songs and updates their type to OG Files'

    def handle(self, *args, **options):
        # List of song IDs to update
        song_ids = [592, 589, 573, 513, 593, 579, 547, 513]
        
        # Remove duplicates
        song_ids = list(set(song_ids))
        
        with transaction.atomic():
            updated_count = 0
            
            for song_id in song_ids:
                try:
                    song = CartiCatalog.objects.get(id=song_id)
                    
                    # Store original values for logging
                    old_file_date = song.file_date
                    old_type = song.type
                    
                    # Update file_date (remove Album Track badge)
                    if song.file_date == "Album Track":
                        song.file_date = ""
                    
                    # Update type to OG Files
                    song.type = "OG Files"
                    
                    # Save changes
                    song.save()
                    
                    # Log the changes
                    self.stdout.write(self.style.SUCCESS(
                        f"Updated song {song_id} ({song.name}): "
                        f"file_date: {old_file_date or '(empty)'} -> {song.file_date or '(empty)'}, "
                        f"type: {old_type or '(empty)'} -> {song.type}"
                    ))
                    
                    updated_count += 1
                    
                except CartiCatalog.DoesNotExist:
                    self.stdout.write(self.style.ERROR(f"Song with ID {song_id} not found"))
            
            self.stdout.write(self.style.SUCCESS(f"Updated {updated_count} songs"))