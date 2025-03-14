from django.core.management.base import BaseCommand
from catalog.models import CartiCatalog, SheetTab

class Command(BaseCommand):
    help = 'Check for incorrect AI assignments'

    def handle(self, *args, **options):
        try:
            # Get AI tab
            ai_tab = SheetTab.objects.get(name='🤖 AI Tracks')
            self.stdout.write(f'Found AI Tab (ID: {ai_tab.id})')
            
            # Find songs with 🤖 prefix (should be in AI category)
            ai_songs = CartiCatalog.objects.filter(name__startswith='🤖')
            self.stdout.write(f'Songs with 🤖 prefix: {ai_songs.count()}')
            for song in ai_songs:
                self.stdout.write(f'- {song.id}: {song.name}')
                
            # Find all songs in the AI category
            songs_in_ai_category = CartiCatalog.objects.filter(categories__sheet_tab=ai_tab)
            self.stdout.write(f'\nSongs in AI category: {songs_in_ai_category.count()}')
            for song in songs_in_ai_category:
                self.stdout.write(f'- {song.id}: {song.name}')
            
            # Find songs incorrectly in AI category (no 🤖 prefix)
            incorrect_ai_songs = songs_in_ai_category.exclude(name__startswith='🤖')
            self.stdout.write(f'\nIncorrect AI assignments: {incorrect_ai_songs.count()}')
            for song in incorrect_ai_songs:
                self.stdout.write(f'- {song.id}: {song.name}')
                
        except SheetTab.DoesNotExist as e:
            self.stdout.write(self.style.ERROR(f'Error: {str(e)}'))