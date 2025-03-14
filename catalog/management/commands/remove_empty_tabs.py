from django.core.management.base import BaseCommand
from catalog.models import SheetTab, SongMetadata, SongCategory
from django.db.models import Count, Q

class Command(BaseCommand):
    help = 'Removes sheet tabs that have no associated songs'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            dest='dry_run',
            help='Show what would be deleted without actually deleting',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        # Find tabs with no songs in either primary or secondary categories
        empty_tabs = SheetTab.objects.filter(
            ~Q(id__in=SongMetadata.objects.values('sheet_tab_id').distinct()) &
            ~Q(id__in=SongCategory.objects.values('sheet_tab_id').distinct())
        )
        
        if not empty_tabs.exists():
            self.stdout.write(self.style.SUCCESS('No empty tabs found!'))
            return
        
        self.stdout.write(f'Found {empty_tabs.count()} empty tabs:')
        for tab in empty_tabs:
            self.stdout.write(f'  - {tab.id}: {tab.name} (Sheet ID: {tab.sheet_id})')
        
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN: No tabs were deleted'))
            return
        
        # Delete the empty tabs
        deleted_count = empty_tabs.delete()[0]
        self.stdout.write(self.style.SUCCESS(f'Successfully removed {deleted_count} empty tabs!'))