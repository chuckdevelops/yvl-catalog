from django.core.management.base import BaseCommand
from catalog.models import CartiCatalog, SheetTab, SongCategory
from django.db.models import Q

class Command(BaseCommand):
    help = 'Fix misclassifications of songs in the AI category'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            dest='dry_run',
            help='Show what would be fixed without actually fixing',
        )
        parser.add_argument(
            '--fix-database',
            action='store_true',
            dest='fix_database',
            help='Fix the database entries by removing non-AI songs from AI category',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        fix_database = options['fix_database']
        
        try:
            # Get AI tab
            ai_tab = SheetTab.objects.get(name='🤖 AI Tracks')
            self.stdout.write(f'Found AI Tab (ID: {ai_tab.id})')
            
            # Find misclassified songs - songs with different emoji prefixes that are in AI category
            emoji_prefixes = ['⭐', '🏆', '🥇', '✨', '🗑️']
            
            for emoji in emoji_prefixes:
                # Get songs with this emoji prefix that are incorrectly in AI category
                misclassified_songs = CartiCatalog.objects.filter(
                    name__startswith=emoji,
                    categories__sheet_tab=ai_tab
                )
                
                if misclassified_songs.exists():
                    self.stdout.write(f'Found {misclassified_songs.count()} songs with {emoji} prefix incorrectly in AI category:')
                    
                    for song in misclassified_songs:
                        # Get correct emoji tab based on song name prefix
                        correct_tab = None
                        if emoji == '⭐':
                            correct_tab = SheetTab.objects.get(name='⭐ Best Of')
                        elif emoji == '🏆':
                            correct_tab = SheetTab.objects.get(name='🏆 Grails')
                        elif emoji == '🥇':
                            correct_tab = SheetTab.objects.get(name='🥇 Wanted')
                        elif emoji == '✨':
                            correct_tab = SheetTab.objects.get(name='✨ Special')
                        elif emoji == '🗑️':
                            correct_tab = SheetTab.objects.get(name='🗑️ Worst Of')
                        
                        self.stdout.write(f'  - {song.id}: {song.name} - Remove from AI, ensure in {correct_tab.name if correct_tab else "n/a"}')
                        
                        if (not dry_run and correct_tab) and fix_database:
                            # Remove from AI category
                            SongCategory.objects.filter(song=song, sheet_tab=ai_tab).delete()
                            
                            # Ensure in correct category based on emoji
                            SongCategory.objects.get_or_create(song=song, sheet_tab=correct_tab)
                
            # Find songs without emoji prefix incorrectly in AI category
            # unless they have AI in their name or notes
            non_ai_songs = SongCategory.objects.filter(
                sheet_tab=ai_tab
            ).exclude(
                Q(song__name__startswith='🤖') |
                Q(song__name__icontains='AI') |
                Q(song__notes__icontains='AI')
            )
            
            if non_ai_songs.exists():
                self.stdout.write(f'Found {non_ai_songs.count()} songs without AI indicators incorrectly in AI category:')
                
                count = 0
                for song_category in non_ai_songs:
                    song = song_category.song
                    count += 1
                    if count > 20:
                        self.stdout.write(f'  - ... and {non_ai_songs.count() - 20} more')
                        break
                        
                    self.stdout.write(f'  - {song.id}: {song.name}')
                    
                    if not dry_run and fix_database:
                        # Remove from AI category
                        song_category.delete()
            
            # Find all songs with 🤖 prefix
            ai_songs = CartiCatalog.objects.filter(name__startswith='🤖')
            
            if ai_songs.exists():
                self.stdout.write(f'Found {ai_songs.count()} songs with 🤖 prefix - these should be in AI category:')
                
                for song in ai_songs[:10]:  # Show first 10
                    self.stdout.write(f'  - {song.id}: {song.name}')
                
                if ai_songs.count() > 10:
                    self.stdout.write(f'  - ... and {ai_songs.count() - 10} more')
                
                # Make sure all AI songs are in the AI category
                if not dry_run and fix_database:
                    count = 0
                    for song in ai_songs:
                        # Check if not already in AI category
                        if not SongCategory.objects.filter(song=song, sheet_tab=ai_tab).exists():
                            # Add to AI category
                            SongCategory.objects.create(song=song, sheet_tab=ai_tab)
                            count += 1
                    
                    if count > 0:
                        self.stdout.write(self.style.SUCCESS(f'Added {count} songs with 🤖 prefix to AI category'))
            
            if dry_run:
                self.stdout.write(self.style.WARNING('DRY RUN: No changes were made'))
            elif not fix_database:
                self.stdout.write(self.style.WARNING('No database changes made. Use --fix-database to update the database.'))
            else:
                self.stdout.write(self.style.SUCCESS('Successfully fixed AI category misclassifications!'))
                
        except SheetTab.DoesNotExist as e:
            self.stdout.write(self.style.ERROR(f'Error: {str(e)}'))