from django.core.management.base import BaseCommand
from catalog.models import CartiCatalog, SongMetadata, SheetTab, SongCategory
from django.db import transaction


class Command(BaseCommand):
    help = 'Updates Whole Lotta Red album tracks with proper formatting and "Album Track" badge'

    def handle(self, *args, **options):
        # Get or create the necessary tabs
        released_tab, _ = SheetTab.objects.get_or_create(name="Released")
        special_tab, _ = SheetTab.objects.get_or_create(name="✨ Special")
        best_of_tab, _ = SheetTab.objects.get_or_create(name="⭐ Best Of")
        worst_of_tab, _ = SheetTab.objects.get_or_create(name="🗑️ Worst Of")

        # Find or create the Whole Lotta Red subsection
        wlr_subsection = "Whole Lotta Red"

        # Define the album tracks with their proper formatting
        wlr_tracks = [
            {
                "name": "⭐ Rockstar Made (prod. F1LTHY & Jonah Abraham)",
                "notes": "Track 1 off Playboi Carti's album \"Whole Lotta Red\".",
                "track_length": "3:13",
                "leak_date": "Dec 25, 2020",
                "file_date": "Album Track",
                "type": "Streaming",
                "links": "https://open.spotify.com/track/3cWmqvMwVQKDigWLSZ3w9h?si=339968d7f99e46a4",
                "emoji_tabs": ["⭐"],
                "track_number": 1
            },
            {
                "name": "✨ Go2DaMoon (feat. Ye) (prod. Wheezy)",
                "notes": "Track 2 off Playboi Carti's album \"Whole Lotta Red\". Contains an uncredited sample from \"Soul of Bobby Theme, Pt. 2\" by Laxmikant-Pyarelal. Ye carries hard",
                "track_length": "1:59",
                "leak_date": "Dec 25, 2020",
                "file_date": "Album Track",
                "type": "Streaming",
                "links": "https://open.spotify.com/track/0F13K9dwYH2zpTWiR8d628?si=50b58281168d411a",
                "emoji_tabs": ["✨"],
                "track_number": 2
            },
            {
                "name": "⭐ Stop Breathing (prod. F1LTHY, Lukrative & ssort)",
                "notes": "Track 3 off Playboi Carti's album \"Whole Lotta Red\".",
                "track_length": "3:38",
                "leak_date": "Dec 25, 2020",
                "file_date": "Album Track",
                "type": "Streaming",
                "links": "https://open.spotify.com/track/2lLG56qpLP3UbcLuzMvkWX?si=227f78d3119a4e3a",
                "emoji_tabs": ["⭐"],
                "track_number": 3
            },
            {
                "name": "Beno! (prod. Outtatown & Lil88)",
                "notes": "Track 4 off Playboi Carti's album \"Whole Lotta Red\".",
                "track_length": "2:33",
                "leak_date": "Dec 25, 2020",
                "file_date": "Album Track",
                "type": "Streaming",
                "links": "https://open.spotify.com/track/4CYTQpr2jc4uBScYvpEK2w?si=fa7a46fe23354645",
                "emoji_tabs": [],
                "track_number": 4
            },
            {
                "name": "🗑️ JumpOutTheHouse (prod. Richie Souf)",
                "notes": "Track 5 off Playboi Carti's album \"Whole Lotta Red\".",
                "track_length": "1:33",
                "leak_date": "Dec 25, 2020",
                "file_date": "Album Track",
                "type": "Streaming",
                "links": "https://open.spotify.com/track/0cgD36xPIJBdKUNJRHYDgP?si=064dd1f99ea14ee4",
                "emoji_tabs": ["🗑️"],
                "track_number": 5
            },
            {
                "name": "🗑️ M3tamorphosis (feat. Kid Cudi) (prod. F1LTHY & Gab3)",
                "notes": "Track 6 off Playboi Carti's album \"Whole Lotta Red\".",
                "track_length": "5:12",
                "leak_date": "Dec 25, 2020",
                "file_date": "Album Track",
                "type": "Streaming",
                "links": "https://open.spotify.com/track/7zLMYtNJcabv4h4wBnjNQI?si=07188dc454644fd3",
                "emoji_tabs": ["🗑️"],
                "track_number": 6
            },
            {
                "name": "⭐ Slay3r (prod. Juberlee & Roark Bailey)",
                "notes": "Track 7 off Playboi Carti's album \"Whole Lotta Red\".",
                "track_length": "2:44",
                "leak_date": "Dec 25, 2020",
                "file_date": "Album Track",
                "type": "Streaming",
                "links": "https://open.spotify.com/track/1eMNW1HQjF1dbb4GtnmpaX?si=f55f111889af41ea",
                "emoji_tabs": ["⭐"],
                "track_number": 7
            },
            {
                "name": "🗑️ No Sl33p (prod. KP & Jonah Abraham)",
                "notes": "Track 8 off Playboi Carti's album \"Whole Lotta Red\".",
                "track_length": "1:28",
                "leak_date": "Dec 25, 2020",
                "file_date": "Album Track",
                "type": "Streaming",
                "links": "https://open.spotify.com/track/6i6whmV36EJmxs5zFahMrb?si=4bb90630a7fe4c82",
                "emoji_tabs": ["🗑️"],
                "track_number": 8
            },
            {
                "name": "⭐ New Tank (prod. F1LTHY & Jonah Abraham)",
                "notes": "Track 9 off Playboi Carti's album \"Whole Lotta Red\".",
                "track_length": "1:29",
                "leak_date": "Dec 25, 2020",
                "file_date": "Album Track",
                "type": "Streaming",
                "links": "https://open.spotify.com/track/4txKMpsSfZRV6durPuHVq0?si=f2e264dd9d1a4d15",
                "emoji_tabs": ["⭐"],
                "track_number": 9
            },
            {
                "name": "✨ Teen X (feat. Future) (prod. Maaly Raw)",
                "notes": "Track 10 off Playboi Carti's album \"Whole Lotta Red\".",
                "track_length": "3:25",
                "leak_date": "Dec 25, 2020",
                "file_date": "Album Track",
                "type": "Streaming",
                "links": "https://open.spotify.com/track/5uYqmEN6TAAE8ss8YmprNV?si=d22053c8d57f45ef",
                "emoji_tabs": ["✨"],
                "track_number": 10
            },
            {
                "name": "🗑️ Meh (prod. Outtatown, Art Dealer & star boy)",
                "notes": "Track 11 off Playboi Carti's album \"Whole Lotta Red\".",
                "track_length": "1:58",
                "leak_date": "Dec 25, 2020",
                "file_date": "Album Track",
                "type": "Streaming",
                "links": "https://open.spotify.com/track/15JRvf02KKGHKgC31jrpuh?si=4eb9715abf60417e",
                "emoji_tabs": ["🗑️"],
                "track_number": 11
            },
            {
                "name": "Vamp Anthem (prod. KP & Jasper Harris)",
                "notes": "Track 12 off Playboi Carti's album \"Whole Lotta Red\".",
                "track_length": "2:04",
                "leak_date": "Dec 25, 2020",
                "file_date": "Album Track",
                "type": "Streaming",
                "links": "https://open.spotify.com/track/4CzhtKifG867Lu5DNQVBSA?si=2908409c74c744f3",
                "emoji_tabs": [],
                "track_number": 12
            },
            {
                "name": "⭐ New N3on (prod. Maaly Raw)",
                "notes": "Track 13 off Playboi Carti's album \"Whole Lotta Red\".",
                "track_length": "1:56",
                "leak_date": "Dec 25, 2020",
                "file_date": "Album Track",
                "type": "Streaming",
                "links": "https://open.spotify.com/track/7ejepEh5DJ79YI6owGRfkk?si=2de75c9cd59e4139",
                "emoji_tabs": ["⭐"],
                "track_number": 13
            },
            {
                "name": "✨ Control (prod. Outtatown, Art Dealer & star boy)",
                "notes": "Track 14 off Playboi Carti's album \"Whole Lotta Red\". Features an uncredited sample by DJ Akademiks.",
                "track_length": "3:17",
                "leak_date": "Dec 25, 2020",
                "file_date": "Album Track",
                "type": "Streaming",
                "links": "https://open.spotify.com/track/78YTl0P96kBCBXUSzKoqAm?si=c2702133a2d44e1e",
                "emoji_tabs": ["✨"],
                "track_number": 14
            },
            {
                "name": "🗑️ Punk Monk (prod. F1LTHY, Lucian & Lukrative)",
                "notes": "Track 15 off Playboi Carti's album \"Whole Lotta Red\".",
                "track_length": "3:49",
                "leak_date": "Dec 25, 2020",
                "file_date": "Album Track",
                "type": "Streaming",
                "links": "https://open.spotify.com/track/5fSZXFOZfPVW9gvnnG4ZVW?si=62bd6aee3caa4400",
                "emoji_tabs": ["🗑️"],
                "track_number": 15
            },
            {
                "name": "⭐ On That Time (prod. F1LTHY & Ojivolta)",
                "notes": "Track 16 off Playboi Carti's album \"Whole Lotta Red\".",
                "track_length": "1:42",
                "leak_date": "Dec 25, 2020",
                "file_date": "Album Track",
                "type": "Streaming",
                "links": "https://open.spotify.com/track/3dl8bSF08LQfCf4T6CCksf?si=567f21d558964518",
                "emoji_tabs": ["⭐"],
                "track_number": 16
            },
            {
                "name": "✨ King Vamp (prod. Outtatown, Art Dealer & star boy)",
                "notes": "Track 17 off Playboi Carti's album \"Whole Lotta Red\".",
                "track_length": "3:06",
                "leak_date": "Dec 25, 2020",
                "file_date": "Album Track",
                "type": "Streaming",
                "links": "https://open.spotify.com/track/2iqHcRoOfLl1fXCf1bGO0J?si=55bdeb7533724b3f",
                "emoji_tabs": ["✨"],
                "track_number": 17
            },
            {
                "name": "Place (prod. Pi'erre Bourne)",
                "notes": "Track 18 off Playboi Carti's album \"Whole Lotta Red\".",
                "track_length": "1:57",
                "leak_date": "Dec 25, 2020",
                "file_date": "Album Track",
                "type": "Streaming",
                "links": "https://open.spotify.com/track/1Bg2CNZw6S4e9cGWPmi0uI?si=9927eed0d4e8471d",
                "emoji_tabs": [],
                "track_number": 18
            },
            {
                "name": "⭐ Sky (prod. Art Dealer)",
                "notes": "Track 19 off Playboi Carti's album \"Whole Lotta Red\".",
                "track_length": "3:13",
                "leak_date": "Dec 25, 2020",
                "file_date": "Album Track",
                "type": "Streaming",
                "links": "https://open.spotify.com/track/29TPjc8wxfz4XMn21O7VsZ?si=ea2d8348e2fd44ba",
                "emoji_tabs": ["⭐"],
                "track_number": 19
            },
            {
                "name": "⭐ Over (prod. Art Dealer)",
                "notes": "Track 20 off Playboi Carti's album \"Whole Lotta Red\".",
                "track_length": "2:46",
                "leak_date": "Dec 25, 2020",
                "file_date": "Album Track",
                "type": "Streaming",
                "links": "https://open.spotify.com/track/08dz3ygXyFur6bL7Au8u8J?si=44dc3b1887a049ae",
                "emoji_tabs": ["⭐"],
                "track_number": 20
            },
            {
                "name": "⭐ ILoveUIHateU (prod. Pi'erre Bourne)",
                "notes": "Track 21 off Playboi Carti's album \"Whole Lotta Red\".",
                "track_length": "2:15",
                "leak_date": "Dec 25, 2020",
                "file_date": "Album Track",
                "type": "Streaming",
                "links": "https://open.spotify.com/track/1BpKJw4RZxaFB88NE5uxXf?si=554a88b42f504a9b",
                "emoji_tabs": ["⭐"],
                "track_number": 21
            },
            {
                "name": "✨ Die4Guy (prod. Outtatown, Art Dealer & star boy)",
                "notes": "Track 22 off Playboi Carti's album \"Whole Lotta Red\".",
                "track_length": "2:11",
                "leak_date": "Dec 25, 2020",
                "file_date": "Album Track",
                "type": "Streaming",
                "links": "https://open.spotify.com/track/7rbalRuIx7sIXFHYTphE0n?si=294a9f1365e74c77",
                "emoji_tabs": ["✨"],
                "track_number": 22
            },
            {
                "name": "⭐ Not PLaying (prod. Art Dealer)",
                "notes": "Track 23 off Playboi Carti's album \"Whole Lotta Red\".",
                "track_length": "2:10",
                "leak_date": "Dec 25, 2020",
                "file_date": "Album Track",
                "type": "Streaming",
                "links": "https://open.spotify.com/track/03rcC8SVxCa9UdY5qgkITe?si=5d4b22fd6c2b4ad0",
                "emoji_tabs": ["⭐"],
                "track_number": 23
            },
            {
                "name": "F33l Lik3 Dyin (prod. Richie Souf & Roark Bailey)",
                "notes": "Track 24 off Playboi Carti's album \"Whole Lotta Red\". Samples \"iMi\" by Bon Iver.",
                "track_length": "3:24",
                "leak_date": "Dec 25, 2020",
                "file_date": "Album Track",
                "type": "Streaming",
                "links": "https://open.spotify.com/track/1xVVYE1ahLotRpppJViVzs?si=56d6ffa39ce64884",
                "emoji_tabs": [],
                "track_number": 24
            }
        ]

        with transaction.atomic():
            total_updated = 0
            total_created = 0
            
            for track_data in wlr_tracks:
                # Prepare search parameters
                search_name = track_data["name"]
                base_name = search_name.replace("⭐ ", "").replace("✨ ", "").replace("🗑️ ", "")
                track_num = track_data["track_number"]
                
                # Search for existing tracks in different ways
                # First try to find exact match with Whole Lotta Red era
                exact_matches = CartiCatalog.objects.filter(name=search_name, era="Whole Lotta Red")
                
                # Also try with Whole Lotta Red [V4] era as that's the format used in the input
                exact_matches_v4 = CartiCatalog.objects.filter(name=search_name, era="Whole Lotta Red [V4]")
                
                # Try base name match (without emoji) with both eras
                base_matches = CartiCatalog.objects.filter(name=base_name, era="Whole Lotta Red")
                base_matches_v4 = CartiCatalog.objects.filter(name=base_name, era="Whole Lotta Red [V4]")
                
                # Extract the main song name without producer/feature info
                import re
                main_title = re.split(r'\s*\(', search_name)[0].strip()
                main_title = main_title.replace("⭐ ", "").replace("✨ ", "").replace("🗑️ ", "")
                
                # Look for simple matches with both eras
                simple_matches = CartiCatalog.objects.filter(
                    name__icontains=main_title,
                    era__in=["Whole Lotta Red", "Whole Lotta Red [V4]"]
                )
                
                # Also look for matches based on track number in notes
                track_matches = CartiCatalog.objects.filter(
                    notes__icontains=f"Track {track_num}",
                    era__in=["Whole Lotta Red", "Whole Lotta Red [V4]"]
                )
                
                # Find the best match - prioritize different match types
                existing_song = None
                match_source = ""
                
                if exact_matches.exists():
                    existing_song = exact_matches.first()
                    match_source = "exact match (WLR)"
                elif exact_matches_v4.exists():
                    existing_song = exact_matches_v4.first()
                    match_source = "exact match (WLR V4)"
                elif base_matches.exists():
                    existing_song = base_matches.first()
                    match_source = "base match (WLR)"
                elif base_matches_v4.exists():
                    existing_song = base_matches_v4.first()
                    match_source = "base match (WLR V4)"
                elif track_matches.exists():
                    existing_song = track_matches.first()
                    match_source = "track number match"
                elif simple_matches.exists():
                    existing_song = simple_matches.first()
                    match_source = "simple match"
                
                if existing_song:
                    # Update the existing song
                    old_name = existing_song.name
                    old_era = existing_song.era
                    
                    # Standardize era to "Whole Lotta Red" (without [V4])
                    existing_song.era = "Whole Lotta Red"
                    existing_song.name = track_data["name"]
                    existing_song.notes = track_data["notes"]
                    existing_song.track_length = track_data["track_length"]
                    existing_song.leak_date = track_data["leak_date"]
                    existing_song.file_date = track_data["file_date"]
                    existing_song.type = track_data["type"]
                    existing_song.links = track_data["links"]
                    existing_song.save()
                    
                    self.stdout.write(self.style.SUCCESS(f"Updated song from {match_source}: {old_name} ({old_era}) -> {track_data['name']} (Whole Lotta Red)"))
                    total_updated += 1
                else:
                    # Create a new song
                    new_song = CartiCatalog.objects.create(
                        era="Whole Lotta Red",
                        name=track_data["name"],
                        notes=track_data["notes"],
                        track_length=track_data["track_length"],
                        leak_date=track_data["leak_date"],
                        file_date=track_data["file_date"],
                        type=track_data["type"],
                        links=track_data["links"]
                    )
                    self.stdout.write(self.style.SUCCESS(f"Created new song: {track_data['name']}"))
                    existing_song = new_song
                    total_created += 1
                
                # Make sure it has the proper metadata
                try:
                    metadata, created = SongMetadata.objects.get_or_create(
                        song=existing_song,
                        defaults={
                            'sheet_tab': released_tab,
                            'subsection': wlr_subsection
                        }
                    )
                    
                    if not created:
                        metadata.sheet_tab = released_tab
                        metadata.subsection = wlr_subsection
                        metadata.save()
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"Error updating metadata for {track_data['name']}: {str(e)}"))
                
                # Remove any existing categories to avoid duplicates
                try:
                    existing_song.categories.all().delete()
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"Error removing existing categories for {track_data['name']}: {str(e)}"))
                
                # Add emoji category tabs
                for emoji in track_data["emoji_tabs"]:
                    try:
                        if emoji == "⭐":
                            SongCategory.objects.get_or_create(song=existing_song, sheet_tab=best_of_tab)
                        elif emoji == "✨":
                            SongCategory.objects.get_or_create(song=existing_song, sheet_tab=special_tab)
                        elif emoji == "🗑️":
                            SongCategory.objects.get_or_create(song=existing_song, sheet_tab=worst_of_tab)
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f"Error adding category for {track_data['name']}: {str(e)}"))
            
            # After all tracks are processed, remove any duplicate tracks
            # Find possible duplicates by track number to clean up
            for track_num in range(1, 25):
                dupes = CartiCatalog.objects.filter(
                    notes__icontains=f"Track {track_num} off Playboi Carti's album \"Whole Lotta Red\"",
                    era__in=["Whole Lotta Red", "Whole Lotta Red [V4]"]
                )
                
                if dupes.count() > 1:
                    # Keep the first one (which should be the updated one) and delete the rest
                    to_keep = dupes.first()
                    for dupe in dupes[1:]:
                        self.stdout.write(self.style.WARNING(f"Removing duplicate track {track_num}: {dupe.name}"))
                        dupe.delete()
            
            self.stdout.write(self.style.SUCCESS(
                f"Whole Lotta Red album tracks update complete: {total_updated} updated, {total_created} created"
            ))