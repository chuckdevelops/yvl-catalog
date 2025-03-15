from django.core.management.base import BaseCommand
from catalog.models import CartiCatalog, SongMetadata
from django.db import transaction

class Command(BaseCommand):
    help = 'Fix the subsection name for I AM MUSIC [V2] songs'

    def handle(self, *args, **options):
        try:
            with transaction.atomic():
                # Get all songs with era "I AM MUSIC [V2]"
                songs = CartiCatalog.objects.filter(era="I AM MUSIC [V2]")
                count = songs.count()
                
                if count == 0:
                    self.stdout.write(self.style.WARNING("No songs found with era 'I AM MUSIC [V2]'"))
                    return
                
                # Update all these songs' metadata to have the correct subsection "I AM MUSIC [V2]"
                updated = 0
                for song in songs:
                    try:
                        metadata = SongMetadata.objects.get(song=song)
                        if metadata.subsection == "I AM MUSIC":
                            metadata.subsection = "I AM MUSIC [V2]"
                            metadata.save()
                            updated += 1
                    except SongMetadata.DoesNotExist:
                        self.stdout.write(f"No metadata found for song: {song.name}")
                
                self.stdout.write(self.style.SUCCESS(f"Successfully updated {updated} songs to have subsection 'I AM MUSIC [V2]'"))
        
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error: {e}"))