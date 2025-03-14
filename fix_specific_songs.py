import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'carti_project.settings')
django.setup()

from catalog.models import CartiCatalog, SheetTab, SongCategory

# Get the AI tab
ai_tab = SheetTab.objects.get(name='🤖 AI Tracks')

# Fix all songs in the database
def fix_all_songs():
    # Find all songs with non-AI prefix in AI category
    song_categories = SongCategory.objects.filter(sheet_tab=ai_tab).all()
    
    for song_category in song_categories:
        song = song_category.song
        # If the song doesn't start with 🤖, remove it from AI category
        if not song.name.startswith('🤖'):
            print(f"Removing song from AI category: {song.id} - {song.name}")
            song_category.delete()
    
    # Make sure all 🤖 songs are in AI category
    ai_songs = CartiCatalog.objects.filter(name__startswith='🤖')
    for song in ai_songs:
        if not SongCategory.objects.filter(song=song, sheet_tab=ai_tab).exists():
            print(f"Adding song to AI category: {song.id} - {song.name}")
            SongCategory.objects.create(song=song, sheet_tab=ai_tab)
    
    # Verify the fix
    remaining = SongCategory.objects.filter(sheet_tab=ai_tab).exclude(song__name__startswith='🤖').count()
    print(f"Remaining incorrect AI associations: {remaining}")
    
    if remaining == 0:
        print('Fix successful! No more incorrect AI categories')
    else:
        print('Some incorrect AI categories still remain!')

if __name__ == "__main__":
    fix_all_songs()