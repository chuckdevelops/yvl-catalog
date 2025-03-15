from django.core.management.base import BaseCommand
from catalog.models import CartiCatalog, SongMetadata
from django.db import transaction

class Command(BaseCommand):
    help = 'Update subsection of I AM MUSIC [V1] songs'

    def handle(self, *args, **options):
        try:
            with transaction.atomic():
                # Get all songs with era "I AM MUSIC [V1]"
                songs = CartiCatalog.objects.filter(era="I AM MUSIC [V1]")
                count = songs.count()
                
                if count == 0:
                    self.stdout.write(self.style.WARNING("No songs found with era 'I AM MUSIC [V1]'"))
                    return
                
                # Update metadata subsection for these songs
                updated = 0
                
                for song in songs:
                    try:
                        metadata, created = SongMetadata.objects.get_or_create(song=song)
                        if metadata.subsection != "I AM MUSIC [V1]":
                            old_subsection = metadata.subsection
                            metadata.subsection = "I AM MUSIC [V1]"
                            metadata.save()
                            updated += 1
                            self.stdout.write(f"Updated subsection for {song.name}: {old_subsection} -> I AM MUSIC [V1]")
                    except Exception as e:
                        self.stdout.write(f"Error updating metadata for song: {song.name}: {e}")
                
                self.stdout.write(self.style.SUCCESS(f"Successfully updated {updated} songs with subsection 'I AM MUSIC [V1]'"))
        
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error: {e}"))