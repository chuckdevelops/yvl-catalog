from django.core.management.base import BaseCommand
from catalog.models import CartiCatalog, SongMetadata
from django.db import transaction

class Command(BaseCommand):
    help = 'Fix remaining I AM MUSIC [V2] songs with no subsection'

    def handle(self, *args, **options):
        try:
            with transaction.atomic():
                # Get all songs that need subsection updated
                songs = CartiCatalog.objects.filter(era="I AM MUSIC [V2]").select_related('metadata')
                count = 0
                
                for song in songs:
                    try:
                        metadata, created = SongMetadata.objects.get_or_create(song=song)
                        if not metadata.subsection:
                            metadata.subsection = "I AM MUSIC [V2]"
                            metadata.save()
                            count += 1
                            self.stdout.write(f"Updated subsection for {song.name}: None -> I AM MUSIC [V2]")
                    except Exception as e:
                        self.stdout.write(f"Error updating metadata for song: {song.name}: {e}")
                
                self.stdout.write(self.style.SUCCESS(f"Successfully updated {count} songs with missing subsections"))
        
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error: {e}"))