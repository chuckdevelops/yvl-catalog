from django.core.management.base import BaseCommand
from catalog.models import CartiCatalog, FitPic
from django.db.models import Q

class Command(BaseCommand):
    help = 'Transfers songs with "Unreleased" quality to the FitPic model'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            dest='dry_run',
            help='Show what would be migrated without actually making changes',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        # Find songs with "Unreleased" quality
        unreleased_songs = CartiCatalog.objects.filter(quality="Unreleased")
        
        self.stdout.write(f"Found {unreleased_songs.count()} songs with 'Unreleased' quality")
        
        # Process each song
        migrated_count = 0
        skipped_count = 0
        
        for song in unreleased_songs:
            # Check if the song has a link we can use for the image
            if not song.links:
                self.stdout.write(self.style.WARNING(f"Skipping {song.name}: No links found"))
                skipped_count += 1
                continue
            
            # Create a new FitPic entry
            era = song.era if song.era else "Unknown Era"
            caption = song.name if song.name else "Untitled Fit Pic"
            notes = song.notes if song.notes else ""
            
            # Detect photographer from notes if possible
            photographer = None
            if notes and "photographer:" in notes.lower():
                import re
                photographer_match = re.search(r'photographer:\s*([^\.;,\n]+)', notes, re.IGNORECASE)
                if photographer_match:
                    photographer = photographer_match.group(1).strip()
            
            # Extract release_date from leak_date if available
            release_date = song.leak_date if song.leak_date else "Unknown Date"
            
            # Set up FitPic-specific fields
            pic_type = "Archive Post"  # Default type for migrated entries
            portion = "Full"  # Default value
            quality = song.quality if song.quality else "Standard Quality"
            
            # Use the first link as the source link
            source_links = song.links.split('\n')[0] if '\n' in song.links else song.links
            
            # Try to extract image URL if it's directly in the links
            image_url = None
            import re
            img_patterns = [
                r'(https?://[^\s]+\.(?:jpg|jpeg|png|gif))',
                r'(https?://[^\s]+\bimage[^\s]*)',
            ]
            
            for pattern in img_patterns:
                match = re.search(pattern, song.links, re.IGNORECASE)
                if match:
                    image_url = match.group(1)
                    break
            
            if not dry_run:
                # Create the new FitPic entry
                new_fitpic = FitPic.objects.create(
                    era=era,
                    caption=caption,
                    notes=notes,
                    photographer=photographer,
                    release_date=release_date,
                    pic_type=pic_type,
                    portion=portion,
                    quality=quality,
                    image_url=image_url,
                    source_links=source_links
                )
                self.stdout.write(self.style.SUCCESS(f"Migrated: {song.name} → FitPic #{new_fitpic.id}"))
            else:
                self.stdout.write(f"Would migrate: {song.name}")
                
            migrated_count += 1
        
        if dry_run:
            self.stdout.write(self.style.WARNING(f"\nDRY RUN: No changes made to the database"))
            self.stdout.write(f"Would migrate {migrated_count} songs to FitPics (skipped {skipped_count})")
        else:
            self.stdout.write(self.style.SUCCESS(f"\nSuccessfully migrated {migrated_count} songs to FitPics (skipped {skipped_count})"))