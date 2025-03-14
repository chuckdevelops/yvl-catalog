import os
import django
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'carti_project.settings')
django.setup()

from catalog.models import CartiCatalog, SheetTab, SongCategory

def check_and_fix_categories():
        
        # Check all emoji prefixes
        emoji_prefixes = ['⭐', '🏆', '🥇', '✨', '🗑️','🤖']
        
        for emoji in emoji_prefixes:
            # Get songs with this emoji
            emoji_songs = CartiCatalog.objects.filter(name__startswith=emoji)
            
            # Find songs with this emoji that are incorrectly in AI category
            ai_categories = SongCategory.objects.filter(sheet_tab=ai_tab, song__name__startswith=emoji)
            
            print(f'{emoji} songs in AI category: {ai_categories.count()} / {emoji_songs.count()}')
            
            if ai_categories.count() > 0:
                print("Examples:")
                for category in ai_categories[:5]:
                    print(f"- {category.song.id}: {category.song.name}")
                
                # Auto-fix mode
                deleted_count = ai_categories.delete()[0]
                print(f"Removed {deleted_count} category associations")
                
                # Get correct category based on emoji
                try:
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
                    
                    # Ensure all emoji songs are in their correct category
                    add_count = 0
                    for song in emoji_songs:
                        if not SongCategory.objects.filter(song=song, sheet_tab=correct_tab).exists():
                            SongCategory.objects.create(song=song, sheet_tab=correct_tab)
                            add_count += 1
                    
                    if add_count > 0:
                        print(f"Added {add_count} missing songs to {correct_tab.name}")
                        
                except SheetTab.DoesNotExist:
                    print(f"Could not find correct tab for {emoji} songs")
                
        # Check AI songs with duplicate categories
        ai_songs = CartiCatalog.objects.filter(name__startswith='🤖')
        print(f'\nTotal AI songs: {ai_songs.count()}')
        
        dupe_count = 0
        for song in ai_songs:
            ai_cats = SongCategory.objects.filter(sheet_tab=ai_tab, song=song)
            if ai_cats.count() > 1:
                dupe_count += 1
                print(f"Song {song.id}: {song.name} has {ai_cats.count()} AI category associations")
                # Keep only one
                keep_id = ai_cats.first().id
                SongCategory.objects.filter(sheet_tab=ai_tab, song=song).exclude(id=keep_id).delete()
                print(f"  - Kept one, deleted {ai_cats.count() - 1}")
        
        if dupe_count == 0:
            print("No duplicate AI category associations found")
                
        # Ensure all AI songs are in AI category
        ai_songs_missing = 0
        for song in ai_songs:
            if not SongCategory.objects.filter(sheet_tab=ai_tab, song=song).exists():
                SongCategory.objects.create(sheet_tab=ai_tab, song=song)
                ai_songs_missing += 1
        
        if ai_songs_missing > 0:
            print(f"Added {ai_songs_missing} AI songs to AI category")
        else:
            print("All AI songs are correctly categorized")
            
    except SheetTab.DoesNotExist:
        print("AI Tracks tab not found!")

def check_specific_song(song_id):
    try:
        song = CartiCatalog.objects.get(id=song_id)
        print(f"Song ID: {song.id}, Name: {song.name}")
        print("Categories:")
        for category in SongCategory.objects.filter(song=song):
            print(f"- {category.sheet_tab.name} (ID: {category.sheet_tab.id})")
            
    except CartiCatalog.DoesNotExist:
        print(f"Song with ID {song_id} not found!")

if __name__ == "__main__":
    print("Manual category fix tool - AUTO MODE\n")
    
    if len(sys.argv) > 1 and sys.argv[1].isdigit():
        # Check specific song
        check_specific_song(int(sys.argv[1]))
    else:
        # Check and fix all categories
        check_and_fix_categories()