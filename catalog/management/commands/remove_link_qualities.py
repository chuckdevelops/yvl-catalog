from django.core.management.base import BaseCommand
from catalog.models import CartiCatalog

class Command(BaseCommand):
    help = 'Removes songs with URL-based qualities after they have been migrated'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            dest='dry_run',
            help='Show what would be deleted without actually making changes',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            dest='force',
            help='Skip confirmation and force deletion',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        # Find songs with URL-based qualities
        link_songs = CartiCatalog.objects.filter(
            quality__startswith='http'
        )
        count = link_songs.count()
        
        self.stdout.write(f"Found {count} songs with URL-based qualities to remove")
        
        if count == 0:
            self.stdout.write(self.style.SUCCESS("No songs to remove"))
            return
            
        # Print the songs that will be removed
        for song in link_songs:
            self.stdout.write(f"Would remove: {song.name} (ID: {song.id}) - Quality: {song.quality}")
        
        # Add a force option to skip confirmation
        force = options.get('force', False)
        
        # Confirm with the user if not forced
        if not dry_run:
            if not force:
                try:
                    confirm = input(f"\nAre you sure you want to delete these {count} songs? (y/n): ")
                    if confirm.lower() != 'y':
                        self.stdout.write(self.style.WARNING("Operation cancelled by user"))
                        return
                except (EOFError, KeyboardInterrupt):
                    # If we can't get input (like in non-interactive environments), proceed anyway
                    self.stdout.write(self.style.WARNING("Non-interactive environment detected, proceeding with deletion"))
            
            # Delete the songs
            link_songs.delete()
            self.stdout.write(self.style.SUCCESS(f"Successfully removed {count} songs with URL-based qualities"))
        else:
            self.stdout.write(self.style.WARNING(f"\nDRY RUN: No changes made to the database"))
            self.stdout.write(f"Would remove {count} songs with URL-based qualities")