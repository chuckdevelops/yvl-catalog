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
        
        # 5. Display and update the order in the database
        if not sorted_songs:
            self.stdout.write(self.style.WARNING('No 2025 songs found'))
            return
        
        total_count = len(sorted_songs)
        
        self.stdout.write(f'Found {total_count} songs with 2025 leak dates')
        
        # Display the sorted songs
        self.stdout.write('\nSorted 2025 songs:')
        for i, (song, date) in enumerate(sorted_songs, 1):
            date_str = date.strftime("%Y-%m-%d") if date else "Unknown date"
            self.stdout.write(f'{i}. {song.name} - Leaked on: {date_str}')
        
        if dry_run:
            self.stdout.write(self.style.WARNING('\nDRY RUN: No changes made to the database'))
            return
            
        # Actually update the songs in the database
        self.stdout.write('\nUpdating Recent tab with 2025 songs only...')
        
        # Remove all songs from the Recent tab
        SongCategory.objects.filter(sheet_tab=recent_tab).delete()
        self.stdout.write('Removed all songs from the Recent tab')
        
        # Add 2025 songs back in the sorted order
        for i, (song, date) in enumerate(sorted_songs, 1):
            SongCategory.objects.create(
                song=song,
                sheet_tab=recent_tab
            )
            self.stdout.write(f'Added {song.name} back to Recent tab (position {i})')
        
        self.stdout.write(self.style.SUCCESS(f'\nSuccessfully updated the Recent tab with {total_count} songs from 2025'))