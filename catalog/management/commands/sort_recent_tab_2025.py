from django.core.management.base import BaseCommand
from catalog.models import CartiCatalog, SheetTab, SongCategory
from django.db.models import Q
from datetime import datetime, timedelta
import re

class Command(BaseCommand):
    help = 'Sort songs in the Recent tab by leak date, including only 2025 songs'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            dest='dry_run',
            help='Show what would be changed without actually making changes',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        self.stdout.write('Looking for songs leaked in 2025...')
        
        # 1. Identify the "Recent" tab
        try:
            recent_tab = SheetTab.objects.get(name="Recent")
        except SheetTab.DoesNotExist:
            self.stdout.write(self.style.ERROR('Recent tab not found in the database'))
            return
            
        # 2. Get all songs
        all_songs = CartiCatalog.objects.all()
        
        # 3. Parse leak dates and filter for 2025 songs
        start_of_2025 = datetime(2025, 1, 1)
        
        # Dictionary to store songs with parsed dates
        songs_with_dates = []
        
        # Date formats to try (from most to least specific)
        date_formats = [
            '%m/%d/%Y',     # 03/15/2024
            '%m/%d/%y',     # 03/15/24
            '%B %d, %Y',    # March 15, 2024
            '%b %d, %Y',    # Mar 15, 2024
            '%d-%m-%Y',     # 15-03-2024
            '%Y-%m-%d',     # 2024-03-15
            '%m/%Y',        # 03/2024
            '%B %Y',        # March 2024
            '%b %Y',        # Mar 2024
        ]
        
        for song in all_songs:
            leak_date_str = song.leak_date
            file_date_str = song.file_date
            parsed_date = None
            
            # Try to parse the leak date first
            if leak_date_str:
                # Check if "2025" appears in the string directly
                if "2025" in leak_date_str:
                    # Try each format
                    for fmt in date_formats:
                        try:
                            parsed_date = datetime.strptime(leak_date_str, fmt)
                            break
                        except ValueError:
                            continue
            
            # If leak date couldn't be parsed, try file date
            if parsed_date is None and file_date_str:
                # Check if "2025" appears in the string directly
                if "2025" in file_date_str:
                    for fmt in date_formats:
                        try:
                            parsed_date = datetime.strptime(file_date_str, fmt)
                            break
                        except ValueError:
                            continue
            
            # Only include songs from 2025
            if parsed_date and parsed_date.year == 2025:
                songs_with_dates.append((song, parsed_date))
        
        # 4. Sort the songs by leak date (most recent first)
        sorted_songs = sorted(
            songs_with_dates,
            key=lambda x: (x[1] is None, -int(x[1].timestamp()) if x[1] else 0)
        )
        
        # 5. Use the exact songs specified by ID
        
        # Get the songs by ID for specific ordering (priority songs at the top of the Recent tab)
        song_ids = [
            4,  # 🏆 Dancer
            5,  # 🏆 Paramount
            6,  # DEMONSLURK
            7,  # ⭐ Not Real [V3]
            8   # Lil Uzi Vert - Cartier [V2]
        ]
        
        # Number of songs to show in the Recent tab (increase from 5 to 25)
        max_recent_songs = 25
        
        # Get the exact songs in the exact order
        found_songs = []
        for song_id in song_ids:
            try:
                song = CartiCatalog.objects.get(id=song_id)
                found_songs.append(song)
                self.stdout.write(f"Found song #{song_id}: {song.name}")
            except CartiCatalog.DoesNotExist:
                self.stdout.write(self.style.WARNING(f"Could not find song with ID {song_id}"))
        
        # If we didn't find all songs by ID, fall back to search by name/era
        if len(found_songs) < len(song_ids):
            self.stdout.write("Some songs not found by ID, falling back to finding by name and era...")
            
            # Define the specific songs to find by name/era - IMPORTANT: Match exactly what's used in views.py index view
            specific_songs = [
                {'name': '🏆 Dancer', 'era': 'TMB Collab', 'producer': 'TrapMoneyBenny'},
                {'name': '🏆 Paramount', 'era': 'Whole Lotta Red', 'producer': 'DP Beats'},
                {'name': 'DEMONSLURK', 'era': 'MUSIC', 'feature': 'Swamp Izzo'},
                {'name': '⭐ Not Real', 'era': 'Whole Lotta Red', 'producer': 'Pi\'erre Bourne'},
                {'name': 'Cartier', 'era': 'Chucky Era', 'feature': 'Playboi Carti'}
            ]
            
            # Find songs by name and era
            found_songs = []
            
            for spec in specific_songs:
                # Get the most likely matching song
                matches = CartiCatalog.objects.filter(
                    Q(name__icontains=spec['name'].replace('🏆 ', '').replace('⭐ ', '')) & 
                    Q(era__icontains=spec['era'])
                )
            
                # If multiple matches, try to refine with producer or feature
                if 'producer' in spec and matches.count() > 1:
                    producer_matches = matches.filter(
                        Q(name__icontains=spec['producer']) | 
                        Q(notes__icontains=spec['producer'])
                    )
                    if producer_matches.exists():
                        matches = producer_matches
                
                if 'feature' in spec and matches.count() > 1:
                    feature_matches = matches.filter(
                        Q(name__icontains=spec['feature']) | 
                        Q(notes__icontains=spec['feature'])
                    )
                    if feature_matches.exists():
                        matches = feature_matches
                
                # Get the first match if any
                if matches.exists():
                    found_songs.append(matches.first())
                    self.stdout.write(f"Found song: {matches.first().name}")
                else:
                    self.stdout.write(self.style.WARNING(f"Could not find song: {spec['name']} from {spec['era']}"))
        
        total_count = len(found_songs)
        
        self.stdout.write(f'Found {total_count} specific songs to add to Recent tab')
        
        # Start with our specific priority songs
        priority_songs = found_songs.copy() if found_songs else []
        
        # If specific songs not found, and no sorted songs, exit
        if not priority_songs and not sorted_songs:
            self.stdout.write(self.style.WARNING('No 2025 songs found'))
            return
        
        # Now let's add more songs from sorted_songs up to max_recent_songs
        # But skip any that are already in priority_songs
        songs_to_add = priority_songs.copy()
        priority_song_ids = {song.id for song in priority_songs}
        
        if sorted_songs:
            # Display the sorted songs
            self.stdout.write('\nSorted 2025 songs available to add:')
            for i, (song, date) in enumerate(sorted_songs, 1):
                date_str = date.strftime("%Y-%m-%d") if date else "Unknown date"
                self.stdout.write(f'{i}. {song.name} - Leaked on: {date_str}')
                
            # Add more songs from sorted_songs up to max_recent_songs, 
            # skipping any that are already in priority_songs
            for song, _ in sorted_songs:
                if song.id not in priority_song_ids and len(songs_to_add) < max_recent_songs:
                    songs_to_add.append(song)
        
        # Fall back to using recent IDs if we have no other options
        if not songs_to_add:
            self.stdout.write(self.style.WARNING("No songs found by specific IDs or dates, using most recent songs by ID"))
            songs_to_add = list(CartiCatalog.objects.order_by('-id')[:max_recent_songs])
        
        total_count = len(songs_to_add)
        self.stdout.write(f'Adding {total_count} songs to Recent tab')
        
        if dry_run:
            self.stdout.write(self.style.WARNING('\nDRY RUN: No changes made to the database'))
            return
            
        # Actually update the songs in the database
        self.stdout.write('\nUpdating Recent tab...')
        
        # Remove all songs from the Recent tab
        SongCategory.objects.filter(sheet_tab=recent_tab).delete()
        self.stdout.write('Removed all songs from the Recent tab')
        
        # Add specified songs to the Recent tab
        for i, song in enumerate(songs_to_add, 1):
            SongCategory.objects.create(
                song=song,
                sheet_tab=recent_tab
            )
            self.stdout.write(f'Added {song.name} to Recent tab (position {i})')
        
        self.stdout.write(self.style.SUCCESS(f'\nSuccessfully updated the Recent tab with {total_count} songs from 2025'))