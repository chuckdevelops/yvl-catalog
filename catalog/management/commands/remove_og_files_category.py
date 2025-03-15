from django.core.management.base import BaseCommand
from catalog.models import CartiCatalog, SongCategory, SheetTab
from django.db import transaction

class Command(BaseCommand):
    help = 'Remove the OG Files category from song ID 574'

    def handle(self, *args, **options):
        song_id = 574
        category_name = "OG Files"
        
        try:
            # Get the song
            song = CartiCatalog.objects.get(id=song_id)
            self.stdout.write(f"Found song: {song.name} (ID: {song.id})")
            
            # Get the OG Files sheet tab
            og_files_tab = SheetTab.objects.get(name=category_name)
            
            with transaction.atomic():
                # Find and delete the category assignment
                deleted_count = SongCategory.objects.filter(
                    song=song,
                    sheet_tab=og_files_tab
                ).delete()
                
                if deleted_count[0] > 0:
                    self.stdout.write(self.style.SUCCESS(
                        f"Successfully removed '{category_name}' category from {song.name}"
                    ))
                else:
                    self.stdout.write(self.style.WARNING(
                        f"No '{category_name}' category found for {song.name}"
                    ))
                
                # List remaining categories
                remaining_categories = SongCategory.objects.filter(song=song)
                self.stdout.write("Remaining categories:")
                for cat in remaining_categories:
                    self.stdout.write(f"- {cat.sheet_tab.name}")
        
        except CartiCatalog.DoesNotExist:
            self.stdout.write(self.style.ERROR(f"Song with ID {song_id} not found"))
        except SheetTab.DoesNotExist:
            self.stdout.write(self.style.ERROR(f"Sheet tab '{category_name}' not found"))