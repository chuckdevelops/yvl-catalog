from django.core.management.base import BaseCommand
from catalog.models import CartiCatalog
from django.db import transaction


class Command(BaseCommand):
    help = 'Standardizes type values to prevent duplicates in dropdown'

    def handle(self, *args, **options):
        with transaction.atomic():
            # Count songs with various type values
            yes_count = CartiCatalog.objects.filter(type__iexact='Yes').count()
            no_count = CartiCatalog.objects.filter(type__iexact='No').count()
            streaming_count = CartiCatalog.objects.filter(type__iexact='Streaming').count()
            off_streaming_count = CartiCatalog.objects.filter(type__iexact='Off Streaming').count()
            
            self.stdout.write(self.style.WARNING(f"Found songs with 'Yes': {yes_count}"))
            self.stdout.write(self.style.WARNING(f"Found songs with 'No': {no_count}"))
            self.stdout.write(self.style.WARNING(f"Found songs with 'Streaming': {streaming_count}"))
            self.stdout.write(self.style.WARNING(f"Found songs with 'Off Streaming': {off_streaming_count}"))
            
            # Standardize "Yes" to "Streaming"
            if yes_count > 0:
                yes_songs = CartiCatalog.objects.filter(type__iexact='Yes')
                for song in yes_songs:
                    song.type = "Streaming"
                    song.save()
                self.stdout.write(self.style.SUCCESS(f"Converted {yes_count} songs from 'Yes' to 'Streaming'"))
            
            # Standardize "No" to "Off Streaming"
            if no_count > 0:
                no_songs = CartiCatalog.objects.filter(type__iexact='No')
                for song in no_songs:
                    song.type = "Off Streaming"
                    song.save()
                self.stdout.write(self.style.SUCCESS(f"Converted {no_count} songs from 'No' to 'Off Streaming'"))
            
            # Check lowercase and other case variations
            yes_variations = CartiCatalog.objects.filter(type__icontains='yes').exclude(type__iexact='Yes')
            if yes_variations.exists():
                for song in yes_variations:
                    self.stdout.write(self.style.WARNING(f"Found song with '{song.type}': {song.name}"))
                    song.type = "Streaming"
                    song.save()
                self.stdout.write(self.style.SUCCESS(f"Converted {yes_variations.count()} songs with 'yes' variations to 'Streaming'"))
            
            no_variations = CartiCatalog.objects.filter(type__icontains='no').exclude(type__iexact='No')
            if no_variations.exists():
                for song in no_variations:
                    self.stdout.write(self.style.WARNING(f"Found song with '{song.type}': {song.name}"))
                    song.type = "Off Streaming"
                    song.save()
                self.stdout.write(self.style.SUCCESS(f"Converted {no_variations.count()} songs with 'no' variations to 'Off Streaming'"))
            
            # Verify final counts
            streaming_count_after = CartiCatalog.objects.filter(type='Streaming').count()
            off_streaming_count_after = CartiCatalog.objects.filter(type='Off Streaming').count()
            yes_count_after = CartiCatalog.objects.filter(type__iexact='Yes').count()
            no_count_after = CartiCatalog.objects.filter(type__iexact='No').count()
            
            self.stdout.write(self.style.SUCCESS(f"Final count of 'Streaming': {streaming_count_after}"))
            self.stdout.write(self.style.SUCCESS(f"Final count of 'Off Streaming': {off_streaming_count_after}"))
            self.stdout.write(self.style.SUCCESS(f"Final count of 'Yes': {yes_count_after} (should be 0)"))
            self.stdout.write(self.style.SUCCESS(f"Final count of 'No': {no_count_after} (should be 0)"))
            
            self.stdout.write(self.style.SUCCESS("Type values have been standardized to prevent duplicates in dropdown"))