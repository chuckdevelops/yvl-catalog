from django.core.management.base import BaseCommand
from catalog.models import CartiCatalog, SongMetadata, SheetTab, SongCategory
from django.db import transaction


class Command(BaseCommand):
    help = 'Updates Playboi Carti self-titled album tracks with proper formatting and "Album Track" badge'

    def handle(self, *args, **options):
        # Get or create the necessary tabs
        released_tab, _ = SheetTab.objects.get_or_create(name="Released")
        special_tab, _ = SheetTab.objects.get_or_create(name="✨ Special")
        best_of_tab, _ = SheetTab.objects.get_or_create(name="⭐ Best Of")
        worst_of_tab, _ = SheetTab.objects.get_or_create(name="🗑️ Worst Of")

        # Find or create the Self-Titled subsection
        selftitled_subsection = "Self-Titled"

        # Define the album tracks with their proper formatting
        selftitled_tracks = [
            {
                "name": "⭐ Location (prod. Harry Fraud)",
                "notes": "Track 1 off Playboi Carti's self titled album \"Playboi Carti\". Samples \"Endomorph\" by Holdsworth.",
                "track_length": "",
                "leak_date": "Apr 14, 2017",
                "file_date": "Album Track",
                "type": "Streaming",
                "links": "https://open.spotify.com/track/3yk7PJnryiJ8mAPqsrujzf?si=49a1882430524e96",
                "emoji_tabs": ["⭐"],
                "track_number": 1
            },
            {
                "name": "⭐ Magnolia (prod. Pi'erre Bourne)",
                "notes": "Track 2 off Playboi Carti's self titled album \"Playboi Carti\". Released as a single prior to the album release. The beat was made by Pi'erre in his car.",
                "track_length": "",
                "leak_date": "Apr 13, 2017",
                "file_date": "Album Track",
                "type": "Streaming",
                "links": "https://open.spotify.com/track/1e1JKLEDKP7hEQzJfNAgPl?si=31f2df0a1ada437d",
                "emoji_tabs": ["⭐"],
                "track_number": 2
            },
            {
                "name": "Lookin (feat. Lil Uzi Vert) (prod. Roark Bailey)",
                "notes": "Track 3 off Playboi Carti's self titled album \"Playboi Carti\". Released as a single prior to the album release.",
                "track_length": "",
                "leak_date": "Mar 10, 2017",
                "file_date": "Album Track",
                "type": "Streaming",
                "links": "https://open.spotify.com/track/1UAmQe8EwpxQ80OfYVD13z?si=cc9de6c1e2be42ac",
                "emoji_tabs": [],
                "track_number": 3
            },
            {
                "name": "⭐ wokeuplikethis* (feat. Lil Uzi Vert) (prod. Pi'erre Bourne)",
                "notes": "Track 4 off Playboi Carti's self titled album \"Playboi Carti\".",
                "track_length": "",
                "leak_date": "Mar 10, 2017",
                "file_date": "Album Track",
                "type": "Streaming",
                "links": "https://open.spotify.com/track/59J5nzL1KniFHnU120dQzt?si=35375ee3c6274e2d",
                "emoji_tabs": ["⭐"],
                "track_number": 4
            },
            {
                "name": "⭐ Let It Go (prod. Pi'erre Bourne)",
                "notes": "Track 5 off Playboi Carti's self titled album \"Playboi Carti\". Features uncredited background vocals by MexikoDro.",
                "track_length": "",
                "leak_date": "Apr 14, 2017",
                "file_date": "Album Track",
                "type": "Streaming",
                "links": "https://open.spotify.com/track/23QyE9GQpXsX9WgEDADMa6?si=7f1d5beda2fd4b44",
                "emoji_tabs": ["⭐"],
                "track_number": 5
            },
            {
                "name": "Half & Half (prod. Southside, K-Major & Murphy Kid)",
                "notes": "Track 6 off Playboi Carti's self titled album \"Playboi Carti\".",
                "track_length": "",
                "leak_date": "Apr 14, 2017",
                "file_date": "Album Track",
                "type": "Streaming",
                "links": "https://open.spotify.com/track/2TdZdeKIDMqi1B3139W4Wb?si=840435602bbc4a52",
                "emoji_tabs": [],
                "track_number": 6
            },
            {
                "name": "⭐ New Choppa (feat. A$AP Rocky) (prod. Ricci Riera)",
                "notes": "Track 7 off Playboi Carti's self titled album \"Playboi Carti\".",
                "track_length": "",
                "leak_date": "Apr 14, 2017",
                "file_date": "Album Track",
                "type": "Streaming",
                "links": "https://open.spotify.com/track/30sc425JEvj3tgmGAKORea?si=df3dd27ea2794c31",
                "emoji_tabs": ["⭐"],
                "track_number": 7
            },
            {
                "name": "Other Shit (prod. Hit-Boy)",
                "notes": "Track 8 off Playboi Carti's self titled album \"Playboi Carti\".",
                "track_length": "",
                "leak_date": "Apr 14, 2017",
                "file_date": "Album Track",
                "type": "Streaming",
                "links": "https://open.spotify.com/track/1KsfhDZbBY2JjTHLmYhkK1?si=168c030cc7594a03",
                "emoji_tabs": [],
                "track_number": 8
            },
            {
                "name": "NO.9 (prod. JStewOnTheBeat)",
                "notes": "Track 9 off Playboi Carti's self titled album \"Playboi Carti\".",
                "track_length": "",
                "leak_date": "Apr 14, 2017",
                "file_date": "Album Track",
                "type": "Streaming",
                "links": "https://open.spotify.com/track/5Nq6lLSxphlsA6nQB0KtES?si=c6f44e824f5548d8",
                "emoji_tabs": [],
                "track_number": 9
            },
            {
                "name": "dothatshit! (prod. Pi'erre Bourne)",
                "notes": "Track 10 off Playboi Carti's self titled album \"Playboi Carti\".",
                "track_length": "",
                "leak_date": "Apr 14, 2017",
                "file_date": "Album Track",
                "type": "Streaming",
                "links": "https://open.spotify.com/track/1KzNsOkpQthVwpCJrADJEQ?si=aa562acb2ce5425f",
                "emoji_tabs": [],
                "track_number": 10
            },
            {
                "name": "🗑️ Lame Niggaz (prod. Pi'erre Bourne)",
                "notes": "Track 11 off Playboi Carti's self titled album \"Playboi Carti\".",
                "track_length": "",
                "leak_date": "Apr 14, 2017",
                "file_date": "Album Track",
                "type": "Streaming",
                "links": "https://open.spotify.com/track/1xUQwXDDKW79z7GRUt2vMW?si=9e7ae4beacc64f51",
                "emoji_tabs": ["🗑️"],
                "track_number": 11
            },
            {
                "name": "⭐ Yah Mean (prod. Pi'erre Bourne)",
                "notes": "Track 12 off Playboi Carti's self titled album \"Playboi Carti\".",
                "track_length": "",
                "leak_date": "Apr 14, 2017",
                "file_date": "Album Track",
                "type": "Streaming",
                "links": "https://open.spotify.com/track/5MUxrNd7Gr2HksLcAlB0IO?si=1d40366534f249ae",
                "emoji_tabs": ["⭐"],
                "track_number": 12
            },
            {
                "name": "⭐ Flex (feat. Leven Kali) (prod. KasimGotJuice & J. Cash Beatz)",
                "notes": "Track 13 off Playboi Carti's self titled album \"Playboi Carti\".",
                "track_length": "",
                "leak_date": "Apr 14, 2017",
                "file_date": "Album Track",
                "type": "Streaming",
                "links": "https://open.spotify.com/track/2xyBvir9n474qfsOkxXMgx?si=751d76a513a24593",
                "emoji_tabs": ["⭐"],
                "track_number": 13
            },
            {
                "name": "⭐ Kelly K (prod. Southside & Jake One)",
                "notes": "Track 14 off Playboi Carti's self titled album \"Playboi Carti\". Features uncredited additional background vocals by Blakk Soul.",
                "track_length": "",
                "leak_date": "Apr 14, 2017",
                "file_date": "Album Track",
                "type": "Streaming",
                "links": "https://open.spotify.com/track/3hDp5jRxvtD31giFGUaE1x?si=8a10531f2d5e44e5",
                "emoji_tabs": ["⭐"],
                "track_number": 14
            },
            {
                "name": "⭐ Had 2 (prod. MexikoDro)",
                "notes": "Track 15 off Playboi Carti's self titled album \"Playboi Carti\".",
                "track_length": "",
                "leak_date": "Apr 14, 2017",
                "file_date": "Album Track",
                "type": "Streaming",
                "links": "https://open.spotify.com/track/2mkV4angeBLZPTcYOSrjee?si=0d9a5d43f6844fc3",
                "emoji_tabs": ["⭐"],
                "track_number": 15
            }
        ]

        with transaction.atomic():
            total_updated = 0
            total_created = 0
            
            for track_data in selftitled_tracks:
                # Prepare search parameters
                search_name = track_data["name"]
                base_name = search_name.replace("⭐ ", "").replace("✨ ", "").replace("🗑️ ", "")
                track_num = track_data["track_number"]
                
                # Search for:
                # 1. Exact name match
                # 2. Base name match (without emoji)
                # 3. Simple name match (looking for the main title)
                exact_matches = CartiCatalog.objects.filter(name=search_name, era="Self-Titled")
                base_matches = CartiCatalog.objects.filter(name=base_name, era="Self-Titled")
                
                # Extract the main song name without producer/feature info
                import re
                main_title = re.split(r'\s*\(', search_name)[0].strip()
                main_title = main_title.replace("⭐ ", "").replace("✨ ", "").replace("🗑️ ", "")
                
                simple_matches = CartiCatalog.objects.filter(
                    name__icontains=main_title,
                    era="Self-Titled"
                )
                
                # Also look for matches based on track number in notes
                track_matches = CartiCatalog.objects.filter(
                    notes__icontains=f"Track {track_num}",
                    era="Self-Titled"
                )
                
                # Find the best match - prioritize different match types
                existing_song = None
                
                if exact_matches.exists():
                    existing_song = exact_matches.first()
                    self.stdout.write(self.style.WARNING(f"Found exact match for '{search_name}'"))
                elif base_matches.exists():
                    existing_song = base_matches.first()
                    self.stdout.write(self.style.WARNING(f"Found base match for '{search_name}'"))
                elif track_matches.exists():
                    existing_song = track_matches.first()
                    self.stdout.write(self.style.WARNING(f"Found track number match for '{search_name}'"))
                elif simple_matches.exists():
                    existing_song = simple_matches.first()
                    self.stdout.write(self.style.WARNING(f"Found simple match for '{search_name}'"))
                
                if existing_song:
                    # Update the existing song
                    old_name = existing_song.name
                    existing_song.name = track_data["name"]
                    existing_song.notes = track_data["notes"]
                    if track_data["track_length"]:
                        existing_song.track_length = track_data["track_length"]
                    existing_song.leak_date = track_data["leak_date"]
                    existing_song.file_date = track_data["file_date"]
                    existing_song.type = track_data["type"]
                    existing_song.links = track_data["links"]
                    existing_song.save()
                    
                    self.stdout.write(self.style.SUCCESS(f"Updated song: {old_name} -> {track_data['name']}"))
                    total_updated += 1
                else:
                    # Create a new song
                    new_song = CartiCatalog.objects.create(
                        era="Self-Titled",
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
                            'subsection': selftitled_subsection
                        }
                    )
                    
                    if not created:
                        metadata.sheet_tab = released_tab
                        metadata.subsection = selftitled_subsection
                        metadata.save()
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"Error updating metadata for {track_data['name']}: {str(e)}"))
                
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
            
            self.stdout.write(self.style.SUCCESS(
                f"Self-Titled album tracks update complete: {total_updated} updated, {total_created} created"
            ))