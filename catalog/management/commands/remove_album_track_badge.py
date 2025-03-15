from django.core.management.base import BaseCommand
from catalog.models import CartiCatalog
from django.db import transaction

class Command(BaseCommand):
    help = 'Remove the Album Track badge from song with ID 8531'

    def handle(self, *args, **options):
        song_id = 8531
        
        try:
            with transaction.atomic():
                # Get the song
                song = CartiCatalog.objects.get(id=song_id)
                
                # Get original values before changes
                old_file_date = song.file_date
                
                self.stdout.write(f"Found song: {song.name} (ID: {song.id})")
                self.stdout.write(f"Current file_date: {old_file_date}")
                
                # Clear the file_date field (removing the Album Track badge)
                song.file_date = None
                song.save()
                
                self.stdout.write(self.style.SUCCESS(
                    f"Successfully removed 'Album Track' badge from {song.name}"
                ))
                self.stdout.write(f"New file_date: {song.file_date}")
                
        except CartiCatalog.DoesNotExist:
            self.stdout.write(self.style.ERROR(f"Song with ID {song_id} not found"))