from django.core.management.base import BaseCommand
from catalog.models import CartiCatalog
from django.db import transaction

class Command(BaseCommand):
    help = 'Fix the era name for I AM MUSIC [V2] songs'

    def handle(self, *args, **options):
        try:
            with transaction.atomic():
                # Get all songs with era "I AM MUSIC"
                songs = CartiCatalog.objects.filter(era="I AM MUSIC")
                count = songs.count()
                
                if count == 0:
                    self.stdout.write(self.style.WARNING("No songs found with era 'I AM MUSIC'"))
                    return
                
                # Update all these songs to have the correct era "I AM MUSIC [V2]"
                songs.update(era="I AM MUSIC [V2]")
                
                self.stdout.write(self.style.SUCCESS(f"Successfully updated {count} songs to era 'I AM MUSIC [V2]'"))
        
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error: {e}"))