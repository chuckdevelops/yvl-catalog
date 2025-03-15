from django.core.management.base import BaseCommand
from catalog.models import CartiCatalog, SheetTab, SongCategory, SongMetadata
from django.db import transaction
from django.utils import timezone

class Command(BaseCommand):
    help = 'Import I AM MUSIC V2 songs to the database'

    def handle(self, *args, **options):
        # Songs data from I AM MUSIC V2
        songs_data = [
            {
                'name': 'MUSIC [V2]	⭐ POP OUT',
                'era': 'I AM MUSIC',
                'notes': '(prod. F1LTHY, SLOWBURNZ & DJH)\n(POP, P0P 0UT, P0P)	Track 1 on "I AM MUSIC"\nDoes not have the live guitars from when it was performed :/',
                'track_length': '2:41',
                'leak_date': 'Mar 14, 2025',
                'type': 'Album Track',
                'is_streaming': 'Yes',
                'links': 'https://open.spotify.com/track/3j3SfV4hAcR4XjCvW393Gr?si=c8eb1433dce140f3',
            },
            {
                'name': 'MUSIC [V2]	CRUSH',
                'era': 'I AM MUSIC',
                'notes': '(feat. Travis Scott) (prod. F1LTHY & Ojivolta)	Track 2 on "I AM MUSIC"',
                'track_length': '2:53',
                'leak_date': 'Mar 14, 2025',
                'type': 'Album Track',
                'is_streaming': 'Yes',
                'links': 'https://open.spotify.com/track/3VdooJLOy4tLxKpnn46SMP?si=815cb7394481401a',
            },
            {
                'name': 'MUSIC [V2]	K POP',
                'era': 'I AM MUSIC',
                'notes': '(prod. Cardo Got Wings, Ojivolta & Twisco)\n(KETAMINE)	Track 3 on "I AM MUSIC"\nMay have minor differences but appears the same as the single release',
                'track_length': '1:52',
                'leak_date': 'Mar 14, 2025',
                'type': 'Album Track',
                'is_streaming': 'Yes',
                'links': 'https://open.spotify.com/track/00iLTetTLAeImmBlh6jOJh?si=77eee1aa690b41b3',
            },
            {
                'name': 'MUSIC [V2]	EVIL J0RDAN [V3]',
                'era': 'I AM MUSIC',
                'notes': '(prod. Cardo Got Wings, Johnny Juliano & Ojivolta)\n(EVILJ0RDAN, Ms. Jackson, Moving The Molly)	Track 4 on "I AM MUSIC"\nAdded TikTok intro',
                'track_length': '3:03',
                'leak_date': 'Mar 14, 2025',
                'type': 'Album Track',
                'is_streaming': 'Yes',
                'links': 'https://open.spotify.com/track/6iycYUk3oB0NPMdaDUrN1w?si=174aa203195b402f',
            },
            {
                'name': 'MUSIC [V2]	MOJO JOJO [V2]',
                'era': 'I AM MUSIC',
                'notes': '(feat. Kendrick Lamar) (prod. Cardo Got Wings,\nJohnny Juliano, ​ssort & Ojivolta)\n(M0J0 J0J0, SH0T)	Track 5 on "I AM MUSIC"\nKendrick Lamar was added onto leak, different mix & structure',
                'track_length': '2:36',
                'leak_date': 'Mar 14, 2025',
                'type': 'Album Track',
                'is_streaming': 'Yes',
                'links': 'https://open.spotify.com/track/3WRUvGqySBZC6RkB5c2w1S?si=e5d83efca61a43cf',
            },
            {
                'name': 'MUSIC [V2]	✨ PHILLY',
                'era': 'I AM MUSIC',
                'notes': '(feat. Travis Scott) (prod. Cardo Got Wings)	Track 6 on "I AM MUSIC"',
                'track_length': '3:05',
                'leak_date': 'Mar 14, 2025',
                'type': 'Album Track',
                'is_streaming': 'Yes',
                'links': 'https://open.spotify.com/track/5SIvP6TdWc9DNvKbENjnYc?si=8e6636c7281441ed',
            },
            {
                'name': 'MUSIC [V2]	✨ RADAR',
                'era': 'I AM MUSIC',
                'notes': '(prod. Metro Boomin)	Track 7 on "I AM MUSIC"',
                'track_length': '1:47',
                'leak_date': 'Mar 14, 2025',
                'type': 'Album Track',
                'is_streaming': 'Yes',
                'links': 'https://open.spotify.com/track/3lAEHk0eZzMKtCUFLXz8Ln?si=60d0d718431946ee',
            },
            {
                'name': 'MUSIC [V2]	⭐🤖 RATHER LIE',
                'era': 'I AM MUSIC',
                'notes': '(feat. The Weeknd & Lawson) (prod. F1LTHY, MIKE DEAN, Twisco, Ramzoid & Ojivolta)	Track 8 on "I AM MUSIC"\nCarti vocals are AI with seemingly real adlibs.',
                'track_length': '3:29',
                'leak_date': 'Mar 14, 2025',
                'type': 'Album Track',
                'is_streaming': 'Yes',
                'links': 'https://open.spotify.com/track/68qeaZhtMZ6abrJCYt6nQn?si=309eb0e0a6684e78',
            },
            {
                'name': 'MUSIC [V2]	🤖 FINE SHIT',
                'era': 'I AM MUSIC',
                'notes': '(feat. Lawson) (prod. Cash Cobain, Keanu Beats & Ojivolta)	Track 9 on "I AM MUSIC"\nAll AI Lawson vocals except for the second verse.',
                'track_length': '1:46',
                'leak_date': 'Mar 14, 2025',
                'type': 'Album Track',
                'is_streaming': 'Yes',
                'links': 'https://open.spotify.com/track/79mFFAOYcG8ZF6AN1JecAL?si=5763712b76a84752',
            },
            {
                'name': 'MUSIC [V2]	✨ BACKD00R [V2]',
                'era': 'I AM MUSIC',
                'notes': '(feat. Kendrick Lamar & Jhené Aiko) (prod. Keanu Beats, Ojivolta, Twisco, Nagra & Darius Rameshni)	Track 10 on "I AM MUSIC"',
                'track_length': '3:10',
                'leak_date': 'Mar 14, 2025',
                'type': 'Album Track',
                'is_streaming': 'Yes',
                'links': 'https://open.spotify.com/track/0rNgWFQJtfttOYIHfDOHCg?si=cb578280741646a1',
            },
            {
                'name': 'MUSIC [V2]	✨ TOXIC',
                'era': 'I AM MUSIC',
                'notes': '(feat. Skepta) (prod. Cardo Got Wings, Dez Wright, Mu Lean & Stoopid Lou)	Track 11 on "I AM MUSIC"',
                'track_length': '2:15',
                'leak_date': 'Mar 14, 2025',
                'type': 'Album Track',
                'is_streaming': 'Yes',
                'links': 'https://open.spotify.com/track/4evMMKc2HD6fV9slMfgkMx?si=a87e978ff19d4923',
            },
            {
                'name': 'MUSIC [V2]	MUNYUN',
                'era': 'I AM MUSIC',
                'notes': '(prod. Keanu Beats, Ojivolta, DJH & 99Hurts)	Track 12 on "I AM MUSIC"',
                'track_length': '2:34',
                'leak_date': 'Mar 14, 2025',
                'type': 'Album Track',
                'is_streaming': 'Yes',
                'links': 'https://open.spotify.com/track/2JJFJEvFSWyQ59Pwl2gqSF?si=8bfb79e4f4324561',
            },
            {
                'name': 'MUSIC [V2]	✨ CRANK',
                'era': 'I AM MUSIC',
                'notes': '(prod. Cardo Got Wings, Yung Exclusive & Johnny Juliano)	Track 13 on "I AM MUSIC"',
                'track_length': '2:27',
                'leak_date': 'Mar 14, 2025',
                'type': 'Album Track',
                'is_streaming': 'Yes',
                'links': 'https://open.spotify.com/track/7xAvtuHf8nGi5OtXVPYgb3?si=096f83b844134d7c',
            },
            {
                'name': 'MUSIC [V2]	✨CHARGE DEM HOES A FEE',
                'era': 'I AM MUSIC',
                'notes': '(feat. Future & Travis Scott) (prod. Wheezy, Southside, Dez Wright, Car!ton, Smatt Sertified & Juke Wong)	Track 14 on "I AM MUSIC"',
                'track_length': '3:45',
                'leak_date': 'Mar 14, 2025',
                'type': 'Album Track',
                'is_streaming': 'Yes',
                'links': 'https://open.spotify.com/track/21aDVa64pWR8SYQ7wBRMkd?si=580fdb2931da45f8',
            },
            {
                'name': 'MUSIC [V2]	GOOD CREDIT',
                'era': 'I AM MUSIC',
                'notes': '(feat. Kendrick Lamar) (prod. Cardo Got Wings)	Track 15 on "I AM MUSIC"',
                'track_length': '3:10',
                'leak_date': 'Mar 14, 2025',
                'type': 'Album Track',
                'is_streaming': 'Yes',
                'links': 'https://open.spotify.com/track/2n9fC0A4ptmWqYeMXEVaok?si=6d277d015abd4708',
            },
            {
                'name': 'MUSIC [V2]	⭐ I SEEEEEE YOU BABY BOI [V2]',
                'era': 'I AM MUSIC',
                'notes': '(prod. KP Beatz, Lucian & DJ Moon)\n(LIE TO ME, I CAN SEE YA, YOUNG VAMP LOVE, Young Vamp Life, YVL)	OG Filename: 16 I SEE YOU MASTER INTRO FIX\nTrack 16 on "I AM MUSIC"',
                'track_length': '2:38',
                'leak_date': 'Mar 14, 2025',
                'type': 'Album Track',
                'is_streaming': 'Yes',
                'links': 'https://open.spotify.com/track/2ydagYqcyFfRtQPzKc5E8l?si=caeb6e03670f49d1',
            },
            {
                'name': 'MUSIC [V2]	WAKE UP F1LTHY [V2]',
                'era': 'I AM MUSIC',
                'notes': '(feat. Travis Scott) (prod. BNYX & F1LTHY)\n(WAKE UP, Different Hoes, Racks Up)	Track 17 on "I AM MUSIC"\nRework of a 2022 throwaway with new verses & hook vocals.',
                'track_length': '2:49',
                'leak_date': 'Mar 14, 2025',
                'type': 'Album Track',
                'is_streaming': 'Yes',
                'links': 'https://open.spotify.com/track/1pzN8bCzy017iK3vWzkk6Z?si=fac99bbe680e4cad',
            },
            {
                'name': 'MUSIC [V2]	JUMPIN',
                'era': 'I AM MUSIC',
                'notes': '(feat. Lil Uzi Vert) (prod. D. Hill)	Track 18 on "I AM MUSIC"\nRecorded in 2021, in the same session as "Two Out".\nPINK TAPE PINK TAPE PINK TAPE PINK TAPE',
                'track_length': '1:32',
                'leak_date': 'Mar 14, 2025',
                'type': 'Album Track',
                'is_streaming': 'Yes',
                'links': 'https://open.spotify.com/track/7oZOCPjlLpHZtIebTXhlfZ?si=3e7e60dfb0e34a29',
            },
            {
                'name': 'MUSIC [V2]	TRIM [V2]',
                'era': 'I AM MUSIC',
                'notes': '(feat. Future) (prod. TM88, Akachi, DJ Moon, Sonickaboom, C$D Sid & Macnificent)	Track 19 on "I AM MUSIC"\nHas alternative Carti vocals + worse verse, production is altered and quieter',
                'track_length': '3:13',
                'leak_date': 'Mar 14, 2025',
                'type': 'Album Track',
                'is_streaming': 'Yes',
                'links': 'https://open.spotify.com/track/4qvsNsA4gQKC9HLrmPC2Vx?si=51bb3cd003a84180',
            },
            {
                'name': 'MUSIC [V2]	✨ COCAINE NOSE',
                'era': 'I AM MUSIC',
                'notes': '(prod. F1LTHY, 100yrd & Brak3)	Track 20 on "I AM MUSIC"\nSamples "Only U" by Ashanti',
                'track_length': '2:31',
                'leak_date': 'Mar 14, 2025',
                'type': 'Album Track',
                'is_streaming': 'Yes',
                'links': 'https://open.spotify.com/track/4rXxjHSAglOynjIF8Z34dx?si=6e2dc76fcd9d428a',
            },
            {
                'name': 'MUSIC [V2]	✨ WE NEED ALL DA VIBES [V2]',
                'era': 'I AM MUSIC',
                'notes': '(feat. Young Thug, Gunna, & Ty Dolla $ign) (prod. Wheezy & Dez Wright)\n(Vibing, Vibin, South Atlanta)	Track 21 on "I AM MUSIC"\nReuses Young Thug 2021 song "Vibing", but Gunna\'s verse was cut despite his adlibs being kept on Carti\'s verse (he washed all 3)',
                'track_length': '3:01',
                'leak_date': 'Mar 14, 2025',
                'type': 'Album Track',
                'is_streaming': 'Yes',
                'links': 'https://open.spotify.com/track/4XcZp2xqbiD8YsnPboNUDo?si=717093707d2b4534',
            },
            {
                'name': 'MUSIC [V2]	✨ OLYMPIAN',
                'era': 'I AM MUSIC',
                'notes': '(prod. Clif Shayne, DJ Moon & Nick Spiders)	Track 22 on "I AM MUSIC"',
                'track_length': '2:54',
                'leak_date': 'Mar 14, 2025',
                'type': 'Album Track',
                'is_streaming': 'Yes',
                'links': 'https://open.spotify.com/track/4uoADk7q83CHvXHW3k1etM?si=20fe48c849a644d4',
            },
            {
                'name': 'MUSIC [V2]	OPM BABI',
                'era': 'I AM MUSIC',
                'notes': '(prod. Clayco, Streo & 󠁪opiumbaby)	Track 23 on "I AM MUSIC"',
                'track_length': '2:53',
                'leak_date': 'Mar 14, 2025',
                'type': 'Album Track',
                'is_streaming': 'Yes',
                'links': 'https://open.spotify.com/track/76yJsfb1CUy5Um8nFL7jKQ?si=b64c5b9b1d504d9b',
            },
            {
                'name': 'MUSIC [V2]	TWIN TRIM',
                'era': 'I AM MUSIC',
                'notes': '(feat. Lil Uzi Vert) (prod. KP Beatz & Rok)	Track 24 on "I AM MUSIC"\nAssumed to be an interlude, but rumored that Carti\'s verse was "muted"',
                'track_length': '1:34',
                'leak_date': 'Mar 14, 2025',
                'type': 'Album Track',
                'is_streaming': 'Yes',
                'links': 'https://open.spotify.com/track/3surY3LebvLLdJezmiKUBO?si=9fa4eb29430b404e',
            },
            {
                'name': 'MUSIC [V2]	✨ LIKE WEEZY',
                'era': 'I AM MUSIC',
                'notes': '(prod. Kelvin Krash & Ojivolta)	Track 25 on "I AM MUSIC"',
                'track_length': '1:55',
                'leak_date': 'Mar 14, 2025',
                'type': 'Album Track',
                'is_streaming': 'Yes',
                'links': 'https://open.spotify.com/track/4zK082ykqJzJGzC64NXjp1?si=5fc72de0d0e1461e',
            },
            {
                'name': 'MUSIC [V2]	DIS 1 GOT IT',
                'era': 'I AM MUSIC',
                'notes': '(prod. F1LTHY, Lukrative & Malik Ninety Five)	Track 26 on "I AM MUSIC"',
                'track_length': '2:03',
                'leak_date': 'Mar 14, 2025',
                'type': 'Album Track',
                'is_streaming': 'Yes',
                'links': 'https://open.spotify.com/track/4tMhjP02FRQ0KIUUEJ2oGK?si=ad656a4714ea44d8',
            },
            {
                'name': 'MUSIC [V2]	WALK',
                'era': 'I AM MUSIC',
                'notes': '(prod. DJH)\n(BBYBOI, Money on Top of Money)	Track 27 on "I AM MUSIC"\nTeased on September 1, 2024',
                'track_length': '1:34',
                'leak_date': 'Mar 14, 2025',
                'type': 'Album Track',
                'is_streaming': 'Yes',
                'links': 'https://open.spotify.com/track/5Qya13gFXqupr4sSmZMKDg?si=6878fa1cf16f4976',
            },
            {
                'name': 'MUSIC [V2]	✨ HBA [V3]',
                'era': 'I AM MUSIC',
                'notes': '(prod. Cardo Got Wings & Onokey)\n(H00DBYAIR, Tundra)	Track 28 on "I AM MUSIC"\nHas additional production compared to the single, but had 5 lines removed/censored',
                'track_length': '3:32',
                'leak_date': 'Mar 14, 2025',
                'type': 'Album Track',
                'is_streaming': 'Yes',
                'links': 'https://open.spotify.com/track/6q2PbvM9UEig4r8xku7VIb?si=f13f607b099e4d95',
            },
            {
                'name': 'MUSIC [V2]	OVERLY',
                'era': 'I AM MUSIC',
                'notes': '(prod. Maaly Raw)	Track 29 on "I AM MUSIC"',
                'track_length': '1:45',
                'leak_date': 'Mar 14, 2025',
                'type': 'Album Track',
                'is_streaming': 'Yes',
                'links': 'https://open.spotify.com/track/5tRylsadMpm8TydUgq7NWj?si=918b97bc2271434d',
            },
            {
                'name': 'MUSIC [V2]	SOUTH ATLANTA BABY',
                'era': 'I AM MUSIC',
                'notes': '(prod. DJH & Ojivolta)	Track 30 on "I AM MUSIC"',
                'track_length': '2:13',
                'leak_date': 'Mar 14, 2025',
                'type': 'Album Track',
                'is_streaming': 'Yes',
                'links': 'https://open.spotify.com/track/7cHhlnawdN87aZbjO6LMRN?si=814637611abe4271',
            },
        ]

        try:
            with transaction.atomic():
                # Get or create the "Released" tab
                released_tab, _ = SheetTab.objects.get_or_create(name="Released")
                
                # Get or create special tabs based on song prefixes
                special_tabs = {
                    "✨": SheetTab.objects.get_or_create(name="✨ Special")[0],
                    "⭐": SheetTab.objects.get_or_create(name="⭐ Best Of")[0],
                    "🤖": SheetTab.objects.get_or_create(name="🤖 AI Tracks")[0],
                }
                
                # Get Recent tab
                recent_tab, _ = SheetTab.objects.get_or_create(name="Recent")
                
                # Track created songs to add to Recent tab later
                created_songs = []
                
                for song_data in songs_data:
                    # Process the data
                    # Use is_streaming value for the type field
                    is_streaming = song_data.pop('is_streaming', None)
                    if is_streaming:
                        song_data['type'] = is_streaming
                    
                    # Create the song
                    song, created = CartiCatalog.objects.get_or_create(
                        name=song_data['name'],
                        era=song_data['era'],
                        defaults={
                            **song_data,
                            'type': song_data.get('type', 'Album Track'),
                            'quality': 'CDQ',
                            'available_length': song_data.get('track_length', ''),
                            'scraped_at': timezone.now(),
                        }
                    )
                    
                    if created:
                        self.stdout.write(f"Created song: {song.name}")
                        created_songs.append(song)
                    else:
                        self.stdout.write(f"Found existing song: {song.name}, updating...")
                        # Update song fields
                        for key, value in song_data.items():
                            setattr(song, key, value)
                        
                        # Special fields
                        song.quality = 'CDQ'
                        song.available_length = song_data.get('track_length', '')
                        song.scraped_at = timezone.now()
                        song.save()
                    
                    # Add primary metadata - all songs are in the "Released" tab
                    SongMetadata.objects.update_or_create(
                        song=song,
                        defaults={
                            'sheet_tab': released_tab,
                            'subsection': 'I AM MUSIC'
                        }
                    )
                    
                    # Add secondary category based on prefixes in the name
                    for prefix, tab in special_tabs.items():
                        if prefix in song.name:
                            SongCategory.objects.get_or_create(
                                song=song,
                                sheet_tab=tab
                            )
                            self.stdout.write(f"Added {song.name} to {tab.name} tab")
                    
                # Now update the Recent tab with all new songs
                # First, remove all existing songs from Recent tab
                SongCategory.objects.filter(sheet_tab=recent_tab).delete()
                self.stdout.write('Cleared Recent tab')
                
                # Add all created songs to the Recent tab
                for song in created_songs:
                    SongCategory.objects.create(
                        song=song,
                        sheet_tab=recent_tab
                    )
                    self.stdout.write(f"Added {song.name} to Recent tab")
                
                self.stdout.write(self.style.SUCCESS(f"Successfully added {len(created_songs)} songs to the database"))
        
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error: {e}"))