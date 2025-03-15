from django.core.management.base import BaseCommand
from catalog.models import CartiCatalog, SongMetadata, SheetTab, SongCategory
from django.db import transaction


class Command(BaseCommand):
    help = 'Updates Die Lit album tracks with proper formatting and "Album Track" badge'

    def handle(self, *args, **options):
        # Get or create the necessary tabs
        released_tab, _ = SheetTab.objects.get_or_create(name="Released")
        special_tab, _ = SheetTab.objects.get_or_create(name="✨ Special")
        best_of_tab, _ = SheetTab.objects.get_or_create(name="⭐ Best Of")
        worst_of_tab, _ = SheetTab.objects.get_or_create(name="🗑️ Worst Of")

        # Find or create the Die Lit subsection
        die_lit_subsection = "Die Lit"

        # Define the album tracks with their proper formatting
        die_lit_tracks = [
            {
                "name": "⭐ Love Hurts (feat. Travis Scott) (prod. Pi'erre Bourne & Playboi Carti)",
                "notes": "Track 5 off Playboi Carti's album \"Die Lit\". Released on SoundCloud as a single.",
                "track_length": "",
                "leak_date": "May 3, 2018",
                "file_date": "Album Track",
                "type": "Streaming",
                "links": "https://open.spotify.com/track/3K6U7TamNyVSWcFH8pCQHX?si=433c9bc5f9cd4f95",
                "emoji_tabs": ["⭐"],
                "track_number": 5
            },
            {
                "name": "⭐ Long Time - Intro (prod. Art Dealer)",
                "notes": "Track 1 off Playboi Carti's album \"Die Lit\".",
                "track_length": "",
                "leak_date": "May 11, 2018",
                "file_date": "Album Track",
                "type": "Streaming",
                "links": "https://open.spotify.com/track/4IO2X2YoXoUMv0M2rwomLC?si=adc59ae02a1344bb",
                "emoji_tabs": ["⭐"],
                "track_number": 1
            },
            {
                "name": "⭐ R.I.P. (prod. Pi'erre Bourne)",
                "notes": "Track 2 off Playboi Carti's album \"Die Lit\". Samples \"What About Us\" by Jodeci.",
                "track_length": "",
                "leak_date": "May 11, 2018",
                "file_date": "Album Track",
                "type": "Streaming",
                "links": "https://open.spotify.com/track/3L0IKstjUgDFVQAbQIRZRv?si=31ecf193f2ea479e",
                "emoji_tabs": ["⭐"],
                "track_number": 2
            },
            {
                "name": "⭐ Lean 4 Real (feat. Skepta) (prod. IndigoChildRick)",
                "notes": "Track 3 off Playboi Carti's album \"Die Lit\".",
                "track_length": "",
                "leak_date": "May 11, 2018",
                "file_date": "Album Track",
                "type": "Streaming",
                "links": "https://open.spotify.com/track/1JgkiUg9mSXSwcb5Gbi4Ur?si=15db581cd7094597",
                "emoji_tabs": ["⭐"],
                "track_number": 3
            },
            {
                "name": "⭐ Old Money (prod. Pi'erre Bourne)",
                "notes": "Track 4 off Playboi Carti's album \"Die Lit\".",
                "track_length": "",
                "leak_date": "May 11, 2018",
                "file_date": "Album Track",
                "type": "Streaming",
                "links": "https://open.spotify.com/track/0syXbGoFZbTMXm8hGCEvW0?si=cbd013f85b494d2e",
                "emoji_tabs": ["⭐"],
                "track_number": 4
            },
            {
                "name": "⭐ Shoota (feat. Lil Uzi Vert) (prod. Maaly Raw)",
                "notes": "Track 6 off Playboi Carti's album \"Die Lit\".",
                "track_length": "",
                "leak_date": "May 11, 2018",
                "file_date": "Album Track",
                "type": "Streaming",
                "links": "https://open.spotify.com/track/2BJSMvOGABRxokHKB0OI8i?si=7be52ea5f5fd48da",
                "emoji_tabs": ["⭐"],
                "track_number": 6
            },
            {
                "name": "⭐ Right Now (feat. Pi'erre Bourne) (prod. Pi'erre Bourne)",
                "notes": "Track 7 off Playboi Carti's album \"Die Lit\".",
                "track_length": "",
                "leak_date": "May 11, 2018",
                "file_date": "Album Track",
                "type": "Streaming",
                "links": "https://open.spotify.com/track/475jSz0H6U3duJyNiDS0tT?si=ba78ab27bdf74f56",
                "emoji_tabs": ["⭐"],
                "track_number": 7
            },
            {
                "name": "🗑️ Poke It Out (feat. Nicki Minaj) (prod. Pi'erre Bourne)",
                "notes": "Track 8 off Playboi Carti's album \"Die Lit\".",
                "track_length": "",
                "leak_date": "May 11, 2018",
                "file_date": "Album Track",
                "type": "Streaming",
                "links": "https://open.spotify.com/track/2rPSFKzGeqUWwfcCFVkkq3?si=0afd46c045864fd0",
                "emoji_tabs": ["🗑️"],
                "track_number": 8
            },
            {
                "name": "✨ Home (KOD) (prod. Pi'erre Bourne)",
                "notes": "Track 9 off Playboi Carti's album \"Die Lit\".",
                "track_length": "",
                "leak_date": "May 11, 2018",
                "file_date": "Album Track",
                "type": "Streaming",
                "links": "https://open.spotify.com/track/5wPyd3IQAZft1vmxoIqGrU?si=8819e8b4c3c4428d",
                "emoji_tabs": ["✨"],
                "track_number": 9
            },
            {
                "name": "⭐ Fell In Luv (feat. Bryson Tiller) (prod. Pi'erre Bourne)",
                "notes": "Track 10 off Playboi Carti's album \"Die Lit\". Samples \"Grandloves\" by Purity Love.",
                "track_length": "",
                "leak_date": "May 11, 2018",
                "file_date": "Album Track",
                "type": "Streaming",
                "links": "https://open.spotify.com/track/1s9DTymg5UQrdorZf43JQm?si=3316d678d4d64de9",
                "emoji_tabs": ["⭐"],
                "track_number": 10
            },
            {
                "name": "✨ Foreign (prod. Pi'erre Bourne)",
                "notes": "Track 11 off Playboi Carti's album \"Die Lit\".",
                "track_length": "",
                "leak_date": "May 11, 2018",
                "file_date": "Album Track",
                "type": "Streaming",
                "links": "https://open.spotify.com/track/500l6Cwe40hkPqS7Sf7ufY?si=ecbdd18947b344d9",
                "emoji_tabs": ["✨"],
                "track_number": 11
            },
            {
                "name": "Pull Up (prod. Pi'erre Bourne)",
                "notes": "Track 12 off Playboi Carti's album \"Die Lit\".",
                "track_length": "",
                "leak_date": "May 11, 2018",
                "file_date": "Album Track",
                "type": "Streaming",
                "links": "https://open.spotify.com/track/424qpX6swdUdhLq95cecNu?si=16d8006950c54799",
                "emoji_tabs": [],
                "track_number": 12
            },
            {
                "name": "Mileage (feat. Chief Keef) (prod. Pi'erre Bourne)",
                "notes": "Track 13 off Playboi Carti's album \"Die Lit\".",
                "track_length": "",
                "leak_date": "May 11, 2018",
                "file_date": "Album Track",
                "type": "Streaming",
                "links": "https://open.spotify.com/track/1oNcc2isuz7d3hc1fMoHqj?si=1629c5b37b7e4dce",
                "emoji_tabs": [],
                "track_number": 13
            },
            {
                "name": "⭐ FlatBed Freestyle (prod. Pi'erre Bourne)",
                "notes": "Track 14 off Playboi Carti's album \"Die Lit\".",
                "track_length": "",
                "leak_date": "May 11, 2018",
                "file_date": "Album Track",
                "type": "Streaming",
                "links": "https://open.spotify.com/track/5nayhWICkQGMTkisxVMbRw?si=64559815b479426f",
                "emoji_tabs": ["⭐"],
                "track_number": 14
            },
            {
                "name": "✨ No Time (feat. Gunna) (prod. Don Cannon)",
                "notes": "Track 15 off Playboi Carti's album \"Die Lit\".",
                "track_length": "",
                "leak_date": "May 11, 2018",
                "file_date": "Album Track",
                "type": "Streaming",
                "links": "https://open.spotify.com/track/5pHJv0bgNsT9nPoK2BjNBn?si=65c90b905a6b4970",
                "emoji_tabs": ["✨"],
                "track_number": 15
            },
            {
                "name": "✨ Middle Of The Summer (feat. Red Coldhearted) (prod. Pi'erre Bourne)",
                "notes": "Track 16 off Playboi Carti's album \"Die Lit\". Samples \"Let It Go\".",
                "track_length": "",
                "leak_date": "May 11, 2018",
                "file_date": "Album Track",
                "type": "Streaming",
                "links": "https://open.spotify.com/track/7AtBtwrKhz94hYXgGYyG58?si=3cbb602f3691437c",
                "emoji_tabs": ["✨"],
                "track_number": 16
            },
            {
                "name": "⭐ Choppa Won't Miss (feat. Young Thug) (prod. Pi'erre Bourne)",
                "notes": "Track 17 off Playboi Carti's album \"Die Lit\".",
                "track_length": "",
                "leak_date": "May 11, 2018",
                "file_date": "Album Track",
                "type": "Streaming",
                "links": "https://open.spotify.com/track/5O9zs6G6RcB6yP1OKwnwiM?si=fc7e50856c34495a",
                "emoji_tabs": ["⭐"],
                "track_number": 17
            },
            {
                "name": "⭐ R.I.P. Fredo - Notice Me (feat. Young Nudy) (prod. Pi'erre Bourne)",
                "notes": "Track 18 off Playboi Carti's album \"Die Lit\".",
                "track_length": "",
                "leak_date": "May 11, 2018",
                "file_date": "Album Track",
                "type": "Streaming",
                "links": "https://open.spotify.com/track/45Ln3F9PRPYTXBcMFkZMzS?si=8b41a97310494fd9",
                "emoji_tabs": ["⭐"],
                "track_number": 18
            },
            {
                "name": "Top (feat. Pi'erre Bourne) (prod. Pi'erre Bourne)",
                "notes": "Track 19 off Playboi Carti's album \"Die Lit\".",
                "track_length": "",
                "leak_date": "May 11, 2018",
                "file_date": "Album Track",
                "type": "Streaming",
                "links": "https://open.spotify.com/track/7HsvTUJcXRQVK6QuALkAvW?si=428feafafa994789",
                "emoji_tabs": [],
                "track_number": 19
            }
        ]

        with transaction.atomic():
            total_updated = 0
            total_created = 0
            
            for track_data in die_lit_tracks:
                # Prepare search parameters
                search_name = track_data["name"]
                base_name = search_name.replace("⭐ ", "").replace("✨ ", "").replace("🗑️ ", "")
                track_num = track_data["track_number"]
                
                # Search for:
                # 1. Exact name match
                # 2. Base name match (without emoji)
                # 3. Simple name match (looking for the main title)
                exact_matches = CartiCatalog.objects.filter(name=search_name, era="Die Lit")
                base_matches = CartiCatalog.objects.filter(name=base_name, era="Die Lit")
                
                # Extract the main song name without producer/feature info
                import re
                main_title = re.split(r'\s*\(', search_name)[0].strip()
                main_title = main_title.replace("⭐ ", "").replace("✨ ", "").replace("🗑️ ", "")
                
                simple_matches = CartiCatalog.objects.filter(
                    name__icontains=main_title,
                    era="Die Lit"
                )
                
                # Also look for matches based on track number in notes
                track_matches = CartiCatalog.objects.filter(
                    notes__icontains=f"Track {track_num}",
                    era="Die Lit"
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
                        era="Die Lit",
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
                            'subsection': die_lit_subsection
                        }
                    )
                    
                    if not created:
                        metadata.sheet_tab = released_tab
                        metadata.subsection = die_lit_subsection
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
                f"Die Lit album tracks update complete: {total_updated} updated, {total_created} created"
            ))