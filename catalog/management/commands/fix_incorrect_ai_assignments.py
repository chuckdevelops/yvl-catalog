from django.core.management.base import BaseCommand
from catalog.models import CartiCatalog, SheetTab, SongCategory
from django.db.models import Q

class Command(BaseCommand):
    help = 'Find and fix songs incorrectly assigned to AI Tracks'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            dest='dry_run',
            help='Show what would change without applying changes',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        try:
            # Get AI Tracks tab
            ai_tab = SheetTab.objects.get(name='🤖 AI Tracks')
            self.stdout.write(f'Found AI Tracks tab (ID: {ai_tab.id})')
            
            # Get Unreleased tab for reassignment
            unreleased_tab = SheetTab.objects.get(name='Unreleased')
            self.stdout.write(f'Found Unreleased tab (ID: {unreleased_tab.id})')
            
            # 1. Find songs incorrectly in AI category (don't have 🤖 prefix)
            wrong_ai_songs = CartiCatalog.objects.filter(
                categories__sheet_tab=ai_tab
            ).exclude(
                name__startswith='🤖'
            )
            
            self.stdout.write(f'Found {wrong_ai_songs.count()} songs incorrectly in AI category')
            
            fixed_count = 0
            for song in wrong_ai_songs:
                self.stdout.write(f'Processing: {song.id}: {song.name}')
                
                # Get the AI category for this song
                ai_category = SongCategory.objects.filter(song=song, sheet_tab=ai_tab).first()
                
                # Remove from AI category
                if not dry_run and ai_category:
                    ai_category.delete()
                    self.stdout.write(f'  - Removed from AI Tracks')
                    
                    # Check if song has any categories left
                    if not song.categories.exists():
                        # Add to Unreleased if no categories left
                        SongCategory.objects.create(song=song, sheet_tab=unreleased_tab)
                        self.stdout.write(f'  - Added to Unreleased')
                    
                    fixed_count += 1
                elif dry_run:
                    self.stdout.write(f'  - Would remove from AI Tracks')
                    if not song.categories.exclude(sheet_tab=ai_tab).exists():
                        self.stdout.write(f'  - Would add to Unreleased')
            
            # 2. Find actual AI songs (with 🤖 prefix) missing from AI category
            ai_prefix_songs = CartiCatalog.objects.filter(name__startswith='🤖')
            missing_ai_songs = []
            
            for song in ai_prefix_songs:
                if not SongCategory.objects.filter(song=song, sheet_tab=ai_tab).exists():
                    missing_ai_songs.append(song)
            
            if missing_ai_songs:
                self.stdout.write(f'Found {len(missing_ai_songs)} songs with 🤖 prefix not in AI category')
                
                for song in missing_ai_songs:
                    self.stdout.write(f'Adding {song.id}: {song.name} to AI category')
                    
                    if not dry_run:
                        SongCategory.objects.create(song=song, sheet_tab=ai_tab)
                        self.stdout.write(f'  - Added to AI Tracks')
            
            if dry_run:
                self.stdout.write(self.style.WARNING('DRY RUN: No changes were made'))
            else:
                self.stdout.write(self.style.SUCCESS(f'Successfully fixed {fixed_count} incorrect AI assignments'))
                
        except SheetTab.DoesNotExist as e:
            self.stdout.write(self.style.ERROR(f'Error: {str(e)}'))