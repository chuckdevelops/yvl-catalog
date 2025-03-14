from django.core.management.base import BaseCommand
from catalog.models import SheetTab, SongCategory

class Command(BaseCommand):
    help = 'Removes specified categories and their associated song categories'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            dest='dry_run',
            help='Show what would be deleted without actually deleting',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        # Categories to remove
        categories_to_remove = ['Buys', 'Fakes', 'Social Media']
        
        for category_name in categories_to_remove:
            try:
                # Find the category tab
                category_tab = SheetTab.objects.get(name=category_name)
                self.stdout.write(f'Found category: {category_tab.name} (ID: {category_tab.id})')
                
                # Find songs in this category
                song_categories = SongCategory.objects.filter(sheet_tab=category_tab)
                
                if song_categories.exists():
                    self.stdout.write(f'Found {song_categories.count()} songs in the {category_name} category:')
                    for sc in song_categories:
                        self.stdout.write(f'  - {sc.song.name} (ID: {sc.song.id})')
                    
                    if not dry_run:
                        self.stdout.write(f'Deleting song categories for {category_name}...')
                        song_categories.delete()
                else:
                    self.stdout.write(f'No songs found in the {category_name} category')
                
                # Delete the category itself
                if not dry_run:
                    self.stdout.write(f'Deleting category: {category_name}')
                    category_tab.delete()
                    self.stdout.write(self.style.SUCCESS(f'Successfully removed {category_name} category!'))
                
            except SheetTab.DoesNotExist:
                self.stdout.write(self.style.WARNING(f'Category {category_name} not found'))
        
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN: No changes were made'))