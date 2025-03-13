import os
import django
import csv
import argparse

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "carti_project.settings")
django.setup()

from catalog.models import CartiCatalog, SheetTab, SongMetadata

def reset_tabs_from_csv():
    """Reset tab assignments based on the sheetsdata.csv file"""
    print("Resetting tab assignments from sheetsdata.csv...")
    
    # APPROACH: We want songs to be in these tabs in order of priority:
    # 1. If type is 'Single' or 'Album Track', song should be in 'Released'
    # 2. If name has an emoji, follow the emoji to its tab
    # 3. Use other rules for specific types
    # 4. Default to Unreleased
    
    # Check if the CSV exists
    if not os.path.exists('sheetsdata.csv'):
        print("Error: sheetsdata.csv not found. Run python3 main.py first.")
        return
    
    # Read CSV column headers to understand the format
    with open('sheetsdata.csv', 'r') as f:
        reader = csv.reader(f)
        headers = next(reader)
        print(f"CSV headers: {headers}")
    
    # Load all songs from the database
    all_songs = {f"{song.era}|{song.name}": song for song in CartiCatalog.objects.all()}
    print(f"Loaded {len(all_songs)} songs from database")
    
    # Load the rules for tab assignment
    released_tab = SheetTab.objects.get(name="Released")
    unreleased_tab = SheetTab.objects.get(name="Unreleased")
    
    # Get all sheet tabs by name
    sheet_tab_by_name = {}
    for tab in SheetTab.objects.all():
        sheet_tab_by_name[tab.name] = tab
    
    # Define emoji to tab mapping
    emoji_tabs = {
        "🏆": SheetTab.objects.get(name="🏆 Grails"),
        "🥇": SheetTab.objects.get(name="🥇 Wanted"),
        "⭐": SheetTab.objects.get(name="⭐ Best Of"),
        "✨": SheetTab.objects.get(name="✨ Special"),
        "🗑️": SheetTab.objects.get(name="🗑️ Worst Of"),
        "🗑": SheetTab.objects.get(name="🗑️ Worst Of"),
        "🤖": SheetTab.objects.get(name="🤖 AI Tracks")
    }
    
    # Special type/keyword to tab mapping
    keyword_tabs = {
        "OG Files": SheetTab.objects.get(name="OG Files"),
        "Stems": SheetTab.objects.get(name="Stems"),
        "Fakes": SheetTab.objects.get(name="Fakes"),
        "Art": SheetTab.objects.get(name="Art"),
        "Social Media": SheetTab.objects.get(name="Social Media"),
        "Tracklists": SheetTab.objects.get(name="Tracklists"),
        "Buys": SheetTab.objects.get(name="Buys")
    }
    
    print(f"Loaded {len(SheetTab.objects.all())} sheet tabs")
    
    # Track statistics
    updated = 0
    not_found = 0
    no_change = 0
    
    # Now let's directly set tab assignments based on priority rules
    total_songs = CartiCatalog.objects.count()
    print(f"Processing {total_songs} songs...")
    
    # Priority 1: Released songs
    released_count = 0
    for song in CartiCatalog.objects.filter(type__in=["Single", "Album Track"]):
        metadata, created = SongMetadata.objects.get_or_create(song=song)
        
        if metadata.sheet_tab != released_tab:
            old_tab = metadata.sheet_tab.name if metadata.sheet_tab else "None"
            metadata.sheet_tab = released_tab
            metadata.save()
            print(f"[RELEASED] '{song.name}' from '{old_tab}' to 'Released'")
            updated += 1
            released_count += 1
        else:
            no_change += 1
    
    print(f"Set {released_count} songs with type 'Single'/'Album Track' to Released tab")
    
    # Priority 2: Emoji-based assignment
    emoji_count = 0
    for emoji, tab in emoji_tabs.items():
        # Find songs with this emoji that aren't in Released tab
        emoji_songs = CartiCatalog.objects.filter(
            name__contains=emoji
        ).exclude(
            metadata__sheet_tab=released_tab
        )
        
        for song in emoji_songs:
            metadata, created = SongMetadata.objects.get_or_create(song=song)
            
            if metadata.sheet_tab != tab:
                old_tab = metadata.sheet_tab.name if metadata.sheet_tab else "None"
                metadata.sheet_tab = tab
                metadata.save()
                print(f"[EMOJI] '{song.name}' from '{old_tab}' to '{tab.name}'")
                updated += 1
                emoji_count += 1
            else:
                no_change += 1
    
    print(f"Set {emoji_count} songs with emojis to their appropriate tabs")
    
    # Priority 3: Keyword/type-based assignments
    keyword_count = 0
    
    # OG Files
    og_files_songs = CartiCatalog.objects.filter(
        type__contains="OG"
    ).exclude(
        metadata__sheet_tab=released_tab
    ).exclude(
        name__contains="🏆"
    ).exclude(
        name__contains="🥇"
    ).exclude(
        name__contains="⭐"
    ).exclude(
        name__contains="✨"
    ).exclude(
        name__contains="🗑️"
    ).exclude(
        name__contains="🗑"
    ).exclude(
        name__contains="🤖"
    )
    
    for song in og_files_songs:
        metadata, created = SongMetadata.objects.get_or_create(song=song)
        
        if metadata.sheet_tab != keyword_tabs["OG Files"]:
            old_tab = metadata.sheet_tab.name if metadata.sheet_tab else "None"
            metadata.sheet_tab = keyword_tabs["OG Files"]
            metadata.save()
            print(f"[KEYWORD] '{song.name}' from '{old_tab}' to 'OG Files'")
            updated += 1
            keyword_count += 1
        else:
            no_change += 1
    
    # Stems
    stems_songs = CartiCatalog.objects.filter(
        type__contains="Stem"
    ).exclude(
        metadata__sheet_tab=released_tab
    ).exclude(
        name__contains="🏆"
    ).exclude(
        name__contains="🥇"
    ).exclude(
        name__contains="⭐"
    ).exclude(
        name__contains="✨"
    ).exclude(
        name__contains="🗑️"
    ).exclude(
        name__contains="🗑"
    ).exclude(
        name__contains="🤖"
    )
    
    for song in stems_songs:
        metadata, created = SongMetadata.objects.get_or_create(song=song)
        
        if metadata.sheet_tab != keyword_tabs["Stems"]:
            old_tab = metadata.sheet_tab.name if metadata.sheet_tab else "None"
            metadata.sheet_tab = keyword_tabs["Stems"]
            metadata.save()
            print(f"[KEYWORD] '{song.name}' from '{old_tab}' to 'Stems'")
            updated += 1
            keyword_count += 1
        else:
            no_change += 1
    
    # Art
    art_songs = CartiCatalog.objects.filter(
        name__contains="Art"
    ).exclude(
        metadata__sheet_tab=released_tab
    ).exclude(
        name__contains="🏆"
    ).exclude(
        name__contains="🥇"
    ).exclude(
        name__contains="⭐"
    ).exclude(
        name__contains="✨"
    ).exclude(
        name__contains="🗑️"
    ).exclude(
        name__contains="🗑"
    ).exclude(
        name__contains="🤖"
    )
    
    cover_songs = CartiCatalog.objects.filter(
        name__contains="Cover"
    ).exclude(
        metadata__sheet_tab=released_tab
    ).exclude(
        name__contains="🏆"
    ).exclude(
        name__contains="🥇"
    ).exclude(
        name__contains="⭐"
    ).exclude(
        name__contains="✨"
    ).exclude(
        name__contains="🗑️"
    ).exclude(
        name__contains="🗑"
    ).exclude(
        name__contains="🤖"
    )
    
    art_songs = list(art_songs) + list(cover_songs)
    
    for song in art_songs:
        metadata, created = SongMetadata.objects.get_or_create(song=song)
        
        if metadata.sheet_tab != keyword_tabs["Art"]:
            old_tab = metadata.sheet_tab.name if metadata.sheet_tab else "None"
            metadata.sheet_tab = keyword_tabs["Art"]
            metadata.save()
            print(f"[KEYWORD] '{song.name}' from '{old_tab}' to 'Art'")
            updated += 1
            keyword_count += 1
        else:
            no_change += 1
    
    # Social Media
    social_songs = CartiCatalog.objects.filter(
        name__contains="Social Media"
    ).exclude(
        metadata__sheet_tab=released_tab
    ).exclude(
        name__contains="🏆"
    ).exclude(
        name__contains="🥇"
    ).exclude(
        name__contains="⭐"
    ).exclude(
        name__contains="✨"
    ).exclude(
        name__contains="🗑️"
    ).exclude(
        name__contains="🗑"
    ).exclude(
        name__contains="🤖"
    )
    
    instagram_songs = CartiCatalog.objects.filter(
        name__contains="Instagram"
    ).exclude(
        metadata__sheet_tab=released_tab
    ).exclude(
        name__contains="🏆"
    ).exclude(
        name__contains="🥇"
    ).exclude(
        name__contains="⭐"
    ).exclude(
        name__contains="✨"
    ).exclude(
        name__contains="🗑️"
    ).exclude(
        name__contains="🗑"
    ).exclude(
        name__contains="🤖"
    )
    
    twitter_songs = CartiCatalog.objects.filter(
        name__contains="Twitter"
    ).exclude(
        metadata__sheet_tab=released_tab
    ).exclude(
        name__contains="🏆"
    ).exclude(
        name__contains="🥇"
    ).exclude(
        name__contains="⭐"
    ).exclude(
        name__contains="✨"
    ).exclude(
        name__contains="🗑️"
    ).exclude(
        name__contains="🗑"
    ).exclude(
        name__contains="🤖"
    )
    
    social_songs = list(social_songs) + list(instagram_songs) + list(twitter_songs)
    
    for song in social_songs:
        metadata, created = SongMetadata.objects.get_or_create(song=song)
        
        if metadata.sheet_tab != keyword_tabs["Social Media"]:
            old_tab = metadata.sheet_tab.name if metadata.sheet_tab else "None"
            metadata.sheet_tab = keyword_tabs["Social Media"]
            metadata.save()
            print(f"[KEYWORD] '{song.name}' from '{old_tab}' to 'Social Media'")
            updated += 1
            keyword_count += 1
        else:
            no_change += 1
            
    # Fakes
    fakes_songs = CartiCatalog.objects.filter(
        name__contains="Fake"
    ).exclude(
        metadata__sheet_tab=released_tab
    ).exclude(
        name__contains="🏆"
    ).exclude(
        name__contains="🥇"
    ).exclude(
        name__contains="⭐"
    ).exclude(
        name__contains="✨"
    ).exclude(
        name__contains="🗑️"
    ).exclude(
        name__contains="🗑"
    ).exclude(
        name__contains="🤖"
    )
    
    ai_songs = CartiCatalog.objects.filter(
        name__contains="AI"
    ).exclude(
        metadata__sheet_tab=released_tab
    ).exclude(
        name__contains="🏆"
    ).exclude(
        name__contains="🥇"
    ).exclude(
        name__contains="⭐"
    ).exclude(
        name__contains="✨"
    ).exclude(
        name__contains="🗑️"
    ).exclude(
        name__contains="🗑"
    ).exclude(
        name__contains="🤖"
    )
    
    fakes_songs = list(fakes_songs) + list(ai_songs)
    
    for song in fakes_songs:
        metadata, created = SongMetadata.objects.get_or_create(song=song)
        
        if metadata.sheet_tab != keyword_tabs["Fakes"]:
            old_tab = metadata.sheet_tab.name if metadata.sheet_tab else "None"
            metadata.sheet_tab = keyword_tabs["Fakes"]
            metadata.save()
            print(f"[KEYWORD] '{song.name}' from '{old_tab}' to 'Fakes'")
            updated += 1
            keyword_count += 1
        else:
            no_change += 1
            
    # Tracklists
    tracklist_songs = CartiCatalog.objects.filter(
        name__contains="Tracklist"
    ).exclude(
        metadata__sheet_tab=released_tab
    ).exclude(
        name__contains="🏆"
    ).exclude(
        name__contains="🥇"
    ).exclude(
        name__contains="⭐"
    ).exclude(
        name__contains="✨"
    ).exclude(
        name__contains="🗑️"
    ).exclude(
        name__contains="🗑"
    ).exclude(
        name__contains="🤖"
    )
    
    for song in tracklist_songs:
        metadata, created = SongMetadata.objects.get_or_create(song=song)
        
        if metadata.sheet_tab != keyword_tabs["Tracklists"]:
            old_tab = metadata.sheet_tab.name if metadata.sheet_tab else "None"
            metadata.sheet_tab = keyword_tabs["Tracklists"]
            metadata.save()
            print(f"[KEYWORD] '{song.name}' from '{old_tab}' to 'Tracklists'")
            updated += 1
            keyword_count += 1
        else:
            no_change += 1
    
    print(f"Set {keyword_count} songs based on keywords/types")
    
    # Priority 4: Default to Unreleased
    default_count = 0
    
    # Get all tab names excluding Unreleased
    tab_names = []
    for tab in SheetTab.objects.exclude(name="Unreleased"):
        tab_names.append(tab.name)
    
    # Find songs that aren't in any of those tabs
    default_songs = CartiCatalog.objects.exclude(
        metadata__sheet_tab__name__in=tab_names
    )
    
    for song in default_songs:
        metadata, created = SongMetadata.objects.get_or_create(song=song)
        
        if metadata.sheet_tab != unreleased_tab:
            old_tab = metadata.sheet_tab.name if metadata.sheet_tab else "None"
            metadata.sheet_tab = unreleased_tab
            metadata.save()
            print(f"[DEFAULT] '{song.name}' from '{old_tab}' to 'Unreleased'")
            updated += 1
            default_count += 1
        else:
            no_change += 1
    
    print(f"Set {default_count} songs to default tab (Unreleased)")
    
    print(f"Finished processing sheetsdata.csv")
    print(f"Updated: {updated} songs")
    print(f"No change needed: {no_change} songs")
    print(f"Not found in database: {not_found} songs")

def force_released():
    """Force all songs with Single/Album Track type to Released tab"""
    print("Forcing all Single/Album Track songs to Released tab...")
    
    released_tab = SheetTab.objects.get(name="Released")
    updated = 0
    
    for song in CartiCatalog.objects.filter(type__in=["Single", "Album Track"]):
        metadata, created = SongMetadata.objects.get_or_create(song=song)
        
        if metadata.sheet_tab != released_tab:
            old_tab = metadata.sheet_tab.name if metadata.sheet_tab else "None"
            metadata.sheet_tab = released_tab
            metadata.save()
            print(f"Changed '{song.name}' from '{old_tab}' to 'Released'")
            updated += 1
    
    print(f"Updated {updated} songs to Released tab")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Reset tab assignments to match sheetsdata.csv')
    parser.add_argument('--force-released', action='store_true', help='Force all Single/Album Track songs to Released tab')
    args = parser.parse_args()
    
    if args.force_released:
        force_released()
    else:
        reset_tabs_from_csv()