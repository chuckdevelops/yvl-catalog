from django.core.management.base import BaseCommand
from catalog.models import CartiCatalog, SheetTab, SongCategory, SongMetadata
from django.db.models import Q

class Command(BaseCommand):
    help = 'Fix various display issues with song data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            dest='dry_run',
            help='Show what would be changed without actually changing',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        # 1. Fix "yes"/"no" in type field
        yes_no_types = CartiCatalog.objects.filter(type__in=['yes', 'no'])
        if yes_no_types.exists():
            self.stdout.write(f'Found {yes_no_types.count()} songs with Type as "yes" or "no":')
            for song in yes_no_types:
                self.stdout.write(f'  - {song.id}: {song.name}, Type: {song.type}')
                
                # Set type to an empty string instead of yes/no
                if not dry_run:
                    song.type = ''
                    song.save(update_fields=['type'])
                    self.stdout.write(f'    -> Changed type to empty string')
        else:
            self.stdout.write('No songs found with Type as "yes" or "no"')
            
        # 2. Fix AI track categorization issues
        try:
            # Find AI tab
            ai_tab = SheetTab.objects.get(name='🤖 AI Tracks')
            
            # Find songs with "AI" in name that aren't in the AI category
            ai_songs = CartiCatalog.objects.filter(
                Q(name__icontains='AI') | 
                Q(notes__icontains='AI generated') | 
                Q(notes__icontains='AI track')
            ).exclude(
                Q(categories__sheet_tab=ai_tab)
            )
            
            if ai_songs.exists():
                self.stdout.write(f'Found {ai_songs.count()} potential AI songs not in AI category:')
                for song in ai_songs:
                    self.stdout.write(f'  - {song.id}: {song.name}')
                    
                    if not dry_run:
                        # Add to AI category if not already there
                        SongCategory.objects.get_or_create(
                            song=song,
                            sheet_tab=ai_tab
                        )
                        self.stdout.write(f'    -> Added to AI category')
        except SheetTab.DoesNotExist:
            self.stdout.write('AI Tracks tab not found')
            
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN: No changes were made'))