from django.core.management.base import BaseCommand
from catalog.models import CartiCatalog, SheetTab, SongCategory
from django.db.models import Q

class Command(BaseCommand):
    help = 'Fix all AI badge and classification issues'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            dest='dry_run',
            help='Show what would be changed without actually changing',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        # Get AI tab
        try:
            ai_tab = SheetTab.objects.get(name='🤖 AI Tracks')
            self.stdout.write(f'Found AI Tab (ID: {ai_tab.id})')
            
            # PART 1: Find and fix songs with 🤖 prefix not in AI category
            ai_songs = CartiCatalog.objects.filter(name__startswith='🤖')
            
            if ai_songs.exists():
                self.stdout.write(f'Found {ai_songs.count()} songs with 🤖 prefix - ensuring they are in AI category')
                
                count_added = 0
                for song in ai_songs:
                    # Check if not already in AI category
                    if not SongCategory.objects.filter(song=song, sheet_tab=ai_tab).exists():
                        if not dry_run:
                            # Add to AI category
                            SongCategory.objects.create(song=song, sheet_tab=ai_tab)
                        count_added += 1
                
                if count_added > 0:
                    self.stdout.write(f'Found {count_added} AI songs not in AI category')
                    if not dry_run:
                        self.stdout.write(self.style.SUCCESS(f'Added {count_added} songs with 🤖 prefix to AI category'))
            
            # PART 2: Find songs without 🤖 prefix incorrectly in AI category
            non_ai_songs = SongCategory.objects.filter(
                sheet_tab=ai_tab
            ).exclude(
                Q(song__name__startswith='🤖')
            )
            
            if non_ai_songs.exists():
                self.stdout.write(f'Found {non_ai_songs.count()} songs without 🤖 prefix incorrectly in AI category:')
                
                count_removed = 0
                for song_category in non_ai_songs:
                    song = song_category.song
                    self.stdout.write(f'  - {song.id}: {song.name}')
                    
                    if not dry_run:
                        # Remove from AI category
                        song_category.delete()
                        count_removed += 1
                
                if count_removed > 0 and not dry_run:
                    self.stdout.write(self.style.SUCCESS(f'Removed {count_removed} non-AI songs from AI category'))
            
            # PART 3: Find songs with different emoji prefixes (⭐, 🏆, etc.) that might be incorrectly in AI
            emoji_prefixes = ['⭐', '🏆', '🥇', '✨', '🗑️']
            emoji_tab_map = {
                '⭐': '⭐ Best Of',
                '🏆': '🏆 Grails',
                '🥇': '🥇 Wanted',
                '✨': '✨ Special',
                '🗑️': '🗑️ Worst Of',
            }
            
            for emoji, tab_name in emoji_tab_map.items():
                try:
                    # Get the correct tab for this emoji
                    correct_tab = SheetTab.objects.get(name=tab_name)
                    
                    # Find songs with this emoji prefix
                    emoji_songs = CartiCatalog.objects.filter(name__startswith=emoji)
                    
                    if emoji_songs.exists():
                        self.stdout.write(f'Found {emoji_songs.count()} songs with {emoji} prefix - ensuring they are in correct category')
                        
                        count_fixed = 0
                        for song in emoji_songs:
                            # Ensure in correct category
                            if not SongCategory.objects.filter(song=song, sheet_tab=correct_tab).exists():
                                if not dry_run:
                                    SongCategory.objects.create(song=song, sheet_tab=correct_tab)
                                count_fixed += 1
                            
                            # Remove from AI category if present
                            if SongCategory.objects.filter(song=song, sheet_tab=ai_tab).exists():
                                if not dry_run:
                                    SongCategory.objects.filter(song=song, sheet_tab=ai_tab).delete()
                                count_fixed += 1
                        
                        if count_fixed > 0:
                            self.stdout.write(f'Fixed {count_fixed} songs with {emoji} prefix')
                except SheetTab.DoesNotExist:
                    self.stdout.write(self.style.WARNING(f'Tab {tab_name} not found, skipping'))
            
            if dry_run:
                self.stdout.write(self.style.WARNING('DRY RUN: No changes were made'))
            else:
                self.stdout.write(self.style.SUCCESS('Successfully fixed AI badges and categories!'))
                
        except SheetTab.DoesNotExist as e:
            self.stdout.write(self.style.ERROR(f'Error: {str(e)}'))