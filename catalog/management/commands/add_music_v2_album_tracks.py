from django.core.management.base import BaseCommand
from catalog.models import CartiCatalog, SongMetadata, SheetTab
from django.db import transaction


class Command(BaseCommand):
    help = 'Adds I AM MUSIC [V2] album tracks with proper structure and "Album Track" badge'

    def handle(self, *args, **options):
        # Get or create the Released tab
        released_tab, _ = SheetTab.objects.get_or_create(name="Released")

        # Find or create the I AM MUSIC [V2] subsection
        music_v2_subsection = "I AM MUSIC [V2]"

        # Get existing emoji tabs for categorization
        try:
            special_tab = SheetTab.objects.get(name="✨ Special")
            best_of_tab = SheetTab.objects.get(name="⭐ Best Of")
            ai_tracks_tab = SheetTab.objects.get(name="🤖 AI Tracks")
        except SheetTab.DoesNotExist:
            self.stdout.write(self.style.WARNING("Some emoji tabs don't exist. Creating them."))
            special_tab, _ = SheetTab.objects.get_or_create(name="✨ Special")
            best_of_tab, _ = SheetTab.objects.get_or_create(name="⭐ Best Of")
            ai_tracks_tab, _ = SheetTab.objects.get_or_create(name="🤖 AI Tracks")

        # Define the album tracks with their proper formatting
        music_v2_tracks = [
            {
                "name": "⭐ POP OUT (prod. F1LTHY, SLOWBURNZ & DJH) (POP, P0P 0UT, P0P)",
                "notes": "Track 1 on \"I AM MUSIC\"\nDoes not have the live guitars from when it was performed :/",
                "track_length": "2:41",
                "leak_date": "Mar 14, 2025",
                "file_date": "Album Track",
                "type": "Streaming",
                "links": "https://open.spotify.com/track/3j3SfV4hAcR4XjCvW393Gr?si=c8eb1433dce140f3",
                "emoji_tabs": ["⭐"]
            },
            {
                "name": "CRUSH (feat. Travis Scott) (prod. F1LTHY & Ojivolta)",
                "notes": "Track 2 on \"I AM MUSIC\"",
                "track_length": "2:53",
                "leak_date": "Mar 14, 2025",
                "file_date": "Album Track",
                "type": "Streaming",
                "links": "https://open.spotify.com/track/3VdooJLOy4tLxKpnn46SMP?si=815cb7394481401a",
                "emoji_tabs": []
            },
            {
                "name": "K POP (prod. Cardo Got Wings, Ojivolta & Twisco) (KETAMINE)",
                "notes": "Track 3 on \"I AM MUSIC\"\nMay have minor differences but appears the same as the single release",
                "track_length": "1:52",
                "leak_date": "Mar 14, 2025",
                "file_date": "Album Track",
                "type": "Streaming",
                "links": "https://open.spotify.com/track/00iLTetTLAeImmBlh6jOJh?si=77eee1aa690b41b3",
                "emoji_tabs": []
            },
            {
                "name": "EVIL J0RDAN [V3] (prod. Cardo Got Wings, Johnny Juliano & Ojivolta) (EVILJ0RDAN, Ms. Jackson, Moving The Molly)",
                "notes": "Track 4 on \"I AM MUSIC\"\nAdded TikTok intro",
                "track_length": "3:03",
                "leak_date": "Mar 14, 2025",
                "file_date": "Album Track",
                "type": "Streaming",
                "links": "https://open.spotify.com/track/6iycYUk3oB0NPMdaDUrN1w?si=174aa203195b402f",
                "emoji_tabs": []
            },
            {
                "name": "MOJO JOJO [V2] (feat. Kendrick Lamar) (prod. Cardo Got Wings, Johnny Juliano, ​ssort & Ojivolta) (M0J0 J0J0, SH0T)",
                "notes": "Track 5 on \"I AM MUSIC\"\nKendrick Lamar was added onto leak, different mix & structure",
                "track_length": "2:36",
                "leak_date": "Mar 14, 2025",
                "file_date": "Album Track",
                "type": "Streaming",
                "links": "https://open.spotify.com/track/3WRUvGqySBZC6RkB5c2w1S?si=e5d83efca61a43cf",
                "emoji_tabs": []
            },
            {
                "name": "✨ PHILLY (feat. Travis Scott) (prod. Cardo Got Wings)",
                "notes": "Track 6 on \"I AM MUSIC\"",
                "track_length": "3:05",
                "leak_date": "Mar 14, 2025",
                "file_date": "Album Track",
                "type": "Streaming",
                "links": "https://open.spotify.com/track/5SIvP6TdWc9DNvKbENjnYc?si=8e6636c7281441ed",
                "emoji_tabs": ["✨"]
            },
            {
                "name": "✨ RADAR (prod. Metro Boomin)",
                "notes": "Track 7 on \"I AM MUSIC\"",
                "track_length": "1:47",
                "leak_date": "Mar 14, 2025",
                "file_date": "Album Track",
                "type": "Streaming",
                "links": "https://open.spotify.com/track/3lAEHk0eZzMKtCUFLXz8Ln?si=60d0d718431946ee",
                "emoji_tabs": ["✨"]
            },
            {
                "name": "⭐🤖 RATHER LIE (feat. The Weeknd & Lawson) (prod. F1LTHY, MIKE DEAN, Twisco, Ramzoid & Ojivolta)",
                "notes": "Track 8 on \"I AM MUSIC\"\nCarti vocals are AI with seemingly real adlibs.",
                "track_length": "3:29",
                "leak_date": "Mar 14, 2025",
                "file_date": "Album Track",
                "type": "Streaming",
                "links": "https://open.spotify.com/track/68qeaZhtMZ6abrJCYt6nQn?si=309eb0e0a6684e78",
                "emoji_tabs": ["⭐", "🤖"]
            },
            {
                "name": "🤖 FINE SHIT (feat. Lawson) (prod. Cash Cobain, Keanu Beats & Ojivolta)",
                "notes": "Track 9 on \"I AM MUSIC\"\nAll AI Lawson vocals except for the second verse.",
                "track_length": "1:46",
                "leak_date": "Mar 14, 2025",
                "file_date": "Album Track",
                "type": "Streaming",
                "links": "https://open.spotify.com/track/79mFFAOYcG8ZF6AN1JecAL?si=5763712b76a84752",
                "emoji_tabs": ["🤖"]
            },
            {
                "name": "✨ BACKD00R [V2] (feat. Kendrick Lamar & Jhené Aiko) (prod. Keanu Beats, Ojivolta, Twisco, Nagra & Darius Rameshni)",
                "notes": "Track 10 on \"I AM MUSIC\"",
                "track_length": "3:10",
                "leak_date": "Mar 14, 2025",
                "file_date": "Album Track",
                "type": "Streaming",
                "links": "https://open.spotify.com/track/0rNgWFQJtfttOYIHfDOHCg?si=cb578280741646a1",
                "emoji_tabs": ["✨"]
            },
            {
                "name": "✨ TOXIC (feat. Skepta) (prod. Cardo Got Wings, Dez Wright, Mu Lean & Stoopid Lou)",
                "notes": "Track 11 on \"I AM MUSIC\"",
                "track_length": "2:15",
                "leak_date": "Mar 14, 2025",
                "file_date": "Album Track",
                "type": "Streaming",
                "links": "https://open.spotify.com/track/4evMMKc2HD6fV9slMfgkMx?si=a87e978ff19d4923",
                "emoji_tabs": ["✨"]
            },
            {
                "name": "MUNYUN (prod. Keanu Beats, Ojivolta, DJH & 99Hurts)",
                "notes": "Track 12 on \"I AM MUSIC\"",
                "track_length": "2:34",
                "leak_date": "Mar 14, 2025",
                "file_date": "Album Track",
                "type": "Streaming",
                "links": "https://open.spotify.com/track/2JJFJEvFSWyQ59Pwl2gqSF?si=8bfb79e4f4324561",
                "emoji_tabs": []
            },
            {
                "name": "✨ CRANK (prod. Cardo Got Wings, Yung Exclusive & Johnny Juliano)",
                "notes": "Track 13 on \"I AM MUSIC\"",
                "track_length": "2:27",
                "leak_date": "Mar 14, 2025",
                "file_date": "Album Track",
                "type": "Streaming",
                "links": "https://open.spotify.com/track/7xAvtuHf8nGi5OtXVPYgb3?si=096f83b844134d7c",
                "emoji_tabs": ["✨"]
            },
            {
                "name": "✨CHARGE DEM HOES A FEE (feat. Future & Travis Scott) (prod. Wheezy, Southside, Dez Wright, Car!ton, Smatt Sertified & Juke Wong)",
                "notes": "Track 14 on \"I AM MUSIC\"",
                "track_length": "3:45",
                "leak_date": "Mar 14, 2025",
                "file_date": "Album Track",
                "type": "Streaming",
                "links": "https://open.spotify.com/track/21aDVa64pWR8SYQ7wBRMkd?si=580fdb2931da45f8",
                "emoji_tabs": ["✨"]
            },
            {
                "name": "GOOD CREDIT (feat. Kendrick Lamar) (prod. Cardo Got Wings)",
                "notes": "Track 15 on \"I AM MUSIC\"",
                "track_length": "3:10",
                "leak_date": "Mar 14, 2025",
                "file_date": "Album Track",
                "type": "Streaming",
                "links": "https://open.spotify.com/track/2n9fC0A4ptmWqYeMXEVaok?si=6d277d015abd4708",
                "emoji_tabs": []
            },
            {
                "name": "⭐ I SEEEEEE YOU BABY BOI [V2] (prod. KP Beatz, Lucian & DJ Moon) (LIE TO ME, I CAN SEE YA, YOUNG VAMP LOVE, Young Vamp Life, YVL)",
                "notes": "OG Filename: 16 I SEE YOU MASTER INTRO FIX\nTrack 16 on \"I AM MUSIC\"",
                "track_length": "2:38",
                "leak_date": "Mar 14, 2025",
                "file_date": "Album Track",
                "type": "Streaming",
                "links": "https://open.spotify.com/track/2ydagYqcyFfRtQPzKc5E8l?si=caeb6e03670f49d1",
                "emoji_tabs": ["⭐"]
            },
            {
                "name": "WAKE UP F1LTHY [V2] (feat. Travis Scott) (prod. BNYX & F1LTHY) (WAKE UP, Different Hoes, Racks Up)",
                "notes": "Track 17 on \"I AM MUSIC\"\nRework of a 2022 throwaway with new verses & hook vocals.",
                "track_length": "2:49",
                "leak_date": "Mar 14, 2025",
                "file_date": "Album Track",
                "type": "Streaming",
                "links": "https://open.spotify.com/track/1pzN8bCzy017iK3vWzkk6Z?si=fac99bbe680e4cad",
                "emoji_tabs": []
            },
            {
                "name": "JUMPIN (feat. Lil Uzi Vert) (prod. D. Hill)",
                "notes": "Track 18 on \"I AM MUSIC\"\nRecorded in 2021, in the same session as \"Two Out\".\nPINK TAPE PINK TAPE PINK TAPE PINK TAPE",
                "track_length": "1:32",
                "leak_date": "Mar 14, 2025",
                "file_date": "Album Track",
                "type": "Streaming",
                "links": "https://open.spotify.com/track/7oZOCPjlLpHZtIebTXhlfZ?si=3e7e60dfb0e34a29",
                "emoji_tabs": []
            },
            {
                "name": "TRIM [V2] (feat. Future) (prod. TM88, Akachi, DJ Moon, Sonickaboom, C$D Sid & Macnificent)",
                "notes": "Track 19 on \"I AM MUSIC\"\nHas alternative Carti vocals + worse verse, production is altered and quieter",
                "track_length": "3:13",
                "leak_date": "Mar 14, 2025",
                "file_date": "Album Track",
                "type": "Streaming",
                "links": "https://open.spotify.com/track/4qvsNsA4gQKC9HLrmPC2Vx?si=51bb3cd003a84180",
                "emoji_tabs": []
            },
            {
                "name": "✨ COCAINE NOSE (prod. F1LTHY, 100yrd & Brak3)",
                "notes": "Track 20 on \"I AM MUSIC\"\nSamples \"Only U\" by Ashanti",
                "track_length": "2:31",
                "leak_date": "Mar 14, 2025",
                "file_date": "Album Track",
                "type": "Streaming",
                "links": "https://open.spotify.com/track/4rXxjHSAglOynjIF8Z34dx?si=6e2dc76fcd9d428a",
                "emoji_tabs": ["✨"]
            },
            {
                "name": "✨ WE NEED ALL DA VIBES [V2] (feat. Young Thug, Gunna, & Ty Dolla $ign) (prod. Wheezy & Dez Wright) (Vibing, Vibin, South Atlanta)",
                "notes": "Track 21 on \"I AM MUSIC\"\nReuses Young Thug 2021 song \"Vibing\", but Gunna's verse was cut despite his adlibs being kept on Carti's verse (he washed all 3)",
                "track_length": "3:01",
                "leak_date": "Mar 14, 2025",
                "file_date": "Album Track",
                "type": "Streaming",
                "links": "https://open.spotify.com/track/4XcZp2xqbiD8YsnPboNUDo?si=717093707d2b4534",
                "emoji_tabs": ["✨"]
            },
            {
                "name": "✨ OLYMPIAN (prod. Clif Shayne, DJ Moon & Nick Spiders)",
                "notes": "Track 22 on \"I AM MUSIC\"",
                "track_length": "2:54",
                "leak_date": "Mar 14, 2025",
                "file_date": "Album Track",
                "type": "Streaming",
                "links": "https://open.spotify.com/track/4uoADk7q83CHvXHW3k1etM?si=20fe48c849a644d4",
                "emoji_tabs": ["✨"]
            },
            {
                "name": "OPM BABI (prod. Clayco, Streo & 󠁪opiumbaby)",
                "notes": "Track 23 on \"I AM MUSIC\"",
                "track_length": "2:53",
                "leak_date": "Mar 14, 2025",
                "file_date": "Album Track",
                "type": "Streaming",
                "links": "https://open.spotify.com/track/76yJsfb1CUy5Um8nFL7jKQ?si=b64c5b9b1d504d9b",
                "emoji_tabs": []
            },
            {
                "name": "TWIN TRIM (feat. Lil Uzi Vert) (prod. KP Beatz & Rok)",
                "notes": "Track 24 on \"I AM MUSIC\"\nAssumed to be an interlude, but rumored that Carti's verse was \"muted\"",
                "track_length": "1:34",
                "leak_date": "Mar 14, 2025",
                "file_date": "Album Track",
                "type": "Streaming",
                "links": "https://open.spotify.com/track/3surY3LebvLLdJezmiKUBO?si=9fa4eb29430b404e",
                "emoji_tabs": []
            },
            {
                "name": "✨ LIKE WEEZY (prod. Kelvin Krash & Ojivolta)",
                "notes": "Track 25 on \"I AM MUSIC\"",
                "track_length": "1:55",
                "leak_date": "Mar 14, 2025",
                "file_date": "Album Track",
                "type": "Streaming",
                "links": "https://open.spotify.com/track/4zK082ykqJzJGzC64NXjp1?si=5fc72de0d0e1461e",
                "emoji_tabs": ["✨"]
            },
            {
                "name": "DIS 1 GOT IT (prod. F1LTHY, Lukrative & Malik Ninety Five)",
                "notes": "Track 26 on \"I AM MUSIC\"",
                "track_length": "2:03",
                "leak_date": "Mar 14, 2025",
                "file_date": "Album Track",
                "type": "Streaming",
                "links": "https://open.spotify.com/track/4tMhjP02FRQ0KIUUEJ2oGK?si=ad656a4714ea44d8",
                "emoji_tabs": []
            },
            {
                "name": "WALK (prod. DJH) (BBYBOI, Money on Top of Money)",
                "notes": "Track 27 on \"I AM MUSIC\"\nTeased on September 1, 2024",
                "track_length": "1:34",
                "leak_date": "Mar 14, 2025",
                "file_date": "Album Track",
                "type": "Streaming",
                "links": "https://open.spotify.com/track/5Qya13gFXqupr4sSmZMKDg?si=6878fa1cf16f4976",
                "emoji_tabs": []
            },
            {
                "name": "✨ HBA [V3] (prod. Cardo Got Wings & Onokey) (H00DBYAIR, Tundra)",
                "notes": "Track 28 on \"I AM MUSIC\"\nHas additional production compared to the single, but had 5 lines removed/censored",
                "track_length": "3:32",
                "leak_date": "Mar 14, 2025",
                "file_date": "Album Track",
                "type": "Streaming",
                "links": "https://open.spotify.com/track/6q2PbvM9UEig4r8xku7VIb?si=f13f607b099e4d95",
                "emoji_tabs": ["✨"]
            },
            {
                "name": "OVERLY (prod. Maaly Raw)",
                "notes": "Track 29 on \"I AM MUSIC\"",
                "track_length": "1:45",
                "leak_date": "Mar 14, 2025",
                "file_date": "Album Track",
                "type": "Streaming",
                "links": "https://open.spotify.com/track/5tRylsadMpm8TydUgq7NWj?si=918b97bc2271434d",
                "emoji_tabs": []
            },
            {
                "name": "SOUTH ATLANTA BABY (prod. DJH & Ojivolta)",
                "notes": "Track 30 on \"I AM MUSIC\"",
                "track_length": "2:13",
                "leak_date": "Mar 14, 2025",
                "file_date": "Album Track",
                "type": "Streaming",
                "links": "https://open.spotify.com/track/7cHhlnawdN87aZbjO6LMRN?si=814637611abe4271",
                "emoji_tabs": []
            }
        ]

        with transaction.atomic():
            for track_data in music_v2_tracks:
                # Clean up the "MUSIC [V2]" prefix for era, since that's redundant with subsection
                era = "I AM MUSIC [V2]"
                
                # Check if the song already exists
                song_name = track_data["name"]
                existing_songs = CartiCatalog.objects.filter(name=song_name, era=era)

                if existing_songs.exists():
                    song = existing_songs.first()
                    self.stdout.write(self.style.WARNING(f"Song '{song_name}' already exists. Updating details..."))
                    
                    # Update song details
                    song.notes = track_data["notes"]
                    song.track_length = track_data["track_length"]
                    song.leak_date = track_data["leak_date"]
                    song.file_date = track_data["file_date"]
                    song.type = track_data["type"]
                    song.links = track_data["links"]
                    song.save()
                else:
                    # Create the new song
                    song = CartiCatalog.objects.create(
                        era=era,
                        name=song_name,
                        notes=track_data["notes"],
                        track_length=track_data["track_length"],
                        leak_date=track_data["leak_date"],
                        file_date=track_data["file_date"],
                        type=track_data["type"],
                        links=track_data["links"]
                    )
                    self.stdout.write(self.style.SUCCESS(f"Created new song: {song_name}"))

                # Make sure it has the proper metadata
                try:
                    metadata = SongMetadata.objects.get(song=song)
                    metadata.sheet_tab = released_tab
                    metadata.subsection = music_v2_subsection
                    metadata.save()
                    self.stdout.write(self.style.SUCCESS(f"Updated metadata for: {song_name}"))
                except SongMetadata.DoesNotExist:
                    metadata = SongMetadata.objects.create(
                        song=song,
                        sheet_tab=released_tab,
                        subsection=music_v2_subsection
                    )
                    self.stdout.write(self.style.SUCCESS(f"Created metadata for: {song_name}"))
                
                # Add emoji category tabs based on the song name prefix
                from catalog.models import SongCategory
                
                # Remove existing categories to avoid duplicates
                SongCategory.objects.filter(song=song).delete()
                
                for emoji in track_data["emoji_tabs"]:
                    if emoji == "✨":
                        SongCategory.objects.get_or_create(song=song, sheet_tab=special_tab)
                    elif emoji == "⭐":
                        SongCategory.objects.get_or_create(song=song, sheet_tab=best_of_tab)
                    elif emoji == "🤖":
                        SongCategory.objects.get_or_create(song=song, sheet_tab=ai_tracks_tab)
                
                self.stdout.write(self.style.SUCCESS(f"Added categories for: {song_name}"))

            self.stdout.write(self.style.SUCCESS(f"All {len(music_v2_tracks)} I AM MUSIC [V2] tracks have been processed"))