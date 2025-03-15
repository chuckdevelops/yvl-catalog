from django.core.management.base import BaseCommand
from catalog.models import CartiCatalog
from django.db import transaction

class Command(BaseCommand):
    help = 'Update Whole Lotta Red era songs with type "Streaming" to use era "Whole Lotta Red [V4]"'

    def handle(self, *args, **options):
        with transaction.atomic():
            # Find all songs from WLR era with type "Streaming" or "Yes"
            wlr_songs = CartiCatalog.objects.filter(
                era="Whole Lotta Red",
                type__in=["Streaming", "Yes"]
            )
            
            count = wlr_songs.count()
            self.stdout.write(f"Found {count} Whole Lotta Red songs with type Streaming/Yes")
            
            # Update the era field to include [V4]
            updated = wlr_songs.update(era="Whole Lotta Red [V4]")
            
            self.stdout.write(self.style.SUCCESS(f"Successfully updated {updated} songs to era 'Whole Lotta Red [V4]'"))