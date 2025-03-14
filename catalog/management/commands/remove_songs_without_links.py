from django.core.management.base import BaseCommand
from django.db.models import Q
from catalog.models import CartiCatalog

class Command(BaseCommand):
    help = 'Removes songs without any links (both links and primary_link fields empty)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            dest='dry_run',
            help='Show what would be deleted without actually deleting',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        # Find songs without links
        songs_without_links = CartiCatalog.objects.filter(
            (Q(links__isnull=True) | Q(links="")) &
            (Q(primary_link__isnull=True) | Q(primary_link=""))
        )
        
        if not songs_without_links.exists():
            self.stdout.write(self.style.SUCCESS('No songs without links found!'))
            return
        
        self.stdout.write(f'Found {songs_without_links.count()} songs without links:')
        for song in songs_without_links:
            self.stdout.write(f'  - {song.id}: {song.name} ({song.era or "Unknown Era"})')
        
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN: No songs were deleted'))
            return
        
        # Delete the songs without links
        deleted_count = songs_without_links.delete()[0]
        self.stdout.write(self.style.SUCCESS(f'Successfully removed {deleted_count} songs without links!'))