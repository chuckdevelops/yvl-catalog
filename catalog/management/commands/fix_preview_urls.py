import os
from django.core.management.base import BaseCommand
from django.conf import settings
from catalog.models import CartiCatalog

class Command(BaseCommand):
    help = 'Fixes preview URLs to ensure they have the correct format'

    def handle(self, *args, **options):
        # Get all songs with preview URLs
        songs_with_previews = CartiCatalog.objects.exclude(preview_url__isnull=True)
        
        self.stdout.write(f"Found {songs_with_previews.count()} songs with preview URLs")
        
        fixed_count = 0
        missing_count = 0
        unchanged_count = 0
        
        for song in songs_with_previews:
            # Check if the preview URL is correctly formatted
            if not song.preview_url.startswith('/media/previews/'):
                # Fix the URL format
                filename = os.path.basename(song.preview_url)
                fixed_url = f'/media/previews/{filename}'
                
                # Check if the file exists
                file_path = os.path.join(settings.MEDIA_ROOT, 'previews', filename)
                if os.path.exists(file_path):
                    self.stdout.write(f"Fixing URL for song {song.id} - {song.name}")
                    song.preview_url = fixed_url
                    song.save(update_fields=['preview_url'])
                    fixed_count += 1
                else:
                    self.stdout.write(self.style.WARNING(
                        f"Preview file not found for song {song.id}: {file_path}"
                    ))
                    missing_count += 1
            else:
                # URL is already in the correct format
                # Verify the file exists
                filename = os.path.basename(song.preview_url)
                file_path = os.path.join(settings.MEDIA_ROOT, 'previews', filename)
                
                if os.path.exists(file_path):
                    self.stdout.write(f"URL is already correct for song {song.id}")
                    unchanged_count += 1
                else:
                    self.stdout.write(self.style.WARNING(
                        f"Preview file not found for song {song.id}: {file_path}"
                    ))
                    missing_count += 1
                
        self.stdout.write(self.style.SUCCESS(
            f"Fixed {fixed_count} URLs, {unchanged_count} were already correct, {missing_count} files missing"
        ))