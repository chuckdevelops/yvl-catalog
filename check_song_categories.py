import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'carti_project.settings')
django.setup()

from catalog.models import CartiCatalog, SheetTab, SongCategory

# Check "VETEMENTS JEANS"
vetements = CartiCatalog.objects.filter(name__contains='VETEMENTS JEANS').first()
if vetements:
    print(f'Song: {vetements.id} - {vetements.name}')
    print('Categories:')
    for cat in vetements.categories.all():
        print(f'- {cat.sheet_tab.name}')
else:
    print("VETEMENTS JEANS not found")

# Check "Margiela Roof"
margiela = CartiCatalog.objects.filter(name__contains='Margiela Roof').first()
if margiela:
    print(f'\nSong: {margiela.id} - {margiela.name}')
    print('Categories:')
    for cat in margiela.categories.all():
        print(f'- {cat.sheet_tab.name}')
else:
    print("\nMargiela Roof not found")

# Check if any songs without 🤖 prefix are in AI category
ai_tab = SheetTab.objects.get(name='🤖 AI Tracks')
wrong_songs = SongCategory.objects.filter(sheet_tab=ai_tab).exclude(song__name__startswith='🤖')
print(f'\nFound {wrong_songs.count()} songs incorrectly in AI category')
for song_cat in wrong_songs[:5]:
    print(f'- {song_cat.song.id}: {song_cat.song.name}')