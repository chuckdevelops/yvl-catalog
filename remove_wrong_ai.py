import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'carti_project.settings')
django.setup()

from catalog.models import CartiCatalog, SheetTab, SongCategory
from django.db.models import Q

def clean_ai_categories():
    try:
        # Get AI Tracks tab
        ai_tab = SheetTab.objects.get(name='🤖 AI Tracks')
        print(f'Found AI tab (ID: {ai_tab.id})')
        
        # Find ALL songs that are in AI category but don't start with 🤖
        wrong_ai_songs = SongCategory.objects.filter(
            sheet_tab=ai_tab
        ).exclude(
            song__name__startswith='🤖'
        )
        
        print(f'Found {wrong_ai_songs.count()} songs incorrectly in AI category')
        
        if wrong_ai_songs:
            # Display some examples
            for cat in wrong_ai_songs[:10]:
                print(f'- {cat.song.id}: {cat.song.name}')
            
            # Delete all incorrect associations
            count = wrong_ai_songs.delete()[0]
            print(f'Removed {count} incorrect AI category associations')
        
        # Verify the fix
        remaining = SongCategory.objects.filter(sheet_tab=ai_tab).exclude(song__name__startswith='🤖').count()
        print(f'Remaining incorrect AI associations: {remaining}')
        
        if remaining == 0:
            print('Fix successful! No more incorrect AI categories')
        else:
            print('Some incorrect AI categories still remain!')
            
        # Make sure all actual AI songs (🤖 prefix) are in AI category
        ai_songs = CartiCatalog.objects.filter(name__startswith='🤖')
        ai_songs_count = ai_songs.count()
        print(f'\nTotal AI songs (with 🤖 prefix): {ai_songs_count}')
        
        ai_correctly_categorized = SongCategory.objects.filter(sheet_tab=ai_tab, song__name__startswith='🤖').count()
        print(f'AI songs correctly in AI category: {ai_correctly_categorized}')
        
        # Add missing AI songs to AI category
        if ai_correctly_categorized < ai_songs_count:
            missing_count = 0
            for song in ai_songs:
                if not SongCategory.objects.filter(sheet_tab=ai_tab, song=song).exists():
                    SongCategory.objects.create(sheet_tab=ai_tab, song=song)
                    missing_count += 1
            
            print(f'Added {missing_count} missing AI songs to AI category')
        
    except SheetTab.DoesNotExist:
        print('AI Tracks tab not found!')

if __name__ == "__main__":
    clean_ai_categories()