from django.core.management.base import BaseCommand
from catalog.models import CartiCatalog, SheetTab, SongCategory
from django.db.models import Q

class Command(BaseCommand):
    help = 'Verify that songs are in the correct categories based on their names'

    def handle(self, *args, **options):
        self.stdout.write('Checking song categories...')
        
        # Check emoji songs
        emoji_mappings = {
            '⭐': 'Best Of',
            '🏆': 'Grails', 
            '🥇': 'Wanted',
            '✨': 'Special',
            '🗑️': 'Worst Of',
            '🤖': 'AI Tracks'
        }
        
        for emoji, category_name in emoji_mappings.items():
            # Get full tab name with emoji
            tab_name = f"{emoji} {category_name}"
            
            try:
                tab = SheetTab.objects.get(name=tab_name)
                self.stdout.write(f'Checking {tab_name} songs...')
                
                # Find songs with this emoji prefix
                emoji_songs = CartiCatalog.objects.filter(name__startswith=emoji)
                
                self.stdout.write(f'  Found {emoji_songs.count()} songs with {emoji} prefix')
                
                # Check if all these songs are in the correct category
                for song in emoji_songs:
                    is_in_category = SongCategory.objects.filter(song=song, sheet_tab=tab).exists()
                    
                    if not is_in_category:
                        self.stdout.write(self.style.WARNING(f'  - {song.id}: {song.name} is NOT in {tab_name} category'))
                        # Add to correct category
                        SongCategory.objects.get_or_create(song=song, sheet_tab=tab)
                        self.stdout.write(self.style.SUCCESS(f'    -> Added to {tab_name} category'))
                    
                # For AI category, check for "AI" in name or notes, but exclude emoji prefixed songs
                if emoji == '🤖':
                    ai_songs = CartiCatalog.objects.filter(
                        Q(name__icontains='AI') | 
                        Q(notes__icontains='AI generated') | 
                        Q(notes__icontains='AI track')
                    ).exclude(
                        Q(name__startswith='🤖') |
                        Q(name__startswith='⭐') |
                        Q(name__startswith='🏆') |
                        Q(name__startswith='🥇') |
                        Q(name__startswith='✨') |
                        Q(name__startswith='🗑️')
                    )
                    
                    self.stdout.write(f'  Found {ai_songs.count()} additional songs with AI mentions')
                    
                    for song in ai_songs:
                        is_in_category = SongCategory.objects.filter(song=song, sheet_tab=tab).exists()
                        
                        if not is_in_category:
                            self.stdout.write(self.style.WARNING(f'  - {song.id}: {song.name} has AI mentions but is NOT in AI category'))
                            # Add to AI category
                            SongCategory.objects.get_or_create(song=song, sheet_tab=tab)
                            self.stdout.write(self.style.SUCCESS(f'    -> Added to AI category'))
                
                # Check for misplaced songs (songs in wrong categories)
                for other_emoji, other_category in emoji_mappings.items():
                    if emoji == other_emoji:
                        continue
                        
                    other_tab_name = f"{other_emoji} {other_category}"
                    try:
                        other_tab = SheetTab.objects.get(name=other_tab_name)
                        
                        # Find songs with this emoji prefix that are incorrectly in other category
                        misplaced_songs = CartiCatalog.objects.filter(
                            name__startswith=emoji,
                            categories__sheet_tab=other_tab
                        )
                        
                        if misplaced_songs.exists():
                            self.stdout.write(self.style.WARNING(f'  Found {misplaced_songs.count()} {emoji} songs incorrectly in {other_tab_name} category:'))
                            
                            for song in misplaced_songs:
                                self.stdout.write(f'  - {song.id}: {song.name} is incorrectly in {other_tab_name}')
                                
                                # Remove from wrong category
                                SongCategory.objects.filter(song=song, sheet_tab=other_tab).delete()
                                self.stdout.write(self.style.SUCCESS(f'    -> Removed from {other_tab_name}'))
                    except SheetTab.DoesNotExist:
                        pass
                        
            except SheetTab.DoesNotExist:
                self.stdout.write(self.style.WARNING(f'{tab_name} category not found!'))
                
        self.stdout.write(self.style.SUCCESS('All song categories checked!'))