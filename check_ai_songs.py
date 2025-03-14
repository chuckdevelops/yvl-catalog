import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'carti_project.settings')
django.setup()

from catalog.models import CartiCatalog, SheetTab, SongCategory

# Find AI tab
ai_tab = SheetTab.objects.get(name='🤖 AI Tracks')
print(f"Found AI tab with ID: {ai_tab.id}")

# Find songs incorrectly in AI category
wrong_songs = SongCategory.objects.filter(sheet_tab=ai_tab).exclude(song__name__startswith='🤖')
print(f"\nFound {wrong_songs.count()} songs incorrectly in AI category:")
for i, song_cat in enumerate(wrong_songs[:10]):
    print(f"{i+1}. ID: {song_cat.song.id} - {song_cat.song.name}")

# Find all songs with 🤖 prefix not in AI category
ai_prefix_songs = CartiCatalog.objects.filter(name__startswith='🤖')
print(f"\nTotal songs with 🤖 prefix: {ai_prefix_songs.count()}")

missing_from_ai = []
for song in ai_prefix_songs:
    if not SongCategory.objects.filter(song=song, sheet_tab=ai_tab).exists():
        missing_from_ai.append(song)

print(f"Found {len(missing_from_ai)} songs with 🤖 prefix not in AI category:")
for i, song in enumerate(missing_from_ai[:10]):
    print(f"{i+1}. ID: {song.id} - {song.name}")

# Check songs with other emoji prefixes incorrectly in AI category
emoji_prefixes = ['⭐', '🏆', '🥇', '✨', '🗑️']
for prefix in emoji_prefixes:
    wrong_emoji_songs = SongCategory.objects.filter(
        sheet_tab=ai_tab,
        song__name__startswith=prefix
    )
    if wrong_emoji_songs.exists():
        print(f"\nFound {wrong_emoji_songs.count()} songs with {prefix} prefix incorrectly in AI category:")
        for i, song_cat in enumerate(wrong_emoji_songs[:5]):
            print(f"{i+1}. ID: {song_cat.song.id} - {song_cat.song.name}")

# Look for specific songs mentioned
vetements = CartiCatalog.objects.filter(name__contains='VETEMENTS JEANS').first()
if vetements:
    print(f"\nVETEMENTS JEANS:")
    print(f"ID: {vetements.id}")
    print(f"Name: {vetements.name}")
    print("Categories:")
    for cat in vetements.categories.all():
        print(f"- {cat.sheet_tab.name}")
    
    # Check if in AI category
    in_ai = SongCategory.objects.filter(song=vetements, sheet_tab=ai_tab).exists()
    print(f"In AI category: {in_ai}")

margiela = CartiCatalog.objects.filter(name__contains='Margiela Roof').first()
if margiela:
    print(f"\nMargiela Roof:")
    print(f"ID: {margiela.id}")
    print(f"Name: {margiela.name}")
    print("Categories:")
    for cat in margiela.categories.all():
        print(f"- {cat.sheet_tab.name}")
    
    # Check if in AI category
    in_ai = SongCategory.objects.filter(song=margiela, sheet_tab=ai_tab).exists()
    print(f"In AI category: {in_ai}")