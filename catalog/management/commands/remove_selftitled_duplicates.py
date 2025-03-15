from django.core.management.base import BaseCommand
from catalog.models import CartiCatalog, SongMetadata
from django.db import transaction

class Command(BaseCommand):
    help = 'Remove Self-Titled duplicate songs that also exist in Playboi Carti era'

    def handle(self, *args, **options):
        # List of duplicate songs found (Self-Titled era duplicates that need to be deleted)
        duplicates_to_delete = [
            68307,  # NO.9 (prod. JStewOnTheBeat)
            68308,  # dothatshit! (prod. Pi'erre Bourne)
            68311,  # ⭐ Flex (feat. Leven Kali) (prod. KasimGotJuice & J. Cash Beatz)
            68313,  # ⭐ Had 2 (prod. MexikoDro)
            68312,  # ⭐ Kelly K (prod. Southside & Jake One)
            68303,  # ⭐ Let It Go (prod. Pi'erre Bourne)
            68299,  # ⭐ Location (prod. Harry Fraud)
            68300,  # ⭐ Magnolia (prod. Pi'erre Bourne)
            68305,  # ⭐ New Choppa (feat. A$AP Rocky) (prod. Ricci Riera)
            68310,  # ⭐ Yah Mean (prod. Pi'erre Bourne)
            68302   # ⭐ wokeuplikethis* (feat. Lil Uzi Vert) (prod. Pi'erre Bourne)
        ]
        
        with transaction.atomic():
            # Display what we're going to delete
            self.stdout.write("The following Self-Titled era songs will be deleted (duplicates of Playboi Carti era):")
            for song_id in duplicates_to_delete:
                try:
                    song = CartiCatalog.objects.get(id=song_id)
                    self.stdout.write(f"- ID: {song.id}, Name: {song.name}, Era: {song.era}")
                except CartiCatalog.DoesNotExist:
                    self.stdout.write(f"Song with ID {song_id} not found")
            
            # Get confirmation (not actually needed in script, but useful for logging)
            self.stdout.write(f"Deleting {len(duplicates_to_delete)} duplicate songs...")
            
            # Delete the duplicates
            deleted_count = CartiCatalog.objects.filter(id__in=duplicates_to_delete).delete()
            
            self.stdout.write(self.style.SUCCESS(f"Successfully deleted {deleted_count[0]} songs and related objects"))