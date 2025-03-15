from django.core.management.base import BaseCommand
from catalog.models import CartiCatalog
from django.db import transaction

class Command(BaseCommand):
    help = 'Remove the "MUSIC [V2]" prefix from I AM MUSIC [V2] songs'

    def handle(self, *args, **options):
        try:
            with transaction.atomic():
                # Get all songs from the I AM MUSIC [V2] era that have the prefix
                songs = CartiCatalog.objects.filter(
                    era="I AM MUSIC [V2]",
                    name__startswith="MUSIC [V2]"
                )
                count = songs.count()
                
                if count == 0:
                    self.stdout.write(self.style.WARNING("No songs found with prefix 'MUSIC [V2]'"))
                    return
                
                # Update each song to remove the prefix
                for song in songs:
                    old_name = song.name
                    # Remove "MUSIC [V2]<tab>" from the beginning of the name
                    new_name = song.name.replace("MUSIC [V2]\t", "", 1)
                    
                    song.name = new_name
                    song.save()
                    
                    self.stdout.write(f"Updated: {old_name} -> {new_name}")
                
                self.stdout.write(self.style.SUCCESS(f"Successfully updated {count} song names"))
        
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error: {e}"))