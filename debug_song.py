import os
import django
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'carti_project.settings')
django.setup()

from catalog.models import CartiCatalog, SheetTab, SongCategory

def check_song(song_id):
    try:
        song = CartiCatalog.objects.get(id=song_id)
        print(f"Song: {song.name}")
        
        # Check categories
        print("Categories:")
        for cat in SongCategory.objects.filter(song=song):
            print(f"- {cat.sheet_tab.name}")
        
        # Directly simulate what the view would do
        secondary_tabs = [category.sheet_tab for category in song.categories.all()]
        secondary_tab_names = [tab.name for tab in secondary_tabs]
        print(f"Secondary tab names: {secondary_tab_names}")
        
        emoji_tab_names = []
        other_tab_names = []
        
        # First attempt - what our view filtering should do
        for tab in secondary_tab_names:
                
            if any(emoji in tab for emoji in ["🏆", "🥇", "⭐", "✨", "🗑️", "🤖"]):
                emoji_tab_names.append(tab)
            else:
                other_tab_names.append(tab)
                
        print(f"Emoji tabs (filtered): {emoji_tab_names}")
        print(f"Other tabs: {other_tab_names}")
        
        # Raw, unfiltered list
        unfiltered_emoji_tabs = [tab for tab in secondary_tab_names 
                           if any(emoji in tab for emoji in ["🏆", "🥇", "⭐", "✨", "🗑️", "🤖"])]
        print(f"Unfiltered emoji tabs: {unfiltered_emoji_tabs}")
        
    except CartiCatalog.DoesNotExist:
        print(f"No song found with ID {song_id}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        song_id = int(sys.argv[1])
        check_song(song_id)
    else:
        print("Usage: python debug_song.py SONG_ID")
        
        # Example - check VETEMENTS JEANS
        print("\nChecking song with ID 1076:")
        check_song(1076)
        
        # Example - check an AI song
        print("\nChecking AI song with ID 8444:")
        check_song(8444)