from django.core.management.base import BaseCommand
from catalog.models import SheetTab, SongCategory

class Command(BaseCommand):
    help = 'Removes the Tracklists tab and any tabs that appear after it in the dropdown'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            dest='dry_run',
            help='Show what would be deleted without actually deleting',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        # Get all tabs ordered as they appear in the dropdown
        tab_order_map = {
            'Released': 1,
            'Unreleased': 2,
            '🏆 Grails': 3,
            '🥇 Wanted': 4,
            '⭐ Best Of': 5,
            '✨ Special': 6,
            '🤖 AI Tracks': 7,
            '🗑️ Worst Of': 8,
            'OG Files': 9,
            'Recent': 10,
            'Stems': 11,
            'Tracklists': 12,
        }
        
        # Get all tabs
        all_tabs = SheetTab.objects.all()
        
        # Tabs to remove (Tracklists and all that aren't in our order map)
        tabs_to_remove = []
        
        # Find tabs to remove
        for tab in all_tabs:
            if tab.name == 'Tracklists' or tab.name not in tab_order_map:
                tabs_to_remove.append(tab)
        
        if not tabs_to_remove:
            self.stdout.write(self.style.WARNING('No tabs to remove'))
            return
        
        self.stdout.write(f'Found {len(tabs_to_remove)} tabs to remove:')
        for tab in tabs_to_remove:
            self.stdout.write(f'  - {tab.name} (ID: {tab.id})')
            
            # Count songs in this tab
            song_categories = SongCategory.objects.filter(sheet_tab=tab)
            if song_categories.exists():
                self.stdout.write(f'    Found {song_categories.count()} songs in this tab')
                
                if not dry_run:
                    self.stdout.write(f'    Removing song associations for {tab.name}...')
                    song_categories.delete()
            
            # Delete the tab itself
            if not dry_run:
                self.stdout.write(f'    Deleting tab: {tab.name}')
                tab.delete()
                
        if dry_run:
            self.stdout.write(self.style.WARNING('\nDRY RUN: No changes were made'))
        else:
            self.stdout.write(self.style.SUCCESS(f'\nSuccessfully removed {len(tabs_to_remove)} tabs from the dropdown!'))